import re 
import os
import time
import datetime
import subprocess
from JobRecord import JobRecord

def LoadConfiguration(configFileName):

  config = dict()

  with open(configFileName,'r') as configFile:
    configIn = configFile.read().splitlines()

  for line in configIn:
    if( re.match(r'export',line) ):
      varKey = line.split('=')[0]
      varKey = varKey.replace("export","")
      varKey = varKey.strip()
      varValue = varValue = line.split('=')[1]
      varValue = varValue.strip()
      varValue = varValue.strip('"')
      config[varKey] = varValue

  return config


# basic plot used by the default WebBuilder

def createRunAndWaitTimePlot(outputFileName,logScale,records):

  #find utc offset
  utcoffset = int(round((datetime.datetime.now() - datetime.datetime.utcnow()).total_seconds()))

  #create data file to send to gnuplot
  dataFileName = outputFileName+'.data'
  with open(dataFileName,'w') as dataFile:
    for job in records:
      print >>dataFile, '%d %d %d' % (job.startTime+utcoffset,job.waitTime(),job.runTime())

  if logScale:
    logScaleString = 'set logscale y'
  else:
    logScaleString = ''

  # make the plot
  # note: gnuplot needs to be compiled with 
  # png terminal support.
  os.system(
"""\
gnuplot <<- EOF
  set terminal png crop enhanced  size 750,350 
  set output "%s"
  set xlabel "timestamp (recent 24 hours)"
  set ylabel "time (s)"
  set xdata time
  set timefmt "%%s"
  set xtics 14400
  set format x "%%a %%H:%%M"
  #set yrange [0:1000]
  %s
  #set xtics border nomirror in rotate by -45 offset character 0, 0, 0
  set style line 1 lc rgb 'red' pt 5 ps 0.7  # square
  set style line 2 lc rgb 'green' pt 5 ps 0.7  # square
  plot '%s' using 1:2 title "Waiting Time" ls 1, \
       '%s' using 1:3 title "Running Time" ls 2
EOF""" % ( outputFileName, logScaleString, dataFileName, dataFileName )
  ) 

  os.remove(dataFileName) 


def createHistogram(outputFileName,binWidth,xtit,ytit,attr,records):

  # make a 1-column data file of the attr for records that have it
  dataFileName = outputFileName+'.data'
  with open(dataFileName,'w') as dataFile:
    for job in filter( lambda job: hasattr(job,attr) , records ):
      print >>dataFile, '%f' % float(getattr(job,attr))

  # make the plot
  # found this trick at http://www.inference.phy.cam.ac.uk/teaching/comput/C++/examples/gnuplot/#two
  os.system(
"""\
gnuplot <<- EOF
set terminal png crop enhanced  size 500,350 
set output "%s"
set ylabel "%s"
set xlabel "%s"
set offset graph 0.1, graph 0.1, graph 0.1, graph 0.0
bin_width = %f; 
bin_number(x) = floor(x/bin_width)
rounded(x) = bin_width * ( bin_number(x) + 0.5 )
UNITY = 1
set style line 1 lt 1 lw 2 pt 2 linecolor rgb "red"
plot '%s' u (rounded(\$1)):(UNITY) smooth frequency w histeps notitle ls 1
unset xlabel
unset ylabel
EOF""" % ( outputFileName,ytit,xtit,binWidth,dataFileName )
  ) 

  os.remove(dataFileName)

# This function writes out the properties of a 
# completed job to a file in HTML, and then returns
# a list of startTimes for the jobs it wrote
def writeJobRecords(header,webpage,config,records,**extraAttrs):
  counter = 1
  records.sort(key=lambda x: x.startTime, reverse=True)
  for job in records:
    webpage.write('%s %d: <br />\n' % (header, counter) )
    webpage.write('  Start time: %s <br />\n' % 
                  time.strftime('%c (%Z)', time.localtime(job.startTime))
                 )
    webpage.write('  Node Name: %s <br />\n' % job.node )
    if job.logFile != "N/A":
      webpage.write('  Log File: <a href="%s">%s</a> <br />\n ' %
                    ( job.logFile+".txt",job.logFile+".txt") )
    for attr,text in extraAttrs.iteritems():
      if hasattr(job,attr):
        webpage.write('  %s: %s <br />\n' % (text,getattr(job,attr) ) )

    webpage.write('<hr />\n')
    counter += 1

  return [x.submitTime for x in records] 


def beginWebpage(webpage,config):

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
              time.strftime("%c (%Z)") )
    )

def endWebpage(webpage,config):
 
  webpage.write('</body></html>')


def writeTestDescription(webpage,config):
  dFile = config['AUTOCMS_BASEDIR']+"/"+config['AUTOCMS_TEST_NAME']+"/description.html"
  if os.path.isfile(dFile):
    with open(dFile) as descriptionIn:
      description = descriptionIn.read()
    webpage.write(description + '<br /><br />')
  else:
    webpage.write("No test description found.<br /><br />")


def writeBasicJobStatistics(webpage,config,records):

  yesterday = int(time.time()) - 24 * 3600
  threehours = int(time.time()) - 3 * 3600

  failed24hour = sum( 1 for job in records.values() if not job.isSuccess()
                      and job.startTime > yesterday )
  webpage.write("Failed jobs in the last 24 hours: %d <br />\n" % failed24hour)

  failed3hour = sum( 1 for job in records.values() if not job.isSuccess()
                     and job.startTime > threehours )
  webpage.write("Failed jobs in the last 3 hours: %d <br />\n" % failed3hour)
  webpage.write("<br />\n")


  success24hour = sum( 1 for job in records.values() if job.isSuccess()
                      and job.startTime > yesterday )
  webpage.write("Successful jobs in the last 24 hours: %d <br />\n" % success24hour)

  success3hour = sum( 1 for job in records.values() if job.isSuccess()
                     and job.startTime > threehours )
  webpage.write("Successful jobs in the last 3 hours: %d <br />\n" % success3hour)
  webpage.write("<br />\n")
 
  # only print success rates if jobs have actually run

  if success24hour + failed24hour > 0 :
    successRate24 = float(100 * success24hour) / float(success24hour + failed24hour)
    if successRate24 < 90.0 :
      webpage.write('Success rate (24 hours): <span style="color:red;">%.2f %%</span><br />\n' % successRate24)
    else:
      webpage.write('Success rate (24 hours): %.2f %%<br />\n' % successRate24)

  if success3hour + failed3hour > 0 :
    successRate3 = float(100 * success3hour) / float(success3hour + failed3hour)
    if successRate3 < 90.0 :
      webpage.write('Success rate (3 hours): <span style="color:red;">%.2f %%</span><br />\n' % successRate3)
    else:
      webpage.write('Success rate (3 hours): %.2f %%<br />\n' % successRate3)

  webpage.write("<br />\n")

def listNodesByErrors(webpage,config,records):
  yesterday = int(time.time()) - 24 * 3600
  badNodes = dict()
  for job in records.values():
    if job.isComplete() and not job.isSuccess() and job.startTime > yesterday :
      if job.node in badNodes:
        badNodes[job.node] += 1 
      else:
        badNodes[job.node] = 1

  for node in sorted(badNodes, key=badNodes.get, reverse=True):
    webpage.write("%s - %s<br />" % (badNodes[node],node))

def listErrorsByReason(webpage,config,records):
  yesterday = int(time.time()) - 24 * 3600
  errorMsgs = dict()
  for job in records.values():
    if job.isComplete() and not job.isSuccess() and job.startTime > yesterday :
      if job.errorString in errorMsgs:
        errorMsgs[job.errorString] += 1
      else:
        errorMsgs[job.errorString] = 1

  for message in sorted(errorMsgs, key=errorMsgs.get, reverse=True):
    webpage.write("%s - %s<br />" % (errorMsgs[message],message))

def getCompletedJobs(config):
  cmd = '/usr/scheduler/slurm/bin/sacct --state=CA,CD,F,NF,TO -S $(date +%%Y-%%m-%%d -d @$(( $(date +%%s) - 172800 )) ) --accounts=%s --user=%s -n -o "jobid" | grep -e "^[0-9]* "' % ( config['AUTOCMS_GNAME'], config['AUTOCMS_UNAME'] )
  result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
  lines = result.stdout.readlines()
  lines = map(str.strip,lines)
  return lines
