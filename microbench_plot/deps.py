import yaml
import os.path

def generate_deps(figure_spec, data_search_dirs):
    """Look in figure_spec for needed files, and find files in data_search_dirs if they exist
    otherwise, just use the raw files needed in figure_spec
    """
    deps = []
    for series in figure_spec.get("series", []):

        # Find the first file that exists in data_search_dirs
        if data_search_dirs:
            for dir in data_search_dirs:
                check_path = os.path.join(dir, series["file"])
                if os.path.isfile(check_path):
                    deps += [check_path]
                    break
        else:
            deps += [series["file"]]

    return deps

def save_deps(path, target, dependencies):
    with open(path, 'wb') as f:
        f.write(target)
        f.write(": ")
        for d in dependencies:
            f.write(d)
            f.write(" ")