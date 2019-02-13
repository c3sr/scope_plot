# ScopePlot

[![Build Status](https://travis-ci.com/c3sr/scope_plot.svg?branch=master)](https://travis-ci.com/c3sr/scope_plot)


Plot Google Benchmark results

## Getting Started with ScopePlot

ScopePlot is available on [PyPI](https://pypi.org/project/scope-plot/) can be installed with `pip`

    $ python -m pip install scope_plot

To install the latest development version from [Github](https://github.com/rai-project/scope_plot)

    $ python -m pip install git+git://github.com/c3sr/scope_plot.git
    
To use a version in a local directory

    $ python -m pip install -e ${HOME}/repos/scope_plot

If your current Python installation doesn't have pip available, try [get-pip.py](bootstrap.pypa.io)

After installing ScopePlot you can use it like any other Python module.
Here's a very simple example:

```bash
$ python -m scope_plot bar data.json
```

There are multiple subcommands available

```
$ python -m scope_plot --help

Usage: __main__.py [OPTIONS] COMMAND [ARGS]...

Options:
  --debug / --no-debug  print debug messages to stderr.
  --include DIRECTORY   Search location for input_file in spec.
  --help                Show this message and exit.

Commands:
  bar   Create a bar graph from BENCHMARK and write...
  deps  Create a Makefile dependence
  spec  Create a figure from a spec file
```

More information about the subcommands can be accessed with `python -m scope_plot COMMAND --help`, and also in the documentation: [bar](docs/bar.md), [spec](docs/spec.md), [deps](docs/makefiles.md).

## Prerequisites

You may have to install the following for scope_plot to install matplotlib

    sudo apt install python-dev libfreetype6-dev and libpng-dev

API Reference
-------------

coming soon...

Support / Report Issues
-----------------------

All support requests and issue reports should be
[filed on Github as an issue](https://github.com/rai-project/scope_plot/issues).
Make sure to follow the template so your request may be as handled as quickly as possible.
Please respect contributors by not using personal contacts for support requests.

Contributing
------------

We happily welcome contributions, please see [our guide for Contributors](CONTRIBUTORS.md) for the best places to start and help.

License
-------

scope_plot is made available under the Apache 2.0 License. For more details, see [LICENSE.txt](https://github.com/c3sr/scope_plot/blob/master/LICENSE.txt).
