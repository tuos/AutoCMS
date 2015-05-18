"""Test the AutoCMS web reporting functionality."""

import os
import shutil
import unittest
import re

from autocms.core import load_configuration
# cannot import perform_test_reporting function from autocms.web
# as nose thinks it is a test
import autocms.web

class TestWebPageCreation(unittest.TestCase):
    """Test the accurate creation of test webpages."""

    def setUp(self):
        self.config = load_configuration('autocms.cfg')
        self.config['AUTOCMS_WEBDIR'] = self.config['AUTOCMS_BASEDIR']
        # call the scratch directory 'uscratch' instead of 'scratch'
        # so that in pathological cases one does not resolve to
        # /scratch which is often used.
        self.testdir = os.path.join(self.config['AUTOCMS_BASEDIR'],
                                    'uscratch')
        os.makedirs(self.testdir)
        # make a fake web directory
        webdir = os.path.join(self.config['AUTOCMS_BASEDIR'],
                              'uscratch_web')
        self.config['AUTOCMS_WEBDIR'] = webdir
        os.makedirs(webdir)
        self.page_description = 'AutoCMS Web Unit Test Description'
        description_file = os.path.join(self.testdir, 'description.html')
        with open(description_file, 'w') as description_filehandle:
           description_filehandle.write(self.page_description)

    def tearDown(self):
        shutil.rmtree(os.path.join(self.config['AUTOCMS_BASEDIR'],
                                   'uscratch'))
        shutil.rmtree(os.path.join(self.config['AUTOCMS_BASEDIR'],
                                   'uscratch_web'))

    def test_create_webpage_with_description(self):
        """Test that a default webpage is created with description."""
        autocms.web.perform_test_reporting('uscratch', self.config)
        webpage_path = os.path.join(self.config['AUTOCMS_WEBDIR'],
                                    'uscratch/index.html')
        stylesheet_path = os.path.join(self.config['AUTOCMS_WEBDIR'],
                                    'uscratch/autocms.css')
        self.assertTrue(os.path.isfile(webpage_path))
        self.assertTrue(os.path.isfile(stylesheet_path))
        with open(webpage_path) as webpage:
            webpage_contents = webpage.read()
        self.assertTrue(re.search(self.page_description, webpage_contents))


if __name__ == '__main__':
    unittest.main()
