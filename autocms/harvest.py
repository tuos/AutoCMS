"""Collect information from and manage job log files.

The functions in this module is used to collect and save information about 
submitted and completed jobs and purge old log files.
"""

import sys
import os
import re
import time
import cPickle as pickle

from .core import JobRecord
from .scheduler import Scheduler


def list_log_files(ls_result,scheduler,config):
    """List files in given ls result that are log files.

    Any file matching a regular expression corresponding to the 
    scheduler or produced by the submission script is assumed to be the 
    output log of a submitted job"""
    logs = list()
    for file in ls_result:
        if (re.search(scheduler.logfile_regexp(), file) or
                re.search(r'.submission.[0-9]+.[0-9]+.log', file)):
            logs.append(file)
    return logs


def register_new_stamps(ls_result,stamp_filename):
    """Find new submission stamp files, append the stamp, and delete.

    The working directory of the script should be that of the stamps."""
    newstamp_list = (nsf for nsf in ls_result
                        if re.match(r'newstamp', nsf))
    with open(stamp_filename, 'a') as sfile:
        for newstamp_filename in newstamp_list:
            with open(newstamp_filename, 'r') as nsfile:
                newstamp = nsfile.read().strip()
            print>>sfile, newstamp
            os.remove(newstamp_filename)


def create_records_from_stamps(records, stamplist):
    """Create new job records from submission stamps."""
    for line in stamplist:
        # so skip lines  that have less than three columns
        # (i.e. no job number, timestamp, or exit code)
        if len(line.split()) > 2:
            jobid = line.split()[0]
            timestamp = int(line.split()[1])
            submit_status = line.split()[2]
            if timestamp not in records:
                records[timestamp] = JobRecord(timestamp,
                                               jobid,
                                               submit_status)
                # add submission log for failed submissions
                if int(submit_status) != 0 and len(line.split()) > 3:
                    records[timestamp].logfile = line.split()[3]


def purge_old_stamps(stamplist, purgetime):
    """Remove old stamps from the list, return truncated list"""
    newstamplist = []
    for line in stamplist:
        if len(line.split()) > 1:
            timestamp = int(line.split()[1])
            if timestamp >= purgetime:
                newstamplist.append(line)
    return newstamplist


def write_stamp_file(stamplist, stampfile):
    """Write a list of submission stamps to a file."""
    with open(stampfile, 'w') as file:
        for stamp in stamplist:
            print>>file, stamp


def parse_job_log(job, scheduler, config):
    """See if job log exists and parse it, or record the missing log."""
    logfile = scheduler.jobid_logfilename(job.jobid,
                                          config['AUTOCMS_TEST_NAME'])
    if os.path.isfile(logfile):
        job.parse_output(logfile, config)
    else:
        job.exit_code = 1
        job.error_string = "ERROR standard output of this job was not found."
