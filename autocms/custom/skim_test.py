"""Custom functions for the example_test."""

import os
import time

from ..web import AutoCMSWebpage
from ..plot import (create_run_and_waittime_plot, create_histogram)


def produce_webpage(records, testname, config):
    """Create a webpage specific to the example_test."""
    webpath = os.path.join(config['AUTOCMS_WEBDIR'], testname)
    dice_plot_path = os.path.join(webpath, 'dice.png')
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
        create_run_and_waittime_plot(recent_successes, (8,4), 
                                     runtime_plot_path)
        webpage.add_floating_image(45, 'runtime.png', plot_desc)
        runtime_plot_path = os.path.join(webpath, 'runtimelog.png')
        plot_desc = ('Successful job running and waiting times '
                     '(last 24 hours, log scaled):')
        create_run_and_waittime_plot(recent_successes, (8,4), 
                                     runtime_plot_path, logscale=True)
        webpage.add_floating_image(45, 'runtimelog.png', plot_desc)
    webpage.add_divider()
    webpage.add_test_description(100)
    webpage.add_divider()
    webpage.add_job_failure_rates(30, [24, 3], 90.0)
    webpage.add_failures_by_node(25, 24)
    webpage.add_failures_by_reason(40, 24)
    webpage.add_divider()
    webpage.add_failed_job_listing(24)
    webpage.end_page()
    webpage.write_page()
