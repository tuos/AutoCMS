"""Collect information from and manage job log files.

The functions in this module is used to collect and save information about
submitted and completed jobs and purge old log files.
"""

import os
import re
import time

from .core import JobRecord


def list_log_files(testname, config):
    """List the absolute path of log files in a given test directory.

    Any file ending in '.log' in a test directory is considered
    a log file."""
    logs = []
    testdir = os.path.join(config['AUTOCMS_BASEDIR'], testname)
    for logfile in os.listdir(testdir):
        if (re.search(r'\.log$', logfile)):
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
        if re.match(r'^stamp\.[0-9]+\.[0-9]+',item):
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
    with open(stampfile,'w') as shandle:
        for line in newstamplist:
            shandle.write(line)

def write_stamp_file(stamplist, stampfile):
    """Write a list of submission stamps to a file."""
    with open(stampfile, 'w') as handle:
        for stamp in stamplist:
            print>>handle, stamp


def parse_job_log(job, scheduler, testname, config):
    """See if job log exists and parse it, or record the missing log."""
    logfile = scheduler.jobid_logfilename(job.jobid, testname)
    if os.path.isfile(logfile):
        job.parse_output(logfile, config)
    else:
        job.exit_code = 1
        job.error_string = "ERROR standard output of this job was not found."
