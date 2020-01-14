#!/usr/local/bin/python 
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
from class_mpls import *
from process_case import *
from utility import *
from test_case import *
from subprocess import Popen, PIPE
import multiprocessing
from multiprocessing import Process
import subprocess

######################################
# Get device basic information
######################################

device_file = 'metro_switches_new'
device = get_csv(device_file)
routerFile = open(device_file, 'r')
switch_dev = [a for a in routerFile]

switch_list =  []
dut_list = []
for sw in switch_dev:
   sw_obj = switch(sw)
   switch_list.append(sw_obj) 

###############################################################
#  Input the management optionst
#  Note: backdoor2 -- connect to device with original password
#        backdoor - connect to device with private password
################################################################
num = input_mgmt() 
if num == 1:		# Change passwords for device(s)
	dev = input_select_device()
	if dev == 0:
		print "Change password for all devices"
		for sw in switch_list:
			dut = backdoor2(sw)
			dut.change_pass()
			dut.child.close()
	else:
		sw = switch_list[dev-1]
		print "You are about to change password on %s" % sw.hostname
		dut = backdoor2(sw)
		dut.change_pass()
		dut.child.close()
		
elif num == 2: # Recover passwords for device(s)
	dev = input_select_device()
	if dev == 0:
		print "Recover password for all devices"
		for sw in switch_list:
			dut = backdoor(sw)
			dut.recover_pass()
			dut.child.close()
	else:
		sw = switch_list[dev-1]
		print "You are about to recover password on %s" % sw.hostname
		dut = backdoor(sw)
		dut.recover_pass()
		dut.child.close()
		

elif num == 3:      # Backup configuration for devices
	dev = input_select_device()
	if dev == 0:
		print "\n!!Before you backup this device(s), please make sure you do this after changing password"
		print "you are about to backup configuration on ALL devices, are you sure you want to do this?"
		b = input_select_backup()
		if b == 'Yes':
			pass
		elif b == 'No' or b == 'NA':
			sys.exit(1)
		for sw in switch_list:
			dut = backdoor(sw)
			backup_config(dut)
			dut.child.close()
	else:
		print "\n!!Before you backup this device, please make sure you do this after changing password"
		print "you are about to backup configuration on the device %s , are you sure you want to do this?" %switch_list[dev-1].hostname
		b = input_select_backup()
		if b == 'Yes':
			pass
		elif b == 'No' or b == 'NA':
			sys.exit(1)
		sw = switch_list[dev-1]
		print "You are about to backup configuration on %s" % sw.hostname
		dut = backdoor(sw)
		backup_config(dut)
		dut.child.close()

elif num == 4: # Restore configuration from backup configuration files.  
# !!This will be done later!!!
	dev = input_select_device()
	if dev == 0:
		b = input_select_restore()
		if b == 'Yes':
			pass	
		elif b == 'No' or b == 'NA':
			sys.exit(1)
		print "you are about to restore configuration on ALL devices, are you sure you want to do this?"
		b = input_select_restore()
		if b == 'Yes':
			pass
		elif b == 'No' or b == 'NA':
			sys.exit(1)
		for sw in switch_list:
			dut = backdoor(sw)
			restore_config(dut)
			dut.child.close()
	else:
		sw = switch_list[dev-1]
		print "You are about to backup configuration on %s" % sw.hostname
		b = input_select_restore()
		if b == 'Yes':
			pass	
		elif b == 'No' or b == 'NA':
			sys.exit(1)
		dut = backdoor(sw)
		restore_config(dut)
		dut.child.close()
	
else:
	print "invalid choice, Bye!"
	sys.exit(0)

sys.exit(0)
 

