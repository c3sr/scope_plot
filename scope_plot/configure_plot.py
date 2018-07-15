import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter, AutoMinorLocator
import matplotlib as mpl


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
def configure_plot(fig):
    dirFile = os.path.dirname(os.path.realpath(__file__))
    # Load style file
    fig.style.use(os.path.join(dirFile, 'PaperDoubleFig.mplstyle'))
