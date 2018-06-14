import argparse

from microbench_plot import spec
from microbench_plot import deps

""" If the module has a command line interface then this
file should be the entry point for that interface. """
def main():

    parser = argparse.ArgumentParser(description='Plot rai-project/microbench results')
    parser.add_argument('-s','--spec', required=True, type=str, 
                    help='a yml spec file describing a figure')
    parser.add_argument('-o', '--output', required=True, type=str, help='output path' )
    parser.add_argument('-t', '--target', type=str, help="target for deps")
    parser.add_argument("--deps", action='store_true', help='generate a dep file instead of a figure')
    parser.add_argument("-I", dest="data_search_dirs", nargs="+", help="search directory for data files mentioned in spec")
    args = parser.parse_args()


    figure_spec = spec.load(args.spec)
    print(figure_spec)

    if args.deps:
        assert args.target
        figure_deps = deps.generate_deps(figure_spec, args.data_search_dirs)
        deps.save_deps(args.output, args.target, figure_deps)
    else:
        print("not deps!")

    pass
