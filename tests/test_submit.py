"""Test job submission compnents using local scheduler."""

import os
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
        self.config = load_configuration('autocms.cfg')
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
        record = self.scheduler.submit_job(1, 'uscratch')
        time.sleep(3)
        logpath = os.path.join(self.config['AUTOCMS_BASEDIR'],
                               'uscratch',
                               record.logfile)
        self.assertTrue(os.path.isfile(logpath))
        self.assertIn(record.jobid,
                      self.scheduler.get_completed_jobs([record.jobid]))
        record.parse_output('uscratch', self.config)
        self.assertTrue(record.is_success())
        self.assertEqual(int(record.seq), 1)


    def test_submit_and_stamp(self):
        """Test that proper stamp file is created on submission."""
        stamp_path = submit_and_stamp(2,
                                      'uscratch',
                                      self.scheduler,
                                      self.config)
        self.assertTrue(os.path.isfile(stamp_path))
        with open(stamp_path) as stampfile:
            stamp = stampfile.read()
        record = JobRecord.create_from_stamp(stamp)
        self.assertEqual(int(record.seq), 2)
        self.assertEqual(record.logfile,
                         stamp.split()[4])
        time.sleep(3)
        record.parse_output('uscratch', self.config)
        self.assertTrue(record.is_success())

    def test_job_counter(self):
        """Test setting and retrieving the counter from file."""
        set_job_counter(42, 'uscratch', self.config)
        count = get_job_counter('uscratch', self.config)
        self.assertEqual(count, 42)
