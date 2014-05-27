#!/bin/bash

AUTODIR=/home/appelte1/autocms
WEBDIR=/home/appelte1/web/skim_test
cd $AUTODIR

#
# Clean up web directory
#

rm $WEBDIR/skim_test*.txt
rm $WEBDIR/skim_test*.html
rm $WEBDIR/skim_test*.png


#
# Count successful and failed jobs in the last 24 hours
# and build HTML section on failed jobs


echo "<h3>Successes From The Last 24 Hours</h3><hr />" >> skim_test_successes.tmp 

SUCCESSCOUNT=0
for LOG in `ls skim_test/successlogs`; do
  if [ $((  `date +%s` - `date +%s -r skim_test/successlogs/$LOG` )) -lt 86400 ]; then
    SUCCESSCOUNT=$(( $SUCCESSCOUNT + 1 ))
    ETIME=`cat skim_test/successlogs/$LOG | grep "SKIM_TEST: Beginning at " | sed -e "s/SKIM_TEST: Beginning at //"`
    ENODE=`cat skim_test/successlogs/$LOG | grep "SKIM_TEST: Running on node" | sed -e "s/SKIM_TEST: Running on node //"`
    EFILE=`cat skim_test/successlogs/$LOG | grep "SKIM_TEST: Will use input file " | sed -e "s/SKIM_TEST: Will use input file //"`
    echo "<b>SUCCESS </b> #$SUCCESSCOUNT: <br />" >> skim_test_successes.tmp
    echo "  Start time: $ETIME <br />" >> skim_test_successes.tmp
    echo "  Node Name: $ENODE <br />" >> skim_test_successes.tmp
    echo "  Input File: $EFILE <br />" >> skim_test_successes.tmp
    echo "  Log File: <a href="$LOG.txt">$LOG.txt</a> <hr />" >> skim_test_successes.tmp
    # careful to mask lstore passwd
    cat skim_test/successlogs/$LOG | \
      sed -e 's/--login-id [a-zA-Z0-9_!]*/--login-id XXXX/' | \
      sed -e 's/--password [a-zA-Z0-9_!]*/--password XXXX/' > $WEBDIR/$LOG.txt
    chmod a+r $WEBDIR/$LOG.txt
  fi
done

HOURSUCCESSCOUNT=0
for LOG in `ls skim_test/successlogs`; do
  if [ $((  `date +%s` - `date +%s -r skim_test/successlogs/$LOG` )) -lt 10800 ]; then
    HOURSUCCESSCOUNT=$(( $HOURSUCCESSCOUNT + 1 ))
  fi
done


echo "<h3>Errors From The Last 24 Hours</h3><hr />" >> skim_test_errors.tmp 

FAILCOUNT=0
for LOG in `ls skim_test/errorlogs`; do
  if [ $((  `date +%s` - `date +%s -r skim_test/errorlogs/$LOG` )) -lt 86400 ]; then
    FAILCOUNT=$(( $FAILCOUNT + 1 ))
    ETIME=`cat skim_test/errorlogs/$LOG | grep "SKIM_TEST: Beginning at " | sed -e "s/SKIM_TEST: Beginning at //"` 
    ENODE=`cat skim_test/errorlogs/$LOG | grep "SKIM_TEST: Running on node" | sed -e "s/SKIM_TEST: Running on node //"` 
    EFILE=`cat skim_test/errorlogs/$LOG | grep "SKIM_TEST: Will use input file " | sed -e "s/SKIM_TEST: Will use input file //"`
    EREASON=`cat skim_test/errorlogs/$LOG | grep "SKIM_TEST:.*ERROR" | sed -e "s/SKIM_TEST: //"`
    echo "<b>ERROR</b> #$FAILCOUNT: <br />" >> skim_test_errors.tmp
    echo "  Start time: $ETIME <br />" >> skim_test_errors.tmp
    echo "  Node Name: $ENODE <br />" >> skim_test_errors.tmp
    echo "  Input File: $EFILE <br />" >> skim_test_errors.tmp
    echo "  Error Type: $EREASON <br />" >> skim_test_errors.tmp
    echo "  Log File: <a href="$LOG.txt">$LOG.txt</a> <hr />" >> skim_test_errors.tmp
    # careful to mask lstore passwd
    cat skim_test/errorlogs/$LOG | \
      sed -e 's/--login-id [a-zA-Z0-9_!]*/--login-id XXXX/' | \
      sed -e 's/--password [a-zA-Z0-9_!]*/--password XXXX/' > $WEBDIR/$LOG.txt
    chmod a+r $WEBDIR/$LOG.txt
  fi
done

HOURFAILCOUNT=0
for LOG in `ls skim_test/errorlogs`; do
  if [ $((  `date +%s` - `date +%s -r skim_test/errorlogs/$LOG` )) -lt 10800 ]; then
    HOURFAILCOUNT=$(( $HOURFAILCOUNT + 1 ))
  fi
done


echo "<h3>Long Execution Time Warnings From The Last 24 Hours</h3><hr />" >> skim_test_warn.tmp 

WARNCOUNT=0
for LOG in `ls skim_test/successlogs`; do
  if [ $((  `date +%s` - `date +%s -r skim_test/successlogs/$LOG` )) -lt 86400 ]; then
    JOBSTART=`cat skim_test/successlogs/$LOG | grep "timestamp_begin=" | sed -e "s/timestamp_begin=//"`    
    JOBEND=`cat skim_test/successlogs/$LOG | grep "timestamp_end=" | sed -e "s/timestamp_end=//"`    
    if [ $(( $JOBEND - $JOBSTART )) -gt 3600 ]; then
      JOBTIME=$(( $JOBEND - $JOBSTART ))
      WARNCOUNT=$(( $WARNCOUNT + 1 ))
      ETIME=`cat skim_test/successlogs/$LOG | grep "SKIM_TEST: Beginning at " | sed -e "s/SKIM_TEST: Beginning at //"`
      ENODE=`cat skim_test/successlogs/$LOG | grep "SKIM_TEST: Running on node" | sed -e "s/SKIM_TEST: Running on node //"`
      EFILE=`cat skim_test/successlogs/$LOG | grep "SKIM_TEST: Will use input file " | sed -e "s/SKIM_TEST: Will use input file //"`
      echo "  Warning #$WARNCOUNT: <br />" >> skim_test_warn.tmp
      echo "  Start time: $ETIME <br />" >> skim_test_warn.tmp
      echo "  Node Name: $ENODE <br />" >> skim_test_warn.tmp
      echo "  Input File: $EFILE <br />" >> skim_test_warn.tmp
      echo "  Execution Time: $JOBTIME seconds<br />" >> skim_test_warn.tmp
      echo "  Log File: <a href="$LOG.txt">$LOG.txt</a> <hr />" >> skim_test_warn.tmp
      # careful to mask lstore passwd
      # cp skim_test/errorlogs/$LOG web/$LOG.txt
      cat skim_test/successlogs/$LOG | \
        sed -e 's/--login-id [a-zA-Z0-9_!]*/--login-id XXXX/' | \
        sed -e 's/--password [a-zA-Z0-9_!]*/--password XXXX/' > $WEBDIR/$LOG.txt
      chmod a+r $WEBDIR/$LOG.txt
    fi
  fi
done

HOURWARNCOUNT=0
for LOG in `ls skim_test/successlogs`; do
  if [ $((  `date +%s` - `date +%s -r skim_test/successlogs/$LOG` )) -lt 10800 ]; then
    JOBSTART=`cat skim_test/successlogs/$LOG | grep "timestamp_begin=" | sed -e "s/timestamp_begin=//"`
    JOBEND=`cat skim_test/successlogs/$LOG | grep "timestamp_end=" | sed -e "s/timestamp_end=//"`
    if [ $(( $JOBEND - $JOBSTART )) -gt 3600 ]; then
      HOURWARNCOUNT=$(( $HOURWARNCOUNT + 1 ))
    fi
  fi
done


#
# make plots
#

rm skim_test/success_24hours.dat

for LOG in `ls skim_test/successlogs` ; do
 if [ $((  `date +%s` - `date +%s -r skim_test/successlogs/$LOG` )) -lt 86400 ]; then
 JOBID=`echo skim_test/successlogs/$LOG | sed -e "s/skim_test\/successlogs\/skim_test\.pbs\.o//"` 
 DATE=`date`
  STARTTIME=`cat skim_test/successlogs/$LOG | grep "timestamp_begin=" | sed -e "s/timestamp_begin=//"`
  STARTTIME_LOCALE=$(($STARTTIME-5*3600))	#Vanderbilt local time zone is UTC -06:00
  ENDTIME=`cat skim_test/successlogs/$LOG | grep "timestamp_end=" | sed -e "s/timestamp_end=//"`
  if [ -n "$STARTTIME" -a -n "$ENDTIME" ]; then
    RUNTIME=$(( $ENDTIME - $STARTTIME ))
  fi
  QTIME=`cat skim_test/submission.stamps | grep "^$JOBID\.vmpsched" | cut -d " " -f 2- | tail -n 1`
  if [ -n "$STARTTIME" -a -n "$QTIME" ]; then
    WAITTIME=$(( $STARTTIME - $QTIME ))
  fi
echo "$STARTTIME_LOCALE $WAITTIME $RUNTIME" >> skim_test/success_24hours.dat

fi
done

gnuplot $AUTODIR/skim_test_success.gnu

gnuplot $AUTODIR/skim_test_successlog.gnu

#
# Generate HMTL report and data plots
#
echo "<html><head><title>T2_US_VANDERBILT Internal Site New LSTORE Test: Skimming</title></head>" >> $WEBDIR/skim_test.html
echo "<body>" >> $WEBDIR/skim_test.html
echo "<h2>T2_US_VANDERBILT Internal Site New LSTORE Test: Skimming</h2>" >>  $WEBDIR/skim_test.html
echo `date` >> $WEBDIR/skim_test.html
echo "<hr />" >> $WEBDIR/skim_test.html
#echo "<img src=\"skim_test_success.png\" alt=\"plot\" />" >> $WEBDIR/skim_test.html
#echo "<img src=\"skim_test_successlog.png\" alt=\"plot\" />" >> $WEBDIR/skim_test.html
#echo "<hr />" >> $WEBDIR/skim_test.html

echo "<div style=\"align=left\"><img src=\"skim_test_success.png\">" >> $WEBDIR/skim_test.html

echo "<img src=\"skim_test_successlog.png\"></div>" >> $WEBDIR/skim_test.html

echo "<hr />" >> $WEBDIR/skim_test.html

echo "Failed jobs in the last 24 hours: $FAILCOUNT <br />" >>	$WEBDIR/skim_test.html
echo "Failed jobs in the last three hours: $HOURFAILCOUNT <br /><br />" >> $WEBDIR/skim_test.html
echo "Long running jobs (> 1 hour) in the last 24 hours: $WARNCOUNT <br />" >> $WEBDIR/skim_test.html
echo "Long running jobs (> 1 hour) in the last three hours: $HOURWARNCOUNT <br /><br />" >> $WEBDIR/skim_test.html
echo "Successful jobs in the last 24 hours: $SUCCESSCOUNT <br />" >> $WEBDIR/skim_test.html
echo "Successful jobs in the last three hours: $HOURSUCCESSCOUNT <br /><br />" >> $WEBDIR/skim_test.html

echo "<hr />" >> $WEBDIR/skim_test.html

cat skim_test_errors.tmp >> $WEBDIR/skim_test.html
rm skim_test_errors.tmp

cat skim_test_warn.tmp >> $WEBDIR/skim_test.html
rm skim_test_warn.tmp

cat skim_test_successes.tmp >> $WEBDIR/skim_test.html
rm skim_test_successes.tmp

echo "</body></html>" >>  $WEBDIR/skim_test.html
