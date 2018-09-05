import os
from scope_plot.specification import Specification
from scope_plot import backend
from scope_plot import schema

THIS_DIR = os.path.dirname(os.path.realpath(__file__))


def generate_html(name):
    figure_spec = Specification.load_yaml(os.path.join(THIS_DIR, name))
    figure_spec.find_input_files([THIS_DIR])
    path = "test.html"
    backend_str = backend.infer_from_path(path)
    jobs = backend.construct_jobs(figure_spec, [(path, backend_str)])
    for job in jobs:
        backend.run(job)


def generate_pdf(name):
    figure_spec = Specification.load_yaml(os.path.join(THIS_DIR, name))
    figure_spec.find_input_files([THIS_DIR])
    path = "test.pdf"
    backend_str = backend.infer_from_path(path)
    jobs = backend.construct_jobs(figure_spec, [(path, backend_str)])
    for job in jobs:
        backend.run(job)


def test_figure_pdf():
    """xfield and yfield defined at figure level"""
    generate_pdf("level_figure.yml")


def test_figure_html():
    """xfield and yfield defined at figure level"""
    generate_html("level_figure.yml")


def test_series_pdf():
    """xfield and yfield defined at series level"""
    generate_pdf("level_series.yml")


def test_series_html():
    """xfield and yfield defined at series level"""
    generate_html("level_series.yml")


def test_plot_pdf():
    """xfield and yfield defined at plot level"""
    generate_pdf("level_plot.yml")


def test_plot_html():
    """xfield and yfield defined at plot level"""
    generate_html("level_plot.yml")
