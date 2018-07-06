import click

DEBUG = False
VERBOSE = False

def debug(msg):
    if DEBUG:
        click.echo(click.style("[DEBU] " + msg, fg="yellow"), err=True)

def find_dictionary(key, dictionary):
    """yield all dictionaries that contain "key" in a dictionary of nested
    iterables and dictionaries"""
    for (k, v) in dictionary.items():
        if k == key:
            yield dictionary
        elif isinstance(v, dict):
            for result in find_dictionary(key, v):
                yield result
        else:
            try:
                (e for e in v)
            except TypeError:  # not iterable
                continue
            for e in v:
                if isinstance(e, dict):
                    for result in find_dictionary(key, e):
                        yield result


def find_longest_name(benchmark_list):
    """
    Return the length of the longest benchmark name in a given list of
    benchmark JSON objects
    """
    longest_name = 1
    for bc in benchmark_list:
        if len(bc['name']) > longest_name:
            longest_name = len(bc['name'])
    return longest_name


def calculate_change(old_val, new_val):
    """
    Return a float representing the decimal change between old_val and new_val.
    """
    if old_val == 0 and new_val == 0:
        return 0.0
    if old_val == 0:
        return float(new_val - old_val) / (float(old_val + new_val) / 2)
    return float(new_val - old_val) / abs(old_val)
