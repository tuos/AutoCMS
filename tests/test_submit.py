"""Test job submission compnents using local scheduler."""

import os
import re
import shutil
import unittest
import time

from autocms.core import (
    load_configuration,
    JobRecord
)
from autocms.scheduler import create_scheduler
from autocms.submit import (
    submit_and_stamp,
    get_job_counter,
    set_job_counter
)


class TestSubmission(unittest.TestCase):
    """Test that submission results in valid stamp and log.

    Note that the local scheduler is used for all unit tests."""

    def setUp(self):
        self.config = load_configuration('autocms.cfg.example')
        self.scheduler = create_scheduler('local', self.config)
        basedir = self.config['AUTOCMS_BASEDIR']
        # call the scratch directory 'uscratch' instead of 'scratch'
        # so that in pathological cases one does not resolve to
        # /scratch which is often used.
        os.makedirs(os.path.join(basedir, 'uscratch'))
        src_testscript = os.path.join(basedir, 'tests/data/testscript.local')
        dst_testscript = os.path.join(basedir, 'uscratch/uscratch.local')
        shutil.copyfile(src_testscript, dst_testscript)

    def tearDown(self):
        shutil.rmtree(os.path.join(self.config['AUTOCMS_BASEDIR'],
                                   'uscratch'))

    def test_basic_job_submission(self):
        """Test if jobs are properly submitted with a valid record and log."""
        record = self.scheduler.submit_job(1,'uscratch')
        time.sleep(3)
        logpath = os.path.join(self.config['AUTOCMS_BASEDIR'],
                               'uscratch',
                               record.logfile)
        self.assertTrue(os.path.isfile(logpath))
        self.assertIn(record.jobid,
                      self.scheduler.get_completed_jobs([record.jobid]))
        record.parse_output('uscratch', self.config)
        self.assertTrue(record.is_success())
        self.assertEqual(int(record.seq),1)


#    def test_job_counter(self):
#        os.chdir(self.basepath)
#        os.chdir('tests/scratch/localsub')
#        set_job_counter(42)
#        count = get_job_counter()
#        self.assertEqual(count, 42)
