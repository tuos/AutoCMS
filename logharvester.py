import os
import re
import time
import cPickle as pickle
from JobRecord import JobRecord
import AutoCMSUtil

# load configuration and enter test directory
config = AutoCMSUtil.LoadConfiguration('autocms.cfg')
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
  jobid = line.split()[0].replace('.vmpsched','')
  timestamp = int(line.split()[1])
  submitStatus = line.split()[2]
  if now - timestamp < 60*60*24 :
    if timestamp not in records:
      records[timestamp] = JobRecord(timestamp,jobid,submitStatus)
  if timestamp < purgetime:
    stampsIn.remove(line) 

stampFile = open('submission.stamps','w') 
for line in stampsIn:
  print>>stampFile, line
stampFile.close()

# Harvest information from log for jobs not yet 
# known to be completed
for job in records:
  if not records[job].isComplete():
    jobLogFile = config['AUTOCMS_TEST_NAME']+'.pbs.o'+str(records[job].jobid)
    if os.path.isfile(jobLogFile):
      records[job].parseOutput(jobLogFile)

# Remove old log files
for logFileName in filter(lambda x:re.search(r'.pbs.o[0-9]+', x), os.listdir('.')):
  if int(os.path.getctime(logFileName)) < purgetime :
    os.remove(logFileName)

# save logharvester state
pickle.dump( records, open( autocms_pkl, "wb" ) )
