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
        self.logs_to_copy = []

    def begin_page(self):
        """Write head and open webpage body, state name and time."""
        self.page += (
            '<html><head>\n'
            '<title>{0} Site Test: {1}</title>\n'
            '<link rel="stylesheet" type="text/css" href="autocms.css">'
            '<meta name="viewport" content="width=device-width, '
            'initial-scale=1">'
            '</head>\n<body>\n<div class="page-header-box">\n'
            '{2} Site Test: {3}'
            '<div class="timestamp">{4}</div>\n'
            '<div class="version">AutoCMS version {5}</div>\n'
            '</div>\n'.format(
                self.config['AUTOCMS_SITE_NAME'],
                self.testname,
                self.config['AUTOCMS_SITE_NAME'],
                self.testname,
                time.strftime("%c (%Z)"),
                __version__)
        )

    def end_page(self):
        """Close webpage body"""
        self.page += '</body></html>'

    def write_page(self):
        """Writes the web page and stylesheet to file, copy logs"""
        self._write_page_stylesheet()
        self._copy_job_logs()
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

    def _copy_job_logs(self):
        """Copy job logs with displayed links to webdir."""
        basedir = os.path.join(self.config['AUTOCMS_BASEDIR'], self.testname)
        webdir = os.path.join(self.config['AUTOCMS_WEBDIR'], self.testname)
        for log in self.logs_to_copy:
            src_file = os.path.join(basedir, log)
            dst_file = os.path.join(webdir, log)
            if not os.path.isfile(src_file):
                continue
            # dont copy logs already at the destination
            # not only does it waste time, they will not be
            # removed until much later as their mtime is now
            if os.path.isfile(dst_file):
                continue
            shutil.copy(src_file, dst_file)

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

    def add_count_jobs_by_attribute(self, records, attr, header, width):
        """Writes a table of job counts by attribute.

        Arguments:
            records - list of JobRecords to consider
            attr - JobRecord attribute to count
            header - html string to go above start of table but inside textbox
            width - max width of textbox

        Don't add anything to the page if records is empty"""
        records_with_attr = (job for job in records if hasattr(job, attr))
        attr_counts = dict()
        for job in records_with_attr:
            key = getattr(job, attr)
            if key in attr_counts:
                attr_counts[key] += 1
            else:
                attr_counts[key] = 1 
        if not attr_counts:
            return
        self.page += ('<div class="textbox" '
                      'style="max-width:{0}%;">\n'.format(width))
        self.page += '{0}\n<table>\n'.format(header)
        for attr in sorted(attr_counts, key=attr_counts.get, reverse=True):
            self.page += ('<tr><td>{0}</td><td>{1}'
                          '</td></tr> \n'.format(
                          attr_counts[attr], attr))
        self.page += '</table></div>\n'

    def add_failures_by_node(self, width, hours):
        """Writes a list of nodes by number of errors.

        Looks at only jobs starting in the last 'hours' hours.

        Does not do anything if no jobs have failed in the last hours."""
        min_time = int(time.time()) - 3600*hours
        failures = (job for job in self.records if
                        job.completed and not job.is_success() and
                        job.start_time > min_time)
        header = ('<div class="textbox-header">'
                  'Number of failed jobs by worker node:</div>\n'
                  '<br />(previous {0} hours)<br />'
                  '<br />\n<table>'.format(hours))
        self.add_count_jobs_by_attribute(failures, 'node', header, width)

    def add_failures_by_reason(self, width, hours):
        """Writes a list of error strings by number of errors.

        Looks at only jobs starting in the last 'hours' hours.

        Does not do anything if no jobs have failed in the last hours."""
        min_time = int(time.time()) - 3600*hours
        failures = (job for job in self.records if
                        job.completed and not job.is_success() and
                        job.start_time > min_time)
        header = ('<div class="textbox-header">'
                  'Number of failed jobs by reason:</div>\n'
                  '<br />(previous {0} hours)<br />'
                  '<br />\n<table>'.format(hours))
        self.add_count_jobs_by_attribute(failures, 'error_string',
                                         header, width)

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

    def add_job_listing(self, records, header, itemheader, **attr_desc):
        """Display information a list of JobRecords.

        All JobRecords in the list 'records' are reported.
        By default, the start time, node, and error type are shown.
        If records is empty nothing is displayed.

        Additional jobrecord attributes may be shown by adding
        keyword arguments of the form attribute=description, where
        attribute is the JobRecord attribute and description is a
        string which will be displayed preceding the attribute value.

        A link is given to the job log, and the log is appended to the
        logs_to_copy list.

        The string 'header' is displayed at the top of the text box,
        and the string 'itemheader' is displayed for each item."""
        if not records:
            return
        self.logs_to_copy += [job.logfile for job in records]
        self.page += '<div class="textbox" style="max-width:95%;">\n'
        self.page += ('<div class="textbox-header">'
                      '{0}</div><br />\n'.format(header))
        records.sort(key=lambda x: x.start_time, reverse=True)
        for counter, job in enumerate(records):
            self.page += '<br />\n'
            self.page += '{0}&nbsp;{1}:<br />\n'.format(itemheader, counter+1)
            self.page += ('Start time: {0} <br />\n'.format(
                          time.strftime('%c (%Z)',
                              time.localtime(job.start_time))))
            self.page += 'Node name: {0} <br />\n'.format(job.node)
            self.page += ('Log file: <a href="{0}">{1}</a>'
                          '<br />\n'.format(job.logfile, job.logfile))
            self.page += 'Error Type: {0} <br />\n'.format(job.error_string)
            for attr,desc in attr_desc.viewitems():
                if not hasattr(job, attr):
                    continue
                self.page += desc + ": " + getattr(job,attr) + '<br />\n'

    def add_failed_job_listing(self, hours, **attr_desc):
        """Display information about failed jobs.

        All completed jobs not returning is_success True with
        start times within 'hours' of the present are listed.
        By default, the start time, node, and error type are shown.

        Additional jobrecord attributes may be shown by adding
        keyword arguments of the form attribute=description, where
        attribute is the JobRecord attribute and description is a
        string which will be displayed preceding the attribute value.

        A link is given to the job log, and the log is appended to the
        logs_to_copy list."""
        min_time = int(time.time()) - 3600*hours
        records_to_print = [job for job in self.records if
                            job.completed and job.start_time > min_time
                            and not job.is_success()]
        header = 'Failed jobs from the last {0}  hours:'.format(hours)
        itemheader = '<span style="font-weight:bold">Error </span>'
        self.add_job_listing(records_to_print, header,
                             itemheader, **attr_desc)

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
    webpage.add_failures_by_node(25, 24)
    webpage.add_failures_by_reason(40, 24)
    webpage.add_divider()
    webpage.add_failed_job_listing(24)
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
