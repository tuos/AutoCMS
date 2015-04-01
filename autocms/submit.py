"""Functions to submit and register new jobs."""

import os
import socket


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
        with open(logfile_name, 'w') as logfile:
            logfile.write(log)
    newstamp += "\n"
    newstamp_filename = 'newstamp.' + str(timestamp)
    with open(newstamp_filename, 'w') as nsfile:
        nsfile.write(newstamp)
    return newstamp_filename


def get_job_counter():
    """Return an integer for the counter to pass to the next job.

    This should be called from within the test directory."""
    if os.path.exists('counter'):
        with open('counter') as handle:
            count = handle.read()
    else:
        count = 1
    return int(count)


def set_job_counter(count):
    """Write the job counter to file.

    This should be called from within the test directory."""
    with open('counter', 'w') as handle:
        handle.write(str(count))
