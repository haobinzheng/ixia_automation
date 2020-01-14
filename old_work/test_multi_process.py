import os
import pexpect
import sys
import time
import datetime
import logging
import csv
import re
import threading
from switch_class import *
from process_case import *
from utility import *
from test_case import *
import multiprocessing
from multiprocessing import Process
import subprocess
 
 
##################################
#  get host names and IP address 
##################################
 
device_file = 'metro_switches_new'
device = get_csv(device_file)

routerFile = open(device_file, 'r')
switch_dev = [a for a in routerFile]


switch_list =  []
for sw in switch_dev:
   sw_obj = switch(sw)
   switch_list.append(sw_obj) 

#####################################################
# Keep an inventory for the devices 
# including software version, configuration etc
#####################################################
archieve = 0
if archieve == 1: 
	for  s in switch_list: 
		sw1 = cienaswitch(s)
		logfile_name = sw1.host + '.config'
		fout = open (logfile_name,'w')
		sw1.child.logfile_read = fout 
		sw_send_cmd(sw1,'system shell set global-more off')
		#sw_send_cmd(sw1,'soft show')
		#print "start to show config"
		sw_send_cmd(sw1,'config show br')
		#print "done with config show"
		sw_send_cmd(sw1,'system shell set global-more on')

#################################################################
#  Build MPLS VC database  
#################################################################
dut_list = []
online = 0
soak = 0
offline = 0
process_file = 0

# The DUT is 5142_1_A

process_list = [proc_snmp,proc_show_commands]
process_id_list = []
#for proc in process_list: 
#	t = threading.Thread(target=proc, args = (sw_dut_A,))
#	t.daemon = True
#	t.start()

sw_dut_A  = switch_list[2]

for proc in process_list:
		print ("test sub process before soak")
		print (proc)
		p = Process(target=proc,args = (sw_dut_A,))
		#p = Process(target=proc)
		p.daemon = True
		p.start()
		print (dir(p))
		process_id_list.append(p)
		print (p.is_alive())
		#p.terminate()
		p.join()

while 1:
	pass
