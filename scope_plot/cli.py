import argparse
import json
import os.path
import sys
import click
import glob

from scope_plot import specification
from scope_plot.specification import Specification
from scope_plot import figure
from scope_plot.benchmark import GoogleBenchmark
from scope_plot import utils
from scope_plot.__init__ import __version__

""" If the module has a command line interface then this
file should be the entry point for that interface. """


@click.command()
@click.argument('output', type=click.Path(dir_okay=False, resolve_path=True))
@click.argument('spec', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.argument('target')
@click.pass_context
def deps(ctx, output, spec, target):
    """Create a Makefile dependence"""

    utils.debug("Loading {}".format(spec))
    figure_spec = specification.load_yaml(spec)
    figure_spec = specification.apply_search_dirs(figure_spec, ctx.obj.get("INCLUDE", []))
    figure_deps = specification.get_deps(figure_spec)
    utils.debug("Saving to {}".format(output))
    specification.save_makefile_deps(output, target, figure_deps)


@click.command()
@click.argument('benchmark', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.argument('output', type=click.Path(dir_okay=False, resolve_path=True))
@click.option('--name-regex', help="a YAML spec for a figure")
@click.option('--x-field', help="field for X axis")
@click.option('--y-field', help="field for Y axis")
@click.pass_context
def bar(ctx, benchmark, name_regex, output, x_field, y_field):
    """Create a bar graph."""
    default_spec = {
        "generator": "bar",
        "series": [
            {
                "input_file": benchmark,
            }
        ],
    }

    if x_field:
        default_spec["series"][0]["xfield"] = x_field
        default_spec["xaxis"] = {"label": x_field}
    if y_field:
        default_spec["series"][0]["yfield"] = y_field
        default_spec["yaxis"] = {"label": y_field, "scale": "log"}
    if name_regex:
        default_spec["series"][0]["regex"] = name_regex
        default_spec["title"] = name_regex

    fig = figure.generate(default_spec, ctx.obj["STRICT"])
    fig.savefig(output, clip_on=False, transparent=False)


@click.command()
@click.option('-o', '--output', help="Output path.", type=click.Path(dir_okay=False, resolve_path=True))
@click.argument('spec', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.pass_context
def spec(ctx, output, spec):
    """Create a figure from a spec file."""
    include = ctx.obj["INCLUDE"]
    strict = ctx.obj["STRICT"]

    figure_spec = specification.load(spec)

    if include:
        for d in include:
            utils.debug("searching dir {}".format(d))
        figure_spec = specification.apply_search_dirs(figure_spec, include)

    fig = figure.generate(figure_spec, strict=ctx.obj["STRICT"])

    # Decide output path
    if output is None and figure_spec.get("output_file", None) is not None:
        script_dir = os.path.dirname(os.path.realpath(__file__))
        output_path = os.path.join(script_dir, figure_spec.get("output_file"))
        if not output_path.endswith(".pdf") and not output_path.endswith(".png"):
            base_output_path = output_path
            output_path = []
            for ext in figure_spec.get("output_format", ["pdf"]):
                ext = ext.lstrip(".")
                output_path.append(base_output_path + "." + ext)

    if fig is not None:
        # fig.show()
        utils.debug("writing to {}".format(output))
        fig.savefig(output, clip_on=False, transparent=False)


@click.group()
@click.option('--debug/--no-debug', help="print debug messages to stderr.", default=False)
@click.option('--include', help="Search location for input_file in spec.",
              multiple=True, type=click.Path(exists=True, file_okay=False, readable=True, resolve_path=True))
@click.option('--quiet/--no-quiet', help="don't print messages", default=False)
@click.option('--strict/--no-strict', help="require recognized spec contents", default=True)
@click.pass_context
def main(ctx, debug, include, quiet, strict):
    # This is needed if main is called via setuptools entrypoint
    if ctx.obj is None:
        ctx.obj = {}

    utils.DEBUG = debug
    utils.QUIET = quiet
    ctx.obj["INCLUDE"] = include
    ctx.obj["STRICT"] = strict


@click.command()
@click.pass_context
def version(ctx):
    """Show the ScopePlot version"""
    click.echo("ScopePlot {}".format(__version__))


@click.command()
@click.pass_context
def help(ctx):
    """Show this message and exit."""
    with click.Context(main) as ctx:
        click.echo(main.get_help(ctx))

@click.command()
@click.pass_context
@click.argument("regex")
@click.option('-i', '--input', help="Input file (- for stdin)", type=click.File(mode='rb'), default="-")
@click.option('-o', '--output', help="Output path (- for stdout)", type=click.File(mode='wb'), default="-")
def filter_name(ctx, regex, input, output):
    """Filter google benchmark results by name"""
    with GoogleBenchmark(stream=input) as b:
        output.write(b.filter_name(regex).json())

@click.command()
@click.pass_context
@click.argument('FILES', nargs=-1, type=click.File(mode='rb'))
def cat(ctx, files):
    """cat Benchmark files to standard output."""

    gb = GoogleBenchmark()
    for file in files:
        gb += GoogleBenchmark(stream=file)
    click.echo(gb.json())

main.add_command(bar)
main.add_command(deps)
main.add_command(spec)
main.add_command(version)
main.add_command(filter_name)
main.add_command(cat)
main.add_command(help)
