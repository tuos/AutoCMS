# AutoCMS: Testing and Monitoring System

AutoCMS is a simple python-based system for regularly submitting 
and monitoring the results of arbitrarily complex test jobs to a computing
cluster. 

AutoCMS is not officially an acronym for anything, but you may think of it 
as Automatic Cluster Monitoring System if you like. 

## Purpose and History

AutoCMS was originally written as a collection of bash scripts to test 
the performance of the 
[Vanderbilt ACCRE facilty](http://www.accre.vanderbilt.edu/)
when running physics analysis code with a complex set of dependencies 
for the [Compact Muon Solenoid (CMS) collaboration](http://cms.web.cern.ch/)
which would also interface with the [LStore](http://www.lstore.org/)
logistical storage framework under development at ACCRE.

In order to understand complex or infrequent failure modes, a tool was 
needed which would continually submit small test jobs using the 
full software dependencies. In addition, the output logs of any failed 
or poorly performing tests needed to be easily accessible, and the 
parameters of the test itself needed to be easily modifiable through 
directly rewriting the submission script to the scheduler.

AutoCMS was hastily written to fulfill these requirements, and subsequently 
reengineered to be able to be applied to any specialized software that 
would be scheduled on a given computing facility, and to analyze and 
report any application specific statistics about these tests.

## The AutoCMS Workflow

 
