import argparse
import os.path
import sys
import click

from microbench_plot import spec
from microbench_plot import deps
from microbench_plot import figure

""" If the module has a command line interface then this
file should be the entry point for that interface. 

plot deps
plot bar
plot 
"""

@click.command()
@click.argument('spec', )
def deps(spec):
    """Create a Makefile dependence"""
    pass


@click.command()
@click.argument('json')
@click.option('--name-regex', help="a YAML spec for a figure")
@click.option('--x-field', help="field for X axis")
@click.option('--y-field', help="field for Y axis")
@click.pass_context
def bar(ctx, json):
    """Create a bar graph"""
    pass

@click.group(invoke_without_command=True)
@click.option('--output', help="Output path.")
@click.option('--include', help="Search location for input_file in spec.", multiple=True, type=click.Path(exists=True, file_okay=False, readable=True, resolve_path=True))
@click.option('--spec', help="a YAML spec for a figure", type=click.File('rb'))
@click.option('--verbose/--no-verbose', default=False)
@click.pass_context
def main(ctx, output, include, spec, verbose):
    ctx.obj["OUTPUT"] = output
    ctx.obj["INCLUDE"] = include
    ctx.obj["SPEC"] = spec
    ctx.obj["VERBOSE"] = verbose

    if verbose:
        click.echo("verbose mode")

    if ctx.invoked_subcommand is None:
        click.echo('I was invoked without subcommand')
    else:
        click.echo('I am about to invoke %s' % ctx.invoked_subcommand)
    # parser = argparse.ArgumentParser(description='Plot rai-project/microbench results')
    # parser.add_argument('-s', '--spec', required=True, type=str,
    #                     help='a yml spec file describing a figure')
    # parser.add_argument('-o', '--output', required=True, type=str, help='output path')
    # parser.add_argument('-t', '--target', type=str, help="target for deps")
    # parser.add_argument("--deps", action='store_true', help='generate a dep file instead of a figure')
    # parser.add_argument("-I", dest="data_search_dirs", nargs="+", help="search directory for data files mentioned in spec")
    # args = parser.parse_args()

    # figure_spec = spec.load(args.spec)
    # figure_spec = spec.apply_search_dirs(figure_spec, args.data_search_dirs)
    # output_path = args.output

    # Decide output path
    return
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

main.add_command(deps)
main.add_command(bar)