"""Functions for creating plots from JobRecords.

Note that all plots are created in png format. The specified 
filepath should end in '.png'."""

import sys
import os

import matplotlib
import pandas

from .core import JobRecord


def create_histogram(attr, joblist, xtit, size, filepath):
    """Create a histogram of a given job attribute.

    Arguments:
        'attr' - the name of the JobRecord attribute.
        'joblist' - a list of JobRecords to consider. 
        'xtit' - the title of the x-axis.
        'size' - a tuple (x,y) in number of inches (dpi=80).
        'filepath' - the absolute path to the file to be created and 
                     should end in '.png'"""
    matplotlib.use('Agg')
    data = [float(getattr(job, attr)) for job in joblist if hasattr(job, attr)]
    df = pandas.DataFrame({'col':data})
    plot = df.plot(kind='hist', figsize=size, legend=False)
    plot.set_xlabel(xtit)
    plot.set_ylabel('count')
    plot.grid(False)
    # pad the y-axis max a bit
    x1, x2, y1, y2 = plot.axis()
    plot.axis((x1, x2, y1, y2 * 1.1))
    plot.figure.savefig(filepath, 
                        dpi=80, 
                        bbox_inches='tight',
                        pad_inches=0.2)
