# AutoCMS: Testing and Monitoring System

AutoCMS is a simple python-based system for regularly submitting 
and monitoring the results of arbitrarily complex test jobs to a computing
cluster. 

AutoCMS is not officially an acronym for anything, but you may think of it 
as Automatic Cluster Monitoring System if you like. 

## Purpose and History

AutoCMS was originally written as a collection of bash scripts to test 
the performance of the 
[Vanderbilt ACCRE](http://www.accre.vanderbilt.edu/) facility
when running physics analysis code with a complex set of dependencies 
for the [Compact Muon Solenoid](http://cms.web.cern.ch/) (CMS) collaboration
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

AutoCMS works by regularly scheduling submission, harvesting, and reporting
modules to run through cron.

1. The submission module submits one or more jobs to the cluster scheduler
and produces a small one line "submission stamp" file with the submission
time, expected location of the standard output log of the job, and the 
id number that the scheduler assigns to the job. If the job submission fails,
the output of the submission process is logged.

2. The harvesting module looks for submission stamp files and coallates 
each new submission stamp into a single file. A list of tracked jobs is 
determined from the stamps, and the scheduler is queried to determine 
what jobs have completed. The output logs of the completed jobs are parsed
and the results stored in a list of job records, which is written to 
a file. 

3. The statistics module reads the list of job records and 
creates a permanent record of overall statistics for the previous 
n hours.
 
4. The reporting module reads the list of job records produced by the 
harvesting module as well as the permanent record from the statistics 
module and builds a configurable web page with plots and 
statistics indicating job performance. Output logs of failed or otherwise
notable jobs are copied to a web accessible location and linked to 
from the web page.

Different tests may be configured by creating a subdirectory for each test
and run at indpendent intervals. None of the different 
modules write to the same file, so they may be run in parallel or in 
principle from different nodes.

 
