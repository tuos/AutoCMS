#!/bin/bash

print_autocms_crontab ()
{
  if [[ -f autocms.crontab ]] 
  then
    rm autocms.crontab 
  fi

  echo "MAILTO=\"\"" >> autocms.crontab
  SUBWAIT=( $( echo $AUTOCMS_TEST_SUBWAITS | tr ":" " " ) )
  COUNT=0
  for TESTNAME in $( echo $AUTOCMS_TEST_NAMES | tr ":" "\n" ); do
    echo "count: $COUNT subwait: ${SUBWAIT[$COUNT]}"
    if [ ${SUBWAIT[$COUNT]} -lt 60 ]; then
      echo "*/${SUBWAIT[$COUNT]} * * * * cd $AUTOCMS_BASEDIR && $AUTOCMS_BASEDIR/submitter.sh $TESTNAME"  >> autocms.crontab
      echo "0,10,20,30,40,50 * * * * cd $AUTOCMS_BASEDIR && /usr/local/bin/python logharvester.py $TESTNAME" >> autocms.crontab
      echo "5,15,25,35,45,55 * * * * cd $AUTOCMS_BASEDIR && /usr/local/bin/python reporter.py $TESTNAME" >> autocms.crontab
    else
      SUBWAIT[$COUNT]=$(( ${SUBWAIT[$COUNT]} / 60 )) 
      echo "0 */${SUBWAIT[$COUNT]} * * * cd $AUTOCMS_BASEDIR && $AUTOCMS_BASEDIR/submitter.sh $TESTNAME"  >> autocms.crontab
      echo "10,40 * * * * cd $AUTOCMS_BASEDIR && /usr/local/bin/python logharvester.py $TESTNAME" >> autocms.crontab
      echo "20,50 * * * * cd $AUTOCMS_BASEDIR && /usr/local/bin/python reporter.py $TESTNAME" >> autocms.crontab
    fi
    (( COUNT++ ))
  done
}

source autocms.cfg

if [[ $1 = "print" ]]
then
  print_autocms_crontab
  echo
  echo "Crontab lines for autocms below:"
  echo "=================================================="
  cat autocms.crontab
  echo "=================================================="
  echo "These lines are also saved in the file \"autocms.crontab\""
  echo
  exit 0
fi

echo "WARNING: Use of this script will overwrite your crontab on this host."
echo "For manual setup, use \"autocms.sh print\" to print the"
echo "crontab entry lines needed to run the system."
echo "Current host: $HOSTNAME"

read -p "Are you sure [y/n] ? " -n 1 -r
echo; echo   
if [[ $REPLY =~ ^[Yy]$ ]]
then

  if [[ $1 = "start" ]]
  then  
    if [[ -f crontab_host.txt ]]
    then
      AUTOCMS_HOST=`cat crontab_host.txt`
      echo "ERROR: autocms instance already running on $AUTOCMS_HOST"
      echo "Exiting..."
      exit 1
    fi
    echo "Starting autocms..."
    echo $HOSTNAME > crontab_host.txt
    print_autocms_crontab
    crontab autocms.crontab
    exit 0
  fi

  if [[ $1 = "stop" ]]
  then
    if [[ ! -f crontab_host.txt ]]
    then
      echo "No running autocms instance detected. Exiting..."
      exit 1
    fi
    AUTOCMS_HOST=`cat crontab_host.txt`
    if [[ ! $AUTOCMS_HOST = $HOSTNAME ]]
    then
      echo "Attempting to stop autocms on $HOSTNAME "
      echo "but this instance of autocms is running on $AUTOCMS_HOST. "
      echo "Log into $HOSTNAME and try again."
      exit 1
    fi
    echo "Stopping autocms..." 
    crontab -r
    rm crontab_host.txt
    exit 0
  fi

  echo "Usage \"autocms.sh start\" or \"autocms.sh stop\" "
  echo "Please see: "
  echo "  https://wiki.accre.vanderbilt.edu/foswiki/bin/view/VandyCMS/AutoCMS"
  echo "for additional documentation."

fi


