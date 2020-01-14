import switch_class
import os
import pexpect
import sys
import time
import datetime
import logging
import signal
import csv
import re
from subprocess   import Popen, PIPE
import multiprocessing
from multiprocessing import Process
import subprocess
from switch_class import *
from lib import *

def cleanup_begin():
	my_pid = os.getpid()
	p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
	out, err = p.communicate()
	for line in out.splitlines():
		if 'snmp' in line:
			pid = int(line.split(None, 1)[0])
			os.kill(pid, signal.SIGKILL)
		if 'Python' in line:
			pid = int(line.split(None, 1)[0])
			if pid != my_pid:
				os.kill(pid, signal.SIGKILL)
	Popen(["rm " +  "*.log"], shell=True, stdout=PIPE).communicate()
	Popen(["rm " +  "*.bak"], shell=True, stdout=PIPE).communicate()
	Popen(["rm " +  "*.csv"], shell=True, stdout=PIPE).communicate()
	Popen(["rm " +  "temp*.*"], shell=True, stdout=PIPE).communicate()
		
def cleanup_end():
	p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
	out, err = p.communicate()
	for line in out.splitlines():
		if 'Python' in line:
			pid = int(line.split(None, 1)[0])
			os.kill(pid, signal.SIGKILL)
		if 'snmp' in line:
			pid = int(line.split(None, 1)[0])
			os.kill(pid, signal.SIGKILL)
	Popen(["rm " +  "*.log"], shell=True, stdout=PIPE).communicate()
	Popen(["rm " +  "*.bak"], shell=True, stdout=PIPE).communicate()
	Popen(["rm " +  "*.csv"], shell=True, stdout=PIPE).communicate()
	Popen(["rm " +  "temp*.*"], shell=True, stdout=PIPE).communicate()

#def seek_lock(lck_file):
#	while os.path.exists(lck_file):
#		print "wait until someone release the lock"
#		sleep (3)
#	if not os.path.exists(lck_file):
#		file = lck_file
#		open('file', 'w').close()
#
##def release_lock(lck_file):
#	if os.path.exists(lck_file):
#		file = lck_file
#		os.remove(file)
	

def start_snmp(sw_dut):
	snmp_walk = 'snmpwalk -Os -c public -v 2c ' + sw_dut.ip + ' > /dev/null '
	p_snmp = subprocess.Popen(snmp_walk, shell=True)
	return p_snmp

def start_sweepshow():
	p_show = subprocess.Popen("python process_show.py > /dev/null ", shell=True)
	return p_show

# poll process existance and retart
def poll_snmp(p_snmp):
	p = p_snmp
	if p_snmp.poll() != None:
		print "snmp proces doesn't exist, restart the process"
		p_snmp = start_snmp()
		return p_snmp
	else:
		return p


def poll_sweepshow(p_show):
	p = p_show
	if p_show.poll() != None:
		print "background show proces doesn't exist, restart the process"
		p_show = start_sweepshow()
		return p_show
	else:
		return p


def read_lsp(file, lsp_type):
	with open(file, mode = 'r') as infile:
		lsp_list = []
		found = 0
		begin = 1
		for line in infile:
			if lsp_type in line:
				found = 1
				begin = 0
				infile.next()
				infile.next()
				infile.next()
				
			elif found == 1 and begin == 0:
				if '-----------------' in line:
					return lsp_list	
				else:
					line = line.strip()
					lsp = line.split(',')	
					lsp_list.append(lsp)
					#print lsp
			else:
				#sys.exit(1)
				pass
		return lsp_list

def remove_dash_line(list):
	i = 0
	for item in list:
		if '----' in item:
			list.pop(i)
		i += 1
	return list

def remove_crapy_line(list):
	newlist = []
	for line in list:
		line = line.strip('\r')
		line = line.strip('|')
		line = line.strip()
		line_new = line.replace("/","|")
		newlist.append(line_new)
	return newlist

def remove_crapy_line_2(list):
	newlist = []
	for line in list:
		line = line.strip('\r')
		line = line.strip('|')
		line = line.strip()
		newlist.append(line)
	return newlist

def is_dash_line(line):
	if '----' in line:
		return 'True'
	else:
		return 'False'

def remove_head_line(list,str):
	i = 0
	for item in list:
		if str in item:
			list.pop(i)
		i += 1
	return list

def print_line_step(str):
		print "\n----------------------- Executing: %s ---------------------------------------" % str

def print_line_case(str):
		print "\n======================= Test Case: %s ========================================" % str

def print_line_stats(str):
		print "\n####################### Statistics: %s ##########################################" % str

def print_line_test(str):
		print "\n!!!!!!!!!!!!!!!!!!!!!! Debugging:  %s !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" % str

def get_all_ingress_tunnel(dut):
	ingress_tu = ingress_tunnel(dut)
	ingress_tu.get_tunnel_details()
	hhcorout_in_lsp_list = []
	for tunnel_detail in ingress_tu.lsp_detail_list:
		in_lsp = corout_ingress_tunnel(dut, tunnel_detail)
		#in_lsp.print_tunnel_details()
		corout_in_lsp_list.append(in_lsp)
	return corou_in_lsp_list

def flap_all_ingress_tunnel(dut):
	lsp_list = get_all_ingress_tunnel(dut)
	for lsp in lsp_list:
		lsp.disable_tunnel_lsp()

	sleep(10)
	ingress_tu = ingress_tunnel(dut)
	print_line_step()
	ingress_tu.show_tunnel_stats()
	
def show_configuration(dut):
	cmd = 'config show br'
	result = sw_show_cmd(dut,cmd)
	print result
		
def input_for_exit():
	while True:
		print "After creating the max telnet session, do you want to exit?"
		while True:
			#Input .lower() up here so I didn't have to call it multiple times
			replay = raw_input("Play again? ").lower()
			print replay
			if replay in ("yes", "y"):
				break
			elif replay in ("no", "n"):
				raise SystemExit
			else:
				print "Sorry, I didn't understand that."

def input_test_cases():
	print "==============================================================="
	print "Please enter test case number, each time just enter one number:"
	print "		0 --- Execute all test cases"
	print "		1 --- Test case 1: Flap VC and the next hops"
	print "		2 --- Test case 2: Add and Remove ports(AC) and VC to VS"
	print "		3 --- Test case 3: Flush MAC table and MAC learning"
	print "		4 --- Test case 4: MPLS Static LSP Switch Over"
	print "		5 --- Test case 5: Transform software BFD to hardware BFD"
	print "		6 --- Test case 6: Node failure triggering PW failover"
	print "		7 --- Test case 7: Remove And Add MPLS LSP"
	print "		8 --- Test case 8: Test max number of telnet sessions"
	print "		9 --- Test case 9: Change software BFD intervals from 3.3ms to 10sec"
	print "		10 --- Test case 10: MPLS PW manual switchover"
	print "		11 --- Exucute"

	case = raw_input('Enter a test case number [0-10]: ')
	case_num = int(case)
	if case_num > 11:
		print "this is wrong"
	else:
		return case_num

def input_mgmt():
	print "==============================================================="
	print "Please select what management action you want to take:"
	print "		1 --- Change Password on device(s)"
	print "		2 --- Recover Password on devices(s)"
	print "		3 --- Backup configuration for device(s)"
	print "		4 --- Restore configuration for device(s)"
	

	case = raw_input('Enter a number [1-4]: ')
	num = int(case)
	if num > 5:
		print "this is wrong"
		sys.exit(0)
	else:
		return num

def input_select_device():
	print "==============================================================="
	print "Which device do you want to select?"
	print "		0 --- All devices"
	print "		1 --- CN_8700_C"
	print "		2 --- CN_5160_J"
	print "		3 --- CN_5142_A"
	print "		4 --- CN_8700_D"
	print "		5 --- CN_8700_E"
	print "		6 --- CN_8700_B"
	print "		7 --- CN_5142_F"
	print "		8 --- CN_3930_G"

	case = raw_input('Enter a number [0-8]: ')
	num = int(case)
	if num > 8:
		print "this is wrong"
		sys.exit(0)
	else:
		return num

def input_select_backup():
	print "==============================================================="
	print "Do you want to backup the configuration of the selected device?"
	print "		1 --- Yes"
	print "		2 --- No"

	case = raw_input('Enter a number [1-2]: ')
	num = int(case)
	if num > 2:
		print "this is wrong choice, bye"
		sys.exit(0)
		
	if num == 1:
		return 'Yes'
	elif num == 2:
		return 'No'
	else:
		return 'NA'


def input_select_restore():
	print "==============================================================="
	print "Do you want to restore the configuration of the selected device?"
	print "		1 --- Yes"
	print "		2 --- No"

	case = raw_input('Enter a number [1-2]: ')
	num = int(case)
	if num > 2:
		print "this is wrong choice, bye"
		sys.exit(0)
		
	if num == 1:
		return 'Yes'
	elif num == 2:
		return 'No'
	else:
		return 'NA'

def backup_config(dut):
	logfile_name = '/Users/haobinzheng/Python/config/' + dut.host + '.log'
	fout = open (logfile_name,'w')
	dut.sw_send_cmd('system shell set global-more off')
	dut.child.logfile_read = fout
	print "start to show config"
	dut.sw_log_cmd('config show br')
	print "done with config show"
	dut.sw_send_cmd('system shell set global-more on')
	infile = logfile_name
	outfile = infile + '.processed'
	remove_logical_id(infile,outfile)
	fout.close()


def restore_config_slow(dut):
	logfile_name = '/Users/haobinzheng/Python/config/' + dut.host + '.log'
	processed_config = logfile_name + '.processed'
	f = open(processed_config)
	lines = f.readlines()
	print "\nconfiguring %s from configuration file" % dut.host
	for cmd in lines:
		dut.child.logfile_send = sys.stdout
		dut.child.sendline(cmd)
		#sleep(0.1)

def restore_config(dut):
	log = dut.host + '.log'
	processed_log = log + '.processed'
	path = '/Users/haobinzheng/Python/config/' 
	processed_config = path + processed_log
	f = open(processed_config)
	import netifaces as ni
	#At macbook en0 is the wifi interface, when porting to linux, make sure to make a change here
	#Should change this following line based on OS 
	os = 'mac'
	if os == 'mac':
		ip = ni.ifaddresses('en0')[2][0]['addr']
		print ip  # sh
		if dut.chassis == '8700':
			cmd = 'configuration install ftp-server ' + ip +  ' login-id haobinzheng password SurVive2015 filename ' + processed_config
			dut.child.sendline(cmd)
			dut.child.expect([dut.prompt2, dut.prompt])
		else:
			cmd = 'configuration install ftp-server ' + ip +  ' login-id haobinzheng echoless-password filename ' + processed_config
			print cmd
			dut.child.sendline(cmd)
			dut.child.expect('Enter Password:')
			dut.child.sendline('SurVive2015')
			dut.child.expect(["Verify Password:"])
			dut.child.sendline('SurVive2015')
			dut.child.expect([dut.prompt2, dut.prompt])
		cmd = 'configuration reset-to-user-config filename ' + processed_log
		print cmd
		dut.child.sendline(cmd)
		dut.child.expect([dut.prompt2, dut.prompt])

def get_show_user(dut):
	cmd = 'user show'
	show_result = sw_show_cmd(dut,cmd)
	list = show_result.split('\n')
	user_list = []
	user_list = get_head_block(list,'Username')
	for line in user_list:
		user_dict = {}
		key,val = line.split('|')
		user_dict[key.strip()] = val.strip()
		user_list.append(user_dict)

	return user_list
