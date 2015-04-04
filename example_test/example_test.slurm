#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=1G
#SBATCH --output=example_test.slurm.o%A.log
#SBATCH --time=0-01:00:00
#SBATCH --job-name="example_test"

main ()
{
  # run the AutoCMS Configuration File
  source $AUTOCMS_CONFIGFILE

  echo "${AUTOCMS_start_time_TOKEN}$(date +%s)"
  echo "EXAMPLE_TEST: Beginning at $(date)"
  echo "${AUTOCMS_node_TOKEN}${HOSTNAME}"

  #-----------------------------------------------------------------------
  printbanner "Determining number of proccesses on this node"

  NUM_PROCESSES=`ps aux | wc -l`
  echo "${AUTOCMS_num_proc_TOKEN}${NUM_PROCESSES}"

  #-----------------------------------------------------------------------
  printbanner "Rolling the dice"

  DICE_A=$(( $RANDOM % 6 + 1 ))
  echo "Rolled a ${DICE_A}!!!"
  DICE_B=$(( $RANDOM % 6 + 1 ))
  echo "Rolled a ${DICE_B}!!!"
  echo "${AUTOCMS_dice_sum_TOKEN}$(( $DICE_A + $DICE_B ))"
  if [ $(( $DICE_A + $DICE_B )) -eq 2 ]; then
    echo "${AUTOCMS_error_string_TOKEN}Uh oh, rolled snake eyes! Error!"
    exitclean 2
  fi

  #-----------------------------------------------------------------------
  printbanner "Sleeping for a while"

  SLEEPTIME=$(( $RANDOM % 60 ))
  echo "EXAMPLE_TEST: Sleeping for $SLEEPTIME seconds"
  sleep $SLEEPTIME

  echo
  echo "${AUTOCMS_SUCCESS_TOKEN}" 
  exitclean 0
}

exitclean ()
{
    echo -n "EXAMPLE_TEST: Ending at "; date
    echo "${AUTOCMS_end_time_TOKEN}$(date +%s)"
    echo "${AUTOCMS_exit_code_TOKEN}$1"
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
