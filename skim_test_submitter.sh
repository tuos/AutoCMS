#!/bin/bash

# read configuration file
source `pwd`/autocms.cfg


AUTODIR=$AUTOCMS_BASEDIR
export MOABHOMEDIR=/usr/scheduler/config/moab

#
# Determine number of jobs in the queue
#

NUMJOBS=`/usr/scheduler/moab/bin/showq -w group=$AUTOCMS_GNAME | grep -c $AUTOCMS_UNAME`

if [ $NUMJOBS -lt $AUTOCMS_MAXENQUEUE ]; then

    cd $AUTODIR
#
# increment the inputfile counter
#

    INPUTSEQ=$(( `cat skim_test/inputfile.counter` + 1 ))
    echo -n $INPUTSEQ > skim_test/inputfile.counter

#
# Determine the input file
#

    INPUTSEQ=$(( $INPUTSEQ % `wc -l < skim_test/myfiles.dat` ))
    INFILE=`cat skim_test/myfiles.dat | sed $INPUTSEQ'q;d'`

#
# Submit the skim_test pbs script
#

cd $AUTODIR/skim_test

# chroot jail
#SUBID=`/usr/scheduler/torque/bin/qsub -D /chroot/centos5 $AUTODIR/skim_test/skim_test.pbs -v INPUTFILE="$INFILE"`
# centos6

    SUBID=`/usr/scheduler/torque/bin/qsub  $AUTODIR/skim_test/skim_test.pbs -v INPUTFILE="$INFILE",CONFIGFILE="$AUTODIR/autocms.cfg"`
    SUBMIT_STATUS=$?
    if [ ! $SUBMIT_STATUS -eq 0 ]; then
       NOW=`date`
       echo "$NOW - JobSubmitter: Submission of skim_test script failed with exit code $SUBMIT_STATUS" >> $AUTODIR/skim_test.log
    else
       STAMP=`date +%s`
       echo "$SUBID $STAMP" >> $AUTODIR/skim_test/submission.stamps
    fi

fi

