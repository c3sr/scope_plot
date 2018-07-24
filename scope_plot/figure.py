import json
import sys
import pprint
import os
import re
import numpy as np
import matplotlib.pyplot as plt
import yaml
from future.utils import iteritems

from scope_plot import utils
from scope_plot.error import UnknownGenerator


pp = pprint.PrettyPrinter(indent=4)
plt.switch_backend('agg')


def configure_yaxis(ax, axis_spec, strict):
    for key, value in iteritems(axis_spec):
        if "lim" == key:
            ax.set_ylim(value)
        elif "label" == key:
            ax.set_ylabel(value)
        elif "scale" == key:
            utils.debug("seting y axis scale: {}".format(value))
            ax.set_yscale(value, basey=10)
        elif strict:
            utils.halt("unrecognized key {} in yaxis spec: {}".format(key, axis_spec))
        else:
            utils.debug("unrecognized key {} in yaxis spec: {}".format(key, axis_spec))


def configure_xaxis(ax, axis_spec, strict):
    for key, value in iteritems(axis_spec):
        if "scale" == key:
            utils.debug("seting x axis scale: {}".format(value))
            ax.set_xscale(value, basex=2)
        elif "label" in axis_spec:
            ax.set_xlabel(value)
        elif "lim" in axis_spec:
            ax.set_xlim(value)
        elif strict:
            utils.halt("unrecognized key {} in xaxis spec: {}".format(key, axis_spec))
        else:
            utils.debug("unrecognized key {} in xaxis spec: {}".format(key, axis_spec))


def generator_bar(ax, ax_cfg, strict):

    # set defaults
    bar_width = 0.8
    default_file = "not_found"
    default_x_scale = 1.0
    default_y_scale = 1.0
    default_x_field = "real_time"
    default_y_field = "real_time"
    series_cfgs = []
    title = None
    yaxis_cfg = {}
    xaxis_cfg = {}

    # Parse config
    consume_keys = []
    for key, value in iteritems(ax_cfg):
        if key == "bar_width":
            bar_width = value
        elif key == "series":
            series_cfgs = value
        elif key == "input_file":
            default_file = value
        elif key == "xscale":
            default_x_scale = eval(str(value))
        elif key == "yscale":
            default_y_scale = eval(str(value))
        elif key == "xfield":
            default_x_field = value
        elif key == "yfield":
            default_y_field = value
        elif key == "title":
            title = value
        elif key == "yaxis":
            yaxis_cfg = value
        elif key == "xaxis":
            xaxis_cfg = value
        elif strict:
            utils.halt("unrecognized key {} in bar ax_cfg".format(key))
        else:
            utils.debug("unrecognized key {} in bar ax_cfg".format(key))
        consume_keys += [key]

    # consume config entries
    for key in consume_keys:
        del ax_cfg[key]

    # Generate figure

    num_series = len(series_cfgs)
    utils.debug("Number of series: {}".format(num_series))

    for c, s in enumerate(series_cfgs):
        # defaults
        file_path = default_file
        label = ""
        regex = ".*"
        xfield = default_x_field
        yfield = default_y_field
        xscale = default_x_scale
        yscale = default_y_scale

        # parse config
        for key, value in iteritems(s):
            if key == "input_file":
                file_path = value
            elif key == "label":
                label = value
            elif key == "regex":
                regex = value
            elif key == "xfield":
                xfield = value
            elif key == "yfield":
                yfield = value
            elif key == "xscale":
                xscale = eval(str(value))
            elif key == "yscale":
                yscale = eval(str(value))
            elif strict:
                utils.halt("unrecognized key {} in bar ax_cfg".format(key))
            else:
                utils.debug("unrecognized key {} in bar ax_cfg".format(key))

        # generate series

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

        utils.debug("series {}: x field: {}".format(c, xfield))
        utils.debug("series {}: y field: {}".format(c, yfield))

        # extract data
        x = np.array([float(b[xfield]) for b in matches])
        y = np.array([float(b[yfield]) for b in matches])

        # Rescale
        utils.debug("series {}: x scale={} yscale={}".format(c, xscale, yscale))
        x *= xscale
        y *= yscale

        # sort by x
        x, y = zip(*sorted(zip(x.tolist(), y.tolist())))
        x = np.array(x)
        y = np.array(y)

        ind = np.arange(len(x))
        utils.debug("ind: {}".format(ind))
        utils.debug("x: {}".format(x))
        utils.debug("y: {}".format(y))

        ax.bar(ind + bar_width * c, y, width=bar_width, label=label, align="center")

    ax.set_xticks(ind + bar_width * (len(series_cfgs) - 1) / 2)
    # ax.set_xticklabels((x + bar_width * len(series_cfgs)).round(1))
    ax.set_xticklabels(x.round(2))

    configure_yaxis(ax, yaxis_cfg, strict)
    configure_xaxis(ax, xaxis_cfg, strict)

    if title:
        ax.set_title(title)

    # ax.legend(loc='upper left')
    ax.legend(loc="best")

    return ax


def generator_errorbar(ax, ax_cfg, strict):

    ax.grid(True)

    # defaults
    default_x_field = "bytes"
    default_y_field = "bytes_per_second"
    xaxis_spec = {}
    yaxis_spec = {}
    series = None
    title = None

    # parse config
    consume_keys = []
    for key, value in iteritems(ax_cfg):
        if key == "series":
            series_specs = value
        elif key == "title":
            title = value
        elif key == "xaxis":
            xaxis_spec = value
        elif key == "yaxis":
            yaxis_spec = value
        elif key == "xfield":
            default_x_field = value
        elif key == "yfield":
            default_y_field = value
        elif key == "title":
            title = value
        elif strict:
            utils.halt("unrecognized key {} in errorbar ax_cfg".format(key))
        else:
            utils.debug("unrecognized key {} in errorbar ax_cfg".format(key))
        consume_keys += [key]
    for key in consume_keys:
        del ax_cfg[key]

    for i, s in enumerate(series_specs):
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

        # sort by x
        x, y, e = zip(*sorted(zip(x.tolist(), y.tolist(), e.tolist())))
        x = np.array(x)
        y = np.array(y)
        e = np.array(e)

        # pp.pprint(means)
        if "color" in s:
            color = s["color"]
        else:
            color = color_wheel[i]
        ax.errorbar(x, y, e, capsize=3, label=label, color=color)

    if title:
        ax.set_title(title)

    configure_yaxis(ax, yaxis_spec, strict)
    configure_xaxis(ax, xaxis_spec, strict)

    ax.legend(loc="best")

    return ax


def generator_regplot(ax, ax_spec, strict):

    # defaults
    series_specs = None
    title = ""
    xaxis_spec = {}
    yaxis_spec = {}

    # parse config
    consume_keys = []
    for key, value in iteritems(ax_spec):
        if key == "series":
            series_specs = value
        elif key == "title":
            title = value
        elif key == "xaxis":
            xaxis_spec = value
        elif key == "yaxis":
            yaxis_spec = value
        elif strict:
            utils.halt("unrecognized key {} in regplot ax_spec".format(key))
        else:
            utils.debug("unrecognized key {} in regplot ax_spec".format(key))
        consume_keys += [key]
    for key in consume_keys:
        del ax_spec[key]

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

        # sort by x
        x, y, e = zip(*sorted(zip(x.tolist(), y.tolist(), e.tolist())))
        x = np.array(x)
        y = np.array(y)
        e = np.array(e)

        color = series_spec.get("color", "black")

        # Draw scatter plot of values
        ax.errorbar(x, y, e, capsize=3, ecolor=color, linestyle='None')

        # compute a fit line
        z, _ = np.polyfit(x, y, 1, w=1./e, cov=True)
        slope, intercept = z[0], z[1]
        ax.plot(x, x * slope + intercept, color=color,
                label=label + ": {:.2f}".format(slope) + " us/fault")

    configure_yaxis(ax, yaxis_spec, strict)
    configure_xaxis(ax, xaxis_spec, strict)

    utils.debug("set title to {}".format(title))
    ax.set_title(title)

    ax.legend()

    return ax


def generate_axes(ax, ax_spec, strict):
    generator_str = ax_spec.get("generator", None)

    if generator_str:
        del ax_spec["generator"]

    if generator_str == "bar":
        ax = generator_bar(ax, ax_spec, strict)
    elif generator_str == "errorbar":
        ax = generator_errorbar(ax, ax_spec, strict)
    elif generator_str == "regplot":
        ax = generator_regplot(ax, ax_spec, strict)
    else:
        raise UnknownGenerator(generator_str)

    return ax


def generate_subplots(figure_spec, strict):
    # defaults
    default_x_axis_spec = {}
    default_y_axis_spec = {}
    subplots = None

    # parse figure_spec
    consume_keys = []
    for key, value in iteritems(figure_spec):
        if key == "xaxis":
            default_x_axis_spec = value
        elif key == "yaxis":
            default_y_axis_spec = value
        elif key == "size":
            fig_size = value
        elif key == "subplots":
            subplots = value
        elif strict:
            utils.halt("unrecognized key {} in figure_spec".format(key))
        else:
            utils.debug("unrecognized key {} in figure_spec".format(key))
        consume_keys += [key]

    # delete consumed specs
    for key in consume_keys:
        del figure_spec[key]

    ax_specs = subplots

    for spec in ax_specs:
        assert "pos" in spec

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
        del ax_spec["pos"]
        generate_axes(ax, ax_spec, strict)

    # Apply any global x and y axis configuration to all axes
    for a in axs:
        for b in a:
            configure_yaxis(b, default_y_axis_spec, strict)
            configure_xaxis(b, default_x_axis_spec, strict)

    return fig


def generate(figure_spec, strict):

    fig_size = None
    if "size" in figure_spec:
        fig_size = figure_spec["size"]
        del figure_spec["size"]

    if "subplots" in figure_spec:
        fig = generate_subplots(figure_spec, strict)
    else:
        fig, axs = plt.subplots(1, 1, squeeze=False)
        generate_axes(axs[0, 0], figure_spec, strict)

    consume_keys = []
    for key, value in iteritems(figure_spec):
        if strict:
            utils.halt("unrecognized key {} in figure_spec".format(key))
        else:
            utils.debug("unrecognized key {} in figure_spec".format(key))
        consume_keys += [key]
    for key in consume_keys:
        del figure_spec[key]

    # Set the figure size
    fig.set_tight_layout(True)
    fig.autofmt_xdate()
    if fig_size:
        utils.debug("Using figsize {}".format(fig_size))
        fig.set_size_inches(fig_size)

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
