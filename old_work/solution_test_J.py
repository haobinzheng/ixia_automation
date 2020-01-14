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
from class_dut import *
from process_case import *
from utility import *
from test_case import *
from subprocess import Popen, PIPE
import multiprocessing
from multiprocessing import Process
import subprocess
 
 
##################################
#  get host names and IP address 
##################################
logging.basicConfig(format='%(asctime)s %(message)s', filename='solution_test.log', filemode='w',level=logging.DEBUG, datefmt='%m/%d/%Y %I:%M:%S %p')
logging.debug('Test started')
 
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
		sw_send_cmd(sw1,'soft show')
		print "start to show config"
		sw_send_cmd(sw1,'config show br')
		print "done with config show"
		sw_send_cmd(sw1,'system shell set global-more on')

#################################################################
#  Build MPLS VC database  
#################################################################
dut_list = []
online = 0
soak = 1
offline = 0
background = 0

# The DUT is 5160_J
sw_8700_C  = switch_list[0]
sw_5160_J = switch_list[1]
sw_5142_A  = switch_list[2]
sw_8700_D = switch_list[3]
sw_8700_E = switch_list[4]
sw_8700_B = switch_list[5]
sw_5142_F = switch_list[6]
sw_3930_G = switch_list[7]

# Change this 3 lines when you change to bottom half of the network
sw_dut = sw_5160_J
sw_8700_peer_1 = sw_8700_D
sw_8700_peer_2 = sw_8700_E

#clean up whatever messy files and log files 
print_line_step('cleaning up whatever log files to avoid confusion')
#cleanup_begin()

#snmp_walk = 'snmpwalk -Os -c public -v 2c ' + '10.33.42.119'
if background == 1:
	p_snmp = subprocess.Popen("python process_snmp.py ", shell=True)
	p_show = subprocess.Popen("python process_show.py ", shell=True)
	p_op = subprocess.Popen("python process_op.py", shell=True)
	print p_snmp
	print p_show
	print p_op

if soak == 1:

	#change these 2 lines when change DUT
	dut = cienaswitch(sw_dut)

	print 'before getting to tunnel'
	######################################################################################
	# Set running flags to run certain test cases
	######################################################################################
	flag_vc = 0                    # flap vc and next hops
	flag_vs_attach = 0             # add and remove ports (AC) from virtual switches
	flag_flush = 0                 # flush mac table and flap mac learning
	flag_lsp_switch = 0           # LSP switch over
	flag_hw_bfd = 0
	flag_pw_failover = 0
	flag_lsp_add_drop = 0
	flag_max_telnet = 0
	flag_swbfd_profiles = 0
	flag_pw_switch = 0
	flag_pw_scaleout = 0
	flag_pw_stats = 1
	print " ******************************************************************************"
	print " Before testing show DUT port throughput "
	print " ******************************************************************************"
	for i in range (1,2):
		print "\n****************************** run time = %d **********************************" % i
		######### Based on the flags, decide which test case to run
		if flag_vc == 1:
			collect_dut_vc(dut)
			print_line_step('show bfd sessions at the beginning of run')
			bfd_result = sw_show_cmd(dut,'bfd show')
			print bfd_result
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
			sleep (5)
			stat_num = 3
			port_stat_cmd (dut, stat_num)
		
			print "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
			print "			Enabling mpls vc..........."
			print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
			flap_mpls_vc(dut, 'enable')
			stat_num = 3
			port_stat_cmd (dut, stat_num)
	
			sleep(10)
			result = sw_show_cmd (dut,'bfd show')
			print result
			print_line_case('Diaiableing GMPLS TP-TUNNELS..........')
			ingress_tu = ingress_tunnel(dut)
			egress_tu = egress_tunnel(dut)
			ingress_tu.lsp_stat()
			egress_tu.lsp_stat()
			ingress_tu.lsp_disable()
			egress_tu.lsp_disable()
			sleep (10)
			ingress_tu = ingress_tunnel(dut)
			egress_tu = egress_tunnel(dut)
			ingress_tu.lsp_stat()
			egress_tu.lsp_stat()
			print_line_stats('Show traffic stats after disabling GMPLS TUNNELS')
			port_stat_cmd (dut, stat_num)

			ingress_tu.lsp_enable()
			egress_tu.lsp_enable()
			sleep (10)
			ingress_tu = ingress_tunnel(dut)
			egress_tu = egress_tunnel(dut)
			ingress_tu.lsp_stat()
			egress_tu.lsp_stat()
			print "After enabling mpls vc, sleep 10 seconds"
			port_stat_cmd (dut, stat_num)
			print "\n Show traffic stats after disabling GMPLS TUNNELS"	
			stat_num = 3
			port_stat_cmd (dut, stat_num)
			print_line_step('show bfd sessions at the end of run')
			bfd_result = sw_show_cmd(dut,'bfd show')
			print bfd_result

		if flag_vs_attach== 1:
			vs_list = virtual_switch_list(dut)
			print_line_case('Detaching all MPLS VC')
			detach_all_vc(vs_list)
			remove_vs_all_port(vs_list)
			sleep (10)
			print_line_stats('Showing MPLS VC after detaching VCs and remvoing ACes from VSes')
			vc_db = collect_dut_vc(dut)
			#vc_db = mpls_vc(dut, vc_csv)
			dut.vc_db.mpls_vc_stat()
			print_line_case('Attaching all MPLS VC')
			attach_all_vc(vs_list)
			add_vs_all_port(vs_list)
			#for time in range(0,1000):
			#	dut.vc_db.change_status_interval_all(str(time))
			dut.vc_db.turn_pw_reversion_all_off()
			dut.vc_db.turn_pw_reversion_all_on()
			sleep(10)
			print_line_stats('Showing MPLS VC after attaching VCs from VS and adding ACes to VSes')
			stat_num = 3
			port_stat_cmd (dut, stat_num)

		if flag_flush ==1:
			print_line_stats("show ports throughput before flushing mac tables")
			stat_num = 3
			port_stat_cmd (dut, stat_num)
			vs_list = virtual_switch_list(dut)
			print_line_case('Flush MAC tables aross all Virtual Switches and VCes')
			print_line_step('Enabling MAC learning on all virtual switches')
			vs_list.enable_mac_all_vs()
			print_line_step('Flushing MAC tables on all virtual switches')
			vs_list.flush_mac_all_vs()
			print_line_step('Flushing MAC address on all MPLS VCes')
			vc_db = collect_dut_vc(dut)
			dut.vc_db.flush_mac_all_vc()
			print_line_step('Disabling MAC learning on all virtual switches')
			vs_list.disable_mac_all_vs()
			stat_num = 3
			port_stat_cmd (dut, stat_num)

		if flag_lsp_switch == 1:
			stat_num = 3
			port_stat_cmd (dut, stat_num)
			print_line_case('Switch over active LSPs')
			ingress_tu = ingress_tunnel(dut)
			egress_tu = egress_tunnel(dut)
			print_line_step('collecting information for each individual LSPs')
			ingress_tu.build_tunnel_all()
			egress_tu.build_tunnel_all()
			ingress_tu.switchover_tunnel_all()
			egress_tu.switchover_tunnel_all()
			sleep (10)
			stat_num = 5
			port_stat_cmd (dut, stat_num)
			ingress_tu = ingress_tunnel(dut)
			egress_tu = egress_tunnel(dut)
			ingress_tu.lsp_stat()
			egress_tu.lsp_stat()


		if flag_swbfd_profiles == 1:
			print_line_case('Sweep across BFD profiles with different BFD intervals')
			dut_8700_peer_1 = cienaswitch(sw_8700_peer_1)
			dut_8700_peer_2 = cienaswitch(sw_8700_peer_2)
			#cmd = 'chassis restart now'
			#print_line_step('restarting chassis at 8700 peer 1...')
			#sw_send_cmd_nowait(dut_8700_peer_1,cmd)
			#sleep(5)
			#dut_8700_peer_1.child.close()
			#print_line_step('restarting chassis at 8700 peer 2...')
			#sw_send_cmd_nowait(dut_8700_peer_2,cmd)
			#sleep(5)
			dut_8700_peer_2.child.close()
			#print_line_step('restarting DUT chassis ...')
			#cmd = 'chassis reboot now'
			#sw_send_cmd_nowait(dut,cmd)
			#sleep(5)
			dut.child.close()
			#print_line_step('sleep 10 minutes for all three chassis to come up')
			#sleep(600)

			dut = cienaswitch(sw_dut)
			dut.child.logfile_read = sys.stdout
			get_show_bfd(dut)
			sw_send_cmd(dut,'software show')
			case_sweeping_sw_bfd_profiles(dut)
			sleep(10)
			print_line_step('show bfd sessions after one round change of bfd profile')
			result = sw_show_cmd (dut,'bfd show')
			print result
			result = sw_show_cmd (dut,'bfd session show')
			print result
			sleep(10)
			result = sw_show_cmd (dut,'bfd show')
			print result
			result = sw_show_cmd (dut,'bfd session show')
			print result
			sleep(10)
			result = sw_show_cmd (dut,'bfd show')
			print result
			result = sw_show_cmd (dut,'bfd session show')
			print result

			# excute once and leave the system at the current state. remove the following line later!
			# excute this line for the 2nd time to make sure the DUT doesn't crash
			#case_turn_on_hw_bfd_all(dut)
			#result = sw_show_cmd (dut,'bfd show')
			#print result

			#dumpfile = 'hw-bfd-test-dump-' + i
			#dump_cmd = 'system state-dump ftp-server 10.32.141.50 include-data file-name ' + dumpfile
			#sw_send_cmd(dut,dump_cmd)
			#sys.exit(0)
			#should turn off hw_bfd at normal case execution. 
			#case_turn_off_hw_bfd_all(dut)

		if flag_hw_bfd == 1:
			# At current stage every time the 8700 needs to reboot in order to have hardware bfd to work
			print_line_case('Change to hw bfd ingress and egress tunnels')
			#dut_8700_D = cienaswitch(sw_8700_D)
			#dut_8700_E = cienaswitch(sw_8700_E)
			dut_8700_peer_1 = cienaswitch(sw_8700_peer_1)
			dut_8700_peer_2 = cienaswitch(sw_8700_peer_2)
			cmd = 'chassis restart now'
			print_line_step('restarting chassis at 8700 peer 1...')
			#sw_send_cmd_nowait(dut_8700_peer_1,cmd)
			#sleep(5)
			dut_8700_peer_1.child.close()
			print_line_step('restarting chassis at 8700 peer 2...')
			#sw_send_cmd_nowait(dut_8700_peer_2,cmd)
			#sleep(5)
			dut_8700_peer_2.child.close()
			print_line_step('restarting DUT chassis ...')
			cmd = 'chassis reboot now'
			#sw_send_cmd_nowait(dut,cmd)
			#sleep(5)
			dut.child.close()
			print_line_step('sleep 10 minutes for all three chassis to come up')
			#sleep(600)

			dut = cienaswitch(sw_dut)
			dut.child.logfile_read = sys.stdout
			get_show_bfd(dut)
			sw_send_cmd(dut,'software show')
			bfd1 = bfd(dut)
			case_turn_on_hw_bfd_all(dut)
			print_line_step('show bfd sessions after turning on hw bfd')
			sleep(10)
			result = sw_show_cmd (dut,'bfd show')
			print result
			
			sleep(20)

			# excute once and leave the system at the current state. remove the following line later!
			# excute this line for the 2nd time to make sure the DUT doesn't crash
			#case_turn_on_hw_bfd_all(dut)
			#result = sw_show_cmd (dut,'bfd show')
			#print result

			#dumpfile = 'hw-bfd-test-dump-' + i
			#dump_cmd = 'system state-dump ftp-server 10.32.141.50 include-data file-name ' + dumpfile
			#sw_send_cmd(dut,dump_cmd)
			#sys.exit(0)
			#should turn off hw_bfd at normal case execution. 
			case_turn_off_hw_bfd_all(dut)

		if flag_pw_failover == 1:
			dut_8700_D = cienaswitch(sw_8700_D)
			dut_8700_E = cienaswitch(sw_8700_E)

			cmd = 'chassis restart now'
			print_line_step('restarting chassis ...')
			sw_send_cmd_nowait(dut_8700_D,cmd)
			sleep (5)
			dut_8700_D.child.close()
			stat_num = 5
			port_stat_cmd (dut, stat_num)
			result = sw_show_cmd (dut,'mpls l2-vpn show')
			#print result
			sleep (240)            # sleep 4 minutes to wait for things to be stablized

			sw_send_cmd_nowait(dut_8700_E,cmd) # restart 8700_E to make PW switch over back
			sleep (5)
			dut_8700_E.child.close()
			stat_num = 5
			port_stat_cmd (dut, stat_num)
			result = sw_show_cmd (dut,'mpls l2-vpn show')
			#print result
			sleep (480)            # sleep 6 minutes for things to settle

		if flag_lsp_add_drop == 1:
			print "polling background processes"
			print_line_case('MPLS LSPs Add and Remove')
			print_line_step('Getting LSPs information ...')
			ingress_tu = ingress_tunnel(dut)
			egress_tu = egress_tunnel(dut)
			ingress_tu.lsp_stat()
			egress_tu.lsp_stat()
			egress_tu.build_tunnel_all()
			ingress_tu.build_tunnel_all()
			print_line_step('Removing all LSPs ...')
			#ingress_tu.delete_tunnel_some(100)
			#egress_tu.delete_tunnel_some(100)
			ingress_tu.delete_tunnel_all()
			egress_tu.delete_tunnel_all()
			print_line_step('Configuring all LSPs ...')
			ingress_tu.create_tunnel_all()
			egress_tu.create_tunnel_all()

		if flag_max_telnet == 1:
			telnet_list = []
			for i in range(1,12):
				telnet = cienaswitch(sw_dut)
				sleep(2)
				telnet_list.append(telnet)
			input_for_exit()

		if flag_pw_switch == 1:
			mpls_pw = mpls_l2vpn(dut)
			mpls_pw.mpls_vc_stats()
			mpls_pw.build_mpls_l2vpn_instances()
			mpls_pw.protection_switchover_all()
			mpls_pw = mpls_l2vpn(dut)
			mpls_pw.mpls_vc_stats()
			#dumpfile = 'pw_switch_dump_' + str(i)
			#dump_cmd = 'system state-dump ftp-server 10.32.141.50 include-data file-name ' + dumpfile
			#sw_send_cmd(dut,dump_cmd)
			sleep(30)
			
		if flag_pw_scaleout == 1:
			num = 3000
			#dut_J = CN_5160_J(sw_5160_J)
			#dut_J.configuration_vs(num)
			#dut_J.configuration_pw(num)
			#dut_J.configuration_attach_vs(num)
			#dut_J.configuration_attach_port(num)
			#dut_D = CN_8700_D(sw_8700_D)
			#dut_D.configuration_vs(num)
			#dut_D.configuration_pw(num)
			#dut_D.configuration_attach_vs(num)
			dut_E = CN_8700_E(sw_8700_E)
			dut_E.configuration_vs(num)
			dut_E.configuration_pw(num)
			dut_E.configuration_attach_vs(num)
			mpls_pw = mpls_l2vpn(dut_J)
			mpls_pw.mpls_vc_stats()

		if flag_pw_stats == 1:
			for sw in switch_list:
				dut = cienaswitch(sw)
				mpls_pw = mpls_l2vpn(dut)
				mpls_pw.mpls_vc_stats()
				
			

if background == 1:
	print "this is the end of the script, killing all process"
	p_show.kill()
	p_snmp.kill()

#clean up all the temperary files and log files
print "cleaning up and exit"
#cleanup_end()

sys.exit(0)
