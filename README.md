# AutoCMS: Testing and Monitoring System

[![Travs-CI status](https://travis-ci.org/appeltel/AutoCMS.png)](https://travis-ci.org/appeltel/AutoCMS)

![Example AutoCMS Plot](docs/snapshot/runtime.png)

AutoCMS is a simple python-based system for regularly submitting 
and monitoring the results of arbitrarily complex test jobs to a computing
cluster. You can see the capabilities of the system in this 
[snapshot](docs/snapshot/index.html) of a generated AutoCMS webpage
from an actual test.

AutoCMS is not officially an acronym for anything, but you may think of it 
as Automatic Cluster Monitoring System. 

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

## Requirements

1. Linux cluster with batch scheduler system, currently only 
[SLURM](http://slurm.schedmd.com/) is supported, tested using 
version 14.11.6

2. Python 2.7, tested using version 2.7.8

3. [Pandas](http://pandas.pydata.org/) version 0.15 or later,
tested using version 0.15.2

4. User access to cron utility, a web-accessible directory with 
write privileges, authorization to submit a small number of 
short jobs at regular intervals.

5. Rudimentary knowledge of bash

## Quickstart

This quickstart will guide you to set up a bare-bones example
of the AutoCMS system running a simple mock-up of a scientific 
application that often fails. One can then replace this mock-up
with their own application to be tested on the cluster.

1. Clone or download AutoCMS into a directory to be used as your 
AutoCMS base directory.  

2. Copy the file `autocms.cfg.bare` to `autocms.cfg`

3. Using the editor of your choice, edit `autocms.cfg` to change
the following variables:

    * `AUTOCMS_BASEDIR` should be the absolute path to the directory where you have cloned the repostory

    * `AUTOCMS_CONFIGFILE` should be the absolute path to the `autocms.cfg` file, including the file name itself

    * `AUTOCMS_WEBDIR` should be the absolute path to a web-accessible directory where AutoCMS will create subdirectories, and manage files within those subdirectories
 
    * `AUTOCMS_UNAME` should be your system user name that you will submit jobs to the scheduler as

    * `AUTOCMS_GNAME` should be the group or account that you will use to submit jobs to the scheduler

    * `AUTOCMS_SITE_NAME` should be the name of your cluster

4. Run `./autocms.sh print` to produce the crontab listing needed to run the 
bare-bones test at regular intervals, harvest the output logs, and report to 
the web page.

5. Add the printed lines to your crontab, or if you do not have an 
active crontab, run `crontab autocms.crontab` to add the lines. Make sure
that you are logged into the gateway node that you want AutoCMS jobs
to be submitted from. The system is now running.

6. Wait about 30 minutes for jobs to run and the webpage to be generated,
maybe get a cup of coffee?

7. Test results should be generated with the webpage available at 
`$AUTOCMS_WEBDIR/bare_test/index.html`

## Further Documentation

* [Creating and Running Tests](docs/tests.md)

* [AutoCMS Tokens](docs/tokens.md)

* [Customizing AutoCMS Reporting](docs/custom.md)

* [Troubleshooting](docs/troubleshooting.md)

* [Vanderbilt Site Instructions](docs/vanderbilt.md)
