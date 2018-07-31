from __future__ import absolute_import

import json
import sys
import pprint
import os
import re
import numpy as np
import matplotlib.pyplot as plt
import yaml
from future.utils import iteritems
import pandas as pd

from scope_plot import utils
from scope_plot.error import UnknownGenerator
from scope_plot.schema import validate
from scope_plot import schema
from scope_plot.benchmark import GoogleBenchmark
from scope_plot import styles

# plt.switch_backend('agg')

def configure_yaxis(ax, axis_spec):
    if "lim" in axis_spec:
        ax.set_ylim(axis_spec["lim"])
    if "label" in axis_spec:
        ax.set_ylabel(axis_spec["label"])
    if "type" in axis_spec:
        value = axis_spec["type"]
        utils.debug("seting y axis scale: {}".format(value))
        ax.set_yscale(value, basey=10)


def configure_xaxis(ax, axis_spec):
    if "lim" in axis_spec:
        ax.set_xlim(axis_spec["lim"])
    if "label" in axis_spec:
        ax.set_xlabel(axis_spec["label"])
    if "type" in axis_spec:
        value = axis_spec["type"]
        utils.debug("seting x axis scale: {}".format(value))
        ax.set_xscale(value, basex=2)


def generator_bar(ax, ax_cfg):

    bar_width = ax_cfg.get("bar_width", 0.8)
    default_file = ax_cfg.get("input_file", None)
    default_x_scale = eval(str(ax_cfg.get("xscale", 1.0)))
    default_y_scale = eval(str(ax_cfg.get("yscale", 1.0)))
    default_x_field = ax_cfg.get("xfield", None)
    default_y_field = ax_cfg.get("yfield", None)
    series_specs = ax_cfg["series"]


    utils.debug("Number of series: {}".format(len(series_specs)))

    df = pd.DataFrame()
    for i, series_spec in enumerate(series_specs):
        # defaults
        input_path = default_file
        label = series_spec.get("label", str(i))
        regex = series_spec.get("regex", ".*")
        y_field = series_spec.get("yfield", default_y_field)
        x_field = series_spec.get("yfield", default_x_field)
        y_scale = eval(str(series_spec.get("yscale", default_y_scale)))
        x_scale = eval(str(series_spec.get("xscale", default_x_scale)))
        input_path = series_spec.get("input_file", default_file)
        utils.require(input_path, "input_file should have been defined")

        utils.debug("series {}: Opening {}".format(i, input_path))

        utils.debug("series {}: filter regex is {}".format(i, regex))
        utils.debug("series {}: x field: {}".format(i, x_field))
        utils.debug("series {}: y field: {}".format(i, y_field))

        with GoogleBenchmark(input_path) as b:
            series_df = b.keep_name_regex(regex).xy_dataframe(x_field, y_field)
            series_df.index *= x_scale
            series_df.loc[:, y_field] *= y_scale
            series_df = series_df.rename(columns={y_field: label})

            df = pd.concat([df, series_df], axis=1, sort=True)

    print(df)
    # convert index to a string
    df.index = df.index.map(str)

    # Figure out the unique x values that we'll need to plot
    x_range = list(df.index)

    ax = df.plot(kind='bar')

    if "xaxis" in ax_cfg:
        configure_yaxis(ax, ax_cfg["yaxis"])
    if "yaxis" in ax_cfg:
        configure_xaxis(ax, ax_cfg["xaxis"])

    if "title" in ax_cfg:
        ax.set_title(ax_cfg["title"])

    # ax.legend(loc='upper left')
    ax.legend(loc="best")

    return ax


def generator_errorbar(ax, ax_cfg):
    default_input_file = ax_cfg.get("input_file", None)
    default_x_field = ax_cfg.get("xfield", None)
    default_y_field = ax_cfg.get("yfield", None)
    series_specs = ax_cfg["series"]

    for i, series_spec in enumerate(series_specs):
        file_path = series_spec.get("input_file", default_input_file)
        label = series_spec["label"]
        regex = series_spec.get("regex", ".*")
        yscale = eval(str(series_spec.get("yscale", 1.0)))
        xscale = eval(str(series_spec.get("xscale", 1.0)))
        x_field = series_spec.get("xfield", default_x_field)
        y_field = series_spec.get("yfield", default_y_field)
        utils.debug("series {}: opening {}".format(i, file_path))

        with GoogleBenchmark(file_path) as g:
            stats = g.keep_name_regex(regex).keep_stats()
            df = stats.stats_dataframe(x_field, y_field)
            df = df.sort_values(by=["x_mean"])
            x = df.loc[:, "x_mean"]
            y = df.loc[:, "y_mean"]
            e = df.loc[:, "y_stddev"]

        # Rescale
        x *= xscale
        y *= yscale
        e *= yscale

        color = series_spec.get("color", styles.colors[i])
        ax.errorbar(x, y, e, capsize=3, label=label, color=color)

    if "title" in ax_cfg:
        ax.set_title(ax_cfg["title"])
    if "yaxis" in ax_cfg:
        configure_yaxis(ax, ax_cfg["yaxis"])
    if "xaxis" in ax_cfg:
        configure_xaxis(ax, ax_cfg["xaxis"])

    ax.legend(loc="best")
    ax.grid(True)

    return ax


def generator_regplot(ax, ax_spec):

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

        def show_func(b):
            if "strides" in b and "real_time" in b and "error_message" not in b:
                return True
            return False
        x = np.array(list(map(lambda b: float(b["strides"]), filter(show_func, means))))
        y = np.array(list(map(lambda b: float(b["real_time"]), filter(show_func, means))))
        e = np.array(list(map(lambda b: float(b["real_time"]), filter(show_func, stddevs))))

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

    configure_yaxis(ax, yaxis_spec)
    configure_xaxis(ax, xaxis_spec)

    utils.debug("set title to {}".format(title))
    ax.set_title(title)

    ax.legend()

    return ax


def generate_axes(ax, ax_spec):
    ty = ax_spec["type"]
    if ty== "bar":
        ax = generator_bar(ax, ax_spec)
    elif ty== "errorbar":
        ax = generator_errorbar(ax, ax_spec)
    elif ty== "regplot":
        ax = generator_regplot(ax, ax_spec)
    else:
        raise UnknownGenerator(ty)
    return ax


def generate_subplots(figure_spec):
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
        generate_axes(ax, ax_spec)

    # Apply any global x and y axis configuration to all axes
    for a in axs:
        for b in a:
            configure_yaxis(b, default_y_axis_spec)
            configure_xaxis(b, default_x_axis_spec)

    return fig


def generate(figure_spec):

    fig_size = None
    if "size" in figure_spec:
        fig_size = figure_spec["size"]

    if "subplots" in figure_spec:
        fig = generate_subplots(figure_spec)
    else:
        fig, axs = plt.subplots(1, 1, squeeze=False)
        generate_axes(axs[0, 0], figure_spec)

    # Set the figure size
    fig.set_tight_layout(True)
    fig.autofmt_xdate()
    if fig_size:
        utils.debug("Using figsize {}".format(fig_size))
        fig.set_size_inches(fig_size)

    fig.show()
    plt.show()

    return fig


"""
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