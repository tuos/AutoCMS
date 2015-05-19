#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=1G
#SBATCH --output=bare_test.slurm.o%A.log
#SBATCH --time=0-01:00:00
#SBATCH --job-name="bare_test"

main ()
{
  # run the AutoCMS Configuration File
  source $AUTOCMS_CONFIGFILE

  echo "${AUTOCMS_start_time_TOKEN}$(date +%s)"
  echo "EXAMPLE_TEST: Beginning at $(date)"
  echo "${AUTOCMS_node_TOKEN}${HOSTNAME}"

  #-----------------------------------------------------------------------
  printbanner "Running some scientific application..."

  # replace the line below with your scientific application configured 
  # to run a brief test
  ./frobnicate.sh

  APPLICATION_RESULT=$?
  if [ $APPLICATION_RESULT -ne 0 ]; then
     exitclean $APPLICATION_RESULT
  fi

  echo
  echo "${AUTOCMS_SUCCESS_TOKEN}"
  exitclean 0
}

exitclean ()
{
    echo -n "BARE_TEST: Ending at "; date
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
