#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=1G
#SBATCH --output=example_test.slurm.o%A
#SBATCH --time=0-01:00:00
#SBATCH --job-name="example_test"

main ()
{

  # run the AutoCMS Configuration File
  source $AUTOCMS_CONFIGFILE

  echo "${AUTOCMS_startTime_TOKEN}$(date +%s)"
  echo "EXAMPLE_TEST: Beginning at $(date)"
  echo "${AUTOCMS_node_TOKEN}${HOSTNAME}"

  #-----------------------------------------------------------------------
  printbanner "Determining number of proccesses on this node"

  NUM_PROCESSES=`ps aux | wc -l`
  echo "${AUTOCMS_numProc_TOKEN}${NUM_PROCESSES}"

  #-----------------------------------------------------------------------
  printbanner "Rolling the dice"

  DICE_A=$(( $RANDOM % 6 + 1 ))
  echo "Rolled a ${DICE_A}!!!"
  DICE_B=$(( $RANDOM % 6 + 1 ))
  echo "Rolled a ${DICE_B}!!!"
  echo "${AUTOCMS_diceSum_TOKEN}$(( $DICE_A + $DICE_B ))"
  if [ $(( $DICE_A + $DICE_B )) -eq 2 ]; then
    echo "${AUTOCMS_errorString_TOKEN}Uh oh, rolled snake eyes! Error!"
    exitclean 2
  fi

  #-----------------------------------------------------------------------
  printbanner "Sleeping for a while"

  SLEEPTIME=$(( $RANDOM % 600 ))
  echo "EXAMPLE_TEST: Sleeping for $SLEEPTIME seconds"
  sleep $SLEEPTIME

  #-----------------------------------------------------------------------
  printbanner "Touching a file in /tmp"

  cd /tmp/$PBS_JOBID

  touch tmp_test
  TEMP_TEST_RESULT=$?
  if [ $TEMP_TEST_RESULT -eq 0 ]; then
    echo "EXAMPLE_TEST: touch in directory /tmp/$PBS_JOBID OK"
  else
    echo "${AUTOCMS_errorString_TOKEN}touch in directory /tmp/$PBS_JOBID ERROR $TEMP_TEST_RESULT"
    exitclean $TEMP_TEST_RESULT
  fi

  echo
  echo "${AUTOCMS_SUCCESS_TOKEN}" 
  exitclean 0
}

exitclean ()
{
    printbanner "Cleaning up /tmp and Exiting"
    if [ -e /tmp/$PBS_JOBID/tmp_test ]; then
      rm /tmp/$PBS_JOBID/tmp_test
    fi
    echo -n "EXAMPLE_TEST: Ending at "; date
    echo "${AUTOCMS_endTime_TOKEN}$(date +%s)"
    echo "${AUTOCMS_exitCode_TOKEN}$1"
    exit $1
}

printbanner ()
{
  echo -e "\n\n\n"
  echo "*****************************************************"
  echo "*"
  echo "* $1"
  echo "*"
  echo "*****************************************************"
  echo -e "\n\n\n"

}


main
