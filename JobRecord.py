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
      self.logFile = "N/A"    
    else:
      self.node = "N/A"    
      self.startTime = self.submitTime
      self.endTime = self.submitTime
      self.exitCode = submitStatus
      self.errorString = "ERROR in job submission code "+str(submitStatus)
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
    # if starttime is still zero, set to the submitTime        
    if self.startTime == 0 : 
      self.startTime = self.submitTime
    # if endTime is still zero, set to startTime
    if self.endTime == 0 :
      self.endTime = self.startTime

  def printDebug(self):
    print 'JobRecord id %d:' % self.submitTime
    for attr in dir(self):
      if not hasattr(getattr(self,attr), '__call__'):
        print '  %s: %s' % (attr, str(getattr(self,attr)))
