"""Functions to submit and register new jobs."""

import os


def submit_and_stamp(counter, testname, scheduler, config):
    """Submit a job to the scheduler and produce a newstamp file.

    The full path of the newstamp file is returned."""
    result = scheduler.submit_job(counter, testname, config)
    stamp_filename = ('stamp.' +
                      str(result.submit_time) +
                      str(counter))
    stamp_path = os.path.join(config['AUTOCMS_BASEDIR'],
                              testname,
                              stamp_filename)
    with open(stamp_path, 'w') as stampfile:
        stampfile.write(result.stamp())
    return stamp_path


def get_job_counter(testname, config):
    """Return an integer for the counter to pass to the next job."""
    counter_path = os.path.join(config['AUTOCMS_BASEDIR'],
                                testname,
                                'counter')
    if os.path.exists(counter_path):
        with open(counter_path) as handle:
            count = handle.read()
    else:
        count = 1
    return int(count)


def set_job_counter(count, testname, config):
    """Write the job counter to file."""
    counter_path = os.path.join(config['AUTOCMS_BASEDIR'],
                                testname,
                                'counter')
    with open(counter_path, 'w') as handle:
        handle.write(str(count))
