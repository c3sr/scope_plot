import os
from scope_plot.specification import Specification

FIXTURES_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "..", "__fixtures")


def test_find_input_files():
    figure_spec = Specification.load_yaml(
        os.path.join(FIXTURES_DIR, "bokeh_errorbar.yml"))
    figure_spec.find_input_files([FIXTURES_DIR])
    assert figure_spec.subplots[0].series[0].input_file().startswith(FIXTURES_DIR)
