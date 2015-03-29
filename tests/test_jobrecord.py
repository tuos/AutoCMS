"""Test the AutoCMS JobRecord class methods."""

import unittest

from autocms.core import load_configuration
from autocms.core import JobRecord


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
