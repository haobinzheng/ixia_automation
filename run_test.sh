#!/bin/sh
rm Log/*.log

#python mclag_v2.py -t 448D -test 2 -n 1 -file demo -u
# echo "python mclag_v2.py -t 548D -e -test 2 -n 1 -c -f -file demo_548d_1 -ug 194"

# echo "python mclag_v2.py -t fg-548d -test -1 -sw 385 "
# python mclag_v2.py -t fg-548d -test -1 -sw 385 
# python mclag_v2.py -t fg-548d -test 9 -sw 383
# echo "python mclag_v2.py -t 448D -test 6"
# python mclag_v2.py -t 448D -test 6
#echo "python mclag_v2.py -t 448D -test -1 -c -ug 384"
# echo "python mclag_v2.py -t 448D -test -1 -f -c "

# python mclag_v2.py -t 448D -test -1 -c -e

echo "python mclag_v2.py -t 548D -test -1 -c -nf -f"
python mclag_v2.py -t 548D -test -1 -c -nf -f 


# echo "python mclag_v2.py -t 548D -test 6"
# python mclag_v2.py -t 548D -test 6

# echo "python mclag_v2.py -t 448D -test 2 -b -n 5 -c -f -file demo_1"
# python mclag_v2.py -t 448D -test 2 -b -n 5 -c -f -file demo_1

# echo "python mclag_v2.py -t 448D -test 2 -n 10 -file demo_2"
# python mclag_v2.py -t 448D -test 2 -n 10 -file demo_2 
#python mclag_v2.py -t 448D -test 2 -n 1 -file demo -u


# mv Log/mclag_perf.log Log/mclag_perf.log.old

# mv Log/mclag_perf.log Test_Result/mclag_perf.log.old
#python mclag_v2.py -t 548D -e -test 2 -n 1 
#python mclag_v2.py -t fg-548d -test 4
#echo "python mclag_v2.py -t fg-548d -f -sw -c -mac 1000-5000-1000 -lm -test 3 -v "
# echo "python mclag_v2.py -t fg-548d -mac 2-2-1 -test 3 "
# python mclag_v2.py -t fg-548d -mac 2-2-1 -test 3 
#python mclag_v2.py -t 448D -mac 1000-10000-1000 -test 1 -lm  



#python mclag_v2.py -t 548D -n 3 -b -v -mac 1000 -file mac_1k_no_logmac 

#python mclag_v2.py -t 548D -n 3 -b -v -mac 2000 -file mac_2k_no_logmac 
#python mclag_v2.py -t 548D -n 3 -b -v -mac 2000 -file mac_2k_logmac -lm

# cp Log/*.* Test_Result/
