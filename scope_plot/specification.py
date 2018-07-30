import yaml
import os.path
from future.utils import iteritems

from scope_plot import utils
from scope_plot.error import NoInputFilesError

class NestedDict(object):
    def __init__(self, d, parent=None):
        self.parent = parent
        self.d =  {}
        for k,v in iteritems(d):
            if isinstance(v, dict):
                self.d[k] = NestedDict(v, parent=self)
            else:
                self.d[k] = v


    def __getitem__(self, key):
        if key in self.d:
            return self.d[key]
        else:
            if self.parent:
                return self.parent[key]

    def __setitem__(self, key, value):
        self.d[key] = value

    def __delitem__(self, key):
        del self.d[key]

    def iter_without(self, omit_keys):
        for k in self.d:
            if k not in omit_keys:
                yield k, self.d[k]
        if self.parent:
            return self.parent.iter_without(omit_keys + [k for k in self.d])

    def __iter__(self):
        return self.iter_without([])


class PlotSpecification(object):
    def __init__(self, parent, spec):
        self.spec = spec

    def __getitem__(self, key):
        return self.spec[key]
    def __setitem__(self, key, value):
        self.spec[key] = value
    def __delitem__(self, key):
        del self.spec[key]

class Specification(object):
    def __init__(self, spec, parent):
        self.parent = parent
        self.size = spec.get("size", None)
        self.subplots = [PlotSpecification(self, spec) for spec in spec["subplots"]]

    def apply_search_dirs(self, spec):
        pass

    @staticmethod
    def load_yaml(path):
        with open(path, 'rb') as f:
            spec = yaml.load(f)
            return Specification(spec)


def load(yaml_path):
    with open(yaml_path, "rb") as f:
        cfg = yaml.load(f)
    return cfg

def canonicalize_to_subplot(orig_spec):
    if 'subplots' in orig_spec:
        return orig_spec
    else:
        new_spec = {
            "subplots": [
                {"pos": [1, 1]},
            ]
        }
        for key,value in iteritems(orig_spec):
            if key in ["size"]:
                new_spec[key] = value
            else:
                new_spec["subplots"][0][key] = value
        return new_spec

def apply_search_dirs(figure_spec, data_search_dirs):
    """ look for files in figure_spec, and if those files do not exist, search data_search_dirs for them"""

    new_spec = dict(figure_spec)

    for d in utils.find_dictionary("input_file", new_spec):
        f = d["input_file"]
        if os.path.isfile(f):
            continue
        else:
            found = False
            for dir in data_search_dirs:
                if not os.path.isdir(dir):
                    raise OSError
                check_path = os.path.join(dir, f)
                if os.path.isfile(check_path):
                    d["input_file"] = check_path
                    found = True
                    break
            if not found:
                print("Could not find", f, "in any of", data_search_dirs)
                raise OSError

    return new_spec


def get_deps(figure_spec):
    """Look in figure_spec for needed files, and find files in data_search_dirs if they exist
    otherwise, just use the raw files needed in figure_spec
    """
    deps = []
    for d in utils.find_dictionary("input_file", figure_spec):
        dep = d["input_file"]
        deps += [dep]
    if len(deps) == 0:
        raise NoInputFilesError(figure_spec)
    return sorted(list(set(deps)))


def save_makefile_deps(path, target, dependencies):
    with open(path, 'wb') as f:
        f.write(target)
        f.write(": ")
        for d in dependencies:
            f.write(" \\\n\t")
            f.write(d)
