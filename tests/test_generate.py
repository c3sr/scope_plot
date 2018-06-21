import os
from microbench_plot import spec
from microbench_plot import figure

FIXTURES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "__fixtures")

def generate_fixture(name):
    figure_spec = spec.load(os.path.join(FIXTURES_DIR, name))
    figure_spec = spec.use_search_dirs(figure_spec, [FIXTURES_DIR])
    fig = figure.generate(figure_spec)

def test_generate_errorbar():
    generate_fixture("errorbar.yml")

def test_generate_regplot():
    generate_fixture("regplot.yml")

def test_generate_bar():
    generate_fixture("bar.yml")

def test_generate_subplots():
    generate_fixture("subplots.yml")