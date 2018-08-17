import os
from scope_plot.specification import Specification
from scope_plot import backend
from scope_plot import schema

FIXTURES_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "..", "__fixtures")


def generate_fixture(name):
    figure_spec = Specification.load_yaml(os.path.join(FIXTURES_DIR, name))
    return set(figure_spec.input_files())


def test_generate_errorbar():
    ins = generate_fixture("bokeh_errorbar.yml")
    assert "hal000.ncsa.illinois.edu-UM_Coherence_GPUToGPU-0-1.json" in ins
    assert "hal000.ncsa.illinois.edu-UM_Coherence_GPUToGPU-0-2.json" in ins



