"""AutoCMSWebpage class to simplify generating a web page."""

import os
import time
import re
import shutil

from .core import (load_records, __version__)
from .plot import (
    create_run_and_waittime_plot
)

class AutoCMSWebpage(object):
    """Class for building and writing a page to report on an AutoCMS test."""

    def __init__(self, records, testname, config):
        """Construct new AutoCMSWebpage object.

        Arguments:
             records - dictionary of JobRecords
             testname - name of the autocms test directory
             config - autocms configuration dictionary"""
        self.records = records
        self.testname = testname
        self.config = config
        self.page = ""

    def begin_page(self):
        """Write head and open webpage body, state name and time."""
        self.page += (
            '<html><head>\n'
            '<title>{0} Site Test: {1}</title>\n'
            '<link rel="stylesheet" type="text/css" href="autocms.css">'
            '</head>\n<body>\n<div class="page-header-box">\n'
            '<div class="timestamp">{2}</div>\n'
            '<div class="version">AutoCMS version {3}</div>\n'
            '{4} Site Test: {5}'
            '</div>\n'.format(
                self.config['AUTOCMS_SITE_NAME'],
                self.testname,
                time.strftime("%c (%Z)"),
                __version__,
                self.config['AUTOCMS_SITE_NAME'],
                self.testname)
        )

    def end_page(self):
        """Close webpage body"""
        self.page += '</body></html>'

    def write_page(self):
        """Writes the web page and styleshee to file."""
        self._write_page_stylesheet()
        webpath = os.path.join(self.config['AUTOCMS_WEBDIR'], self.testname)
        if not os.path.exists(webpath):
            os.makedirs(webpath)
        # write a 'index.html.new' file and then rename it to
        # 'index.html'. This prevents users from viewing a half
        # completed webpage when the page refreshes.
        newpagepath = os.path.join(webpath, 'index.html.new')
        pagepath = os.path.join(webpath, 'index.html')
        with open(newpagepath, 'w') as output_file:
            output_file.write(self.page)
        os.rename(newpagepath, pagepath)

    def _write_page_stylesheet(self):
        """Copy the default or custom test stylesheet to the webdir."""
        webpath = os.path.join(self.config['AUTOCMS_WEBDIR'], self.testname)
        src_stylesheet = os.path.join(self.config['AUTOCMS_BASEDIR'],
                                      'default.css')
        dst_stylesheet = os.path.join(webpath, 'autocms.css')
        shutil.copyfile(src_stylesheet, dst_stylesheet)

    def add_test_description(self, width):
        """Writes the webpage description.

        'width' is the max-width of the description box.

        Reads a 'description.html' file in the test directory, or
        reports in the webpage that no description was found."""
        desc_file = os.path.join(self.config['AUTOCMS_BASEDIR'],
                                 self.testname,
                                 "description.html")
        self.page += ('<div class="textbox" '
                      'style="max-width:{0}%;">\n'.format(width))
        self.page += ('<div class="textbox-header">Test Description:'
                      '</div><br /><br />\n')
        if os.path.isfile(desc_file):
            with open(desc_file) as handle:
                description = handle.read()
            self.page += description + '\n'
        else:
            self.page += "No test description found.\n"
        self.page += '</div>\n'

    def add_job_failure_rates(self, width, times, warn_rate):
        """Writes basic statistics on failed and successful jobs.

        Arguments:
            width - max-width of element on the page in percent
            times - list of time intervals in hours
            warn_rate - percent of jobs failing below which to display
                        text in red"""
        self.page += ('<div class="textbox" '
                      'style="max-width:{0}%;">\n'.format(width))
        self.page += ('<div class="textbox-header">'
                      'Recent job success rates:</div>\n')
        for t in times:
            min_time = int(time.time()) - t*3600
            failures = sum(1 for job in self.records
                           if not job.is_success() and
                           job.start_time > min_time)
            successes = sum(1 for job in self.records
                            if job.is_success() and
                            job.start_time > min_time)
            self.page += ("<br /><br />\nSuccessful jobs in the last "
                          "{0} hours: {1}".format(t, successes))
            self.page += ("<br />\nFailed jobs in the last "
                          "{0} hours: {1}".format(t, failures))
            # print success rates if jobs have actually run
            if successes + failures > 0:
                rate = float(100 * successes) / float(failures + successes)
                self.page += "<br />\nSuccess rate ({0} hours): ".format(t)
                if rate < warn_rate:
                    self.page += '<span style="color:red;">'
                self.page += "{0:.2f}%".format(rate)
                if rate < warn_rate:
                    self.page += '</span>'
        self.page += '</div>\n'

    def add_divider(self):
        """Write a <hr /> divider and clear floats."""
        self.page += '<hr style="clear:both;"/>\n'


    def add_floating_image(self, width, image_file):
        """Adds a floating image to open filehandle webpage.

        Arguments:
            width - the maximum width of the image, in percent
            image_file - the name of the path to the image relative
                         to self.path"""
        self.page += ('<div class="plotbox" '
                      'style="max-width:{0}%;">\n'.format(width))
        self.page += '<img src="{0}" /></div>\n'.format(image_file)

    def __repr__(self):
        """Describe object id and page testname."""
        return ('<{0}.{1} object at {2} testname: {3}>'.format(
                    self.__class__.__module__,
                    self.__class__.__name__,
                    hex(id(self)),
                    self.testname))

    def __str__(self):
        """Return page destination and text."""
        return ('{0}.{1} object.\n\nTest Name: {2}\n\n'
                'Page content:\n\n{3}'.format(
                    self.__class__.__module__,
                    self.__class__.__name__,
                    self.testname,
                    self.page))


def produce_default_webpage(records, testname, config):
    """Create a basic test webpage applicable to any AutoCMS test."""
    webpath = os.path.join(config['AUTOCMS_WEBDIR'], testname)
    runtime_plot_path = os.path.join(webpath, 'runtime.png')
    recent_records = [job for job in records
                      if job.start_time > int(time.time()) - 3600*24]
    webpage = AutoCMSWebpage(records, testname, config)
    webpage.begin_page()
    webpage.add_divider()
    webpage.add_test_description(50)
    if len(recent_records) > 1:
        create_run_and_waittime_plot(recent_records, (8,4), runtime_plot_path)
        webpage.add_floating_image(45, 'runtime.png')
    webpage.add_divider()
    webpage.add_job_failure_rates(30, [24, 3], 90.0)
    webpage.end_page()
    webpage.write_page()


def purge_old_web_logs(testname, config):
    """Remove logs older than AUTOCMS_LOG_LIFETIME in test webdir.

    Any file ending in '.log' in a test directory is considered
    a log file."""
    webdir = os.path.join(config['AUTOCMS_WEBDIR'], testname)
    if not os.path.exists(webdir):
        return
    logs = []
    for logfile in os.listdir(webdir):
        if re.search(r'\.log$', logfile):
            logs.append(logfile)
    purgetime = int(time.time()) - 3600*24*int(config['AUTOCMS_LOG_LIFETIME'])
    for logfile in logs:
        if int(os.path.getmtime(logfile)) < purgetime:
            os.remove(logfile)


def perform_test_reporting(testname, config):
    """Analyze job records for given test and create webpage report."""
    records = load_records(testname, config)
    produce_default_webpage(records, testname, config)
