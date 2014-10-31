import re 
import os
import time
from JobRecord import JobRecord
import AutoCMSUtil

def build(newWebpageName,config,records):

  yesterday = int(time.time()) - 24 * 3600

  with open(newWebpageName,'w') as webpage:

    AutoCMSUtil.beginWebpage(webpage,config)

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
    webpage.write( '<br />\n')

    plot2name = config['AUTOCMS_TEST_NAME']+"_dicerolls.png"
    plot2path = config['AUTOCMS_WEBDIR']+"/"+plot2name
    AutoCMSUtil.createHistogram(plot2path,1.0,'sum of the dice','count','diceSum',filter(
      lambda job: job.startTime > yesterday \
                  and job.isComplete(),
      records.values()
      )
    )
    webpage.write( '<img src="%s">\n' % plot2name )

    plot3name = config['AUTOCMS_TEST_NAME']+"_numprocs.png"
    plot3path = config['AUTOCMS_WEBDIR']+"/"+plot3name
    AutoCMSUtil.createHistogram(plot3path,50.0,'number of running processes','count','numProc',filter(
      lambda job: job.startTime > yesterday \
                  and job.isComplete(),
      records.values()
      )
    )
    webpage.write( '<img src="%s">\n' % plot3name )

    webpage.write( '<hr />\n' )

    # description and statistics
    AutoCMSUtil.writeTestDescription(webpage,config)
    webpage.write('<hr />\n')
    AutoCMSUtil.writeBasicJobStatistics(webpage,config,records)
    webpage.write('<hr />\n')

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
      diceSum='Roll of the Dice',
      errorString='Error Type'
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
                               and job.isSuccess(),
                   records.values() ),
           diceSum='Roll of the Dice',
           numProc='Num. of processes on the node'
      )

    AutoCMSUtil.endWebpage(webpage,config)

    return printedJobs
