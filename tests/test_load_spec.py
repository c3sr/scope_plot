import os
from scope_plot import specification

FIXTURES_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "..", "__fixtures")


def test_bokeh_errorbar_spec():
    figure_spec = specification.load(
        os.path.join(FIXTURES_DIR, "bokeh_errorbar.yml"))
    assert figure_spec["type"] == "errorbar"


def test_bokeh_bar_spec():
    figure_spec = specification.load(
        os.path.join(FIXTURES_DIR, "bokeh_bar.yml"))
    assert figure_spec["type"] == "bar"


def test_bokeh_subplots_spec():
    figure_spec = specification.load(
        os.path.join(FIXTURES_DIR, "bokeh_subplots.yml"))
    assert figure_spec["subplots"][0]["type"] == "errorbar"


def test_matplotlib_regplot_spec():
    figure_spec = specification.load(
        os.path.join(FIXTURES_DIR, "matplotlib_regplot.yml"))
    assert figure_spec["type"] == "regplot"
