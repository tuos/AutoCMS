"""Test the AutoCMS log harvesting functionality."""

import os
import shutil
import unittest
import time
import re

from autocms.core import (
    JobRecord,
    load_configuration
)
from autocms.harvest import (
    list_log_files,
    purge_old_log_files,
    append_new_stamps,
    purge_old_stamps,
    add_untracked_jobs
)
from autocms.scheduler import Scheduler


class TestRecordAndLogMaintenance(unittest.TestCase):
    """Test the maintenance of log files, stamps, and records"""

    def setUp(self):
        self.config = load_configuration('autocms.cfg.example')
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
        logs = list_log_files('uscratch', self.config)
        self.assertEqual(len(logs), 10)
        self.assertIn(os.path.join(self.testdir, 'test_0.log'), logs)
        self.assertIn(os.path.join(self.testdir, 'test_9.log'), logs)

    def test_purge_log_files(self):
        time.sleep(2)
        log_lifetime = int(self.config['AUTOCMS_LOG_LIFETIME'])
        purge_old_log_files('uscratch', self.config)
        logs = list_log_files('uscratch', self.config)
        self.assertEqual(len(logs), log_lifetime)

    def test_append_new_stamps(self):
        stampfile = os.path.join(self.testdir, 'stest')
        stamps_to_be_removed = []
        for item in os.listdir(self.testdir):
            if re.match(r'stamp',item):
               stamps_to_be_removed.append(os.path.join(self.testdir, item))
        append_new_stamps(stampfile, 'uscratch', self.config)
        for stamp in stamps_to_be_removed:
            self.assertFalse(os.path.exists(stamp))
        with open(stampfile) as shandle:
            recorded_stamps = shandle.read().splitlines()
        self.assertEqual(len(recorded_stamps),10)

    def test_purge_old_stamps(self):
        time.sleep(2)
        log_lifetime = int(self.config['AUTOCMS_LOG_LIFETIME'])
        stampfile = os.path.join(self.testdir, 'stest2')
        append_new_stamps(stampfile, 'uscratch', self.config)
        purge_old_stamps(stampfile, self.config)
        with open(stampfile) as shandle:
            recorded_stamps = shandle.read().splitlines()
        self.assertEqual(len(recorded_stamps),log_lifetime)

    def test_add_untracked_jobs(self):
        stampfile = os.path.join(self.testdir, 'stest3')
        append_new_stamps(stampfile, 'uscratch', self.config)
        records = []
        add_untracked_jobs(stampfile, records)
        self.assertEqual(len(records), 10)
        # make a few more stamps and add them
        with open(stampfile,'a') as sfile:
            mtime = int(time.time())
            for count in range(0,4):
                stamp = (str(count + 200) + ' ' + str(count*100 + 5) +
                         ' ' + str(mtime) + ' ' + '0 ' +
                         'test_a_' + str(count) + '.log\n')
                sfile.write(stamp)
        add_untracked_jobs(stampfile, records)
        self.assertEqual(len(records), 14)


if __name__ == '__main__':
    unittest.main()
