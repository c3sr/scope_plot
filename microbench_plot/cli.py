import argparse
import json
import os.path
import sys
import click

from microbench_plot import specification
from microbench_plot import figure
from microbench_plot.benchmark import GoogleBenchmark
from microbench_plot import utils

""" If the module has a command line interface then this
file should be the entry point for that interface. 

plot deps
plot bar
plot 
"""

@click.command()
@click.argument('output', type=click.Path(dir_okay=False, resolve_path=True))
@click.argument('spec', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.argument('target')
@click.pass_context
def deps(ctx, output, spec, target):
    """Create a Makefile dependence"""

    utils.debug("Loading {}".format(spec))
    figure_spec = specification.load(spec)
    figure_spec = specification.apply_search_dirs(figure_spec, ctx.obj.get("INCLUDE", []))
    figure_deps = specification.get_deps(figure_spec)
    utils.debug("Saving to {}".format(output))
    specification.save_makefile_deps(output, target, figure_deps)


@click.command()
@click.argument('benchmark', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.option('--name-regex', help="a YAML spec for a figure")
@click.option('--x-field', help="field for X axis")
@click.option('--y-field', help="field for Y axis")
@click.pass_context
def bar(ctx, benchmark, name_regex, x_field, y_field):
    """Create a bar graph"""
    default_spec = {
        "generator": "bar",
        "series": [
            {
                "input_file": benchmark,
            }
        ],
    }
    # with open(benchmark, 'rb') as f:
    #     json_string = json.loads(f.read().decode('utf-8'))
    # data = GoogleBenchmark(json_string)
    # data = data.filter(name_regex)

    if x_field:
        utils.debug("x field {}".format(x_field))
        default_spec["xaxis"] = {"field": x_field}
    if y_field:
        default_spec["yaxis"] = {"field": y_field}
    if name_regex:
        default_spec["series"][0]["regex"] = name_regex

    fig = figure.generate(default_spec)
    output_path = ctx.obj["OUTPUT"]
    utils.debug("Saving to {}".format(output_path))
    fig.savefig(ctx.obj["OUTPUT"], clip_on=False, transparent=False)

@click.group(invoke_without_command=True)
@click.option('--debug/--no-debug', default=False)
@click.option('--include', help="Search location for input_file in spec.", multiple=True, type=click.Path(exists=True, file_okay=False, readable=True, resolve_path=True))
@click.option('--output', help="Output path.", default="figure.pdf", type=click.Path(dir_okay=False, resolve_path=True))
@click.option('--spec', help="a YAML spec for a figure", type=click.File('rb'))
@click.option('--verbose/--no-verbose', default=False)
@click.pass_context
def main(ctx, debug, output, include, spec, verbose):
    ctx.obj["DEBUG"] = debug
    ctx.obj["INCLUDE"] = include
    ctx.obj["OUTPUT"] = output
    ctx.obj["SPEC"] = spec
    ctx.obj["VERBOSE"] = verbose

    if verbose:
        utils.VERBOSE = True

    if debug:
        utils.DEBUG = True

    if ctx.invoked_subcommand is None:
        utils.debug('I was invoked without a subcommand')
    else:
        utils.debug('I am about to invoke %s' % ctx.invoked_subcommand)

        


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

    fig = figure.generate(figure_spec)

    if fig is not None:
        # Save plot
        fig.show()
        fig.savefig(output_path, clip_on=False, transparent=False)


main.add_command(deps)
main.add_command(bar)