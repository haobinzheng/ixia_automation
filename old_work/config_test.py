import os
import pexpect
import sys
import time
import datetime
import logging
import csv
import re
from switch_class import *
from utility import *
from test_case import *
from subprocess   import Popen, PIPE
 
 
##################################
#  get host names and IP address 
##################################
 
device_file = '5160_1_J.host'

routerFile = open(device_file, 'r')
switch_dev = [a for a in routerFile]


switch_list =  []
for sw in switch_dev:
   sw_obj = switch(sw)
   switch_list.append(sw_obj) 

#####################################################################################
# Keep an inventory for the devices 
# including software version, configuration etc
# The configuration test needs to have the following procedure:
# 0) The DUT has the correct configuration. 
# !!!!!!!!!!!!!! If DUT dosn't have correct configuration set archieve = 0
# 1) Run the scrip with archieve = 1, the script will archive the good configuration
# 2) The script will set the initial load configuration to the initial configuration
# 3) Then reboot the DUT. The DUT will boot up with minimum configuration
# 4) After the DUT is booted up, the script will configuration the DUT from file
# 5) Do not reboot the DUT after the configuration is done 
#####################################################################################
archieve = 0
if archieve == 1: 
	for  s in switch_list: 
		sw1 = cienaswitch(s)
		original_config = s.original_config_file
		print original_config
		processed_config = s.processed_config_file
		#For the 6.13 testing we dont want to archive 8700
		if '8700' in sw1.host:
			continue	
		print "start to show config"
		sw_read_cmd(sw1,original_config,'config show br')
		print "done with config show"
		sw1.child.sendline('config set default-load-filename initial-config')
		sw1.child.sendline('chassis reboot now')
		print "wait for 800 seconds for chassis to reboot"
		sleep(600)
		sw1.child.close()

for s in switch_list:
		sw1 = cienaswitch(s)
		#sw1.child.logfile_send = sys.stdout
		original_config = s.original_config_file
		processed_config = s.processed_config_file
		remove_logical_id(original_config,processed_config)
		f = open(processed_config)
		lines = f.readlines()
		print "\nconfiguring %s from configuration file" % s.hostname
		for cmd in lines:
			#sw1.child.logfile_send = sys.stdout
			sw1.child.sendline(cmd)
			#sleep(0.1)
		sw1.child.close()

sys.exit(1)
#################################################################
#  process configuration file  
#################################################################
dut_list = []
online = 0
soak = 0
offline = 0
process_file = 1


if offline == 1:
	#lsp_log = '5160_1_J_lsp.log'
	#process_log_file(lsp_log)	# Process the log file to remove not needed stuff

	dut = cienaswitch(switch_list[1])
	print "+++++++++++++ This is start of show vs processing"
	show_vs(dut)
	get_vs_name_vc(dut,'VS-F001-S0001')
	#i_lsp_list = read_lsp(lsp_log, 'INGRESS')
	#print "++++++++++ This is egress lsp"
	#e_lsp_list = read_lsp(lsp_log, 'EGRESS')
	#print "++++++++++ This is transit lsp"
	#t_lsp_list = read_lsp(lsp_log, 'TRANSIT')
	#ingress_tu = ingress_tunnel(dut)
	#ingress_tu.get_tunnel_details()
	#egress_tu = egress_tunnel(dut)
	#transit_tu = transit_tunnel(dut)

	#ingress_tu.lsp_stat()
	#disable ingress tunnel
	#ingress_tu.lsp_disable()
	#ingress_tu = ingress_tunnel(dut)
	#ingress_tu.lsp_stat()

	#ingress_tu.lsp_enable()
	#ingress_tu = ingress_tunnel(dut)
	#ingress_tu.lsp_stat()

	#egress_tu.lsp_stat()
	#egress_tu.lsp_disable()
	#gress_tu.lsp_stat()
	#gress_tu = egress_tunnel(dut)
	#gress_tu.lsp_enable()
	#gress_tu.lsp_stat()
	#transit_tu.show_tunnel()

if online == 1:
	for s in switch_list:
		dut = cienaswitch(s)
		sw_send_cmd(dut,'system shell set global-more off')
		vc_log = dut.host + '_vc' + '.log'
		lsp_log = dut.host + '_lsp' + '.log'
		vc_csv = dut.host + '_vc' + '.csv'
		lsp_csv = dut.host + '_lsp' + '.csv'
		result = sw_read_cmd(dut, vc_log, 'mpls l2-vpn show')
		result_lsp = sw_read_cmd(dut, lsp_log, 'gmpls tp-tunnel show')
		sw_send_cmd(dut,'system shell set global-more on')
		process_log_file(vc_log)	# Process the log file to remove not needed stuff
		vc_str = 'F00'				# The string being used to identify VC name
		lsp_str= 'Sta'				# The string being used to identify LSP name
		create_vc_csv(vc_log, vc_csv,vc_str, lsp_str)
		vc_db = mpls_vc(dut, vc_csv)
		dut_list.append(dut)
		dut.vc_db = vc_db 
		vc_db.mpls_vc_stat()
		#vc_db.show_mpls_vc_name()	

	dut  = dut_list[1]
	vc_flap = 0
	stat_num = 4
	port_stat_cmd (dut, stat_num)
	print "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
	print "			Disabling mpls vc..........."
	print "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
	#flap_mpls_vc(dut, 'disable')
	#show port statistics after disabling vcs ###########
	print "\n+++++++After disabling mpls vc, sleep 10 seconds"
	sleep (10)
	stat_num = 4
	port_stat_cmd (dut, stat_num)

	print "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
	print "			Enabling mpls vc..........."
	print "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
	#flap_mpls_vc(dut, 'enable')

	#show port statistics after enabling vcs ###########
	print "\n++++++++After enabling mpls vc, sleep 10 seconds"
	stat_num = 4
	port_stat_cmd (dut, stat_num)


	print "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
	print "			disabling mpls vc next hop..........."
	print "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
	flap_vc_nh(dut, 'disable')

	#show port statistics after enabling vcs ###########
	print "\n++++++++After disabling mpls vc next hop tunnels, sleep 10 seconds"
	stat_num = 4
	port_stat_cmd (dut, stat_num)



	print "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
	print "			Enabling mpls vc next hop..........."
	print "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
	flap_vc_nh(dut, 'enable')

	#show port statistics after enabling vcs ###########
	print "\n++++++++After enabling mpls vc next hop tunnels, sleep 10 seconds"
	stat_num = 4
	port_stat_cmd (dut, stat_num)

if soak == 1:
	for s in switch_list:
		dut = cienaswitch(s)
		dut_list.append(dut)
		sw_send_cmd(dut,'system shell set global-more off')
		vc_log = dut.host + '_vc' + '.log'
		vc_csv = dut.host + '_vc' + '.csv'
		result = sw_read_cmd(dut, vc_log, 'mpls l2-vpn show')
		sw_send_cmd(dut,'system shell set global-more on')
		process_log_file(vc_log)	# Process the log file to remove not needed stuff
		vc_str = 'F00'				# The string being used to identify VC name
		lsp_str= 'Sta'				# The string being used to identify LSP name
		create_vc_csv(vc_log, vc_csv,vc_str, lsp_str)
		vc_db = mpls_vc(dut, vc_csv)
		dut.vc_db = vc_db 
		vc_db.mpls_vc_stat()
		#vc_db.show_mpls_vc_name()	

	dut  = dut_list[1]
	#Collect Ingress And Egress Tunnels information
	vs_list = virtual_switch_list(dut)
	print_line_case('Detaching all MPLS VC')
	#detach_all_vc(vs_list)
	remove_vs_all_port(vs_list)
	sleep (10)
	print_line_stats('Showing MPLS VC after detaching VCs and remvoing ACes from VSes')
	vc_db = mpls_vc(dut, vc_csv)
	vc_db.mpls_vc_stat()
	print_line_case('Attaching all MPLS VC')
	#attach_all_vc(vs_list)
	add_vs_all_port(vs_list)
	print_line_stats('Showing MPLS VC after attaching VCs from VS and adding ACes to VSes')
	#ingress_tu = ingress_tunnel(dut) 	
	#ingress_tu.show_tunnel_stats()
	#flap_all_ingress_tunnel(dut)
	sys.exit(0)

	#egress_tu = egress_tunnel(dut)

	print 'before getting to tunnel'
	#ingress_tu.lsp_stat()
	#egress_tu.lsp_stat()
	print " ******************************************************************************"
	print " Before testing show DUT port throughput "
	print " ******************************************************************************"
	for i in range (1,2000):
		stat_num = 3
		port_stat_cmd (dut, stat_num)
		print "\n****************************** run time = %d **********************************" % i
		stat_num = 3
		port_stat_cmd (dut, stat_num)
		print "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
		print "			Disabling mpls vc..........."
		print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
		flap_mpls_vc(dut, 'disable')
		#show port statistics after disabling vcs ###########
		print "\n++++++++++After disabling mpls vc, sleep 10 seconds"
		sleep (10)
		stat_num = 3
		port_stat_cmd (dut, stat_num)
	
		print "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
		print "			Enabling mpls vc..........."
		print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
		flap_mpls_vc(dut, 'enable')
		stat_num = 3
		port_stat_cmd (dut, stat_num)

		print "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
		print "			Diableing GMPLS TP-TUNNELS..........."
		print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

		ingress_tu.lsp_disable()
		egress_tu.lsp_disable()
		ingress_tu = ingress_tunnel(dut)
		egress_tu = egress_tunnel(dut)
		ingress_tu.lsp_stat()
		egress_tu.lsp_stat()
		print "\n Show traffic stats after disabling GMPLS TUNNELS"	
		port_stat_cmd (dut, stat_num)

		ingress_tu.lsp_enable()
		egress_tu.lsp_enable()
		ingress_tu = ingress_tunnel(dut)
		egress_tu = egress_tunnel(dut)
		ingress_tu.lsp_stat()
		egress_tu.lsp_stat()
		print "After enabling mpls vc, sleep 10 seconds"
		port_stat_cmd (dut, stat_num)
		print "\n Show traffic stats after disabling GMPLS TUNNELS"	
		port_stat_cmd (dut, stat_num)


 
sys.exit(0)
