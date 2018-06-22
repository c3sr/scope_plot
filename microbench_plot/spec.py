import yaml
import os.path

from microbench_plot import utils


def load(yaml_path):
    with open(yaml_path, "rb") as f:
        cfg = yaml.load(f)
    return cfg


def use_search_dirs(figure_spec, data_search_dirs):
    """ look for files in figure_spec, and if those files do not exist, search data_search_dirs for them"""

    new_spec = dict(figure_spec)

    for d in utils.find_dictionary("input_file", new_spec):
        f = d["input_file"]
        if os.path.isfile(f):
            continue
        else:
            for dir in data_search_dirs:
                if not os.path.isdir(dir):
                    raise OSError
                check_path = os.path.join(dir, f)
                if os.path.isfile(check_path):
                    d["input_file"] = check_path
                    break

    print(new_spec)
    return new_spec
