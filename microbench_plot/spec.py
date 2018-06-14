import yaml
import os.path

def load(yaml_path):
    with open(yaml_path, "rb") as f:
        cfg = yaml.load(f)
    return cfg

def use_search_dirs(figure_spec, data_search_dirs):
    """ look for files in figure_spec, and if those files do not exist, search data_search_dirs for them"""

    new_spec = dict(figure_spec)

    for series in new_spec.get("series", []):
        if os.path.isfile(series["file"]):
            continue
        else:
            for dir in data_search_dirs:
                if not os.path.isdir(dir):
                    raise OSError
                check_path = os.path.join(dir, series["file"])
                if os.path.isfile(check_path):
                    series["file"] = check_path
                    break

    return new_spec