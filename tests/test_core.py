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
        self.config = load_configuration('autocms.cfg.example')

    def test_cmsrun_timeout(self):
        """Check that config sets the test names."""
        self.assertEqual(self.config['AUTOCMS_TEST_NAMES'],
                                     'example_test:bare_test')

    def test_input_file_token(self):
        """Check that config sets the start time token."""
        self.assertEqual(self.config['AUTOCMS_start_time_TOKEN'],
                         'AutoCMS: timestamp_start ')


class TestJobRecord(unittest.TestCase):
    """Test the JobRecord class methods."""

    def setUp(self):
        self.config = load_configuration('autocms.cfg')

    def test_jobrecord_parse(self):
        """Test that a job log is correctly parsed."""
        record = JobRecord(1, 928417, 1427266702, 0, 'data/example_A.log')
        record.parse_output('tests', self.config)
        self.assertEqual(getattr(record, 'num_proc'), '383')
        self.assertEqual(record.exit_code, 0)
        self.assertEqual(record.start_time, 1427266802)
        self.assertEqual(record.end_time, 1427267170)

    def test_jobrecord_stamp(self):
        """Test writing and constructing from a stamp."""
        record = JobRecord(1, '928417', 1427266702, 0, 'data/example_A.log')
        stamp = record.stamp()
        record_copy = JobRecord.create_from_stamp(stamp)
        self.assertEqual(record.__dict__, record_copy.__dict__)
        record = JobRecord(3, None, 427266792, 4, 'c.log')
        stamp = record.stamp()
        record_copy = JobRecord.create_from_stamp(stamp)
        self.assertEqual(record.__dict__, record_copy.__dict__)

class TestRecordPersistance(unittest.TestCase):
    """Test that jobrecord lists are loaded and saved correctly."""

    def setUp(self):
        """Make a sample list of JobRecords and try to save it."""
        self.config = load_configuration('autocms.cfg')
        self.records = []
        self.records.append(JobRecord(1, '928417', 1427266702, 0, 'a.log'))
        self.records.append(JobRecord(2, '928423', 427266742, 0, 'b.log'))
        self.records.append(JobRecord(3, None, 427266792, 4, 'c.log'))
        save_records(self.records, 'tests', self.config)
        self.recordpath = os.path.join(self.config['AUTOCMS_BASEDIR'],
                                       'tests',
                                       'records.pickle')

    def tearDown(self):
        """Clean up temporary test files upon exit."""
        if os.path.isfile(self.recordpath):
            os.remove(self.recordpath)

    def test_recordpersistance_save(self):
        """Check that the records pickle file was created."""
        self.assertTrue(os.path.isfile(self.recordpath))

    def test_recordpersistance_load(self):
        """Check that records are accurately loaded."""
        rdict = {job.seq : job for job in self.records}
        records_copy = load_records('tests', self.config)
        rdict_copy = {job.seq : job for job in records_copy}
        for key in rdict.viewkeys():
            self.assertEqual(rdict[key].__dict__,
                             rdict_copy[key].__dict__)


if __name__ == '__main__':
    unittest.main()
