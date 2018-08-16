import yaml
import os.path
from future.utils import iteritems

from scope_plot import utils
from scope_plot.error import NoInputFilesError
from scope_plot import schema

class InputFileMixin(object):
    def input_file(self):
        if "input_file" not in self.spec:
            if self.parent:
                return self.parent.input_file()
            else:
                return None
        else:
            return self.spec["input_file"]

class SpecificationBase(object):
    """ emulate a dictionary to provide compatibility with old implementation"""
    def __init__(self, parent, spec):
        self.parent = parent
        self.spec = spec

    def __contains__(self, key):
        return key in self.spec

    def __getitem__(self, key):
        return self.spec[key]

    def __setitem__(self, key, value):
        self.spec[key] = value

    def __delitem__(self, key):
        del self.spec[key]

    def get(self, key, default):
        return self.spec.get(key, default)


class SeriesSpecification(SpecificationBase, InputFileMixin):
    def __init(self, parent, spec):
        super(SeriesSpecification, self).__init__(parent, spec)

    def label_seperator(self):
        """the seperator that should be used to build the label, or None if the label a string"""
        label_spec = self.spec["label"]
        if isinstance(label_spec, dict):
            return label_spec.get("seperator", "x")
        return None


    def label_fields(self):
        """the fields that should be used to build the label, or None if the label a string"""
        label_spec = self.spec["label"]
        if isinstance(label_spec, dict):
            return label_spec["fields"]
        return None


    def label(self):
        """return the label, if it is a string, or None"""
        label_spec = self.spec["label"]
        if isinstance(label_spec, str):
            return label_spec
        return None




class PlotSpecification(SpecificationBase, InputFileMixin):
    def __init__(self, parent, spec):
        super(PlotSpecification, self).__init__(parent, spec)
        self.series =  [ 
            SeriesSpecification(self, spec) for spec in self.spec["series"]
        ]

    def __getitem__(self, key):
        return self.spec[key]


    def __setitem__(self, key, value):
        self.spec[key] = value


    def __delitem__(self, key):
        del self.spec[key]


class Specification(SpecificationBase, InputFileMixin):
    def __init__(self, spec):
        super(Specification, self).__init__(parent=None, spec=spec)
        self.size = spec.get("size", None)
        if "subplots" in self.spec:
            self.subplots = [
                PlotSpecification(self, spec) for spec in self.spec["subplots"]
            ]
        else:
            self.subplots = [PlotSpecification(self, self.spec)]


    def input_files(self):
        """ return all input_files entries in the specification"""
        files = []
        for plot in self.subplots:
            for series in plot.series:
                files += [series.input_file()]
        return files


    def apply_search_dirs(self, data_search_dirs):
        """
        look for series input_files in data_search_dirs
        """

        for f in self.input_files():
            if os.path.isfile(f):
                utils.debug("found {} without search".format(f))
                continue
            else:
                found = False
                for dir in data_search_dirs:
                    if not os.path.isdir(dir):
                        raise OSError
                    check_path = os.path.join(dir, f)
                    if os.path.isfile(check_path):
                        utils.debug("found input_file {} at {}".format(f, check_path))
                        print(id(f))
                        f = check_path
                        found = True
                        print(id(f))
                        break
                if not found:
                    utils.error("Could not find", f, "in any of", data_search_dirs)
                    raise OSError


    @staticmethod
    def load_yaml(path):
        with open(path, 'rb') as f:
            spec = yaml.load(f)
            spec = schema.validate(spec)
            return Specification(spec)

    @staticmethod
    def load_dict(d):
        spec = schema.validate(d)
        return Specification(d)

    def output_paths(self):
        raise NotImplementedError
        if "output" not in self.spec:
            return []
        output_spec = figure_spec['output']
        name = output_spec.get("name", None)
        specs = []
        for spec in figure_spec.get("output", []):
            backend = spec['backend']
            ext = spec['extension']
            specs += [(name + "." + ext, backend)]
        return specs


def canonicalize_to_subplot(orig_spec):
    if 'subplots' in orig_spec:
        return orig_spec
    else:
        new_spec = {
            "subplots": [
                {
                    "pos": [1, 1]
                },
            ]
        }
        for key, value in iteritems(orig_spec):
            if key in ["size"]:
                new_spec[key] = value
            else:
                new_spec["subplots"][0][key] = value
        return new_spec


def get_deps(figure_spec):
    """Look in figure_spec for needed files, and find files
    in data_search_dirs if they exist
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
    with open(path, 'w') as f:
        f.write(target)
        f.write(": ")
        for d in dependencies:
            f.write(" \\\n\t")
            f.write(d)




