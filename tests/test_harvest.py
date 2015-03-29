"""Test the AutoCMS log harvesting functionality."""

import os
import shutil
import unittest

from autocms.core import (
    JobRecord,
    load_configuration
)
from autocms.harvest import (
    list_log_files,
    register_new_stamps,
    create_records_from_stamps,
    write_stamp_file,
    parse_job_log,
    purge_old_stamps
)
from autocms.scheduler import Scheduler


class TestLogFiles(unittest.TestCase):
    """Test the discovery and maintenance of log files."""

    def setUp(self):
        self.config = load_configuration('tests/data/autocms.cfg.unittest')
        self.ls_result = os.listdir('tests/data')
        self.scheduler = Scheduler.factory('slurm')

    def test_list_log_files(self):
        logs = list_log_files(self.ls_result, self.scheduler, self.config)
        self.assertEqual(len(logs), 2)
        self.assertIn('unit_test.submission.5.1427385181.log', logs)
        self.assertIn('unit_test.slurm.o928417', logs)


class TestSubmissionStamps(unittest.TestCase):
    """Test the discovery and maintenance of submission stamps."""

    def setUp(self):
        """Copy a sample stamp  and two new stamps."""
        with open("tests/data/submission.stamps") as sfile:
            self.stamps = sfile.read().splitlines()
        with open("tests/data/newstamp.1427267142") as nsfile1:
            self.newstamp1 = nsfile1.read().splitlines()[0]
        with open("tests/data/newstamp.1427267182") as nsfile2:
            self.newstamp2 = nsfile2.read().splitlines()[0]
        shutil.copyfile("tests/data/submission.stamps",
                        "tests/scratch/submission.stamps")
        shutil.copyfile("tests/data/newstamp.1427267142",
                        "tests/scratch/newstamp.1427267142")
        shutil.copyfile("tests/data/newstamp.1427267182",
                        "tests/scratch/newstamp.1427267182")
        self.ls_result = os.listdir('tests/scratch')

    def tearDown(self):
        """Remove stamp files created for the test."""
        if os.path.exists('tests/scratch/submission.stamps'):
            os.remove('tests/scratch/submission.stamps')        
        if os.path.exists('tests/scratch/newstamp.1427267142'):
            os.remove('tests/scratch/newstamp.1427267142')        
        if os.path.exists('tests/scratch/newstamp.1427267182'):
            os.remove('tests/scratch/newstamp.1427267182')        

    def test_register_new_stamps(self):
        shutil.copyfile("tests/data/submission.stamps",
                        "tests/scratch/submission.stamps")
        os.chdir('tests/scratch')
        register_new_stamps(self.ls_result, "submission.stamps")
        os.chdir('../..')
        with open("tests/scratch/submission.stamps","r") as file:
            reg_stamps = file.read().splitlines()
        self.assertEqual(len(reg_stamps),5)
        self.assertIn(self.newstamp1,reg_stamps) 
        self.assertIn(self.newstamp2,reg_stamps) 
        self.assertIn(self.stamps[1],reg_stamps)
        self.assertFalse(os.path.exists('tests/scratch/newstamp.1427267182'))

    def test_record_creation_from_stamps(self):
        records = {}
        with open("tests/data/submission.stamps") as sfile:
            stamplist = sfile.read().splitlines() 
        create_records_from_stamps(records, stamplist)
        self.assertEqual(len(records),3)
        self.assertEqual(records[1427266802].jobid, '928417')
        self.assertEqual(records[1427266802].submit_status, 0)
        self.assertEqual(records[1427266802].submit_time, 1427266802)
        self.assertEqual(records[1427385181].exit_code, '1')
        self.assertEqual(records[1427385181].logfile, 
                         'skim_test.submission.95.1427385181.log')

    def test_write_stamps(self):
        if os.path.exists('tests/scratch/submission.stamps'):
            os.remove('tests/scratch/submission.stamps')
        write_stamp_file(self.stamps, 
                         'tests/scratch/submission.stamps')
        with open('tests/data/submission.stamps') as src:
            src_stamps = src.read()
        with open('tests/scratch/submission.stamps') as dst:
            dst_stamps = dst.read()
        self.assertEqual(src_stamps, dst_stamps)

    def test_purge_old_stamps(self):
        newstamps = purge_old_stamps(self.stamps, 1427266850)
        self.assertEqual(len(newstamps), 2)
        self.assertIn(self.stamps[2], newstamps)
        self.assertNotIn(self.stamps[0], newstamps)

 
if __name__ == '__main__':
    unittest.main()
