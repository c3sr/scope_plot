import os
from microbench_plot import spec
from microbench_plot import figure

FIXTURES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "__fixtures")

def test_use_search_dirs():
    figure_spec = spec.load(os.path.join(FIXTURES_DIR, "errorbar.yml"))
    figure_spec = spec.use_search_dirs(figure_spec, [FIXTURES_DIR])
    assert figure_spec["series"][0]["input_file"].startswith(FIXTURES_DIR)