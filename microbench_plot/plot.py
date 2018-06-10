#! /usr/bin/env python3

import json
import sys
import pprint
import os
import re
import numpy as np
import matplotlib.pyplot as plt
import yaml
import seaborn as sns
import pandas as pd
from matplotlib.ticker import ScalarFormatter, AutoMinorLocator
import matplotlib as mpl

pp = pprint.PrettyPrinter(indent=4)

def generator_bar(fig, yaml_dir, plot_cfg):
    ax = fig.add_subplot(1, 1, 1)
    bar_width = plot_cfg.get("bar_width", 0.8)
    num_series = len(plot_cfg["series"])

    default_file = plot_cfg.get("file", "not_found")

    default_x_scale =  eval(str(plot_cfg.get("xaxis", {}).get("scale", 1.0)))
    default_y_scale =  eval(str(plot_cfg.get("yaxis", {}).get("scale", 1.0)))

    default_x_field = plot_cfg.get("xaxis", {}).get("field", "real_time")
    default_y_field = plot_cfg.get("yaxis", {}).get("field", "real_time")

    for c, s in enumerate(plot_cfg["series"]):
        file_path = s.get("file", default_file)
        label = s["label"]
        print(label)
        regex = s.get("regex", ".*")
        print("Using regex:", regex)
        yscale = eval(str(s.get("yscale", default_y_scale)))
        xscale = eval(str(s.get("xscale", default_x_scale)))
        if not os.path.isabs(file_path):
            file_path = os.path.join(yaml_dir, file_path)
        print("reading", file_path)
        with open(file_path, "rb") as f:
            j = json.loads(f.read().decode('utf-8'))
        
        pattern = re.compile(regex)
        matches = [b for b in j["benchmarks"] if pattern == None or pattern.search(b["name"])]
        times = matches

        if len(times) == 0:
            continue

        xfield = s.get("xfield", default_x_field)
        x = np.array([float(b[xfield]) for b in times])

        yfield = s.get("yfield", default_y_field)
        y = np.array([float(b[yfield]) for b in times])

        # Rescale
        x *= xscale
        y *= yscale

        # pp.pprint(y)

        # ax.bar(x + (c - num_series/2) * bar_width, y, width=bar_width, label=label, align='center')
        ax.bar(x + bar_width*c, y, width=bar_width, label=label, align='center')
        ax.set_xticks(x + 1.5 * bar_width)
        if c == 0:
            ax.set_xticklabels((x + c*bar_width).round(1))
        # ax.bar(x , y, width=bar_width, label=label, align='center')

    if "yaxis" in plot_cfg:
        axis_cfg = plot_cfg["yaxis"]
        if axis_cfg and "lim" in axis_cfg:
            lim = axis_cfg["lim"]
            print("setting ylim", lim)
            ax.set_ylim(lim)
        if axis_cfg and "label" in axis_cfg:
            label = axis_cfg["label"]
            print("setting ylabel", label)
            ax.set_ylabel(label)

    if "xaxis" in plot_cfg:
        axis_cfg = plot_cfg["xaxis"]
        if axis_cfg and "lim" in axis_cfg:
            lim = axis_cfg["lim"]
            print("setting xlim", lim)
            ax.set_xlim(lim)
        if axis_cfg and "scaling_function" in axis_cfg:
            scale = axis_cfg["scaling_function"]
            print("setting xscale", scale)
            ax.set_xscale(scale, basex=2)
        if axis_cfg and "label" in axis_cfg:
            label = axis_cfg["label"]
            print("setting xlabel", label)
            ax.set_xlabel(label)

    if "title" in plot_cfg:
        title = plot_cfg["title"]
        print("setting title", title)
        ax.set_title(title)

    # ax.legend(loc='upper left')
    ax.legend(loc='best')

    return fig


def generate_figure(plot_cfg, root_dir):


    fig = plt.figure()
    fig.set_tight_layout(True)
    fig.autofmt_xdate()

    fig = generator_bar(fig, root_dir, plot_cfg)

    return fig


# Make some style choices for plotting
color_wheel = ['#329932',
               '#ff6961',
               'b',
               '#6a3d9a',
               '#fb9a99',
               '#e31a1c',
               '#fdbf6f',
               '#ff7f00',
               '#cab2d6',
               '#6a3d9a',
               '#ffff99',
               '#b15928',
               '#67001f',
               '#b2182b',
               '#d6604d',
               '#f4a582',
               '#fddbc7',
               '#f7f7f7',
               '#d1e5f0',
               '#92c5de',
               '#4393c3',
               '#2166ac',
               '#053061']
dashes_styles = [[3, 1],
                [1000, 1],
                [2, 1, 10, 1],
                [4, 1, 1, 1, 1, 1]]


# ===========================================================
# Directory and filename; style file open
# ===========================================================
def configure_plot():
    dirFile = os.path.dirname(os.path.realpath(__file__))
    # Load style file
    plt.style.use(os.path.join(dirFile, 'PaperDoubleFig.mplstyle'))



if __name__ == '__main__':

    if len(sys.argv) >= 3:
        output_path = sys.argv[1]
        yaml_path = sys.argv[2]
    else:
        sys.exit(1)

    root_dir = os.path.dirname(os.path.abspath(yaml_path))

    # load the config
    with open(yaml_path, 'rb') as f:
        cfg = yaml.load(f)


    configure_plot()

    fig = generate_figure(cfg, root_dir)
    if fig is not None:
        # Save plot
        print("saving to", output_path)
        fig.show()
        fig.savefig(output_path,  clip_on=False, transparent=True)