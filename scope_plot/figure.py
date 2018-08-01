import json
import sys
import pprint
import os
import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.figure
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


def generate(figure_spec):
    backend_str = figure_spec["backend"]
    if "bokeh" == backend_str:
        figure_spec = canonicalize_to_subplot(figure_spec)
        return bokeh_backend.generate(figure_spec)
    elif "matplotlib" == backend_str:
        return matplotlib_backend.generate(figure_spec)
    else:
        utils.halt("Unexpected backend: {}".format(backend_str))


def save(fig, paths):
    if isinstance(fig, matplotlib.figure.Figure):
        matplotlib_backend.save(fig, paths)
    elif isinstance(fig, bokeh.Figure):
        bokeh_backend.save(fig, paths)
    else:
        utils.halt("Unhandled figure type {}".format(fig))