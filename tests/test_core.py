"""Test the AutoCMS core functionality."""

import os
import unittest

from autocms.core import (JobRecord,
                          load_configuration,
                          load_records,
                          save_records)


class TestConfiguration(unittest.TestCase):
    """Test that the configuration is loaded correctly."""

    def setUp(self):
        self.config = load_configuration('tests/data/autocms.cfg.unittest')

    def test_cmsrun_timeout(self):
        self.assertEqual(self.config['SKIMTEST_CMSRUN_TIMEOUT'], '14400')

    def test_input_file_token(self):
        self.assertEqual(self.config['AUTOCMS_input_file_TOKEN'],
                         'AutoCMS: input file ')


class TestJobRecord(unittest.TestCase):
    """Test the JobRecord class methods."""

    def setUp(self):
        self.config = load_configuration('tests/data/autocms.cfg.unittest')

    def test_jobrecord_parse(self):
        """Test that bash configuration is correctly parsed."""
        record = JobRecord(1427266702, 928417, 0)
        record.parse_output('tests/data/unit_test.slurm.o928417',
                             self.config)
        self.assertEqual(record.num_proc, '383')
        self.assertEqual(record.exit_code, 0)
        self.assertEqual(record.start_time, 1427266802)
        self.assertEqual(record.end_time, 1427267170)

    def test_jobrecord_repr(self):
        """Test that repr returns constructor for an identical object."""
        record = JobRecord(1427266702, 928417, 0)
        record.parse_output('tests/data/unit_test.slurm.o928417',
                             self.config)
        record_copy = eval(repr(record)) 
        self.assertEqual(repr(record), repr(record_copy))


class TestRecordPersistance(unittest.TestCase):
    """Test that jobrecord dictionaries are loaded and saved correctly."""
    
    def setUp(self):
        """Make a sample dictionary of JobRecords and try to save it."""
        self.records = {}
        self.records[1427266702] = JobRecord(1427266702, 928417, 0)
        self.records[1427266742] = JobRecord(1427266742, 928423, 0)
        self.records[1427266792] = JobRecord(1427266792, 'FAIL', 4)
        save_records(self.records, 'tests/scratch/records.backup')

    def tearDown(self):
        """Clean up tests/scratch upon exit."""
        if os.path.exists('tests/scratch/records.backup'):
            os.remove('tests/scratch/records.backup')

    def test_recordpersistance_save(self):
        """Check that the records pickle file was created."""
        self.assertTrue(os.path.exists('tests/scratch/records.backup'))

    def test_recordpersistance_load(self):
        """Check that records are accurately loaded."""
        records_copy = load_records('tests/scratch/records.backup')
        for key in self.records.iterkeys():
            attrs = (a for a in dir(self.records[key]) if 
                         not callable(getattr(self.records[key],a)))
            for a in attrs:
                self.assertEqual(getattr(records_copy[key], a), 
                                 getattr(self.records[key], a))


if __name__ == '__main__':
    unittest.main()
