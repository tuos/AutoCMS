"""Custom functions for the example_test."""

import os
import time

from ..web import AutoCMSWebpage
from ..plot import (create_run_and_waittime_plot, create_histogram)


def produce_webpage(records, testname, config):
    """Create a webpage specific to the example_test."""
    webpath = os.path.join(config['AUTOCMS_WEBDIR'], testname)
    runtime_plot_path = os.path.join(webpath, 'runtime.png')
    dice_plot_path = os.path.join(webpath, 'dice.png')
    proc_plot_path = os.path.join(webpath, 'proc.png')
    recent_successes = [job for job in records
                        if job.start_time > int(time.time()) - 3600*24 and
                        job.completed and job.is_success()]
    webpage = AutoCMSWebpage(records, testname, config)
    webpage.begin_page('AutoCMS Example Test')
    webpage.add_divider()
    webpage.add_test_description(50)
    if len(recent_successes) > 1:
        plot_desc = ('Successful job running and waiting times '
                     '(last 24 hours):')
        create_run_and_waittime_plot(recent_successes, (8,4), 
                                     runtime_plot_path)
        webpage.add_floating_image(45, 'runtime.png', plot_desc)
    webpage.add_divider()
    if len(recent_successes) > 1:
        create_histogram('dice_sum', recent_successes, 'Sum of the Dice',
                         (5, 3), dice_plot_path)
        webpage.add_floating_image(30, 'dice.png',
                                   'Dice Rolls (last 24 hours):')
        create_histogram('num_proc', recent_successes, 
                         'Processes on the Node',
                         (5, 3), proc_plot_path)
        webpage.add_floating_image(30, 'proc.png',
                                   'Processes on the Node (last 24 hours):')
    webpage.add_divider()
    webpage.add_job_failure_rates(30, [24, 3], 90.0)
    webpage.add_failures_by_node(25, 24)
    webpage.add_failures_by_reason(40, 24)
    webpage.add_divider()
    webpage.add_failed_job_listing(24)
    webpage.end_page()
    webpage.write_page()
