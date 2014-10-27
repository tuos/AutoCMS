import os
import re
import shutil
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
  
  yesterday = int(time.time()) - 24 * 3600

  # build new webpage
  with open(newWebpageName,'w') as webpage:

    #header 
    writeWebpageHeader(webpage,config) 

    #plots

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

    webpage.write( '</div><hr />\n' )

    # description and statistics
    writeTestDescription(webpage,config)  
    writeJobStatistics(webpage,config,records)

    # start a list of jobs to be printed
    # whose logs will be copied to the webdir
    printedJobs = list()

    # print failed jobs from last 24 hours, add them to the list
    webpage.write('<h3>Errors from the last 24 Hours</h3><hr />')
    printedJobs = printedJobs + \
    writeJobRecords('<b>ERROR</b>',True,webpage,config,filter(
      lambda job: job.startTime > yesterday \
                  and job.isComplete() \
                  and not job.isSuccess() , 
      records.values()
      ) 
    )

    # print long running jobs, add them to the list
    webpage.write('<h3>Long Running Jobs (> %s s)</h3><hr />' 
                  % config['AUTOCMS_RUNTIME_WARNING'] )
    printedJobs = printedJobs + \
    writeJobRecords('Warning',False,webpage,config,filter(
      lambda job: job.startTime > yesterday \
                  and job.isComplete() \
                  and job.isSuccess() \
                  and job.runTime() > config['AUTOCMS_RUNTIME_WARNING'], 
      records.values()
      ) 
    )

    # print successful jobs (not long running) if requested, add them to the list
    if int(config['AUTOCMS_PRINT_SUCCESS']) == 1:
      webpage.write('<h3>Successful Jobs</h3><hr />' )
      printedJobs = printedJobs + \
      writeJobRecords('Success',False,webpage,config,filter(
        lambda job: job.startTime > yesterday \
                    and job.isComplete() \
                    and job.isSuccess() \
                    and job.runTime() <= config['AUTOCMS_RUNTIME_WARNING'],
        records.values()
        )
      )

    # close body and html tags
    webpage.write('</body></html>')

  # copy logs for printed jobs
  for subTime in printedJobs:
    srcFile = testdir+"/"+records[subTime].logFile
    destFile = config['AUTOCMS_WEBDIR']+"/"+records[subTime].logFile+".txt"
    if os.path.isfile(srcFile):
      shutil.copyfile(srcFile, destFile)

  # get rid of other logs in the webdir
  logsToKeep = list()
  for subTime in printedJobs:
    logsToKeep.append( records[subTime].logFile+".txt" )
  for logFile in filter(lambda x:re.search(r'.pbs.o[0-9]+.txt', x), 
                        os.listdir(config['AUTOCMS_WEBDIR'])): 
    if logFile not in logsToKeep:
      os.remove(config['AUTOCMS_WEBDIR']+"/"+logFile)

  os.rename(newWebpageName,webpageName)  

def writeWebpageHeader(webpage,config):

    webpage.write(
"""\
<html><head><title>%s Internal Site Test: %s</title></head>
<body>
<h2>%s Internal Site Test: %s</h2>
Page generated at: %s
<hr />""" % ( config['AUTOCMS_SITE_NAME'], 
              config['AUTOCMS_TEST_NAME'], 
              config['AUTOCMS_SITE_NAME'], 
              config['AUTOCMS_TEST_NAME'],
              time.strftime("%c") )
    )

def writeTestDescription(webpage,config):
  dFile = config['AUTOCMS_BASEDIR']+"/"+config['AUTOCMS_TEST_NAME']+".description.html"
  if os.path.isfile(dFile):
    with open(dFile) as descriptionIn:
      description = descriptionIn.read()
    webpage.write(description+"<hr />")
  else:
    webpage.write("No test description found.<br /><hr />")

def writeJobStatistics(webpage,config,records):
  
  yesterday = int(time.time()) - 24 * 3600
  threehours = int(time.time()) - 3 * 3600
  
  failed24hour = sum( 1 for job in records.values() if not job.isSuccess() 
                      and job.startTime > yesterday )
  webpage.write("Failed jobs in the last 24 hours: %d <br />\n" % failed24hour)

  failed3hour = sum( 1 for job in records.values() if not job.isSuccess() 
                     and job.startTime > threehours )
  webpage.write("Failed jobs in the last 3 hours: %d <br />\n" % failed3hour)
  webpage.write("<br />\n")

  long24hour = sum( 1 for job in records.values() if job.isSuccess() 
                    and job.startTime > yesterday 
                    and job.runTime() > 3600 )
  webpage.write("Long running jobs (> %s s) in the last 24 hours: %d <br />\n" 
                % (config['AUTOCMS_RUNTIME_WARNING'],long24hour) )

  long3hour = sum( 1 for job in records.values() if job.isSuccess() 
                   and job.startTime > threehours  
                   and job.runTime() > 3600 )
  webpage.write("Long running jobs (> %s s) in the last 3 hours: %d <br />\n" 
                % (config['AUTOCMS_RUNTIME_WARNING'],long3hour) )
  webpage.write("<br />\n")

  success24hour = sum( 1 for job in records.values() if job.isSuccess() 
                      and job.startTime > yesterday )
  webpage.write("Successful jobs in the last 24 hours: %d <br />\n" % success24hour)

  success3hour = sum( 1 for job in records.values() if job.isSuccess() 
                     and job.startTime > threehours )
  webpage.write("Successful jobs in the last 3 hours: %d <br />\n" % success3hour)
  webpage.write("<br />\n")
 
  webpage.write("<hr />\n") 

# This function writes out the properties of a 
# completed job to a file in HTML, and then returns
# a list of startTimes for the jobs it wrote
def writeJobRecords(header,showError,webpage,config,records):
  counter = 1
  records.sort(key=lambda x: x.startTime, reverse=True)
  for job in records:
    webpage.write('%s %d: <br />\n' % (header, counter) )
    webpage.write('  Start time: %s <br />\n' % 
                    datetime.datetime.fromtimestamp(
                      job.startTime
                    ).strftime('%c')
                 )
    webpage.write('  Node Name: %s <br />\n' % job.node )
    webpage.write('  Input File: %s <br />\n' % job.inputFile )
    if showError:
      webpage.write('  Error Type: %s <br />\n' % job.errorString )
    if job.logFile != "N/A":
      webpage.write('  Log File: <a href="%s">%s</a> <br />\n ' %
                    ( job.logFile+".txt",job.logFile+".txt") )
    webpage.write('<hr />\n')
    counter += 1

  return [x.submitTime for x in records]      


main()
