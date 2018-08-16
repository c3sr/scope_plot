import os
from scope_plot.specification import Specification

FIXTURES_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "..", "__fixtures")


def test_apply_search_dirs():
    figure_spec = Specification.load_yaml(
        os.path.join(FIXTURES_DIR, "bokeh_errorbar.yml"))
    figure_spec.apply_search_dirs([FIXTURES_DIR])
    assert figure_spec["series"][0]["input_file"].startswith(FIXTURES_DIR)
