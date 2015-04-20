"""Functions for creating plots from JobRecords.

Note that all plots are created in png format. The specified
filepath should end in '.png'."""

import sys
import os
import math
import time
import datetime

import matplotlib
matplotlib.use('Agg')
import pandas as pd
import matplotlib.pyplot as plt

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
    data = [float(getattr(job, attr)) for job in joblist if hasattr(job, attr)]
    df = pd.DataFrame({'col':data})
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
    data = [(convert_timestamp(job.start_time),
            job.run_time(), job.wait_time()) for job in joblist]
    df = pd.DataFrame(data, columns=['start', 'run', 'wait'])
    ax = df.plot(kind='scatter', figsize=size, x='start', y='run',
                 color='DarkGreen', label='Run Time')
    df.plot(kind='scatter', figsize=size, x='start', y='wait',
            color='Red', label='Wait Time', ax=ax)
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
    #ax.grid(False)
    lines, labels = ax.get_legend_handles_labels()
    ax.legend(lines, labels, loc='best', fontsize=12, framealpha=0.7)
    # pad the y-axis max a bit, force y-axis min to zero (1 if log scaled)
    x1, x2, y1, y2 = ax.axis()
    ax.axis((x1, x2, y_minimum, y2 * 1.1))
    ax.figure.savefig(filepath,
                      dpi=80,
                      bbox_inches='tight',
                      pad_inches=0.2)


def create_default_statistics_plot(df, filepath, size=(8,4), days=7):
    """Create a basic job statistics plot from DataFrame."""
    min_time = int(time.time()) - 24*3600*days
    df = df[df.index > min_time]
    df.index = [convert_timestamp(ts) for ts in df.index]
    df['failure'] = df['failure'].astype('float')
    df['failure_rate'] = df['failure'] / (df['success'] + df['failure']) * 100
    fig, ax = plt.subplots() 
    ax.set_xlabel('Date')
    ax.set_ylabel('Failure Rate (%)')
    ax2 = ax.twinx()
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Wall Clock Time [seconds]')
    df.plot(kind='area', figsize=size, x=df.index, y=['failure_rate'],
            color='LightBlue', label='Date', ax=ax)
    df.plot(kind='line', figsize=size, x=df.index, y=['failure_rate'],
            color='Black', label='Date', ax=ax)
    df.plot(kind='line', figsize=size, x=df.index, y=['max_runtime'],
            color='Red', lw=2, label='Max. Run Time', ax=ax2)
    df.plot(kind='line', figsize=size, x=df.index, y=['mean_runtime'],
            color='Blue', lw=2, label='Mean Run Time', ax=ax2)
    df.plot(kind='line', figsize=size, x=df.index, y=['min_runtime'],
            color='Green', lw=2, label='Min. Run Time', ax=ax2)
    lines, labels = ax2.get_legend_handles_labels()
    lines = lines + [matplotlib.patches.Patch(color='LightBlue', ec='Black')]
    labels2 = ['Max. Runtime', 'Mean Runtime', 'Min. Runtime', 'Failure Rate']
    ax2.legend(lines, labels2, loc='best', fontsize=12, framealpha=0.7)
    ax.legend_.remove()
    tickw = int(math.ceil(days/6))
    ax.xaxis.set_major_locator(matplotlib.dates.DayLocator(interval=tickw))
    ax.xaxis.set_major_formatter(
        matplotlib.dates.DateFormatter('%b %d')
    )
    # pad the y-axis max a bit, force y-axis min to zero 
    x1, x2, y1, y2 = ax.axis()
    ax.axis((x1, x2, 0, y2 * 1.1))
    ax.grid(False)
    #ax2.grid(False)
    ax.figure.savefig(filepath,
                      dpi=80,
                      bbox_inches='tight',
                      pad_inches=0.2)
