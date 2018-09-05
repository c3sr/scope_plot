from __future__ import absolute_import

import sys
import os
if sys.platform == "darwin":
    import matplotlib
    matplotlib.use("TkAgg")
if 'DISPLAY' not in os.environ:
    import matplotlib
    matplotlib.use("agg")

import json
import pprint
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


def configure_yaxis(ax, axis_spec):
    if "lim" in axis_spec:
        ax.set_ylim(axis_spec["lim"])
    if "label" in axis_spec:
        ax.set_ylabel(axis_spec["label"])
    if "type" in axis_spec:
        value = axis_spec["type"]
        utils.debug("seting y axis type: {}".format(value))
        ax.set_yscale(value, basey=10)


def configure_xaxis(ax, axis_spec):
    if "lim" in axis_spec:
        ax.set_xlim(axis_spec["lim"])
    if "label" in axis_spec:
        ax.set_xlabel(axis_spec["label"])
    if "type" in axis_spec:
        value = axis_spec["type"]
        utils.debug("seting x axis type: {}".format(value))
        ax.set_xscale(value, basex=2)


def generator_bar(ax, ax_cfg):

    bar_width = ax_cfg.get("bar_width", 0.8)
    series_specs = ax_cfg.series
    utils.debug("Number of series: {}".format(len(series_specs)))

    df = pd.DataFrame()
    for i, series_spec in enumerate(series_specs):
        input_path = series_spec.input_file()
        label = series_spec.label_or(str(i))
        regex = series_spec.regex()
        y_field = series_spec.yfield()
        x_field = series_spec.xfield()
        y_scale = series_spec.yscale()
        x_scale = series_spec.xscale()
        input_path = series_spec.input_file()
        utils.require(input_path, "input_file should have been defined")
        utils.require(y_field, "yfield should have been defined")
        utils.require(x_field, "xfield should have been defined")

        utils.debug("series {}: Opening {}".format(i, input_path))
        utils.debug("series {}: filter regex is {}".format(i, regex))
        utils.debug("series {}: x field: {}".format(i, x_field))
        utils.debug("series {}: y field: {}".format(i, y_field))
        if x_scale != 1:
            utils.debug("series {}: xscale: {}".format(i, x_scale))
        if y_scale != 1:
            utils.debug("series {}: yscale: {}".format(i, y_scale))

        with GoogleBenchmark(input_path) as b:
            matches = b.keep_name_regex(regex)
            for entry in matches.benchmarks:
                utils.debug("name {} matched regex {}".format(entry["name"], regex))
            series_df = matches.xy_dataframe(x_field, y_field)

        if series_df.dtypes[x_field] == np.object:
            utils.debug("Not scaling non-numeric x data by {}".format(x_scale))
        else:
            series_df.loc[:, x_field] *= x_scale
        series_df.loc[:, y_field] *= y_scale
        series_df = series_df.rename(columns={y_field: label})
        series_df = series_df.set_index(x_field)

        # FIXME: this could be resolved with join?
        # https://stackoverflow.com/questions/27719407/pandas-concat-valueerror-shape-of-passed-values-is-blah-indices-imply-blah2
        if not series_df.index.is_unique:
            utils.warn(
                "multiple benchmark results with identical {} values. The plot might be weird.".format(
                    x_field))
        df = pd.concat([df, series_df], axis=1, sort=False)
    df = df.sort_index()

    df.plot.bar(ax=ax)

    if "xaxis" in ax_cfg:
        configure_yaxis(ax, ax_cfg["yaxis"])
    if "yaxis" in ax_cfg:
        configure_xaxis(ax, ax_cfg["xaxis"])

    if "title" in ax_cfg:
        ax.set_title(ax_cfg["title"])

    ax.legend(loc="best")

    return ax


def generator_errorbar(ax, ax_cfg):
    series_specs = ax_cfg.series

    for i, series_spec in enumerate(series_specs):
        file_path = series_spec.input_file()
        label = series_spec.label_or(str(i))
        regex = series_spec.regex()
        yscale = series_spec.yscale()
        xscale = series_spec.xscale()
        x_field = series_spec.xfield()
        y_field = series_spec.yfield()
        utils.debug("series {}: opening {}".format(i, file_path))

        with GoogleBenchmark(file_path) as g:
            stats = g.keep_name_regex(regex).keep_stats()
            df = stats.stats_dataframe(x_field, y_field)
            df = df.sort_values(by=["x_mean"])
        x = df.loc[:, "x_mean"]
        y = df.loc[:, "y_mean"]
        e = df.loc[:, "y_stddev"]

        x *= xscale
        y *= yscale
        e *= yscale

        color = series_spec.color_or(styles.colors[i])
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

    series_specs = ax_spec.series

    for i, series_spec in enumerate(series_specs):
        file_path = series_spec.input_file()
        label = series_spec.label_or(str(i))
        regex = series_spec.regex()
        yscale = series_spec.yscale()
        xscale = series_spec.xscale()
        x_field = series_spec.xfield()
        y_field = series_spec.yfield()
        utils.debug("series {}: opening {}".format(i, file_path))

        with GoogleBenchmark(file_path) as g:
            stats = g.keep_name_regex(regex).keep_stats()
            df = stats.stats_dataframe(x_field, y_field)
            df = df.sort_values(by=["x_mean"])
        x = df.loc[:, "x_mean"]
        y = df.loc[:, "y_mean"]
        e = df.loc[:, "y_stddev"]

        x *= xscale
        y *= yscale
        e *= yscale

        color = series_spec.color_or(styles.colors[i])

        # Draw scatter plot of values
        ax.errorbar(
            x, y, e, capsize=3, ecolor=color, linestyle='None', label=None)

        # compute a fit line and show
        z, _ = np.polyfit(x, y, 1, w=1. / e, cov=True)
        slope, intercept = z[0], z[1]
        ax.plot(
            x,
            x * slope + intercept,
            color=color,
            label=label + ": {:.2f}".format(slope) + " us/fault")

    if "title" in ax_spec:
        ax.set_title(ax_spec["title"])
    if "yaxis" in ax_spec:
        configure_yaxis(ax, ax_spec["yaxis"])
    if "xaxis" in ax_spec:
        configure_xaxis(ax, ax_spec["xaxis"])

    ax.legend(loc="best")
    ax.grid(True)

    return ax


def generate_axes(ax, ax_spec):
    ty = ax_spec.ty()
    if ty == "bar":
        ax = generator_bar(ax, ax_spec)
    elif ty == "errorbar":
        ax = generator_errorbar(ax, ax_spec)
    elif ty == "regplot":
        ax = generator_regplot(ax, ax_spec)
    else:
        raise UnknownGenerator(ty)
    return ax


def generate_subplots(figure_spec):
    default_x_axis_spec = figure_spec.get("xaxis", {})
    default_y_axis_spec = figure_spec.get("yaxis", {})

    ax_specs = figure_spec.subplots

    for spec in ax_specs:
        assert "pos" in spec

    # number of subplots in the figure
    num_x = max([int(spec["pos"][0]) for spec in ax_specs])
    num_y = max([int(spec["pos"][1]) for spec in ax_specs])
    fig, axs = plt.subplots(
        num_y, num_x, sharex='col', sharey='row', squeeze=False)

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

    fig = generate_subplots(figure_spec)

    # Set the figure size
    # fig.autofmt_xdate()
    if "size" in figure_spec:
        size = figure_spec["size"]
        utils.debug("Using figsize {}".format(size))
        fig.set_size_inches(size)
    fig.set_tight_layout(True)

    return fig


def run(job):
    figure_spec = job.figure_spec
    fig = generate(figure_spec)
    if not fig:
        utils.halt("Unable to generate figure")
    save(fig, job.path)


def save(fig, path):
    utils.debug("saving matplotlib figure: {}".format(path))
    fig.savefig(path, clip_on=False, transparent=False)
