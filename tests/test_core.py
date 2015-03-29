"""Test the AutoCMS core functionality."""

import unittest

from autocms.core import (JobRecord,
                          load_configuration)

class TestConfiguration(unittest.TestCase):
    """Test that the configuration is loaded correctly."""

    def setUp(self):
        self.config = load_configuration('tests/data/autocms.cfg.unittest')

    def test_cmsrun_timeout(self):
        self.assertEqual(self.config['SKIMTEST_CMSRUN_TIMEOUT'],'14400')

    def test_input_file_token(self):
        self.assertEqual(self.config['AUTOCMS_input_file_TOKEN'],
                         'AutoCMS: input file ')


class TestJobRecord(unittest.TestCase):
    """Test the JobRecord class methods."""

    def setUp(self):
        self.config = load_configuration('tests/data/autocms.cfg.unittest')

    def test_jobrecord_parse(self):
        record = JobRecord(1427266702,928417,0)
        record.parse_output('tests/data/unit_test.slurm.o928417',
                             self.config)
        self.assertEqual(record.num_proc,'383')
        self.assertEqual(record.exit_code,0)
        self.assertEqual(record.start_time,1427266802)
        self.assertEqual(record.end_time,1427267170)

    def test_jobrecord_repr(self):
        """Test that repr returns constructor for an identical object."""
        record = JobRecord(1427266702,928417,0)
        record.parse_output('tests/data/unit_test.slurm.o928417',
                             self.config)
        record_copy = eval(repr(record)) 
        self.assertEqual(repr(record),repr(record_copy))


if __name__ == '__main__':
    unittest.main()
