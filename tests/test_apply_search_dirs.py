import os
from scope_plot import specification
from scope_plot import figure

FIXTURES_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "..", "__fixtures")


def test_apply_search_dirs():
    figure_spec = specification.load(
        os.path.join(FIXTURES_DIR, "bokeh_errorbar.yml"))
    figure_spec = specification.apply_search_dirs(figure_spec, [FIXTURES_DIR])
    assert figure_spec["series"][0]["input_file"].startswith(FIXTURES_DIR)
