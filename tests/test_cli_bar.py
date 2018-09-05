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


def test_scope_plot_bar(tmpdir, run):
    result = run("bar", os.path.join(FIXTURES_DIR, "unsorted.json"), "bytes",
                 "real_time", os.path.join(FIXTURES_DIR, "temp.pdf"))
    assert result.ret == 0


def test_scope_plot_bar_nonfloat(tmpdir, run):
    result = run("bar", os.path.join(FIXTURES_DIR, "unsorted.json"), "name",
                 "real_time", os.path.join(FIXTURES_DIR, "temp.pdf"))
    assert result.ret == 0
