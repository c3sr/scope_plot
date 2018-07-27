#  This causes bokeh.plotting to not refer to this file, bokeh.py
from __future__ import absolute_import


from scope_plot import utils
from scope_plot.schema import validate
from scope_plot import schema
from scope_plot.benchmark import GoogleBenchmark
from voluptuous import Any, Schema, Optional
from bokeh.plotting import figure
from bokeh.io import show
from bokeh.layouts import gridplot
from bokeh.transform import dodge
from bokeh.models import ColumnDataSource
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


def generate_bar(bar_spec, strict):

    bar_width = 0.2

    # validate bar_spec
    bar_schema = {
        Optional("title", default=""): basestring,
        "input_file": basestring,
        "bar_width": Any(float, int),
        Optional("yfield", default="real_time"): basestring,
        Optional("xfield", default="real_time"): basestring,
        "yaxis": schema.AXIS_RAW,
        "xaxis": schema.AXIS_RAW,
        "series": list,
        "yscale": schema.SCALE_RAW,
        "xscale": schema.SCALE_RAW,
        "xtype": basestring,
        "ytype": basestring,
    }
    bar_spec, extras = validate(bar_schema, bar_spec, strict)
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
            new_df = b.filter_name(regex).xy_dataframe(x_field, y_field)
            new_df = new_df.rename(columns={y_field: label})
            print(new_df)
            df = pd.concat([df, new_df], axis=1, sort=True)
            # utils.debug("found {} values with regex={} && xfield={} && yfield={}".format(len(x), regex, x_field, y_field))
            # series_x_data += [x]
            # series_y_data += [y]


    df.index = df.index.map(str)
    print(df)
    source = ColumnDataSource(data=df)
    print(source)
    print(source.data)

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
    lane_width = 1 / (len(bar_spec["series"]) + 1) # bar width plus spacing
    bar_width = lane_width * 0.95

    dodge_each = lane_width
    dodge_total = len(series_x_data) * dodge_each

    # plot the bars
    for i, series_spec in enumerate(bar_spec["series"]):
        # fig.vbar(x=[str(e) for e in series_x_data[i]], top=y, width=bar_width)
        dodge_amount = -0.5 + (i+1) * lane_width
        fig.vbar(x=dodge('num_segments', dodge_amount, range=fig.x_range), top=series_spec["label"], width=bar_width, source=source)

    return fig

def generate_plot(plot_spec, strict):

    # validate plot_spec
    if "type" not in plot_spec:
        utils.halt("Expected type key in plot_spec")

    type_str = plot_spec['type']
    del plot_spec['type']

    if type_str == "bar":
        fig = generate_bar(plot_spec, strict)
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

    for plot_spec in figure_spec["subplots"]:
        if "pos" not in plot_spec:
            utils.halt("expected pos key in specification")
        pos = plot_spec["pos"]
        del plot_spec["pos"]
        fig = generate_plot(plot_spec, strict)
        grid[pos[1]-1][pos[0]-1] = fig

    grid = gridplot(grid)
    show(grid)
