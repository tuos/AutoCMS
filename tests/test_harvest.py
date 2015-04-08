"""Test the AutoCMS log harvesting functionality."""

import os
import shutil
import unittest
import time
import re

from autocms.core import load_configuration
from autocms.harvest import (
    list_log_files,
    purge_old_log_files,
    append_new_stamps,
    purge_old_stamps,
    add_untracked_jobs,
    purge_old_jobs,
    parse_completed_job_logs
)
from autocms.scheduler import create_scheduler
from autocms.submit import submit_and_stamp

class TestRecordAndLogMaintenance(unittest.TestCase):
    """Test the maintenance of log files, stamps, and records"""

    def setUp(self):
        self.config = load_configuration('autocms.cfg')
        # call the scratch directory 'uscratch' instead of 'scratch'
        # so that in pathological cases one does not resolve to
        # /scratch which is often used.
        self.testdir = os.path.join(self.config['AUTOCMS_BASEDIR'],
                                    'uscratch')
        os.makedirs(self.testdir)
        # make a few dummy log files and backdate their modification time
        # also produce some dummy stamp files
        for count in range(0, 10):
            mtime = int(time.time()) - 3600*24*count
            logfile = os.path.join(self.testdir,
                                   'test_' + str(count) + '.log')
            with open(logfile, 'w') as log:
                log.write('test log ' + str(count))
            os.utime(logfile, (mtime, mtime))
            stamp = (str(count) + ' ' + str(count*100) + ' ' +
                     str(mtime) + ' ' + '0 ' + 'test_' + str(count) + '.log')
            stampfile = os.path.join(self.testdir,
                                     'stamp.' + str(mtime) + '.' + str(count))
            with open(stampfile, 'w') as shandle:
                shandle.write(stamp)

    def tearDown(self):
        shutil.rmtree(os.path.join(self.config['AUTOCMS_BASEDIR'],
                                   'uscratch'))

    def test_list_log_files(self):
        """Test listing of log files in a test directory."""
        logs = list_log_files('uscratch', self.config)
        self.assertEqual(len(logs), 10)
        self.assertIn(os.path.join(self.testdir, 'test_0.log'), logs)
        self.assertIn(os.path.join(self.testdir, 'test_9.log'), logs)

    def test_purge_log_files(self):
        """Test removal of old log files."""
        time.sleep(2)
        log_lifetime = int(self.config['AUTOCMS_LOG_LIFETIME'])
        purge_old_log_files('uscratch', self.config)
        logs = list_log_files('uscratch', self.config)
        self.assertEqual(len(logs), log_lifetime)

    def test_append_new_stamps(self):
        """Test adding new stamps to combined file."""
        stampfile = os.path.join(self.testdir, 'stest')
        stamps_to_be_removed = []
        for item in os.listdir(self.testdir):
            if re.match(r'stamp', item):
                stamps_to_be_removed.append(os.path.join(self.testdir, item))
        append_new_stamps(stampfile, 'uscratch', self.config)
        for stamp in stamps_to_be_removed:
            self.assertFalse(os.path.exists(stamp))
        with open(stampfile) as shandle:
            recorded_stamps = shandle.read().splitlines()
        self.assertEqual(len(recorded_stamps), 10)

    def test_purge_old_stamps(self):
        """Test removal of old stamps."""
        time.sleep(2)
        log_lifetime = int(self.config['AUTOCMS_LOG_LIFETIME'])
        stampfile = os.path.join(self.testdir, 'stest2')
        append_new_stamps(stampfile, 'uscratch', self.config)
        purge_old_stamps(stampfile, self.config)
        with open(stampfile) as shandle:
            recorded_stamps = shandle.read().splitlines()
        self.assertEqual(len(recorded_stamps), log_lifetime)

    def test_add_untracked_jobs(self):
        """Test adding new jobs to a JobRecord list from stamps."""
        stampfile = os.path.join(self.testdir, 'stest3')
        append_new_stamps(stampfile, 'uscratch', self.config)
        records = []
        add_untracked_jobs(stampfile, records)
        self.assertEqual(len(records), 10)
        # make a few more stamps and add them
        with open(stampfile, 'a') as sfile:
            mtime = int(time.time())
            for count in range(0, 4):
                stamp = (str(count + 200) + ' ' + str(count*100 + 5) +
                         ' ' + str(mtime) + ' ' + '0 ' +
                         'test_a_' + str(count) + '.log\n')
                sfile.write(stamp)
        add_untracked_jobs(stampfile, records)
        self.assertEqual(len(records), 14)

    def test_purge_old_jobs(self):
        """Test purging old jobs from a JobRecords list."""
        time.sleep(2)
        log_lifetime = int(self.config['AUTOCMS_LOG_LIFETIME'])
        stampfile = os.path.join(self.testdir, 'stest4')
        append_new_stamps(stampfile, 'uscratch', self.config)
        records = []
        add_untracked_jobs(stampfile, records)
        purge_old_jobs(records, self.config)
        self.assertEqual(len(records), log_lifetime)

class TestRecordHarvesting(unittest.TestCase):
    """Comprehensive test submitting and then parsing jobs."""

    def setUp(self):
        self.config = load_configuration('autocms.cfg')
        self.config['AUTOCMS_SCHEDULER'] = 'local'
        # call the scratch directory 'uscratch' instead of 'scratch'
        # so that in pathological cases one does not resolve to
        # /scratch which is often used.
        self.testdir = os.path.join(self.config['AUTOCMS_BASEDIR'],
                                    'uscratch')
        os.makedirs(self.testdir)
        src_testscript = os.path.join(self.config['AUTOCMS_BASEDIR'],
                                      'tests/data/testscript.local')
        dst_testscript = os.path.join(self.config['AUTOCMS_BASEDIR'],
                                      'uscratch/uscratch.local')
        shutil.copyfile(src_testscript, dst_testscript)
        self.scheduler = create_scheduler('local', self.config)
        for count in range(0, 4):
            submit_and_stamp(count, 'uscratch', self.scheduler, self.config)

    def tearDown(self):
        shutil.rmtree(os.path.join(self.config['AUTOCMS_BASEDIR'],
                                   'uscratch'))

    def test_parse_completed_job_logs(self):
        """Full test of log file parsing starting from local submission."""
        time.sleep(2)
        stampfile = os.path.join(self.testdir, 'stest')
        append_new_stamps(stampfile, 'uscratch', self.config)
        records = []
        add_untracked_jobs(stampfile, records)
        parse_completed_job_logs(records, self.scheduler,
                                 'uscratch', self.config)
        self.assertEqual(len(records), 4)
        for job in records:
            self.assertEqual(int(job.exit_code), 0)
            self.assertTrue(job.completed)


if __name__ == '__main__':
    unittest.main()
