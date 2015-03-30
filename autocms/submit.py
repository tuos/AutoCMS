"""Functions to submit and register new jobs."""

import sys
import os
import re
import time
import socket

from .core import JobRecord
from .scheduler import Scheduler

def submit_and_stamp(counter, testname, scheduler, config):
    """Submit a job to the scheduler and produce a newstamp file.

    This function should be run from within the test directory.
    If the submission fails an output log will be produced with the 
    standard output of the submitter.

    The name of the new stamp is returned."""
    (jobid, timestamp, returncode, output) = scheduler.submit_job(counter, 
                                                                  testname,
                                                                  config)
    newstamp = str(jobid) + ' ' + str(timestamp) + ' ' + str(returncode)
    if returncode != 0:
        logfile_name = (testname + '.submission.' + str(counter) +
                        '.' + str(timestamp) + '.log')
        newstamp += ' ' + logfile_name
        log = "Job submission failed at {0}\n".format(timestamp)
        log += "On node {0}\n".format(socket.gethostname())
        log += "Submission command output:\n\n"
        for line in output:
            log += line + '\n'
        with open(logfile_name,'w') as logfile:
            logfile.write(log)
    newstamp += "\n"
    newstamp_filename = 'newstamp.' + str(timestamp)
    with open(newstamp_filename,'w') as nsfile:
        nsfile.write(newstamp)
    return newstamp_filename
