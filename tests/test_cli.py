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
        args = [
            "scope_plot", "--debug", "--include", FIXTURES_DIR, "spec",
            "--output", "test.pdf", spec_path
        ]
        return testdir._run(*args)

    return do_run


def test_scope_plot_help(tmpdir, run):
    result = run("--help")
    assert result.ret == 0


def test_scope_plot_version(tmpdir, run):
    result = run("version")
    assert result.ret == 0


def test_scope_plot_cat(tmpdir, run):
    result = run("cat", os.path.join(FIXTURES_DIR, "unsorted.json"),
                 os.path.join(FIXTURES_DIR, "unsorted.json"))
    assert result.ret == 0


def test_scope_plot_bar(tmpdir, run):
    result = run("bar", os.path.join(FIXTURES_DIR, "unsorted.json"), "bytes",
                 "real_time", os.path.join(FIXTURES_DIR, "temp.pdf"))
    assert result.ret == 0


def test_spec_missing(tmpdir, run_spec):
    result = run_spec("matplotlib_bar_missing.yml")
    assert result.ret == 0


def test_bokeh_bar(tmpdir, run_spec):
    result = run_spec("bokeh_bar.yml")
    assert result.ret == 0


def test_bokeh_errorbar(tmpdir, run_spec):
    result = run_spec("bokeh_errorbar.yml")
    assert result.ret == 0


def test_bokeh_subplots(tmpdir, run_spec):
    result = run_spec("bokeh_subplots.yml")
    assert result.ret == 0


def test_matplotlib_bar(tmpdir, run_spec):
    result = run_spec("matplotlib_bar.yml")
    assert result.ret == 0


def test_matplotlib_errorbar(tmpdir, run_spec):
    result = run_spec("matplotlib_errorbar.yml")
    assert result.ret == 0


def test_matplotlib_regplot(tmpdir, run_spec):
    result = run_spec("matplotlib_regplot.yml")
    assert result.ret == 0


def test_matplotlib_subplots(tmpdir, run_spec):
    result = run_spec("matplotlib_subplots.yml")
    assert result.ret == 0
