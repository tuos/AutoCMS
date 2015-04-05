"""Collect information from and manage job log files.

The functions in this module is used to collect and save information about
submitted and completed jobs and purge old log files.
"""

import os
import re
import time

from .core import (
    JobRecord,
    load_records,
    save_records
)
from .scheduler import create_scheduler


def list_log_files(testname, config):
    """List the absolute path of log files in a given test directory.

    Any file ending in '.log' in a test directory is considered
    a log file."""
    logs = []
    testdir = os.path.join(config['AUTOCMS_BASEDIR'], testname)
    for logfile in os.listdir(testdir):
        if re.search(r'\.log$', logfile):
            logs.append(logfile)
    return [os.path.join(testdir, logfile) for logfile in logs]


def purge_old_log_files(testname, config):
    """Remove logs older than AUTOCMS_LOG_LIFETIME in the given test dir.

    Any file ending in '.log' in a test directory is considered
    a log file."""
    loglist = list_log_files(testname, config)
    purgetime = int(time.time()) - 3600*24*int(config['AUTOCMS_LOG_LIFETIME'])
    for logfile in loglist:
        if int(os.path.getmtime(logfile)) < purgetime:
            os.remove(logfile)


def append_new_stamps(stampfile, testname, config):
    """Find new submission stamp files, append the stamp, and delete."""
    stamplist = []
    testdir = os.path.join(config['AUTOCMS_BASEDIR'], testname)
    for item in os.listdir(testdir):
        if re.match(r'^stamp\.[0-9]+\.[0-9]+', item):
            stamplist.append(os.path.join(testdir, item))
    with open(stampfile, 'a') as shandle:
        for newstamp_filename in stamplist:
            with open(newstamp_filename, 'r') as nsfile:
                shandle.write(nsfile.read() + '\n')
            os.remove(newstamp_filename)


def purge_old_stamps(stampfile, config):
    """Remove old stamps from a merged stamp file."""
    purgetime = int(time.time()) - 3600*24*int(config['AUTOCMS_LOG_LIFETIME'])
    with open(stampfile) as shandle:
        stamplist = shandle.readlines()
    newstamplist = []
    for line in stamplist:
        if int(line.split()[2]) > purgetime:
            newstamplist.append(line)
    with open(stampfile, 'w') as shandle:
        for line in newstamplist:
            shandle.write(line)


def add_untracked_jobs(stampfile, records):
    """Add new jobs to a JobRecords list from stamps.

    If the stamp corresponds to a job already in the list, it is not added."""
    jobkeys = [str(job.seq) + '.' + str(job.submit_time) for job in records]
    with open(stampfile) as shandle:
        stamplist = shandle.readlines()
    for stamp in stamplist:
        stampkey = stamp.split()[0] + '.' + stamp.split()[2]
        if stampkey in jobkeys:
            continue
        else:
            records.append(JobRecord.create_from_stamp(stamp))


def purge_old_jobs(records, config):
    """Remove old jobs from a JobRecords list."""
    purgetime = int(time.time()) - 3600*24*int(config['AUTOCMS_LOG_LIFETIME'])
    for job in records[:]:
        if job.submit_time < purgetime:
            records.remove(job)


def parse_completed_job_logs(records, scheduler, testname, config):
    """Check scheduler for completed jobs, and parse logs if they exist."""
    jobids_to_check = [job.jobid for job in records if job.completed == False]
    completed_jobids = scheduler.get_completed_jobs(jobids_to_check)
    jobs_to_parse = [job for job in records if job.jobid in completed_jobids]
    for job in jobs_to_parse:
        job.completed = True
        logpath = os.path.join(config['AUTOCMS_BASEDIR'], testname,
                               job.logfile)
        if os.path.isfile(logpath):
            job.parse_output(testname, config)
        else:
            job.exit_code = 1
            job.error_string = ("ERROR standard output of this job "
                                "was not found.")
            job.start_time = job.submit_time
            job.end_time = job.submit_time

def perform_test_harvesting(testname, config):
    """Track new submitted jobs, parse logs, and purge old information."""
    records = load_records(testname, config)
    scheduler = create_scheduler(config['AUTOCMS_SCHEDULER'], config)
    stampfile = os.path.join(config['AUTOCMS_BASEDIR'],
                             testname, 'submission.stamps')
    append_new_stamps(stampfile, testname, config)
    add_untracked_jobs(stampfile, records)
    parse_completed_job_logs(records, scheduler, testname, config)
    purge_old_jobs(records, config)
    purge_old_stamps(stampfile, config)
    purge_old_log_files(testname, config)
    save_records(records, testname, config)
