# scope_plot bar

ScopePlot can be used to generate bar graphs without a full spec file.
For example

```
$ scope_plot bar --help

Usage: scope_plot bar [OPTIONS] BENCHMARK X_FIELD Y_FIELD OUTPUT

  Create a bar graph from BENCHMARK data (default stdin) using X_FIELD and
  Y_FIELD as the fields for the x- and y-data respectively, rendering to
  OUTPUT.

Options:
  --filter-name TEXT  only keep benchmarks with this name
  --help              Show this message and exit.
```

The options allow you to plot only certain entries in the file, and to select specific fields from those benchmark entries to work as the x and y axis of the plot.

```bash
python -m scope_plot bar benchmark.json results.pdf --name-regex "NUMAUM_Prefetch_GPUToHost/.*/0/0" --y-field "bytes_per_second" --x-field=bytes
```

Build [Scope](github.com/rai-project/scope) with support for [Comm|Scope](github.com/rai-project/comm_scope).

    cd scope
    cmake -DENABLE_COMM ...

Try generating some data from the `Comm_NUMAMemcpy_HostToPinned/.*/0/0` sequence of benchmarks.
This repeats each benchmark 5 times to generate aggregate data.

    ./scope --benchmark_filter="Comm_NUMAMemcpy_HostToPinned/.*/0/0" --benchmark_out=Comm_NUMAMemcpy_HostToPinned.json --benchmark_repetitions=5

Create a bar graph in `output.pdf`.
Only keep entries with "mean" in the name (the mean of the 5 aggregated entries).

    scope_plot bar --filter-name=mean Comm_NUMAMemcpy_HostToPinned.json bytes bytes_per_second output.pdf