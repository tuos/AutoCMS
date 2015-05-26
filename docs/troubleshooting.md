# Troubleshooting AutoCMS Tests

If a test has apparently stopped running or is not producing an 
updated webpage, first log into the node from which AutoCMS should
be submitting and run `crontab -l` to ensure that AutoCMS is still
being called from cron.

A list of the current job records being tracked can be 
printed interactively with:

    python print_records.py some_test

You can then try running the job submission, logharvesting, and 
reporting on the command line to see if any error messages 
can be detected:

```bash
./autocms.sh submit some_test 1

./autocms.sh logharvest some_test

./autocms.sh report some_test
```

You can also delete the file `some_test/records.pickle` file which 
contains the python list of JobRecords. This will not permanently 
lose any information about recent jobs, but will cause the logharevester
to parse all logs again to reconstruct the list of JobRecords.
This may fix the problem if the pickle file was corrupted.

If you are not concerned about losing track of recent jobs, you can delete
both `some_test/records.pickle` and `some_test/submission.stamps` which
will remove all records of recent submissions, effectively reseting the
state of the AutoCMS test.

 
