# AutoCMS Tokens

AutoCMS parses the standard output of test scripts by looking for 
specific strings called tokens that are set in the `autocms.cfg` file.
The idea behind this system is to track job properties in a manner
that can be understood by the bash submission script, the 
python AutoCMS system parsing the logs, and a human trying to
read job logs to understand possible errors.

As an example, the starting time of the test job as a unix timestamp 
is to be stored as 
the `start_time` attribute in an AutoCMS `JobRecord` object. In the 
`autocms.cfg` file, there is a line:

    export AUTOCMS_start_time_TOKEN="AutoCMS: timestamp_start "

The AutoCMS system will look for a line in the job output 
beginning with "AutoCMS: timestamp_start " and store the rest of the 
line in the `start_time` attribute. To have this function properly,
the test script may have a command as follows at the beginning of the job:

    echo "${AUTOCMS_start_time_TOKEN}$(date +%s)"

The following tokens are expected for all AutoCMS jobs:

    * AUTOCMS_start_time_TOKEN - unix timestamp of job start
    * AUTOCMS_end_time_TOKEN - unix timestamp of job end
    * AUTOCMS_node_TOKEN - hostname of worker node on which the job runs
    * AUTOCMS_exit_code_TOKEN - exit code to report
    * AUTOCMS_error_string_TOKEN - description of error

If the job is successtul, AUTOCMS_SUCCESS_TOKEN should be printed.

The [bare_test script](../bare_test/bare_test.slurm) and 
[example_test script](../example_test/example_test.slurm) both show how this
is implemented in bash. 

More tokesn can also be added if new information is needed from the job.
AutoCMS will automatically add an attribute to the JobRecord
corresponding to that token.

For example, one could add the following into the `autocms.cfg`:

   export AUTOCMS_cpuTemperature_TOKEN="AutoCMS: cpu temperature is "

Then in the test job script one could add

    echo "${AUTOCMS_cpuTemperature_TOKEN}74"

Then the AutoCMS JobRecord recorded after logharvesting will have the attribute "cpuTemperature" with value "74"

To report on this additional information, see the 
[customization section](custom.md).
