# Creating and Running AutoCMS Tests

AutoCMS can be configured to run and report on 
multiple different tests simultaneously, or to run a single 
test. New tests can be created from the examples provided.

## Creating New Tests

A test is created by making a subdirectory with the name of the test 
within the AutoCMS base directory. For example, the pre-made tests 
`bare_test` and `example_test` are included in the AutoCMS distribution.

For a test with name *some_test*, AutoCMS will submit the script 
$AUTOCMS_BASEDIR/*some_test*/*some_test*.*scheduler_name*, where 
*scheduler_name* is the name of the scheduler set by the 
$AUTOCMS_SCHEDULER variable. So if the test to be executed is 
`example_test` and the scheduler is `slurm`, the script 
$AUTOCMS_BASEDIR/example_test/example_test.slurm will be executed.

AutoCMS provides a counter available to the submitted script as the 
environment variable $AUTOCMS_COUNTER which is incremented for each 
submission. This value can be used to seed a random number generator,
select a file from a list, or generally be used to customize each test
if desired.

A running test is considered successful if and only if the 
value of $AUTOCMS_SUCCESS_TOKEN is printed to standard output of the 
job log. AutoCMS will parse the output log to look for this and 
a number of other tokens to determine the job start time, end time,
appropriate exit code, and reason for any error. See the 
[tokens section](tokens.md) for more details.

A description of the test should be given in the file 
$AUTOCMS_BASEDIR/*some_test*/description.html. This description
will be added to the generated web page with the test results.

The [bare_test.slurm](../bare_test/bare_test.slurm) and 
[example_test.slurm](../example_test/example_test.slurm) scripts 
can be used as templates to write new test scripts.

## Running Various Tests

Which tests are to be run are controlled by the AUTOCMS_TEST_NAMES 
configuration variable, which should be set to a ':' delimited list
of tests to be run. For example, to run both `bare_test` and 
`example_test`, set `AUTOCMS_TEST_NAMES=example_test:bare_test`. To run 
just `bare_test`, set `AUTOCMS_TEST_NAMES=bare_test` in the 
`autocms.cfg` file.

The number of minutes to wait between each batch of test jobs is given by 
AUTOCMS_TEST_SUBWAITS which should be an integer if one test is to be 
run or a ':' delimited list of integers for multiple tests. The order 
of tests should be the same as in AUTOCMS_TEST_NAMES. The number
of test jobs to submit in each batch is similarly determined 
by AUTOCMS_TEST_SUBCOUNTS which should also be a ':' delimited list of 
integers.

Changing the tests to be run in `autocms.cfg` does not immediately
cause the changes to take effect. Run `./autocms.sh print` to print a 
new list of lines for your crontab for the new configuration and 
then edit your crotab appropriately. If you are only using cron 
for AutoCMS, you can replace your existing crontab with the new 
configuration with `crontab autocms.crontab`. Make sure to 
always update your crontab on the same node that you intend to have 
AutoCMS run on!

## Running AutoCMS from the Command Line

It is possible to submit jobs, harvest log files, and 
generate web-page reports for various jobs on the command line using
the `autocms.sh` script. As given in the following examples:

```bash
# submit 3 example_test jobs
./autocms.sh submit example_test 3

# harvest logs for example_test
./autocms.sh logharvest example_test

# generate a new webpage for example_test based on harvested logs
./autocms.sh report example_test
```
