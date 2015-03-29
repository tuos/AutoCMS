"""Test the AutoCMS configuration loading function."""

import unittest

from autocms.core import load_configuration

class TestConfiguration(unittest.TestCase):
    """Test that the configuration is loaded correctly."""

    def setUp(self):
        self.config = load_configuration('tests/data/autocms.cfg.unittest')

    def test_cmsrun_timeout(self):
        self.assertEqual(self.config['SKIMTEST_CMSRUN_TIMEOUT'],'14400')

    def test_input_file_token(self):
        self.assertEqual(self.config['AUTOCMS_input_file_TOKEN'],
                         'AutoCMS: input file ')

if __name__ == '__main__':
    unittest.main()
