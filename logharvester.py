import sys
import os
import re
import time
import cPickle as pickle
from JobRecord import JobRecord
import AutoCMSUtil

# load configuration, determine test, and enter test directory
config = AutoCMSUtil.LoadConfiguration('autocms.cfg')
config['AUTOCMS_TEST_NAME'] = sys.argv[1]
testdir = config['AUTOCMS_BASEDIR']+"/"+config['AUTOCMS_TEST_NAME']
os.chdir(testdir)

# set current time, and timestamp before which old
# logs and stamps will be purged
now = int(time.time())
if int(config['AUTOCMS_LOG_LIFETIME']) > 0:
  purgetime = now - 3600 * 24 * int(config['AUTOCMS_LOG_LIFETIME'])
else:
  purgetime = now - 3600 * 24 * 7

# initialize JobRecord dictionary, or load saved state
autocms_pkl = 'records.pickle'
if os.path.isfile(autocms_pkl):
  records = pickle.load( open(autocms_pkl, "rb") )
else:
  records = dict()

# create new entries for jobs submitted today, but not 
# found in the dictionary, delete old stamps
#
# note: to avoid locking and race conditions, the submitter 
# creates new stamps in files of the form "newstamp.1414308601"
# containing the jobid and timestamp. These are 
# addded to the "submission.stamps" file and removed 
# only by this script, which also removes old stamps from the 
# file. 
#
with open('submission.stamps','a') as stampFile:
  for newStampFileName in filter(lambda x:re.match(r'newstamp', x), os.listdir('.')):
    with open(newStampFileName,'r') as newStampFile:
      newStamp = newStampFile.read().strip()
    print>>stampFile, newStamp
    os.remove(newStampFileName)
with open('submission.stamps','r') as stampFile:
  stampsIn = stampFile.read().splitlines()
for line in stampsIn[:]:
  # for some reason slurm is not always reporting a job number, so skip lines 
  # that have less than three columns (i.e. no job number, timestamp, or exit code)
  if len(line.split()) > 2 :
    jobid = line.split()[0].replace('.vmpsched','')
    timestamp = int(line.split()[1])
    submitStatus = line.split()[2]
    if timestamp not in records:
      records[timestamp] = JobRecord(timestamp,jobid,submitStatus)
      # add submission log for failed submissions
      if int(submitStatus) != 0 and len(line.split()) > 3:
        records[timestamp].logFile = line.split()[3]
    if timestamp < purgetime:
      stampsIn.remove(line) 

stampFile = open('submission.stamps','w') 
for line in stampsIn:
  print>>stampFile, line
stampFile.close()

# get a list of jobs completed in the 
# last 24-48 hours from this account, 
# then updated jobs not completed, and attempt to
# parse their logs if they exist
completedJobs = AutoCMSUtil.getCompletedJobs(config)
for job in records:
  if not records[job].isCompleted:
    if records[job].jobid in completedJobs:
      records[job].isCompleted = True
      jobLogFile = config['AUTOCMS_TEST_NAME']+'.slurm.o'+str(records[job].jobid)
      if os.path.isfile(jobLogFile):
        records[job].parseOutput(jobLogFile,config)
      else:
        records[job].exitCode = 1
        records[job].errorString = "ERROR standard output of this job was not found."

# Remove old log files and job records
for logFileName in filter(lambda x:re.search(r'.slurm.o[0-9]+', x), os.listdir('.')):
  if int(os.path.getctime(logFileName)) < purgetime :
    os.remove(logFileName)
oldRecords = list()
for job in records.keys():
  if job < purgetime:
    oldRecords.append(job)
for job in oldRecords:
  del records[job]

# debug - print record status
if '--debug' in sys.argv[1:]:
  for job in records:
    records[job].printDebug()
    print

# save logharvester state
pickle.dump( records, open( autocms_pkl, "wb" ) )
