#!/bin/bash

# read configuration file and determine test name
source `pwd`/autocms.cfg
AUTOCMS_TEST_NAME=$1

AUTODIR=$AUTOCMS_BASEDIR

# Determine number of jobs in the queue

NUMJOBS=`squeue -h --user=$AUTOCMS_UNAME --account=$AUTOCMS_GNAME | wc -l`

if [ $NUMJOBS -ge $AUTOCMS_MAXENQUEUE ]; then
  exit 0
fi

cd $AUTODIR

# increment the counter
if [ ! -f $AUTOCMS_TEST_NAME/counter ]; then
  echo -n "0" > $AUTOCMS_TEST_NAME/counter
fi

SEQ=$(( `cat $AUTOCMS_TEST_NAME/counter` + 1 ))
echo -n $SEQ > $AUTOCMS_TEST_NAME/counter

# Submit the skim_test slurm script
cd $AUTODIR/$AUTOCMS_TEST_NAME

export AUTOCMS_COUNTER=$SEQ
export AUTOCMS_CONFIGFILE=$AUTODIR/autocms.cfg

SUBID_MESSAGE=`sbatch  --account=$AUTOCMS_GNAME $AUTODIR/$AUTOCMS_TEST_NAME/$AUTOCMS_TEST_NAME.slurm -export=AUTOCMS_COUNTER,AUTOCMS_CONFIGFILE  2>&1`
SUBMIT_STATUS=$?
SUBID=`echo $SUBID_MESSAGE | sed -e "s/Submitted batch job //"`
NOW=`date`
STAMP=`date +%s`
SLOG=""
if [ ! $SUBMIT_STATUS -eq 0 ]; then
   SUBID=FAIL
   SLOG=$AUTOCMS_TEST_NAME.submission.$SEQ.$(date +%s).log
   echo "Job submission failed at $(date)" >> $SLOG
   echo "On node $HOSTNAME" >> $SLOG
   echo "Submission command output:" >> $SLOG ;  echo >> $SLOG
   echo "$SUBID_MESSAGE" >> $SLOG 
fi

echo "$SUBID $STAMP $SUBMIT_STATUS $SLOG" >> $AUTODIR/$AUTOCMS_TEST_NAME/newstamp.$(date +%s)