#  This causes bokeh.plotting to not refer to this file, bokeh.py
from __future__ import absolute_import


from scope_plot import utils
from scope_plot.schema import validate
from scope_plot import schema
from scope_plot.benchmark import GoogleBenchmark
from voluptuous import Any, Schema, Optional
from bokeh.plotting import figure
from bokeh.io import show
# from bokeh.models import Range1d, Label
# from bokeh.models import scales

def generate_bar(bar_spec, strict):

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

    fig = figure(title=bar_spec["title"],
                 x_axis_label=x_axis_label,
                 y_axis_label=y_axis_label,
                 x_axis_type=x_type,
                 y_axis_type=y_type,
                 x_range=None,
                 y_range=None,
                 plot_width=808,
                 plot_height=int(500/2.0),
                 toolbar_location='above',
                 sizing_mode='scale_width'
    )

    for i, series_spec in enumerate(bar_spec["series"]):

        # validate series_spec
        series_schema = {
            Optional("label", default=""): basestring,
            "label": basestring,
            "input_file": Any(float, int),
            "regex": basestring,
            "xfield": basestring,
            "yfield": basestring,
            "xscale": basestring,
            "yscale": basestring,
        }

        input_path = series_spec.get("input_file", bar_spec.get("input_file", None))
        if not input_path:
            utils.halt("Expected input_file in bar_spec or series_spec")

        regex = series_spec.get("regex", ".*")
        x_field = series_spec.get("xfield", bar_spec["xfield"])
        y_field = series_spec.get("yfield", bar_spec["yfield"])

        utils.debug("Opening {}".format(input_path))
        with GoogleBenchmark(input_path) as b:
            x, y = b.filter_name(regex).fields(x_field, y_field)
            utils.debug("found {} values with regex={} && xfield={} && yfield={}".format(len(x), regex, x_field, y_field))

        fig.vbar(x=x, top=y, width=0.9)

    show(fig)

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

    for plot_spec in figure_spec["subplots"]:
        if "pos" not in plot_spec:
            utils.halt("expected pos key in specification")
        pos = plot_spec["pos"]
        del plot_spec["pos"]
        fig = generate_plot(plot_spec, strict)

