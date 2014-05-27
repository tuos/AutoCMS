set terminal png crop enhanced  size 750,350 
set output "/home/appelte1/web/skim_test/skim_test_success.png"
set xlabel "timestamp (recent 24 hours)"
set ylabel "time (s)"
set xdata time
set timefmt "%s"
set xtics 14400
set format x "%a %H:%M"
#set yrange [0:1000]
#set xtics border nomirror in rotate by -45 offset character 0, 0, 0 
plot 'skim_test/success_24hours.dat' using 1:2 title "Waiting Time", \
     'skim_test/success_24hours.dat' using 1:3 title "Running Time"
