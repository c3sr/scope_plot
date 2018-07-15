import os
import pytest

from scope_plot import cli

pytest_plugins = ["pytester"]


@pytest.fixture
def run(testdir):
    def do_run(*args):
        args = ["scope_plot"] + list(args)
        return testdir._run(*args)
    return do_run


def test_scope_plot_help(tmpdir, run):
    result = run("--help")
    assert result.ret == 0

# def test_scope_plot_version(tmpdir, run):
#     input = tmpdir.join("example.txt")
#     content = unicode("\xc3\xa4\xc3\xb6", "latin1")
#     with input.open("wb") as f:
#         f.write(content.encode("latin1"))
#     output = tmpdir.join("example.txt.utf8")
#     result = run("-flatin1", "-tutf8", input, "-o", output)
#     assert result.ret == 0
#     with output.open("rb") as f:
#         newcontent = f.read()
#     assert content.encode("utf8") == newcontent
