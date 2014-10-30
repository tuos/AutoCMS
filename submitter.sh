#!/bin/bash

# read configuration file and determine test name
source `pwd`/autocms.cfg
AUTOCMS_TEST_NAME=$1

AUTODIR=$AUTOCMS_BASEDIR
export MOABHOMEDIR=/usr/scheduler/config/moab

# Determine number of jobs in the queue

NUMJOBS=`/usr/scheduler/moab/bin/showq -w group=$AUTOCMS_GNAME | grep -c $AUTOCMS_UNAME`

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

# Submit the skim_test pbs script
cd $AUTODIR/$AUTOCMS_TEST_NAME

SUBID=`/usr/scheduler/torque/bin/qsub  $AUTODIR/$AUTOCMS_TEST_NAME/$AUTOCMS_TEST_NAME.pbs -v AUTOCMS_COUNTER="$SEQ",AUTOCMS_CONFIGFILE="$AUTODIR/autocms.cfg"`
SUBMIT_STATUS=$?
NOW=`date`
STAMP=`date +%s`
if [ ! $SUBMIT_STATUS -eq 0 ]; then
   SUBID=FAIL
fi

echo "$SUBID $STAMP $SUBMIT_STATUS" >> $AUTODIR/$AUTOCMS_TEST_NAME/newstamp.$(date +%s)
