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

def validate_errorbar(orig_spec, strict, allow_extra=False):
    if allow_extra:
        extra = ALLOW_EXTRA
    else:
        if strict:
            extra = PREVENT_EXTRA
        else:
            extra = REMOVE_EXTRA
    
    lambda spec: require_series_field(spec, "xfield")

    schema = Schema(
        All(
            ERRORBAR_RAW,
            lambda spec: require_series_field(spec, "xfield"),
            lambda spec: require_series_field(spec, "yfield"),
            lambda spec: require_series_field(spec, "input_file"),

        ),
        extra=extra,
    )

    valid_spec = schema(orig_spec)

    if not strict:
        extras = { k : orig_spec[k] for k in set(orig_spec) - set(valid_spec) }
        for key, value in iteritems(extras):
            utils.warn("extra key {} in errorbar spec".format(key))
    else:
        extras = {}

    return valid_spec, extras


def validate_bar(orig_spec, strict, allow_extra=False):
    if allow_extra:
        extra = ALLOW_EXTRA
    else:
        if strict:
            extra = PREVENT_EXTRA
        else:
            extra = REMOVE_EXTRA
    
    schema = Schema(
        All(
            BAR_RAW,
            input_file_defined,
            xfield_defined,
        ),
        extra=extra,
    )

    valid_spec = schema(orig_spec)

    if not strict:
        extras = { k : orig_spec[k] for k in set(orig_spec) - set(valid_spec) }
        for key, value in iteritems(extras):
            utils.warn("extra key {} in bar spec".format(key))
    else:
        extras = {}

    return valid_spec, extras



def validate(schema_dict, orig_spec, strict, allow_extra=False):
    """validate and return the validated orig_spec"""

    if allow_extra:
        extra = ALLOW_EXTRA
    else:
        if strict:
            extra = PREVENT_EXTRA
        else:
            extra = REMOVE_EXTRA

    schema = Schema(
        schema_dict,
        extra=extra
    )

    valid_spec = schema(orig_spec)


    if not strict:
        extras = { k : orig_spec[k] for k in set(orig_spec) - set(valid_spec) }
        for key, value in iteritems(extras):
            utils.warn("extra key {} in spec".format(key))
    else:
        extras = {}

    return valid_spec, extras