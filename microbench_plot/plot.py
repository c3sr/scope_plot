#! /usr/bin/env python3

import json
import sys
import prettyprinter as pp
import os
import re
import numpy as np
import matplotlib.pyplot as plt
import yaml
import seaborn as sns

from .configure_plot import *

pp = pprint.PrettyPrinter(indent=4)

def generator_errorbar(fig, yaml_dir, plot_cfg):
    ax = fig.add_subplot(111)
    
    for s in plot_cfg["series"]:
        file_path = s["file"]
        label = s["label"]
        regex = s.get("regex", ".*")
        print("Using regex:", regex)
        yscale = float(s.get("yscale", 1.0))
        xscale = float(s.get("xscale", 1.0))
        if not os.path.isabs(file_path):
            file_path = os.path.join(yaml_dir, file_path)
        print("reading", file_path)
        with open(file_path, "rb") as f:
            j = json.loads(f.read().decode('utf-8'))
        
        pattern = re.compile(regex)
        matches = [b for b in j["benchmarks"] if pattern == None or pattern.search(b["name"])]
        means = [b for b in matches if b["name"].endswith("_mean")]
        stddevs = [b for b in matches if b["name"].endswith("_stddev")]
        x = np.array([float(b["bytes"]) for b in means])
        y = np.array([float(b["bytes_per_second"]) for b in means])
        e = np.array([float(b["bytes_per_second"]) for b in stddevs])

        # Rescale
        x *= xscale
        y *= yscale
        e *= yscale

        # pp.pprint(means)

        ax.errorbar(x, y, e, capsize=3, label=label)

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
        if axis_cfg and "scale" in axis_cfg:
            scale = axis_cfg["scale"]
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

    ax.legend()

    return fig

def generator_regplot(fig, yaml_dir, plot_cfg):

    ax = fig.add_subplot(111)

    series_cfgs = plot_cfg["series"]
    for s_cfg in series_cfgs:
        file_path = s_cfg["file"]
        label = s_cfg["label"]
        regex = s_cfg.get("regex", ".*")
        print("Using regex:", regex)
        if not os.path.isabs(file_path):
            file_path = os.path.join(yaml_dir, file_path)
        print("reading", file_path)
        with open(file_path, "rb") as f:
            j = json.loads(f.read().decode('utf-8'))
        
        pattern = re.compile(regex)
        matches = [b for b in j["benchmarks"] if pattern == None or pattern.search(b["name"])]
        means = [b for b in matches if b["name"].endswith("_mean")]
        stddevs = [b for b in matches if b["name"].endswith("_stddev")]
        x = np.array([int(b["bytes"]) for b in means])
        y = np.array([float(b["bytes_per_second"]) for b in means])
        e = np.array([float(b["bytes_per_second"]) for b in stddevs])

        color = s_cfg.get("color", "black")
        style = s_cfg.get("style", "-")

        ax = sns.regplot(ax=ax, x=x_col, y=col, data=df,
                         ci=68, label=label, color=color, line_kws={"linestyle": style})

    # Set limits
    ax.set_ylim([0, 1600])
    ylabel = plot_cfg.get("yaxis", {}).get("label", "")
    print ("set ylabel to:", ylabel)
    ax.set_ylabel(ylabel)

    # update labels
    h, l = ax.get_legend_handles_labels()
    for s_cfg in enumerate(series_cfgs):
        # def get_linregress(series):
        #     return scipy.stats.linregress(x=ax.get_lines()[series].get_xdata(), y=ax.get_lines()[series].get_ydata())
        def get_polyfit(series):
            x = ax.get_lines()[series].get_xdata()
            y = ax.get_lines()[series].get_ydata()
            z, cov = np.polyfit(x, y, 1, cov=True)
            # print np.sqrt(np.diag(cov))
            return z[0], z[1]
        # slope, intercept, r_value, p_value, std_err = get_linregress(c)
        slope, intercept = get_polyfit(c)
        l[c] = l[c] + ": " + "{:.2f}".format(slope) + " us/fault"
        print ("set label", c, "to:", l[c])
    ax.legend(h, l)
    ax.legend(frameon=False, loc='upper left', ncol=2, handlelength=4)

    title = plot_cfg.get("title", "")
    ax.set_title(title)

    ax.set_xlabel('')
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.yaxis.major.formatter._useMathText = True
    ax.yaxis.set_minor_locator(AutoMinorLocator(5))
    ax.xaxis.set_minor_locator(AutoMinorLocator(5))
    ax.yaxis.set_label_coords(0.63, 1.01)
    ax.yaxis.tick_right()

    return fig

def generate_figure(plot_cfg, root_dir):

    fig = plt.figure()


    configure_plot(fig)

    if "generator" in plot_cfg:
        if plot_cfg["generator"] == "regplot":
            fig = generator_regplot(fig, root_dir, plot_cfg)
        else:
            print("Unhandled generator!")
            assert False
    else:
        fig = generator_errorbar(fig, root_dir, plot_cfg)

    return fig

def generator_errorbar_deps(yaml_dir, plot_cfg):
    deps = ""
    
    for s in plot_cfg["series"]:
        file_path = s["file"]
        if not os.path.isabs(file_path):
            file_path = os.path.join(yaml_dir, file_path)
        deps += file_path + " "

    return deps

def generate_deps(plot_cfg, root_dir):

    if "generator" in plot_cfg:
        print("Unhandled generator!")
        assert False
    else:
        deps = generator_errorbar_deps(root_dir, plot_cfg)

    return deps

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


    if "--deps" in sys.argv[1:]:
        deps_str = generate_deps(cfg, root_dir)
        print(output_path, ":", deps_str)
    else:
        fig = generate_figure(cfg, root_dir)

        # Save plot
        print("saving to", output_path)
        fig.savefig(output_path, bbox_inches="tight",
                    clip_on=False, transparent=True)