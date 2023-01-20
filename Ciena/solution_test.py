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
		logfile_name = sw1.host + '.log'
		if '8700' in sw1.host:
			continue	
		fout = open (logfile_name,'w')
		sw1.child.logfile_read = fout 
		sw_send_cmd(sw1,'system shell set global-more off')
		#sw_send_cmd(sw1,'soft show')
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
process_file = 1
sw_8700_C  = switch_list[0]
sw_5160_J = switch_list[1]
sw_5142_A  = switch_list[2]
sw_8700_D = switch_list[3]
sw_8700_E = switch_list[4]
sw_8700_B = switch_list[5]
sw_5142_F = switch_list[6]
sw_3930_G = switch_list[7]

if soak == 1:
	sw_dut  = switch_list[1]
	sw_8700_D = switch_list[3]
	sw_8700_E = switch_list[4]

	#remove this line later
	sw_dut = sw_5142_A
	dut = cienaswitch(sw_dut)
	collect_dut_vc(dut)

	print 'before getting to tunnel'
	######################################################################################
	# Set running flags to run certain test cases
	######################################################################################
	flag_vc = 1                    # flap vc and next hops
	flag_port = 0                  # add and remove ports (AC) from virtual switches
	flag_flush = 0                 # flush mac table and flap mac learning
	flag_lsp_switch = 0            # LSP switch over
	flag_hw_bfd = 0
	flag_pw_switch = 0
	print " ******************************************************************************"
	print " Before testing show DUT port throughput "
	print " ******************************************************************************"
	for i in range (1,2):
		######### Set the running flag to decide which test case to run
		if flag_vc == 1:
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

			ingress_tu = ingress_tunnel(dut)
			egress_tu = egress_tunnel(dut)
			ingress_tu.lsp_disable()
			egress_tu.lsp_disable()
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
			stat_num = 3
			port_stat_cmd (dut, stat_num)

		if flag_port == 1:
			vs_list = virtual_switch_list(dut)
			print_line_case('Detaching all MPLS VC')
			detach_all_vc(vs_list)
			remove_vs_all_port(vs_list)
			sleep (10)
			print_line_stats('Showing MPLS VC after detaching VCs and remvoing ACes from VSes')
			vc_db = mpls_vc(dut, vc_csv)
			vc_db.mpls_vc_stat()
			print_line_case('Attaching all MPLS VC')
			attach_all_vc(vs_list)
			add_vs_all_port(vs_list)
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
			dut.vc_db.flush_mac_all_vc()
			print_line_step('Disabling MAC learning on all virtual switches')
			vs_list.disable_mac_all_vs()
			stat_num = 3
			port_stat_cmd (dut, stat_num)

		if flag_lsp_switch == 1:
			print_line_case('Switch over active LSPs')
			ingress_tu = ingress_tunnel(dut)
			egress_tu = egress_tunnel(dut)
			egress_tu.build_tunnel_all()
			ingress_tu.build_tunnel_all()
			ingress_tu.switchover_tunnel_all()
			egress_tu.switchover_tunnel_all()
			sleep (10)
			stat_num = 5
			port_stat_cmd (dut, stat_num)
			ingress_tu = ingress_tunnel(dut)
			egress_tu = egress_tunnel(dut)
			ingress_tu.lsp_stat()
			egress_tu.lsp_stat()
		if flag_hw_bfd == 1:
			# At current stage every time the 8700 needs to reboot in order to have hardware bfd to work
			print_line_case('Change to hw bfd ingress and egress tunnels')
			dut_8700_D = cienaswitch(sw_8700_D)
			dut_8700_E = cienaswitch(sw_8700_E)
			cmd = 'chassis restart now'
			print_line_step('restarting chassis at 8700_D...')
			sw_send_cmd_nowait(dut_8700_D,cmd)
			dut_8700_D.child.close()
			print_line_step('restarting chassis at 8700_E...')
			sw_send_cmd_nowait(dut_8700_E,cmd)
			dut_8700_E.child.close()
			print_line_step('restarting chassis at 5160_J...')
			cmd = 'chassis reboot now'
			sw_send_cmd_nowait(dut,cmd)
			dut.child.close()
			print_line_step('sleep 10 minutes for all three chassis to come up')
			sleep(600)

			dut = cienaswitch(sw_dut)
			bfd1 = bfd(dut)
			case_turn_on_hw_bfd_all(dut)
			print_line_step('show bfd sessions after turning on hw bfd')
			sleep(10)
			result = sw_show_cmd (dut,'bfd show')
			print result
			
			sleep(20)

			#case_turn_on_hw_bfd_all(dut)
			#result = sw_show_cmd (dut,'bfd show')
			#print result

			#dump_cmd = 'system state-dump ftp-server 10.32.141.50 include-data file-name hw-bfd-test-dump'
			#sw_send_cmd(dut,dump_cmd)
			#should turn off hw_bfd at normal case execution. 
			#case_turn_off_hw_bfd_all(dut)

		if flag_pw_switch == 1:
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
			print result
			sleep (240)            # sleep 4 minutes to wait for things to be stablized

			sw_send_cmd_nowait(dut_8700_E,cmd) # restart 8700_E to make PW switch over back
			sleep (5)
			dut_8700_E.child.close()
			stat_num = 5
			port_stat_cmd (dut, stat_num)
			result = sw_show_cmd (dut,'mpls l2-vpn show')
			print result
			sleep (480)            # sleep 6 minutes for things to settle

			
			

 
sys.exit(0)
