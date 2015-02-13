import re 
import os
import time
import datetime
from JobRecord import JobRecord
import AutoCMSUtil

def build(newWebpageName,config,records):

  now = int(time.time())
  yesterday = int(time.time()) - 24 * 3600
  threehours = int(time.time()) - 3 * 3600

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
    webpage.write( '<div style="float:left;font-weight:bold"><br />Rutime and wait time plot '
                   + 'from last 24 hours:<br /><br />')
    webpage.write( '<img src="%s"></div>\n' % plot1name )
  
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
    webpage.write( '<div style="float:right;font-weight:bold"><br />Rutime and wait time plot '
                   + 'from last 24 hours (log scaled):<br /><br />')
    webpage.write( '<img src="%s"></div>\n' % plot2name )

    webpage.write( '<div style="clear:both"></div><hr />\n' )


    # runtime plot by number of cmsRun processes
    plot3name = config['AUTOCMS_TEST_NAME']+"_successBycmsRun_log.png"
    plot3path = config['AUTOCMS_WEBDIR']+"/"+plot3name
    createCMSRunTimePlot(plot3path,filter(
      lambda job: job.startTime > yesterday \
                  and job.isComplete() \
                  and job.isSuccess() ,
      records.values()
      )
    )
    webpage.write( '<div style="float:left;font-weight:bold"><br />Rutimes by number of additional cmsRun '
                   + 'processes on the node from last 24 hours:<br /><br />')
    webpage.write( '<img src="%s"></div>\n' % plot3name )


    # long term statistics plot
    statFile = "statistics.dat"
    statPlotName = config['AUTOCMS_TEST_NAME']+"_basicStats.png"
    statPlotPath = config['AUTOCMS_WEBDIR']+"/"+statPlotName
    AutoCMSUtil.createBasicStatisticsPlot(statFile,statPlotPath, now - 7*24*3600, now)
    webpage.write( '<div style="float:right;font-weight:bold"><br />Fake rate and '
                   + 'runtime statistics of completed jobs over last week, trailing '
                   + config['AUTOCMS_STAT_INTERVAL'] + ' hours: <br /><br />' )
    webpage.write( '<img src="%s"></div>\n' % statPlotName )
    
    webpage.write( '<div style="clear:both"></div><hr />\n' )
 

  
    # description and statistics
    AutoCMSUtil.writeTestDescription(webpage,config)
    webpage.write('<hr />\n')

    webpage.write('<div style="width:30%;min-width: 20em;float:left;">\n')

    webpage.write('<b>Daily Job Statistics</b><br /><br />')
    AutoCMSUtil.writeBasicJobStatistics(webpage,config,records)
    # add some statistics on long running jobs
    long24hour = sum( 1 for job in records.values() if job.isSuccess()
                      and job.startTime > yesterday
                      and job.runTime() >= int(config['SKIMTEST_RUNTIME_WARNING']) )
    webpage.write("Long running jobs (> %s s) in the last 24 hours: %d <br />\n"
                  % (config['SKIMTEST_RUNTIME_WARNING'],long24hour) )

    long3hour = sum( 1 for job in records.values() if job.isSuccess()
                     and job.startTime > threehours
                     and job.runTime() >= int(config['SKIMTEST_RUNTIME_WARNING']) )
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
                             and job.runTime() >= int(config['SKIMTEST_RUNTIME_WARNING']),
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




def createCMSRunTimePlot(outputFileName,records):

  now = int(time.time())
  yesterday = now - 24*3600

  #find utc offset
  utcoffset = int(round((datetime.datetime.now() - datetime.datetime.utcnow()).total_seconds()))

  #create data file to send to gnuplot
  dataFileName = outputFileName+'.data'
  with open(dataFileName,'w') as dataFile:
    for job in filter( lambda job: hasattr(job,'cmsRunProcCount') , records ):
      try:
        cmsRPCfloat = float(job.cmsRunProcCount)
        print >>dataFile, '%d %d %d' % (job.startTime+utcoffset,job.runTime(),cmsRPCfloat)
      except ValueError:
        pass

  # make the plot
  # note: gnuplot needs to be compiled with 
  # png terminal support.
  os.system(
"""\
gnuplot <<- EOF
  set terminal png crop enhanced  size 700,350 
  set output "%s"
  set palette model RGB defined ( 0 'dark-green', 4 'dark-yellow',  8 'red', 12 'dark-violet' )
  set xlabel "timestamp (recent 24 hours)"
  set ylabel "running time (s)"
  set cblabel "# of cmsRun procs on node"
  set xdata time
  set timefmt "%%s"
  set xtics 14400
  set format x "%%a %%Hh"
  #set yrange [0:1000]
  set xrange ["%d":"%d"]
  set cbrange [0:12]
  #set xtics border nomirror in rotate by -45 offset character 0, 0, 0
  set style line 1 lc rgb 'red' pt 5 ps 0.7  # square
  set style line 2 lc rgb 'green' pt 5 ps 0.7  # square
  plot '%s' using 1:2:3 notitle ls 1 palette
EOF""" % ( outputFileName, yesterday+utcoffset, now+utcoffset, dataFileName )
  ) 

  os.remove(dataFileName) 



