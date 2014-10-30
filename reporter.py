import os
import sys
import re
import shutil
import time
import datetime
import cPickle as pickle
from JobRecord import JobRecord
import AutoCMSUtil

# load configuration, determine test, and enter test directory
config = AutoCMSUtil.LoadConfiguration('autocms.cfg')
config['AUTOCMS_TEST_NAME'] = sys.argv[1]
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

# build new webpage using custom module for the test (if it exists)
# or the default page builder module
customWebPageBuilderModule = config['AUTOCMS_BASEDIR']+"/"+config['AUTOCMS_TEST_NAME']+"WebPageBuilder.py"
if os.path.isfile(customWebPageBuilderModule):
  WebPageBuilder = __import__(config['AUTOCMS_TEST_NAME']+"WebPageBuilder")
else:
  WebPageBuilder = __import__("WebPageBuilder")

printedJobs = WebPageBuilder.build(newWebpageName,config,records)

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
for logFile in filter(lambda x:re.search('%s.pbs.o[0-9]+.txt' % config['AUTOCMS_TEST_NAME'], x), 
                      os.listdir(config['AUTOCMS_WEBDIR'])): 
  if logFile not in logsToKeep:
    os.remove(config['AUTOCMS_WEBDIR']+"/"+logFile)

os.rename(newWebpageName,webpageName)  
