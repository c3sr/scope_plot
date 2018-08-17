import os
import pytest

from scope_plot import cli

pytest_plugins = ["pytester"]

FIXTURES_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "..", "__fixtures")


@pytest.fixture
def run_deps(testdir):
    def do_run(spec_file):
        spec_path = os.path.join(FIXTURES_DIR, spec_file)
        output_path = os.path.join(FIXTURES_DIR, "test.pdf")
        args = [
            "scope_plot", "--debug", "--include", FIXTURES_DIR, "deps",
            output_path, spec_path, "test"
        ]
        return testdir._run(*args)

    return do_run


def test_spec_missing(tmpdir, run_deps):
    result = run_deps("matplotlib_bar_missing.yml")
    assert result.ret == 0

