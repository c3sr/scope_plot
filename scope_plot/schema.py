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

SCALE_SCHEMA = Schema(Any(float, int, basestring))

AXIS_SCHEMA = Schema({
    Optional('label'): basestring,
    Optional('lim'): list,
    Optional('tick_rotation'): Any(float, int),
    Optional('type'): basestring,
})

AXIS_SCHEMA = Schema({
    Optional('label'): basestring,
    Optional('lim'): list,
    Optional('tick_rotation'): Any(float, int),
    Optional('type'): basestring,
})

def require_series_field(plot_spec, field):
    """ require field to be present in plot_spec or plot_spec["series"] """
    if field not in plot_spec:
        for series_spec in plot_spec["series"]:
            if field not in series_spec:
                raise Invalid("field {} not defined".format(field))
    return plot_spec

SCALE_SCHEMA = Schema(Any(float, int, basestring))

SERIES_SCHEMA = Schema({
    Optional("label"): basestring,
    Optional("input_file"): basestring,
    Optional("regex"): basestring,
    Optional("xfield"): basestring,
    Optional("yfield"): basestring,
    Optional("xscale"): SCALE_SCHEMA,
    Optional("yscale"): SCALE_SCHEMA,    
})

POS_SCHEMA = Schema(list)

PLOT_SCHEMA_BASE = Schema(
    {
        Optional("title"): basestring,
        Optional("input_file"): basestring,
        Optional("yfield"): basestring,
        Optional("xfield"): basestring,
        Optional("yaxis"): AXIS_SCHEMA,
        Optional("xaxis"): AXIS_SCHEMA,
        Optional("series"): [SERIES_SCHEMA],
        Optional("yscale"): SCALE_SCHEMA,
        Optional("xscale"): SCALE_SCHEMA,
        Optional("xtype"): basestring,
        Optional("ytype"): basestring,
        Required("pos"): POS_SCHEMA,
        Required("type"): basestring,
    }
)

BAR_SCHEMA_BASE = PLOT_SCHEMA_BASE.extend({
    Optional("bar_width"): Schema(Any(int, float))
})

BAR_SCHEMA = Schema(
    All(
        BAR_SCHEMA_BASE,
        lambda spec: require_series_field(spec, "xfield"),
        lambda spec: require_series_field(spec, "yfield"),
        lambda spec: require_series_field(spec, "input_file"),        
    )
)

ERRORBAR_SCHEMA = Schema(
    All(
        PLOT_SCHEMA_BASE,
        lambda spec: require_series_field(spec, "xfield"),
        lambda spec: require_series_field(spec, "yfield"),
        lambda spec: require_series_field(spec, "input_file"),        
    )
)

PLOT_SCHEMA = Schema(Any(
    ERRORBAR_SCHEMA,
    BAR_SCHEMA,
)
)

SPEC_SCHEMA = Schema({
    Required("subplots"): [PLOT_SCHEMA],
    Optional("yaxis"): AXIS_SCHEMA,
    Optional("xaxis"): AXIS_SCHEMA,
    Optional("size"): list,
})

def validate_spec(orig_spec):
    return SPEC_SCHEMA(orig_spec)
