# from ixia_lib import *

# chassis = "10.105.241.234"
# ixnetwork = "10.105.19.19:8004"
# #tcl_server=${Ixia Tcl Srv} | device=${Ixia Chasis} | ixnetwork_tcl_server=${Ixia IxNetwork Srv} | port_list=${Ixia ports} | reset=1 |
# portsList = ['1/1','1/2','1/3','1/4']
# connect_status = ixia_connect(tcl_server=chassis,device=chassis,ixnetwork_tcl_server=ixnetwork,port_list=portsList,reset=1)

# port_handle = connect_status['vport_list']

# ports = connect_status['vport_list'].split()

# port_1 = port_handle.split(' ')[0]
# port_2 = port_handle.split(' ')[1]
# port_3 = port_handle.split(' ')[2]
# port_4 = port_handle.split(' ')[3]

# port_handle = ('port_1','port_2','port_3','port_4')




################################################################################
# Version 1.0    $Revision: 1 $                                                #
#                                                                              #
#    Copyright  1997 - 2015 by IXIA                                            #
#    All Rights Reserved.                                                      #
#                                                                              #
#    Revision Log:                                                             #
#    01/20/2014 - Andrei Zamisnicu - created sample                            #
#                                                                              #
################################################################################

################################################################################
#                                                                              #
#                                LEGAL  NOTICE:                                #
#                                ==============                                #
# The following code and documentation (hereinafter "the script") is an        #
# example script for demonstration purposes only.                              #
# The script is not a standard commercial product offered by Ixia and have     #
# been developed and is being provided for use only as indicated herein. The   #
# script [and all modifications enhancements and updates thereto (whether      #
# made by Ixia and/or by the user and/or by a third party)] shall at all times #
# remain the property of Ixia.                                                 #
#                                                                              #
# Ixia does not warrant (i) that the functions contained in the script will    #
# meet the users requirements or (ii) that the script will be without          #
# omissions or error-free.                                                     #
# THE SCRIPT IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND AND IXIA         #
# DISCLAIMS ALL WARRANTIES EXPRESS IMPLIED STATUTORY OR OTHERWISE              #
# INCLUDING BUT NOT LIMITED TO ANY WARRANTY OF MERCHANTABILITY AND FITNESS FOR #
# A PARTICULAR PURPOSE OR OF NON-INFRINGEMENT.                                 #
# THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE SCRIPT  IS WITH THE #
# USER.                                                                        #
# IN NO EVENT SHALL IXIA BE LIABLE FOR ANY DAMAGES RESULTING FROM OR ARISING   #
# OUT OF THE USE OF OR THE INABILITY TO USE THE SCRIPT OR ANY PART THEREOF     #
# INCLUDING BUT NOT LIMITED TO ANY LOST PROFITS LOST BUSINESS LOST OR          #
# DAMAGED DATA OR SOFTWARE OR ANY INDIRECT INCIDENTAL PUNITIVE OR              #
# CONSEQUENTIAL DAMAGES EVEN IF IXIA HAS BEEN ADVISED OF THE POSSIBILITY OF    #
# SUCH DAMAGES IN ADVANCE.                                                     #
# Ixia will not be required to provide any software maintenance or support     #
# services of any kind (e.g. any error corrections) in connection with the     #
# script or any part thereof. The user acknowledges that although Ixia may     #
# from time to time and in its sole discretion provide maintenance or support  #
# services for the script any such services are subject to the warranty and    #
# damages limitations set forth herein and will not obligate Ixia to provide   #
# any additional maintenance or support services.                              #
#                                                                              #
################################################################################

################################################################################
#                                                                              #
# Description:                                                                 #
#   The script below walks through the workflow of an AppLibrary end to end    #	
#	test, using the below steps:											   #	
#		1. Connection to the chassis, IxNetwork Tcl Server 					   #
#		2. Topology configuration											   #
#		3. Configure trafficItem 1 for Layer 4-7 AppLibrary Profile			   #	
#		4. Configure trafficItem 2 for Layer 4-7 AppLibrary Profile			   #
#		5. Start protocols													   #	
#		6. Apply and run AppLibrary traffic									   #
#		7. Drill down per IP addresses during traffic run					   #
#		8. Stop Traffic.													   #	
#																			   #	
#                                                                              #
################################################################################

################################################################################
# Utils																		   #
################################################################################

# Libraries to be included
# package require Ixia
# Other procedures used in the script, that do not use HL API configuration/control procedures

from pprint import pprint
import os
import sys
import time
import re
import argparse
import threading
from threading import Thread
from time import sleep
import multiprocessing

# Append paths to python APIs (Linux and Windows)

sys.path.append('C:/Program Files (x86)/Ixia/hltapi/4.97.0.2/TclScripts/lib/hltapi/library/common/ixiangpf/python')
sys.path.append('C:/Program Files (x86)/Ixia/IxNetwork/7.50.0.8EB/API/Python')

 
from ixia_ngfp_lib import *
from utils import *
from settings import *
from test_process import * 
#from clear_console import *
#init()
################################################################################
# Connection to the chassis, IxNetwork Tcl Server                 			   #
################################################################################
class Test_Monitor_Process(multiprocessing.Process):
	def __init__(self, q, style):
		multiprocessing.Process.__init__(self)
		self.q = q
		self.style = style

	def run(self):
		monitor_dut()


# This section should contain the connect procedure values (device ip, port list etc) and, of course, the connect procedure		
def period_login(dut_list,stop):
	tprint("Staring period_login thread")
	while True:
		if stop():
			tprint("*** Login thread: Main thread is done....Existing background DUT login activities")
			break
		sleep(300)
		tprint("*****Login thread: relogin after 300 seconds ")
		for dut in dut_list:
			relogin_if_needed(dut)


def mac_log_stress(topology_handle_dict_list, dut_list, mac_table, stop, **kwargs):
	dut1 = dut_list[0]
	dut2 = dut_list[1]
	dut3 = dut_list[2]
	dut4 = dut_list[3]

	ethernet_1_handle = topology_handle_dict_list[0]['ethernet_handle']
	ethernet_2_handle = topology_handle_dict_list[1]['ethernet_handle']
	ethernet_3_handle = topology_handle_dict_list[2]['ethernet_handle']
	ethernet_4_handle = topology_handle_dict_list[3]['ethernet_handle']

	port_1_handle = topology_handle_dict_list[0]['port_handle']
	port_2_handle = topology_handle_dict_list[1]['port_handle']
	port_3_handle = topology_handle_dict_list[2]['port_handle']
	port_4_handle = topology_handle_dict_list[3]['port_handle']

	topology_1_handle = topology_handle_dict_list[0]['topology_handle']
	topology_2_handle = topology_handle_dict_list[1]['topology_handle']
	topology_3_handle = topology_handle_dict_list[2]['topology_handle']
	topology_4_handle = topology_handle_dict_list[3]['topology_handle']

	ipv4_1_handle = topology_handle_dict_list[0]['ipv4_handle']
	ipv4_2_handle = topology_handle_dict_list[1]['ipv4_handle']
	ipv4_3_handle = topology_handle_dict_list[2]['ipv4_handle']
	ipv4_4_handle = topology_handle_dict_list[3]['ipv4_handle']


	deviceGroup_1_handle = topology_handle_dict_list[0]['deviceGroup_handle']
	deviceGroup_2_handle = topology_handle_dict_list[1]['deviceGroup_handle']
	deviceGroup_3_handle = topology_handle_dict_list[2]['deviceGroup_handle']
	deviceGroup_4_handle = topology_handle_dict_list[3]['deviceGroup_handle']
	ip3 = "100.2.0.1"
	ip4 = "100.2.10.1"
	gw3 = "100.2.10.1"
	gw4 = "100.2.0.1"

	tprint("================================ Start running  mac_log_stress thread  ====================")
	counter = 1
	 
	MAC_CLEAR_TIME = 5
	SHORT_TIMEOUT = 5
	LONG_TIMEOUT = 10

	sleep(LONG_TIMEOUT)
	if "log" in kwargs:
		log_flag = kwargs['log']
	else:
		log_flag = True
	with lock:
		for dut in dut_list:
			relogin_if_needed(dut)
		 
	if log_flag == True: 
		cmd = "set log-mac-event disable"
		port_list = ["icl","mclag-core-2","mclag-core"]
		for dut in dut_list:
			for port in port_list:
				config_switch_port_cmd(dut,port,cmd)
		# switch_configure_cmd(dut3,"config switch interface")
		# switch_configure_cmd(dut3,"edit port39")
		# switch_configure_cmd(dut3,"set log-mac-event enable")
		# switch_configure_cmd(dut3,"end")

		# switch_configure_cmd(dut4,"config switch interface")
		# switch_configure_cmd(dut4,"edit port39")
		# switch_configure_cmd(dut4,"set log-mac-event enable")
		# switch_configure_cmd(dut4,"end")

		# config_switch_port_cmd(dut1,"port39",cmd)
		# config_switch_port_cmd(dut1,"port39",cmd)
	else:
		cmd = "set log-mac-event disable"
		port_list = ["port39", "icl","mclag-core-2","mclag-core"]
		for dut in dut_list:
			for port in port_list:
				config_switch_port_cmd(dut,port,cmd)

		# switch_configure_cmd(dut3,"config switch interface")
		# switch_configure_cmd(dut3,"edit port39")
		# switch_configure_cmd(dut3,"set log-mac-event disable")
		# switch_configure_cmd(dut3,"end")

		# switch_configure_cmd(dut4,"config switch interface")
		# switch_configure_cmd(dut4,"edit port39")
		# switch_configure_cmd(dut4,"set log-mac-event disable")
		# switch_configure_cmd(dut4,"end")

		
	
	while True:
		if stop():
			tprint("Main thread is done....Existing background mac_log_stress thread")
			break
		# ip3,ip4 = ip4,ip3
		# gw3,gw4 = gw4,gw3
		#keyin = input("testing....press any key")
		 
		tprint("=========  mac_log_stress thread: manually clear MAC table entries on DUT3 and DUT4")
		 
		#tprint("===== IXIA thread: Lock Acquired")
		for i in range(10):
			tprint("::::: mac_log_stress thread: clearing mac-address on DUT1")
			switch_show_cmd(dut1,"diagnose switch mac-address delete all")
			tprint("::::: mac_log_stress thread: clearing mac-address on DUT2")
			switch_show_cmd(dut2,"diagnose switch mac-address delete all")
			tprint("::::: mac_log_stress thread: clearing mac-address on DUT3")
			switch_show_cmd(dut3,"diagnose switch mac-address delete all")
			tprint("::::: mac_log_stress thread: clearing mac-address on DUT4")
			switch_show_cmd(dut4,"diagnose switch mac-address delete all")
			tprint("::::: mac_log_stress thread: Re-learn MAC")
			ixia_stop_one_protcol(ipv4_3_handle)
			ixia_stop_one_protcol(ipv4_4_handle)
			ixia_start_one_protcol(ipv4_3_handle)
			ixia_start_one_protcol(ipv4_4_handle)
			sleep(MAC_CLEAR_TIME)
		 
		#keyin = input("testing....press any key")
		with lock:
			tprint("===== mac_log_stress thread: Lock Acquired")
			ixia_destroy_topology(topology_3_handle,deviceGroup_3_handle,mac_table)
			#ixia_destroy_topology(topology_4_handle,deviceGroup_4_handle,mac_table)
		sleep(SHORT_TIMEOUT)
		#keyin = input("testing....press any key")
		with lock:
			tprint("===== mac_log_stress thread: Lock Acquired")
			tprint("=====  mac_log_stress thread: Generating MAC move events. Now port3 is having the same MAC address as port4")
			handle_dict = ixia_static_ipv4_topo(
				port=port_3_handle,
				multiplier=mac_table,
				topology_name="Topology 3",
				device_group_name = "Device Group 3",
				intf_ip=ip3, 
				gateway = gw3,
				intf_mac="00.14.01.00.00.01",
				mask="255.255.0.0"
			)
			ethernet_3_handle = handle_dict['ethernet_handle']
			port_3_handle = handle_dict['port_handle']
			topology_3_handle = handle_dict['topology_handle']
			ipv4_3_handle = handle_dict['ipv4_handle']
			deviceGroup_3_handle = handle_dict['deviceGroup_handle']
			ixia_start_one_protcol(ipv4_3_handle)
			 
		for i in range(10):
			tprint("::::: mac_log_stress thread: Clear mac-address after having MAC move")
			tprint("::::: mac_log_stress thread: clearing mac-address on DUT3")
			switch_show_cmd(dut3,"diagnose switch mac-address delete all")
			tprint("::::: mac_log_stress thread: clearing mac-address on DUT4")
			switch_show_cmd(dut4,"diagnose switch mac-address delete all")
			tprint("::::: mac_log_stress thread: Re-learn MAC")
			ixia_stop_one_protcol(ipv4_3_handle)
			ixia_stop_one_protcol(ipv4_4_handle)
			ixia_start_one_protcol(ipv4_3_handle)
			ixia_start_one_protcol(ipv4_4_handle)
			sleep(MAC_CLEAR_TIME)

		tprint("=====  mac_log_stress thread:Restore original MAC address ")
		ixia_destroy_topology(topology_3_handle,deviceGroup_3_handle,mac_table)
		ixia_destroy_topology(topology_4_handle,deviceGroup_4_handle,mac_table)
		sleep(SHORT_TIMEOUT)
		#keyin = input("testing....press any key")
		with lock:
			tprint("===== mac_log_stress thread: Lock Acquired")
			tprint("=====  mac_log_stress thread:Restore original MAC address ")
			handle_dict = ixia_static_ipv4_topo(
				port=port_3_handle,
				multiplier=mac_table,
				topology_name="Topology 3",
				device_group_name = "Device Group 3",
				intf_ip=ip3, 
				gateway = gw3,
				intf_mac="00.13.01.00.00.01",
				mask="255.255.0.0"
			)
			ethernet_3_handle = handle_dict['ethernet_handle']
			port_3_handle = handle_dict['port_handle']
			topology_3_handle = handle_dict['topology_handle']
			ipv4_3_handle = handle_dict['ipv4_handle']
			deviceGroup_3_handle = handle_dict['deviceGroup_handle']

			handle_dict = ixia_static_ipv4_topo(
				port=port_4_handle,
				multiplier=mac_table,
				topology_name="Topology 4",
				device_group_name = "Device Group 4",
				intf_ip=ip4, 
				gateway = gw4,
				intf_mac="00.14.01.00.00.01",
				mask="255.255.0.0"
			)
			ethernet_4_handle = handle_dict['ethernet_handle']
			port_4_handle = handle_dict['port_handle']
			topology_4_handle = handle_dict['topology_handle']
			ipv4_4_handle = handle_dict['ipv4_handle']
			deviceGroup_4_handle = handle_dict['deviceGroup_handle']

			ixia_start_one_protcol(ipv4_3_handle)
			ixia_start_one_protcol(ipv4_4_handle)
		sleep(MAC_CLEAR_TIME)
		counter += 1
		if counter == 50:
			counter = 0
			with lock:
				for dut in dut_list:
					relogin_if_needed(dut)

def dut_cpu_memory(dut_dir_list,stop):
	cmd = "diagnose sys top"
	counter = 0
	dut_list = []
	dut_name_list = []
	dut_location_list = []
	for d in dut_dir_list:
		dut = d['telnet']
		dut_list.append(dut)
		dut_name = d['name']
		dut_name_list.append(dut_name)
		location = d['location']
		dut_location_list.append(location)
	while True:
		# if stop():
		# 	tprint("Main thread is done....Existing background CPU and memory monitoring activities")
		# 	break
		tprint("================== polling CPU Utils =================")
		for d in dut_dir_list:
			dut = d['telnet']
			dut_name = d['name']
			location = d['location']
			result = loop_command_output(dut,cmd)
			tprint("==============dut_cpu_memory thread: CPU utilization at {}=======".format(dut_name))
			print(result)
		sleep(20)
		# counter += 1
		# if counter == 50:
		# 	counter = 0
		# 	with lock:
		# 		for dut in dut_list:
		# 			relogin_if_needed(dut)

def dut_polling(dut_list,stop):
	tprint("================================ Start running dut_polling ====================")
	dut1 = dut_list[0]
	dut2 = dut_list[1]
	dut3 = dut_list[2]
	dut4 = dut_list[3]
	counter = 0
	while True:
		if stop():
			tprint("Main thread is done....Existing background CLI show command activities")
			break
		tprint("================== CLI show commands for DUT1 =================")
		switch_show_cmd(dut1,"diagnose switch mac-address list")
		switch_show_cmd(dut1,"execute log display")
		switch_show_cmd(dut1,"diagnose stp vlan list")
		tprint("================== CLI show commands for DUT2 =================")
		switch_show_cmd(dut2,"diagnose switch mac-address list")
		switch_show_cmd(dut2,"execute log display")
		switch_show_cmd(dut2,"diagnose stp vlan list")
		tprint("================== CLI show commands for DUT3 =================")
		switch_show_cmd(dut3,"diagnose switch mac-address list")
		switch_show_cmd(dut3,"execute log display")
		switch_show_cmd(dut3,"diagnose stp vlan list")
		tprint("================== CLI show commands for DUT4 =================")
		switch_show_cmd(dut4,"diagnose switch mac-address list")
		switch_show_cmd(dut4,"execute log display")
		switch_show_cmd(dut4,"diagnose stp vlan list")
		sleep(20)
		counter += 1
		if counter == 50:
			counter = 0
			with lock:
				for dut in dut_list:
					relogin_if_needed(dut)


def background_ixia_activity(topology_handle_dict_list,dut_list,stop):
	dut3 = dut_list[2]
	dut4 = dut_list[3]

	ethernet_1_handle = topology_handle_dict_list[0]['ethernet_handle']
	ethernet_2_handle = topology_handle_dict_list[1]['ethernet_handle']
	ethernet_3_handle = topology_handle_dict_list[2]['ethernet_handle']
	ethernet_4_handle = topology_handle_dict_list[3]['ethernet_handle']

	port_1_handle = topology_handle_dict_list[0]['port_handle']
	port_2_handle = topology_handle_dict_list[1]['port_handle']
	port_3_handle = topology_handle_dict_list[2]['port_handle']
	port_4_handle = topology_handle_dict_list[3]['port_handle']

	topology_1_handle = topology_handle_dict_list[0]['topology_handle']
	topology_2_handle = topology_handle_dict_list[1]['topology_handle']
	topology_3_handle = topology_handle_dict_list[2]['topology_handle']
	topology_4_handle = topology_handle_dict_list[3]['topology_handle']

	ipv4_1_handle = topology_handle_dict_list[0]['ipv4_handle']
	ipv4_2_handle = topology_handle_dict_list[1]['ipv4_handle']
	ipv4_3_handle = topology_handle_dict_list[2]['ipv4_handle']
	ipv4_4_handle = topology_handle_dict_list[3]['ipv4_handle']


	deviceGroup_1_handle = topology_handle_dict_list[0]['deviceGroup_handle']
	deviceGroup_2_handle = topology_handle_dict_list[1]['deviceGroup_handle']
	deviceGroup_3_handle = topology_handle_dict_list[2]['deviceGroup_handle']
	deviceGroup_4_handle = topology_handle_dict_list[3]['deviceGroup_handle']
	ip3 = "100.2.0.1"
	ip4 = "100.2.10.1"
	gw3 = "100.2.10.1"
	gw4 = "100.2.0.1"

	tprint("================================ Start running thread at background ====================")
	counter = 1
	MAC_TIMEOUT = 350
	MAC_CLEAR_TIME = 30
	SHORT_TIMEOUT = 5
	LONG_TIMEOUT = 10

	sleep(LONG_TIMEOUT)
	while True:
		if stop():
			tprint("Main thread is done....Existing background IXIA activities")
			break
		ip3,ip4 = ip4,ip3
		gw3,gw4 = gw4,gw3
		#keyin = input("testing....press any key")
		with lock:
			tprint("===== IXIA thread: Lock Acquired")
			ixia_stop_one_protcol(ipv4_3_handle)
			ixia_stop_one_protcol(ipv4_4_handle)
		if counter%2 == 0:
			tprint("========= IXIA thread: Wait for MAC table entries to time out: {} seconds".format(MAC_TIMEOUT))
			sleep(MAC_TIMEOUT)

		else:
			sleep(MAC_CLEAR_TIME)
			tprint("========= IXIA thread: manually clear MAC table entries on DUT3 and DUT4")
			with lock:
				tprint("===== IXIA thread: Lock Acquired")
				relogin_if_needed(dut3)
				relogin_if_needed(dut4)
				tprint("::::: IXIA thread: clearing mac-address on DUT3")
				switch_show_cmd(dut3,"diagnose switch mac-address delete all")
				tprint("::::: IXIA thread: clearing mac-address on DUT3")
				switch_show_cmd(dut4,"diagnose switch mac-address delete all")
				
		sleep(MAC_CLEAR_TIME)
		with lock:		
			tprint("===== IXIA thread: Lock Acquired")
			ixia_start_one_protcol(ipv4_3_handle)
			ixia_start_one_protcol(ipv4_4_handle)
		tprint("========= IXIA thread: Wait time after start IP prtocols on port3 and port4: {}".format(MAC_TIMEOUT))
		sleep(MAC_TIMEOUT)
		#keyin = input("testing....press any key")
		with lock:
			tprint("===== IXIA thread: Lock Acquired")
			ixia_destroy_topology(topology_3_handle,deviceGroup_3_handle,1000)
			ixia_destroy_topology(topology_4_handle,deviceGroup_4_handle,1000)
		sleep(SHORT_TIMEOUT)
		#keyin = input("testing....press any key")
		with lock:
			tprint("===== IXIA thread: Lock Acquired")
			tprint("===== IXIA thread: Generating MAC move events")
			handle_dict = ixia_static_ipv4_topo(
				port=port_3_handle,
				multiplier=1000,
				topology_name="Topology 3",
				device_group_name = "Device Group 3",
				intf_ip=ip3, 
				gateway = gw3,
				intf_mac="00.13.01.00.00.01",
				mask="255.255.0.0"
			)
			ethernet_3_handle = handle_dict['ethernet_handle']
			port_3_handle = handle_dict['port_handle']
			topology_3_handle = handle_dict['topology_handle']
			ipv4_3_handle = handle_dict['ipv4_handle']
			deviceGroup_3_handle = handle_dict['deviceGroup_handle']

			handle_dict = ixia_static_ipv4_topo(
				port=port_4_handle,
				multiplier=1000,
				topology_name="Topology 4",
				device_group_name = "Device Group 4",
				intf_ip=ip4, 
				gateway = gw4,
				intf_mac="00.14.01.00.00.01",
				mask="255.255.0.0"
			)
			ethernet_4_handle = handle_dict['ethernet_handle']
			port_4_handle = handle_dict['port_handle']
			topology_4_handle = handle_dict['topology_handle']
			ipv4_4_handle = handle_dict['ipv4_handle']
			deviceGroup_4_handle = handle_dict['deviceGroup_handle']

			# keyin = input("testing....press any key")
			ixia_start_one_protcol(ipv4_3_handle)
			ixia_start_one_protcol(ipv4_4_handle)
		sleep(MAC_CLEAR_TIME)
		counter += 1
		if counter == 50:
			counter = 0
			with lock:
				for dut in dut_list:
					relogin_if_needed(dut)


def pre_test_verification(dut_list):
	for dut in dut_list:
		print("########################################################################################")
		switch_show_cmd(dut,"get system status")
		switch_show_cmd(dut,"show switch trunk")
		switch_show_cmd(dut,"diagnose switch mclag peer-consistency-check")
		switch_show_cmd(dut,"get switch lldp neighbors-summary")
		switch_show_cmd(dut,"show switch interface port39")

def topology_mclag_8(dut_list):
	print("--------------------------------------------------------------------------")
	print(" 		Configure a MCALG-8 Topology")
	print("--------------------------------------------------------------------------")
	for dut in dut_list:
		switch_unshut_port(dut,"port1")
		switch_unshut_port(dut,"port2")
		switch_unshut_port(dut,"port3")
		switch_unshut_port(dut,"port4")
		switch_configure_cmd(dut,"config switch trunk")
		switch_configure_cmd(dut,"edit mclag-core")
		switch_configure_cmd(dut,"set members port1 port2 port3 port4")
		switch_configure_cmd(dut,"end")

def topology_mclag_4(dut_list):
	print("--------------------------------------------------------------------------")
	print(" 		Configure a MCALG-4 Topology")
	print("--------------------------------------------------------------------------")
	for dut in dut_list:
		switch_unshut_port(dut,"port1")
		switch_unshut_port(dut,"port2")
		switch_unshut_port(dut,"port3")
		switch_unshut_port(dut,"port4")

		switch_shut_port(dut,"port1")
		switch_shut_port(dut,"port3")
		switch_configure_cmd(dut,"config switch trunk")
		switch_configure_cmd(dut,"edit mclag-core")
		switch_configure_cmd(dut,"set members port2 port4")
		switch_configure_cmd(dut,"end")
		time.sleep(2)

def dut_shut_test_mclag_4(dut2,dut4):
	wait_time = 10
	for i in range(2):
		tprint("========= Run Time #{}".format(i+1))
		tprint("Shut 1st active port on dut4 -- Rack20-22: port4")
		switch_shut_port(dut4,"port4")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to unplugging first active link on DUT4----------")
		with lock:
			tprint("==== Main thread: Acquired lock")
			traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
 
		tprint("Shut 2nd active port on dut4 -- Rack20-22: port2")
		switch_shut_port(dut4,"port2")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to unplugging 2nd active link on DUT4----------")
		with lock:
			tprint("==== Main thread: Acquired lock")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
 
		print("##### Test Case: Unshut 2nd active port on dut4 -- Rack20-22: port2")
		switch_unshut_port(dut4,"port2")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to reconnect 2nd active link on DUT4----------")
		with lock:
			tprint("==== Main thread: Acquired lock")
			traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
 		
		print("##### Test Case: Unshut first active port on dut4 -- Rack20-22: port4")
		switch_unshut_port(dut4,"port4")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to reconnect first active link on DUT4----------")
		with lock:
			tprint("==== Main thread: Acquired lock")
			traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
 
	for i in range(2):
		tprint("========= Run Time #{}".format(i))
		tprint("Shut 1st active port on dut2 -- Rack23-28: port4")
		switch_shut_port(dut2,"port4")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to unplugging first active link on DUT4----------")
		with lock:
			tprint("==== Main thread: Acquired lock")
			traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
 
		tprint("Shut 2nd active port on dut2 -- Rack23-28: port2")
		switch_shut_port(dut2,"port2")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to unplugging 2nd active link on DUT4----------")
		with lock:
			tprint("==== Main thread: Acquired lock")
			traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
 
		tprint("Unshut 2nd active port on dut2 -- Rack23-28: port2")
		switch_unshut_port(dut2,"port2")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to reconnect 2nd active link on DUT4----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
 		
		tprint("Unshut first active port on dut2 -- Rack23-28: port4")
		switch_unshut_port(dut2,"port4")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to reconnect first active link on DUT4----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
 
def dut_fibercut_test(dut_dir,mode,**kwargs):
	dut=dut_dir['telnet']
	location = dut_dir['location']
	dut_name = dut_dir['name']

	twargs = {}
	for k, v in kwargs.items():
		twargs[k] = v

	lag_mem = twargs["mem"]
	tier = twargs["tier"]
	runtime = twargs["runtime"]
	#mode = twargs["mode"]
	#location = "XXXXX" # future: location = dut["location"] or something like that
	test_list = []
	if mode == "auto":
		wait_time = 30
	else:
		wait_time = 15
	wait_time_long = 120
	wait_loss_time = 10

	tprint("Clearing traffic statistics before fiber-cut testing starts ....")
	ixia_clear_traffic_stats()
	for i in range(runtime):
		iterate_list = []
		#relogin_if_needed(dut)
		tprint("========= Run Time #{}: MCLAG-{}".format(i+1,lag_mem))
		first_active_port = "port4" # future: port=find_active_trunk_port(dut)
		first_active_port = find_active_trunk_port(dut)
		tprint("MCLAG-{}, Shut/unplug dut:{} 1st active port:{} on located at:{}".format(lag_mem,dut_name,first_active_port,location))  # this has to change to have location and port# dynamic
		if mode == 'auto':
			switch_shut_port(dut,first_active_port)
		else:
			print_interactive_line()
			tprint("Unplug 1st active port fiber on DUT: {} located at: {} port:{}".format(dut_name,location,first_active_port))
			keyin = input("Are you done with unplugging cable? if so press any key...")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		with lock:
			traffic_stats = collect_ixia_traffic_stats()
		 
		flow_stat_list_down_1 = parse_traffic_stats_new(traffic_stats,reason="1st-down")
		for f in flow_stat_list_down_1:
			f['dut'] = dut_name
			f['lag_mem'] = lag_mem
			f['test_num'] = i+1
			f['tier'] = tier
		print_flow_stats_new(flow_stat_list_down_1)

		tprint("Clearing IXIA traffic statistics ....")
		ixia_clear_traffic_stats()
		if lag_mem == 8:
			lag8_inactive_port1 = "port1" # future: lag4_inactive_port1,lag4_inactive_port2 = find_inactive_trunk_port()
			lag8_inactive_port2 = "port3"
			try:
				lag8_inactive_port1,lag8_inactive_port2 = find_inactive_trunk_port(dut)
			except  Exception as e:
				tprint("something is wrong with getting inactive port on switch:{}".format(dut_name))
			tprint("MCLAG-8: Shut 2nd and 3rd inactive ports: {},{} on dut:{} located at {} ". \
				format(lag8_inactive_port1,lag8_inactive_port2,dut_name,location))
			if mode == "auto":
				switch_shut_port(dut,lag8_inactive_port1)
				switch_shut_port(dut,lag8_inactive_port2)
			elif mode == "manual":
				print_interactive_line()
				tprint("Unplug MCLAG-8 inactive port fibers on DUT: {} located at: {} ports:{} {}".\
					format(dut_name,location,lag8_inactive_port1,lag8_inactive_port2))
				keyin = input("Are you done with changing cable? if so press any key...")
		else:
			lag2_2nd_port = "port2" # future: port1  = find_active_trunk_port()
			lag2_2nd_port = find_active_trunk_port(dut)
			tprint("MCLAG-2: Shut 2nd active port: {} on dut:{} located at {} ".format(lag2_2nd_port,dut_name,location))
			if mode == "auto":
				switch_shut_port(dut,lag2_2nd_port)
			elif mode == "manual":
				print_interactive_line()
				tprint("Unplug MCLAG-2 2nd port fiber on DUT: {} located at: {} port:{}".format(dut_name,location,lag2_2nd_port))
				keyin = input("Are you done with changing cable? if so press any key...")
		tprint("Wait for {} seconds before measuring traffic loss".format(wait_time))
		time.sleep(wait_time)
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list_down_2 = parse_traffic_stats_new(traffic_stats,reason="2nd-down")
		for f in flow_stat_list_down_2:
			f['dut'] = dut_name
			f['lag_mem'] = lag_mem
			f['test_num'] = i+1
			f['tier'] = tier
		print_flow_stats_new(flow_stat_list_down_2)

		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
		if lag_mem == 8:
			tprint("MCLAG-8: UnSnshut 2nd and 3rd inactive ports:{},{} on dut:{} located at: {} ". \
				format(lag8_inactive_port1,lag8_inactive_port2,dut_name,location))	
			if mode == "auto":		 
				switch_unshut_port(dut,lag8_inactive_port1)
				switch_unshut_port(dut,lag8_inactive_port2)
			elif mode == "manual":
				print_interactive_line()
				tprint(" MCLAG-8: Reconnect inactive fibers on DUT:{} located at:{} ports:{} {}".\
					format(dut_name,location,lag8_inactive_port1,lag8_inactive_port2))
				keyin = input("Are you done with changing cable? if so press any key...")
		else:
			tprint("MCLAG-2: UnShut 2nd active port: {} on dut:{} located at {} ".format(lag2_2nd_port,dut_name,location))
			if mode == "auto":
				switch_unshut_port(dut,lag2_2nd_port)
			else:
				print_interactive_line()
				tprint(" MCLAG-2: Reconnect 2nd fiber on DUT: {} located at: {} port:{}".format(dut_name,location,lag2_2nd_port))
				keyin = input("Are you done with changing cable? if so press any key...")
	
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		traffic_stats = collect_ixia_traffic_stats()
		 
		flow_stat_list_up_1 = parse_traffic_stats_new(traffic_stats,reason="2nd-up")
		for f in flow_stat_list_up_1:
			f['dut'] = dut_name
			f['lag_mem'] = lag_mem
			f['test_num'] = i+1
			f['tier'] = tier
		print_flow_stats_new(flow_stat_list_up_1)

		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
		if lag_mem == 8:
			tprint("MCLAG8: Unshut first active port:{} on dut: located at: {}".format(first_active_port,dut_name,location))
			if mode == "auto":
				switch_unshut_port(dut,first_active_port)
			else:
				print_interactive_line()
				tprint(" MCLAG-8: Reconnect 1st active fiber on DUT:{} located at:{} port:{}".\
					format(dut_name,location,first_active_port))
				keyin = input("Are you done with changing cable? if so press any key...")
		else:
			tprint("MCLAG2: Unshut first active port:{} on dut: {} located at: {}".format(first_active_port,dut_name,location))
			if mode == "auto":
				switch_unshut_port(dut,first_active_port)
			else:
				print_interactive_line()
				tprint("MCLAG-2: Reconnect 1st active fiber on DUT:{} located at:{} port:{}".format(dut_name,location,first_active_port))
				keyin = input("Are you done with changing cable? if so press any key...")
		
		tprint("Wait for {} seconds and measure packet loss".format(wait_time_long))
		time.sleep(wait_time)
		traffic_stats = collect_ixia_traffic_stats()

		
		count = 0
		while traffic_loss_2_flows(traffic_stats,20) == False:
			count += 1
			if count > 10:
				tprint("There is no traffic loss after {} tries, give up!".format(count))
				break
			debug("There is no traffic loss yet, wait for {} seconds and try again ".format(wait_loss_time))
			time.sleep(wait_loss_time)
			traffic_stats = collect_ixia_traffic_stats()
		end_test_active_port = find_active_trunk_port(dut)
		tprint("Before test starts, active port = {}".format(first_active_port))
		tprint("After test finishes, active port = {}".format(end_test_active_port))
		if end_test_active_port != first_active_port:
			tprint("!!!!!! After fiber_cut test, active port has been changed from: {} to: {}".format(first_active_port,end_test_active_port))
		flow_stat_list_up_2 = parse_traffic_stats_new(traffic_stats,reason="1st-up")
		for f in flow_stat_list_up_2:
			f['dut'] = dut_name
			f['lag_mem'] = lag_mem
			f['test_num'] = i+1
			f['tier'] = tier
		print_flow_stats_new(flow_stat_list_up_2)


		iterate_list = flow_stat_list_down_1 + flow_stat_list_down_2 + flow_stat_list_up_1 + flow_stat_list_up_2
		test_list.append(iterate_list)

		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
 
	return test_list

def dut_shut_test_mclag_8(dut2,dut4):
	wait_time = 10
	for i in range(2):
		tprint("========= Run Time #{}".format(i))
		tprint("Shut 1st active port on dut4 -- Rack20-22: port4")
		switch_shut_port(dut4,"port4")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to shutting first active port on DUT4----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
 
		tprint("Shut 2nd and 3rd inactive port on dut4 -- Rack20-22: port1, port3")
		switch_shut_port(dut4,"port1")
		switch_shut_port(dut4,"port3")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to shutting 2nd and 3rd inactive port on DUT4----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
 
		tprint("Unshut 2nd and 3rd inactive port on dut4 -- Rack20-22: port1 and port3")
		switch_unshut_port(dut4,"port1")
		switch_unshut_port(dut4,"port3")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to reconnect 2nd active link on DUT4----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
 		
		tprint("Unshut first active port on dut4 -- Rack20-22: port4")
		switch_unshut_port(dut4,"port4")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to reconnect first active link on DUT4----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
 
	for i in range(2):
		tprint("========= Run Time #{}".format(i))
		tprint("Shut 1st active port on dut2 -- Rack23-28: port4")
		switch_shut_port(dut2,"port4")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to shutting first active port on DUT4----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
 

		tprint("Shut 2nd and third inactive port on dut2 -- Rack23-28: port2")
		switch_shut_port(dut2,"port2")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to unplugging 2nd active link on DUT4----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()

		tprint("Unshut 2nd active port on dut2 -- Rack23-28: port2")
		switch_unshut_port(dut2,"port2")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to reconnect 2nd active link on DUT4----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
		
		tprint("Unshut first active port on dut2 -- Rack23-28: port4")
		switch_unshut_port(dut2,"port4")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to reconnect first active link on DUT4----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()

def dut_unplug_test_mclag_4(dut2,dut4):
	wait_time = 10
	for i in range(2):
		tprint("========= Run Time #{}".format(i))
		tprint("Unplug 1st active link on dut4 -- Rack20-22: port4")
		keyin = input("Are you done with unplugging cable? if so press any key...")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to unplugging first active link on DUT4----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()

		tprint("Unplug 2nd active link on dut4 -- Rack20-22: port2")
		keyin = input("Are you done with unplugging cable? if so press any key...")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to unplugging 2nd active link on DUT4----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()

		tprint("Reconnect 2nd active link on dut4 -- Rack20-22: port2")
		keyin = input("Are you done with changing cable? if so press any key...")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to reconnect 2nd active link on DUT4----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
		
		tprint("Reconnect first active link on dut4 -- Rack20-22: port4")
		keyin = input("Are you done with changing cable? if so press any key...")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to reconnect first active link on DUT4----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()

	for i in range(2):
		tprint("========= Run Time #{}".format(i))
		tprint("Unplug 1st active link on dut2 -- Rack23-28: port4")
		keyin = input("Are you done with changing cable? if so press any key...")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to unplugging first active link on DUT2----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()

		tprint("Unplug 2nd active link on dut4 -- Rack23-28: port2")
		keyin = input("Are you done with changing cable? if so press any key...")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to unplugging 2nd active link on DUT2----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()

		tprint("Reconnect 2nd active link on dut4 -- Rack23-28: port2")
		keyin = input("Are you done with changing cable? if so press any key...")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to reconnect 2nd active link on DUT2----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
		
		tprint("Reconnect first active link on dut4 -- Rack23-28: port4")
		keyin = input("Are you done with changing cable? if so press any key...")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to reconnect first active link on DUT2----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()

def dut_reboot_test_new(dut1,**kwargs):
	twargs = {}
	for k, v in kwargs.items():
		twargs[k] = v

	dut_name = twargs["dut"]
	lag_mem = twargs["mem"]
	runtime = twargs['runtime']
	test_list = []
	tprint("Clearing traffic statistics before reboot-testing starts ....")
	ixia_clear_traffic_stats()
	for i in range(runtime):
		iterate_list = []
		relogin_if_needed(dut1)
		tprint("========= Run Time #{}".format(i+1))
		tprint("Rebooting DUT :....".format(dut_name))
		switch_exec_reboot(dut1,device=dut_name)
		tprint("DUT is being rebooted, wait for 2 seconds before measuring traffic loss")
		time.sleep(2)
		tprint("After waiting for 2 seconds,collect ixia traffic stats")
		print("********* Measure packet loss right after DUT went down ----------")
		traffic_stats = collect_ixia_traffic_stats_stable()
		tprint("Clearing traffic statistics after collecting the down_stats....")
		ixia_clear_traffic_stats()
		flow_stat_list_down = parse_traffic_stats_new(traffic_stats,reason="down")
		for f in flow_stat_list_down:
			f['dut'] = dut_name
			f['lag_mem'] = lag_mem
			f['test_num'] = i+1
		print_flow_stats_new(flow_stat_list_down)

		tprint("Allow traffic to run for another 200 seconds after rebooting ....")
		time.sleep(200)
		tprint("Collect traffic stats 20 seconds after DUT1 rebooted")
		print("*********** Measure packet loss due to STP converage after DUT finished rebooting-------")
		traffic_stats = collect_ixia_traffic_stats_stable()
		flow_stat_list_up = parse_traffic_stats_new(traffic_stats,reason="up")
		for f in flow_stat_list_up:
			f['dut'] = dut_name
			f['lag_mem'] = lag_mem
			f['test_num'] = i+1
		print_flow_stats_new(flow_stat_list_up)
		iterate_list = flow_stat_list_up + flow_stat_list_down
		test_list.append(iterate_list)
		

		tprint("Clearing traffic statistics after collecting the up_stats....")
		ixia_clear_traffic_stats()
 
	return test_list
# def print_flow_stats(flow_stats_list):
# 	for flow in flow_stats_list:
# 		tprint("Flow ID:{}, RX_Port:{}, TX_Port:{}, TX packet rate:{}, TX packets:{}, RX packets:{},Pkt Loss:{}, Pkt Loss time:{}". \
# 			format(flow['id'],flow['rx_port'],flow['tx_port'],flow['total_pkt_rate'], \
# 				flow['total_tx_pkts'],flow['total_rx_pkts'],flow['loss_pkts'],flow["loss_time"]))
# 		tprint("")

# 		print("--------------------------------")

def collect_ixia_traffic_stats_stable():
	threshold = 30
	stats = collect_ixia_traffic_stats()
	parsed_stats = parse_traffic_stats(stats)
	#there is no packet loss, continue collecting stats
	count = 0
	while traffic_loss_2_flows(stats,threshold) == False and count < 20:
		count += 1
		flow_stat_list_down = parse_traffic_stats_new(stats,reason="down")
		debug("^^^^^^^^^^^^^^^^^^^^^^^^^ Waiting packet loss to show up ^^^^^^^^^^^^^^")
		print_flow_stats_new(flow_stat_list_down)
		time.sleep(3)
		stats = collect_ixia_traffic_stats()

		#parsed_stats = parse_traffic_stats(stats)
	#After packet loss begins to show up, wait for a few seconds to measure again
	time.sleep(3)
	while True:
		stats = collect_ixia_traffic_stats()
		parsed_stats_2 = parse_traffic_stats(stats)
		if abs(parsed_stats_2[0]["loss_pkts"] - parsed_stats[0]["loss_pkts"]) < 10 :
			return stats
		else:
			debug("1st check-point pkt loss= {}, 2nd check-point pkt loss = {}".format(parsed_stats[0]["loss_pkts"],parsed_stats_2[0]["loss_pkts"]))
			parsed_stats = parsed_stats_2
			time.sleep(3)

def traffic_loss_2_flows(traffic_stats,threshold):
	flow_list = parse_traffic_stats(traffic_stats)

	for flow_info in flow_list:
		if flow_info['loss_pkts'] > threshold:
			return True
	return False

def parse_traffic_stats_new(traffic_stats,**kwargs):
	tkwargs = {}
	for key, value in kwargs.items():
		tkwargs[key]=value

	for k, v in traffic_stats.items():
		if k == "flow":
			flow_stats = v
			break
	flow_num = list(flow_stats.keys())[0]

	 
	flow_stats_items = flow_stats[flow_num]
	#tprint(flow_stats_items)
	flow_list = []
	for k, v in flow_stats.items():
		flow_info = {}
		flow_info['reason'] = tkwargs["reason"]
		flow_info['id'] = k
		# flow_info['rx'] = rx_stats = v['rx']
		# flow_info['tx'] = tx_stats = v['tx']
		rx_stats = v['rx']
		tx_stats = v['tx']
		flow_info['rx_port'] = rx_stats['port']
		flow_info['total_pkts'] = int(rx_stats['total_pkts'])
		flow_info['total_pkts_bytes'] = int(rx_stats['total_pkts_bytes'])

		flow_info['loss_pkts'] = int(rx_stats['loss_pkts'])
		flow_info['max_delay'] = int(rx_stats['max_delay'])
		flow_info['total_pkt_rate'] =float(tx_stats['total_pkt_rate'])
		flow_info['total_tx_pkts'] = tx_stats['total_pkts']
		flow_info['total_rx_pkts'] = rx_stats['total_pkts']
		if flow_info['total_pkt_rate'] != 0:
			flow_info["loss_time"] = str(flow_info['loss_pkts']/flow_info['total_pkt_rate'])
		else:
			flow_info["loss_time"] = "0 seconds"
		flow_info['tx_port'] = tx_stats['port']
		flow_list.append(flow_info)

	return (flow_list)

def parse_traffic_stats(traffic_stats):
	for k, v in traffic_stats.items():
		if k == "flow":
			flow_stats = v
			break
	flow_num = list(flow_stats.keys())[0]

	 
	flow_stats_items = flow_stats[flow_num]
	#tprint(flow_stats_items)
	flow_list = []
	for k, v in flow_stats.items():
		flow_info = {}
		flow_info['id'] = k
		flow_info['rx'] = rx_stats = v['rx']
		flow_info['tx'] = tx_stats = v['tx']
		flow_info['rx_port'] = rx_stats['port']
		flow_info['total_pkts'] = int(rx_stats['total_pkts'])
		flow_info['total_pkts_bytes'] = int(rx_stats['total_pkts_bytes'])

		flow_info['loss_pkts'] = int(rx_stats['loss_pkts'])
		flow_info['max_delay'] = int(rx_stats['max_delay'])
		flow_info['total_pkt_rate'] =float(tx_stats['total_pkt_rate'])
		flow_info['total_tx_pkts'] = tx_stats['total_pkts']
		flow_info['total_rx_pkts'] = rx_stats['total_pkts']
		if flow_info['total_pkt_rate'] != 0:
			flow_info["loss_time"] = str(flow_info['loss_pkts']/flow_info['total_pkt_rate'])
		else:
			flow_info["loss_time"] = "0 seconds"
		flow_info['tx_port'] = tx_stats['port']
		flow_list.append(flow_info)

	return (flow_list)


def print_dict(obj, nested_level=0, output=sys.stdout):
    """
    Print each dict key with indentions for readability.
    """
    spacing = '   '
    if type(obj) == dict:
        #print >> output, '%s' % ((nested_level) * spacing)
        tprint('%s' % ((nested_level) * spacing),file=output)
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                #print >> output, '%s%s:' % ((nested_level + 1) * spacing, k)
                tprint('%s%s:' % ((nested_level + 1) * spacing, k),file=output)
                print_dict(v, nested_level + 1, output)
            else:
                #print >> output, '%s%s: %s' % ((nested_level + 1) * spacing, k, v)
                tprint('%s%s: %s' % ((nested_level + 1) * spacing, k, v),file = output)

        #print >> output, '%s' % (nested_level * spacing)
        tprint('%s' % (nested_level * spacing),file=output)
    elif type(obj) == list:
        #print >> output, '%s[' % ((nested_level) * spacing)
        tprint('%s[' % ((nested_level) * spacing),file=output)
        for v in obj:
            if hasattr(v, '__iter__'):
                print_dict(v, nested_level + 1, output)
            else:
                #print >> output, '%s%s' % ((nested_level + 1) * spacing, v)
                tprint('%s%s' % ((nested_level + 1) * spacing, v),file=output)
        #print >> output, '%s]' % ((nested_level) * spacing)
        tprint('%s]' % ((nested_level) * spacing),file=output)
    else:
        tprint('%s%s' % (nested_level * spacing, obj),file=output)

sys.stdout = Logger("Log/mclag_perf.log")

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", help="Configure switches before starting testing", action="store_true")
#parser.add_argument("-a", "--auto", help="Run in fully automated mode without manually unplugging cables", action="store_true")
parser.add_argument("-m", "--manual", help="Run in manual mode when unplugging cables", action="store_true")
parser.add_argument("-t", "--testbed", type=str, help="Specific which testbed to run this test. Valid options:1)548D 2)448D 3)fgt")
parser.add_argument("-file", "--file", type=str, help="Specific file name appendix when exporting to excel. Example:mac-1k. Default=none")
parser.add_argument("-x", "--ixia", type=str, help="ixia port setup: default=static,option1 = dhcp")
parser.add_argument("-n", "--run_time", type=int, help="Specific how many times you want to run the test, default=2")
parser.add_argument("-test", "--testcase", type=int, help="Specific which test case you want to run. Example: 1/1-3/1,3,4,7 etc")
parser.add_argument("-mac", "--mac", type=int, help="Background MAC entries learning,defaul size=1000")
parser.add_argument("-d", "--dev", help="IXIA Development mode,do not verify any network status", action="store_true")
parser.add_argument("-b", "--boot", help="Perform reboot test", action="store_true")
parser.add_argument("-f", "--factory", help="Run the test after factory resetting all devices", action="store_true")
parser.add_argument("-v", "--verbose", help="Run the test in verbose mode with amble debugs info", action="store_true")
parser.add_argument("-s", "--setup_only", help="Setup testbed and IXIA only for manual testing", action="store_true")
parser.add_argument("-nf", "--no_fortigate", help="No Fortigate: convert FSW from managed mode to standalone mode ", action="store_true")
parser.add_argument("-lm", "--log_mac", help="enable port mac log event", action="store_true")
parser.add_argument("-i", "--interactive", help="Enter interactive mode for test parameters", action="store_true")
parser.add_argument("-e", "--config_host_sw", help="Configure host switches when changing testbed", action="store_true")

global DEBUG
if len(sys.argv) > 1:
    #parser.print_help()
	args = parser.parse_args()

	if args.verbose:
		settings.DEBUG = True
		tprint("** Running the test in verbose mode")
	else:
		settings.DEBUG = False
		tprint("** Running the test in silent mode") 
	if args.config:
		setup = True
		tprint("** Before starting testing, configure devices")
	else:
		setup = False   
		tprint("** Skip setting up testbed and configuring devices")  
	# if args.auto:
	# 	mode='auto'
	if args.log_mac:
		log_mac_event = True
		tprint("** Running test with port log-mac-event enabled")
	else:
		log_mac_event = False
	if args.factory:
		factory = True
		tprint("** Will factory reset each FSW ")
	else:
		factory = False
	if args.manual:
		mode='manual'
		tprint("** Fiber cut test will be in manual mode")
	else:
		mode = 'auto'
		tprint("** Fiber cut test will be in automated mode")
	if args.testbed:
		test_setup = args.testbed
		tprint("** Test Bed = {}".format(test_setup))
	else:
		tprint("** Not test bed is needed for this run" )
		test_setup = None
	if args.ixia:
		ixia_topo = args.ixia
		tprint("** IXIA ports will be allocated IP address via DHCP server ")
	else:
		ixia_topo = "static"
		tprint("** IXIA ports will be allocated IP address statically ")
	if args.file:
		file_appendix = args.file
		tprint("** Export test ressult to file with appendix: {}".format(file_appendix))
	if args.run_time:
		Run_time = args.run_time
		tprint("** Test iterate numbers = {}".format(Run_time))
	else:
		Run_time = 2
		tprint("** Test iterate numbers = {}".format(Run_time))
	if args.testcase:
		testcase = args.testcase
		tprint("** Test Case To Run:{}".format(testcase))
	else:
		testcase = "all"
		tprint("** Test Case To Run:{}".format(testcase))
	if args.mac:
		mac_table = args.mac
		tprint("** Test under background MAC address learning,size = {}".format(mac_table))
	else:
		mac_table = 1000
		tprint("** Test under background MAC address learning,size = {}".format(mac_table))
	if args.dev:
		dev_mode = True
		tprint("** Only for developing IXIA codes, not test will be done")
	else:
		dev_mode = False
	if args.boot:
		Reboot = True
		tprint("** Measure performance with rebooting DUTs")
	else:
		Reboot = False
		tprint("** Measure performance WITHOUT rebooting DUTs")
	if args.setup_only:
		Setup_only = True
		tprint("** Set up IXIA only for manual testing")
	else:
		Setup_only = False
	if args.no_fortigate:
		no_fortigate = True
		tprint("** Will remove fortigate from the setup, need to convert for managed mode to standalone")
	else:
		no_fortigate = False
	if args.config_host_sw:
		config_host_sw = True
	else:
		config_host_sw = False
# print("Testing running in batch mode. comment out later")
# filename = "MCLAG_Perf_"+test_setup+file_appendix+".xlsx"
# touch(filename)
# sleep(5)
# scp_file(file=filename)
# exit()
tprint("====== Main thread: Creating multithread lock...")

#If in code development mode, skipping loging into switches 
if dev_mode == False:

	# filename = "LACP_Perf.xlsx"
	# dict_2_excel(stat_dir_list,filename)
	# exit()
	# tprint("Creating blank spread sheet to record test result")
	# exel_8_member_lacp_blank("LACP_Perf.xlsx","8-lacp-test1","8-member LACP trunk","6.2.0 Interim Build 168","Test1")
	# exel_8_member_lacp_blank("LACP_Perf.xlsx","8-lacp-test2","8-member LACP trunk","6.2.0 Interim Build 168","Test2")
	# exel_2_member_lacp_blank("LACP_Perf.xlsx","2-lacp-test1","2-member LACP trunk","6.2.0 Interim Build 168","Test1")
	# exel_2_member_lacp_blank("LACP_Perf.xlsx","2-lacp-test2","2-member LACP trunk","6.2.0 Interim Build 168","Test2")
	# tprint("Finish creating blank spread sheet to record test result")
	# exit()
	sw1=get_switch_telnet_connection("10.105.50.3",2097)
	sw2=get_switch_telnet_connection("10.105.50.2",2092)
	if test_setup.lower() == "fgt":
		################################
		#548D Test setup
		################################
		dut1_com = "10.105.50.3"
		dut1_location = "Rack23-29"
		dut1_port = 2057
		dut1_name = "dut1-548d"
		dut1_cfg = "dut1_548d.cfg"

		dut2_com = "10.105.50.3"
		dut2_port = 2056
		dut2_location = "Rack23-28"
		dut2_name = "dut2-548d"
		dut2_cfg = "dut2_548d.cfg"

		dut3_com = "10.105.50.1"
		dut3_port = 2075
		dut3_name = "dut3-548d"
		dut3_location = "Rack20-23"
		dut3_cfg = "dut3_548d.cfg"

		dut4_com = "10.105.50.1"
		dut4_port = 2078
		dut4_location = "Rack20-22"
		dut4_name = "dut4-548d"
		dut4_cfg = "dut4_548d.cfg"
		# tprint("======================== Configure SW1 and SW2 for this setup ===============")
		# switch_shut_port(sw1,"port25")
		# switch_shut_port(sw1,"port26")
		# switch_unshut_port(sw1,"port13")
		# switch_unshut_port(sw1,"port14")

		# switch_shut_port(sw2,"port23")
		# switch_shut_port(sw2,"port24")
		# switch_unshut_port(sw2,"port13")
		# switch_unshut_port(sw2,"port14")
	fgt1_com = "10.105.50.1"
	fgt1_port = 2066
	fgt1_location = "Rack20"
	fgt1_name = "3960E"
	fgt1_cfg = "fgt1.cfg"

	fgt2_com = "10.105.50.2"
	fgt2_port = 2074
	fgt2_location = "Rack21"
	fgt2_name = "3960E"
	fgt2_cfg = "fgt2.cfg"

	if test_setup == "548D":
		################################
		#548D Test setup
		################################
		dut1_com = "10.105.50.3"
		dut1_location = "Rack23-29"
		dut1_port = 2057
		dut1_name = "dut1-548d"
		dut1_cfg = "dut1_548d.cfg"

		dut2_com = "10.105.50.3"
		dut2_port = 2056
		dut2_location = "Rack23-28"
		dut2_name = "dut2-548d"
		dut2_cfg = "dut2_548d.cfg"

		dut3_com = "10.105.50.1"
		dut3_port = 2075
		dut3_name = "dut3-548d"
		dut3_location = "Rack20-23"
		dut3_cfg = "dut3_548d.cfg"

		dut4_com = "10.105.50.1"
		dut4_port = 2078
		dut4_location = "Rack20-22"
		dut4_name = "dut4-548d"
		dut4_cfg = "dut4_548d.cfg"

		if config_host_sw == True:
			tprint("======================== Configure SW1 and SW2 for 548D setup ===============")
			switch_shut_port(sw1,"port25")
			switch_shut_port(sw1,"port26")
			switch_unshut_port(sw1,"port13")
			switch_unshut_port(sw1,"port14")

			switch_shut_port(sw2,"port23")
			switch_shut_port(sw2,"port24")
			switch_unshut_port(sw2,"port13")
			switch_unshut_port(sw2,"port14")
			switch_unshut_port(sw2,"port7")
		

	if test_setup == "448D":
		##############################
		#448D Test stup
		##############################
		dut1_com = "10.105.50.1"
		dut1_port = 2074
		dut1_location = "Rack20-18"
		dut1_name = "dut1-448d"
		dut1_cfg = "dut1_448d.cfg"

		dut2_com = "10.105.50.1"
		dut2_port = 2081
		dut2_location = "Rack20-25"
		dut2_name = "dut2-448d"
		dut2_cfg = "dut2_448d.cfg"

		dut3_com = "10.105.50.2"
		dut3_port = 2077
		dut3_location = "Rack21-18"
		dut3_name = "dut3-448d"
		dut3_cfg = "dut3_448d.cfg"

		dut4_com = "10.105.50.2"
		dut4_port = 2078
		dut4_location = "Rack21-19"
		dut4_name = "dut4-448d"
		dut4_cfg = "dut4_448d.cfg"
		if config_host_sw == True:
			tprint("======================== Configure SW1 and SW2 for 448D setup ===============")

			switch_unshut_port(sw1,"port25")
			switch_unshut_port(sw1,"port26")
			switch_shut_port(sw1,"port13")
			switch_shut_port(sw1,"port14")

			switch_unshut_port(sw2,"port23")
			switch_unshut_port(sw2,"port24")
			switch_shut_port(sw2,"port13")
			switch_shut_port(sw2,"port14")
			switch_shut_port(sw2,"port7")

	dut1_dir = {}
	dut2_dir = {}
	dut3_dir = {} 
	dut4_dir = {}
	dut1 = get_switch_telnet_connection(dut1_com,dut1_port)
	dut1_dir['name'] = dut1_name
	dut1_dir['location'] = dut1_location
	dut1_dir['telnet'] = dut1
	dut1_dir['cfg'] = dut1_cfg

	dut2 = get_switch_telnet_connection(dut2_com,dut2_port)
	dut2_dir['name'] = dut2_name
	dut2_dir['location'] = dut2_location
	dut2_dir['telnet'] = dut2
	dut2_dir['cfg'] = dut2_cfg

	dut3 = get_switch_telnet_connection(dut3_com,dut3_port)
	dut3_dir['name'] = dut3_name
	dut3_dir['location'] = dut3_location
	dut3_dir['telnet'] = dut3
	dut3_dir['cfg'] = dut3_cfg

	dut4 = get_switch_telnet_connection(dut4_com,dut4_port)
	dut4_dir['name'] = dut4_name
	dut4_dir['location'] = dut4_location
	dut4_dir['telnet'] = dut4
	dut4_dir['cfg'] = dut4_cfg

	dut_list = [dut1,dut2,dut3,dut4]
	dut_dir_list = [dut1_dir,dut2_dir,dut3_dir,dut4_dir]

	stop_threads = False
	dut_cpu_memory(dut_dir_list,stop_threads)

	##################################################
	#   Filling in blank excel data structure
	##################################################


	if no_fortigate:
		tprint("--------------------------Shutting down connetions to Fortigate nodes -------")
		fgt1_dir = {}
		fgt2_dir = {}
		fgt_dir_list = []
		fgt1 = get_switch_telnet_connection(fgt1_com,fgt1_port,password='admin')
		fgt1_dir['name'] = fgt1_name
		fgt1_dir['location'] = fgt1_location
		fgt1_dir['telnet'] = fgt1
		fgt1_dir['cfg'] = fgt1_cfg
		fgt_dir_list.append(fgt1_dir)

		fgt2 = get_switch_telnet_connection(fgt2_com,fgt2_port,password='admin')
		fgt2_dir['name'] = fgt2_name
		fgt2_dir['location'] = fgt2_location
		fgt2_dir['telnet'] = fgt2
		fgt2_dir['cfg'] = fgt2_cfg
		fgt_dir_list.append(fgt1_dir)

		if test_setup == "448D":
			pass
		if test_setup == "548D":
			fgt_shut_port(fgt1,"port13")		
			fgt_shut_port(fgt1,"port14")
			fgt_shut_port(fgt2,"port13")		
			fgt_shut_port(fgt2,"port14")


	if factory == True:
		print("------------------------------------- Factory resetting FSWs ------------------")
		for d in dut_dir_list:
			dut = d['telnet']
			dut_name = d['name']
			location = d['location']
			tprint("Factory reseting {} at {}......".format(dut_name,location))
			switch_interactive_exec(dut,"execute factoryreset","Do you want to continue? (y/n)")

		sleep(200)
		for dut in dut_list:
			relogin_if_needed(dut)

	image = find_dut_image(dut1)
	tprint("============================ Image = {}".format(image))
	stat_dir_list = []   # this the data structure that has the final report

	if setup == True or Setup_only:
		for d in dut_dir_list:
			configure_switch_file(d['telnet'],d['cfg'])
 
		tprint("++++Wait for 30 seconds before verifying configuration")
		time.sleep(30)
		print("*****************Reboot all DUTs to have a fresh start, it takes probably 3 minutes")
		i=0
		for dut in dut_list:
			i+=1
			switch_exec_reboot(dut,device="dut{}".format(i))

		time.sleep(180)
	# for dut in dut_list:
	# 	relogin_if_needed(dut)
 
	tprint("===================================== Pre-test Configuration Verification ============================")
	for dut in dut_list:
		print("########################################################################################")
		switch_show_cmd(dut,"get system status")
		switch_show_cmd(dut,"show switch trunk")
		switch_show_cmd(dut,"diagnose switch mclag peer-consistency-check")
		switch_show_cmd(dut,"get switch lldp neighbors-summary")
# chassis = "10.105.241.234"
# ixnetwork = "10.105.19.19:8004"
# #tcl_server=${Ixia Tcl Srv} | device=${Ixia Chasis} | ixnetwork_tcl_server=${Ixia IxNetwork Srv} | port_list=${Ixia ports} | reset=1 |
# portsList = ['1/1','1/2','1/3','1/4']

chassis_ip = '10.105.241.234'
tcl_server = '10.105.241.234'
ixnetwork_tcl_server = "10.105.19.19:8004"

if ixia_topo == "dhcp":
	portsList_v4 = ['1/1','1/2']
	debug("ixia_topo = {}".format(ixia_topo))
	debug("Setup IXIA with ports running as dhcp client mode")
	ports = ixia_connect_ports(chassis_ip,portsList_v4,ixnetwork_tcl_server,tcl_server)
	topo_list = []
	multiplier = 1
	dhcp_handle_list = []
	counter = 1
	for port in ports:
		(topo_handle,device_group_handle) = ixia_port_topology(port,multiplier,topo_name="Topology "+str(counter))
		topo_list.append(topo_handle)
		dhcp_status = ixia_emulation_dhcp_group_config(handle=device_group_handle)	
		dhcp_client_handle = dhcp_status['dhcpv4client_handle']
		dhcp_handle_list.append(dhcp_client_handle)
		counter +=1 

	topo_h1 = topo_list[0]
	topo_h2 = topo_list[1]
	ixia_start_protcols_verify(dhcp_handle_list)
	tprint("Creating traffic item I....")
	ixia_create_ipv4_traffic(topo_h1,topo_h2,rate=80)
	tprint("Creating traffic item II....")
	ixia_create_ipv4_traffic(topo_h2,topo_h1,rate=80)
	ixia_start_traffic()
	time.sleep(15)
	tprint("Collect statistics after running traffic for 15 seconds, Please take a look at printed traffic stats to make sure no packet loss..")
 
	traffic_stats = ixiangpf.traffic_stats(
	    mode = 'flow'
	    )
	if traffic_stats['status'] != '1':
	    tprint('\nError: Failed to get traffic flow stats.\n')
	    tprint(traffic_stats)
	    sys.exit()

	flow_stat_list = parse_traffic_stats(traffic_stats)
	print_flow_stats(flow_stat_list)
	if dev_mode == True:
		sys.exit()
		
#########################################################################################
#    	Test Case #1
#########################################################################################
if testcase == 1:
	for dut in dut_list:
		switch_unshut_port(dut,"port1")
		switch_unshut_port(dut,"port2")
		switch_unshut_port(dut,"port3")
		switch_unshut_port(dut,"port4")
	# for dut in dut_list:
	# 	switch_exec_reboot(dut)
	# sleep(200)
	# for dut in dut_list:
	# 	relogin_if_needed(dut)
	pre_test_verification(dut_list)
	portsList_v4 = ['1/1','1/2','1/7','1/8']
	debug("Setup IXIA with one port pair running static IP mode")
	# handle_list = ixia_static_ipv4_setup(chassis_ip,portsList_v4,ixnetwork_tcl_server,tcl_server)
	##### Connect to IXIA chassis and configure ports, topology and protocols
	tprint("==========Connect to IXIA chassis and configure ports, topology and protocols=====")
	connect_status = ixia_connect(
		reset               =           1,
		device              =           chassis_ip,
		port_list           =           portsList_v4,
		ixnetwork_tcl_server=           ixnetwork_tcl_server,
		tcl_server          =           tcl_server,
	)

	if connect_status['status'] != '1':
		ErrorHandler('connect', connect_status)

	port_handle = connect_status['vport_list']

	ports = connect_status['vport_list'].split()

	port_1 = port_handle.split(' ')[0]
	port_2 = port_handle.split(' ')[1]
	port_3 = port_handle.split(' ')[2]
	port_4 = port_handle.split(' ')[3]
    
	lock = threading.Lock()
	port_handle = ('port_1','port_2','port_3','port_4')
	topology_handle_dict_list = []
	handle_dict = ixia_static_ipv4_topo(
		port=port_1,
		multiplier=mac_table,
		topology_name="Topology 1",
		device_group_name = "Device Group 1",
		intf_ip="100.1.0.1", 
		gateway = "100.1.100.1",
		intf_mac="00.11.01.00.00.01",
		mask="255.255.0.0",
		)

	topology_handle_dict_list.append(handle_dict)
	handle_dict = ixia_static_ipv4_topo(
		port=port_2,
		multiplier=mac_table,
		topology_name="Topology 2",
		device_group_name = "Device Group 2",
		intf_ip="100.1.100.1", 
		gateway = "100.1.0.1",
		intf_mac="00.12.01.00.00.01",
		mask="255.255.0.0"
	)
	topology_handle_dict_list.append(handle_dict)

	handle_dict = ixia_static_ipv4_topo(
		port=port_3,
		multiplier=mac_table,
		topology_name="Topology 3",
		device_group_name = "Device Group 3",
		intf_ip="100.2.0.1", 
		gateway = "100.2.100.1",
		intf_mac="00.13.01.00.00.01",
		mask="255.255.0.0"
	)
	topology_handle_dict_list.append(handle_dict)

	handle_dict= ixia_static_ipv4_topo(
		port=port_4,
		multiplier=mac_table,
		topology_name="Topology 4",
		device_group_name = "Device Group 4",
		intf_ip="100.2.100.1", 
		gateway = "100.2.0.1",
		intf_mac="00.14.01.00.00.01",
		mask="255.255.0.0"
	)
	topology_handle_dict_list.append(handle_dict)
	

	ethernet_1_handle = topology_handle_dict_list[0]['ethernet_handle']
	ethernet_2_handle = topology_handle_dict_list[1]['ethernet_handle']
	ethernet_3_handle = topology_handle_dict_list[2]['ethernet_handle']
	ethernet_4_handle = topology_handle_dict_list[3]['ethernet_handle']

	port_1_handle = topology_handle_dict_list[0]['port_handle']
	port_2_handle = topology_handle_dict_list[1]['port_handle']
	port_3_handle = topology_handle_dict_list[2]['port_handle']
	port_4_handle = topology_handle_dict_list[3]['port_handle']

	topology_1_handle = topology_handle_dict_list[0]['topology_handle']
	topology_2_handle = topology_handle_dict_list[1]['topology_handle']
	topology_3_handle = topology_handle_dict_list[2]['topology_handle']
	topology_4_handle = topology_handle_dict_list[3]['topology_handle']

	ipv4_1_handle = topology_handle_dict_list[0]['ipv4_handle']
	ipv4_2_handle = topology_handle_dict_list[1]['ipv4_handle']
	ipv4_3_handle = topology_handle_dict_list[2]['ipv4_handle']
	ipv4_4_handle = topology_handle_dict_list[3]['ipv4_handle']


	deviceGroup_1_handle = topology_handle_dict_list[0]['deviceGroup_handle']
	deviceGroup_2_handle = topology_handle_dict_list[1]['deviceGroup_handle']
	deviceGroup_3_handle = topology_handle_dict_list[2]['deviceGroup_handle']
	deviceGroup_4_handle = topology_handle_dict_list[3]['deviceGroup_handle']

	ip_handle_list= [ipv4_1_handle,ipv4_2_handle,ipv4_3_handle,ipv4_4_handle]
	ixia_start_protcols_verify(ip_handle_list)

	tprint("Creating traffic item I....")
	ixia_create_ipv4_traffic(topology_1_handle,topology_2_handle)
	tprint("Creating traffic item II....")
	ixia_create_ipv4_traffic(topology_2_handle,topology_1_handle)
	ixia_start_traffic()

	tprint("Test Case #{}: Start executing test case and generating activites".format(testcase))
	stop_threads = False
	thread1 = Thread(target = mac_log_stress,args = (topology_handle_dict_list,dut_list,mac_table,lambda: stop_threads))
	thread1.start()
	thread2 = Thread(target = dut_polling,args = (dut_list,lambda: stop_threads))
	thread2.start()
	thread3 = Thread(target = dut_cpu_memory,args = (dut_dir_list,lambda: stop_threads))
	thread3.start()
	sleep(5)
	try:
		while True:
			ixia_clear_traffic_stats()
			traffic_stats = collect_ixia_traffic_stats()
			flow_stat_list = parse_traffic_stats(traffic_stats)
			print_flow_stats_3rd(flow_stat_list)
			sleep(30)
	except KeyboardInterrupt:
		print ("=== Main thread:Ctrl-c received! Sending kill to threads...")
		stop_threads = True
		thread1.kill_received = True
		thread2.kill_received = True
#########################################################################################
#    	Test Case #2: MC-LAG Performance Measurement
#########################################################################################
if testcase == 2:
	port_handle = ('port_1','port_2','port_3','port_4')
	topology_handle_dict_list = []
	handle_dict = ixia_static_ipv4_topo(
		port=port_1,
		multiplier=1,
		topology_name="Topology 1",
		device_group_name = "Device Group 1",
		intf_ip="100.1.0.1", 
		gateway = "100.1.0.2",
		intf_mac="00.11.01.00.00.01",
		mask="255.255.255.0",
		)

	topology_handle_dict_list.append(handle_dict)
	handle_dict = ixia_static_ipv4_topo(
		port=port_2,
		multiplier=1,
		topology_name="Topology 2",
		device_group_name = "Device Group 2",
		intf_ip="100.1.0.2", 
		gateway = "100.1.0.1",
		intf_mac="00.12.01.00.00.01",
		mask="255.255.255.0"
	)
	topology_handle_dict_list.append(handle_dict)

	handle_dict = ixia_static_ipv4_topo(
		port=port_3,
		multiplier=mac_table,
		topology_name="Topology 3",
		device_group_name = "Device Group 3",
		intf_ip="100.2.0.1", 
		gateway = "100.2.10.1",
		intf_mac="00.13.01.00.00.01",
		mask="255.255.0.0"
	)
	topology_handle_dict_list.append(handle_dict)

	handle_dict= ixia_static_ipv4_topo(
		port=port_4,
		multiplier=mac_table,
		topology_name="Topology 4",
		device_group_name = "Device Group 4",
		intf_ip="100.2.10.1", 
		gateway = "100.2.0.1",
		intf_mac="00.14.01.00.00.01",
		mask="255.255.0.0"
	)
	topology_handle_dict_list.append(handle_dict)
	

	ethernet_1_handle = topology_handle_dict_list[0]['ethernet_handle']
	ethernet_2_handle = topology_handle_dict_list[1]['ethernet_handle']
	ethernet_3_handle = topology_handle_dict_list[2]['ethernet_handle']
	ethernet_4_handle = topology_handle_dict_list[3]['ethernet_handle']

	port_1_handle = topology_handle_dict_list[0]['port_handle']
	port_2_handle = topology_handle_dict_list[1]['port_handle']
	port_3_handle = topology_handle_dict_list[2]['port_handle']
	port_4_handle = topology_handle_dict_list[3]['port_handle']

	topology_1_handle = topology_handle_dict_list[0]['topology_handle']
	topology_2_handle = topology_handle_dict_list[1]['topology_handle']
	topology_3_handle = topology_handle_dict_list[2]['topology_handle']
	topology_4_handle = topology_handle_dict_list[3]['topology_handle']

	ipv4_1_handle = topology_handle_dict_list[0]['ipv4_handle']
	ipv4_2_handle = topology_handle_dict_list[1]['ipv4_handle']
	ipv4_3_handle = topology_handle_dict_list[2]['ipv4_handle']
	ipv4_4_handle = topology_handle_dict_list[3]['ipv4_handle']


	deviceGroup_1_handle = topology_handle_dict_list[0]['deviceGroup_handle']
	deviceGroup_2_handle = topology_handle_dict_list[1]['deviceGroup_handle']
	deviceGroup_3_handle = topology_handle_dict_list[2]['deviceGroup_handle']
	deviceGroup_4_handle = topology_handle_dict_list[3]['deviceGroup_handle']

	ip_handle_list= [ipv4_1_handle,ipv4_2_handle,ipv4_3_handle,ipv4_4_handle]
	ixia_start_protcols_verify(ip_handle_list)
	tprint("Creating traffic item I....")
	ixia_create_ipv4_traffic(topology_1_handle,topology_2_handle)
	tprint("Creating traffic item II....")
	ixia_create_ipv4_traffic(topology_2_handle,topology_1_handle)
	ixia_start_traffic()
	
	time.sleep(15)
	
	tprint("Collect statistics after running traffic for 15 seconds, Please take a look at printed traffic stats to make sure no packet loss..")
 
	traffic_stats = ixiangpf.traffic_stats(
	    mode = 'flow'
	    )

	if traffic_stats['status'] != '1':
	    tprint('\nError: Failed to get traffic flow stats.\n')
	    tprint(traffic_stats)
	    sys.exit()

	flow_stat_list = parse_traffic_stats(traffic_stats)
	print_flow_stats(flow_stat_list)
	if dev_mode == True:
		stop_threads = True
		thread.join()
		#thread2.join()
		sys.exit()

	# for dut in dut_list:
	# 	relogin_if_needed(dut)


	if Setup_only == True:
		tprint("========== Finished setting up testbed and IXIA traffic for manual testing ===============")
		exit()

	#For fortigate setup, you can not change managed FSW's MCLAG config
	if test_setup.lower() != "fgt":
		topology_mclag_8(dut_list)  #temp
		time.sleep(20) #temp
		pass
	pre_test_verification(dut_list) #temp
	# stat_dir_list = [{'member': 2, 'B1:H1': '2-member LACP trunk', 'B2:F2': 'image name to be filled', 'B3': 'No.', 'C3': 'Action', 'D3:E3': 'Frame Loss', 'F3': 'Loss Time Sec', 'B4': 'Test 1', 'C4': 'un-plug 1st active link', 'D4': 'host1', 'D5': 'host2', 'C7': 'un-plug 2nd active link', 'D7': 'host1', 'D8': 'host2', 'C10': 're-connect 2nd link', 'D10': 'host1', 'D11': 'host2', 'C13': 're-connect 1st active link', 'D13': 'host1', 'D14': 'host2', 'C16': 'Tier-1 DUT1 Down', 'D16': 'host1', 'D17': 'host2', 'C18': 'Tier-1 DUT2 Down', 'D18': 'host1', 'D19': 'host2', 'C21': 'Tier-1 DUT1 Up', 'D21': 'host1', 'D22': 'host2', 'C23': 'Tier-1 DUT2 Up', 'D23': 'host1', 'D24': 'host2', 'C26': 'Tier-2 DUT3 Down', 'D26': 'host1', 'D27': 'host2', 'C28': 'Tier-2 DUT4 Down', 'D28': 'host1', 'D29': 'host2', 'C31': 'Tier-2 DUT3 Up', 'D31': 'host1', 'D32': 'host2', 'C33': 'Tier-2 DUT4 Up', 'D33': 'host1', 'D34': 'host2', 'test': 1, 'sheetname': 'LACP-2 Test1'}, {'member': 2, 'B1:H1': '2-member LACP trunk', 'B2:F2': 'image name to be filled', 'B3': 'No.', 'C3': 'Action', 'D3:E3': 'Frame Loss', 'F3': 'Loss Time Sec', 'B4': 'Test 2', 'C4': 'un-plug 1st active link', 'D4': 'host1', 'D5': 'host2', 'C7': 'un-plug 2nd active link', 'D7': 'host1', 'D8': 'host2', 'C10': 're-connect 2nd link', 'D10': 'host1', 'D11': 'host2', 'C13': 're-connect 1st active link', 'D13': 'host1', 'D14': 'host2', 'C16': 'Tier-1 DUT1 Down', 'D16': 'host1', 'D17': 'host2', 'C18': 'Tier-1 DUT2 Down', 'D18': 'host1', 'D19': 'host2', 'C21': 'Tier-1 DUT1 Up', 'D21': 'host1', 'D22': 'host2', 'C23': 'Tier-1 DUT2 Up', 'D23': 'host1', 'D24': 'host2', 'C26': 'Tier-2 DUT3 Down', 'D26': 'host1', 'D27': 'host2', 'C28': 'Tier-2 DUT4 Down', 'D28': 'host1', 'D29': 'host2', 'C31': 'Tier-2 DUT3 Up', 'D31': 'host1', 'D32': 'host2', 'C33': 'Tier-2 DUT4 Up', 'D33': 'host1', 'D34': 'host2', 'sheetname': 'LACP-2 Test2', 'test': 2}, {'member': 8, 'B1:H1': '2-member LACP trunk', 'B2:F2': 'image name to be filled', 'B3': 'No.', 'C3': 'Action', 'D3:E3': 'Frame Loss', 'F3': 'Loss Time Sec', 'B4': 'Test 1', 'C4': 'un-plug 1st active link', 'D4': 'host1', 'D5': 'host2', 'C7': 'un-plug 3~4 active link', 'D7': 'host1', 'D8': 'host2', 'C10': 're-connect 3~4 link', 'D10': 'host1', 'D11': 'host2', 'C13': 're-connect 1st active link', 'D13': 'host1', 'D14': 'host2', 'C16': 'Tier-1 DUT1 Down', 'D16': 'host1', 'D17': 'host2', 'C18': 'Tier-1 DUT2 Down', 'D18': 'host1', 'D19': 'host2', 'C21': 'Tier-1 DUT1 Up', 'D21': 'host1', 'D22': 'host2', 'C23': 'Tier-1 DUT2 Up', 'D23': 'host1', 'D24': 'host2', 'C26': 'Tier-2 DUT3 Down', 'D26': 'host1', 'D27': 'host2', 'C28': 'Tier-2 DUT4 Down', 'D28': 'host1', 'D29': 'host2', 'C31': 'Tier-2 DUT3 Up', 'D31': 'host1', 'D32': 'host2', 'C33': 'Tier-2 DUT4 Up', 'D33': 'host1', 'D34': 'host2', 'sheetname': 'LACP-8 Test1', 'test': 1, 'E22': 9, 'F22': '7.344001175040188e-05 seconds', 'E21': 8, 'F21': '6.528001044480167e-05 seconds'}, {'member': 8, 'B1:H1': '2-member LACP trunk', 'B2:F2': 'image name to be filled', 'B3': 'No.', 'C3': 'Action', 'D3:E3': 'Frame Loss', 'F3': 'Loss Time Sec', 'B4': 'Test 2', 'C4': 'un-plug 1st active link', 'D4': 'host1', 'D5': 'host2', 'C7': 'un-plug 3~4 active link', 'D7': 'host1', 'D8': 'host2', 'C10': 're-connect 3~4 link', 'D10': 'host1', 'D11': 'host2', 'C13': 're-connect 1st active link', 'D13': 'host1', 'D14': 'host2', 'C16': 'Tier-1 DUT1 Down', 'D16': 'host1', 'D17': 'host2', 'C18': 'Tier-1 DUT2 Down', 'D18': 'host1', 'D19': 'host2', 'C21': 'Tier-1 DUT1 Up', 'D21': 'host1', 'D22': 'host2', 'C23': 'Tier-1 DUT2 Up', 'D23': 'host1', 'D24': 'host2', 'C26': 'Tier-2 DUT3 Down', 'D26': 'host1', 'D27': 'host2', 'C28': 'Tier-2 DUT4 Down', 'D28': 'host1', 'D29': 'host2', 'C31': 'Tier-2 DUT3 Up', 'D31': 'host1', 'D32': 'host2', 'C33': 'Tier-2 DUT4 Up', 'D33': 'host1', 'D34': 'host2', 'sheetname': 'LACP-8 Test2', 'test': 2, 'E22': 8, 'F22': '6.528001044480167e-05 seconds', 'E21': 8, 'F21': '6.528001044480167e-05 seconds'}]

	# filename = "LACP_Perf.xlsx"
	# dict_2_excel(stat_dir_list,filename)
	# exit()

	create_excel_sheets(stat_dir_list,image,mem=2,runtime=Run_time)
	create_excel_sheets(stat_dir_list,image,mem=8,runtime=Run_time)
	thread = Thread(target = background_ixia_activity,args = (topology_handle_dict_list,dut_list,lambda: stop_threads))
	thread.start()
	# thread2 = Thread(target = period_login,args = (dut_list,lambda: stop_threads))
	# thread2.start()

	if log_mac_event:
		switch_configure_cmd(dut3,"config switch interface")
		switch_configure_cmd(dut3,"edit port39")
		switch_configure_cmd(dut3,"set log-mac-event enable")
		switch_configure_cmd(dut3,"end")

		switch_configure_cmd(dut4,"config switch interface")
		switch_configure_cmd(dut4,"edit port39")
		switch_configure_cmd(dut4,"set log-mac-event enable")
		switch_configure_cmd(dut4,"end")
	else:
		switch_configure_cmd(dut3,"config switch interface")
		switch_configure_cmd(dut3,"edit port39")
		switch_configure_cmd(dut3,"set log-mac-event disable")
		switch_configure_cmd(dut3,"end")

		switch_configure_cmd(dut4,"config switch interface")
		switch_configure_cmd(dut4,"edit port39")
		switch_configure_cmd(dut4,"set log-mac-event disable")
		switch_configure_cmd(dut4,"end")

	pre_test_verification(dut_list)

	if Reboot == True:
		tprint("===================================== DUT_1 Reboot MALAG PERFORMANCE Test:8-Member =======================")
		reboot_result = dut_reboot_test_new(dut1,dut="dut1",mem=8,runtime=Run_time)
		debug("!!!!!! debug: print reboot_result after reboot test")
		debug(reboot_result)
		dict_lacp_boot_update(dir_list=stat_dir_list,dut_name="dut1",mem=8,result=reboot_result)
		debug("!!!!! print stat dir list after updating the stats dictionary")
		debug(stat_dir_list)
		 
		tprint("===================================== DUT_2 Reboot MALAG PERFORMANCE Test:8-Member =======================")
		reboot_result = dut_reboot_test_new(dut2,dut="dut2",mem=8,runtime=Run_time)
		dict_lacp_boot_update(dir_list=stat_dir_list,dut_name="dut2",mem=8,result=reboot_result)
		debug(stat_dir_list)

		tprint("===================================== DUT_3 Reboot MALAG PERFORMANCE Test:8-Member =======================")
		reboot_result = dut_reboot_test_new(dut3,dut="dut3",mem=8,runtime=Run_time)
		dict_lacp_boot_update(dir_list=stat_dir_list,dut_name="dut3",mem=8,result=reboot_result)
		debug(stat_dir_list)

		tprint("===================================== DUT_4 Reboot MALAG PERFORMANCE Tes:8-Membert =======================")
		reboot_result = dut_reboot_test_new(dut4,dut="dut4",mem=8,runtime=Run_time)
		dict_lacp_boot_update(dir_list=stat_dir_list,dut_name="dut4",mem=8,result=reboot_result)
		debug(stat_dir_list)


		# for dut in dut_list:
		# 	relogin_if_needed(dut)
		fiber_result = dut_fibercut_test(dut2_dir,mode,tier = 1, mem=8,dut_name="dut2",runtime=Run_time)
		dict_lacp_boot_update(dir_list=stat_dir_list,dut_name="dut2",mem=8,result=fiber_result)
		debug(stat_dir_list)
		fiber_result = dut_fibercut_test(dut4_dir,mode,tier = 2, mem=8,dut_name="dut4",runtime=Run_time)
		dict_lacp_boot_update(dir_list=stat_dir_list,dut_name="dut4",mem=8,result=fiber_result)
		debug(stat_dir_list)
		# old ---dut_shut_test_mclag_8(dut2,dut4)

		if test_setup.lower() != "fgt":
			topology_mclag_4(dut_list)
			time.sleep(20)

		if Reboot == True:
			tprint("===================================== DUT_1 Reboot MALAG PERFORMANCE Test:2-Member =======================")
			reboot_result = dut_reboot_test_new(dut1,dut="dut1",mem=2,runtime=Run_time)
			debug("!!!!!! debug: print reboot_result after reboot test")
			debug(reboot_result)
			dict_lacp_boot_update(dir_list=stat_dir_list,dut_name="dut1",mem=2,result=reboot_result)
			debug("!!!!! print stat dir list after updating the stats dictionary")
			debug(stat_dir_list)
			 
			tprint("===================================== DUT_2 Reboot MALAG PERFORMANCE Test:2-Member =======================")
			reboot_result = dut_reboot_test_new(dut2,dut="dut2",mem=2,runtime=Run_time)
			dict_lacp_boot_update(dir_list=stat_dir_list,dut_name="dut2",mem=2,result=reboot_result)
			debug(stat_dir_list)

			tprint("===================================== DUT_3 Reboot MALAG PERFORMANCE Test:2-Member =======================")
			reboot_result = dut_reboot_test_new(dut3,dut="dut3",mem=2,runtime=Run_time)
			dict_lacp_boot_update(dir_list=stat_dir_list,dut_name="dut3",mem=2,result=reboot_result)
			debug(stat_dir_list)

			tprint("===================================== DUT_4 Reboot MALAG PERFORMANCE Tes:2-Membert =======================")
			reboot_result = dut_reboot_test_new(dut4,dut="dut4",mem=2,runtime=Run_time)
			dict_lacp_boot_update(dir_list=stat_dir_list,dut_name="dut4",mem=2,result=reboot_result)
			debug(stat_dir_list)

			tprint ("=============================== Done: Performance Reboot Test  ===========================")


		tprint ("=============================== Start: Fiber Cut Test ===========================")	
		debug("Fiber Cut Test: Relogin DUTs if necessary ")
		for dut in dut_list:
			relogin_if_needed(dut)
		fiber_result = dut_fibercut_test(dut2_dir, mode,tier = 1, mem=2,dut_name="dut2",runtime=Run_time)
		dict_lacp_boot_update(dir_list=stat_dir_list,dut_name="dut2",mem=2,result=fiber_result)
		debug(stat_dir_list)
		fiber_result = dut_fibercut_test(dut4_dir,mode,tier = 2, mem=2,dut_name="dut4",runtime=Run_time)
		dict_lacp_boot_update(dir_list=stat_dir_list,dut_name="dut4",mem=2,result=fiber_result)
		debug(stat_dir_list)

		tprint ("=============================== Done: Fiber Cut Test ===========================")	

		filename = "MCLAG_Perf_"+test_setup+"_"+file_appendix+".xlsx"
		dict_2_excel(stat_dir_list,filename)
		sleep(5)
		scp_file(file=filename)
		stop_threads = True
		thread.join()
		tprint(" ===================================== End OF MCLAG Port-Down Performance Test:4-Member ========================= ")

# topology_change_428(dut_list)
# pre_test_verification(dut_list)
#dut_unplug_test_mclag_4(dut2,dut4)

####################################################
# Stop traffic
####################################################
tprint(" ===================================== Stop IXIA traffic and clean up ========================= ")
kwargs={}
kwargs['action']='stop'
kwargs['max_wait_timer']=60

tprint("Stopping traffic....")
tprint("Wait for 20 seconds before collect final traffic")
traffic_control_status = ixiangpf.traffic_control(**kwargs)
time.sleep(20)

if traffic_control_status['status'] != '1':
    ErrorHandler('traffic_control', traffic_control_status)
else:
    if traffic_control_status['stopped'] == '0':
        ixia_tprint("traffic is not stop yet... Give poll for the traffic status for another 60 seconds\n")
        count = 30
        waitTime = 0
        while True:
            traffic_poll_status = ixiangpf.traffic_control(
                action = 'poll',
            )
            if traffic_poll_status['stopped'] == '0':
                if count == 0:
                    break
                else:
                    time.sleep(2)
                    count -= 1
                    waitTime += 2
            else:
                break

        if traffic_poll_status['stopped'] == '0':
            ErrorHandler('traffic_control', traffic_control_status)
        else:
            ixia_tprint('traffic is stopped (wait time=%s seconds)' % waitTime)
    else:
        tprint('traffic is stopped')
        time.sleep(2)
	
################################################################################
# Collect traffic statistics                                                             #
################################################################################

tprint("Collect statistics after stooping traffic ....")
#tprint('\ngetList: ', ixNet.getList(ixNet.getRoot()+'traffic', 'trafficItem'))
traffic_stats = ixiangpf.traffic_stats(
    mode = 'flow'
    )

if traffic_stats['status'] != '1':
    tprint('\nError: Failed to get traffic flow stats.\n')
    tprint(traffic_stats)
    sys.exit()

flow_stat_list = parse_traffic_stats(traffic_stats)
print_flow_stats(flow_stat_list)
# print_dict(traffic_stats)
# tprint(traffic_stats)
 

#thread2.join()
####################################################
# Test END
####################################################

print("###################")
tprint("Test run is PASSED")
print("###################")


##################################################################################################################################################
##################################################################################################################################################
