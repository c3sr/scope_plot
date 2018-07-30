#  This causes bokeh.plotting to not refer to this file, bokeh.py
from __future__ import absolute_import


from scope_plot import utils
from scope_plot.schema import validate
from scope_plot import schema
from scope_plot.benchmark import GoogleBenchmark
from scope_plot import styles
from voluptuous import Any, Schema, Optional
from bokeh.plotting import figure
from bokeh.io import show
from bokeh.layouts import gridplot
from bokeh.transform import dodge
from bokeh.models import ColumnDataSource, Whisker
import pandas as pd

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

def generate_errorbar(errorbar_spec, strict):

    errorbar_spec, extras = validate(schema.ERRORBAR_RAW, errorbar_spec, strict)
    if not strict:
        utils.warn("Found extras {} in errorbar_spec".format(extras))

    x_axis_label = errorbar_spec.get("xaxis", {}).get("label", "")
    y_axis_label = errorbar_spec.get("yaxis", {}).get("label", "")
    x_type = errorbar_spec.get("xaxis", {}).get("type", "auto")
    y_type = errorbar_spec.get("yaxis", {}).get("type", "auto")

    # Create the figure
    fig = figure(title=errorbar_spec["title"],
                 x_axis_label=x_axis_label,
                 y_axis_label=y_axis_label,
                 x_axis_type=x_type,
                 y_axis_type=y_type,
                 plot_width=808,
                 plot_height=int(500/2.0),
                 toolbar_location='above',
                 sizing_mode='scale_width'
    )

    # Read all the series data
    df = pd.DataFrame()
    for i, series_spec in enumerate(errorbar_spec["series"]):
        schema.validate(schema.SERIES_RAW, series_spec, strict)

        color = series_spec.get("color", styles.colors[i % len(styles.colors)])

        input_path = series_spec.get("input_file", errorbar_spec.get("input_file", None))
        regex = series_spec.get("regex", ".*")
        x_field = series_spec.get("xfield", errorbar_spec["xfield"])
        y_field = series_spec.get("yfield", errorbar_spec["yfield"])
        label = series_spec.get("label", str(i))

        utils.debug("Opening {}".format(input_path))
        with GoogleBenchmark(input_path) as b:
            df = b.keep_name_regex(regex) \
                  .keep_stats() \
                  .stats_dataframe(x_field, y_field)

            df = df.sort_values(by=['x_mean'])

            fig.line(x=df.loc[:, "x_mean"], y=df.loc[:, "y_mean"], color=color)

            df.loc[:, "lower"] = df.loc[:, 'y_mean'] - df.loc[:, 'y_stddev']
            df.loc[:, "upper"] = df.loc[:, 'y_mean'] + df.loc[:, 'y_stddev']
            error_source = ColumnDataSource(df)

            whisker = Whisker(source=error_source, base='x_mean', upper="upper", lower="lower", line_color=color)
            whisker.upper_head.line_color = color
            whisker.lower_head.line_color = color
            fig.add_layout(whisker)

    return fig



def generate_bar(bar_spec, strict):

    bar_width = 0.2

    bar_spec, extras = validate(schema.BAR_RAW, bar_spec, strict)
    if not strict:
        utils.warn("Found extras {} in bar_spec".format(extras))

    xaxis_spec, extras = validate(schema.AXIS_RAW, bar_spec["xaxis"], strict)
    if not strict:
        utils.warn("Found extras {} in xaxis_spec".format(extras))

    yaxis_spec, extras = validate(schema.AXIS_RAW, bar_spec["yaxis"], strict)
    if not strict:
        utils.warn("Found extras {} in yaxis_spec".format(extras))

    x_axis_label = bar_spec.get("xaxis", {}).get("label", "")
    y_axis_label = bar_spec.get("yaxis", {}).get("label", "")
    x_type = bar_spec.get("xtype", "auto")
    y_type = bar_spec.get("ytype", "auto")


    # Read all the series data
    series_x_data = []
    series_y_data = []
    df = pd.DataFrame()
    for i, series_spec in enumerate(bar_spec["series"]):

        schema.validate(schema.SERIES_RAW, series_spec, strict)

        input_path = series_spec.get("input_file", bar_spec.get("input_file", None))
        regex = series_spec.get("regex", ".*")
        x_field = series_spec.get("xfield", bar_spec["xfield"])
        y_field = series_spec.get("yfield", bar_spec["yfield"])
        label = series_spec.get("label", str(i))

        utils.debug("Opening {}".format(input_path))
        with GoogleBenchmark(input_path) as b:
            new_df = b.keep_name_regex(regex).xy_dataframe(x_field, y_field)
            new_df = new_df.rename(columns={y_field: label})
            print(new_df)
            df = pd.concat([df, new_df], axis=1, sort=True)


    df.index = df.index.map(str)
    source = ColumnDataSource(data=df)

    # Figure out the union of the x fields we want:

    x_range = list(df.index)
    utils.debug("x_range contains {} unique values".format(len(x_range)))
    # x_range = [str(e) for e in sorted(list(x_range))]

    # Create the figure
    fig = figure(title=bar_spec["title"],
                 x_axis_label=x_axis_label,
                 y_axis_label=y_axis_label,
                 x_axis_type=x_type,
                 y_axis_type=y_type,
                 x_range=x_range,
                 plot_width=808,
                 plot_height=int(500/2.0),
                 toolbar_location='above',
                 sizing_mode='scale_width'
    )

    # offset each series
    lane_width = 1 / (len(bar_spec["series"]) + 1) # each group of bars is 1 wide, leave 1 bar-width between groups
    bar_width = lane_width * 0.95 # small gap between bars

    dodge_each = lane_width
    dodge_total = len(series_x_data) * dodge_each

    # plot the bars
    for i, series_spec in enumerate(bar_spec["series"]):
        dodge_amount = -0.5 + (i+1) * lane_width
        fig.vbar(x=dodge('num_segments', dodge_amount, range=fig.x_range), top=series_spec["label"], width=bar_width, source=source)

    return fig

def generate_plot(plot_spec, strict):

    # validate plot_spec
    if "type" not in plot_spec:
        utils.halt("Expected type key in plot_spec")

    type_str = plot_spec['type']
    del plot_spec['type']

    if "bar" == type_str:
        fig = generate_bar(plot_spec, strict)
    elif "errorbar" == type_str:
        fig = generate_errorbar(plot_spec, strict)
    else:
        utils.halt("Unrecognized type: {}".format(type_str))

    return fig



def generate(figure_spec, strict):

    if "subplots" not in figure_spec:
        utils.halt("expected key subplots in spec")

    # figure out the size of the grid
    num_x = max([int(spec["pos"][0]) for spec in figure_spec["subplots"]])
    num_y = max([int(spec["pos"][1]) for spec in figure_spec["subplots"]])

    grid = [[None for i in range(num_x)] for j in range(num_y)]
    utils.debug("grid: {}".format(grid))

    for plot_spec in figure_spec["subplots"]:
        if "pos" not in plot_spec:
            utils.halt("expected pos key in specification")
        pos = plot_spec["pos"]
        del plot_spec["pos"]
        fig = generate_plot(plot_spec, strict)
        grid[pos[1]-1][pos[0]-1] = fig

    grid = gridplot(grid)
    show(grid)
