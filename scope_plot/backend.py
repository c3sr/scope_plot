from scope_plot import utils
import scope_plot.backends.bokeh as bokeh_backend
import scope_plot.backends.matplotlib as matplotlib_backend


def run(job):
    backend_str = job.backend
    if "bokeh" == backend_str:
        return bokeh_backend.run(job)
    elif "matplotlib" == backend_str:
        return matplotlib_backend.run(job)
    else:
        utils.halt("Unexpected backend str: {}".format(backend_str))
