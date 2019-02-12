Changelog
=========

Release 0.2.3 (Development)
---------------------------
* Use `agg` matplotlib backend if tkinter cannot be imported
* allow subplots to have error bars
* hide error bar labels by default
* add linestyle spec to matplotlib errorbars
* don't resolve path for scope_plot deps since makefiles probably expect target names to be relative
* print error when an input file is not found

Release 0.2.2 (Development)
---------------------------
* Add NOTICE and Apache 2.0 LICENSE
* Fixed a bug where ScopePlot would not run without DISPLAY environment set
* Use TkAgg backend on macOS to support running from a virtualenv
* Allow non-numeric x data in bar plots
* Add support for the `output` field in spec files


Release 0.2.1 (Development)
---------------------------
* Fix bugs in handling labels, color, regex for matplotlib and regex backends

Release 0.2.0 (Development)
---------------------------

* Refactor some underlying data structures
* break matplotlib backend

Release 0.1.5 (Development)
---------------------------

* Enable strict checking of spec files by default
* Sort benchmark data
* Omit invalid benchmark data

Release 0.1.3 (Development)
---------------------------

* Change documentation to docsify
* Fix a bug with unexpected "strict" argument

Release 0.1.2 (Development)
---------------------------

* rename to `scope_plot`
* Initial support for `spec` and `bar` subcommands.
