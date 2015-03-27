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

The slurm scheduler is queried for jobs that have completed in the last
24-48 hours. For completed jobs not already marked by a previous pass of the
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
import cPickle as pickle

from JobRecord import JobRecord
import AutoCMSUtil


def list_log_files():
    """List the log files in the current directory."""
    logs = list()
    for file in os.listdir('.'):
        if (re.search(r'.slurm.o[0-9]+', file) or
                re.search(r'.submission.[0-9]+.[0-9]+.log', file)):
            logs += file
    return logs


def get_records():
    """Get the JobRecord dictionary from the pickle or make a new one."""
    autocms_pkl = 'records.pickle'
    if os.path.isfile(autocms_pkl):
        records = pickle.load(open(autocms_pkl, "rb"))
    else:
        records = dict()
    return records


def save_records(records):
    """Write the JobRecord dictionary to the pickle."""
    autocms_pkl = 'records.pickle'
    pickle.dump( records, open(autocms_pkl, "wb"))


def register_new_stamps():
    """Find new submission stamp files, append the stamp, and delete."""
    newstamp_files = [file for file in os.listdir('.')
                      if re.match(r'newstamp', file)]
    with open('submission.stamps','a') as stamp_file:
        for newstamp_filename in newstamp_files:
            with open(newstamp_filename,'r') as newstamp_file:
                newstamp = newstamp_file.read().strip()
            print>>stamp_file, newstamp
            os.remove(newstamp_filename)


def create_records_from_stamps(records,stamplist):
    """Create new job records from submission stamps."""
    for line in stamplist:
	# for some reason slurm is not always reporting a job number, 
	# so skip lines  that have less than three columns 
	# (i.e. no job number, timestamp, or exit code)
	if len(line.split()) > 2 :
	    jobid = line.split()[0].replace('.vmpsched','')
	    timestamp = int(line.split()[1])
	    submitStatus = line.split()[2]
	    if timestamp not in records:
		records[timestamp] = JobRecord(timestamp,
					       jobid,
					       submitStatus)
                # add submission log for failed submissions
		if int(submitStatus) != 0 and len(line.split()) > 3:
		    records[timestamp].logFile = line.split()[3]


def purge_old_stamps(stamplist,purgetime):
    """Remove old stamps from the list"""
    for line in stamplist[:]:
        if len(line.split()) > 1:
            timestamp = int(line.split()[1])
            if timestamp < purgetime:
                stamplist.remove(line)


def write_stamp_file(stamplist,stampfile):
    """Write a list of submission stamps to a file."""
    with open(stampfile,'w') as file:
        for stamp in stamplist:
            print>>file, stamp


def parse_job_log(job,config):
    """See if job log exists and parse it, or record the missing log."""
    logfile = (config['AUTOCMS_TEST_NAME'] + '.slurm.o' + str(job.jobid))
    if os.path.isfile(logfile):
        job.parseOutput(logfile,config)
    else:
        job.exitCode = 1
        job.errorString = "ERROR standard output of this job was not found."


def run_harvest():
    """Perform log harvesting and old log cleanup."""

    # Basic setup: load configuration, determine test,
    # enter test directory, load records
    config = AutoCMSUtil.LoadConfiguration('autocms.cfg')
    config['AUTOCMS_TEST_NAME'] = sys.argv[1]
    testdir = os.path.join(config['AUTOCMS_BASEDIR'],
                           config['AUTOCMS_TEST_NAME'])
    os.chdir(testdir)
    records = get_records()

    # time to purge old stamps and logs, default to a week ago
    now = int(time.time())
    if int(config['AUTOCMS_LOG_LIFETIME']) > 0:
        purgetime = now - 3600 * 24 * int(config['AUTOCMS_LOG_LIFETIME'])
    else:
        purgetime = now - 3600 * 24 * 7

    # collect new stamps to the stampfile, create new records
    # from new stamps, get rid of old stamps, and write new stamp file
    register_new_stamps()
    with open('submission.stamps', 'r') as stamp_file:
        stamps = stamp_file.read().splitlines()
        create_records_from_stamps(records,stamps)
        purge_old_stamps(stamps,purgetime)
    write_stamp_file(stamps,'submission.stamps')

    # get a list of jobs completed in the
    # last 24-48 hours from this account, 
    # then updated jobs not completed, and attempt to
    # parse their logs if they exist
    completedJobs = AutoCMSUtil.getCompletedJobs(config)
    for job in records:
        if (records[job].jobid in completedJobs 
                and not records[job].isCompleted):
            records[job].isCompleted = True
            parse_job_log(records[job],config)

    # Remove old log files and job records
    logfile_list = [ x for x in os.listdir('.') if
                         re.search(r'.slurm.o[0-9]+', x) or
                         re.search(r'.submission.[0-9]+.[0-9]+.log', x)]
    for logfile_name in logfile_list:
        if int(os.path.getctime(logfile_name)) < purgetime :
            os.remove(logfile_name)
    
    old_records = [job for job in records.keys() if job < purgetime]
    for job in old_records:
        del records[job]

    save_records(records)


def main():
    run_harvest()


if __name__ == '__main__':
    status = main()
    sys.exit(status)
