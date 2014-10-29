import re

class JobRecord:
  'information about a specific AutoCMS job'

  def __init__(self, timestamp, jobid, submitStatus):
    self.submitTime = int(timestamp)
    self.jobid = jobid
    self.submitStatus = int(submitStatus) 
    if self.submitStatus == 0 :
      self.node = "N/A"    
      self.startTime = 0
      self.endTime = 0
      self.exitCode = 255
      self.errorString = "Job did not report success."
      self.inputFile = "N/A"
      self.logFile = "N/A"    
    else:
      self.node = "N/A"    
      self.startTime = self.submitTime
      self.endTime = self.submitTime
      self.exitCode = submitStatus
      self.errorString = "ERROR in job submission code "+str(submitStatus)
      self.inputFile = "N/A"
      self.logFile = "N/A" 
      

  def runTime(self):
    return self.endTime - self.startTime

  def waitTime(self):
    return self.startTime - self.submitTime

  def isSuccess(self):
    if self.exitCode == 0:
      return True
    else:
      return False

  def isComplete(self):
    if self.startTime != 0:
      return True
    else:
      return False

  def parseOutput(self,logFileName,config):
    self.logFile = logFileName
    with open(logFileName,'r') as logFile:
      log = logFile.read().splitlines()
    for line in log:
      for setting in config.keys():
        if( re.match(r'AUTOCMS_.*_TOKEN',setting) ):
          if( re.match(config[setting],line) ):
            recordAttrName = setting.replace('AUTOCMS_','').replace('_TOKEN','') 
            recordAttrValue = line.replace(config[setting],'')
            if recordAttrName == 'SUCCESS':
              self.exitCode = 0
            else:
              setattr(self,recordAttrName,recordAttrValue) 
    # ensure that required attributes remain ints
    self.exitCode = int(self.exitCode)
    self.startTime = int(self.startTime)
    self.endTime = int(self.endTime)             
#      if( re.match(r'timestamp_begin=',line)):
#        self.startTime = int(line.replace('timestamp_begin=',''))
#      if( re.match(r'timestamp_end=',line)):
#        self.endTime = int(line.replace('timestamp_end=',''))
#      if( re.match(r'SKIM_TEST: Running on node',line)):
#        self.node = line.replace('SKIM_TEST: Running on node ','')
#      if( re.match(r'SKIM_TEST: Will use input file ',line)):
#        self.inputFile = line.replace('SKIM_TEST: Will use input file ','')
#      if( re.search(r'ALL TESTS SUCCESSFUL',line)):
#        self.exitCode = 0 
#      if( re.match(r'SKIM_TEST:.*ERROR',line)):
#        self.errorString = line.replace('SKIM_TEST: ','')

  def printDebug(self):
    print "Job Record: "+str(self.submitTime)
    print "  pbs id: "+str(self.jobid) 
    print "  submission status: "+str(self.submitStatus)
    if self.isComplete():
      print "  This is a completed job"
      print "  cluster node: "+str(self.node)
      print "  start time: "+str(self.startTime)
      print "  end time: "+str(self.endTime)
      print "  exit code: "+str(self.exitCode)
      print "  input file: "+str(self.inputFile)
      print "  log file: "+str(self.logFile)
      if self.isSuccess():
        print "  This job succeeded."
      else:
        print self.errorString
