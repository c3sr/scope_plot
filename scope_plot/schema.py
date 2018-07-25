from voluptuous import Schema, REMOVE_EXTRA, PREVENT_EXTRA   
   
def validate(schema_dict, orig_spec, strict):

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