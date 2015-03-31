"""AutoCMSWebpage class to simplify generating a web page."""

import sys
import os
import time


class AutoCMSWebpage(object):

    def __init__(self, testname, path, records, config):
        """Construct new AutoCMSWebpage object.

        Arguments:
             testname - name of the autocms test directory
             path - name of output file to write html
             records - dictionary of JobRecords
             config - autocms configuration dictionary"""
        self.testname = testname
        self.records = records
        self.config = config
        self.output_path = path
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
                time.strftime("%c (%Z)") )
        )

    def end_page(self):
        """Close webpage body."""
        self.page += '</body></html>'

    def write_page(self):
        """Writes the web page to file."""
        with open(self.output_path,'w') as f:
            f.write(self.page)

    def add_test_description(self):
        """Writes the webpage description.

        Reads a 'description.html' file in the test directory, or 
        reports in the webpage that no description was found."""
        desc_file  = os.path.join(self.config['AUTOCMS_BASEDIR'],
                                  self.testname, 
                                  "description.html")
        if os.path.isfile(desc_file):
            with open(desc_file) as df:
                description = df.read()
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
            failures = sum(1 for job in self.records.viewvalues() 
                               if not job.is_success() and 
                                   job.start_time > min_time )
            successes = sum( 1 for job in self.records.viewvalues() 
                               if job.is_success() and 
                                   job.start_time > min_time )
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
                    selfpage += '</span>'
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
