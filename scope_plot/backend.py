from scope_plot import utils
import scope_plot.backends.bokeh as bokeh_backend
import scope_plot.backends.matplotlib as matplotlib_backend
import os
from sys import exit


class Job(object):
    """Job holds specification for generating a figure, as well as a specification for saving the figure"""

    def __init__(self, figure_spec, path, backend):
        self.figure_spec = figure_spec
        self.backend = backend
        self.path = path


def run(job):
    backend_str = job.backend
    if "bokeh" == backend_str:
        return bokeh_backend.run(job)
    elif "matplotlib" == backend_str:
        return matplotlib_backend.run(job)
    else:
        utils.halt("Unexpected backend str: {}".format(backend_str))


def infer_from_path(output_path):
    _, file_extension = os.path.splitext(output_path)
    if file_extension == ".pdf" or file_extension == ".png":
        utils.debug(
            "inferring matplotlib backend from output path {}".format(
                output_path))
        return 'matplotlib'
    elif file_extension == ".svg" or file_extension == ".html":
        utils.debug("inferring bokeh backend from output path {}".format(
            output_path))
        return 'bokeh'
    else:
        utils.error("No backend for extension {}".format(file_extension))
        exit(-1)


def construct_jobs(spec, output_specs):
    """ construct jobs from spec, ignoring output field in spec and using output_specs"""
    jobs = []
    for output_spec in output_specs:
        output_path, backend = output_spec
        jobs += [Job(spec, output_path, backend)]
    return jobs
