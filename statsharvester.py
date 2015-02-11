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

# harvest statistics using custom module for the test (if it exists)
# or the default daily statistics module
customStatisticsModule = config['AUTOCMS_BASEDIR']+"/"+config['AUTOCMS_TEST_NAME']+"/Statistics.py"
if os.path.isfile(customStatisticsModule):
  AutoCMSStatistics = __import__(config['AUTOCMS_TEST_NAME']+".Statistics",
                                     globals(), locals(), ['Statistics'], -1)
else:
  AutoCMSStatistics = __import__("Statistics")

newStats = AutoCMSStatistics.harvest(config,records)

#newStatFileName = config['AUTOCMS_TEST_NAME']+'/statistics.dat.new'
statFileName = 'statistics.dat'

with open(statFileName,'a+') as statFile:
 print>>statFile,newStats 

#os.rename(newStatFileName,statFileName)  
