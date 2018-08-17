from scope_plot import utils
import scope_plot.backends.bokeh as bokeh_backend
import scope_plot.backends.matplotlib as matplotlib_backend
import os


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


def construct_jobs(spec, output_paths):
    """ construct jobs from spec, ignoring output field in spec and using output_paths"""
    jobs = []
    for output_path in output_paths:
        _, file_extension = os.path.splitext(output_path)
        if file_extension == ".pdf" or file_extension == ".png":
            utils.debug(
                "inferring matplotlib backend from output path {}".format(
                    output_path))
            backend = 'matplotlib'
        elif file_extension == ".svg" or file_extension == ".html":
            utils.debug("inferring bokeh backend from output path {}".format(
                output_path))
            backend = 'bokeh'
        else:
            utils.halt("No backend for extension {}".format(file_extension))

        jobs += [Job(spec, output_path, backend)]
    return jobs
