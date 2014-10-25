class JobRecord:
  'information about a specific AutoCMS job'

  def __init__(self, timestamp, jobid):
    self.submitTime = timestamp
    self.jobid = jobid

    self.node = None    
    self.startTime = None
    self.endTime = None
    self.exitCode = None
    self.errorString = None
    
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
    if self.startTime is not None and self.endTime is not None:
      return True
    else:
      return False

 
