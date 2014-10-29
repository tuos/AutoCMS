import re 
import os
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


# Right now graphics are only used by the reporter, but
# other scripts could potentially use them

def createRunAndWaitTimePlot(outputFileName,logScale,records):

  #create data file to send to gnuplot
  dataFileName = outputFileName+'.data'
  with open(dataFileName,'w') as dataFile:
    for job in records:
      print >>dataFile, '%d %d %d' % (job.startTime,job.waitTime(),job.runTime())

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
  plot '%s' using 1:2 title "Waiting Time", \
       '%s' using 1:3 title "Running Time"
EOF""" % ( outputFileName, logScaleString, dataFileName, dataFileName )
  ) 

  os.remove(dataFileName) 
