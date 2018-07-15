import yaml
import os.path

from microbench_plot import utils
from microbench_plot.error import NoInputFilesError


def load(yaml_path):
    with open(yaml_path, "rb") as f:
        cfg = yaml.load(f)
    return cfg


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
