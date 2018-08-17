import yaml
import os.path
from future.utils import iteritems

from scope_plot import utils
from scope_plot.error import NoInputFilesError
from scope_plot import schema

class InputFileNotFoundError(Exception):
    """raise when a spec file does not define 'backend'"""
    def __init__(self, name, search_dirs):
        self.name = name
        self.search_dirs = search_dirs
    def __str__(self):
        return "input_file {} not found in any of {}".format(self.name, self.search_dirs)

def find(name, search_dirs):
    if not os.path.isfile(name):
        found = False
        for dir in search_dirs:
            if not os.path.isdir(dir):
                raise OSError
            check_path = os.path.join(dir, name)
            if os.path.isfile(check_path):
                return check_path
        if not found:
            return None

class SpecificationBase(object):
    """ emulate a dictionary to provide compatibility with most of old implementation"""
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


class SeriesSpecification(SpecificationBase):
    def __init__(self, parent, spec):
        super(SeriesSpecification, self).__init__(parent, spec)
        self._input_file = spec.get("input_file", None)


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


    def find_input_file(self, search_dirs):
        if self._input_file:
            utils.debug("searching for input_file={} defined for series".format(self.input_file))
            e = InputFileNotFoundError(self._input_file, search_dirs)
            self._input_file = find(self._input_file, search_dirs)
            if not self._input_file:
                raise e

    def input_file(self):
        if self._input_file:
            return self._input_file
        f = self.parent.input_file()
        assert f
        return f


class PlotSpecification(SpecificationBase):
    def __init__(self, parent, spec):
        super(PlotSpecification, self).__init__(parent, spec)
        self.series =  [ 
            SeriesSpecification(self, s) for s in spec["series"]
        ]
        self._input_file = spec.get("input_file", None)
        self.type_str = spec.get("type", None)
        self.spec = spec


    def find_input_files(self, search_dirs):
        if self._input_file:
            e = InputFileNotFoundError(self._input_file, search_dirs)
            self._input_file = find(self._input_file, search_dirs)
            if not self._input_file:
                raise e

        for series in self.series:
            series.find_input_file(search_dirs)

    def input_file(self):
        """ input_file for plot """
        if self._input_file:
            return self._input_file
        return self.parent.input_file()

    def ty(self):
        """ plot type """
        if self.type_str:
            return self.type_str
        type_str = self.parent.ty()
        assert type_str
        return type_str


class Specification(SpecificationBase):
    def __init__(self, spec):
        super(Specification, self).__init__(parent=None, spec=spec)
        if "subplots" in spec:
            self.subplots = [
                PlotSpecification(self, s) for s in spec["subplots"]
            ]
        else:
            utils.debug("subplot not in spec")
            self.subplots = [PlotSpecification(self, spec)]
            self.subplots[0]["pos"] = (1,1)
        self._input_file = spec.get("input_file", None)
        self.size = spec.get("size", None)
        self.type_str = spec.get("type", None)


    def input_files(self):
        """ return all input_files entries in the specification"""
        for plot in self.subplots:
            for series in plot.series:
                yield series.input_file()

    def input_file(self):
        return self._input_file


    def find_input_files(self, search_dirs):
        if self._input_file:
            utils.debug("searching for input_file={} defined at top level of spec".format(self.input_file))
            e = InputFileNotFoundError(self._input_file, search_dirs)
            self._input_file = find(self._input_file, search_dirs)
            if not self._input_file:
                raise e

        for plot in self.subplots:
            plot.find_input_files(search_dirs)

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

    def ty(self):
        return self.type_str

    def save_makefile_deps(self, path, target):

        deps = sorted(list(set(self.input_files())))
        if len(deps) == 0:
            raise NoInputFilesError(self) 
        with open(path, 'w') as f:
            f.write(target)
            f.write(": ")
            for d in deps:
                f.write(" \\\n\t")
                f.write(d)

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

