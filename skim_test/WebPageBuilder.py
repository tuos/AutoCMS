import re 
import os
import time
from JobRecord import JobRecord
import AutoCMSUtil

def build(newWebpageName,config,records):

  yesterday = int(time.time()) - 24 * 3600
  threehours = int(time.time()) - 3 * 3600

  with open(newWebpageName,'w') as webpage:

    AutoCMSUtil.beginWebpage(webpage,config)

    webpage.write( '<div style="align=left">\n' )

    # run and wait time plot (not log scaled)
    plot1name = config['AUTOCMS_TEST_NAME']+"_success24runwait.png"
    plot1path = config['AUTOCMS_WEBDIR']+"/"+plot1name
    AutoCMSUtil.createRunAndWaitTimePlot(plot1path,False,filter(
      lambda job: job.startTime > yesterday \
                  and job.isComplete() \
                  and job.isSuccess() ,
      records.values()
      )
    )
    webpage.write( '<img src="%s">\n' % plot1name )

    # run and wait time plot (log scaled) 
    plot2name = config['AUTOCMS_TEST_NAME']+"_success24runwait_log.png"
    plot2path = config['AUTOCMS_WEBDIR']+"/"+plot2name
    AutoCMSUtil.createRunAndWaitTimePlot(plot2path,True,filter(
      lambda job: job.startTime > yesterday \
                  and job.isComplete() \
                  and job.isSuccess() ,
      records.values()
      )
    )
    webpage.write( '<img src="%s">\n' % plot2name )

    webpage.write( '</div>\n' )

    webpage.write( '<hr />\n' )

    # description and statistics
    AutoCMSUtil.writeTestDescription(webpage,config)
    webpage.write('<hr />\n')

    webpage.write('<div style="width:30%;min-width: 20em;float:left;">\n')

    webpage.write('<b>Daily Job Statistics</b><br /><br />')
    AutoCMSUtil.writeBasicJobStatistics(webpage,config,records)
    # add some statistics on long running jobs
    long24hour = sum( 1 for job in records.values() if job.isSuccess()
                      and job.startTime > yesterday
                      and job.runTime() > config['SKIMTEST_RUNTIME_WARNING'] )
    webpage.write("Long running jobs (> %s s) in the last 24 hours: %d <br />\n"
                  % (config['SKIMTEST_RUNTIME_WARNING'],long24hour) )

    long3hour = sum( 1 for job in records.values() if job.isSuccess()
                     and job.startTime > threehours
                     and job.runTime() > config['SKIMTEST_RUNTIME_WARNING'] )
    webpage.write("Long running jobs (> %s s) in the last 3 hours: %d <br />\n"
                % (config['SKIMTEST_RUNTIME_WARNING'],long3hour) )
    webpage.write("<br /></div>\n")

    webpage.write('<div style="width:25%;min-width: 15em;float:left;">\n')
    webpage.write('<b>Errors by Worker Node:</b><br /><br />\n')
    AutoCMSUtil.listNodesByErrors(webpage,config,records)
    webpage.write('<br /></div>\n')

    webpage.write('<div style="width:40%;min-width: 25em;float:left;">\n')
    webpage.write('<b>Errors by Reason:</b><br /><br />\n')
    AutoCMSUtil.listErrorsByReason(webpage,config,records)
    webpage.write('<br /></div>\n')

    webpage.write('<div style="clear:both;"></div><hr />\n')

    # start a list of jobs to be printed
    printedJobs = list()

    # print failed jobs from last 24 hours, add them to the list
    webpage.write('<h3>Errors from the last 24 Hours</h3><hr />')
    printedJobs = printedJobs + AutoCMSUtil.writeJobRecords(
      '<b>ERROR</b>',
      webpage,
      config,
      filter( lambda job: job.startTime > yesterday \
                          and job.isComplete() \
                          and not job.isSuccess() ,
              records.values() ),
      inputFile='Input File',
      errorString='Error Type'
    )

    # print long execution time jobs
    webpage.write('<h3>Long Execution Time Warnings from the Last 24 Hours</h3><hr />' )
    printedJobs = printedJobs + AutoCMSUtil.writeJobRecords(
        'Warning',
         webpage,
         config,
         filter( lambda job: job.startTime > yesterday \
                             and job.isComplete() \
                             and job.isSuccess() \
                             and job.runTime() >= config['SKIMTEST_RUNTIME_WARNING'],
                 records.values() ),
         inputFile='Input File'
    )

    # print successful jobs if requested, add them to the list
    if int(config['AUTOCMS_PRINT_SUCCESS']) == 1:
      webpage.write('<h3>Successful Jobs</h3><hr />' )
      printedJobs = printedJobs + AutoCMSUtil.writeJobRecords(
          'Success',
           webpage,
           config,
           filter( lambda job: job.startTime > yesterday \
                               and job.isComplete() \
                               and job.isSuccess() \
                               and job.runTime() < config['SKIMTEST_RUNTIME_WARNING'],
                   records.values() ),
           inputFile='Input File'
      )

    AutoCMSUtil.endWebpage(webpage,config)

    return printedJobs
