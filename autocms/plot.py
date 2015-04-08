"""Functions for creating plots from JobRecords.

Note that all plots are created in png format. The specified
filepath should end in '.png'."""

import sys
import os
import datetime

import matplotlib
import pandas

from .core import JobRecord


def convert_timestamp(ts):
    """Convert raw unix timestamp (int) to matplotlib date object."""
    dt_object = datetime.datetime.fromtimestamp(ts)
    return matplotlib.dates.date2num(dt_object)


def create_histogram(attr, joblist, xtit, size, filepath):
    """Create a histogram of a given job attribute.

    Arguments:
        'attr' - the name of the JobRecord attribute.
        'joblist' - a list of JobRecords to consider.
        'xtit' - the title of the x-axis.
        'size' - a tuple (x,y) in number of inches (dpi=80).
        'filepath' - the absolute path of the file to be created and
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


def create_run_and_waittime_plot(joblist, size, filepath, logscale=False):
    """Create a scatterplot of recent job run and wait times."

    Arguments:
        'joblist' - a list of JobRecords to consider.
        'size' - a tuple (x,y) in number of inches (dpi=80).
        'filepath' - the absolute path to the file to be created and
                     should end in '.png'
        'logscale' - use a logarithmic scale on the vertical axis."""
    matplotlib.use('Agg')
    data = [(convert_timestamp(job.start_time),
            job.run_time(), job.wait_time()) for job in joblist]
    df = pandas.DataFrame(data, columns=['start', 'run', 'wait'])
    ax = df.plot(kind='scatter', figsize=size, x='start', y='run',
                 color='DarkGreen', label='Run Time')
    df.plot(kind='scatter', figsize=size, x='start', y='wait',
            color='DarkRed', label='Wait Time', ax=ax)
    ax.set_xlabel('Job Start Time')
    ax.set_ylabel('Wall Clock Time [seconds]')
    y_minimum = 0
    if logscale:
        ax.set_yscale('log')
        y_minimum = 1
    ax.xaxis.set_major_locator(matplotlib.dates.HourLocator(interval=4))
    ax.xaxis.set_major_formatter(
        matplotlib.dates.DateFormatter('%a\n%H:%M')
    )
    ax.grid(False)
    # pad the y-axis max a bit, force y-axis min to zero (1 if log scaled)
    x1, x2, y1, y2 = ax.axis()
    ax.axis((x1, x2, y_minimum, y2 * 1.1))
    ax.figure.savefig(filepath,
                      dpi=80,
                      bbox_inches='tight',
                      pad_inches=0.2)
