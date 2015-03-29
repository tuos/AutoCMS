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
    parse_job_log
)


class TestLogFiles(unittest.TestCase):
    """Test the discovery and maintenance of log files."""

    def setUp(self):
        self.config = load_configuration('tests/data/autocms.cfg.unittest')
        self.ls_result = os.listdir('tests/data')

    def test_list_log_files(self):
        logs = list_log_files(self.ls_result, self.config)
        self.assertEqual(len(logs), 2)
        self.assertIn('unit_test.submission.5.1427385181.log', logs)
        self.assertIn('unit_test.slurm.o928417', logs)


class TestSubmissionStamps(unittest.TestCase):
    """Test the discovery and maintenance of submission stamps."""

    def setUp(self):
        """Make a sample stamp file and two new stamps."""
        self.stamps = (
            "FAIL 1427385181 1 skim_test.submission.95.1427385181.log\n"
            "928417 1427266802 0\n"
            "928533 1427267102 0\n")
        with open("tests/scratch/submission.stamps","w") as file:
            file.write(self.stamps)
        # need a copy of the file that tests dont mess with, 
        # so that tests are not dependent on each other
        shutil.copyfile("tests/scratch/submission.stamps",
                        "tests/scratch/submission.fixed")
        self.newstamp1 = "928535 1427267142 0"
        with open("tests/scratch/newstamp.1427267142","w") as nsfile:
            nsfile.write(self.newstamp1)
        self.newstamp2 = "928538 1427267182 0"
        with open("tests/scratch/newstamp.1427267182","w") as nsfile:
            nsfile.write(self.newstamp2)
        self.ls_result = os.listdir('tests/scratch')

    def tearDown(self):
        """Remove stamp files created for the test."""
        if os.path.exists('tests/scratch/submission.stamps'):
            os.remove('tests/scratch/submission.stamps')        
        if os.path.exists('tests/scratch/submission.fixed'):
            os.remove('tests/scratch/submission.fixed')        
        if os.path.exists('tests/scratch/newstamp.1427267142'):
            os.remove('tests/scratch/newstamp.1427267142')        
        if os.path.exists('tests/scratch/newstamp.1427267182'):
            os.remove('tests/scratch/newstamp.1427267182')        

    def test_register_new_stamps(self):
        shutil.copyfile("tests/scratch/submission.fixed",
                        "tests/scratch/submission.stamps")
        os.chdir('tests/scratch')
        register_new_stamps(self.ls_result, "submission.stamps")
        os.chdir('../..')
        with open("tests/scratch/submission.stamps","r") as file:
            reg_stamps = file.read().splitlines()
        self.assertEqual(len(reg_stamps),5)
        self.assertIn(self.newstamp1,reg_stamps) 
        self.assertIn(self.newstamp2,reg_stamps) 
        self.assertIn('928417 1427266802 0',reg_stamps)
        self.assertFalse(os.path.exists('tests/scratch/newstamp.1427267182'))

    def test_record_creation_from_stamps(self):
        records = {}
        with open("tests/scratch/submission.fixed") as sfile:
            stamplist = sfile.read().splitlines() 
        create_records_from_stamps(records, stamplist)
        self.assertEqual(len(records),3)
        self.assertEqual(records[1427266802].jobid, '928417')
        self.assertEqual(records[1427266802].submit_status, 0)
        self.assertEqual(records[1427266802].submit_time, 1427266802)
        self.assertEqual(records[1427385181].exit_code, '1')
        self.assertEqual(records[1427385181].logfile, 
                         'skim_test.submission.95.1427385181.log')


    def test_purge_stamps(self):
        if os.path.exists('tests/scratch/submission.stamps'):
            os.remove('tests/scratch/submission.stamps')
        write_stamp_file(self.stamps.splitlines(), 
                         'tests/scratch/submission.stamps')
        with open('tests/scratch/submission.fixed') as src:
            src_stamps = src.read()
        with open('tests/scratch/submission.stamps') as dst:
            dst_stamps = dst.read()
        self.assertEqual(src_stamps, dst_stamps)

 
if __name__ == '__main__':
    unittest.main()
