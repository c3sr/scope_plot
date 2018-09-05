import yaml
import os.path
from future.utils import iteritems

from scope_plot import utils
from scope_plot.error import NoInputFilesError
from scope_plot import schema


class InputFileNotFoundError(Exception):
    """raise when an input_file cannot be found in include directories"""
    def __init__(self, name, search_dirs):
        self.name = name
        self.search_dirs = search_dirs

    def __str__(self):
        return "input_file {} not found in any of {}".format(self.name, self.search_dirs)


class InputFileNotDefinedError(Exception):
    """raise when a spec file does not define input_file"""
    def __init__(self, series):
        self.series = series


class XfieldNotFoundError(Exception):
    """raise when xfield is not defined"""


class YfieldNotFoundError(Exception):
    """raise when yfield is not defined"""


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


class input_file_mixin(object):
    def __init__(self, parent, spec):
        self.parent = parent
        self._input_file = spec.get("input_file", None)

    def input_file(self):
        if self._input_file:
            return self._input_file
        elif isinstance(self.parent, input_file_mixin):
            return self.parent.input_file()
        else:
            raise InputFileNotDefinedError(self)


class regex_mixin(object):
    def __init__(self, parent, spec):
        self.parent = parent
        self._regex = spec.get("regex", None)

    def regex(self):
        if self._regex:
            return self._regex
        elif isinstance(self.parent, regex_mixin):
            return self.parent.regex()
        else:
            return ".*"


class xfield_mixin(object):
    def __init__(self, parent, spec):
        self.parent = parent
        self._xfield = spec.get("xfield", None)

    def xfield(self):
        if self._xfield:
            return self._xfield
        elif isinstance(self.parent, xfield_mixin):
            f = self.parent.xfield()
            if not f:
                raise XfieldNotFoundError
            return f
        return None


class yfield_mixin(object):
    def __init__(self, parent, spec):
        self.parent = parent
        self._yfield = spec.get("yfield", None)

    def yfield(self):
        if self._yfield:
            return self._yfield
        elif isinstance(self.parent, yfield_mixin):
            f = self.parent.yfield()
            if not f:
                raise YfieldNotFoundError
            return f
        return None


class xscale_mixin(object):
    def __init__(self, parent, spec):
        self.parent = parent
        self._xscale = spec.get("xscale", None)

    def xscale(self):
        if self._xscale:
            return eval(str(self._xscale))
        elif isinstance(self.parent, xscale_mixin):
            f = self.parent.xscale()
            if f:
                return f
        return 1.0


class yscale_mixin(object):
    def __init__(self, parent, spec):
        self.parent = parent
        self._yscale = spec.get("yscale", None)

    def yscale(self):
        if self._yscale:
            return eval(str(self._yscale))
        elif isinstance(self.parent, yscale_mixin):
            f = self.parent.yscale()
            if f:
                return f
        return 1.0


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


class SeriesSpecification(
    input_file_mixin,
    SpecificationBase,
    regex_mixin,
    xfield_mixin,
    xscale_mixin,
    yfield_mixin,
    yscale_mixin,
):
    def __init__(self, parent, spec):
        SpecificationBase.__init__(self, parent, spec)
        input_file_mixin.__init__(self, parent, spec)
        regex_mixin.__init__(self, parent, spec)
        xfield_mixin.__init__(self, parent, spec)
        yfield_mixin.__init__(self, parent, spec)
        xscale_mixin.__init__(self, parent, spec)
        yscale_mixin.__init__(self, parent, spec)
        self._color = spec.get("color", None)
        self._label = spec.get("label", None)

    def label_seperator(self):
        """the seperator that should be used to build the label, or x if not defined"""
        if isinstance(self._label, dict):
            return self._label.get("seperator", "x")
        return "x"

    def label_fields(self):
        """the benchmark fields that should be used to build the label, or [] if not defined"""
        if isinstance(self._label, dict):
            return self._label.get("fields", [])
        return []

    def label_or(self, default=None):
        """return the series label, if it is a string, the default"""
        if isinstance(self._label, str):
            return self._label
        return default

    def find_input_file(self, search_dirs):
        if self._input_file:
            utils.debug("searching for input_file={} defined for series".format(self._input_file))
            e = InputFileNotFoundError(self._input_file, search_dirs)
            self._input_file = find(self._input_file, search_dirs)
            if not self._input_file:
                raise e

    def color_or(self, default=None):
        """return series color, or default value if color not defined"""
        if self._color:
            return self._color
        return default


class PlotSpecification(
    SpecificationBase,
    input_file_mixin,
    regex_mixin,
    xfield_mixin,
    xscale_mixin,
    yfield_mixin,
    yscale_mixin,
):
    def __init__(self, parent, spec):
        SpecificationBase.__init__(self, parent, spec)
        input_file_mixin.__init__(self, parent, spec)
        regex_mixin.__init__(self, parent, spec)
        xfield_mixin.__init__(self, parent, spec)
        yfield_mixin.__init__(self, parent, spec)
        xscale_mixin.__init__(self, parent, spec)
        yscale_mixin.__init__(self, parent, spec)
        self.series = [
            SeriesSpecification(self, s) for s in spec["series"]
        ]
        self.type_str = spec.get("type", None)

    def find_input_files(self, search_dirs):
        if self._input_file:
            e = InputFileNotFoundError(self._input_file, search_dirs)
            self._input_file = find(self._input_file, search_dirs)
            if not self._input_file:
                raise e
        for series in self.series:
            series.find_input_file(search_dirs)

    def ty(self):
        """ plot type """
        if self.type_str:
            return self.type_str
        type_str = self.parent.ty()
        assert type_str
        return type_str


class Specification(
    SpecificationBase,
    input_file_mixin,
    regex_mixin,
    xfield_mixin,
    xscale_mixin,
    yfield_mixin,
    yscale_mixin
):
    def __init__(self, spec, spec_path=None):
        SpecificationBase.__init__(self, parent=None, spec=spec)
        input_file_mixin.__init__(self, None, spec)
        regex_mixin.__init__(self, None, spec)
        xfield_mixin.__init__(self, None, spec)
        yfield_mixin.__init__(self, None, spec)
        xscale_mixin.__init__(self, None, spec)
        yscale_mixin.__init__(self, None, spec)
        if "subplots" in spec:
            self.subplots = [
                PlotSpecification(self, s) for s in spec["subplots"]
            ]
        else:
            utils.debug("subplot not in spec")
            self.subplots = [PlotSpecification(self, spec)]
            self.subplots[0]["pos"] = (1, 1)
        self.size = spec.get("size", None)
        self.type_str = spec.get("type", None)
        self.output_spec = spec.get("output", None)
        self.spec_path = spec_path  # path of file this spec came from, if any

    def input_files(self):
        """ return all input_files entries in the specification"""
        for plot in self.subplots:
            for series in plot.series:
                yield series.input_file()

    def find_input_files(self, search_dirs):
        if self._input_file:
            utils.debug("searching for input_file={} defined at top level of spec".format(self._input_file))
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
            return Specification(spec, path)

    @staticmethod
    def load_dict(d):
        spec = schema.validate(d)
        return Specification(d)

    def output_specs(self):
        """ return a list of (name, backend) parsed from spec.output"""
        if not self.output_spec:
            return []
        name = self.output_spec.get("name", None)
        if not name:
            if self.spec_path:
                base = os.path.basename(self.spec_path)
                name = os.path.splitext(base)[0]
            else:
                raise ValueError("spec.name undefined and no spec_path")
        specs = []
        for spec in self.output_spec.get("files", []):
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
