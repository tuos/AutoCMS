"""Test the AutoCMS log harvesting functionality."""

import os
import shutil
import unittest
import time

from autocms.core import (
    JobRecord,
    load_configuration
)
from autocms.harvest import (
    list_log_files,
    purge_old_log_files,
    register_new_stamps,
    create_records_from_stamps,
    write_stamp_file,
    parse_job_log,
    purge_old_stamps
)
from autocms.scheduler import Scheduler


class TestLogFiles(unittest.TestCase):
    """Test the maintenance of log files."""

    def setUp(self):
        self.config = load_configuration('autocms.cfg.example')
        # call the scratch directory 'uscratch' instead of 'scratch'
        # so that in pathological cases one does not resolve to
        # /scratch which is often used.
        self.testdir = os.path.join(self.config['AUTOCMS_BASEDIR'],
                                    'uscratch')
        os.makedirs(self.testdir)
        # make a few dummy log files and backdate their modification time
        for count in range(0, 10):
            mtime = int(time.time()) - 3600*24*count
            logfile = os.path.join(self.testdir,
                                   'test_' + str(count) + '.log')
            with open(logfile, 'w') as log:
                log.write('test log '+str(count))
            os.utime(logfile, (mtime, mtime))

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

if __name__ == '__main__':
    unittest.main()
