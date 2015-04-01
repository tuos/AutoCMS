"""Collect information from and manage job log files.

This module is used to collect and save information about submitted and
completed jobs and purge old log files.

The intended usage pattern is to be called from the autocms.sh script
which is invoked through cron at regular intervals, but it may also be
invoked on the command line as

python logharvester.py test_name

where test_name is the name of a specific AutoCMS test to be harvested.

The module first looks for "newstamp" files produced by the AutoCMS
submitted which  encode the submission timestamp, exit code of the
sbatch command, and slurm jobid as applicable. This information is copied
to the "submission.stamps" file, and old entries are removed.

The JobRecord dictionary is loaded from a pickle file, and new records
are created for any job submitted that does not already have a record. The
records of old jobs are purged.

The scheduler is queried for jobs that have completed (for the 
slurm scheduler, in the last 24-48 hours). 
For completed jobs not already marked by a previous pass of the
logharvester, the standard output log of the job is parsed, unless this
output does not exist, in which case the job is marked as a failure with
the lack of an output log noted.

Old standard output log files are removed, and the updated dictionary
of records is saved to the pickle file for the specified test.

The number of days that must have elapsed before old job records,
stamps, and logs are removed is controlled by the AUTOCMS_LOG_LIFETIME
variable in autocms.cfg.

Note: the JobRecord dictionary is currently keyed by the submission
timestamp of the job, but in the future this may be changed to allow for
multiple job submissions in a single call to the submitter with unique ids.
"""

import sys
import os
import re
import time

from autocms.core import (
    JobRecord,
    load_configuration,
    load_records,
    save_records
)
from autocms.harvest import (
    list_log_files,
    register_new_stamps,
    create_records_from_stamps,
    purge_old_stamps,
    write_stamp_file,
    parse_job_log
)
from autocms.scheduler import Scheduler


def run_harvest():
    """Perform log harvesting and old log cleanup."""

    # Basic setup: load configuration, determine test,
    # enter test directory, load records, list directory contents,
    # instantiate scheduler
    config = load_configuration('autocms.cfg')
    testname = sys.argv[1]
    testdir = os.path.join(config['AUTOCMS_BASEDIR'], testname)
    os.chdir(testdir)
    records = load_records('records.pickle')
    ls_result = os.listdir('.')
    scheduler = Scheduler.factory(config['AUTOCMS_SCHEDULER'])

    # time to purge old stamps and logs, default to a week ago
    now = int(time.time())
    if int(config['AUTOCMS_LOG_LIFETIME']) > 0:
        purgetime = now - 3600*24*int(config['AUTOCMS_LOG_LIFETIME'])
    else:
        purgetime = now - 3600*24*7

    # collect new stamps to the stampfile, create new records
    # from new stamps, get rid of old stamps, and write new stamp file
    stamp_filename = 'submission.stamps'
    register_new_stamps(ls_result, stamp_filename)
    with open(stamp_filename, 'r') as stamp_file:
        stamps = stamp_file.read().splitlines()
        create_records_from_stamps(records, stamps)
        purge_old_stamps(stamps, purgetime)
    write_stamp_file(stamps, stamp_filename)

    # get a list of jobs completed in the
    # last 24-48 hours from this account,
    # then updated jobs not completed, and attempt to
    # parse their logs if they exist
    jobids_to_check = [records[job].jobid for job in records.viewkeys() if
                               not records[job].completed]
    jobids_to_parse =  scheduler.get_completed_jobs(jobids_to_check, config)
    for job in records.viewkeys():
        if records[job].jobid in jobids_to_parse:
            parse_job_log(records[job], scheduler, testname, config)
            records[job].completed = True

    # Remove old log files and job records
    for logfile_name in list_log_files(ls_result, scheduler):
        if int(os.path.getctime(logfile_name)) < purgetime:
            os.remove(logfile_name)
    old_records = [job for job in records.keys() if job < purgetime]
    for job in old_records:
        del records[job]

    save_records(records,'records.pickle')


def main():
    run_harvest()


if __name__ == '__main__':
    status = main()
    sys.exit(status)
