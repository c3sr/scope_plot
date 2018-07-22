# ScopePlot spec

ScopePlot can be used to generate graphs defined by a spec file

```
$ python -m scope_plot spec --help

Usage: __main__.py spec [OPTIONS] SPEC

  Create a figure from a spec file

Options:
  -o, --output PATH  Output path.
  --help             Show this message and exit.
```

Additionally, `--include` inherited from base `scope_plot` command allows you to set a search directory for the `input_file`s specified in the spec, if they are relative paths.

```bash
python -m scope_plot spec --include data spec.yml -o figure.pdf
```

The spec file controls the data present in the figure, the kind of figure generated, and the sytling of the figure.
The spec file is a YAML file with specifications for the overall figure, for plots, and for axes within the plot.
Typically, the figure specification object would be at the top level of the YAML file, and fields of the figure specification would specify the plot and within the plot, the axes.
If the figure kind has only one plot, or the plot kind has only one MatPlotLib `ax` object, then those objects can appear at the top level of the file.

## Figure Specification Object Fields

* `subplots` is a list of plot specification objects.
* `yaxis` and `xaxis` Axis specification objects for the Y and X axis of the figure.

## Plot Specification Object Fields

* `generator` controls the type of plot
* `series` a list of axes specification objects
* `pos`: a two-element list specifying the position of the plot within the figure.

## Axes specification Objects

* `label`: a string label for the series
* `input_file`: the Google Benchmark output file that is the source of the data.
May be an absolute path, or a relative path and a search directory can be specified with the `--include` command line option.
* `regex`: a regular expression for selecting entries from the `input_file`, to plot only certain benchmarks or argument combinations.
* `yfield` and `xfield`: control which fields from the benchmark output file are used for the y and x data
* `yscale` and `xscale`: is a numeric value for scaling the y data and x data before plotting.

## Axis Specification Objects

* `label`: An axis label
* `lim` a two-element list controlling the limits on the axis. For bar plots, it controls the index of bars shown, not the values associated with those indices.
* `scale` is the scaling method applied to the axis. Only `log` is supported.