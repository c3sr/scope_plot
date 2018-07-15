import json
import sys
import pprint
import os
import re
import numpy as np
import matplotlib.pyplot as plt
import yaml

from microbench_plot import utils
from microbench_plot.error import UnknownGenerator

pp = pprint.PrettyPrinter(indent=4)
plt.switch_backend('agg')


def configure_yaxis(ax, axis_spec):
    if "lim" in axis_spec:
        lim = axis_spec["lim"]
        ax.set_ylim(lim)
    if "label" in axis_spec:
        label = axis_spec["label"]
        ax.set_ylabel(label)
    if "scale" in axis_spec:
        scale = axis_spec["scale"]
        utils.debug("seting y axis scale: {}".format(scale))
        ax.set_yscale(scale, basey=10)


def configure_xaxis(ax, axis_spec):
    if "scale" in axis_spec:
        scale = axis_spec["scale"]
        utils.debug("seting x axis scale: {}".format(scale))
        ax.set_xscale(scale, basex=2)
    if "label" in axis_spec:
        label = axis_spec["label"]
        ax.set_xlabel(label)
    if "lim" in axis_spec:
        lim = axis_spec["lim"]
        ax.set_xlim(lim)


def generator_bar(ax, ax_cfg):
    bar_width = ax_cfg.get("bar_width", 0.8)
    num_series = len(ax_cfg["series"])
    utils.debug("Number of series: {}".format(num_series))

    default_file = ax_cfg.get("input_file", "not_found")

    default_x_scale = eval(str(ax_cfg.get("xscale", 1.0)))
    default_y_scale = eval(str(ax_cfg.get("yscale", 1.0)))

    default_x_field = ax_cfg.get("xfield", "real_time")
    default_y_field = ax_cfg.get("yfield", "real_time")

    series_cfgs = ax_cfg.get("series", [])
    for c, s in enumerate(series_cfgs):
        file_path = s.get("input_file", default_file)
        label = s.get("label", "")
        regex = s.get("regex", ".*")
        yscale = eval(str(s.get("yscale", default_y_scale)))
        xscale = eval(str(s.get("xscale", default_x_scale)))
        utils.debug("series {}: Opening {}".format(c, file_path))
        with open(file_path, "rb") as f:
            j = json.loads(f.read().decode("utf-8"))

        utils.debug("series {}: filter regex is {}".format(c, regex))
        pattern = re.compile(regex)
        matches = [
            b for b in j["benchmarks"] if pattern is None or pattern.search(b["name"])
        ]
        utils.debug("{} datapoints matched {}".format(len(matches), regex))

        if len(matches) == 0:
            continue

        xfield = s.get("xfield", default_x_field)
        yfield = s.get("yfield", default_y_field)
        utils.debug("series {}: x field: {}".format(c, xfield))
        utils.debug("series {}: y field: {}".format(c, yfield))

        x = np.array([float(b[xfield]) for b in matches])
        ind = np.arange(len(x))
        y = np.array([float(b[yfield]) for b in matches])

        # Rescale
        x *= xscale
        y *= yscale
        utils.debug("series {}: x scale={} yscale={}".format(c, xscale, yscale))

        utils.debug("ind: {}".format(ind))
        utils.debug("x: {}".format(x))
        utils.debug("y: {}".format(y))

        # pp.pprint(y)

        ax.bar(ind + bar_width * c, y, width=bar_width, label=label, align="center")

    ax.set_xticks(ind + bar_width * (len(series_cfgs) - 1) / 2)
    # ax.set_xticklabels((x + bar_width * len(series_cfgs)).round(1))
    ax.set_xticklabels(x.round(2))

    configure_yaxis(ax, ax_cfg.get("yaxis", {}))
    configure_xaxis(ax, ax_cfg.get("xaxis", {}))

    if "title" in ax_cfg:
        title = ax_cfg["title"]
        ax.set_title(title)

    # ax.legend(loc='upper left')
    ax.legend(loc="best")

    return ax


def generator_errorbar(ax, ax_cfg):

    ax.grid(True)

    default_x_field = ax_cfg.get("xaxis", {}).get("field", "bytes")
    default_y_field = ax_cfg.get("yaxis", {}).get("field", "bytes_per_second")

    for i, s in enumerate(ax_cfg["series"]):
        file_path = s["input_file"]
        label = s["label"]
        regex = s.get("regex", ".*")
        yscale = float(s.get("yscale", 1.0))
        xscale = float(s.get("xscale", 1.0))
        utils.debug("series {}: opening {}".format(i, file_path))
        with open(file_path, "rb") as f:
            j = json.loads(f.read().decode('utf-8'))

        pattern = re.compile(regex)
        matches = [b for b in j["benchmarks"] if pattern is None or pattern.search(b["name"])]
        means = [b for b in matches if b["name"].endswith("_mean")]
        stddevs = [b for b in matches if b["name"].endswith("_stddev")]
        x = np.array([float(b[default_x_field]) for b in means])
        y = np.array([float(b[default_y_field]) for b in means])
        e = np.array([float(b[default_y_field]) for b in stddevs])

        # Rescale
        x *= xscale
        y *= yscale
        e *= yscale

        # pp.pprint(means)
        if "color" in s:
            color = s["color"]
        else:
            color = color_wheel[i]
        ax.errorbar(x, y, e, capsize=3, label=label, color=color)

    if "title" in ax_cfg:
        title = ax_cfg["title"]
        ax.set_title(title)

    if "yaxis" in ax_cfg:
        axis_cfg = ax_cfg["yaxis"]
        configure_yaxis(ax, axis_cfg)

    if "xaxis" in ax_cfg:
        axis_cfg = ax_cfg["xaxis"]
        configure_xaxis(ax, axis_cfg)

    ax.legend(loc="best")

    return ax


def generator_regplot(ax, ax_spec):

    series_specs = ax_spec["series"]
    for series_spec in series_specs:
        file_path = series_spec["input_file"]
        label = series_spec["label"]
        regex = series_spec.get("regex", ".*")
        with open(file_path, "rb") as f:
            j = json.loads(f.read().decode('utf-8'))

        pattern = re.compile(regex)
        matches = [b for b in j["benchmarks"] if pattern is None or pattern.search(b["name"])]
        means = [b for b in matches if b["name"].endswith("_mean")]
        stddevs = [b for b in matches if b["name"].endswith("_stddev")]
        x = np.array([float(b["strides"]) for b in means])
        y = np.array([float(b["real_time"]) for b in means])
        e = np.array([float(b["real_time"]) for b in stddevs])

        # Rescale
        x *= float(series_spec.get("xscale", 1.0))
        y *= float(series_spec.get("yscale", 1.0))
        e *= float(series_spec.get("yscale", 1.0))

        color = series_spec.get("color", "black")

        # Draw scatter plot of values
        ax.errorbar(x, y, e, capsize=3, ecolor=color, linestyle='None')

        # compute a fit line
        z, _ = np.polyfit(x, y, 1, w=1./e, cov=True)
        slope, intercept = z[0], z[1]
        ax.plot(x, x * slope + intercept, color=color,
                label=label + ": {:.2f}".format(slope) + " us/fault")

    if "yaxis" in ax_spec:
        axis_cfg = ax_spec["yaxis"]
        configure_yaxis(ax, axis_cfg)

    if "xaxis" in ax_spec:
        axis_cfg = ax_spec["xaxis"]
        configure_xaxis(ax, axis_cfg)

    title = ax_spec.get("title", "")
    utils.debug("set title to {}".format(title))
    ax.set_title(title)

    ax.legend()

    return ax


def generate_axes(ax, ax_spec):
    generator_str = ax_spec.get("generator", None)
    if generator_str == "bar":
        ax = generator_bar(ax, ax_spec)
    elif generator_str == "errorbar":
        ax = generator_errorbar(ax, ax_spec)
    elif generator_str == "regplot":
        ax = generator_regplot(ax, ax_spec)
    else:
        raise UnknownGenerator(generator_str)

    return ax


def generate(figure_spec):
    # If there are subplots, apply the generator to each subplot axes
    if "subplots" in figure_spec:
        ax_specs = figure_spec["subplots"]

        # number of subplots in the figure
        num_x = max([int(spec["pos"][0]) for spec in ax_specs])
        num_y = max([int(spec["pos"][1]) for spec in ax_specs])
        fig, axs = plt.subplots(num_y, num_x, sharex='col', sharey='row', squeeze=False)

        # generate each subplot
        for i in range(len(ax_specs)):
            ax_spec = ax_specs[i]
            subplot_x = int(ax_spec["pos"][0]) - 1
            subplot_y = int(ax_spec["pos"][1]) - 1
            ax = axs[subplot_y, subplot_x]
            generate_axes(ax, ax_spec)
    else:
        # otherwise, apply generator to the single figure axes
        # and treat the figure spec as an axes spec as well
        fig, axs = plt.subplots(1, 1, squeeze=False)
        generate_axes(axs[0, 0], figure_spec)

    # Apply any global x and y axis configuration to all axes
    default_x_axis_spec = figure_spec.get("xaxis", {})
    default_y_axis_spec = figure_spec.get("yaxis", {})
    for a in axs:
        for b in a:
            configure_yaxis(b, default_y_axis_spec)
            configure_xaxis(b, default_x_axis_spec)

    # Set the figure size
    fig.set_tight_layout(True)
    fig.autofmt_xdate()
    if "size" in figure_spec:
        figsize = figure_spec["size"]
        utils.debug("Using figsize {}".format(figsize))
        fig.set_size_inches(figsize)

    return fig


# Make some style choices for plotting
color_wheel = [
    "#e9d043",
    "#83c995",
    "#859795",
    "#d7369e",
    "#c4c9d8",
    "#f37738",
    "#7b85d4",
    "#ad5b50",
    "#329932",
    "#ff6961",
    "b",
    "#6a3d9a",
    "#fb9a99",
    "#e31a1c",
    "#fdbf6f",
    "#ff7f00",
    "#cab2d6",
    "#6a3d9a",
    "#ffff99",
    "#b15928",
    "#67001f",
    "#b2182b",
    "#d6604d",
    "#f4a582",
    "#fddbc7",
    "#f7f7f7",
    "#d1e5f0",
    "#92c5de",
    "#4393c3",
    "#2166ac",
    "#053061",
]
dashes_styles = [[3, 1], [1000, 1], [2, 1, 10, 1], [4, 1, 1, 1, 1, 1]]

color_wheel2 = [
    "#000000",
    "#009E73",
    "#e79f00",
    "#9ad0f3",
    "#0072B2",
    "#D55E00",
    "#CC79A7",
    "#F0E442",
]

plt.style.use(
    {
        # "xtick.labelsize": 16,
        # "ytick.labelsize": 16,
        # "font.size": 15,
        "figure.autolayout": True,
        # "figure.figsize": (7.2, 4.45),
        # "axes.titlesize": 16,
        # "axes.labelsize": 17,
        "lines.linewidth": 2,
        # "lines.markersize": 6,
        # "legend.fontsize": 13,
        "mathtext.fontset": "stix",
        "font.family": "STIXGeneral",
    }
)


"""
if __name__ == "__main__":

    if len(sys.argv) == 2:
        output_path = None
        yaml_path = sys.argv[1]
    elif len(sys.argv) == 3:
        output_path = sys.argv[1]
        yaml_path = sys.argv[2]
    else:
        sys.exit(1)

    root_dir = os.path.dirname(os.path.abspath(yaml_path))

    # load the config
    with open(yaml_path, "rb") as f:
        cfg = yaml.load(f)

    if output_path is None and cfg.get("output_file", None) is not None:
        output_path = os.path.join(root_dir, cfg.get("output_file"))
        if not output_path.endswith(".pdf") and not output_path.endswith(".png"):
            base_output_path = output_path
            output_path = []
            for ext in cfg.get("output_format", ["pdf"]):
                ext = ext.lstrip(".")
                output_path.append(base_output_path + "." + ext)

    output_paths = [output_path] if type(output_path) == list() else output_path

    fig = generate(cfg, root_dir)
    if fig is not None:
        # Save plot
        for output_path in output_paths:
            fig.savefig(output_path, clip_on=False, transparent=False)
"""
