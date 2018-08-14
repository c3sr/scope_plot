import os
import pytest

from scope_plot import cli

pytest_plugins = ["pytester"]

FIXTURES_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "..", "__fixtures")


@pytest.fixture
def run(testdir):
    def do_run(*args):
        args = ["scope_plot", "--debug"] + list(args)
        return testdir._run(*args)

    return do_run


@pytest.fixture
def run_spec(testdir):
    def do_run(spec_file):
        spec_path = os.path.join(FIXTURES_DIR, spec_file)
        output_path = os.path.join(FIXTURES_DIR, "test.pdf")
        args = [
            "scope_plot", "--debug", "--include", FIXTURES_DIR, "spec",
            "--output", output_path, spec_path
        ]
        return testdir._run(*args)

    return do_run


def test_cat(tmpdir, run):
    result = run("cat", os.path.join(FIXTURES_DIR, "unsorted.json"),
                 os.path.join(FIXTURES_DIR, "unsorted.json"))
    assert result.ret == 0
