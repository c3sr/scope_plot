from future.utils import iteritems
from voluptuous import All, Any, Schema, Optional, Required, ALLOW_EXTRA, REMOVE_EXTRA, PREVENT_EXTRA, Invalid

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

SCALE = Any(float, int, basestring)
COLOR = Any(basestring, float, int)

SERIES_SCHEMA = Schema({
    Optional("label"): basestring,
    Optional("input_file"): basestring,
    Optional("regex"): basestring,
    Optional("xfield"): basestring,
    Optional("yfield"): basestring,
    Optional("xscale"): SCALE,
    Optional("yscale"): SCALE,
    Optional("color"): COLOR,
})

POS = list
SIZE = list

EVAL = Any(basestring, float, int)

BACKEND = Any("bokeh", "matplotlib")
TYPE = Any("errorbar", "bar", "regplot")

SPEC_FIELDS = Schema({
    Required("backend"): BACKEND,
})

PLOT_DICT = Schema({
    Required("type"): TYPE,
    Optional("title"): basestring,
    Optional("input_file"): basestring,
    Optional("yfield"): basestring,
    Optional("xfield"): basestring,
    Optional("yaxis"): AXIS,
    Optional("xaxis"): AXIS,
    Optional("series"): [SERIES_SCHEMA],
    Optional("yscale"): SCALE,
    Optional("xscale"): SCALE,
    Optional("xtype"): basestring,
    Optional("ytype"): basestring,
    Optional("yscale"): EVAL,
    Optional("xscale"): EVAL,
    Optional("size"): SIZE
})

BAR_EXTENSIONS = {Optional("bar_width"): Any(int, float)}

BAR_DICT = PLOT_DICT.extend(BAR_EXTENSIONS)

ERRORBAR_EXTENSIONS = {
    Required("backend"): BACKEND,
}

ERRORBAR_DICT = PLOT_DICT.extend(ERRORBAR_EXTENSIONS)

REG_EXTENSIONS = {
    Required("backend"): BACKEND,
}

REG_DICT = PLOT_DICT.extend(REG_EXTENSIONS)


def require_series_field(plot_spec, field):
    """ require field to be present in plot_spec or plot_spec["series"] """
    if field not in plot_spec:
        for series_spec in plot_spec["series"]:
            if field not in series_spec:
                raise Invalid("field {} not defined".format(field))
    return plot_spec


BAR = All(
    BAR_DICT,
    lambda spec: require_series_field(spec, "xfield"),
    lambda spec: require_series_field(spec, "yfield"),
    lambda spec: require_series_field(spec, "input_file"),
)

ERRORBAR = All(
    ERRORBAR_DICT,
    lambda spec: require_series_field(spec, "xfield"),
    lambda spec: require_series_field(spec, "yfield"),
    lambda spec: require_series_field(spec, "input_file"),
)

REG = All(
    REG_DICT,
    lambda spec: require_series_field(spec, "xfield"),
    lambda spec: require_series_field(spec, "yfield"),
    lambda spec: require_series_field(spec, "input_file"),
)

# subplot additional field requirements
SUBPLOT_EXTENSIONS = {
    Required("pos"): POS,
}
# all figures require these fields
FIGURE_EXTENSIONS = {Required("backend"): BACKEND}

BAR_FIGURE_FIELDS = BAR_DICT.extend(FIGURE_EXTENSIONS)
ERRORBAR_FIGURE_FIELDS = ERRORBAR_DICT.extend(FIGURE_EXTENSIONS)
REG_FIGURE_FIELDS = REG_DICT.extend(FIGURE_EXTENSIONS)

SUBPLOT_DICT = PLOT_DICT.extend(SUBPLOT_EXTENSIONS)
BAR_SUBPLOT_DICT = SUBPLOT_DICT.extend(BAR_EXTENSIONS)

# a bar plot that is a full figure
BAR_FIGURE = All(
    BAR_FIGURE_FIELDS,
    lambda spec: require_series_field(spec, "xfield"),
    lambda spec: require_series_field(spec, "yfield"),
    lambda spec: require_series_field(spec, "input_file"),
)

# an errorbar plot that is a full figure
ERRORBAR_FIGURE = All(
    ERRORBAR_FIGURE_FIELDS,
    lambda spec: require_series_field(spec, "xfield"),
    lambda spec: require_series_field(spec, "yfield"),
    lambda spec: require_series_field(spec, "input_file"),
)

# a reg plot that is a full figure
REG_FIGURE = All(
    REG_FIGURE_FIELDS,
    lambda spec: require_series_field(spec, "xfield"),
    lambda spec: require_series_field(spec, "yfield"),
    lambda spec: require_series_field(spec, "input_file"),
)

# an errorbar plot in a subplot
ERRORBAR_SUBPLOT = All(
    SUBPLOT_DICT,
    lambda spec: require_series_field(spec, "xfield"),
    lambda spec: require_series_field(spec, "yfield"),
    lambda spec: require_series_field(spec, "input_file"),
)

# a bar plot in a subplot
BAR_SUBPLOT = All(
    BAR_SUBPLOT_DICT,
    lambda spec: require_series_field(spec, "xfield"),
    lambda spec: require_series_field(spec, "yfield"),
    lambda spec: require_series_field(spec, "input_file"),
)

SUBPLOT = Any(
    ERRORBAR_SUBPLOT,
    BAR_SUBPLOT,
)

SUBPLOT_FIGURE = Schema({
    Required("subplots"): [SUBPLOT],
    Optional("size"): SIZE,
    Required("backend"): BACKEND,
    Optional("xaxis"): AXIS,
    Optional("yaxis"): AXIS,
    Optional("yscale"): SCALE,
    Optional("xscale"): SCALE,
})


def validate(orig_spec):
    if "backend" not in orig_spec:
        utils.halt("spec should define backend")

    backend = orig_spec["backend"]
    if "subplots" in orig_spec:
        return SUBPLOT_FIGURE(orig_spec)
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
