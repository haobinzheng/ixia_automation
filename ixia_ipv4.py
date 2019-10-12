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

# Append paths to python APIs (Linux and Windows)

sys.path.append('C:/Program Files (x86)/Ixia/hltapi/4.97.0.2/TclScripts/lib/hltapi/library/common/ixiangpf/python')
sys.path.append('C:/Program Files (x86)/Ixia/IxNetwork/7.50.0.8EB/API/Python')

from ixiatcl import IxiaTcl
from ixiahlt import IxiaHlt
from ixiangpf import IxiaNgpf
from ixiaerror import IxiaError


ixiatcl = IxiaTcl()
ixiahlt = IxiaHlt(ixiatcl)
ixiangpf = IxiaNgpf(ixiahlt)
ixNet = ixiangpf.ixnet # For low level Python API commands

from ixia_ngfp_lib import *
from utils import *


################################################################################
# Connection to the chassis, IxNetwork Tcl Server                 			   #
################################################################################

# This section should contain the connect procedure values (device ip, port list etc) and, of course, the connect procedure		

chassis_ip = '10.105.241.234'
tcl_server = '10.105.241.234'
ixnetwork_tcl_server = "10.105.19.19:8004"
portsList = ['1/1','1/2','1/3','1/4']



def pre_test_verification(dut_list):
	for dut in dut_list:
		print("########################################################################################")
		switch_show_cmd(dut,"get system status")
		switch_show_cmd(dut,"show switch trunk")
		switch_show_cmd(dut,"diagnose switch mclag peer-consistency-check")
		switch_show_cmd(dut,"get switch lldp neighbors-summary")

def topology_change_428(dut_list):
	print("--------------------------------------------------------------------------")
	print(" 		Change the MCALG Topology from 4-members to 8 members")
	print("--------------------------------------------------------------------------")
	for dut in dut_list:
		switch_unshut_port(dut,"port1")
		switch_unshut_port(dut,"port3")
		switch_configure_cmd(dut,"config switch trunk")
		switch_configure_cmd(dut,"edit mclag-core")
		switch_configure_cmd(dut,"set members port1 port2 port3 port4")
		switch_configure_cmd(dut,"end")
		time.sleep(20)

def topology_change_824(dut_list):
	print("--------------------------------------------------------------------------")
	print(" 		Change the MCALG Topology from 4-members to 8 members")
	print("--------------------------------------------------------------------------")
	for dut in dut_list:
		switch_shut_port(dut,"port1")
		switch_shut_port(dut,"port3")
		switch_configure_cmd(dut,"config switch trunk")
		switch_configure_cmd(dut,"edit mclag-core")
		switch_configure_cmd(dut,"set members port2 port4")
		switch_configure_cmd(dut,"end")
		time.sleep(20)

def dut_shut_test_mclag_4(dut2,dut4):
	wait_time = 10
	for i in range(2):
		tprint("========= Run Time #{}".format(i))
		tprint("Shut 1st active port on dut4 -- Rack20-22: port4")
		switch_shut_port(dut4,"port4")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to unplugging first active link on DUT4----------")
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

def dut_fibercut_test(dut,**kwargs):
	twargs = {}
	for k, v in kwargs.items():
		twargs[k] = v

	dut_name = twargs["dut_name"]
	lag_mem = twargs["mem"]
	tier = twargs["tier"]
	mode = twargs["mode"]
	location = "XXXXX" # future: location = dut["location"] or something like that
	test_list = []
	wait_time = 10
	for i in range(2):
		iterate_list = []
		relogin_if_needed(dut)
		tprint("========= Run Time #{}".format(i))
		first_active_port = "port4" # future: port=find_active_trunk_port(dut)
		tprint("Shut 1st active port: {} on dut located at:{}".format(first_active_port,location))  # this has to change to have location and port# dynamic
		switch_shut_port(dut,first_active_port)
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
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
			tprint("MCLAG-8: Shut 2nd and 3rd inactive ports: {},{} on dut:{} located at {} ". \
				format(lag8_inactive_port1,lag8_inactive_port2,dut_name,location))
			switch_shut_port(dut,lag8_inactive_port1)
			switch_shut_port(dut,lag8_inactive_port2)
		else:
			lag2_2nd_port = "port2" # future: port1  = find_active_trunk_port()
			tprint("MCLAG-2: Shut 2nd active port {} on dut:{} located at {} ".format(lag2_2nd_port,dut_name,location))
			switch_shut_port(dut,lag2_2nd_port)
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
			switch_unshut_port(dut,lag8_inactive_port1)
			switch_unshut_port(dut,lag8_inactive_port2)
		else:
			tprint("MCLAG-2: UnShut 2nd active port {} on dut:{} located at {} ".format(lag2_2nd_port,dut_name,location))
			switch_unshut_port(dut,lag2_2nd_port)
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
			switch_unshut_port(dut,first_active_port)
		else:
			tprint("MCLAG2: Unshut first active port:{} on dut: {} located at: {}".format(first_active_port,dut_name,location))
			switch_unshut_port(dut,first_active_port)
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		traffic_stats = collect_ixia_traffic_stats()
		 
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
		keyin = input("Are you done with unplugging cable? if so press any key")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to unplugging first active link on DUT4----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()

		tprint("Unplug 2nd active link on dut4 -- Rack20-22: port2")
		keyin = input("Are you done with unplugging cable? if so press any key")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to unplugging 2nd active link on DUT4----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()

		tprint("Reconnect 2nd active link on dut4 -- Rack20-22: port2")
		keyin = input("Are you done with changing cable? if so press any key")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to reconnect 2nd active link on DUT4----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
		
		tprint("Reconnect first active link on dut4 -- Rack20-22: port4")
		keyin = input("Are you done with changing cable? if so press any key")
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
		keyin = input("Are you done with changing cable? if so press any key")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to unplugging first active link on DUT2----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()

		tprint("Unplug 2nd active link on dut4 -- Rack23-28: port2")
		keyin = input("Are you done with changing cable? if so press any key")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to unplugging 2nd active link on DUT2----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()

		tprint("Reconnect 2nd active link on dut4 -- Rack23-28: port2")
		keyin = input("Are you done with changing cable? if so press any key")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to reconnect 2nd active link on DUT2----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
		
		tprint("Reconnect first active link on dut4 -- Rack23-28: port4")
		keyin = input("Are you done with changing cable? if so press any key")
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
	test_list = []
	for i in range(2):
		iterate_list = []
		relogin_if_needed(dut1)
		tprint("========= Run Time #{}".format(i))
		tprint("Rebooting DUT....")
		switch_exec_reboot(dut1,device="DUT")
		tprint("DUT is being rebooted, wait for 20 seconds before measuring traffic loss")
		time.sleep(20)
		tprint("After waiting for 20 seconds,collect ixia traffic stats")
		print("********* Measure packet loss due to DUT does down after reboot----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list_down = parse_traffic_stats_new(traffic_stats,reason="down")
		for f in flow_stat_list_down:
			f['dut'] = dut_name
			f['lag_mem'] = lag_mem
			f['test_num'] = i+1
		print_flow_stats_new(flow_stat_list_down)

		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()

		tprint("Allow traffic to run for another 120 seconds after rebooting ....")
		time.sleep(120)
		tprint("Collect traffic stats 180seconds after DUT1 rebooted")
		print("*********** Measure packet loss due to STP converage after DUT finished rebooting-------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list_up = parse_traffic_stats_new(traffic_stats,reason="up")
		for f in flow_stat_list_up:
			f['dut'] = dut_name
			f['lag_mem'] = lag_mem
			f['test_num'] = i+1
		print_flow_stats_new(flow_stat_list_up)
		iterate_list = flow_stat_list_up + flow_stat_list_down
		test_list.append(iterate_list)
		

		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()

	return test_list
# def print_flow_stats(flow_stats_list):
# 	for flow in flow_stats_list:
# 		tprint("Flow ID:{}, RX_Port:{}, TX_Port:{}, TX packet rate:{}, TX packets:{}, RX packets:{},Pkt Loss:{}, Pkt Loss time:{}". \
# 			format(flow['id'],flow['rx_port'],flow['tx_port'],flow['total_pkt_rate'], \
# 				flow['total_tx_pkts'],flow['total_rx_pkts'],flow['loss_pkts'],flow["loss_time"]))
# 		tprint("")

# 		print("--------------------------------")

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
parser.add_argument("-a", "--auto", help="Run in fully automated mode without manually unplugging cables", action="store_true")
parser.add_argument("-t", "--testbed", type=str, help="Specific which testbed to run this test")
parser.add_argument("-d", "--dev", help="Development mode, do not verify any network status", action="store_true")


if len(sys.argv) > 1:
    #parser.print_help()
    args = parser.parse_args()
    if args.config:
        setup = True
        tprint("----- Before starting testing, configure devices")
    else:
    	setup = False   
    	tprint("-----Skip setting up testbed and configuring devices")  
    if args.auto:
        manual = False
    else:
    	manual = True
    if args.testbed:
    	test_setup = args.testbed
    if args.dev:
        dev_mode = True
    else:
    	dev_mode = False

#If in code development mode, skipping loging into switches 
if dev_mode == False:
	stat_dir_list = []
	d = dict_lacp_blank(2)
	d["test"] = 1
	d['B4'] = "Test 1"
	d["sheetname"] = "LACP-2 Test1"
	stat_dir_list.append(d)
	d = dict_lacp_blank(2)
	d["sheetname"] = "LACP-2 Test2"
	d["test"] = 2
	d['B4'] = "Test 2"
	stat_dir_list.append(d)

	d = dict_lacp_blank(8)
	d["sheetname"] = "LACP-8 Test1"
	d["test"] = 1
	d['B4'] = "Test 1"
	stat_dir_list.append(d)
	d = dict_lacp_blank(8)
	d["sheetname"] = "LACP-8 Test2"
	d["test"] = 2
	d['B4'] = "Test 2"
	stat_dir_list.append(d)

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
	if test_setup == "548D":
		################################
		#548D Test setup
		################################
		dut1_com = "10.105.50.3"
		dut1_port = 2057
		dut2_com = "10.105.50.3"
		dut2_port = 2056
		dut3_com = "10.105.50.1"
		dut3_port = 2075
		dut4_com = "10.105.50.1"
		dut4_port = 2078
		switch_shut_port(sw1,"port25")
		switch_shut_port(sw1,"port26")
		switch_unshut_port(sw1,"port13")
		switch_unshut_port(sw1,"port14")

		switch_shut_port(sw2,"port23")
		switch_shut_port(sw2,"port24")
		switch_unshut_port(sw2,"port13")
		switch_unshut_port(sw2,"port14")


	if test_setup == "448D":
		##############################
		#448D Test stup
		##############################
		dut1_com = "10.105.50.1"
		dut1_port = 2074
		dut2_com = "10.105.50.1"
		dut2_port = 2081
		dut3_com = "10.105.50.2"
		dut3_port = 2077
		dut4_com = "10.105.50.2"
		dut4_port = 2078
		switch_unshut_port(sw1,"port25")
		switch_unshut_port(sw1,"port26")
		switch_shut_port(sw1,"port13")
		switch_shut_port(sw1,"port14")

		switch_unshut_port(sw2,"port23")
		switch_unshut_port(sw2,"port24")
		switch_shut_port(sw2,"port13")
		switch_shut_port(sw2,"port14")

	dut1 = get_switch_telnet_connection(dut1_com,dut1_port)

	dut2 = get_switch_telnet_connection(dut2_com,dut2_port)

	dut3 = get_switch_telnet_connection(dut3_com,dut3_port)

	dut4 = get_switch_telnet_connection(dut4_com,dut4_port)

	dut_list = [dut1,dut2,dut3,dut4]

	# for dut in dut_list:
	# 	switch_login(dut)
	if setup == True:
		configure_switch_file(dut1,"dut1_548d.cfg")
		configure_switch_file(dut2,"dut2_548d.cfg")
		configure_switch_file(dut3,"dut3_548d.cfg")
		configure_switch_file(dut4,"dut4_548d.cfg")

		tprint("++++Wait for 30 seconds before verifying configuration")
		time.sleep(30)
		tprint("===================================== After Initical Configuration Verification ============================")
		for dut in dut_list:
			print("########################################################################################")
			switch_show_cmd(dut,"get system status")
			switch_show_cmd(dut,"show switch trunk")
			switch_show_cmd(dut,"diagnose switch mclag peer-consistency-check")
			switch_show_cmd(dut,"get switch lldp neighbors-summary")

		print("*****************Reboot all DUTs to have a fresh start, it takes probably 3 minutes")
		i=0
		for dut in dut_list:
			i+=1
			switch_exec_reboot(dut,device="dut{}".format(i))

		time.sleep(180)
		for dut in dut_list:
			relogin_if_needed(dut1)
 
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

connect_status = ixiangpf.connect(
    reset 				=			1,
    device				=			chassis_ip,
    port_list			=			portsList,
    ixnetwork_tcl_server=			ixnetwork_tcl_server,
    tcl_server			=			tcl_server,
)

if connect_status['status'] != '1':
    ErrorHandler('connect', connect_status)

port_handle = connect_status['vport_list']

ports = connect_status['vport_list'].split()

port_1 = port_handle.split(' ')[0]
port_2 = port_handle.split(' ')[1]
port_3 = port_handle.split(' ')[2]
port_4 = port_handle.split(' ')[3]

port_handle = ('port_1','port_2','port_3','port_4')


################################################################################
# Configure Topology 1, Device Group 1                                         #
################################################################################

topology_1_status = ixiangpf.topology_config(
        topology_name     = 'Topology 1',
        port_handle       = port_1,
    )
topology_1_handle = topology_1_status['topology_handle']

if topology_1_status['status'] != IxiaHlt.SUCCESS:
    ErrorHandler('topology_config', topology_1_status)

device_group_1_status = ixiangpf.topology_config(
        topology_handle			    = topology_1_handle,
        device_group_name			= 'Device Group 1',
        device_group_multiplier	    = "1",
        device_group_enabled		= "1",
    )
	
if device_group_1_status['status'] != IxiaHlt.SUCCESS:
    ErrorHandler('topology_config', device_group_1_status)
	
deviceGroup_1_handle = device_group_1_status['device_group_handle']

################################################################################
# Configure protocol interfaces for first topology                             #
################################################################################

multivalue_1_status = ixiangpf.multivalue_config(
        pattern                ="counter",
        counter_start          ="00.11.01.00.00.01",
        counter_step           ="00.00.00.00.00.01",
        counter_direction      ="increment",
        nest_step              ="00.00.01.00.00.00",
        nest_owner             =topology_1_handle,
        nest_enabled           ="1",
    )
	
if multivalue_1_status['status'] != IxiaHlt.SUCCESS:
    ErrorHandler('multivalue_config', multivalue_1_status)

multivalue_1_handle = multivalue_1_status ['multivalue_handle']


ethernet_1_status =ixiangpf.interface_config(
        protocol_name                ="Ethernet 1"               ,
        protocol_handle              =deviceGroup_1_handle      ,
        mtu                          ="1500"                       ,
        src_mac_addr                 =multivalue_1_handle       ,
        vlan                         ="0"                          ,
        vlan_id                      ="1"                          ,
        vlan_id_step                 ="0"                          ,
        vlan_id_count                ="1"                          ,
        vlan_tpid                    ="0x8100"                     ,
        vlan_user_priority           ="0"                          ,
        vlan_user_priority_step      ="0"                          ,
        use_vpn_parameters           ="0"                          ,
        site_id                      ="0"                          ,
    )
	
if ethernet_1_status['status'] != IxiaHlt.SUCCESS:
    ErrorHandler('interface_config', ethernet_1_status)

ethernet_1_handle = ethernet_1_status['ethernet_handle']


multivalue_2_status = ixiangpf.multivalue_config(
        pattern                ="counter"                 ,
        counter_start          ="100.1.0.1"               ,
        counter_step           ="0.0.0.1"                 ,
        counter_direction      ="increment"               ,
        nest_step              ="0.1.0.0"                 ,
        nest_owner             =topology_1_handle      ,
        nest_enabled           ="1"                       ,
    )
	
if multivalue_2_status['status'] != IxiaHlt.SUCCESS:
    ErrorHandler('multivalue_config', multivalue_2_status)	

multivalue_2_handle = multivalue_2_status['multivalue_handle']


multivalue_3_status = ixiangpf.multivalue_config(
        pattern                ="counter"                 ,
        counter_start          ="100.1.0.2"               ,
        counter_step           ="255.255.255.255"         ,
        counter_direction      ="decrement"               ,
        nest_step              ="0.0.0.1"                 ,
        nest_owner             =topology_1_handle      ,
        nest_enabled           ="0"                       ,
    )
	
if multivalue_3_status['status'] != IxiaHlt.SUCCESS:
    ErrorHandler('multivalue_config', multivalue_3_status)	

multivalue_3_handle = multivalue_3_status['multivalue_handle']


ipv4_1_status = ixiangpf.interface_config(
        protocol_name                ="IPv4 1"                  ,
        protocol_handle              =ethernet_1_handle        ,
        ipv4_resolve_gateway         ="1"                         ,
        ipv4_manual_gateway_mac      ="00.00.00.00.00.01"         ,
        gateway                      =multivalue_3_handle      ,
        intf_ip_addr                 =multivalue_2_handle      ,
        netmask                      ="255.255.255.0"             ,
    )
	
if ipv4_1_status['status'] != IxiaHlt.SUCCESS:
    ErrorHandler('interface_config', ipv4_1_status)	
	
ipv4_1_handle =ipv4_1_status['ipv4_handle']


################################################################################
# Configure Topology 2, Device Group 2                                         #
################################################################################

topology_2_status =ixiangpf.topology_config(
        topology_name      ="Topology 2"                            ,
        port_handle        =port_2							        ,
    )

if topology_2_status['status'] != IxiaHlt.SUCCESS:
    ErrorHandler('multivalue_config', topology_2_status)
	
topology_2_handle = topology_2_status['topology_handle']


device_group_2_status = ixiangpf.topology_config(
        topology_handle              =topology_2_handle      ,
        device_group_name            ="Device Group 2"        ,
        device_group_multiplier      ="1"	                  ,
        device_group_enabled         ="1"                       ,
    )

if device_group_2_status['status'] != IxiaHlt.SUCCESS:
    ErrorHandler('multivalue_config', device_group_2_status)

deviceGroup_2_handle = device_group_2_status['device_group_handle']

################################################################################
# Configure protocol interfaces for second topology                             #
################################################################################

multivalue_4_status =ixiangpf.multivalue_config(
        pattern               ="counter"                 ,
        counter_start         ="00.12.01.00.00.01"       ,
        counter_step          ="00.00.00.00.00.01"       ,
        counter_direction     ="increment"               ,
        nest_step             ="00.00.01.00.00.00"       ,
        nest_owner            =topology_2_handle      ,
        nest_enabled          ="1"                       ,
    )
	
if multivalue_4_status['status'] != IxiaHlt.SUCCESS:
    ErrorHandler('multivalue_config', multivalue_4_status)

multivalue_4_handle = multivalue_4_status['multivalue_handle']


ethernet_2_status = ixiangpf.interface_config(
        protocol_name                ="Ethernet 2"               ,
        protocol_handle              =deviceGroup_2_handle      ,
        mtu                          ="1500"                      ,
        src_mac_addr                 =multivalue_4_handle       ,
        vlan                         ="0"                          ,
        vlan_id                      ="1"                          ,
        vlan_id_step                 ="0"                          ,
        vlan_id_count                ="1"                          ,
        vlan_tpid                    ="0x8100"                     ,
        vlan_user_priority           ="0"                          ,
        vlan_user_priority_step      ="0"                          ,
        use_vpn_parameters           ="0"                          ,
        site_id                      ="0"                          ,
    )
if ethernet_2_status['status'] != IxiaHlt.SUCCESS:
    ErrorHandler('interface_config', ethernet_2_status)
	
ethernet_2_handle=ethernet_2_status['ethernet_handle']


multivalue_5_status = ixiangpf.multivalue_config(
        pattern                ="counter"                 ,
        counter_start          ="100.1.0.2"               ,
        counter_step           ="0.0.0.1"                 ,
        counter_direction      ="increment"               ,
        nest_step              ="0.1.0.0"                 ,
        nest_owner             =topology_2_handle      ,
        nest_enabled           ="1"                       ,
    )
	
if multivalue_5_status['status'] != IxiaHlt.SUCCESS:
    ErrorHandler('multivalue_config', multivalue_5_status)
	
multivalue_5_handle = multivalue_5_status['multivalue_handle']


multivalue_6_status = ixiangpf.multivalue_config(
        pattern                ="counter"                 ,
        counter_start          ="100.1.0.1"               ,
        counter_step           ="255.255.255.255"         ,
        counter_direction      ="decrement"               ,
        nest_step              ="0.0.0.1"                 ,
        nest_owner             =topology_2_handle      ,
        nest_enabled           ="0"                       ,
    )	
if multivalue_6_status['status'] != IxiaHlt.SUCCESS:
    ErrorHandler('multivalue_config', multivalue_6_status)
	
multivalue_6_handle = multivalue_6_status['multivalue_handle']


ipv4_2_status = ixiangpf.interface_config(
        protocol_name                ="IPv4 2"                  ,
        protocol_handle              =ethernet_2_handle        ,
        ipv4_resolve_gateway         ="1"                         ,
        ipv4_manual_gateway_mac      ="00.00.00.00.00.01"         ,
        gateway                      =multivalue_6_handle      ,
        intf_ip_addr                 =multivalue_5_handle      ,
        netmask                      ="255.255.255.0"             ,
    )
	
if ipv4_2_status['status'] != IxiaHlt.SUCCESS:
    ErrorHandler('interface_config', ipv4_2_status)

ipv4_2_handle = ipv4_2_status['ipv4_handle']



################################################################################
# Configure Topology 3, Device Group 3                                         #
################################################################################

topology_3_status = ixiangpf.topology_config(
        topology_name      ="Topology 3"                          ,
        port_handle        =port_3								  ,
    )	
	
if topology_3_status['status'] != IxiaHlt.SUCCESS:
    ErrorHandler('multivalue_config', topology_3_status)

topology_3_handle = topology_3_status['topology_handle']


device_group_3_status = ixiangpf.topology_config(
        topology_handle              =topology_3_handle      ,
        device_group_name            ="Device Group3"         ,
        device_group_multiplier      ="1"                      ,
        device_group_enabled         ="1"                       ,
    )
	
if device_group_3_status['status'] != IxiaHlt.SUCCESS:
    ErrorHandler('multivalue_config', device_group_3_status)
	
deviceGroup_3_handle = device_group_3_status['device_group_handle']

################################################################################
# Configure protocol interfaces for the third topology                         #
################################################################################

multivalue_7_status = ixiangpf.multivalue_config(
        pattern                ="counter"                 ,
        counter_start          ="00.13.01.00.00.01"       ,
        counter_step           ="00.00.00.00.00.01"       ,
        counter_direction      ="increment"               ,
        nest_step              ="00.00.01.00.00.00"       ,
        nest_owner             =topology_3_handle      ,
        nest_enabled           ="1"                       ,
    )
	
	
if multivalue_7_status['status'] != IxiaHlt.SUCCESS:
    ErrorHandler('multivalue_config', multivalue_7_status)

multivalue_7_handle = multivalue_7_status['multivalue_handle']


ethernet_3_status = ixiangpf.interface_config(
        protocol_name                ="Ethernet 3"               ,
        protocol_handle              =deviceGroup_3_handle      ,
        mtu                          ="1500"                       ,
        src_mac_addr                 =multivalue_7_handle       ,
        src_mac_addr_step            ="00.00.00.00.00.00"          ,
        vlan                         ="0"                          ,
        vlan_id                      ="1"                          ,
        vlan_id_step                 ="0"                          ,
        vlan_id_count                ="1"                          ,
        vlan_tpid                    ="0x8100"                     ,
        vlan_user_priority           ="0"                          ,
        vlan_user_priority_step      ="0"                          ,
        use_vpn_parameters           ="0"                          ,
        site_id                      ="0"                          ,
    )
	
if ethernet_3_status['status'] != IxiaHlt.SUCCESS:
    ErrorHandler('interface_config', ethernet_3_status)
	
ethernet_3_handle = ethernet_3_status ['ethernet_handle']


multivalue_8_status = ixiangpf.multivalue_config (
        pattern                ="counter"                 ,
        counter_start          ="3000:0:0:1:0:0:0:2"      ,
        counter_step           ="0:0:0:1:0:0:0:0"         ,
        counter_direction      ="increment"               ,
        nest_step              ="0:0:0:1:0:0:0:0"         ,
        nest_owner             ="topology_3_handle"      ,
        nest_enabled           ="1"                       ,
    )
	
if multivalue_8_status['status'] != IxiaHlt.SUCCESS:
    ErrorHandler('multivalue_config', multivalue_8_status)

multivalue_8_handle = multivalue_8_status['multivalue_handle']

multivalue_9_status = ixiangpf.multivalue_config(
        pattern                ="counter"                 ,
        counter_start          ="3000:0:1:1:0:0:0:2"      ,
        counter_step           ="0:0:0:1:0:0:0:0"         ,
        counter_direction      ="increment"               ,
        nest_step              ="0:0:0:1:0:0:0:0"         ,
        nest_owner             =topology_3_handle      ,
        nest_enabled           ="1"                       ,
    )
	
if multivalue_9_status['status'] != IxiaHlt.SUCCESS:
    ErrorHandler('multivalue_config', multivalue_9_status)
	
multivalue_9_handle = multivalue_9_status["multivalue_handle"]


ipv6_3_status =ixiangpf.interface_config(
        protocol_name                     ="IPv6 3"                  ,
        protocol_handle                   =ethernet_3_handle        ,
        ipv6_multiplier                   ="1"                         ,
        ipv6_resolve_gateway              ="1"                         ,
        ipv6_manual_gateway_mac           ="00.00.00.00.00.01"         ,
        ipv6_manual_gateway_mac_step      ="00.00.00.00.00.00"         ,
        ipv6_gateway                      =multivalue_9_handle      ,
        ipv6_gateway_step                 ="::0"                       ,
        ipv6_intf_addr                    =multivalue_8_handle      ,
        ipv6_intf_addr_step               ="::0"                       ,
        ipv6_prefix_length                ="64"                        ,
    )	
if ipv6_3_status['status'] != IxiaHlt.SUCCESS:
    ErrorHandler('interface_config', ipv6_3_status)
	
ipv6_3_handle = ipv6_3_status["ipv6_handle"]

################################################################################
# Configure Topology 4, Device Group 4                                         #
################################################################################

topology_4_status = ixiangpf.topology_config(
        topology_name      ="Topology 4"                          ,
        port_handle        =port_4								  ,
    )
	
if topology_4_status['status'] != IxiaHlt.SUCCESS:
    ErrorHandler('multivalue_config', topology_4_status)
	
topology_4_handle = topology_4_status["topology_handle"]


device_group_4_status=ixiangpf.topology_config(
        topology_handle              =topology_4_handle      ,
        device_group_name            ="Device Group4"         ,
        device_group_multiplier      ="1"                      ,
        device_group_enabled         ="1"                       ,
    )
if device_group_4_status['status'] != IxiaHlt.SUCCESS:
    ErrorHandler('multivalue_config', device_group_4_status)
	
deviceGroup_4_handle = device_group_4_status["device_group_handle"]

################################################################################
# Configure protocol interfaces for the fourth topology                        #
################################################################################

multivalue_10_status = ixiangpf.multivalue_config (
        pattern                ="counter"                 ,
        counter_start          ="00.14.01.00.00.01"       ,
        counter_step           ="00.00.00.00.00.01"       ,
        counter_direction      ="increment"               ,
        nest_step              ="00.00.01.00.00.00"       ,
        nest_owner             =topology_4_handle      ,
        nest_enabled           ="1"                       ,
    )

if multivalue_10_status['status'] != IxiaHlt.SUCCESS:
    ErrorHandler('multivalue_config', multivalue_10_status)

multivalue_10_handle = multivalue_10_status ["multivalue_handle"]

ethernet_4_status = ixiangpf.interface_config (
        protocol_name                ="Ethernet 4"               ,
        protocol_handle              =deviceGroup_4_handle      ,
        mtu                          ="1500"                       ,
        src_mac_addr                 =multivalue_10_handle      ,
        src_mac_addr_step            ="00.00.00.00.00.00"          ,
        vlan                         ="0"                          ,
        vlan_id                      ="1"                          ,
        vlan_id_step                 ="0"                          ,
        vlan_id_count                ="1"                          ,
        vlan_tpid                    ="0x8100"                     ,
        vlan_user_priority           ="0"                          ,
        vlan_user_priority_step      ="0"                         ,
        use_vpn_parameters           ="0"                          ,
        site_id                      ="0"                          ,
    )

	
if ethernet_4_status['status'] != IxiaHlt.SUCCESS:
    ErrorHandler('interface_config', ethernet_4_status)

ethernet_4_handle = ethernet_4_status["ethernet_handle"]


multivalue_11_status = ixiangpf.multivalue_config(
        pattern                ="counter"                 ,
        counter_start          ="3000:0:1:1:0:0:0:2"      ,
        counter_step           ="0:0:0:1:0:0:0:0"         ,
        counter_direction      ="increment"               ,
        nest_step              ="0:0:0:1:0:0:0:0"         ,
        nest_owner             =topology_4_handle      ,
        nest_enabled           ="1"                       ,
    )

if multivalue_11_status['status'] != IxiaHlt.SUCCESS:
    ErrorHandler('multivalue_config', multivalue_11_status)

multivalue_11_handle = multivalue_11_status ["multivalue_handle"]


multivalue_12_status=ixiangpf.multivalue_config(
        pattern                ="counter"                 ,
        counter_start          ="3000:0:0:1:0:0:0:2"      ,
        counter_step           ="0:0:0:1:0:0:0:0"         ,
        counter_direction      ="increment"               ,
        nest_step              ="0:0:0:1:0:0:0:0"         ,
        nest_owner             =topology_4_handle      ,
        nest_enabled           ="1"                       ,
    )

if multivalue_12_status['status'] != IxiaHlt.SUCCESS:
    ErrorHandler('multivalue_config', multivalue_12_status)
	
multivalue_12_handle = multivalue_12_status["multivalue_handle"]


ipv6_4_status = ixiangpf.interface_config(
        protocol_name                     ="IPv6 4"                  ,
        protocol_handle                   =ethernet_4_handle        ,
        ipv6_multiplier                   ="1"                         ,
        ipv6_resolve_gateway              ="1"                         ,
        ipv6_manual_gateway_mac           ="00.00.00.00.00.01"         ,
        ipv6_manual_gateway_mac_step      ="00.00.00.00.00.00"         ,
        ipv6_gateway                      =multivalue_12_handle      ,
        ipv6_gateway_step                 ="::0"                       ,
        ipv6_intf_addr                    =multivalue_11_handle      ,
        ipv6_intf_addr_step               ="::0"                       ,
        ipv6_prefix_length                ="64"                        ,
    )
	
if ipv6_4_status['status'] != IxiaHlt.SUCCESS:
    ErrorHandler('interface_config', ipv6_4_status)
	
ipv6_4_handle = ipv6_4_status ["ipv6_handle"]

####################################################
# Start protocols
####################################################
tprint("Startting protocols....")

start = ixiangpf.test_control(action='start_all_protocols')
if start['status'] != IxiaHlt.SUCCESS:
    ErrorHandler('test_control', start)

tprint("After starting protocols, wait for 30 seconds for things to settle before creating traffic items")
time.sleep(30)
tprint("Verify sessions status after protocol is started")
ipv4_proto_info_1 = ixia_protocal_info(ipv4_1_handle)
#tprint('protocol_info', ipv4_proto_info_1)
ipv4_proto_info_1.pop('status') 
if ixia_protocal_status(ipv4_proto_info_1) == "UP":
	tprint("IPv4 protocol session is UP: {}".format(ipv4_proto_info_1.keys()))
elif ixia_protocal_status(ipv4_proto_info_1) == "DOWN":
	tprint("IPv4 protocol session is DOWN: {}, check your test setup!!".format(list(ipv4_proto_info_1.keys())[0]))
	sys.exit()
ipv4_proto_info_2 = ixia_protocal_info(ipv4_2_handle)
#tprint('protocol_info', ipv4_proto_info_1)
ipv4_proto_info_2.pop('status') 
if ixia_protocal_status(ipv4_proto_info_2) == "UP":
	tprint("IPv4 protocol session is UP: {}".format(ipv4_proto_info_2.keys()))
elif ixia_protocal_status(ipv4_proto_info_2) == "DOWN":
	tprint("IPv4 protocol session is DOWN: {}, check your test setup!!".format(list(ipv4_proto_info_2.keys())[0]))
	sys.exit()

# IPv6 stuff, will handle later!!!
# ipv6_proto_info_1 = ixia_protocal_info(ipv6_4_handle)
# tprint('protocol_info', ipv6_proto_info_1)
# ipv6_proto_info_1.pop('status') 
# if ixia_protocal_status(ipv6_proto_info_1) == "UP":
# 	tprint("IPv6 protocol session is UP {}".format(ipv6_proto_info_1.keys()))
# elif ixia_protocal_status(ipv6_proto_info_1) == "DOWN":
# 	tprint("IPv6 protocol session is DOWN: {}".format(ipv6_proto_info_1.keys()))
# exit()
####################################################
##Configure traffic for all configuration elements##
##########################################################
tprint("Creating traffic item I....")

twargs = {}
tkwargs = {
        'mode':'create',
        'endpointset_count':1,
        'src_dest_mesh':'one_to_one',
        'emulation_src_handle': topology_1_handle,
    	'emulation_dst_handle': topology_2_handle,
        'route_mesh':'one_to_one',
        'src_dest_mesh':'one_to_one',
        'bidirectional':0,
        'name':'Traffic_Item_1',
        'circuit_endpoint_type':'ipv4',
        'frame_size':1000,
        'rate_mode':'percent',
        'rate_percent':100,
        'burst_loop_count':1000,
        'inter_burst_gap':100,
        'pkts_per_burst':10000,
        'track_by':'endpoint_pair',
        'l3_protocol':'ipv4'
    }
for key, value in tkwargs.items():
    if re.search('port_handle', key):
        tkwargs[key]='%s/%s' % (1, value)
    else:
        tkwargs[key]=value

 
traffic_config_status = ixiangpf.traffic_config(**tkwargs)

if traffic_config_status['status'] != '1':
    ErrorHandler('traffic_config', traffic_config_status)
else:
    tprint('Create Burst Traffic stream: Done')

tprint("Creating traffic item II....")
twargs = {}
tkwargs = {
        'mode':'create',
        'endpointset_count':1,
        'src_dest_mesh':'one_to_one',
        'emulation_src_handle': topology_2_handle,
    	'emulation_dst_handle': topology_1_handle,
        'route_mesh':'one_to_one',
        'src_dest_mesh':'one_to_one',
        'bidirectional':0,
        'name':'Traffic_Item_2',
        'circuit_endpoint_type':'ipv4',
        'frame_size':1000,
        'rate_mode':'percent',
        'rate_percent':100,
        'burst_loop_count':1000,
        'inter_burst_gap':100,
        'pkts_per_burst':10000,
        'track_by':'endpoint_pair',
        'l3_protocol':'ipv4'
    }
for key, value in tkwargs.items():
    if re.search('port_handle', key):
        tkwargs[key]='%s/%s' % (1, value)
    else:
        tkwargs[key]=value

 
traffic_config_status = ixiangpf.traffic_config(**tkwargs)

if traffic_config_status['status'] != '1':
    ErrorHandler('traffic_config', traffic_config_status)
else:
    tprint('\nCreate Burst Traffic stream: Done')


################################################################################
# Apply And Start traffic                                                                #
################################################################################
tprint("Starting Traffic.....")
kwargs={}
tkwargs = {}
kwargs = {
        'action':'apply',
        'max_wait_timer':120,
    }
for key, value in kwargs.items():
    tkwargs[key]=value
traffic_control_status = ixiangpf.traffic_control(**tkwargs)

if traffic_control_status['status'] != '1':
    ErrorHandler('traffic_control -action apply', traffic_control_status)
else:
    tprint('\nApply traffic to hardward: Done')


tprint("Running traffic for 30 seconds...")
kwargs={}
tkwargs = {}
kwargs = {
        'action':'run',
        'max_wait_timer':120,
    }
for key, value in kwargs.items():
    tkwargs[key]=value
run_traffic = ixiangpf.traffic_control(**tkwargs)

if run_traffic['status'] != IxiaHlt.SUCCESS:
    ErrorHandler('test_control', run_traffic)

time.sleep(30)


################################################################################
# Collect traffic statistics                                                              #
################################################################################

tprint("Collect statistics after running traffic for 30 seconds, make sure no packet loss..")
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
for dut in dut_list:
	relogin_if_needed(dut)


topology_change_428(dut_list)
time.sleep(20)
pre_test_verification(dut_list)
# stat_dir_list = [{'member': 2, 'B1:H1': '2-member LACP trunk', 'B2:F2': 'image name to be filled', 'B3': 'No.', 'C3': 'Action', 'D3:E3': 'Frame Loss', 'F3': 'Loss Time Sec', 'B4': 'Test 1', 'C4': 'un-plug 1st active link', 'D4': 'host1', 'D5': 'host2', 'C7': 'un-plug 2nd active link', 'D7': 'host1', 'D8': 'host2', 'C10': 're-connect 2nd link', 'D10': 'host1', 'D11': 'host2', 'C13': 're-connect 1st active link', 'D13': 'host1', 'D14': 'host2', 'C16': 'Tier-1 DUT1 Down', 'D16': 'host1', 'D17': 'host2', 'C18': 'Tier-1 DUT2 Down', 'D18': 'host1', 'D19': 'host2', 'C21': 'Tier-1 DUT1 Up', 'D21': 'host1', 'D22': 'host2', 'C23': 'Tier-1 DUT2 Up', 'D23': 'host1', 'D24': 'host2', 'C26': 'Tier-2 DUT3 Down', 'D26': 'host1', 'D27': 'host2', 'C28': 'Tier-2 DUT4 Down', 'D28': 'host1', 'D29': 'host2', 'C31': 'Tier-2 DUT3 Up', 'D31': 'host1', 'D32': 'host2', 'C33': 'Tier-2 DUT4 Up', 'D33': 'host1', 'D34': 'host2', 'test': 1, 'sheetname': 'LACP-2 Test1'}, {'member': 2, 'B1:H1': '2-member LACP trunk', 'B2:F2': 'image name to be filled', 'B3': 'No.', 'C3': 'Action', 'D3:E3': 'Frame Loss', 'F3': 'Loss Time Sec', 'B4': 'Test 2', 'C4': 'un-plug 1st active link', 'D4': 'host1', 'D5': 'host2', 'C7': 'un-plug 2nd active link', 'D7': 'host1', 'D8': 'host2', 'C10': 're-connect 2nd link', 'D10': 'host1', 'D11': 'host2', 'C13': 're-connect 1st active link', 'D13': 'host1', 'D14': 'host2', 'C16': 'Tier-1 DUT1 Down', 'D16': 'host1', 'D17': 'host2', 'C18': 'Tier-1 DUT2 Down', 'D18': 'host1', 'D19': 'host2', 'C21': 'Tier-1 DUT1 Up', 'D21': 'host1', 'D22': 'host2', 'C23': 'Tier-1 DUT2 Up', 'D23': 'host1', 'D24': 'host2', 'C26': 'Tier-2 DUT3 Down', 'D26': 'host1', 'D27': 'host2', 'C28': 'Tier-2 DUT4 Down', 'D28': 'host1', 'D29': 'host2', 'C31': 'Tier-2 DUT3 Up', 'D31': 'host1', 'D32': 'host2', 'C33': 'Tier-2 DUT4 Up', 'D33': 'host1', 'D34': 'host2', 'sheetname': 'LACP-2 Test2', 'test': 2}, {'member': 8, 'B1:H1': '2-member LACP trunk', 'B2:F2': 'image name to be filled', 'B3': 'No.', 'C3': 'Action', 'D3:E3': 'Frame Loss', 'F3': 'Loss Time Sec', 'B4': 'Test 1', 'C4': 'un-plug 1st active link', 'D4': 'host1', 'D5': 'host2', 'C7': 'un-plug 3~4 active link', 'D7': 'host1', 'D8': 'host2', 'C10': 're-connect 3~4 link', 'D10': 'host1', 'D11': 'host2', 'C13': 're-connect 1st active link', 'D13': 'host1', 'D14': 'host2', 'C16': 'Tier-1 DUT1 Down', 'D16': 'host1', 'D17': 'host2', 'C18': 'Tier-1 DUT2 Down', 'D18': 'host1', 'D19': 'host2', 'C21': 'Tier-1 DUT1 Up', 'D21': 'host1', 'D22': 'host2', 'C23': 'Tier-1 DUT2 Up', 'D23': 'host1', 'D24': 'host2', 'C26': 'Tier-2 DUT3 Down', 'D26': 'host1', 'D27': 'host2', 'C28': 'Tier-2 DUT4 Down', 'D28': 'host1', 'D29': 'host2', 'C31': 'Tier-2 DUT3 Up', 'D31': 'host1', 'D32': 'host2', 'C33': 'Tier-2 DUT4 Up', 'D33': 'host1', 'D34': 'host2', 'sheetname': 'LACP-8 Test1', 'test': 1, 'E22': 9, 'F22': '7.344001175040188e-05 seconds', 'E21': 8, 'F21': '6.528001044480167e-05 seconds'}, {'member': 8, 'B1:H1': '2-member LACP trunk', 'B2:F2': 'image name to be filled', 'B3': 'No.', 'C3': 'Action', 'D3:E3': 'Frame Loss', 'F3': 'Loss Time Sec', 'B4': 'Test 2', 'C4': 'un-plug 1st active link', 'D4': 'host1', 'D5': 'host2', 'C7': 'un-plug 3~4 active link', 'D7': 'host1', 'D8': 'host2', 'C10': 're-connect 3~4 link', 'D10': 'host1', 'D11': 'host2', 'C13': 're-connect 1st active link', 'D13': 'host1', 'D14': 'host2', 'C16': 'Tier-1 DUT1 Down', 'D16': 'host1', 'D17': 'host2', 'C18': 'Tier-1 DUT2 Down', 'D18': 'host1', 'D19': 'host2', 'C21': 'Tier-1 DUT1 Up', 'D21': 'host1', 'D22': 'host2', 'C23': 'Tier-1 DUT2 Up', 'D23': 'host1', 'D24': 'host2', 'C26': 'Tier-2 DUT3 Down', 'D26': 'host1', 'D27': 'host2', 'C28': 'Tier-2 DUT4 Down', 'D28': 'host1', 'D29': 'host2', 'C31': 'Tier-2 DUT3 Up', 'D31': 'host1', 'D32': 'host2', 'C33': 'Tier-2 DUT4 Up', 'D33': 'host1', 'D34': 'host2', 'sheetname': 'LACP-8 Test2', 'test': 2, 'E22': 8, 'F22': '6.528001044480167e-05 seconds', 'E21': 8, 'F21': '6.528001044480167e-05 seconds'}]

# filename = "LACP_Perf.xlsx"
# dict_2_excel(stat_dir_list,filename)
# exit()

tprint("===================================== DUT_1 Reboot MALAG PERFORMANCE Test:8-Member =======================")
reboot_result = dut_reboot_test_new(dut1,dut="dut1",mem=8)
print("!!!!!! debug: print reboot_result after reboot test")
print(reboot_result)
dict_lacp_boot_update(dir_list=stat_dir_list,dut_name="dut1",mem=8,result=reboot_result)
print("!!!!! print stat dir list after updating the stats dictionary")
print(stat_dir_list)
 
tprint("===================================== DUT_2 Reboot MALAG PERFORMANCE Test:8-Member =======================")
reboot_result = dut_reboot_test_new(dut2,dut="dut2",mem=8)
dict_lacp_boot_update(dir_list=stat_dir_list,dut_name="dut2",mem=8,result=reboot_result)
print(stat_dir_list)

tprint("===================================== DUT_3 Reboot MALAG PERFORMANCE Test:8-Member =======================")
reboot_result = dut_reboot_test_new(dut3,dut="dut3",mem=8)
dict_lacp_boot_update(dir_list=stat_dir_list,dut_name="dut3",mem=8,result=reboot_result)
print(stat_dir_list)

tprint("===================================== DUT_4 Reboot MALAG PERFORMANCE Tes:8-Membert =======================")
reboot_result = dut_reboot_test_new(dut4,dut="dut4",mem=8)
dict_lacp_boot_update(dir_list=stat_dir_list,dut_name="dut4",mem=8,result=reboot_result)
print(stat_dir_list)




for dut in dut_list:
	relogin_if_needed(dut)
fiber_result = dut_fibercut_test(dut2,tier = 1, mem=8, mode="auto",dut_name="dut2")
dict_lacp_boot_update(dir_list=stat_dir_list,dut_name="dut2",mem=8,result=fiber_result)
print(stat_dir_list)
fiber_result = dut_fibercut_test(dut4,tier = 2, mem=8, mode="auto",dut_name="dut4")
dict_lacp_boot_update(dir_list=stat_dir_list,dut_name="dut4",mem=8,result=fiber_result)
print(stat_dir_list)
# old ---dut_shut_test_mclag_8(dut2,dut4)

topology_change_824(dut_list)
pre_test_verification(dut_list)

tprint("===================================== DUT_1 Reboot MALAG PERFORMANCE Test:2-Member =======================")
reboot_result = dut_reboot_test_new(dut1,dut="dut1",mem=2)
print("!!!!!! debug: print reboot_result after reboot test")
print(reboot_result)
dict_lacp_boot_update(dir_list=stat_dir_list,dut_name="dut1",mem=2,result=reboot_result)
print("!!!!! print stat dir list after updating the stats dictionary")
print(stat_dir_list)
 
tprint("===================================== DUT_2 Reboot MALAG PERFORMANCE Test:2-Member =======================")
reboot_result = dut_reboot_test_new(dut2,dut="dut2",mem=2)
dict_lacp_boot_update(dir_list=stat_dir_list,dut_name="dut2",mem=2,result=reboot_result)
print(stat_dir_list)

tprint("===================================== DUT_3 Reboot MALAG PERFORMANCE Test:2-Member =======================")
reboot_result = dut_reboot_test_new(dut3,dut="dut3",mem=2)
dict_lacp_boot_update(dir_list=stat_dir_list,dut_name="dut3",mem=2,result=reboot_result)
print(stat_dir_list)

tprint("===================================== DUT_4 Reboot MALAG PERFORMANCE Tes:2-Membert =======================")
reboot_result = dut_reboot_test_new(dut4,dut="dut4",mem=2)
dict_lacp_boot_update(dir_list=stat_dir_list,dut_name="dut4",mem=2,result=reboot_result)
print(stat_dir_list)

fiber_result = dut_fibercut_test(dut2,tier = 1, mem=2, mode="auto",dut_name="dut2")
dict_lacp_boot_update(dir_list=stat_dir_list,dut_name="dut2",mem=2,result=fiber_result)
print(stat_dir_list)
fiber_result = dut_fibercut_test(dut4,tier = 2, mem=2, mode="auto",dut_name="dut4")
dict_lacp_boot_update(dir_list=stat_dir_list,dut_name="dut4",mem=2,result=fiber_result)
print(stat_dir_list)


filename = "LACP_Perf.xlsx"
dict_2_excel(stat_dir_list,filename)
exit()

tprint(" ===================================== MCLAG Port-Down Performance Test:4-Member ========================= ")

for dut in dut_list:
	relogin_if_needed(dut)
	 
dut_shut_test_mclag_4(dut2,dut4)
dut_list = []
for dut in dut_list:
	relogin_if_needed(dut1)

# topology_change_428(dut_list)
# pre_test_verification(dut_list)
#dut_unplug_test_mclag_4(dut2,dut4)

####################################################
# Stop traffic
####################################################
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
 

####################################################
# Test END
####################################################

print("###################")
tprint("Test run is PASSED")
print("###################")


##################################################################################################################################################
##################################################################################################################################################