"""AutoCMSWebpage class to simplify generating a web page."""

import os
import time
import re

from .core import load_records


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
            "<html><head>\n"
            "<title>{0} Internal Site Test: {1}</title>\n"
            "<style>div.fcontent {{ float:left;}}</style>\n"
            "</head>\n"
            "<body>\n"
            "<h2>{2} Internal Site Test: {3}</h2>\n"
            "Page generated at: {4}\n".format(
                self.config['AUTOCMS_SITE_NAME'],
                self.testname,
                self.config['AUTOCMS_SITE_NAME'],
                self.testname,
                time.strftime("%c (%Z)"))
        )

    def end_page(self):
        """Close webpage body."""
        self.page += '</body></html>'

    def write_page(self):
        """Writes the web page to file."""
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

    def add_test_description(self):
        """Writes the webpage description.

        Reads a 'description.html' file in the test directory, or
        reports in the webpage that no description was found."""
        desc_file = os.path.join(self.config['AUTOCMS_BASEDIR'],
                                 self.testname,
                                 "description.html")
        if os.path.isfile(desc_file):
            with open(desc_file) as handle:
                description = handle.read()
            self.page += description + '<br />\n'
        else:
            self.page += "No test description found.<br />\n"

    def add_job_failure_rates(self, width, times, warn_rate):
        """Writes basic statistics on failed and successful jobs.

        Arguments:
            width - width of element on the page in percent
            times - list of time intervals in hours
            warn_rate - percent of jobs failing below which to display
                        text in red"""
        self.page += ('<div class="fcontent" '
                      'style="min-width:{0}%;">'.format(width))
        for t in times:
            min_time = int(time.time()) - t*3600
            failures = sum(1 for job in self.records
                           if not job.is_success() and
                           job.start_time > min_time)
            successes = sum(1 for job in self.records
                            if job.is_success() and
                            job.start_time > min_time)
            self.page += ("Successful jobs in the last {0} hours: {1}"
                          "<br />\n".format(t, successes))
            self.page += ("Failed jobs in the last {0} hours: {1}"
                          "<br />\n".format(t, failures))
            # print success rates if jobs have actually run
            if successes + failures > 0:
                rate = float(100 * successes) / float(failures + successes)
                self.page += "Success rate ({0} hours): ".format(t)
                if rate < warn_rate:
                    self.page += '<span style="color:red;">'
                self.page += "{0:.2f}%".format(rate)
                if rate < warn_rate:
                    self.page += '</span>'
                self.page += '<br />\n'
            self.page += '<br />\n'
        self.page += '</div>\n'

    def add_divider(self):
        """Write a <hr /> divider and spacing to filehandle webpage."""
        self.page += '<br style="clear:both;"/>\n<hr />\n<br />\n'


    def add_floating_image(self, width, image_file):
        """Adds a floating image to open filehandle webpage.

        Arguments:
            width - the minimum width of the image, in percent
            image_file - the name of the path to the image relative
                         to self.path"""
        self.page += ('<div class="fcontent" '
                      'style="min-width:{0}%;">\n'.format(width))
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
    webpage = AutoCMSWebpage(records, testname, config)
    webpage.begin_page()
    webpage.add_divider()
    webpage.add_test_description()
    webpage.add_divider()
    webpage.add_job_failure_rates(30, [24, 3], 90.0)
    webpage.add_divider()
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
