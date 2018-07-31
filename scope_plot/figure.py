import json
import sys
import pprint
import os
import re
import numpy as np
import matplotlib.pyplot as plt
import yaml
from future.utils import iteritems
from voluptuous import Required, Schema

from scope_plot import utils
from scope_plot.error import UnknownGenerator
from scope_plot.schema import validate
from scope_plot import schema
import scope_plot.backends.bokeh as bokeh_backend
import scope_plot.backends.matplotlib as matplotlib_backend
from scope_plot.specification import canonicalize_to_subplot

def generate(figure_spec, strict):

    # verify that info for backend configuration is present
    if "backend" not in figure_spec:
        utils.halt("Expected to find backend in specification")
    backend_str = figure_spec["backend"]
    del figure_spec["backend"]

    if "bokeh" == backend_str:
        figure_spec = canonicalize_to_subplot(figure_spec)
        bokeh_backend.generate(figure_spec)
        return
    elif "matplotlib" == backend_str:
        matplotlib_backend.generate(figure_spec)


    fig_size = None
    if "size" in figure_spec:
        fig_size = figure_spec["size"]
        del figure_spec["size"]

    if "subplots" in figure_spec:
        fig = generate_subplots(figure_spec, strict)
    else:
        fig, axs = plt.subplots(1, 1, squeeze=False)
        generate_axes(axs[0, 0], figure_spec, strict)

    consume_keys = []
    for key, value in iteritems(figure_spec):
        if strict:
            utils.halt("unrecognized key {} in figure_spec".format(key))
        else:
            utils.debug("unrecognized key {} in figure_spec".format(key))
        consume_keys += [key]
    for key in consume_keys:
        del figure_spec[key]

    # Set the figure size
    fig.set_tight_layout(True)
    fig.autofmt_xdate()
    if fig_size:
        utils.debug("Using figsize {}".format(fig_size))
        fig.set_size_inches(fig_size)

    return fig
