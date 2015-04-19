"""Harvesting of persistent statsitical records."""

import os
import time
import importlib

from .core import load_records


def harvest_default_stats(records, config):
    """Add a row to the long term statistics record for a given test."""
    now = int(time.time())
    harvest_time = now - int(config['AUTOCMS_STAT_INTERVAL'])*3600
    stat_records = [job for job in records if job.completed and
                    job.end_time > harvest_time]
    runtimes = [job.run_time() for job in stat_records if job.is_success()]
    if len(runtimes) == 0:
        max_runtime = 0
        min_runtime = 0
        mean_runtime = 0
    else:
        max_runtime = max(runtimes)
        min_runtime = min(runtimes)
        mean_runtime = sum(runtimes)/float(len(runtimes))
    successes = sum(1 for job in stat_records if job.is_success())
    failures = sum(1 for job in stat_records if not job.is_success())
    return "{} {} {} {} {} {}".format(now, successes, failures, min_runtime,
                                      mean_runtime, max_runtime)


def append_stats_row(row, testname, config):
    """Add a line to the persistent statistics log of a test."""
    statfile = os.path.join(config['AUTOCMS_BASEDIR'], testname,
                            'statistics.dat')
    with open(statfile, 'a') as stat_handle:
        stat_handle.write(row + '\n')


def perform_stats_harvesting(testname, config):
    """Analyze job records for given test and create row of statistics."""
    records = load_records(testname, config)
    # use a custom row if the test has configured one
    harvest_stats = harvest_default_stats
    try:
        test_custom = importlib.import_module('autocms.custom.' + testname)
        if hasattr(test_custom, 'harvest_stats'):
            harvest_stats = getattr(test_custom, 'produce_webpage')
    except ImportError:
        pass
    row = harvest_stats(records, config)
    append_stats_row(row, testname, config)
