import argparse
import json
import os.path
import sys
import click
import glob

from scope_plot import specification
from scope_plot.specification import Specification
from scope_plot import schema
from scope_plot.benchmark import GoogleBenchmark
from scope_plot import utils
from scope_plot.error import NoBackendError
from scope_plot import backend
from scope_plot.__init__ import __version__
""" If the module has a command line interface then this
file should be the entry point for that interface. """


@click.command()
@click.argument('output', type=click.Path(dir_okay=False, resolve_path=True))
@click.argument(
    'spec', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.argument('target', type=click.Path(dir_okay=False, resolve_path=True))
@click.pass_context
def deps(ctx, output, spec, target):
    """Create a Makefile dependence"""

    utils.debug("Loading {}".format(spec))
    figure_spec = specification.load(spec)
    include_dirs = ctx.obj["INCLUDE"]
    utils.debug("Searching for input_file values in: {}".format(include_dirs))
    figure_spec = specification.apply_search_dirs(figure_spec, include_dirs)
    figure_deps = specification.get_deps(figure_spec)
    utils.debug("Saving deps to {}".format(output))
    specification.save_makefile_deps(output, target, figure_deps)


@click.command()
@click.argument(
    'benchmark',
    type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.argument('x-field')
@click.argument('y-field')
@click.argument('output', type=click.Path(dir_okay=False, resolve_path=True))
@click.option('--name-regex', help="a YAML spec for a figure")
@click.pass_context
def bar(ctx, benchmark, name_regex, output, x_field, y_field):
    """Create a bar graph."""
    bar_spec = {
        "backend": "matplotlib",
        "type": "bar",
        "series": [{
            "input_file": benchmark,
        }],
    }

    bar_spec["series"][0]["label"] = ""
    if x_field:
        bar_spec["series"][0]["xfield"] = x_field
        bar_spec["xaxis"] = {"label": x_field}
    if y_field:
        bar_spec["series"][0]["yfield"] = y_field
        bar_spec["yaxis"] = {"label": y_field, "type": "log"}
    if name_regex:
        bar_spec["series"][0]["regex"] = name_regex
        bar_spec["title"] = name_regex

    bar_spec = schema.validate(bar_spec)
    fig = figure.generate(bar_spec)
    utils.debug("saving figure to {}".format(output))

    figure.save(fig, [output])


@click.command()
@click.option(
    '-o',
    '--output',
    help="override spec output paths",
    type=click.Path(dir_okay=False, resolve_path=True))
@click.option('--output-prefix', help="prepend to all output paths")
@click.argument(
    'spec', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.pass_context
def spec(ctx, output, output_prefix, spec):
    """Create a figure from a spec file."""
    include = ctx.obj["INCLUDE"]

    # load YAML spec file
    figure_spec = specification.load(spec)

    # validate specification
    try:
        figure_spec = schema.validate(figure_spec)
    except NoBackendError as e:
        utils.halt("in {}: {}".format(spec, e))

    # apply include directories
    if include:
        for d in include:
            utils.debug("searching dir {}".format(d))
        figure_spec = specification.apply_search_dirs(figure_spec, include)

    # determine the figures that need to be constructed
    jobs = specification.construct_jobs(figure_spec, output, output_prefix)

    utils.debug("{} generation jobs".format(len(jobs)))

    for job in jobs:
        backend.run(job)
        


@click.group()
@click.option(
    '--debug/--no-debug',
    help="print debug messages to stderr.",
    default=False)
@click.option(
    "-I", '--include',
    help="Search location for input_file in spec.",
    multiple=True,
    type=click.Path(
        exists=True, file_okay=False, readable=True, resolve_path=True))
@click.option('--quiet/--no-quiet', help="don't print messages", default=False)
@click.pass_context
def main(ctx, debug, include, quiet):
    # This is needed if main is called via setuptools entrypoint
    if ctx.obj is None:
        ctx.obj = {}

    utils.DEBUG = debug
    utils.QUIET = quiet
    ctx.obj["INCLUDE"] = include

    utils.debug("Running: {}".format(" ".join(sys.argv)))


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
@click.option(
    '-i',
    '--input',
    help="Input file (- for stdin)",
    type=click.File(mode='rb'),
    default="-")
@click.option(
    '-o',
    '--output',
    help="Output path (- for stdout)",
    type=click.File(mode='wb'),
    default="-")
def filter_name(ctx, regex, input, output):
    """Filter google benchmark results by name"""
    with GoogleBenchmark(stream=input) as b:
        output.write(b.keep_name_regex(regex).json())


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
