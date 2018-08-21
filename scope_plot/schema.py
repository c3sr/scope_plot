from future.utils import iteritems
from voluptuous import All, Any, Schema, Optional, Required, ALLOW_EXTRA, REMOVE_EXTRA, PREVENT_EXTRA, Invalid

from scope_plot.error import NoBackendError
from scope_plot import utils

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

AXIS = Schema({
    Optional('label'): basestring,
    Optional('lim'): list,
    Optional('tick_rotation'): Any(float, int),
    Optional('type'): basestring,
})

COLOR = Any(basestring, float, int)
EVAL = Any(basestring, float, int)

SERIES_SCHEMA = Schema({
    Optional("label"): basestring,
    Optional("input_file"): basestring,
    Optional("regex"): basestring,
    Optional("xfield"): basestring,
    Optional("yfield"): basestring,
    Optional("xscale"): EVAL,
    Optional("yscale"): EVAL,
    Optional("color"): COLOR,
    Optional("tick_seperator"): basestring,
    Optional("tick_fields"): list,
})

POS = list
SIZE = list

BACKEND = Any("bokeh", "matplotlib")
TYPE = Any("errorbar", "bar", "regplot")

FILES_SCHEMA = Schema({
    Required("backend"): BACKEND,
    Required("extension"): basestring,
})

OUTPUT = Schema({
    Optional("name"): basestring,
    Required("files"): [FILES_SCHEMA],
})

PLOT_FIELDS = Schema({
    Required("type"): TYPE,
    Optional("title"): basestring,
    Optional("input_file"): basestring,
    Optional("yfield"): basestring,
    Optional("xfield"): basestring,
    Optional("yaxis"): AXIS,
    Optional("xaxis"): AXIS,
    Optional("series"): [SERIES_SCHEMA],
    Optional("xtype"): basestring,
    Optional("ytype"): basestring,
    Optional("yscale"): EVAL,
    Optional("xscale"): EVAL,
    Optional("size"): SIZE
})

BAR_EXTENSIONS = {
    Optional("bar_width"): Any(int, float)
}
BAR_FIELDS = PLOT_FIELDS.extend(BAR_EXTENSIONS)

ERRORBAR_EXTENSIONS = {}
ERRORBAR_FIELDS = PLOT_FIELDS.extend(ERRORBAR_EXTENSIONS)

REG_EXTENSIONS = {
    Optional("output"): OUTPUT,
}
REG_FIELDS = PLOT_FIELDS.extend(REG_EXTENSIONS)


def require_series_field(plot_spec, field):
    """ require field to be present in plot_spec or plot_spec["series"] """
    if field not in plot_spec:
        for series_spec in plot_spec["series"]:
            if field not in series_spec:
                raise Invalid("field {} not defined".format(field))
    return plot_spec


# Schema for an entry in a subplot list
SUBPLOT_FIELDS = {
    Required("pos"): POS,
}
SUBPLOT_FIELDS = PLOT_FIELDS.extend(SUBPLOT_FIELDS)


# Schema for top-level figure spec
FIGURE_FIELDS = {
    Optional("output"): OUTPUT,
    Optional("xfield"): basestring,
    Optional("yfield"): basestring,
    Optional("size"): SIZE,
    Optional("output"): OUTPUT,
    Optional("xaxis"): AXIS,
    Optional("yaxis"): AXIS,
    Optional("yscale"): EVAL,
    Optional("xscale"): EVAL,
}

# bar figure is a bar plot which is also a figure
BAR_FIGURE_FIELDS = BAR_FIELDS.extend(FIGURE_FIELDS)
ERRORBAR_FIGURE_FIELDS = ERRORBAR_FIELDS.extend(FIGURE_FIELDS)
REG_FIGURE_FIELDS = REG_FIELDS.extend(FIGURE_FIELDS)

BAR_SUBPLOT_FIELDS = SUBPLOT_FIELDS.extend(BAR_EXTENSIONS)

# figures that are bar, errorbar, or reg at the figure level
BAR_FIGURE = BAR_FIGURE_FIELDS
ERRORBAR_FIGURE = ERRORBAR_FIGURE_FIELDS
REG_FIGURE = REG_FIGURE_FIELDS

# an errorbar plot in a subplot
ERRORBAR_SUBPLOT = SUBPLOT_FIELDS
BAR_SUBPLOT = BAR_SUBPLOT_FIELDS

# anythink that can be a subplot
SUBPLOT = Any(
    ERRORBAR_SUBPLOT,
    BAR_SUBPLOT,
)

# a figure that defines the subplots
SUBPLOTS_EXTENSIONS = {
    Required("subplots"): [SUBPLOT],
}

SUBPLOTS_FIGURE = Schema(FIGURE_FIELDS).extend(SUBPLOTS_EXTENSIONS)


def validate(orig_spec):
    if "subplots" in orig_spec:
        return SUBPLOTS_FIGURE(orig_spec)
    else:
        if "type" not in orig_spec:
            utils.halt("spec without subplots should define type")
        ty = orig_spec["type"]
        if ty == "errorbar":
            return ERRORBAR_FIGURE(orig_spec)
        elif ty == "bar":
            return BAR_FIGURE(orig_spec)
        elif ty == "regplot":
            return REG_FIGURE(orig_spec)
