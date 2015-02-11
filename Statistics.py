import re 
import os
import time
from JobRecord import JobRecord
import AutoCMSUtil

# This harvests a single row of data for jobs completed in the last X 
# hours, where X is given by the configuration option 'AUTOCMS_STAT_INTERVAL'.
#
# The default format is as follows:
#
# (timestamp) (# successes) (# failures) (min runtime) (mean runtime) (max runtime)
#
# The harvest function can be overridden for a test by creating 
# a Statistics.py file in the test directory with an alternate 
# harvest function.

def harvest(config,records):

  now = int(time.time())
  harvestTime = now - int(config['AUTOCMS_STAT_INTERVAL']) * 3600 

  statrecords =  filter(
                          lambda job: job.endTime > harvestTime \
                          and job.isComplete() ,
                          records.values()
                       )
  successes = 0
  failures = 0
  minRuntime = 999999999.0
  meanRuntime = 0.0
  maxRuntime = 0.0
  
  for job in statrecords:
  
    if( job.isSuccess() ):
      successes += 1
      runtime = job.endTime - job.startTime
      if( runtime > maxRuntime):
        maxRuntime = runtime
      if( runtime < minRuntime):
        minRuntime = runtime
      meanRuntime += runtime
    else:
      failures += 1
 
  if( successes == 0 ):
    minRuntime = 0 
  meanRuntime /= float(successes)

  return "%d %d %d %f %f %f" % ( now, successes, failures, minRuntime, meanRuntime, maxRuntime ) 
