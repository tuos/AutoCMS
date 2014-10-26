#!/bin/bash

# read configuration file
source `pwd`/autocms.cfg

AUTODIR=$AUTOCMS_BASEDIR
export MOABHOMEDIR=/usr/scheduler/config/moab

# Determine number of jobs in the queue

NUMJOBS=`/usr/scheduler/moab/bin/showq -w group=$AUTOCMS_GNAME | grep -c $AUTOCMS_UNAME`

if [ $NUMJOBS -ge $AUTOCMS_MAXENQUEUE ]; then
  exit 0
fi

cd $AUTODIR

# increment the inputfile counter
INPUTSEQ=$(( `cat $AUTOCMS_TEST_NAME/inputfile.counter` + 1 ))
echo -n $INPUTSEQ > $AUTOCMS_TEST_NAME/inputfile.counter

# Determine the input file
INPUTSEQ=$(( $INPUTSEQ % `wc -l < skim_test/myfiles.dat` ))
INFILE=`cat skim_test/myfiles.dat | sed $INPUTSEQ'q;d'`

# Submit the skim_test pbs script
cd $AUTODIR/$AUTOCMS_TEST_NAME

SUBID=`/usr/scheduler/torque/bin/qsub  $AUTODIR/$AUTOCMS_TEST_NAME/$AUTOCMS_TEST_NAME.pbs -v INPUTFILE="$INFILE",CONFIGFILE="$AUTODIR/autocms.cfg"`
SUBMIT_STATUS=$?
NOW=`date`
STAMP=`date +%s`
if [ ! $SUBMIT_STATUS -eq 0 ]; then
   SUBID=FAIL
fi

echo "$SUBID $STAMP $SUBMIT_STATUS" >> $AUTODIR/$AUTOCMS_TEST_NAME/newstamp.$(date +%s)
