
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
import settings 
from test_process import * 
from common_lib import *
from common_codes import *
from cli_functions import *
from device_config import *
from protocols_class import *
from ixia_restpy_lib import *

#from clear_console import *
#init()
################################################################################
# Connection to the chassis, IxNetwork Tcl Server                 			   #
################################################################################


sys.stdout = Logger("Log/bgp_testing.log")

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--guide", help="print out simple user manual", action="store_true")
parser.add_argument("-c", "--config", help="Configure switches before starting testing", action="store_true")
#parser.add_argument("-a", "--auto", help="Run in fully automated mode without manually unplugging cables", action="store_true")
parser.add_argument("-u", "--fibercut", help="Run in manual mode when unplugging cables", action="store_true")
parser.add_argument("-t", "--testbed", type=str, help="Specific which testbed to run this test. Valid options:\
					1)548D 2)448D 3)FG-548D 4)FG-448D")
parser.add_argument("-file", "--file", type=str, help="Specific file name appendix when exporting to excel. Example:mac-1k. Default=none")
parser.add_argument("-x", "--ixia", type=str, help="ixia port setup: default=static,option1 = dhcp")
parser.add_argument("-n", "--run_time", type=int, help="Specific how many times you want to run the test, default=2")
parser.add_argument("-test", "--testcase", type=int, help="Specific which test case you want to run. Example: 1/1-3/1,3,4,7 etc")
parser.add_argument("-mac", "--mac", type=str, help="Background MAC entries learning,defaul size=1000")
parser.add_argument("-d", "--dev", help="IXIA Development mode,do not verify any network status", action="store_true")
parser.add_argument("-b", "--boot", help="Perform reboot test", action="store_true")
parser.add_argument("-f", "--factory", help="Run the test after factory resetting all devices", action="store_true")
parser.add_argument("-v", "--verbose", help="Run the test in verbose mode with amble debugs info", action="store_true")
parser.add_argument("-s", "--setup_only", help="Setup testbed and IXIA only for manual testing", action="store_true")
parser.add_argument("-nf", "--no_fortigate", help="No Fortigate: convert FSW from managed mode to standalone mode ", action="store_true")
parser.add_argument("-lm", "--log_mac", help="enable port mac log event", action="store_true")
parser.add_argument("-i", "--interactive", help="Enter interactive mode for test parameters", action="store_true")
parser.add_argument("-e", "--config_host_sw", help="Configure host switches connected to ixia when changing testbed", action="store_true")
parser.add_argument("-y", "--clean_up", help="Clean up IXIA after test is done. Default = No", action="store_true")
parser.add_argument("-sw", "--upgrade", type = int,help="FSW software upgrade via FGT,image build number at settings.py, example: 193")
parser.add_argument("-ug", "--sa_upgrade", type = int,help="FSW software upgrade in standlone mode. For debug image enter -1. Example: 193,-1(debug image)")




global DEBUG
# if len(sys.argv) > 1:
#     #parser.print_help()
args = parser.parse_args()
if args.guide:
	guide = """
=============================================== Simple User manual ===============================================
1)For first time to connect all FSW to FGTs, the following is an sample command:
python mclag_v2.py -t FG-548D -e -f
-e: configure host-sw
-t: FGT and 548D connect together
-f: Execute factory reset

2)For first time converting managed FSW to standalone without doing any testing, the followng sample command:
python mclag_v2.py -t 548D -e -nf -c
-nf: No Fortigate.  This will configure related host switches, and then do a factory reset
-c: configure all the FSW using the standalone switch's config files
-e: configure host-sw 

3)For running fiber-cut and reboot performance test on standalone switches setup, use the following command:
python mclag_v2.py -t 548D -e -test 2 -n 1 -b
-test : Test case #
-n: How many times you want to run the test
-b: perform reboot test 
-e: configure host-sw

4)For running fiber-cut performance test on standalone switches setup, use the following command:
python mclag_v2.py -t 548D -e -test 2 -n 1 
-test : Test case #2 is for 2-tier mclag perf test
-n: How many times you want to run the test
-e: configure host-sw

5)For running process CPU utilization test, use the following command:
python mclag_v2.py -t 448D -mac 1000-10000-1000 -e -test 1 -lm
-test : Test case #1 is for process cpu test
-lm: enable log-mac-event
-e: configure host-sw
-mac: iterate starting from mac-table sie 1k to 10k, increment 1k each time
"""
	print(guide)
	exit()
if args.sa_upgrade:
	upgrade_sa = True
	sw_build = args.sa_upgrade
	tprint(f"**Upgrade FSW software in standalone mode to build {sw_build}")
else:
	upgrade_sa = False
if args.upgrade:
	upgrade_fgt = True
	sw_build = args.upgrade
	tprint(f"**Upgrade FSW software via via Fortigate to build {sw_build}")
else:
	upgrade_fgt = False
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
	tprint("** Running test with port log-mac-event disable")
	log_mac_event = False
if args.factory:
	factory = True
	tprint("** Will factory reset each FSW ")
else:
	factory = False
	tprint("** Will NOT factory reset each FSW")
if args.fibercut:
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
	test_all = False
	tprint("** Test Case To Run: #{}".format(testcase))
else:
	test_all = True
	testcase = 0
	tprint("** All Test Case To Be Run:{}".format(test_all))
if args.mac:
	mac_input = args.mac
	if "-" in mac_input:
		low,high,step = mac_input.split('-')
		low,high,step = int(low),int(high),int(step)
		mac_list = [i for i in range(low,high+1,step)]
	else:

		mac_list = re.split('\\s+|,\\s+|,|\n',str(mac_input))
		for i in range(len(mac_list)):
			mac_list[i] = int(mac_list[i])
	print(f"For test #1, MAC table size = {mac_list}")
	tprint("** Test under background MAC address learning,size = {}".format(mac_list))
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
if args.clean_up:
	clean_up = True
else:
	clean_up = False

print(settings.ONBOARD_MSG)
#If in code development mode, skipping loging into switches 
tprint("============================== Pre-test setup and configuration ===================")

testbed_description = """
TBD
"""
print(testbed_description)


dut_dir_list = bgp_testbed_init()
if factory == True:
	for dut_dir in dut_dir_list:
		switch_factory_reset_nologin(dut_dir)

	console_timer(200,msg="Wait for 200s after reset factory default all switches")
	tprint('-------------------- re-login Fortigate devices after factory rest-----------------------')
	for dut_dir in dut_dir_list:
		dut_com = dut_dir['comm'] 
		dut_port = dut_dir['comm_port']
		dut = get_switch_telnet_connection_new(dut_com,dut_port)
		dut_dir['telnet'] = dut
if setup: 
	for dut_dir in dut_dir_list:
		dut = dut_dir['telnet']
		dut_name = dut_dir['name']
		image = find_dut_image(dut)
		tprint(f"============================ {dut_name} software image = {image}")
		sw_init_config(device=dut_dir)

	console_timer(30,msg="After intial configuration, show switch related information")
	switches = [FortiSwitch(dut_dir) for dut_dir in dut_dir_list]
	for switch in switches:
			switch.router_ospf.show_ospf_neighbors()
			switch.router_bgp.show_bgp_summary()
		# Develop new codes starts from here
		# stop_threads = False
		# dut_cpu_memory(dut_dir_list,lambda: stop_threads)

if upgrade_sa:
	for dut_dir in dut_dir_list:
		result = fsw_upgrade(build=sw_build,dut_dict=dut_dir)
		if not result:
			tprint(f"############# Upgrade {dut_dir['name']} to build #{sw_build} Fails ########### ")
		else:
			tprint(f"############# Upgrade {dut_dir['name']} to build #{sw_build} is successful ############")

	console_timer(400,msg="Wait for 400s after started upgrading all switches")
	for dut_dir in dut_dir_list:
		dut = dut_dir['telnet']
		dut_name = dut_dir['name']
		try:
			relogin_if_needed(dut)
		except Exception as e:
			debug("something is wrong with rlogin_if_needed at bgp, try again")
			relogin_if_needed(dut)
		image = find_dut_image(dut)
		tprint(f"============================ {dut_name} software image = {image} ============")

switches = [FortiSwitch(dut_dir) for dut_dir in dut_dir_list]
if testcase == 1 or test_all:
	testcase = 1
	description = "Test iBGP via loopbacks"
	print_test_subject(testcase,description)
	switches_clean_up(switches)

	for switch in switches:
		switch.show_switch_info()
		switch.router_ospf.basic_config()
	console_timer(20,msg="After configuring ospf, wait for 20 sec")

	for switch in switches:
		switch.router_ospf.neighbor_discovery()
		switch.router_bgp.update_ospf_neighbors()
		switch.router_bgp.config_ibgp_mesh_loopback()

	console_timer(30,msg="After configuring iBGP sessions via loopbacks, wait for 30s")
	for switch in switches:
		switch.router_ospf.show_ospf_neighbors()
		switch.router_bgp.show_bgp_summary()

	for switch in switches:
		switch.router_bgp.config_ibgp_loopback_bfd('enable')

	console_timer(20,msg="After configuring iBGP sessions via loopbacks, wait for 20s")
	for switch in switches:
		switch.router_ospf.show_ospf_neighbors()
		switch.router_bgp.show_bgp_summary()

	for switch in switches:
		switch.router_bgp.config_ibgp_loopback_bfd('disable')

	console_timer(20,msg="After configuring iBGP sessions via loopbacks, wait for 20s")
	for switch in switches:
		switch.show_routing()

	check_bgp_test_result(testcase,description,switches)

if testcase == 2 or test_all:
	testcase = 2
	description = "iBGP SVI interface"
	print_test_subject(testcase,description)
	switches_clean_up(switches)
	for switch in switches:
		switch.show_switch_info()
		switch.router_ospf.basic_config()

	console_timer(20,msg="After configuring basic OSPF, wait for 20s")
	for switch in switches:
		switch.router_ospf.neighbor_discovery()
		switch.router_bgp.config_ibgp_mesh_direct()

	console_timer(60,msg="After configuring iBGP sessions, wait for 60s")
	for switch in switches:
		switch.show_routing()

	check_bgp_test_result(testcase,description,switches)
if testcase == 3 or test_all:
	testcase = 3
	description = "BGP Redistribute connected"
	print_test_subject(testcase,description)
	switches_clean_up(switches)

	for switch in switches:
		switch.show_switch_info()
		switch.router_ospf.basic_config()

	for switch in switches:
		switch.config_sys_interface(10)
	

	for switch in switches:
		switch.router_bgp.config_ibgp_mesh_loopback()

	console_timer(20,msg="After configuring iBGP sessions, wait for 20s")
	for switch in switches:
		switch.router_bgp.show_bgp_summary()
		switch.router_bgp.config_redistribute_connected()

	console_timer(10,meg="After redistributing connected into BGP, wait for 10 sec")

	for switch in switches:
		switch.show_routing()
	check_bgp_test_result(testcase,description,switches)

if testcase == 4 or test_all:
	testcase = 4
	description = "BGP Redistribute static"
	print_test_subject(testcase,description)
	switches_clean_up(switches)
	for switch in switches:
		switch.show_switch_info()
		switch.router_ospf.basic_config()

	for switch in switches:
		switch.config_static_routes(10)

	console_timer(10,msg="After configuring static routes, wait for 10 sec")

	for switch in switches:
		switch.router_bgp.config_redistribute_static()

	console_timer(10,msg="After redistributing static routes into BGP, wait for 10 sec")
	for switch in switches:
		switch.show_routing()

	check_bgp_test_result(testcase,description,switches)

if testcase == 5 or test_all:
	testcase = 5
	description = "iBGP via second interface" 
	print_test_subject(testcase,description)
	switches_clean_up(switches)
	
	for switch in switches:
		switch.router_ospf.change_router_id(switch.vlan1_2nd)
		switch.router_ospf.disable_redistributed_connected()
		switch.router_ospf.delete_network_entries()
		switch.router_ospf.add_network_entries([switch.vlan1_2nd,switch.vlan1_subnet],['255.255.255.255',switch.vlan1_mask])
		switch.router_ospf.enable_redistributed_connected()
	console_timer(10,msg="After changing ospf configuration, wait for 10 sec")
	for switch in switches:
		switch.show_switch_info()
		switch.router_ospf.update_neighbors()
		switch.router_bgp.update_ospf_neighbors()
		switch.router_ospf.show_ospf_neighbors()
		switch.router_bgp.config_ibgp_mesh_loopback()

	console_timer(60,msg="After configuring iBGP sessions, wait for 60s")
	for switch in switches:
		switch.show_routing()

	check_bgp_test_result(testcase,description,switches)

if testcase == 6 or test_all:
	testcase = 6
	description = "eBGP connection"
	print_test_subject(testcase,description)
	switches_clean_up(switches)
	for switch in switches:
		switch.vlan_neighors(switches)
		switch.show_vlan_neighbors()
		switch.router_bgp.config_ebgp_mesh_direct()
	console_timer(60,msg="After configuring eBGP sessions, wait for 60s")
	for switch in switches:
		switch.show_routing()

if testcase == 7 or test_all:
	testcase = 7
	description = "Redistrubuting ospf into BGP"
	print_test_subject(testcase,description)
	switches_clean_up(switches)
	
	# for switch in switches:
	# 	switch.vlan_neighors(switches)
	# 	switch.show_vlan_neighbors()
	# 	switch.router_bgp.config_ebgp_mesh_direct()
	# console_timer(60,msg="After configuring eBGP sessions, wait for 60s")
	# for switch in switches:	
	# 	switch.router_bgp.show_bgp_summary()

	for switch in switches:
		switch.config_sys_interface(10)
		switch.router_ospf.announce_loopbacks(10)
		switch.router_bgp.config_redistribute_ospf("enable")
	console_timer(10,msg="After announcing loopbacks to BGP, wait for 10s")
	for switch in switches:
		switch.show_routing()
	check_bgp_test_result(testcase,description,switches)

if testcase == 8 or test_all:
	testcase = 8
	description = "BGP BFD neighbor"
	print_test_subject(testcase,description)
	switches_clean_up(switches)
	 
	for switch in switches:
		switch.show_switch_info()
		switch.router_ospf.basic_config()
	console_timer(20,msg="After configuring ospf, wait for 20 sec")

	for switch in switches:
		switch.router_ospf.neighbor_discovery()
		switch.router_bgp.update_ospf_neighbors()
		switch.router_bgp.config_ibgp_mesh_loopback()

	console_timer(30,msg="After configuring iBGP sessions via loopbacks, wait for 30s")
	for switch in switches:
		switch.router_ospf.show_protocol_states()
		switch.router_bgp.show_protocol_states()

	for switch in switches:
		switch.router_bgp.config_ibgp_loopback_bfd('enable')

	console_timer(20,msg="After enabling BFD over iBGP sessions, wait for 20s")
	for switch in switches:
		switch.router_ospf.show_protocol_states()
		switch.router_bgp.show_protocol_states()

	for switch in switches:
		switch.router_bgp.config_ibgp_loopback_bfd('disable')

	console_timer(20,msg="After disabling BFD over iBGP sessions, wait for 20s")
	for switch in switches:
		switch.show_routing()
	check_bgp_test_result(testcase,description,switches)

if testcase == 9 or test_all:
	description = "eBGP with traffic"
	print_test_subject(testcase,description)

	switches_clean_up(switches)

	for switch in switches:
		switch.show_switch_info()
		switch.router_ospf.basic_config()
	console_timer(20,msg="After configuring ospf, wait for 20 sec")

	for switch in switches:
		switch.router_ospf.neighbor_discovery()
		switch.router_bgp.update_ospf_neighbors()
		switch.router_bgp.config_ibgp_mesh_loopback()

	console_timer(30,msg="After configuring iBGP sessions via loopbacks, wait for 30s")
	for switch in switches:
		switch.router_ospf.show_ospf_neighbors()
		switch.router_bgp.show_bgp_summary()
		
	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	portList = [[ixChassisIpList[0], 1,1,"00:11:01:01:01:01","10.10.1.1"], [ixChassisIpList[0], 1, 2,"00:12:01:01:01:01","10.20.1.1"],\
	[ixChassisIpList[0], 1, 3,"00:13:01:01:01:01","10.30.1.1"],[ixChassisIpList[0], 1, 4,"00:14:01:01:01:01","10.40.1.1"], \
	[ixChassisIpList[0], 1, 5,"00:15:01:01:01:01","10.50.1.1"],[ixChassisIpList[0], 1, 6,"00:16:01:01:01:01","10.60.1.1"]]
	myixia = IXIA(apiServerIp,ixChassisIpList,portList)
	myixia.topologies[0].add_ipv4(ip='10.1.1.101',gw='10.1.1.1',mask=24)
	myixia.topologies[1].add_ipv4(ip='10.1.1.102',gw='10.1.1.1',mask=24)
	#myixia.topologies[2].add_ipv4(ip='10.1.1.103',gw='10.1.1.1',mask=24)
	myixia.topologies[3].add_ipv4(ip='10.1.1.104',gw='10.1.1.1',mask=24)
	myixia.topologies[4].add_ipv4(ip='10.1.1.105',gw='10.1.1.1',mask=24)
	myixia.topologies[5].add_ipv4(ip='10.1.1.106',gw='10.1.1.1',mask=24)

	myixia.topologies[0].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=100)
	myixia.topologies[1].add_bgp(dut_ip='10.1.1.2',bgp_type='external',num=100)

	myixia.start_protocol(wait=40)

	myixia.create_traffic(src_topo=myixia.topologies[0].topology, dst_topo=myixia.topologies[1].topology,traffic_name="topo1_2_topo2",tracking_name="Tracking_1")
	myixia.create_traffic(src_topo=myixia.topologies[1].topology, dst_topo=myixia.topologies[0].topology,traffic_name="topo2_2_topo1",tracking_name="Tracking_2")

	myixia.start_traffic()
	myixia.collect_stats()
	myixia.check_traffic()

	check_bgp_test_result(testcase,description,switches)

	# result = "Passed"
	# for switch in switches:
	# 	#switch.router_bgp.get_neighbors_summary()
	# 	if not switch.router_bgp.check_neighbor_status():
	# 		result = "Failed"
	# tprint(f"====================== Test case {testcase} is {result} ==========")		 

print("###################")
tprint("Test run is PASSED")
print("###################")


##################################################################################################################################################
##################################################################################################################################################
