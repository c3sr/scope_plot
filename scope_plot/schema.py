from future.utils import iteritems
from voluptuous import All, Any, Schema, Optional, Required, ALLOW_EXTRA, REMOVE_EXTRA, PREVENT_EXTRA, Invalid

from scope_plot import utils

import pprint
pp = pprint.PrettyPrinter(indent=4)


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

SCALE = Schema(Any(float, int, basestring))

SERIES_SCHEMA = Schema({
    Optional("label"): basestring,
    Optional("input_file"): basestring,
    Optional("regex"): basestring,
    Optional("xfield"): basestring,
    Optional("yfield"): basestring,
    Optional("xscale"): SCALE,
    Optional("yscale"): SCALE,    
})

POS = list
SIZE = list

EVAL = Schema(Any(basestring, float, int))

BACKEND = Any("bokeh", "matplotlib")

PLOT_DICT = Schema(
    {
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
        Required("type"): basestring,
        Optional("yscale"): EVAL,
        Optional("xscale"): EVAL,
        Optional("bar_width"): Any(int, float),
        Required("backend"): BACKEND,
        Optional("size"): SIZE
    }
)

BAR_EXTENSIONS = {
    Optional("bar_width"): Any(int, float)
}

BAR_DICT = PLOT_DICT.extend(BAR_EXTENSIONS)

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


ERRORBAR = Schema(
    All(
        PLOT_DICT,
        lambda spec: require_series_field(spec, "xfield"),
        lambda spec: require_series_field(spec, "yfield"),
        lambda spec: require_series_field(spec, "input_file"),        
    )
)

PLOT = Any(
    ERRORBAR,
    BAR,
)

# subplot additional field requirements
SUBPLOT_EXTENSIONS = {
    Required("pos"): POS,
}

SUBPLOT_DICT = PLOT_DICT.extend(SUBPLOT_EXTENSIONS)

BAR_SUBPLOT_DICT = SUBPLOT_DICT.extend(
    BAR_EXTENSIONS
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

SUBPLOTS = {
    Required("subplots"): [SUBPLOT],
    Optional("size"): SIZE,
    Required("backend"): BACKEND,
    Optional("xaxis"): AXIS,
    Optional("yaxis"): AXIS,
}

SPEC = Any(
    PLOT,
    SUBPLOT,
)

def validate(orig_spec):
    validated_spec = SPEC(orig_spec)
    pp.pprint(SPEC)
    return validated_spec
