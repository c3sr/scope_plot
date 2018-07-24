import os
import pytest

from scope_plot import cli

pytest_plugins = ["pytester"]

FIXTURES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "__fixtures")

@pytest.fixture
def run(testdir):
    def do_run(*args):
        args = ["scope_plot"] + list(args)
        return testdir._run(*args)
    return do_run

def test_scope_plot_help(tmpdir, run):
    result = run("--help")
    assert result.ret == 0

def test_scope_plot_version(tmpdir, run):
    result = run("version")
    assert result.ret == 0

def test_scope_plot_merge(tmpdir, run):
    result = run("merge", FIXTURES_DIR)
    assert result.ret == 0

def test_scope_plot_bar(tmpdir, run):
    result = run("bar", os.path.join(FIXTURES_DIR, "unsorted.json"), os.path.join(FIXTURES_DIR, "temp.pdf"))
    assert result.ret == 0

def test_spec_missing(tmpdir, run):
    result = run("--include", FIXTURES_DIR, "spec", "--output", "test.pdf", os.path.join(FIXTURES_DIR, "bar_missing.yml"))
    assert result.ret == 0