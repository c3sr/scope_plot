import yaml
import os.path

from microbench_plot import utils


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
