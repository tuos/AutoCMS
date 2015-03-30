"""Test job submission compnents."""

import os
import shutil
import unittest
import time

from autocms.core import load_configuration
from autocms.scheduler import Scheduler
from autocms.submit import submit_and_stamp


class TestSubmission(unittest.TestCase):
    """Test that submission results in valid stamp and log."""

    def setUp(self):
        self.config = load_configuration('tests/data/autocms.cfg.unittest')
        self.scheduler = Scheduler.factory('local')
        os.makedirs('tests/scratch/localsub')
        shutil.copyfile("tests/data/unit_test.local",
                        "tests/scratch/localsub/unit_test.local")

    def tearDown(self):
        shutil.rmtree('tests/scratch/localsub')

    def test_stamp_creation(self):
        os.chdir('tests/scratch/localsub')
        stampfile = submit_and_stamp(2,
                                     'unit_test',
                                     self.scheduler,
                                     self.config)
        os.chdir('../../..')
        time.sleep(3)
        stampfile = os.path.join('tests/scratch/localsub', stampfile)
        self.assertTrue(os.path.isfile(stampfile))
        with open(stampfile) as nsfile:
            newstamp_raw = nsfile.read().splitlines()
        self.assertEqual(len(newstamp_raw), 1)
        newstamp = newstamp_raw[0].strip()
        self.assertEqual(newstamp.split()[2],'0')


