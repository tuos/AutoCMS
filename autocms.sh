#!/bin/bash

print_autocms_crontab ()
{
  if [[ -f autocms.crontab ]] 
  then
    rm autocms.crontab 
  fi

  echo "MAILTO=\"\"" >> autocms.crontab
  echo "*/$AUTOCMS_SUBWAIT * * * * cd $AUTOCMS_BASEDIR && $AUTOCMS_BASEDIR/submitter.sh"  >> autocms.crontab
  echo "0,30 * * * * cd $AUTOCMS_BASEDIR && /usr/local/bin/python logharvester.py" >> autocms.crontab
  echo "15,45 * * * * cd $AUTOCMS_BASEDIR && /usr/local/bin/python reporter.py" >> autocms.crontab
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


