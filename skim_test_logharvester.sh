#!/bin/bash

# read configuration file
source `pwd`/autocms.cfg

AUTODIR=$AUTOCMS_BASEDIR
cd $AUTODIR

#
# Look for new output files returned by pbs
#
for LOG in `ls skim_test | grep "skim_test.pbs.o[0-9]*"` ; do

  # determine jobid and current time
  JOBID=`echo skim_test/$LOG | sed -e "s/skim_test\/skim_test\.pbs\.o//"`
  DATE=`date`

  # determine the length of the job
  STARTTIME=`cat skim_test/$LOG | grep -m 1 "timestamp_begin" | cut -d "=" -f 2-`
  ENDTIME=`cat skim_test/$LOG | grep -m 1 "timestamp_end" | cut -d "=" -f 2-`
  if [ -n "$STARTTIME" -a -n "$ENDTIME" ]; then
    RUNTIME=$(( $ENDTIME - $STARTTIME ))
  fi
  QTIME=`cat skim_test/submission.stamps | grep "^$JOBID\.vmpsched" | cut -d " " -f 2- | tail -n 1`
  if [ -n "$STARTTIME" -a -n "$QTIME" ]; then
    WAITTIME=$(( $STARTTIME - $QTIME ))
  fi

  # Check for successful test, delete logs from successes
  if [ `cat skim_test/$LOG | grep -c "ALL TESTS SUCCESSFUL"` -gt 0 ]; then
    echo "$DATE - LogHarvester: Job $JOBID SUCCESS waittime=${WAITTIME}s runtime=${RUNTIME}s" >> skim_test.log
    mv skim_test/$LOG skim_test/successlogs/$LOG
    chmod g+r skim_test/successlogs/$LOG
    echo "$STARTTIME $WAITTIME $RUNTIME" >> skim_test/success.dat
  else
  # print information for failed job, move log to error directory
    echo "$DATE - LogHarvester: Job $JOBID ERROR waittime=${WAITTIME}s runtime=${RUNTIME}s " >> skim_test.log
    cat skim_test/$LOG | grep "^SKIM_TEST" | sed -e "s/^SKIM_TEST:/    /" >> skim_test.log
    mv skim_test/$LOG skim_test/errorlogs/$LOG
    chmod g+r skim_test/errorlogs/$LOG
  fi
    
done


#
# Delete successful job log files over 1 days old
# 
for LOG in `ls skim_test/successlogs | grep "skim_test.pbs.o[0-9]*"` ; do

  # determine age of the log file
  CURDATE=`date +%s`
  MODDATE=`date +%s -r skim_test/successlogs/$LOG`
  if [ -n "$CURDATE" -a -n "$MODDATE" ]; then
    AGE=$(( $CURDATE - $MODDATE ))
  else
    AGE=0
  fi
  # delete old files
  if [ $AGE -gt 86400 ]; then
   rm skim_test/successlogs/$LOG
  fi

done

#
# Delete failed job log files over 1 days old
# 
for LOG in `ls skim_test/errorlogs | grep "skim_test.pbs.o[0-9]*"` ; do

  # determine age of the log file
  CURDATE=`date +%s`
  MODDATE=`date +%s -r skim_test/errorlogs/$LOG`
  if [ -n "$CURDATE" -a -n "$MODDATE" ]; then
    AGE=$(( $CURDATE - $MODDATE ))
  else
    AGE=0
  fi
  # delete old files
  if [ $AGE -gt 86400 ]; then
   rm skim_test/errorlogs/$LOG
  fi

done



