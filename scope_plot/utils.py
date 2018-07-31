import click
import sys
import copy
import traceback

DEBUG = False
VERBOSE = False
QUIET = False


def debug(msg):
    if DEBUG and not QUIET:
        click.echo(click.style("[DEBU] " + msg, fg="green"), err=True)


def error(msg):
    if not QUIET:
        click.echo(click.style("[ERRO] " + msg, fg="red"), err=True)


def warn(msg):
    if not QUIET:
        click.echo(click.style("[WARN] " + msg, fg="yellow"), err=True)


def halt(msg):
    error(msg)
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)


def require(pred, msg=None):
    if not pred:
        if not QUIET:
            if msg:
                click.echo(
                    click.style("[INTERNAL ERROR] " + msg, fg="red"), err=True)
            else:
                click.echo(click.style("[INTERNAL ERROR]", fg="red"), err=True)
    assert pred


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


def propagate_key_if_missing(parent, key, child):
    """
    recursively move kv pairs from parent to child,
    if child is missing any pairs
    """
    value = parent[key]
    if key not in child:
        child[key] = copy.deepcopy(value)

    else:
        if isinstance(value, dict):
            for k in value:
                propagate_key_if_missing(value, k, child[key])


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
