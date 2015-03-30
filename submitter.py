"""Submit and register a test job."""

import sys
import os

from autocms.core import (
    JobRecord,
    load_configuration
)
from autocms.submit import (
    submit_and_stamp,
    get_job_counter,
    set_job_counter
)
from autocms.scheduler import Scheduler


def run_submit():
    """Submit a job, increment counter"""

    # Basic setup: load configuration, determine test,
    # enter test directory, get counter, instantiate scheduler
    config = load_configuration('autocms.cfg')
    testname = sys.argv[1]
    testdir = os.path.join(config['AUTOCMS_BASEDIR'], testname)
    os.chdir(testdir)
    counter = get_job_counter()
    scheduler = Scheduler.factory(config['AUTOCMS_SCHEDULER'])

    # Ensure that we don't have too many jobs already waiting
    # in the queue before submitting another
    jobcount = scheduler.enqueued_job_count(config) 
    if jobcount >= int(config['AUTOCMS_MAXENQUEUE']):
        return

    # Submit new job, increment counter
    submit_and_stamp(counter, testname, scheduler, config)
    counter += 1
    set_job_counter(counter)


def main():
    run_submit()


if __name__ == '__main__':
    status = main()
    sys.exit(status)
