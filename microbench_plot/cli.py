import argparse
import os.path
import sys

from microbench_plot import spec
from microbench_plot import deps
from microbench_plot import figure

""" If the module has a command line interface then this
file should be the entry point for that interface. """


def main():
    parser = argparse.ArgumentParser(description='Plot rai-project/microbench results')
    parser.add_argument('-s', '--spec', required=True, type=str,
                        help='a yml spec file describing a figure')
    parser.add_argument('-o', '--output', required=True, type=str, help='output path')
    parser.add_argument('-t', '--target', type=str, help="target for deps")
    parser.add_argument("--deps", action='store_true', help='generate a dep file instead of a figure')
    parser.add_argument("-I", dest="data_search_dirs", nargs="+", help="search directory for data files mentioned in spec")
    args = parser.parse_args()

    figure_spec = spec.load(args.spec)
    figure_spec = spec.apply_search_dirs(figure_spec, args.data_search_dirs)
    output_path = args.output

    # Decide output path
    if output_path is None and figure_spec.get("output_file", None) is not None:
        script_dir = os.path.dirname(os.path.realpath(__file__))
        output_path = os.path.join(script_dir, figure_spec.get("output_file"))
        if not output_path.endswith(".pdf") and not output_path.endswith(".png"):
            base_output_path = output_path
            output_path = []
            for ext in figure_spec.get("output_format", ["pdf"]):
                ext = ext.lstrip(".")
                output_path.append(base_output_path + "." + ext)

    # Generate make dependencies files
    if args.deps:
        assert args.target
        figure_deps = deps.generate_deps(figure_spec, args.data_search_dirs)
        deps.save_deps(output_path, args.target, figure_deps)
        sys.exit(0)

    fig = figure.generate(figure_spec)
    if fig is not None:
        # Save plot
        fig.show()
        fig.savefig(output_path, clip_on=False, transparent=False)

    sys.exit(0)
