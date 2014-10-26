import os
import time
import cPickle as pickle
import JobRecord
import AutoCMSUtil

# load configuration and enter test directory
config = AutoCMSUtil.LoadConfiguration("autocms.cfg")
testdir = config['AUTOCMS_BASEDIR']+"/"+config['AUTOCMS_TEST_NAME']
os.chdir(testdir)

# initialize JobRecord dictionary, or load saved state
autocms_pkl = "records.pickle"
if os.path.isfile(autocms_pkl):
  records = pickle.load( open(autocms_pkl, "rb") )
else:
  records = dict()

# create new entries for jobs submitted today, but not 
# found in the dictionary
now = int(time.time())
with open('submission.stamps','r') as stampFile:
  

