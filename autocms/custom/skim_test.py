"""Custom functions for the skim_test."""

import os
import time

import matplotlib
matplotlib.use('Agg')
import pandas as pd
import matplotlib.pyplot as plt

from ..web import AutoCMSWebpage
from ..stats import load_stats
from ..plot import (
    create_run_and_waittime_plot,
    create_histogram,
    create_default_statistics_plot,
    convert_timestamp
)


def create_cmsrun_runtime_plot(joblist, filepath):
    """Create a scatterplot of runtimes with colors based on node occupancy.
   
    Plot of start times versus runtimes for listed jobs
    with the color of each point given by the number of 
    cmsRun processes the node."""
    # make sure all job records have the cmsrun_proc_count attr
    records = [job for job in joblist if hasattr(job,'cmsrun_proc_count')]
    data = [(convert_timestamp(job.start_time), job.run_time(),
             float(job.cmsrun_proc_count)) for job in records]
    df = pd.DataFrame(data, columns=['start', 'run', 'nproc'])
    ax = df.plot(kind='scatter', figsize=(10, 4), x='start', y='run',
                 c=df['nproc'], s=75, cmap=matplotlib.cm.jet,
                 vmin=0, vmax=12)
    ax.set_xlabel('Job Start Time')
    ax.set_ylabel('Wall Clock Time [seconds]')
    ax.xaxis.set_major_locator(matplotlib.dates.HourLocator(interval=4))
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%a\n%H:%M'))
    # pad the y-axis max a bit, force y-axis min to zero (1 if log scaled)
    x1, x2, y1, y2 = ax.axis()
    ax.axis((x1, x2, 0, y2 * 1.1))
    ax.figure.savefig(filepath,
                      dpi=80,
                      bbox_inches='tight',
                      pad_inches=0.2)


def produce_webpage(records, testname, config):
    """Create a webpage specific to the skim_test."""
    webpath = os.path.join(config['AUTOCMS_WEBDIR'], testname)
    recent_successes = [job for job in records
                        if job.start_time > int(time.time()) - 3600*24 and
                        job.completed and job.is_success()]
    webpage = AutoCMSWebpage(records, testname, config)
    webpage.begin_page('CMSSW Skim Test')
    webpage.add_divider()
    if len(recent_successes) > 1:
        runtime_plot_path = os.path.join(webpath, 'runtime.png')
        plot_desc = ('Successful job running and waiting times '
                     '(last 24 hours):')
        create_run_and_waittime_plot(recent_successes, (10, 4),
                                     runtime_plot_path)
        webpage.add_floating_image(48, 'runtime.png', plot_desc)
        runtime_plot_path = os.path.join(webpath, 'runtimelog.png')
        plot_desc = ('Successful job running and waiting times '
                     '(last 24 hours, log scaled):')
        create_run_and_waittime_plot(recent_successes, (10, 4),
                                     runtime_plot_path, logscale=True)
        webpage.add_floating_image(48, 'runtimelog.png', plot_desc)
    webpage.add_divider()
    df = load_stats(testname, config)
    if not df.empty:
        webpage.copy_statistics_csv_file()
        stat_plot_path = os.path.join(webpath, 'stats.png')
        create_default_statistics_plot(df, stat_plot_path, size=(10, 4))
        plot_desc = 'Recent job statistics:'
        plot_caption = ('Full test statistics <a href="statistics.csv">'
                        'CSV file</a>.')
        webpage.add_floating_image(48, 'stats.png', plot_desc, 
                                   caption=plot_caption)
    if len(recent_successes) > 1:
        cmsrun_plot_path = os.path.join(webpath, 'cmsrun.png')
        create_cmsrun_runtime_plot(recent_successes, cmsrun_plot_path)
        plot_desc = 'Running Times by Number of cmsRun Processes on the Node:'
        webpage.add_floating_image(48, 'cmsrun.png', plot_desc)
    webpage.add_divider()
    webpage.add_test_description(100)
    webpage.add_divider()
    webpage.add_job_failure_rates(30, [24, 3], 90.0)
    webpage.add_failures_by_node(25, 24)
    webpage.add_failures_by_reason(40, 24)
    webpage.add_divider()
    webpage.add_failed_job_listing(24,input_file='Input File')
    long_running_jobs = [job for job in recent_successes if
                         job.run_time() >
                         int(config['SKIMTEST_RUNTIME_WARNING'])]
    if long_running_jobs:
       webpage.add_job_listing(long_running_jobs,
                               'Long running jobs from the last 24 hours:',
                               'Warning', input_file='Input File') 
    if config['AUTOCMS_PRINT_SUCCESS'] == 'TRUE':
        webpage.add_job_listing(recent_successes,
                                'Successful jobs in the last 24 hours:',
                                'Success', input_file='Input File')
    webpage.end_page()
    webpage.write_page()
