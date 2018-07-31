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


def generate(figure_spec):

    # verify that info for backend configuration is present

    backend_str = figure_spec["backend"]
    del figure_spec["backend"]

    if "bokeh" == backend_str:
        figure_spec = canonicalize_to_subplot(figure_spec)
        bokeh_backend.generate(figure_spec)
        return
    elif "matplotlib" == backend_str:
        matplotlib_backend.generate(figure_spec)
    else:
        utils.halt("Unexpected backend: {}", backend_str)
