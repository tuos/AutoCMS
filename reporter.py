import os
import re
import time
import datetime
import cPickle as pickle
from JobRecord import JobRecord
import AutoCMSUtil

def main():

  # load configuration and enter test directory
  config = AutoCMSUtil.LoadConfiguration('autocms.cfg')
  testdir = config['AUTOCMS_BASEDIR']+"/"+config['AUTOCMS_TEST_NAME']
  os.chdir(testdir)

  # initialize JobRecord dictionary, or load saved state
  autocms_pkl = 'records.pickle'
  if os.path.isfile(autocms_pkl):
    records = pickle.load( open(autocms_pkl, "rb") )
  else:
    records = dict()

  webpageName = config['AUTOCMS_WEBDIR']+"/"+config['AUTOCMS_TEST_NAME']+".html"
  newWebpageName = config['AUTOCMS_WEBDIR']+"/"+config['AUTOCMS_TEST_NAME']+".html.new"

  # build new webpage
  with open(newWebpageName,'w') as webpage:
    writeWebpageHeader(webpage,config) 
    yesterday = int(time.time()) - 24 * 3600
    
    # add code for graphics
  
    # print failed jobs from last 24 hours
    webpage.write('<hr /><h3>Errors from the last 24 Hours</h3><hr />')
    writeJobRecords('ERROR',True,webpage,config,filter(
      lambda job: job.startTime > yesterday \
                  and job.isComplete() \
                  and not job.isSuccess() , 
      records.values()
      ) 
    )

    # print long running jobs
    webpage.write('<hr /><h3>Long Running Jobs (> %s s)</h3><hr />' 
                  % config['AUTOCMS_RUNTIME_WARNING'] )
    writeJobRecords('WARNING',False,webpage,config,filter(
      lambda job: job.startTime > yesterday \
                  and job.isComplete() \
                  and job.isSuccess() \
                  and job.runTime() > config['AUTOCMS_RUNTIME_WARNING'], 
      records.values()
      ) 
    )

    # print successful jobs (not long running) if requested
    if int(config['AUTOCMS_PRINT_SUCCESS']) == 1:
      webpage.write('<hr /><h3>Successful Jobs</h3><hr />' )
      writeJobRecords('SUCCESS',False,webpage,config,filter(
        lambda job: job.startTime > yesterday \
                    and job.isComplete() \
                    and job.isSuccess() \
                    and job.runTime() <= config['AUTOCMS_RUNTIME_WARNING'],
        records.values()
        )
      )

  os.rename(newWebpageName,webpageName)  

def writeWebpageHeader(webpage,config):
    webpage.write(
"""\
<html><head><title>%s Internal Site Test: %s</title></head>
<body>
<h2>%s Internal Site Test: %s</h2>
</body>""" % ( config['AUTOCMS_SITE_NAME'], 
               config['AUTOCMS_TEST_NAME'], 
               config['AUTOCMS_SITE_NAME'], 
               config['AUTOCMS_TEST_NAME'] )
    )

def writeJobRecords(header,showError,webpage,config,records):
  counter = 1
  records.sort(key=lambda x: x.startTime, reverse=True)
  for job in records:
    webpage.write('<b>%s</b> %d: <br />\n' % (header, counter) )
    webpage.write('  Start time: %s <br />\n' % 
                    datetime.datetime.fromtimestamp(
                      job.startTime
                    ).strftime('%Y-%m-%d %H:%M:%S')
                 )
    webpage.write('  Node Name: %s <br />\n' % job.node )
    webpage.write('  Input File: %s <br />\n' % job.inputFile )
    if showError:
      webpage.write('  Error Type: %s <br />\n' % job.errorString )
    webpage.write('  Log File: <a href="%s">%s</a> <br />\n ' %
                  ( job.logFile+".txt",job.logFile+".txt") )
    webpage.write('<hr />\n')
    counter += 1

main()
