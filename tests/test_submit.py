"""Test job submission compnents."""

import os
import re
import shutil
import unittest
import time

from autocms.core import load_configuration
from autocms.scheduler import Scheduler
from autocms.submit import (
    submit_and_stamp,
    get_job_counter,
    set_job_counter
)


class TestSubmission(unittest.TestCase):
    """Test that submission results in valid stamp and log."""

    def setUp(self):
        self.basepath = os.getcwd()
        self.config = load_configuration('tests/data/autocms.cfg.unittest')
        self.scheduler = Scheduler.factory('local')
        os.makedirs('tests/scratch/localsub')
        shutil.copyfile("tests/data/unit_test.local",
                        "tests/scratch/localsub/unit_test.local")

    def tearDown(self):
        os.chdir(self.basepath)
        shutil.rmtree('tests/scratch/localsub')

    def test_stamp_creation(self):
        os.chdir(self.basepath)
        os.chdir('tests/scratch/localsub')
        stampfile = submit_and_stamp(2,
                                     'unit_test',
                                     self.scheduler,
                                     self.config)
        time.sleep(3)
        self.assertTrue(os.path.isfile(stampfile))
        with open(stampfile) as nsfile:
            newstamp_raw = nsfile.read().splitlines()
        self.assertEqual(len(newstamp_raw), 1)
        newstamp = newstamp_raw[0].strip()
        self.assertEqual(newstamp.split()[2],'0')

    def test_job_submit_success(self):
        os.chdir(self.basepath)
        os.chdir('tests/scratch/localsub')
        stampfile = submit_and_stamp(5,
                                     'unit_test',
                                     self.scheduler,
                                     self.config)
        time.sleep(3)
        with open(stampfile) as stamp:
            jobid = stamp.read().splitlines()[0].split()[0]
        logfile = self.scheduler.jobid_logfilename(jobid,'unit_test')
        self.assertTrue(os.path.exists(logfile))
        success = False
        with open(logfile) as log:
            log_lines = log.read().splitlines()
        for line in log_lines:
            if re.match(self.config['AUTOCMS_SUCCESS_TOKEN'],line):
                success = True
        self.assertTrue(success)

    def test_job_counter(self):
        os.chdir(self.basepath)
        os.chdir('tests/scratch/localsub')
        set_job_counter(42)
        count = get_job_counter()
        self.assertEqual(count, 42)
