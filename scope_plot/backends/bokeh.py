#  This causes bokeh.plotting to not refer to this file, bokeh.py
from __future__ import absolute_import

from scope_plot import utils
from scope_plot import schema
from scope_plot.benchmark import GoogleBenchmark
from scope_plot import styles
from voluptuous import Any, Schema, Optional, MultipleInvalid
from bokeh.plotting import figure
from bokeh.io import show, export_png, export_svgs
import bokeh.io
from bokeh.layouts import gridplot
from bokeh.transform import dodge
from bokeh.models import ColumnDataSource, Whisker, Range1d, LinearAxis
import pandas as pd
import math

try:
    unicode = unicode
except NameError:
    # 'unicode' is undefined, must be Python 3
    str = str
    unicode = str
    bytes = bytes
    basestring = str
else:
    # 'unicode' exists, must be Python 2
    str = str
    unicode = unicode
    bytes = str
    basestring = basestring


def configure_xaxis(fig, axis_spec):
    if "lim" in axis_spec:
        lim = axis_spec["lim"]
        fig.x_range = Range1d(lim[0], lim[1])
    if "label" in axis_spec:
        fig.xaxis.axis_label = axis_spec["label"]


def configure_yaxis(fig, axis_spec):
    if "lim" in axis_spec:
        lim = axis_spec["lim"]
        fig.y_range = Range1d(lim[0], lim[1])
    if "label" in axis_spec:
        fig.yaxis.axis_label = axis_spec["label"]


def generate_errorbar(errorbar_spec):
    x_type = errorbar_spec.get("xaxis", {}).get("type", "auto")
    y_type = errorbar_spec.get("yaxis", {}).get("type", "auto")

    default_x_scale = errorbar_spec.get("xscale", 1.0)
    default_y_scale = errorbar_spec.get("yscale", 1.0)

    # Create the figure
    fig = figure(
        title=errorbar_spec["title"],
        x_axis_type=x_type,
        y_axis_type=y_type,
        plot_width=808,
        plot_height=int(500 / 2.0),
        toolbar_location='above',
        sizing_mode='scale_width')

    if "xaxis" in errorbar_spec:
        configure_xaxis(fig, errorbar_spec["xaxis"])
    if "yaxis" in errorbar_spec:
        configure_yaxis(fig, errorbar_spec["yaxis"])

    # Read all the series data
    df = pd.DataFrame()
    for i, series_spec in enumerate(errorbar_spec["series"]):

        color = series_spec.get("color", styles.colors[i])

        input_path = series_spec.get("input_file",
                                     errorbar_spec.get("input_file", None))
        regex = series_spec.get("regex", ".*")
        x_field = series_spec.get("xfield", errorbar_spec["xfield"])
        y_field = series_spec.get("yfield", errorbar_spec["yfield"])
        x_scale = series_spec.get("xscale", default_x_scale)
        y_scale = series_spec.get("yscale", default_y_scale)
        label = series_spec.get("label", str(i))

        utils.debug("Opening {}".format(input_path))
        with GoogleBenchmark(input_path) as b:
            df = b.keep_name_regex(regex) \
                  .keep_stats() \
                  .stats_dataframe(x_field, y_field)

            df.loc[:, 'x_mean'] *= eval(str(x_scale))
            df.loc[:, 'x_median'] *= eval(str(x_scale))
            df.loc[:, 'x_stddev'] *= eval(str(x_scale))
            df.loc[:, 'y_mean'] *= eval(str(y_scale))
            df.loc[:, 'y_median'] *= eval(str(y_scale))
            df.loc[:, 'y_stddev'] *= eval(str(y_scale))

            df = df.sort_values(by=['x_mean'])

            fig.line(x=df.loc[:, "x_mean"], y=df.loc[:, "y_mean"], color=color)

            df.loc[:, "lower"] = df.loc[:, 'y_mean'] - df.loc[:, 'y_stddev']
            df.loc[:, "upper"] = df.loc[:, 'y_mean'] + df.loc[:, 'y_stddev']
            error_source = ColumnDataSource(df)

            whisker = Whisker(
                source=error_source,
                base='x_mean',
                upper="upper",
                lower="lower",
                line_color=color)
            whisker.upper_head.line_color = color
            whisker.lower_head.line_color = color
            fig.add_layout(whisker)

    return fig


def generate_bar(bar_spec):

    x_axis_label = bar_spec.get("xaxis", {}).get("label", "")
    y_axis_label = bar_spec.get("yaxis", {}).get("label", "")
    default_x_scale = eval(str(bar_spec.get("xscale", 1.0)))
    default_y_scale = eval(str(bar_spec.get("yscale", 1.0)))
    x_axis_tick_rotation = bar_spec.get("xaxis", {}).get("tick_rotation", 90)

    # convert x axis tick rotation to radians
    x_axis_tick_rotation = x_axis_tick_rotation / 360.0 * 2 * math.pi

    x_type = bar_spec.get("xaxis", {}).get("type", "auto")
    y_type = bar_spec.get("yaxis", {}).get("type", "auto")

    # Read all the series data
    df = pd.DataFrame()
    for i, series_spec in enumerate(bar_spec["series"]):

        input_path = series_spec.get("input_file",
                                     bar_spec.get("input_file", None))
        y_scale = eval(str(series_spec.get("yscale", default_y_scale)))
        x_scale = eval(str(series_spec.get("xscale", default_x_scale)))
        regex = series_spec.get("regex", ".*")
        utils.debug("Using regex {}".format(regex))
        x_field = series_spec.get("xfield", bar_spec["xfield"])
        y_field = series_spec.get("yfield", bar_spec["yfield"])
        label = series_spec.get("label", str(i))

        utils.debug("Opening {}".format(input_path))
        with GoogleBenchmark(input_path) as b:
            new_df = b.keep_name_regex(regex).xy_dataframe(x_field, y_field)
            new_df.loc[:, x_field] *= x_scale
            new_df.loc[:, y_field] *= y_scale
            new_df = new_df.rename(columns={y_field: label})

            new_df = new_df.set_index(x_field)
            df = pd.concat([df, new_df], axis=1, sort=False)

    # convert index to a string
    df.index = df.index.map(str)
    source = ColumnDataSource(data=df)

    source.data[x_field] = map(str, source.data[x_field])
    # Figure out the unique x values that we'll need to plot
    x_range = list(df.index)
    utils.debug("x_range contains {} unique values".format(len(x_range)))

    # Create the figure
    fig = figure(
        title=bar_spec["title"],
        x_axis_label=x_axis_label,
        y_axis_label=y_axis_label,
        x_axis_type=x_type,
        y_axis_type=y_type,
        x_range=x_range,
        plot_width=800,
        plot_height=int(300),
        toolbar_location='above',
    )

    # offset each series
    group_width = 1.0 / (
        len(bar_spec["series"]) + 1
    )  # each group of bars is 1 wide, leave 1 bar-width between groups
    bar_width = group_width * 0.95  # small gap between bars

    # plot the bars
    for i, series_spec in enumerate(bar_spec["series"]):

        color = series_spec.get("color", styles.colors[i])

        dodge_amount = -0.5 + (i + 1) * group_width
        utils.debug("{}".format(dodge_amount))
        fig.vbar(
            x=dodge(x_field, dodge_amount, range=fig.x_range),
            top=series_spec["label"],
            width=bar_width,
            source=source,
            color=color)

    fig.xaxis.major_label_orientation = x_axis_tick_rotation

    return fig


def generate_plot(plot_spec):

    # validate plot_spec
    if "type" not in plot_spec:
        utils.halt("Expected type key in plot_spec")

    type_str = plot_spec['type']
    del plot_spec['type']

    if "bar" == type_str:
        utils.debug("Generating bar plot")
        return generate_bar(plot_spec)
    elif "errorbar" == type_str:
        utils.debug("Generating errorbar plot")
        return generate_errorbar(plot_spec)
    else:
        utils.halt("Unrecognized type: {}".format(type_str))


def generate(figure_spec):

    if "subplots" not in figure_spec:
        utils.halt("expected key subplots in spec")

    # figure out the size of the grid
    num_x = max([int(spec["pos"][0]) for spec in figure_spec["subplots"]])
    num_y = max([int(spec["pos"][1]) for spec in figure_spec["subplots"]])

    grid = [[None for i in range(num_x)] for j in range(num_y)]
    utils.debug("grid: {}".format(grid))

    for plot_spec in figure_spec["subplots"]:

        # propagate fields down to children if children don't override
        for k in ["yaxis", "xaxis"]:
            if k in figure_spec:
                utils.propagate_key_if_missing(figure_spec, k, plot_spec)

        pos = plot_spec["pos"]

        fig = generate_plot(plot_spec)
        grid[pos[1] - 1][pos[0] - 1] = fig

    merge_tools = False  # don't merge child plot tools
    grid = gridplot(grid, merge_tools=merge_tools)

    return grid


def save(fig, paths):
    for path in paths:
        utils.debug("saving matplotlib figure: {}".format(path))
        if path.endswith(".png"):
            export_png(fig, filename=path)
        elif path.endswith(".svg"):
            export_svgs(fig, filename=path)
        elif path.endswith(".html"):
            bokeh.io.output_file(path)
            bokeh.io.save(fig)
        else:
            utils.error("unsupported bokeh output type {}".format(path))