import os
import re
from setuptools import setup, find_packages

base_package = 'scope_plot'

# Get the version (borrowed from SQLAlchemy)
base_path = os.path.dirname(__file__)
with open(os.path.join(base_path, 'scope_plot', '__init__.py')) as f:
    module_content = f.read()
    VERSION = re.compile(r'.*__version__ = \'(.*?)\'',
                         re.S).match(module_content).group(1)
    LICENSE = re.compile(r'.*__license__ = \'(.*?)\'',
                         re.S).match(module_content).group(1)

with open('README.md') as f:
    readme = f.read()

with open('CHANGELOG.md') as f:
    changes = f.read()

requirements = [
    "bokeh>=0.13,<0.14",
    "click>=6.7,<6.8",
    "future>=0.16.0,<0.17",
    "matplotlib>=2.2,<2.3",
    "numpy>=1.14,<1.15",
    "pandas>=0.23,<0.24",
    "pyyaml>=3.13,<3.14",
    "selenium>=3.13,<3.14",
    "voluptuous>=0.11,<0.12",
]

packages = [
    base_package + '.' + x
    for x in find_packages(os.path.join(base_path, base_package))
]
if base_package not in packages:
    packages.append(base_package)

if __name__ == '__main__':
    setup(
        name='scope_plot',
        description='Plot Google Benchmark results',
        long_description='\n\n'.join([readme, changes]),
        license=LICENSE,
        url='http://scope_plot.readthedocs.io',
        version=VERSION,
        author='Abdul Dakkak',
        author_email='dakkak@illinois.edu',
        maintainer='Carl Pearson',
        maintainer_email='pearson@illinois.edu',
        entry_points={'console_scripts': ['scope_plot=scope_plot.cli:main']},
        install_requires=requirements,
        keywords=['scope_plot'],
        packages=packages,
        zip_safe=False,
        classifiers=[
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6'
        ])
