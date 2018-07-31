import os
from scope_plot import specification

FIXTURES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "__fixtures")


def test_errorbar_spec():
    figure_spec = specification.load(os.path.join(FIXTURES_DIR, "bokeh_errorbar.yml"))
    assert figure_spec["backend"] == "bokeh"
    assert figure_spec["type"] == "errorbar"


def test_errorbar_spec():
    figure_spec = specification.load(os.path.join(FIXTURES_DIR, "regplot.yml"))
    assert figure_spec["generator"] == "regplot"


def test_errorbar_spec():
    figure_spec = specification.load(os.path.join(FIXTURES_DIR, "bokeh_bar.yml"))
    assert figure_spec["backend"] == "bokeh"
    assert figure_spec["type"] == "bar"
