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
    figure_spec = Specification.load_yaml(spec)
    include_dirs = ctx.obj["INCLUDE"]
    utils.debug("Searching for input_file values in: {}".format(include_dirs))
    figure_spec.find_input_files(include_dirs)
    utils.debug("Saving deps to {}".format(output))
    figure_spec.save_makefile_deps(output, target)


@click.command()
@click.argument(
    'benchmark', type=click.Path(dir_okay=False, exists=True, resolve_path=True))
@click.argument('x-field')
@click.argument('y-field')
@click.argument('output', type=click.Path(dir_okay=False, resolve_path=True))
@click.option('--filter-name', help="only keep benchmarks with this name")
@click.pass_context
def bar(ctx, benchmark, filter_name, output, x_field, y_field):
    """
    Create a bar graph from BENCHMARK data (default stdin) using X_FIELD and Y_FIELD
    as the fields for the x- and y-data respectively, rendering to OUTPUT.
    """

    root, ext = os.path.splitext(output)

    bar_spec = {
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
    if filter_name:
        bar_spec["series"][0]["regex"] = filter_name
        bar_spec["title"] = filter_name

    bar_spec = Specification.load_dict(bar_spec)
    backend_str = backend.infer_from_path(output)
    jobs = backend.construct_jobs(bar_spec, [(output, backend_str)])
    for job in jobs:
        backend.run(job)


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
    figure_spec = Specification.load_yaml(spec)

    # apply include directories
    if include:
        utils.debug("searching dirs {}".format(include))
        figure_spec.find_input_files(include)

    # output path from command line or spec
    if output:
        utils.debug("output path from command line: {}".format(output))
        backend_str = backend.infer_from_path(output)
        utils.debug("inferred backend: {}".format(backend_str))
        output_specs = [(output, backend_str)]
    else:
        output_specs = figure_spec.output_specs()

    # prepend prefix to output_path
    if output_prefix:
        output_specs = [(os.path.join(output_prefix, path), backend_str) for path, backend_str in output_specs]
        for (path, backend_str) in output_specs:
            utils.debug("prefixed output path: {}".format(path))

    # determine the figures that need to be constructed
    jobs = backend.construct_jobs(figure_spec, output_specs)

    utils.debug("{} jobs to run".format(len(jobs)))

    # run the jobs
    for job in jobs:
        backend.run(job)


@click.group()
@click.option(
    '--debug/--no-debug',
    help="print debug messages to stderr.",
    default=False)
@click.option(
    "-I",
    '--include',
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
@click.argument("input", type=click.File(mode='rb'), default="-")
@click.argument("regex")
@click.argument("output", type=click.File(mode='wb'), default="-")
def filter_name(ctx, regex, input, output):
    """
    Filter Google Benchmark JSON files by benchmark name.
    INPUT and OUTPUT are optional files, otherwise stdin/stdout are used.
    REGEX is a regular expression for names to keep.
    """
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
