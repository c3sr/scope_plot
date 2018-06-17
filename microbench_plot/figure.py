#! /usr/bin/env python3

import json
import sys
import pprint
import os
import re
import numpy as np
import matplotlib.pyplot as plt
import yaml

pp = pprint.PrettyPrinter(indent=4)


def xprint(*args):
    return

def configure_yaxis(ax, axis_spec):
    if "lim" in axis_spec:
        lim = axis_spec["lim"]
        ax.set_ylim(lim)
    if "label" in axis_spec:
        label = axis_spec["label"]
        ax.set_ylabel(label)
    # ax.yaxis.tick_right()
    # ax.yaxis.set_label_position("right")

def configure_xaxis(ax, axis_spec):
    if "scale" in axis_spec:
        scale = axis_spec["scale"]
        ax.set_xscale(scale, basex=2)
    if "label" in axis_spec:
        label = axis_spec["label"]
        ax.set_xlabel(label)

def generator_bar(ax, yaml_dir, plot_cfg):
    bar_width = plot_cfg.get("bar_width", 0.8)
    num_series = len(plot_cfg["series"])

    default_file = plot_cfg.get("input_file", "not_found")

    default_x_scale = eval(str(plot_cfg.get("xaxis", {}).get("scale", 1.0)))
    default_y_scale = eval(str(plot_cfg.get("yaxis", {}).get("scale", 1.0)))

    default_x_field = plot_cfg.get("xaxis", {}).get("field", "real_time")
    default_y_field = plot_cfg.get("yaxis", {}).get("field", "real_time")

    for c, s in enumerate(plot_cfg["series"]):
        file_path = s.get("input_file", default_file)
        label = s["label"]
        xprint(label)
        regex = s.get("regex", ".*")
        xprint("Using regex:", regex)
        yscale = eval(str(s.get("yscale", default_y_scale)))
        xscale = eval(str(s.get("xscale", default_x_scale)))
        if not os.path.isabs(file_path):
            file_path = os.path.join(yaml_dir, file_path)
        xprint("reading", file_path)
        with open(file_path, "rb") as f:
            j = json.loads(f.read().decode("utf-8"))

        pattern = re.compile(regex)
        matches = [
            b for b in j["benchmarks"] if pattern == None or pattern.search(b["name"])
        ]
        times = matches

        if len(times) == 0:
            continue

        xfield = s.get("xfield", default_x_field)
        x = np.array([float(b[xfield]) for b in times])

        yfield = s.get("yfield", default_y_field)
        y = np.array([float(b[yfield]) for b in times])

        # Rescale
        x *= xscale
        y *= yscale

        # pp.pprint(y)

        ax.bar(x + bar_width * c, y, width=bar_width, label=label, align="center")
        ax.set_xticks(x + 1.5 * bar_width)

        if c == 0:
            ax.set_xticklabels((x + c * bar_width).round(1))
        # ax.bar(x , y, width=bar_width, label=label, align='center')

    if "yaxis" in plot_cfg:
        axis_cfg = plot_cfg["yaxis"]
        if axis_cfg and "lim" in axis_cfg:
            lim = axis_cfg["lim"]
            xprint("setting ylim", lim)
            ax.set_ylim(lim)
        if axis_cfg and "label" in axis_cfg:
            label = axis_cfg["label"]
            xprint("setting ylabel", label)
            ax.set_ylabel(label)

    if "xaxis" in plot_cfg:
        axis_cfg = plot_cfg["xaxis"]
        if axis_cfg and "lim" in axis_cfg:
            lim = axis_cfg["lim"]
            xprint("setting xlim", lim)
            ax.set_xlim(lim)
        if axis_cfg and "scaling_function" in axis_cfg:
            scale = axis_cfg["scaling_function"]
            xprint("setting xscale", scale)
            ax.set_xscale(scale, basex=2)
        if axis_cfg and "label" in axis_cfg:
            label = axis_cfg["label"]
            xprint("setting xlabel", label)
            ax.set_xlabel(label)

    if "title" in plot_cfg:
        title = plot_cfg["title"]
        xprint("setting title", title)
        ax.set_title(title)

    # ax.legend(loc='upper left')
    ax.legend(loc="best")

    return ax

def generator_errorbar(ax, ax_cfg):

    ax.grid(True)

    default_x_field = ax_cfg.get("xaxis", {}).get("field", "bytes")
    default_y_field = ax_cfg.get("yaxis", {}).get("field", "bytes_per_second")

    for i,s in enumerate(ax_cfg["series"]):
        file_path = s["file"]
        label = s["label"]
        regex = s.get("regex", ".*")
        print("Using regex:", regex)
        yscale = float(s.get("yscale", 1.0))
        xscale = float(s.get("xscale", 1.0))
        print("reading", file_path)
        with open(file_path, "rb") as f:
            j = json.loads(f.read().decode('utf-8'))
        
        pattern = re.compile(regex)
        matches = [b for b in j["benchmarks"] if pattern == None or pattern.search(b["name"])]
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
        print("setting title", title)
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
        file_path = series_spec["file"]
        label = series_spec["label"]
        regex = series_spec.get("regex", ".*")
        print("Using regex:", regex)
        print("reading", file_path)
        with open(file_path, "rb") as f:
            j = json.loads(f.read().decode('utf-8'))
        
        pattern = re.compile(regex)
        matches = [b for b in j["benchmarks"] if pattern == None or pattern.search(b["name"])]
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
        style = series_spec.get("style", "-")

        ## Draw scatter plot of values
        ax.errorbar(x, y, e, capsize=3, ecolor=color, linestyle='None')

        ## compute a fit line
        z, cov = np.polyfit(x, y, 1, w=1./e, cov=True)
        print(z)
        slope, intercept = z[0], z[1]
        ax.plot(x, x * slope + intercept, label=label + ": {:.2f}".format(slope) + " us/fault", color=color)


    title = ax_spec.get("title", "")
    print("set title to: ", title)
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
        print("Unepxected axes generator:", generator_str)
        sys.exit(1)

    return ax


def generate(figure_spec):


    # If there are subplots, apply the generator to each subplot axes
    if "subplots" in figure_spec:
        ax_specs = figure_spec["subplots"]

        # Figure out the size of the figure
        num_x = max([int(spec["pos"][0]) for spec in ax_specs])
        num_y = max([int(spec["pos"][1]) for spec in ax_specs])

        fig, axs = plt.subplots(num_y, num_x, sharex='col', sharey='row', squeeze=True)

        for i in range(len(ax_specs)):
            ax_spec = ax_specs[i]
            subplot_x = int(ax_spec["pos"][0]) - 1
            subplot_y = int(ax_spec["pos"][1]) - 1
            ax = axs[subplot_y,subplot_x]
            generate_axes(ax, ax_spec)
    else:
        # otherwise, apply generator to the single figure axes
        fig = plt.figure()
        ax = fig.add_subplot(111)
        generate_axes(fig.axes[0], figure_spec)

    # Apply any global x and y axis configuration to all axes
    default_x_axis_spec = figure_spec.get("xaxis", {})
    default_y_axis_spec = figure_spec.get("yaxis", {})
    for a in axs:
        for b in a:
            configure_yaxis(b, default_y_axis_spec)
            configure_xaxis(b, default_x_axis_spec)

    # Run the axes generators

    fig.set_tight_layout(True)
    fig.autofmt_xdate()

    if "size" in figure_spec:
        figsize = figure_spec["size"]
        print("Using figsize:", figsize)
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

    fig = generate_figure(cfg, root_dir)
    if fig is not None:
        # Save plot
        for output_path in output_paths:
            fig.savefig(output_path, clip_on=False, transparent=False)
