from voluptuous import Any, Schema, Optional, ALLOW_EXTRA, REMOVE_EXTRA, PREVENT_EXTRA   

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

SCALE_RAW = Any(float, int, basestring)

AXIS_RAW = {
    Optional('lim'): list,
    Optional('label'): basestring,
    Optional('scale'): SCALE_RAW,
}

SERIES_RAW = {
    Optional("label", default=""): basestring,
    "label": basestring,
    "input_file": Any(float, int),
    "regex": basestring,
    "xfield": basestring,
    "yfield": basestring,
    "xscale": SCALE_RAW,
    "yscale": SCALE_RAW,
}

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
        for key, value in iteritems(diff):
            utils.warn("extra key {} in yaxis spec".format(key))
    else:
        extras = {}

    return valid_spec, extras