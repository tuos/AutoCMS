"""Functions to simplify generating a web page."""

import sys
import os
import time

from .core import JobRecord


def begin_webpage(testname, webpage, config):
    """Write head and open webpage body, state name of test and time.

    Arguments:
        testname - name of the test directory
        webpage - open filehandle to write to
        config - AutoCMS configuration dictionary""" 
    webpage.write(
        "<html><head><title>{0} Internal Site Test: {1}"
        "</title></head>\n"
        "<body>\n"
        "<h2>{2} Internal Site Test:{3}</h2>\n"
        "Page generated at: {4}\n".format( 
            config['AUTOCMS_SITE_NAME'],
            testname,
            config['AUTOCMS_SITE_NAME'],
            testname,
            time.strftime("%c (%Z)") )
    )


def end_webpage(webpage, config):
    """Close webpage body.

    Arguments:
        webpage - open filehandle to write to
        config - AutoCMS configuration dictionary"""
    webpage.write('</body></html>')


def write_test_description(testname, webpage, config):
    """Writes the webpage description.

    Arguments:
        testname - name of test directory
        webpage - open filehandle to write to
        config - AutoCMS configuration dictionary

    Reads a 'description.html' file in the test directory, or 
    reports in the webpage that no description was found."""
    desc_file  = os.path.join(config['AUTOCMS_BASEDIR'],
                              testname, 
                              "description.html")
    if os.path.isfile(desc_file):
        with open(desc_file) as df:
            description = df.read()
        webpage.write(description + '<br />\n')
    else:
        webpage.write("No test description found.<br />\n") 

def write_job_failure_rates(times, warn_rate, records, webpage, config):
    """Writes basic statistics on failed and successful jobs.

    Arguments:
        times - list of time intervals in hours
        warn_rate - percent of jobs failing below which to display
                    text in red
        records - dictionary of JobRecords
        webpage - open filehandle to write to
        config - AutoCMS configuration dictionary""" 
    for t in times:
        min_time = int(time.time()) - t*3600
        failures = sum( 1 for job in records.viewvalues() 
                        if not job.is_success() and job.start_time > min_time )
        successes = sum( 1 for job in records.viewvalues() 
                         if job.is_success() and job.start_time > min_time )
        webpage.write("Successful jobs in the last {0} hours: {1}"
                      "<br />\n".format(t, successes))
        webpage.write("Failed jobs in the last {0} hours: {1}"
                      "<br />\n".format(t, failures))
        # print success rates if jobs have actually run
        if successes + failures > 0:
            rate = float(100 * successes) / float(failures + successes)
            webpage.write("Success rate ({0} hours): ".format(t))
            if rate < warn_rate:
                webpage.write('<span style="color:red;">')
            webpage.write("{0:.2f}%".format(rate))
            if rate < warn_rate:
                webpage.write('</span>')
            webpage.write('<br />\n')
        webpage.write('<br />\n')
        

def write_divider(webpage):
    """Write a <hr /> divider and spacing to filehandle webpage."""
    webpage.write('<br style="clear:both;"/>\n<hr />\n<br />\n')
