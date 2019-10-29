#!/bin/sh
rm Log/*.log
# mv Log/mclag_perf.log Log/mclag_perf.log.old

# mv Log/mclag_perf.log Test_Result/mclag_perf.log.old
#python mclag_v2.py -t 548D -e -test 2 -n 1 
#python mclag_v2.py -t fg-548d -test 4
#echo "python mclag_v2.py -t fg-548d -f -sw -c -mac 1000-5000-1000 -lm -test 3 -v "
# echo "python mclag_v2.py -t fg-548d -mac 2-2-1 -test 3 "
# python mclag_v2.py -t fg-548d -mac 2-2-1 -test 3 
#python mclag_v2.py -t 448D -mac 1000-10000-1000 -test 1 -lm  

echo "python mclag_v2.py -t 448D -mac 1000-10000-1000 -test 1"
python mclag_v2.py -t 448D -mac 1000-10000-1000 -test 1 

#python mclag_v2.py -t 548D -n 3 -b -v -mac 1000 -file mac_1k_no_logmac 

#python mclag_v2.py -t 548D -n 3 -b -v -mac 2000 -file mac_2k_no_logmac 
#python mclag_v2.py -t 548D -n 3 -b -v -mac 2000 -file mac_2k_logmac -lm

# cp Log/*.* Test_Result/
