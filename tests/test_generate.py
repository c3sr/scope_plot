import os
from scope_plot.specification import Specification
from scope_plot import backend
from scope_plot import schema

FIXTURES_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "..", "__fixtures")


def generate_fixture(name):
    figure_spec = Specification.load_yaml(os.path.join(FIXTURES_DIR, name))
    figure_spec.find_input_files([FIXTURES_DIR])
    path = "test.pdf"
    backend_str = backend.infer_from_path(path)
    jobs = backend.construct_jobs(figure_spec, [(path, backend_str)])
    for job in jobs:
        backend.run(job)


def test_generate_errorbar():
    generate_fixture("bokeh_errorbar.yml")


def test_generate_regplot():
    generate_fixture("matplotlib_regplot.yml")


def test_generate_bar():
    generate_fixture("bokeh_bar.yml")


def test_generate_subplots():
    generate_fixture("matplotlib_subplots.yml")
