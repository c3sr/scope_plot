from voluptuous import Any, Schema, Optional, ALLOW_EXTRA, REMOVE_EXTRA, PREVENT_EXTRA   

SCALE_RAW = Any(float, int, basestring)

AXIS_RAW = {
    Optional('lim'): list,
    Optional('label'): basestring,
    Optional('scale'): SCALE_RAW,
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