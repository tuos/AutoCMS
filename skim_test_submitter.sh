#!/bin/bash
AUTODIR=/home/appelte1/autocms
export MOABHOMEDIR=/usr/scheduler/config/moab

#
# Determine number of jobs in the queue
#

NUMJOBS=`/usr/scheduler/moab/bin/showq -w group=cms_stage2 | grep -c appelte1`
#NUMJOBS=`/usr/scheduler/moab/bin/showq | grep -c appelte1`



if [ $NUMJOBS -lt 20 ]; then

    cd $AUTODIR
#
# increment the inputfile counter
#

    INPUTSEQ=$(( `cat skim_test/inputfile.counter` + 1 ))
    echo -n $INPUTSEQ > skim_test/inputfile.counter

#
# Determine the input file
#

    INPUTSEQ=$(( $INPUTSEQ % 28747 ))
    INFILE=`cat skim_test/myfiles.dat | sed $INPUTSEQ'q;d'`

#
# Submit the skim_test pbs script
#

cd $AUTODIR/skim_test

# chroot jail
#SUBID=`/usr/scheduler/torque/bin/qsub -D /chroot/centos5 $AUTODIR/skim_test/skim_test.pbs -v INPUTFILE="$INFILE"`
# centos6

    SUBID=`/usr/scheduler/torque/bin/qsub  $AUTODIR/skim_test/skim_test.pbs -v INPUTFILE="$INFILE"`
    SUBMIT_STATUS=$?
    if [ ! $SUBMIT_STATUS -eq 0 ]; then
       NOW=`date`
       echo "$NOW - JobSubmitter: Submission of skim_test script failed with exit code $SUBMIT_STATUS" >> $AUTODIR/skim_test.log
    else
       STAMP=`date +%s`
       echo "$SUBID $STAMP" >> $AUTODIR/skim_test/submission.stamps
    fi

fi

