# scope_plot bar

ScopePlot can be used to generate bar graphs without a full spec file.
For example

```
$ python -m scope_plot bar --help

Usage: __main__.py bar [OPTIONS] BENCHMARK OUTPUT

  Create a bar graph from BENCHMARK and write to OUTPUT

Options:
  --name-regex TEXT  a YAML spec for a figure
  --x-field TEXT     field for X axis
  --y-field TEXT     field for Y axis
  --help             Show this message and exit.
```

The options allow you to plot only certain entries in the file, and to select specific fields from those benchmark entries to work as the x and y axis of the plot.

```bash
python -m scope_plot bar benchmark.json results.pdf --name-regex "NUMAUM_Prefetch_GPUToHost/.*/0/0" --y-field "bytes_per_second" --x-field=bytes
```