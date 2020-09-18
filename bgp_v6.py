
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

from utils import *
import settings 
from test_process import * 
from common_lib import *
from common_codes import *
from cli_functions import *
from device_config import *
from protocols_class import *
from ixia_restpy_lib_v2 import *

#from clear_console import *
#init()
################################################################################
# Connection to the chassis, IxNetwork Tcl Server                 			   #
################################################################################

CLEAN_ALL = False
CLEAN_BGP = False
CONFIG_BGP = False
OSPF_NEIGHBORS = 6

#sys.stdout = Logger("Log/bgp_testing.log")

parser = argparse.ArgumentParser()
parser.add_argument("-r", "--restore", help="restore config file from tftp server", action="store_true")
parser.add_argument("-m", "--guide", help="print out simple user manual", action="store_true")
parser.add_argument("-c", "--config", help="Configure switches before starting testing", action="store_true")
parser.add_argument("-tc", "--test_config", help="For each test case,configure switches before starting testing", action="store_true")
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
if args.restore:
	restore_config = True
	tprint(" **Restore config from tftp server")
else:
	restore_config = False

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
if args.test_config:
	test_config = True
	CLEAN_BGP = True
	tprint(" !!!!!!!!!!!!!!!!!!!!!!!! All BGP Config Will Be Cleared  !!!!!!!!!!!!!!!!!!!!")
	tprint("** Before starting each test case, configure devices based on each test case scenario")
else:
	test_config = False 
	CLEAN_BGP = False  
	 
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

def test_clean_config(*args,**kwargs):
	switches = kwargs["switches"]
	if CLEAN_ALL:
		switches_clean_up(switches)
	elif CLEAN_BGP:
		for switch in switches:
			switch.router_bgp.clear_config_all()
	else:
		pass

def test_config_igp_ipv6(*args,**kwargs):
	ospf_config_v4 = False
	ospf_config_v6 = False
	#Config OSPF infra
	for switch in switches:
		switch.show_switch_info()
		switch.router_ospf.neighbor_discovery_all()
		switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)
		if not switch.router_ospf.ospf_neighbor_all_up_v4(num=OSPF_NEIGHBORS):
			switch.router_ospf.basic_config()
			ospf_config_v4 = True
		else:
			Info(f"All OSPFv4 neighbors are up on switch {switch.loop0_ip}, No need to config OSPF ")
		if not switch.router_ospf.ospf_neighbor_all_up_v6(num=OSPF_NEIGHBORS):
			switch.router_ospf.basic_config_v6()
			ospf_config_v6 = True
		else:
			Info(f"All OSPFv6 neighbors are up on switch {switch.loop0_ip}, No need to config OSPF ")
	if ospf_config_v4 or ospf_config_v6:
		console_timer(20,msg="After building ospfv4 and ospf6 routing infra, wait for 20 sec")

	#update IPv4 and IPv6 ospf neighbors after configuring ospf 
	Info("=============== Updating OSPF Config and Neighbor Information ==========")
	for switch in switches:
		switch.router_ospf.show_ospf_neighbors_all()
		print("----------Discovering ospf neighbor ---------")
		switch.router_ospf.neighbor_discovery_all()
		print("----------Updating ospf neighbor database  ---------")
		switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)


# this procedure includes basic ibgp v6 mesh configuration among switches


def test_config_switch2ixia_ipv4(*args,**kwargs):
	switches = kwargs['switches']
	portList_v4_v6 = kwargs['ixia_ports']
	ixia_ipv6_as_list = kwargs['as_lists']
	for switch in switches:  
		switch.router_bgp.config_ibgp_mesh_loopback_v6()
		switch.router_bgp.config_ibgp_mesh_loopback()

	console_timer(30,msg="After configuring iBGPv6 sessions via loopbacks, wait for 30s")	 

	for switch in switches:
		switch.router_ospf.show_ospf_neighbors()
		switch.router_ospf.show_ospf_neighbors_v6()
		switch.router_bgp.show_bgp_summary()
		switch.router_bgp.show_bgp_summary_v6()
	
	for switch,ixia_port_info,ixia_as in zip(switches,portList_v4_v6,ixia_ipv6_as_list):
		if switch.router_bgp.config_ebgp_ixia(portList_v4_v6) == False:
			tprint("================= !!!!! FSW Not able to configure IXIA eBGP v4 peers ==============")
			exit()


def test_config_switch2ixia_ipv6(*args,**kwargs):
	switches = kwargs['switches']
	portList_v4_v6 = kwargs['ixia_ports']
	ixia_ipv6_as_list = kwargs['as_lists']
	for switch in switches:  
		switch.router_bgp.config_ibgp_mesh_loopback_v6()
		switch.router_bgp.config_ibgp_mesh_loopback()

	console_timer(30,msg="After configuring iBGPv6 sessions via loopbacks, wait for 30s")	 

	for switch in switches:
		switch.router_ospf.show_ospf_neighbors()
		switch.router_ospf.show_ospf_neighbors_v6()
		switch.router_bgp.show_bgp_summary()
		switch.router_bgp.show_bgp_summary_v6()
	
	for switch,ixia_port_info,ixia_as in zip(switches,portList_v4_v6,ixia_ipv6_as_list):
		if switch.router_bgp.config_ebgp_ixia_v6(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
			tprint("================= !!!!! FSW Not able to configure IXIA eBGP v6 peers ==============")
			exit()
		if switch.router_bgp.config_ebgp_ixia(portList_v4_v6) == False:
			tprint("================= !!!!! FSW Not able to configure IXIA eBGP v4 peers ==============")
			exit()

def test_config_switch2ixia_all(*args,**kwargs):
	switches = kwargs['switches']
	portList_v4_v6 = kwargs['ixia_ports']
	ixia_ipv6_as_list = kwargs['as_lists']
	for switch in switches:  
		switch.router_bgp.config_ibgp_mesh_loopback_v6()
		switch.router_bgp.config_ibgp_mesh_loopback()

	console_timer(30,msg="After configuring iBGPv6 sessions via loopbacks, wait for 30s")	 

	for switch in switches:
		switch.router_ospf.show_ospf_neighbors()
		switch.router_ospf.show_ospf_neighbors_v6()
		switch.router_bgp.show_bgp_summary()
		switch.router_bgp.show_bgp_summary_v6()
	
	for switch,ixia_port_info,ixia_as in zip(switches,portList_v4_v6,ixia_ipv6_as_list):
		if switch.router_bgp.config_ebgp_ixia_v6(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
			tprint("================= !!!!! FSW Not able to configure IXIA eBGP v6 peers ==============")
			exit()
		if switch.router_bgp.config_ebgp_ixia_v4(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
			tprint("================= !!!!! FSW Not able to configure IXIA eBGP v4 peers ==============")
			exit()

def test_config_single_switch2ixia_all(*args,**kwargs):
	dut_switch = kwargs['switch']
	portList_v4_v6 = kwargs['ixia_ports']
	ixia_ipv6_as_list = kwargs['as_lists']
	if "protocol" in kwargs:
		protocol = kwargs["protocol"]
	else:
		protocol = "ebgp"
	# for switch in switches:  
	# 	switch.router_bgp.config_ibgp_mesh_loopback_v6()
	# 	switch.router_bgp.config_ibgp_mesh_loopback()

	console_timer(30,msg="After configuring iBGPv6 sessions via loopbacks, wait for 30s")	 

	# for switch in switches:
	# 	switch.router_ospf.show_ospf_neighbors()
	# 	switch.router_ospf.show_ospf_neighbors_v6()
	# 	switch.router_bgp.show_bgp_summary()
	# 	switch.router_bgp.show_bgp_summary_v6()
	
	for ixia_port_info,ixia_as in zip(portList_v4_v6,ixia_ipv6_as_list):
		if protocol == "ebgp":
			if dut_switch.router_bgp.config_ebgp_ixia_v6(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
				tprint("================= !!!!! FSW Not able to configure IXIA eBGP v6 peers ==============")
				exit()
			if dut_switch.router_bgp.config_ebgp_ixia_v4(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
				tprint("================= !!!!! FSW Not able to configure IXIA eBGP v4 peers ==============")
				exit()
		elif protocol == "ibgp":
			if dut_switch.router_bgp.config_ibgp_ixia_v6(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
				tprint("================= !!!!! FSW Not able to configure IXIA eBGP v6 peers ==============")
				exit()
			if dut_switch.router_bgp.config_ibgp_ixia_v4(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
				tprint("================= !!!!! FSW Not able to configure IXIA eBGP v4 peers ==============")
				exit()

def test_config_ixia_bgp_v4(myixia,ipv4_networks,switches,ixia_bgp_as_list):
	for topo in myixia.topologies:
		topo.add_ipv4()

	for topo,net,ixia_bgp_as in zip(myixia.topologies,ipv4_networks,ixia_bgp_as_list):
		topo.bgpv4_network = net
		topo.bgp_as = ixia_bgp_as	 
	i = 0
	for topo in myixia.topologies:
		topo.add_bgp(dut_ip=switches[i],bgp_type='external',num=10)
		i += 1

def test_config_ixia_bgp_v6(myixia,ipv6_networks,switches,ixia_bgp_as_list):
	for topo in myixia.topologies:
		topo.add_ipv6()

	for topo,net,ixia_bgp_as in zip(myixia.topologies,ipv6_networks,ixia_bgp_as_list):
		topo.bgpv6_network = net
		topo.bgp_as = ixia_bgp_as	 
	i = 0
	for topo in myixia.topologies:
		topo.add_bgp_v6(dut_ip=switches[i].vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=10)
		i += 1

def test_config_ixia_bgp_all(myixia,ipv6_networks,ipv4_networks,switches,ixia_bgp_as_list):
	for topo in myixia.topologies:
		topo.add_ipv6()
		topo.add_ipv4()

	for topo,net6,net4,ixia_bgp_as in zip(myixia.topologies,ipv6_networks,ipv4_networks,ixia_bgp_as_list):
		topo.bgpv6_network = net6
		topo.bgpv4_network = net4
		topo.bgp_as = ixia_bgp_as	 
	i = 0
	for topo in myixia.topologies:
		topo.add_bgp_v6(dut_ip=switches[i].vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=10)
		topo.add_bgp(dut_ip=switches[i].vlan1_ip,bgp_type='external',num=10)
		i += 1

def test_config_ixia_bgp_all_one_switch_cisco(myixia,ipv6_networks,ipv4_networks,switch,ixia_bgp_as_list,cisco_ipv6_networks,cisco_ipv4_networks,cisco_switch,cisco_ixia_bgp_as_list):
	for topo in myixia.topologies:
		topo.add_ipv6()
		topo.add_ipv4()

	for topo,net6,net4,ixia_bgp_as in zip(myixia.topologies[-2:],ipv6_networks,ipv4_networks,ixia_bgp_as_list):
		topo.bgpv6_network = net6
		topo.bgpv4_network = net4
		topo.bgp_as = ixia_bgp_as	 
	i = 0
	for topo in myixia.topologies[-2:]:
		topo.add_bgp_v6(dut_ip=switch.vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=10)
		topo.add_bgp(dut_ip=switch.vlan1_ip,bgp_type='external',num=10)
		i += 1


	for topo,net6,net4,ixia_bgp_as in zip(myixia.topologies[:2],cisco_ipv6_networks,cisco_ipv4_networks,cisco_ixia_bgp_as_list):
		topo.bgpv6_network = net6
		topo.bgpv4_network = net4
		topo.bgp_as = ixia_bgp_as	 
	i = 0
	for topo in myixia.topologies[:2]:
		topo.add_bgp_v6(dut_ip=cisco_switch.vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=10)
		topo.add_bgp(dut_ip=cisco_switch.vlan1_ip,bgp_type='external',num=10)
		i += 1

 
#print(settings.ONBOAR

def test_config_ixia_bgp_all_one_switch_compare(topologies,ipv6_networks,ipv4_networks,switch,ixia_bgp_as_list):
	for topo in topologies:
		topo.add_ipv6()
		topo.add_ipv4()

	for topo,net6,net4,ixia_bgp_as in zip(topologies,ipv6_networks,ipv4_networks,ixia_bgp_as_list):
		topo.bgpv6_network = net6
		topo.bgpv4_network = net4
		topo.bgp_as = ixia_bgp_as	 
	i = 0
	for topo in topologies:
		topo.add_bgp_v6(dut_ip=switch.vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=10)
		topo.add_bgp(dut_ip=switch.vlan1_ip,bgp_type='external',num=10)
		i += 1

def test_config_ixia_ibgp_all_one_switch_compare(topologies,ipv6_networks,ipv4_networks,switch,ixia_bgp_as_list):
	for topo in topologies:
		topo.add_ipv6()
		topo.add_ipv4()

	for topo,net6,net4,ixia_bgp_as in zip(topologies,ipv6_networks,ipv4_networks,ixia_bgp_as_list):
		topo.bgpv6_network = net6
		topo.bgpv4_network = net4
		topo.bgp_as = ixia_bgp_as	 
	i = 0
	for topo in topologies:
		topo.add_ibgp_v6(dut_ip=switch.vlan1_ipv6.split("/")[0],bgp_type='internal',prefix_num=10)
		topo.add_ibgp(dut_ip=switch.vlan1_ip,bgp_type='internal',num=10)
		i += 1

def test_config_ixia_bgp_all_one_switch(myixia,ipv6_networks,ipv4_networks,switch,ixia_bgp_as_list):
	for topo in myixia.topologies:
		topo.add_ipv6()
		topo.add_ipv4()

	for topo,net6,net4,ixia_bgp_as in zip(myixia.topologies,ipv6_networks,ipv4_networks,ixia_bgp_as_list):
		topo.bgpv6_network = net6
		topo.bgpv4_network = net4
		topo.bgp_as = ixia_bgp_as	 
	i = 0
	for topo in myixia.topologies:
		topo.add_bgp_v6(dut_ip=switch.vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=10)
		topo.add_bgp(dut_ip=switch.vlan1_ip,bgp_type='external',num=10)
		i += 1

 
#print(settings.ONBOARD_MSG)
#If in code development mode, skipping loging into switches 
tprint("============================== Pre-test setup and configuration ===================")

testbed_description = """
TBD
"""
print(testbed_description)


dut_dir_list = bgpv6_testbed_init()

##################################### Pre-Test setup and configuration #############################
if factory == True:
	for dut_dir in dut_dir_list:
		platform = dut_dir['platform']
		if platform == "fortinet":
			switch_factory_reset_nologin(dut_dir)

	console_timer(200,msg="Wait for 200s after reset factory default all switches")
	tprint('-------------------- re-login Fortigate devices after factory rest-----------------------')
	for dut_dir in dut_dir_list:
		dut_com = dut_dir['comm'] 
		dut_port = dut_dir['comm_port']
		platform = dut_dir['platform']
		if platform == "fortinet":
			dut = get_switch_telnet_connection_new(dut_com,dut_port,platform=dut_dir['platform'])
			dut_dir['telnet'] = dut

	for dut_dir in dut_dir_list:
		dut = dut_dir['telnet']
		dut_name = dut_dir['name']
		platform = dut_dir['platform']
		if platform == "fortinet":
			image = find_dut_image(dut)
			tprint(f"============================ {dut_name} software image = {image}")
			sw_init_config_v6(device=dut_dir,config_split =True)
if setup: 
	for dut_dir in dut_dir_list:
		dut = dut_dir['telnet']
		dut_name = dut_dir['name']
		platform = dut_dir['platform']
		if platform == "fortinet":
			image = find_dut_image(dut)
			tprint(f"============================ {dut_name} software image = {image}")
			sw_init_config_v6(device=dut_dir)

	# console_timer(30,msg="After intial configuration, show switch related information")
	# switches = [FortiSwitch(dut_dir) for dut_dir in dut_dir_list]
	# for switch in switches:
	# 		switch.router_ospf.show_ospf_neighbors()
	# 		switch.router_bgp.show_bgp_summary()
	# 	# Develop new codes starts from here
	# 	# stop_threads = False
	# 	# dut_cpu_memory(dut_dir_list,lambda: stop_threads)

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
	exit()

if Reboot:
	for dut_dir in dut_dir_list:
		dut = dut_dir['telnet']
		dut_name = dut_dir['name']
		platform = dut_dir['platform']

		if platform == "fortinet":
			switch_exec_reboot(dut,device=dut_name)
	console_timer(400,msg="Wait for 400s after started rebooting all switches")
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
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "Test iBGP via loopbacks"
	print_test_subject(testcase,description)
	if CLEAN_ALL:
		switches_clean_up(switches)
	else:
		for switch in switches:
			switch.router_bgp.clear_config()

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

if testcase == 6011 or test_all:
	testcase = 6011
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "Test IPv6 iBGP via loopbacks IPv6 address"
	print_test_subject(testcase,description)
	if CLEAN_ALL:
		switches_clean_up(switches)
	elif CLEAN_BGP:
		for switch in switches:
			switch.router_bgp.clear_config_all()
	else:
		pass

	for switch in switches:
		switch.show_switch_info()
		switch.router_ospf.neighbor_discovery_all()
		switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)
		if not switch.router_ospf.ospf_neighbor_all_up_v4(num=OSPF_NEIGHBORS):
			switch.router_ospf.basic_config()
			ospf_config = True
		else:
			Info(f"All OSPFv4 neighbors are up on switch {switch.loop0_ip}, No need to config OSPF ")
		if not switch.router_ospf.ospf_neighbor_all_up_v6(num=OSPF_NEIGHBORS):
			switch.router_ospf.basic_config_v6()
			ospf_config = True
		else:
			Info(f"All OSPFv6 neighbors are up on switch {switch.loop0_ip}, No need to config OSPF ")
	console_timer(20,msg="After discovering ospf with/without configuring, wait for 20 sec")

	for switch in switches:  
		switch.router_ospf.neighbor_discovery_all()
		switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)
		if CONFIG_BGP:
			switch.router_bgp.config_ibgp_mesh_loopback_v6() 
			switch.router_bgp.config_ibgp_mesh_loopback_v4() 

	for switch in switches:
		switch.router_bgp.config_bgp_bfd_all_neighbors('enable')

	console_timer(20,msg="===== After configuring iBGPv6 sessions via loopbacks && enable BFD, wait for 20s =====")
	for switch in switches:
		switch.router_bgp.show_bgp_summary_v6()
		switch.router_bgp.show_bfd_neighbor_v6()
		router_bfd = Router_BFD(switch)
		router_bfd.counte_peers_v6()

	#check_bgp_test_result_v6(testcase,description,switches)

	# for switch in switches:
	# 	switch.router_bgp.config_bgp_bfd_all_neighbors('disable')

	# console_timer(20,msg="===== After configuring iBGPv6 sessions via loopbacks && disable BFD, wait for 20s =====")
	# for switch in switches:
	# 	switch.router_bgp.show_bgp_summary_v6()
	# 	switch.router_bgp.show_bfd_neighbor_v6()

	#console_timer(20,msg="=======After configuring iBGPv6 sessions via loopbacks && disable BFD, wait for 20s ======")
	# for switch in switches:
	# 	switch.router_ospf.show_ospf_neighbors_v6()
	# 	switch.router_bgp.show_bgp_summary_v6()
	# 	switch.show_routing_v6()

	check_bgp_test_result_v6(testcase,description,switches)


if testcase == 6012 or test_all:
	testcase = 6012
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "Test IPv6 iBGP via loopbacks IPv4 and IPv6 addresses"
	print_test_subject(testcase,description)
	if CLEAN_ALL:
		switches_clean_up(switches)
	elif CLEAN_BGP:
		for switch in switches:
			switch.router_bgp.clear_config_v6()
	else:
		pass

	ospf_config = False
	for switch in switches:
		switch.show_switch_info()
		switch.router_ospf.neighbor_discovery_all()
		switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)
		if not switch.router_ospf.ospf_neighbor_all_up_v4(num=OSPF_NEIGHBORS):
			switch.router_ospf.basic_config()
			ospf_config = True
		else:
			Info(f"All OSPFv4 neighbors are up on switch {switch.loop0_ip}, No need to config OSPF ")
		if not switch.router_ospf.ospf_neighbor_all_up_v6(num=OSPF_NEIGHBORS):
			switch.router_ospf.basic_config_v6()
			ospf_config = True
		else:
			Info(f"All OSPFv6 neighbors are up on switch {switch.loop0_ip}, No need to config OSPF ")
	if ospf_config:
		console_timer(20,msg="After configuring ospfv6, wait for 20 sec")

	for switch in switches:  
		switch.router_ospf.neighbor_discovery_all()
		switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)
		switch.router_bgp.config_ibgp_mesh_loopback_v6() 
		switch.router_bgp.config_ibgp_mesh_loopback_v4()  
	console_timer(30,msg="After configuring iBGPv6 sessions via loopbacks, wait for 30s")
	for switch in switches:
		switch.router_ospf.show_ospf_neighbors_v6()
		switch.router_bgp.show_bgp_summary_v6()

	for switch in switches:
		switch.router_bgp.config_ibgp_loopback_bfd_v6('enable')

	console_timer(20,msg="===== After configuring iBGPv6 sessions via loopbacks && enable BFD, wait for 20s =====")
	for switch in switches:
		switch.router_ospf.show_ospf_neighbors_v6()
		switch.router_bgp.show_bgp_summary_v6()
		switch.show_routing_v6()

	check_bgp_test_result_v6(testcase,description,switches)

	for switch in switches:
		switch.router_bgp.config_ibgp_loopback_bfd_v6('disable')

	console_timer(20,msg="=======After configuring iBGPv6 sessions via loopbacks && disable BFD, wait for 20s ======")
	for switch in switches:
		switch.router_ospf.show_ospf_neighbors_v6()
		switch.router_bgp.show_bgp_summary_v6()
		switch.show_routing_v6()

	check_bgp_test_result_v6(testcase,description,switches)


if testcase == 6013 or test_all: #template for basic ipv4 and ipv6 iBGP
	testcase = 6013
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = """Test IPv6 iBGP via loopbacks IPv4 and IPv6 addresses, alternate activate and activate6
	This is for test cases: 952713,952715,952716,952717
	"""
	print_test_subject(testcase,description)
	if CLEAN_ALL:
		switches_clean_up(switches)
	elif CLEAN_BGP:
		for switch in switches:
			switch.router_bgp.clear_config_all()
	else:
		pass

	ospf_config = False
	for switch in switches:
		switch.show_switch_info()
		switch.router_ospf.neighbor_discovery_all()
		switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)
		if not switch.router_ospf.ospf_neighbor_all_up_v4(num=OSPF_NEIGHBORS):
			switch.router_ospf.basic_config()
			ospf_config = True
		else:
			Info(f"All OSPFv4 neighbors are up on switch {switch.loop0_ip}, No need to config OSPF ")
		if not switch.router_ospf.ospf_neighbor_all_up_v6(num=OSPF_NEIGHBORS):
			switch.router_ospf.basic_config_v6()
			ospf_config = True
		else:
			Info(f"All OSPFv6 neighbors are up on switch {switch.loop0_ip}, No need to config OSPF ")
	if ospf_config:
		console_timer(20,msg="After building ospfv4 and ospf6 routing infra, wait for 20 sec")

	for switch in switches:
		switch.router_ospf.show_ospf_neighbors_v6()
		switch.router_ospf.show_ospf_neighbors()

	for switch in switches:  
		switch.router_ospf.neighbor_discovery_all()
		switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)
		switch.router_bgp.config_ibgp_mesh_loopback_v6() 
		switch.router_bgp.config_ibgp_mesh_loopback_v4()  
	console_timer(30,msg="After configuring iBGPv6 sessions via loopbacks, wait for 30s")

	address_families = ['v4','v6']
	versions = ['v4','v6','both']

	for af in address_families:
		for ver in versions:
			for switch in switches:
				switch.router_bgp.activate_bgp_address_family(address_family = af,interface="loopback",version=ver) 
			console_timer(30,msg=f"After activing iBGP version {ver} on loopback interface address_family {af}, wait for 30s")
			switch.router_bgp.show_bgp_summary()
			switch.router_bgp.show_bgp_summary_v6()

	for af in address_families:
		for switch in switches:
			switch.router_bgp.activate_bgp_address_family(address_family = af,interface="loopback",version='both') 
		console_timer(30,msg=f"After activing iBGP version {ver} on loopback interface address_family {af}, wait for 30s")
	switch.router_bgp.show_bgp_summary()
	switch.router_bgp.show_bgp_summary_v6()

	# console_timer(30,msg="After activing address_family v4 and v6 on iBGPv6 sessions via loopbacks, wait for 30s")
	# for switch in switches:
	# 	switch.router_bgp.show_bgp_summary_v6()
	# 	switch.router_bgp.show_bgp_summary()

	check_bgp_test_result_v6(testcase,description,switches)

	#sys.stdout.close()

if testcase == 6014 or test_all:
	testcase = 6014
	description = "iBGP mesh over internal_v6,vlan1_ipv6 and loop0_ipv6. "
	print_test_subject(testcase,description)

	fsw_switches =switches[1:]
	network = BGP_networks(fsw_switches)

	test_clean_config(switches =fsw_switches)
	test_config_igp_ipv6(switches =fsw_switches)

	if test_config:
		network.biuld_ibgp_mesh_topo_sys_intf_v6()
		console_timer(20,msg=f"Test case {testcase}: After configuring fully mesh iBGP across all IPv6 system interfaces, wait....")
	network.show_summary_v6()

	for switch in fsw_switches:
		switch.router_bgp.config_bgp_bfd_all_neighbors('enable')

	console_timer(20,msg="===== After configuring iBGPv6 sessions via loopbacks, svi and LLOC intf && enable BFD, wait for 20s =====")
	for switch in fsw_switches:
		switch.router_bgp.show_bgp_summary_v6()
		switch.router_bgp.show_bfd_neighbor_v6()
		router_bfd = Router_BFD(switch)
		router_bfd.counte_peers_v6()

	for switch in fsw_switches:
		switch.router_bgp.config_bgp_bfd_all_neighbors('disable')

	console_timer(20,msg="===== After configuring iBGPv6 sessions via loopbacks && disable BFD, wait for 20s =====")
	for switch in fsw_switches:
		switch.router_bgp.show_bgp_summary_v6()
		switch.router_bgp.show_bfd_neighbor_v6()

	console_timer(20,msg="=======After configuring iBGPv6 sessions via loopbacks && disable BFD, wait for 20s ======")
	for switch in fsw_switches:
		switch.router_ospf.show_ospf_neighbors_v6()
		switch.router_bgp.show_bgp_summary_v6()
		switch.show_routing_v6()

	check_bgp_test_result_v6(testcase,description,fsw_switches)


if testcase == 2 or test_all:
	testcase = 2
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "iBGP SVI interface"
	print_test_subject(testcase,description)
	if CLEAN_ALL:
		switches_clean_up(switches)
	else:
		for switch in switches:
			switch.router_bgp.clear_config()
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

if testcase == 6021 or test_all:
	testcase = 6021
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "iBGP v6 SVI interface"
	print_test_subject(testcase,description)

	if CLEAN_ALL:
		switches_clean_up(switches)
	elif CLEAN_BGP:
		for switch in switches:
			switch.router_bgp.clear_config_v6()
	else:
		pass

	ospf_config = False
	for switch in switches:
		switch.show_switch_info()
		switch.router_ospf.neighbor_discovery_v6()
		switch.router_bgp.update_ospf_neighbors_v6(sw_list=switches)
		if not switch.router_ospf.ospf_neighbor_all_up_v6(num=OSPF_NEIGHBORS):
			switch.router_ospf.basic_config_v6()
			ospf_config = True

		else:
			Info(f"All OSPFve neighbors are up on switch {switch.loop0_ip}, No need to config OSPF ")
	if ospf_config:
		console_timer(20,msg="After configuring ospfv6, wait for 20 sec")

	for switch in switches:
		switch.router_ospf.show_ospf_neighbors_v6()


	for switch in switches:  
		switch.router_ospf.neighbor_discovery_v6()
		switch.router_bgp.update_ospf_neighbors_v6(sw_list=switches)
		switch.router_bgp.config_ibgp_mesh_svi_v6()

	console_timer(60,msg="After configuring iBGP sessions, wait for 60s")
	for switch in switches:
		switch.router_bgp.show_bgp_summary_v6()
	check_bgp_test_result_v6(testcase,description,switches)


if testcase == 6022 or test_all:
	testcase = 6022
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "iBGP v6 and v4 SVI interface"
	print_test_subject(testcase,description)

	if CLEAN_ALL:
		switches_clean_up(switches)
	elif CLEAN_BGP:
		for switch in switches:
			switch.router_bgp.clear_config_v6()
	else:
		pass

	ospf_config = False
	for switch in switches:
		switch.show_switch_info()
		switch.router_ospf.neighbor_discovery_v6()
		switch.router_bgp.update_ospf_neighbors_v6(sw_list=switches)
		if not switch.router_ospf.ospf_neighbor_all_up_v6(num=OSPF_NEIGHBORS):
			switch.router_ospf.basic_config_v6()
			ospf_config = True

		else:
			Info(f"All OSPFve neighbors are up on switch {switch.loop0_ip}, No need to config OSPF ")
	if ospf_config:
		console_timer(20,msg="After configuring ospfv6, wait for 20 sec")

	for switch in switches:
		switch.router_ospf.show_ospf_neighbors_v6()


	for switch in switches:  
		switch.router_ospf.neighbor_discovery_v6()
		switch.router_bgp.update_ospf_neighbors_v6(sw_list=switches)
		switch.router_bgp.config_ibgp_mesh_svi_v6()
		switch.router_ospf.neighbor_discovery()
		switch.router_bgp.config_ibgp_mesh_direct()

	console_timer(60,msg="After configuring iBGP sessions, wait for 60s")
	for switch in switches:
		switch.router_bgp.show_bgp_summary_v6()

	check_bgp_test_result(testcase,description,switches)
	check_bgp_test_result_v6(testcase,description,switches)

	#sys.stdout.close()

if testcase == 6023 or test_all:
	testcase = 6023
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "iBGP on v6 and v4 SVI interface, alternate address faimily"
	print_test_subject(testcase,description)

	if CLEAN_ALL:
		switches_clean_up(switches)
	elif CLEAN_BGP:
		for switch in switches:
			switch.router_bgp.clear_config_v6()
	else:
		pass

	ospf_config = False
	for switch in switches:
		switch.show_switch_info()
		switch.router_ospf.neighbor_discovery_all()
		switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)
		if not switch.router_ospf.ospf_neighbor_all_up_v4(num=OSPF_NEIGHBORS):
			switch.router_ospf.basic_config()
			ospf_config = True
		else:
			Info(f"All OSPFv4 neighbors are up on switch {switch.loop0_ip}, No need to config OSPF ")
		if not switch.router_ospf.ospf_neighbor_all_up_v6(num=OSPF_NEIGHBORS):
			switch.router_ospf.basic_config_v6()
			ospf_config = True
		else:
			Info(f"All OSPFv6 neighbors are up on switch {switch.loop0_ip}, No need to config OSPF ")
	if ospf_config:
		console_timer(20,msg="After building ospfv4 and ospf6 routing infra, wait for 20 sec")

	for switch in switches:
		switch.router_ospf.show_ospf_neighbors_v6()


	for switch in switches:  
		switch.router_ospf.neighbor_discovery_all()
		switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)
		switch.router_bgp.config_ibgp_mesh_svi_v6()
		switch.router_bgp.config_ibgp_mesh_direct()

	console_timer(60,msg="After configuring iBGP sessions, wait for 60s")

	address_families = ['v4','v6']
	versions = ['v4','v6','both']

	for af in address_families:
		for ver in versions:
			for switch in switches:
				switch.router_bgp.activate_bgp_address_family(address_family = af,interface="svi",version=ver) 
			console_timer(30,msg=f"After activing iBGP version {ver} on SVI interface address_family {af}, wait for 30s")
			print(f"=============== Expecting {af} SVI neighbors have {ver} BGP session activated ============== ")
			switch.router_bgp.show_bgp_summary()
			switch.router_bgp.show_bgp_summary_v6()


	for af in address_families:
		for switch in switches:
			switch.router_bgp.activate_bgp_address_family(address_family = af,interface="svi",version='both') 
		console_timer(30,msg=f"Rewinding config: After activing iBGP version v4 and v6 on loopback interface address_family {af}, wait for 30s")
	switch.router_bgp.show_bgp_summary()
	switch.router_bgp.show_bgp_summary_v6()

	check_bgp_test_result_v6(testcase,description,switches)

	check_bgp_test_result(testcase,description,switches)
 
if testcase == 6024 or test_all:
	testcase = 6024
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "iBGP on Link Local Address"
	print_test_subject(testcase,description)

	if CLEAN_ALL:
		switches_clean_up(switches)
	elif CLEAN_BGP:
		for switch in switches:
			switch.router_bgp.clear_config_v6()
	else:
		pass

	ospf_config = False
	for switch in switches:
		switch.show_switch_info()
		switch.router_ospf.neighbor_discovery_all()
		switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)
		if not switch.router_ospf.ospf_neighbor_all_up_v4(num=OSPF_NEIGHBORS):
			switch.router_ospf.basic_config()
			ospf_config = True
		else:
			Info(f"All OSPFv4 neighbors are up on switch {switch.loop0_ip}, No need to config OSPF ")
		if not switch.router_ospf.ospf_neighbor_all_up_v6(num=OSPF_NEIGHBORS):
			switch.router_ospf.basic_config_v6()
			ospf_config = True
		else:
			Info(f"All OSPFv6 neighbors are up on switch {switch.loop0_ip}, No need to config OSPF ")
	if ospf_config:
		console_timer(20,msg="After building ospfv4 and ospf6 routing infra, wait for 20 sec")

	for switch in switches:
		switch.router_ospf.show_ospf_neighbors_v6()


	for switch in switches:  
		switch.router_ospf.neighbor_discovery_all()
		switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)
		switch.discover_ipv6_neighbors()
		switch.router_bgp.config_ibgp_mesh_svi_v6()
		switch.router_bgp.config_ibgp_mesh_direct()
		switch.router_bgp.update_ipv6_neighbor_cache()
		switch.router_bgp.config_ibgp_mesh_link_local()

	console_timer(60,msg="After configuring iBGP sessions over link local address, wait for 60s")

	for switch in switches:
		switch.router_bgp.config_bgp_bfd_all_neighbors('enable')

	console_timer(20,msg="===== After configuring iBGPv6 sessions via loopbacks, svi and LLOC intf && enable BFD, wait for 20s =====")
	for switch in switches:
		switch.router_bgp.show_bgp_summary_v6()
		switch.router_bgp.show_bfd_neighbor_v6()
		router_bfd = Router_BFD(switch)
		router_bfd.counte_peers_v6()

	for switch in switches:
		switch.router_bgp.config_bgp_bfd_all_neighbors('disable')

	console_timer(20,msg="===== After configuring iBGPv6 sessions via loopbacks && disable BFD, wait for 20s =====")
	for switch in switches:
		switch.router_bgp.show_bgp_summary_v6()
		switch.router_bgp.show_bfd_neighbor_v6()

	console_timer(20,msg="=======After configuring iBGPv6 sessions via loopbacks && disable BFD, wait for 20s ======")
	for switch in switches:
		switch.router_ospf.show_ospf_neighbors_v6()
		switch.router_bgp.show_bgp_summary_v6()
		switch.show_routing_v6()

	check_bgp_test_result_v6(testcase,description,switches)

 
if testcase == 6025 or test_all:
	testcase = 6025
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "Negative Testing: iBGP on all interfaces: loopback,SVI And Link Local Address, Enable BFD"
	print_test_subject(testcase,description)

	if CLEAN_ALL:
		switches_clean_up(switches)
	elif CLEAN_BGP:
		for switch in switches:
			switch.router_bgp.clear_config_all()
	else:
		pass

	ospf_config = False
	for switch in switches:
		switch.show_switch_info()
		switch.router_ospf.neighbor_discovery_all()
		switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)
		if not switch.router_ospf.ospf_neighbor_all_up_v4(num=OSPF_NEIGHBORS):
			switch.router_ospf.basic_config()
			ospf_config = True
		else:
			Info(f"All OSPFv4 neighbors are up on switch {switch.loop0_ip}, No need to config OSPF ")
		if not switch.router_ospf.ospf_neighbor_all_up_v6(num=OSPF_NEIGHBORS):
			switch.router_ospf.basic_config_v6()
			ospf_config = True
		else:
			Info(f"All OSPFv6 neighbors are up on switch {switch.loop0_ip}, No need to config OSPF ")
	if ospf_config:
		console_timer(20,msg="After building ospfv4 and ospf6 routing infra, wait for 20 sec")

	for switch in switches:
		switch.router_ospf.show_ospf_neighbors_v6()


	for switch in switches:  
		switch.router_ospf.neighbor_discovery_all()
		switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)
		switch.discover_ipv6_neighbors()
		switch.router_bgp.config_ibgp_mesh_svi_v6() #config IPv6 over svi 
		switch.router_bgp.config_ibgp_mesh_direct() #config IPv4 over svi 
		switch.router_bgp.update_ipv6_neighbor_cache()
		switch.router_bgp.config_ibgp_mesh_link_local() #config link local
		switch.router_bgp.config_ibgp_mesh_loopback_v6() #config IPv6 over loopback
		switch.router_bgp.config_ibgp_mesh_loopback_v4()  #config IPv4 over loopback

	console_timer(60,msg="After configuring iBGP sessions over loopback, svi and link local address, wait for 60s")

	for switch in switches:
		switch.router_bgp.config_bgp_bfd_all_neighbors('enable')

	console_timer(20,msg="===== After configuring iBGPv6 sessions via loopbacks, svi and LLOC intf && enable BFD, wait for 20s =====")
	for switch in switches:
		switch.router_bgp.show_bgp_summary_v6()
		switch.router_bgp.show_bfd_neighbor_v6()
		router_bfd = Router_BFD(switch)
		router_bfd.counte_peers_v6()

	check_bgp_test_result_v6(testcase,description,switches)

	# for switch in switches:
	# 	switch.router_bgp.config_bgp_bfd_all_neighbors('disable')

	# console_timer(20,msg="===== After configuring iBGPv6 sessions via loopbacks && disable BFD, wait for 20s =====")
	# for switch in switches:
	# 	switch.router_bgp.show_bgp_summary_v6()
	# 	switch.router_bgp.show_bfd_neighbor_v6()

	# console_timer(20,msg="=======After configuring iBGPv6 sessions via loopbacks && disable BFD, wait for 20s ======")
	# for switch in switches:
	# 	switch.router_ospf.show_ospf_neighbors_v6()
	# 	switch.router_bgp.show_bgp_summary_v6()
	# 	switch.show_routing_v6()

	check_bgp_test_result_v6(testcase,description,switches)
	
if testcase == 3 or test_all:
	testcase = 3
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGP Redistribute connected"
	print_test_subject(testcase,description)

	if CLEAN_ALL:
		switches_clean_up(switches)
	else:
		for switch in switches:
			switch.router_bgp.clear_config()

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

if testcase == 6031 or test_all:
	testcase = 6031
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "Test IPv6 redistrubted connected"
	print_test_subject(testcase,description)
	if CLEAN_ALL:
		switches_clean_up(switches)
	elif CLEAN_BGP:
		for switch in switches:
			switch.router_bgp.clear_config_v6()
	else:
		pass

	for switch in switches:
		switch.show_switch_info()
		switch.router_ospf.neighbor_discovery_all()
		switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)
		if not switch.router_ospf.ospf_neighbor_all_up_v4(num=OSPF_NEIGHBORS):
			switch.router_ospf.basic_config()
		else:
			Info(f"All OSPFv4 neighbors are up on switch {switch.loop0_ip}, No need to config OSPF ")
		if not switch.router_ospf.ospf_neighbor_all_up_v6(num=OSPF_NEIGHBORS):
			switch.router_ospf.basic_config_v6()
		else:
			Info(f"All OSPFv6 neighbors are up on switch {switch.loop0_ip}, No need to config OSPF ")
	console_timer(20,msg="After checking and/or configuring  ospf v4 and ospfv6, wait for 20 sec")

	for switch in switches:  
		switch.router_ospf.neighbor_discovery_all()
		switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)
		switch.router_bgp.config_ibgp_mesh_loopback_v6() 
		switch.router_bgp.config_ibgp_mesh_loopback_v4()  
	console_timer(30,msg="After configuring iBGPv6 sessions via loopbacks, wait for 30s")
	for switch in switches:
		switch.router_ospf.show_ospf_neighbors_v6()
		switch.router_bgp.show_bgp_summary_v6()

	for switch in switches:
		switch.router_bgp.show_bgp_summary()
		switch.router_bgp.config_redistribute_connected_v6() 

	check_bgp_test_result_v6(testcase,description,switches)


if testcase == 4 or test_all:
	testcase = 4
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGP Redistribute static"
	print_test_subject(testcase,description)
	if CLEAN_ALL:
		switches_clean_up(switches)
	else:
		for switch in switches:
			switch.router_bgp.clear_config()

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
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "iBGP via second interface" 
	print_test_subject(testcase,description)
	if CLEAN_ALL:
		switches_clean_up(switches)
	else:
		for switch in switches:
			switch.router_bgp.clear_config()
	
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
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "eBGP direct connection"
	print_test_subject(testcase,description)

	if CLEAN_ALL:
		switches_clean_up(switches)
	elif CLEAN_BGP:
		for switch in switches:
			switch.router_bgp.clear_config_v6()
	else:
		pass

	for switch in switches:
		switch.vlan_neighors(switches)
		switch.show_vlan_neighbors()
		switch.router_bgp.config_ebgp_mesh_direct()
	console_timer(60,msg="After configuring eBGP sessions, wait for 60s")
	for switch in switches:
		switch.show_routing()

if testcase == 6061 or test_all:
	testcase = 6061
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "eBGP v6 direct connection via SVI interfaces"
	print_test_subject(testcase,description)

	# Clean up configuration before start testing
	if CLEAN_ALL:
		switches_clean_up(switches)
	elif CLEAN_BGP:
		for switch in switches:
			switch.router_bgp.clear_config_all()
	else:
		pass

	ospf_config_v4 = False
	ospf_config_v6 = False
	#Config OSPF infra
	for switch in switches:
		switch.show_switch_info()
		switch.router_ospf.neighbor_discovery_all()
		switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)
		if not switch.router_ospf.ospf_neighbor_all_up_v4(num=OSPF_NEIGHBORS):
			switch.router_ospf.basic_config()
			ospf_config_v4 = True
		else:
			Info(f"All OSPFv4 neighbors are up on switch {switch.loop0_ip}, No need to config OSPF ")
		if not switch.router_ospf.ospf_neighbor_all_up_v6(num=OSPF_NEIGHBORS):
			switch.router_ospf.basic_config_v6()
			ospf_config_v6 = True
		else:
			Info(f"All OSPFv6 neighbors are up on switch {switch.loop0_ip}, No need to config OSPF ")
	if ospf_config_v4 or ospf_config_v6:
		console_timer(20,msg="After building ospfv4 and ospf6 routing infra, wait for 20 sec")

	#update IPv4 and IPv6 ospf neighbors after configuring ospf 
	Info("=============== Updating OSPF Config and Neighbor Information ==========")
	for switch in switches:
		switch.router_ospf.show_ospf_neighbors_all()
		print("----------Discovering ospf neighbor ---------")
		switch.router_ospf.neighbor_discovery_all()
		print("----------Updating ospf neighbor database  ---------")
		switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)

	for switch in switches:
		switch.router_bgp.config_ebgp_mesh_svi_v6()
	console_timer(60,msg="After configuring eBGP sessions, wait for 60s")
	# for switch in switches:
	# 	switch.show_routing_v6()
	check_bgp_test_result_v6(testcase,description,switches)

if testcase == 6062 or test_all:
	testcase = 6062
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "eBGP v4 and v6 direct connection via SVI interfaces"
	print_test_subject(testcase,description)

	# Clean up configuration before start testing
	if CLEAN_ALL:
		switches_clean_up(switches)
	elif CLEAN_BGP:
		for switch in switches:
			switch.router_bgp.clear_config_all()
	else:
		pass

	ospf_config_v4 = False
	ospf_config_v6 = False
	#Config OSPF infra
	for switch in switches:
		switch.show_switch_info()
		switch.router_ospf.neighbor_discovery_all()
		switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)
		if not switch.router_ospf.ospf_neighbor_all_up_v4(num=OSPF_NEIGHBORS):
			switch.router_ospf.basic_config()
			ospf_config_v4 = True
		else:
			Info(f"All OSPFv4 neighbors are up on switch {switch.loop0_ip}, No need to config OSPF ")
		if not switch.router_ospf.ospf_neighbor_all_up_v6(num=OSPF_NEIGHBORS):
			switch.router_ospf.basic_config_v6()
			ospf_config_v6 = True
		else:
			Info(f"All OSPFv6 neighbors are up on switch {switch.loop0_ip}, No need to config OSPF ")
	if ospf_config_v4 or ospf_config_v6:
		console_timer(20,msg="After building ospfv4 and ospf6 routing infra, wait for 20 sec")

	#update IPv4 and IPv6 ospf neighbors after configuring ospf 
	Info("=============== Updating OSPF Config and Neighbor Information ==========")
	for switch in switches:
		switch.router_ospf.show_ospf_neighbors_all()
		print("----------Discovering ospf neighbor ---------")
		switch.router_ospf.neighbor_discovery_all()
		print("----------Updating ospf neighbor database  ---------")
		switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)

	for switch in switches:
		switch.router_bgp.config_ebgp_mesh_svi_v4()
		switch.router_bgp.config_ebgp_mesh_svi_v6()
	console_timer(60,msg="After configuring eBGP sessions, wait for 60s")
	# for switch in switches:
	# 	switch.show_routing_v6()
	check_bgp_test_result_v6(testcase,description,switches)

if testcase == 6063 or test_all:
	testcase = 6063
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "eBGP v4 and v6 direct connection via SVI interfaces"
	print_test_subject(testcase,description)

	# Clean up configuration before start testing
	if CLEAN_ALL:
		switches_clean_up(switches)
	elif CLEAN_BGP:
		for switch in switches:
			switch.router_bgp.clear_config_all()
	else:
		pass

	ospf_config_v4 = False
	ospf_config_v6 = False
	#Config OSPF infra
	for switch in switches:
		switch.show_switch_info()
		switch.router_ospf.neighbor_discovery_all()
		switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)
		if not switch.router_ospf.ospf_neighbor_all_up_v4(num=OSPF_NEIGHBORS):
			switch.router_ospf.basic_config()
			ospf_config_v4 = True
		else:
			Info(f"All OSPFv4 neighbors are up on switch {switch.loop0_ip}, No need to config OSPF ")
		if not switch.router_ospf.ospf_neighbor_all_up_v6(num=OSPF_NEIGHBORS):
			switch.router_ospf.basic_config_v6()
			ospf_config_v6 = True
		else:
			Info(f"All OSPFv6 neighbors are up on switch {switch.loop0_ip}, No need to config OSPF ")
	if ospf_config_v4 or ospf_config_v6:
		console_timer(20,msg="After building ospfv4 and ospf6 routing infra, wait for 20 sec")

	#update IPv4 and IPv6 ospf neighbors after configuring ospf 
	Info("=============== Updating OSPF Config and Neighbor Information ==========")
	for switch in switches:
		switch.router_ospf.show_ospf_neighbors_all()
		print("----------Discovering ospf neighbor ---------")
		switch.router_ospf.neighbor_discovery_all()
		print("----------Updating ospf neighbor database  ---------")
		switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)

	for switch in switches:
		switch.router_bgp.config_ebgp_mesh_svi_v4()
		switch.router_bgp.config_ebgp_mesh_svi_v6()
	console_timer(60,msg="After configuring eBGP sessions, wait for 60s")
	for switch in switches:
		switch.show_routing_v6()


	for switch in switches:  
		switch.router_bgp.activate_bgp_address_family(address_family = "v4",interface="svi") 
	console_timer(30,msg="After activing address_family on iBGPv6 sessions via loopbacks, wait for 30s")

	for switch in switches:
		switch.router_bgp.show_bgp_summary()
	check_bgp_test_result(testcase,description,switches)
	check_bgp_test_result_v6(testcase,description,switches)

	for switch in switches:  
		switch.router_bgp.activate_bgp_address_family(address_family = "v6",interface="svi") 
	console_timer(30,msg="After activing address_family on iBGPv6 sessions via loopbacks, wait for 30s")

	for switch in switches:
		switch.router_bgp.show_bgp_summary_v6()
	check_bgp_test_result_v6(testcase,description,switches)
	check_bgp_test_result(testcase,description,switches)

	 


if testcase == 7 or test_all:
	testcase = 7
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "Redistrubuting ospf into BGP"
	print_test_subject(testcase,description)
	if CLEAN_ALL:
		switches_clean_up(switches)
	else:
		for switch in switches:
			switch.router_bgp.clear_config()
	
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
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGP BFD neighbor"
	print_test_subject(testcase,description)

	if CLEAN_ALL:
		switches_clean_up(switches)
	else:
		for switch in switches:
			switch.router_bgp.clear_config()
	 
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
	testcase = 9
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "Basic eBGP peered to IXIA and traffic forwarding"
	print_test_subject(testcase,description)

	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	portList = [[ixChassisIpList[0], 2,11,"00:11:01:01:01:01","10.10.1.1",101,"10.1.1.101/24","10.1.1.1"], 
	[ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.20.1.1",102,"10.1.1.102/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.30.1.1",103,"10.1.1.103/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.40.1.1",104,"10.1.1.104/24","10.1.1.1"], 
	[ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.50.1.1",105,"10.1.1.105/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.60.1.1",106,"10.1.1.106/24","10.1.1.1"]]

	if CLEAN_ALL:
		switches_clean_up(switches)
	else:
		for switch in switches:
			switch.router_bgp.clear_config()
	 
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
	
	for switch,ixia_port_info in zip(switches,portList):
		if switch.router_bgp.config_ebgp_ixia(ixia_port_info) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP peers ==============")
			exit()

	myixia = BGPv4_IXIA(apiServerIp,ixChassisIpList,portList)

 	
	for topo in myixia.topologies:
		topo.add_ipv4()

	
	myixia.topologies[0].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=100)
	myixia.topologies[1].add_bgp(dut_ip='10.1.1.2',bgp_type='external',num=100)
	myixia.topologies[2].add_bgp(dut_ip='10.1.1.3',bgp_type='external',num=100)
	myixia.topologies[3].add_bgp(dut_ip='10.1.1.4',bgp_type='external',num=100)
	myixia.topologies[4].add_bgp(dut_ip='10.1.1.5',bgp_type='external',num=100)
	myixia.topologies[5].add_bgp(dut_ip='10.1.1.6',bgp_type='external',num=100)


	myixia.start_protocol(wait=40)

	myixia.create_traffic(src_topo=myixia.topologies[0].topology, dst_topo=myixia.topologies[1].topology,traffic_name="t1_to_t2",tracking_name="Tracking_1")
	myixia.create_traffic(src_topo=myixia.topologies[1].topology, dst_topo=myixia.topologies[0].topology,traffic_name="t2_to_t1",tracking_name="Tracking_2")

	myixia.create_traffic(src_topo=myixia.topologies[2].topology, dst_topo=myixia.topologies[3].topology,traffic_name="t2_to_t3",tracking_name="Tracking_3")
	myixia.create_traffic(src_topo=myixia.topologies[3].topology, dst_topo=myixia.topologies[2].topology,traffic_name="t3_to_t2",tracking_name="Tracking_4")

	myixia.create_traffic(src_topo=myixia.topologies[4].topology, dst_topo=myixia.topologies[5].topology,traffic_name="t4_to_t5",tracking_name="Tracking_5")
	myixia.create_traffic(src_topo=myixia.topologies[5].topology, dst_topo=myixia.topologies[4].topology,traffic_name="t5_to_t4",tracking_name="Tracking_6")


	myixia.start_traffic()
	myixia.collect_stats()
	myixia.check_traffic()

	check_bgp_test_result(testcase,description,switches)

if testcase == 6091 or test_all:
	testcase = 6091
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "Basic eBGP IPv4 And IPv6 peered to IXIA and traffic forwarding"
	print_test_subject(testcase,description)

	# IXIA and switch information
	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	portList_v4_v6 = [
	[ixChassisIpList[0], 2, 11,"00:11:01:01:01:01","10.1.1.211/24","10.1.1.1","2001:10:1:1::211/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.1.1.212/24","10.1.1.1","2001:10:1:1::212/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.1.1.213/24","10.1.1.1","2001:10:1:1::213/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.1.1.214/24","10.1.1.1","2001:10:1:1::214/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.1.1.215/24","10.1.1.1","2001:10:1:1::215/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.1.1.216/24","10.1.1.1","2001:10:1:1::216/64","2001:10:1:1::1",1]
    ]

	ixia_ipv6_as_list = [101,102,103,104,105,106]
	ipv4_networks = ["10.10.1.1","10.10.2.1","10.10.3.1","10.10.4.1","10.10.5.1","10.10.6.1"]
	ipv6_networks = ["2001:101:1:1::1","2001:102:1:1::1","2001:103:1:1::1","2001:104:1:1::1","2001:105:1:1::211","2001:106:1:1::1"]

	fsw_switches =switches[1:]
	network = BGP_networks(switches)

	# Infra configuration
	if test_config:
		test_clean_config(switches =fsw_switches)
		test_config_igp_ipv6(switches =fsw_switches)
		network.biuld_ibgp_mesh_topo_sys_intf_v6()
		network.biuld_ibgp_mesh_topo_sys_intf()
		console_timer(20,msg=f"Test case {testcase}: After configuring fully mesh iBGP across all IPv6 system interfaces, wait....")
		network.show_summary_v6()
	
	# FSW configuration
	for switch, ixia_port_info, ixia_as in zip(fsw_switches,portList_v4_v6,ixia_ipv6_as_list):
		if switch.router_bgp.config_ebgp_ixia_v6(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v6 peers ==============")
			exit()
		if switch.router_bgp.config_ebgp_ixia_v4(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v4 peers ==============")
			exit()

	# IXIA configuration
	myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)

	for topo in myixia.topologies:
		topo.add_ipv6()
		topo.add_ipv4()
	 
	for topo,net6,net4,as_num in zip(myixia.topologies,ipv6_networks,ipv4_networks,ixia_ipv6_as_list):
		topo.bgpv6_network = net6
		topo.bgpv4_network = net4
		topo.bgp_as = as_num
		 
	i = 0
	for topo in myixia.topologies:
		topo.add_bgp(dut_ip=fsw_switches[i].vlan1_ip,bgp_type='external',num=100)
		topo.add_bgp_v6(dut_ip=fsw_switches[i].vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=100)
		i += 1

	myixia.start_protocol(wait=40)


	myixia.create_traffic(src_topo=myixia.topologies[0].topology, dst_topo=myixia.topologies[1].topology,traffic_name="t1_to_t2",tracking_name="Tracking_1")
	myixia.create_traffic(src_topo=myixia.topologies[1].topology, dst_topo=myixia.topologies[0].topology,traffic_name="t2_to_t1",tracking_name="Tracking_2")

	myixia.create_traffic(src_topo=myixia.topologies[2].topology, dst_topo=myixia.topologies[3].topology,traffic_name="t2_to_t3",tracking_name="Tracking_3")
	myixia.create_traffic(src_topo=myixia.topologies[3].topology, dst_topo=myixia.topologies[2].topology,traffic_name="t3_to_t2",tracking_name="Tracking_4")

	myixia.create_traffic(src_topo=myixia.topologies[4].topology, dst_topo=myixia.topologies[5].topology,traffic_name="t4_to_t5",tracking_name="Tracking_5")
	myixia.create_traffic(src_topo=myixia.topologies[5].topology, dst_topo=myixia.topologies[4].topology,traffic_name="t5_to_t4",tracking_name="Tracking_6")


	myixia.create_traffic_v6(src_topo=myixia.topologies[0].topology, dst_topo=myixia.topologies[1].topology,traffic_name="t1_to_t2",tracking_name="Tracking_1_v6")
	myixia.create_traffic_v6(src_topo=myixia.topologies[1].topology, dst_topo=myixia.topologies[0].topology,traffic_name="t2_to_t1",tracking_name="Tracking_2_v6")

	myixia.create_traffic_v6(src_topo=myixia.topologies[2].topology, dst_topo=myixia.topologies[3].topology,traffic_name="t2_to_t3",tracking_name="Tracking_3_v6")
	myixia.create_traffic_v6(src_topo=myixia.topologies[3].topology, dst_topo=myixia.topologies[2].topology,traffic_name="t3_to_t2",tracking_name="Tracking_4_v6")

	myixia.create_traffic_v6(src_topo=myixia.topologies[4].topology, dst_topo=myixia.topologies[5].topology,traffic_name="t4_to_t5",tracking_name="Tracking_5_v6")
	myixia.create_traffic_v6(src_topo=myixia.topologies[5].topology, dst_topo=myixia.topologies[4].topology,traffic_name="t5_to_t4",tracking_name="Tracking_6_v6")


	myixia.start_traffic()
	myixia.collect_stats()
	myixia.check_traffic()

	check_bgp_test_result(testcase,description,switches)


if testcase == 6092 or test_all:
	testcase = 6092
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "Basic eBGP IPv4 And IPv6 ECMP peered to IXIA and traffic forwarding"
	print_test_subject(testcase,description)

	# IXIA and switch information
	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	portList_v4_v6 = [
	[ixChassisIpList[0], 2, 11,"00:11:01:01:01:01","10.1.1.211/24","10.1.1.1","2001:10:1:1::211/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.1.1.212/24","10.1.1.1","2001:10:1:1::212/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.1.1.213/24","10.1.1.1","2001:10:1:1::213/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.1.1.214/24","10.1.1.1","2001:10:1:1::214/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.1.1.215/24","10.1.1.1","2001:10:1:1::215/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.1.1.216/24","10.1.1.1","2001:10:1:1::216/64","2001:10:1:1::1",1]
    ]

	ixia_ipv6_as_list = [101,102,103,104,105,106]
	ipv4_networks = ["10.10.1.1","10.10.1.1","10.10.1.1","10.10.2.1","10.10.2.1","10.10.2.1"]
	ipv6_networks = ["2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:102:1:1::1","2001:102:1:1::1","2001:102:1:1::1"]

	fsw_switches =switches[1:]
	network = BGP_networks(switches)

	# Infra configuration
	if test_config:
		test_clean_config(switches =fsw_switches)
		test_config_igp_ipv6(switches =fsw_switches)
		network.biuld_ibgp_mesh_topo_sys_intf_v6()
		network.biuld_ibgp_mesh_topo_sys_intf()
		console_timer(20,msg=f"Test case {testcase}: After configuring fully mesh iBGP across all IPv6 system interfaces, wait....")
		network.show_summary_v6()
	
	# FSW configuration
		for switch, ixia_port_info, ixia_as in zip(fsw_switches,portList_v4_v6,ixia_ipv6_as_list):
			if switch.router_bgp.config_ebgp_ixia_v6(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
				tprint("================= !!!!! Not able to configure IXIA BGP v6 peers ==============")
				exit()
			if switch.router_bgp.config_ebgp_ixia_v4(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
				tprint("================= !!!!! Not able to configure IXIA BGP v4 peers ==============")
				exit()

	# IXIA configuration
	myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)

	for topo in myixia.topologies:
		topo.add_ipv6()
		topo.add_ipv4()
	 
	for topo,net6,net4,as_num in zip(myixia.topologies,ipv6_networks,ipv4_networks,ixia_ipv6_as_list):
		topo.bgpv6_network = net6
		topo.bgpv4_network = net4
		topo.bgp_as = as_num
		 
	i = 0
	for topo in myixia.topologies:
		topo.add_bgp(dut_ip=fsw_switches[i].vlan1_ip,bgp_type='external',num=10)
		topo.add_bgp_v6(dut_ip=fsw_switches[i].vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=10)
		i += 1

	myixia.start_protocol(wait=40)


	myixia.create_traffic(src_topo=myixia.topologies[1].topology, dst_topo=myixia.topologies[5].topology,traffic_name="t1_to_t6",tracking_name="Tracking_1")
	myixia.create_traffic(src_topo=myixia.topologies[5].topology, dst_topo=myixia.topologies[1].topology,traffic_name="t6_to_t1",tracking_name="Tracking_2")

	myixia.create_traffic_v6(src_topo=myixia.topologies[1].topology, dst_topo=myixia.topologies[5].topology,traffic_name="t1_to_t6_v6",tracking_name="Tracking_1_v6")
	myixia.create_traffic_v6(src_topo=myixia.topologies[5].topology, dst_topo=myixia.topologies[1].topology,traffic_name="t6_to_t1_v6",tracking_name="Tracking_2_v6")

	 

	myixia.start_traffic()
	myixia.collect_stats()
	myixia.check_traffic()

	check_bgp_test_result(testcase,description,fsw_switches)


if testcase == 10 or test_all:
	testcase = 10
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "Large number of eBGP peered to IXIA and traffic forwarding"
	print_test_subject(testcase,description)
	if CLEAN_ALL:
		switches_clean_up(switches)
	else:
		for switch in switches:
			switch.router_bgp.clear_config()

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

	portList = [[ixChassisIpList[0], 2,11,"00:11:01:01:01:01","10.10.1.1",101,"10.1.1.101/24","10.1.1.1"], 
	[ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.20.1.1",102,"10.1.1.102/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.30.1.1",103,"10.1.1.103/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.40.1.1",104,"10.1.1.104/24","10.1.1.1"], 
	[ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.50.1.1",105,"10.1.1.105/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.60.1.1",106,"10.1.1.106/24","10.1.1.1"]]


	for switch,ixia_port_info in zip(switches,portList):
		if switch.router_bgp.config_ebgp_ixia(ixia_port_info) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP peers ==============")
			exit()
	 

	myixia = IXIA(apiServerIp,ixChassisIpList,portList)

 	
	for topo in myixia.topologies:
		topo.add_ipv4()
	 
	myixia.topologies[0].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=1000)
	myixia.topologies[1].add_bgp(dut_ip='10.1.1.2',bgp_type='external',num=1000)
	myixia.topologies[2].add_bgp(dut_ip='10.1.1.3',bgp_type='external',num=1000)
	myixia.topologies[3].add_bgp(dut_ip='10.1.1.4',bgp_type='external',num=1000)
	myixia.topologies[4].add_bgp(dut_ip='10.1.1.5',bgp_type='external',num=1000)
	myixia.topologies[5].add_bgp(dut_ip='10.1.1.6',bgp_type='external',num=1000)


	myixia.start_protocol(wait=40)

	myixia.create_traffic(src_topo=myixia.topologies[0].topology, dst_topo=myixia.topologies[1].topology,traffic_name="t1_to_t2",tracking_name="Tracking_1")
	myixia.create_traffic(src_topo=myixia.topologies[1].topology, dst_topo=myixia.topologies[0].topology,traffic_name="t2_to_t1",tracking_name="Tracking_2")

	myixia.create_traffic(src_topo=myixia.topologies[2].topology, dst_topo=myixia.topologies[3].topology,traffic_name="t2_to_t3",tracking_name="Tracking_3")
	myixia.create_traffic(src_topo=myixia.topologies[3].topology, dst_topo=myixia.topologies[2].topology,traffic_name="t3_to_t2",tracking_name="Tracking_4")

	myixia.create_traffic(src_topo=myixia.topologies[4].topology, dst_topo=myixia.topologies[5].topology,traffic_name="t4_to_t5",tracking_name="Tracking_5")
	myixia.create_traffic(src_topo=myixia.topologies[5].topology, dst_topo=myixia.topologies[4].topology,traffic_name="t5_to_t4",tracking_name="Tracking_6")


	myixia.start_traffic()
	myixia.collect_stats()
	myixia.check_traffic()

	for switch in switches:
		switch.show_routing()

	check_bgp_test_result(testcase,description,switches)

if testcase == 6101 or test_all:
	testcase = 6101
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "Basic eBGP IPv6 peered to IXIA and traffic forwarding"
	print_test_subject(testcase,description)

	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	portList_v4_v6 = [
	[ixChassisIpList[0], 2, 11,"00:11:01:01:01:01","10.1.1.211/24","10.1.1.1","2001:10:1:1::211/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.1.1.212/24","10.1.1.1","2001:10:1:1::212/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.1.1.213/24","10.1.1.1","2001:10:1:1::213/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.1.1.214/24","10.1.1.1","2001:10:1:1::214/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.1.1.215/24","10.1.1.1","2001:10:1:1::215/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.1.1.216/24","10.1.1.1","2001:10:1:1::216/64","2001:10:1:1::1",1]
    ]

	if CLEAN_ALL:
		switches_clean_up(switches)
	elif CLEAN_BGP:
		for switch in switches:
			switch.router_bgp.clear_config_all()
	else:
		pass

	ospf_config_v4 = False
	ospf_config_v6 = False
	#Config OSPF infra
	for switch in switches:
		switch.show_switch_info()
		switch.router_ospf.neighbor_discovery_all()
		switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)
		if not switch.router_ospf.ospf_neighbor_all_up_v4(num=OSPF_NEIGHBORS):
			switch.router_ospf.basic_config()
			ospf_config_v4 = True
		else:
			Info(f"All OSPFv4 neighbors are up on switch {switch.loop0_ip}, No need to config OSPF ")
		if not switch.router_ospf.ospf_neighbor_all_up_v6(num=OSPF_NEIGHBORS):
			switch.router_ospf.basic_config_v6()
			ospf_config_v6 = True
		else:
			Info(f"All OSPFv6 neighbors are up on switch {switch.loop0_ip}, No need to config OSPF ")
	if ospf_config_v4 or ospf_config_v6:
		console_timer(20,msg="After building ospfv4 and ospf6 routing infra, wait for 20 sec")
	 

	#update IPv4 and IPv6 ospf neighbors after configuring ospf 
	Info("=============== Updating OSPF Config and Neighbor Information ==========")
	for switch in switches:
		switch.router_ospf.show_ospf_neighbors_all()
		print("----------Discovering ospf neighbor ---------")
		switch.router_ospf.neighbor_discovery_all()
		print("----------Updating ospf neighbor database  ---------")
		switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)

	for switch in switches:  
		switch.router_bgp.config_ibgp_mesh_loopback_v6() 
	console_timer(30,msg="After configuring iBGPv6 sessions via loopbacks, wait for 30s")	 

	for switch in switches:
		switch.router_ospf.show_ospf_neighbors()
		switch.router_bgp.show_bgp_summary()
	
	ixia_ipv6_as_list = [101,102,103,104,105,106]
	i = 0 
	for switch,ixia_port_info,ixia_as in zip(switches,portList_v4_v6,ixia_ipv6_as_list):
		if switch.router_bgp.config_ebgp_ixia_v6(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP peers ==============")
			exit()

	myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)

 	
	for topo in myixia.topologies:
		topo.add_ipv6()

	ipv6_networks = ["2001:101:1:1::1","2001:102:1:1::1","2001:103:1:1::1","2001:104:1:1::211","2001:105:1:1::211","2001:106:1:1::1"]
	i = 1
	for topo,net in zip(myixia.topologies,ipv6_networks):
		topo.bgpv6_network = net
		topo.bgp_as =  100 + i
		i += 1

	i = 0
	for topo in myixia.topologies:
		topo.add_bgp_v6(dut_ip=switches[i].vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=1000)
		i += 1

	myixia.start_protocol(wait=40)

	myixia.create_traffic_v6(src_topo=myixia.topologies[0].topology, dst_topo=myixia.topologies[1].topology,traffic_name="t1_to_t2",tracking_name="Tracking_1")
	myixia.create_traffic_v6(src_topo=myixia.topologies[1].topology, dst_topo=myixia.topologies[0].topology,traffic_name="t2_to_t1",tracking_name="Tracking_2")

	myixia.create_traffic_v6(src_topo=myixia.topologies[2].topology, dst_topo=myixia.topologies[3].topology,traffic_name="t2_to_t3",tracking_name="Tracking_3")
	myixia.create_traffic_v6(src_topo=myixia.topologies[3].topology, dst_topo=myixia.topologies[2].topology,traffic_name="t3_to_t2",tracking_name="Tracking_4")

	myixia.create_traffic_v6(src_topo=myixia.topologies[4].topology, dst_topo=myixia.topologies[5].topology,traffic_name="t4_to_t5",tracking_name="Tracking_5")
	myixia.create_traffic_v6(src_topo=myixia.topologies[5].topology, dst_topo=myixia.topologies[4].topology,traffic_name="t5_to_t4",tracking_name="Tracking_6")


	myixia.start_traffic()
	myixia.collect_stats()
	myixia.check_traffic()

	check_bgp_test_result_v6(testcase,description,switches)


if testcase == 11 or test_all:
	testcase = 11
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "eBGP multi-hop connection"
	print_test_subject(testcase,description)
	if CLEAN_ALL:
		switches_clean_up(switches)
	else:
		for switch in switches:
			switch.router_bgp.clear_config()

	for switch in switches:
		switch.vlan_neighors(switches)
		switch.show_vlan_neighbors()
		switch.router_bgp.config_ebgp_mesh_multihop()
	console_timer(60,msg="After configuring eBGP sessions, wait for 60s")
	for switch in switches:
		switch.show_routing()

	check_bgp_test_result(testcase,description,switches)


if testcase == 6111 or test_all:
	testcase = 6111
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "eBGP multi-hop v6 via loopback interfaces"
	print_test_subject(testcase,description)

	# Clean up configuration before start testing
	if CLEAN_ALL:
		switches_clean_up(switches)
	elif CLEAN_BGP:
		for switch in switches:
			switch.router_bgp.clear_config_all()
	else:
		pass

	ospf_config_v4 = False
	ospf_config_v6 = False
 
	fsw_switches =switches[1:]
	network = BGP_networks(fsw_switches)

	if test_config:
		test_clean_config(switches =fsw_switches)
		test_config_igp_ipv6(switches =fsw_switches)
		console_timer(20,msg=f"Test case {testcase}: After configuring fully mesh iBGP across all IPv6 system interfaces, wait....")
	
	network.show_summary_v6()

	for switch in fsw_switches:
		switch.router_bgp.config_ebgp_mesh_multihop_v6()
	console_timer(60,msg="After configuring eBGP sessions, wait for 60s")
	# for switch in switches:
	# 	switch.show_routing_v6()
	check_bgp_test_result_v6(testcase,description,switches)

if testcase == 6112 or test_all:
	testcase = 6112
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "eBGP multi-hop v4 and v6 via loopback interfaces"
	print_test_subject(testcase,description)

	# Clean up configuration before start testing
	if CLEAN_ALL:
		switches_clean_up(switches)
	elif CLEAN_BGP:
		for switch in switches:
			switch.router_bgp.clear_config_all()
	else:
		pass

	ospf_config_v4 = False
	ospf_config_v6 = False
	#Config OSPF infra
	for switch in switches:
		switch.show_switch_info()
		switch.router_ospf.neighbor_discovery_all()
		switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)
		if not switch.router_ospf.ospf_neighbor_all_up_v4(num=OSPF_NEIGHBORS):
			switch.router_ospf.basic_config()
			ospf_config_v4 = True
		else:
			Info(f"All OSPFv4 neighbors are up on switch {switch.loop0_ip}, No need to config OSPF ")
		if not switch.router_ospf.ospf_neighbor_all_up_v6(num=OSPF_NEIGHBORS):
			switch.router_ospf.basic_config_v6()
			ospf_config_v6 = True
		else:
			Info(f"All OSPFv6 neighbors are up on switch {switch.loop0_ip}, No need to config OSPF ")
	if ospf_config_v4 or ospf_config_v6:
		console_timer(20,msg="After building ospfv4 and ospf6 routing infra, wait for 20 sec")

	#update IPv4 and IPv6 ospf neighbors after configuring ospf 
	Info("=============== Updating OSPF Config and Neighbor Information ==========")
	for switch in switches:
		switch.router_ospf.show_ospf_neighbors_all()
		print("----------Discovering ospf neighbor ---------")
		switch.router_ospf.neighbor_discovery_all()
		print("----------Updating ospf neighbor database  ---------")
		switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)

	for switch in switches:
		switch.router_bgp.config_ebgp_mesh_multihop_v6()
		switch.router_bgp.config_ebgp_mesh_multihop_v4()
	console_timer(60,msg="After configuring eBGP sessions, wait for 60s")
	# for switch in switches:
	# 	switch.show_routing_v6()
	check_bgp_test_result_v6(testcase,description,switches)


if testcase == 12 or test_all:
	testcase = 12
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGP policy and route filtering:duplicated routes were injected from IXIA. "
	print_test_subject(testcase,description)

	if CLEAN_ALL:
		switches_clean_up(switches)
	else:
		for switch in switches:
			switch.router_bgp.clear_config()
	 
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

	portList = [[ixChassisIpList[0], 2,11,"00:11:01:01:01:01","10.10.1.1",101,"10.1.1.101/24","10.1.1.1"], 
	[ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.20.1.1",102,"10.1.1.102/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.30.1.1",103,"10.1.1.103/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.10.1.1",104,"10.1.1.104/24","10.1.1.1"], 
	[ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.20.1.1",105,"10.1.1.105/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.30.1.1",106,"10.1.1.106/24","10.1.1.1"]]


	for switch,ixia_port_info in zip(switches,portList):
		if switch.router_bgp.config_ebgp_ixia(ixia_port_info) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP peers ==============")
			exit()
	 

	myixia = IXIA(apiServerIp,ixChassisIpList,portList)

 	
	for topo in myixia.topologies:
		topo.add_ipv4()
	 
	myixia.topologies[0].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=100)
	myixia.topologies[1].add_bgp(dut_ip='10.1.1.2',bgp_type='external',num=100)
	myixia.topologies[2].add_bgp(dut_ip='10.1.1.3',bgp_type='external',num=100)
	myixia.topologies[3].add_bgp(dut_ip='10.1.1.4',bgp_type='external',num=100)
	myixia.topologies[4].add_bgp(dut_ip='10.1.1.5',bgp_type='external',num=100)
	myixia.topologies[5].add_bgp(dut_ip='10.1.1.6',bgp_type='external',num=100)


	myixia.start_protocol(wait=40)

	check_bgp_test_result(testcase,description,switches)

if testcase == 6121 or test_all:
	testcase = 6121
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGPv6 policy and route filtering:duplicated routes were injected from IXIA."
	print_test_subject(testcase,description)

	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	portList_v4_v6 = [
	[ixChassisIpList[0], 2, 11,"00:11:01:01:01:01","10.1.1.211/24","10.1.1.1","2001:10:1:1::211/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.1.1.212/24","10.1.1.1","2001:10:1:1::212/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.1.1.213/24","10.1.1.1","2001:10:1:1::213/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.1.1.214/24","10.1.1.1","2001:10:1:1::214/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.1.1.215/24","10.1.1.1","2001:10:1:1::215/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.1.1.216/24","10.1.1.1","2001:10:1:1::216/64","2001:10:1:1::1",1]
    ]

	ixia_ipv6_as_list = [101,102,103,104,105,106]
	ipv6_networks = ["2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:102:1:1::211","2001:102:1:1::1","2001:102:1:1::1"]

	my_switches = switches[-2:]
	my_ixia_ports = portList_v4_v6[-2:]
	my_as_lists = ixia_ipv6_as_list[-2:]
	my_ipv6_networks = ipv6_networks[-2:]
	 
	test_clean_config(switches = switches)
	test_config_igp_ipv6(switches = switches)
	test_config_switch2ixia_ipv6(switches=my_switches,ixia_ports=my_ixia_ports,as_lists=my_as_lists)

	myixia = IXIA(apiServerIp,ixChassisIpList,my_ixia_ports)

	# This method is encapsulating the following lines beneath it. Will remove once it is done. 
	test_config_ixia_bgp_v6(myixia,my_ipv6_networks,my_switches,my_as_lists)
	myixia.start_protocol(wait=40)
 
	check_bgp_test_result_v6(testcase,description,switches[-2:])



if testcase == 13 or test_all:
	testcase = 13
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGP policy and route filtering: Origin attribute. "
	print_test_subject(testcase,description)

	# if CLEAN_ALL:
	# 	switches_clean_up(switches)
	# else:
	# 	for switch in switches:
	# 		switch.router_bgp.clear_config()
	 
	# for switch in switches:
	# 	switch.show_switch_info()
	# 	switch.router_ospf.basic_config()
	# console_timer(20,msg="After configuring ospf, wait for 20 sec")

	# for switch in switches:
	# 	switch.router_ospf.neighbor_discovery()
	# 	switch.router_bgp.update_ospf_neighbors()
	# 	switch.router_bgp.config_ibgp_mesh_loopback()

	# console_timer(30,msg="After configuring iBGP sessions via loopbacks, wait for 30s")
	# for switch in switches:
	# 	switch.router_ospf.show_ospf_neighbors()
	# 	switch.router_bgp.show_bgp_summary()

	# for switch,ixia_port_info in zip(switches,portList):
	# 	if switch.router_bgp.config_ebgp_ixia(ixia_port_info) == False:
	# 		tprint("================= !!!!! Not able to configure IXIA BGP peers ==============")
	# 		exit()
		
	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	portList = [[ixChassisIpList[0], 2,11,"00:11:01:01:01:01","10.10.1.1",101,"10.1.1.101/24","10.1.1.1"], 
	[ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.20.1.1",102,"10.1.1.102/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.30.1.1",103,"10.1.1.103/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.10.1.1",104,"10.1.1.104/24","10.1.1.1"], 
	[ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.20.1.1",105,"10.1.1.105/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.30.1.1",106,"10.1.1.106/24","10.1.1.1"]]

	myixia = IXIA(apiServerIp,ixChassisIpList,portList)

	for topo in myixia.topologies:
		topo.add_ipv4()
	 
	myixia.topologies[0].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=100)
	myixia.topologies[1].add_bgp(dut_ip='10.1.1.2',bgp_type='external',num=100)
	myixia.topologies[2].add_bgp(dut_ip='10.1.1.3',bgp_type='external',num=100)
	myixia.topologies[3].add_bgp(dut_ip='10.1.1.4',bgp_type='external',num=100)
	myixia.topologies[4].add_bgp(dut_ip='10.1.1.5',bgp_type='external',num=100)
	myixia.topologies[5].add_bgp(dut_ip='10.1.1.6',bgp_type='external',num=100)

	myixia.topologies[3].change_origin("egp")
	myixia.topologies[4].change_origin("egp")
	myixia.topologies[5].change_origin("egp")
	 

	myixia.start_protocol(wait=40)

	check_bgp_test_result(testcase,description,switches)


if testcase == 6131 or test_all:
	testcase = 6131
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGPv6 policy and route filtering: Origin attribute. "
	print_test_subject(testcase,description)

	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	portList_v4_v6 = [
	[ixChassisIpList[0], 2, 11,"00:11:01:01:01:01","10.1.1.211/24","10.1.1.1","2001:10:1:1::211/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.1.1.212/24","10.1.1.1","2001:10:1:1::212/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.1.1.213/24","10.1.1.1","2001:10:1:1::213/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.1.1.214/24","10.1.1.1","2001:10:1:1::214/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.1.1.215/24","10.1.1.1","2001:10:1:1::215/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.1.1.216/24","10.1.1.1","2001:10:1:1::216/64","2001:10:1:1::1",1]
    ]

	 
	# if CLEAN_ALL:
	# 	switches_clean_up(switches)
	# else:
	# 	for switch in switches:
	# 		switch.router_bgp.clear_config()
	 
	# for switch in switches:
	# 	switch.show_switch_info()
	# 	switch.router_ospf.basic_config()
	# console_timer(20,msg="After configuring ospf, wait for 20 sec")

	# for switch in switches:
	# 	switch.router_ospf.neighbor_discovery()
	# 	switch.router_bgp.update_ospf_neighbors()
	# 	switch.router_bgp.config_ibgp_mesh_loopback()

	# console_timer(30,msg="After configuring iBGP sessions via loopbacks, wait for 30s")
	# for switch in switches:
	# 	switch.router_ospf.show_ospf_neighbors()
	# 	switch.router_bgp.show_bgp_summary()
	
	# for switch,ixia_port_info in zip(switches,portList_v4_v6):
	# 	if switch.router_bgp.config_ebgp_ixia(ixia_port_info) == False:
	# 		tprint("================= !!!!! Not able to configure IXIA BGP peers ==============")
	# 		exit()

	myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)

 	
	for topo in myixia.topologies:
		topo.add_ipv6()

	ipv6_networks = ["2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:102:1:1::211","2001:102:1:1::211","2001:102:1:1::1"]
	i = 1
	for topo,net in zip(myixia.topologies,ipv6_networks):
		topo.bgpv6_network = net
		topo.bgp_as =  100 + i
		i += 1

	i = 0
	for topo in myixia.topologies:
		topo.add_bgp_v6(dut_ip=switches[i].vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=100)
		i += 1
 
	myixia.topologies[3].change_origin_v6("egp")
	myixia.topologies[4].change_origin_v6("egp")
	myixia.topologies[5].change_origin_v6("egp")

	myixia.start_protocol(wait=40)

	myixia.create_traffic_v6(src_topo=myixia.topologies[0].topology, dst_topo=myixia.topologies[1].topology,traffic_name="t1_to_t2",tracking_name="Tracking_1")
	myixia.create_traffic_v6(src_topo=myixia.topologies[1].topology, dst_topo=myixia.topologies[0].topology,traffic_name="t2_to_t1",tracking_name="Tracking_2")

	myixia.create_traffic_v6(src_topo=myixia.topologies[2].topology, dst_topo=myixia.topologies[3].topology,traffic_name="t2_to_t3",tracking_name="Tracking_3")
	myixia.create_traffic_v6(src_topo=myixia.topologies[3].topology, dst_topo=myixia.topologies[2].topology,traffic_name="t3_to_t2",tracking_name="Tracking_4")

	myixia.create_traffic_v6(src_topo=myixia.topologies[4].topology, dst_topo=myixia.topologies[5].topology,traffic_name="t4_to_t5",tracking_name="Tracking_5")
	myixia.create_traffic_v6(src_topo=myixia.topologies[5].topology, dst_topo=myixia.topologies[4].topology,traffic_name="t5_to_t4",tracking_name="Tracking_6")


	myixia.start_traffic()
	myixia.collect_stats()
	myixia.check_traffic()

	check_bgp_test_result_v6(testcase,description,switches)



if testcase == 14 or test_all:
	testcase = 14
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGP policy and route filtering: MED attribute. "
	print_test_subject(testcase,description)

	if CLEAN_ALL:
		switches_clean_up(switches)
	else:
		for switch in switches:
			switch.router_bgp.clear_config()
	 
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

	portList = [[ixChassisIpList[0], 2,11,"00:11:01:01:01:01","10.10.1.1",101,"10.1.1.101/24","10.1.1.1"], 
	[ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.10.1.1",102,"10.1.1.102/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.10.1.1",103,"10.1.1.103/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.10.1.1",104,"10.1.1.104/24","10.1.1.1"], 
	[ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.10.1.1",105,"10.1.1.105/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.10.1.1",106,"10.1.1.106/24","10.1.1.1"]]

	# switch = switches[0]
	# for ixia_port in portList:
	# 	switch.router_bgp.add_ebgp_peer(ip = ixia_port[6],remote_as = ixia_port[5])
	
	 
	myixia = IXIA(apiServerIp,ixChassisIpList,portList)

 	
	for topo in myixia.topologies:
		topo.add_ipv4()
	
	network_numbers = 10
	myixia.topologies[0].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=network_numbers)
	myixia.topologies[1].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=network_numbers)
	myixia.topologies[2].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=network_numbers)
	myixia.topologies[3].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=network_numbers)
	myixia.topologies[4].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=network_numbers)
	myixia.topologies[5].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=network_numbers)

	# !!!!!!!!!!There could be a bug in IXIA where the first line of the following is NOT excuted
	myixia.topologies[0].change_med(1000)
	myixia.topologies[1].change_med(2000)
	myixia.topologies[2].change_med(3000)
	myixia.topologies[3].change_med(4000)
	myixia.topologies[4].change_med(5000)
	myixia.topologies[5].change_med(6000)
	#myixia.topologies[0].change_med(1000)
	 

	myixia.start_protocol(wait=40)

	check_bgp_test_result(testcase,description,switches)

 
if testcase == 6140 or test_all:
	testcase = 6140
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGPv6 Best Routes Selection: Router ID and Next Hop. eBGP path with smallest MED will be elected "
	print_test_subject(testcase,description)

	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	portList_v4_v6 = [
	[ixChassisIpList[0], 2, 11,"00:11:01:01:01:01","10.1.1.211/24","10.1.1.1","2001:10:1:1::211/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.1.1.212/24","10.1.1.1","2001:10:1:1::212/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.1.1.213/24","10.1.1.1","2001:10:1:1::213/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.1.1.214/24","10.1.1.1","2001:10:1:1::214/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.1.1.215/24","10.1.1.1","2001:10:1:1::215/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.1.1.216/24","10.1.1.1","2001:10:1:1::216/64","2001:10:1:1::1",1]
    ]
	
	ixia_ipv6_as_list = [101,102,103,104,105,106]
	ipv6_networks = ["2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:102:1:1::1","2001:102:1:1::1"]
	ipv4_networks = ["10.10.0.1","10.10.0.1","10.10.1.1","10.10.1.1","10.10.2.1","10.10.2.1"]

	cisco_switch = switches[0]
	sw6_switch = switches[-1]
	my_ixia_ports = portList_v4_v6[-4:]

	sw6_ixia_ports = portList_v4_v6[-2:]
	sw6_as_lists = ixia_ipv6_as_list[-2:]
	sw6_ipv6_networks = ipv6_networks[-2:]
	sw6_ipv4_networks = ipv4_networks[-2:]


	cisco_ixia_ports = portList_v4_v6[-4:-2]
	cisco_as_lists = ixia_ipv6_as_list[-4:-2]
	cisco_ipv6_networks = ipv6_networks[-4:-2]
	cisco_ipv4_networks = ipv4_networks[-4:-2]

	fsw_switches =switches[1:]
	network = BGP_networks(fsw_switches)

	if test_config:
		test_clean_config(switches =fsw_switches)
		test_config_igp_ipv6(switches =fsw_switches)
		network.biuld_ibgp_mesh_topo_sys_intf_v6()
		test_config_single_switch2ixia_all(switch=sw6_switch,ixia_ports=sw6_ixia_ports,as_lists=sw6_as_lists)
		console_timer(20,msg=f"Test case {testcase}: After configuring fully mesh iBGP across all IPv6 system interfaces, wait....")
	
	network.show_summary_v6()
	test_config_single_switch2ixia_all(switch=sw6_switch,ixia_ports=sw6_ixia_ports,as_lists=sw6_as_lists)

	myixia = IXIA(apiServerIp,ixChassisIpList,my_ixia_ports)

	test_config_ixia_bgp_all_one_switch_compare(myixia.topologies[:2],cisco_ipv6_networks,cisco_ipv4_networks,cisco_switch,cisco_as_lists)
	test_config_ixia_bgp_all_one_switch_compare(myixia.topologies[-2:],sw6_ipv6_networks,sw6_ipv4_networks,sw6_switch,sw6_as_lists)

	myixia.start_protocol(wait=40)

	check_bgp_test_result_v6(testcase,description,sw6_switch)

if testcase == 6141 or test_all:
	testcase = 6141
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGPv6 Best Routes Selection: MED. eBGP path with smallest MED will be elected "
	print_test_subject(testcase,description)

	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	portList_v4_v6 = [
	[ixChassisIpList[0], 2, 11,"00:11:01:01:01:01","10.1.1.211/24","10.1.1.1","2001:10:1:1::211/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.1.1.212/24","10.1.1.1","2001:10:1:1::212/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.1.1.213/24","10.1.1.1","2001:10:1:1::213/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.1.1.214/24","10.1.1.1","2001:10:1:1::214/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.1.1.215/24","10.1.1.1","2001:10:1:1::215/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.1.1.216/24","10.1.1.1","2001:10:1:1::216/64","2001:10:1:1::1",1]
    ]
	
	ixia_ipv6_as_list = [101,102,103,104,105,106]
	ipv6_networks = ["2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:102:1:1::1","2001:102:1:1::1"]
	ipv4_networks = ["10.10.0.1","10.10.0.1","10.10.1.1","10.10.1.1","10.10.2.1","10.10.2.1"]

	# my_switches = switches[-2:]
	# my_ixia_ports = portList_v4_v6[-2:]
	# my_as_lists = ixia_ipv6_as_list[-2:]
	# my_ipv6_networks = ipv6_networks[-2:]
	# my_ipv4_networks = ipv4_networks[-2:]
	 
	# myixia = IXIA(apiServerIp,ixChassisIpList,my_ixia_ports)

	# # This method is encapsulating the following lines beneath it. Will remove once it is done. 
	# test_config_ixia_bgp_all(myixia,my_ipv6_networks,my_ipv4_networks,my_switches,my_as_lists)
	cisco_switch = switches[0]
	sw6_switch = switches[-1]
	my_ixia_ports = portList_v4_v6[-4:]

	sw6_ixia_ports = portList_v4_v6[-2:]
	sw6_as_lists = ixia_ipv6_as_list[-2:]
	sw6_ipv6_networks = ipv6_networks[-2:]
	sw6_ipv4_networks = ipv4_networks[-2:]


	cisco_ixia_ports = portList_v4_v6[-4:-2]
	cisco_as_lists = ixia_ipv6_as_list[-4:-2]
	cisco_ipv6_networks = ipv6_networks[-4:-2]
	cisco_ipv4_networks = ipv4_networks[-4:-2]

	fsw_switches =switches[1:]
	network = BGP_networks(fsw_switches)

	if test_config:
		test_clean_config(switches =fsw_switches)
		test_config_igp_ipv6(switches =fsw_switches)
		network.biuld_ibgp_mesh_topo_sys_intf_v6()
		test_config_single_switch2ixia_all(switch=sw6_switch,ixia_ports=sw6_ixia_ports,as_lists=sw6_as_lists)
		console_timer(20,msg=f"Test case {testcase}: After configuring fully mesh iBGP across all IPv6 system interfaces, wait....")
	
	network.show_summary_v6()
	test_config_single_switch2ixia_all(switch=sw6_switch,ixia_ports=sw6_ixia_ports,as_lists=sw6_as_lists)

	myixia = IXIA(apiServerIp,ixChassisIpList,my_ixia_ports)

	test_config_ixia_bgp_all_one_switch_compare(myixia.topologies[:2],cisco_ipv6_networks,cisco_ipv4_networks,cisco_switch,cisco_as_lists)
	test_config_ixia_bgp_all_one_switch_compare(myixia.topologies[-2:],sw6_ipv6_networks,sw6_ipv4_networks,sw6_switch,sw6_as_lists)

	myixia.topologies[0].change_bgp_routes_attributes(med=6111,address_family="v6")
	myixia.topologies[1].change_bgp_routes_attributes(med=6222,address_family="v6")
	myixia.topologies[2].change_bgp_routes_attributes(med=6333,address_family="v6")
	myixia.topologies[3].change_bgp_routes_attributes(med=6444,address_family="v6")

	myixia.topologies[0].change_bgp_routes_attributes(med=4111,address_family="v4")
	myixia.topologies[1].change_bgp_routes_attributes(med=4222,address_family="v4")
	myixia.topologies[2].change_bgp_routes_attributes(med=4333,address_family="v4")
	myixia.topologies[3].change_bgp_routes_attributes(med=4444,address_family="v4")

	myixia.start_protocol(wait=40)

	check_bgp_test_result_v6(testcase,description,sw6_switch)

if testcase == 6142 or test_all:
	testcase = 6142
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGPv6 Best Routes Selection: Origin. Run the test at the last 2 switches: switches[-2:] "
	print_test_subject(testcase,description)

	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	portList_v4_v6 = [
	[ixChassisIpList[0], 2, 11,"00:11:01:01:01:01","10.1.1.211/24","10.1.1.1","2001:10:1:1::211/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.1.1.212/24","10.1.1.1","2001:10:1:1::212/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.1.1.213/24","10.1.1.1","2001:10:1:1::213/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.1.1.214/24","10.1.1.1","2001:10:1:1::214/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.1.1.215/24","10.1.1.1","2001:10:1:1::215/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.1.1.216/24","10.1.1.1","2001:10:1:1::216/64","2001:10:1:1::1",1]
    ]
	
	ixia_ipv6_as_list = [101,102,103,104,105,106]
	ipv6_networks = ["2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:102:1:1::211","2001:102:1:1::1","2001:102:1:1::1"]
	ipv4_networks = ["10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1","10.10.2.1","10.10.2.1"]

	# my_switches = switches[-2:]
	# my_ixia_ports = portList_v4_v6[-2:]
	# my_as_lists = ixia_ipv6_as_list[-2:]
	# my_ipv6_networks = ipv6_networks[-2:]
	# my_ipv4_networks = ipv4_networks[-2:]

	# test_clean_config(switches = switches)
	# test_config_igp_ipv6(switches = switches)
	# test_config_single_switch2ixia_all(switch=my_switch,ixia_ports=my_ixia_ports,as_lists=my_as_lists)
	 
	# test_config_igp_ipv6(switches = switches)
	# test_config_switch2ixia_all(switches=my_switches,ixia_ports=my_ixia_ports,as_lists=my_as_lists)

	# myixia = IXIA(apiServerIp,ixChassisIpList,my_ixia_ports)

	# # This method is encapsulating the following lines beneath it. Will remove once it is done. 
	# test_config_ixia_bgp_all(myixia,my_ipv6_networks,my_ipv4_networks,my_switches,my_as_lists)

	cisco_switch = switches[0]
	sw6_switch = switches[-1]
	my_ixia_ports = portList_v4_v6[-4:]

	sw6_ixia_ports = portList_v4_v6[-2:]
	sw6_as_lists = ixia_ipv6_as_list[-2:]
	sw6_ipv6_networks = ipv6_networks[-2:]
	sw6_ipv4_networks = ipv4_networks[-2:]


	cisco_ixia_ports = portList_v4_v6[-4:-2]
	cisco_as_lists = ixia_ipv6_as_list[-4:-2]
	cisco_ipv6_networks = ipv6_networks[-4:-2]
	cisco_ipv4_networks = ipv4_networks[-4:-2]

	fsw_switches =switches[1:]
	network = BGP_networks(fsw_switches)

	if test_config:
		test_clean_config(switches =fsw_switches)
		test_config_igp_ipv6(switches =fsw_switches)
		network.biuld_ibgp_mesh_topo_sys_intf_v6()
		test_config_single_switch2ixia_all(switch=sw6_switch,ixia_ports=sw6_ixia_ports,as_lists=sw6_as_lists)
		console_timer(20,msg=f"Test case {testcase}: After configuring fully mesh iBGP across all IPv6 system interfaces, wait....")
	
	network.show_summary_v6()
	test_config_single_switch2ixia_all(switch=sw6_switch,ixia_ports=sw6_ixia_ports,as_lists=sw6_as_lists)

	myixia = IXIA(apiServerIp,ixChassisIpList,my_ixia_ports)

	test_config_ixia_bgp_all_one_switch_compare(myixia.topologies[:2],cisco_ipv6_networks,cisco_ipv4_networks,cisco_switch,cisco_as_lists)
	test_config_ixia_bgp_all_one_switch_compare(myixia.topologies[-2:],sw6_ipv6_networks,sw6_ipv4_networks,sw6_switch,sw6_as_lists)

	myixia.topologies[0].change_bgp_routes_attributes(origin="egp",address_family="v6")
	myixia.topologies[1].change_bgp_routes_attributes(origin="incomplete",address_family="v6")
	myixia.topologies[2].change_bgp_routes_attributes(origin="egp",address_family="v6")
	myixia.topologies[3].change_bgp_routes_attributes(origin="incomplete",address_family="v6")
	myixia.topologies[0].change_bgp_routes_attributes(origin="egp",address_family="v4")
	myixia.topologies[1].change_bgp_routes_attributes(origin="incomplete",address_family="v4")
	myixia.topologies[2].change_bgp_routes_attributes(origin="egp",address_family="v4")
	myixia.topologies[3].change_bgp_routes_attributes(origin="incomplete",address_family="v4")


	myixia.topologies[0].change_bgp_routes_attributes_v6(origin="egp",address_family="v6")
	myixia.topologies[1].change_bgp_routes_attributes_v6(origin="incomplete",address_family="v6")
	myixia.topologies[2].change_bgp_routes_attributes_v6(origin="egp",address_family="v6")
	myixia.topologies[3].change_bgp_routes_attributes_v6(origin="incomplete",address_family="v6")
	myixia.topologies[0].change_bgp_routes_attributes_v6(origin="egp",address_family="v4")
	myixia.topologies[1].change_bgp_routes_attributes_v6(origin="incomplete",address_family="v4")
	myixia.topologies[2].change_bgp_routes_attributes_v6(origin="egp",address_family="v4")
	myixia.topologies[3].change_bgp_routes_attributes_v6(origin="incomplete",address_family="v4")

	myixia.start_protocol(wait=40)

	check_bgp_test_result_v6(testcase,description,switches[-2:])


if testcase == 6143 or test_all:
	testcase = 6143
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGPv6 Best Routes Selection: Weight. Run the test at the last switch: switches[-1] "
	print_test_subject(testcase,description)

	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	portList_v4_v6 = [
	[ixChassisIpList[0], 2, 11,"00:11:01:01:01:01","10.1.1.211/24","10.1.1.1","2001:10:1:1::211/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.1.1.212/24","10.1.1.1","2001:10:1:1::212/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.1.1.213/24","10.1.1.1","2001:10:1:1::213/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.1.1.214/24","10.1.1.1","2001:10:1:1::214/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.1.1.215/24","10.1.1.1","2001:10:1:1::215/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.1.1.216/24","10.1.1.1","2001:10:1:1::216/64","2001:10:1:1::1",1]
    ]
	
	ixia_ipv6_as_list = [101,102,103,104,105,106]
	ipv6_networks = ["2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:102:1:1::211","2001:102:1:1::1","2001:102:1:1::1"]
	ipv4_networks = ["10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1","10.10.2.1","10.10.2.1"]

	cisco_switch = switches[0]
	sw6_switch = switches[-1]
	my_ixia_ports = portList_v4_v6[-4:]
	# my_as_lists = ixia_ipv6_as_list[-4:]
	# my_ipv6_networks = ipv6_networks[-4:]
	# my_ipv4_networks = ipv4_networks[-4:]

	sw6_ixia_ports = portList_v4_v6[-2:]
	sw6_as_lists = ixia_ipv6_as_list[-2:]
	sw6_ipv6_networks = ipv6_networks[-2:]
	sw6_ipv4_networks = ipv4_networks[-2:]


	cisco_ixia_ports = portList_v4_v6[-4:-2]
	cisco_as_lists = ixia_ipv6_as_list[-4:-2]
	cisco_ipv6_networks = ipv6_networks[-4:-2]
	cisco_ipv4_networks = ipv4_networks[-4:-2]

	fsw_switches =switches[1:]
	network = BGP_networks(fsw_switches)

	if test_config:
		test_clean_config(switches =fsw_switches)
		test_config_igp_ipv6(switches =fsw_switches)
		network.biuld_ibgp_mesh_topo_sys_intf_v6()
		test_config_single_switch2ixia_all(switch=sw6_switch,ixia_ports=sw6_ixia_ports,as_lists=sw6_as_lists)
		console_timer(20,msg=f"Test case {testcase}: After configuring fully mesh iBGP across all IPv6 system interfaces, wait....")
	
	network.show_summary_v6()
	test_config_single_switch2ixia_all(switch=sw6_switch,ixia_ports=sw6_ixia_ports,as_lists=sw6_as_lists)

	myixia = IXIA(apiServerIp,ixChassisIpList,my_ixia_ports)
 
	#test_config_ixia_bgp_all_one_switch_cisco(myixia,sw6_ipv6_networks,sw6_ipv4_networks,sw6_switch,sw6_as_lists,cisco_ipv6_networks,cisco_ipv4_networks,cisco_switch,cisco_as_lists)
	test_config_ixia_bgp_all_one_switch_compare(myixia.topologies[:2],cisco_ipv6_networks,cisco_ipv4_networks,cisco_switch,cisco_as_lists)
	test_config_ixia_bgp_all_one_switch_compare(myixia.topologies[-2:],sw6_ipv6_networks,sw6_ipv4_networks,sw6_switch,sw6_as_lists)

	myixia.topologies[0].change_bgp_routes_attributes(weight=6111,address_family="v6")
	myixia.topologies[1].change_bgp_routes_attributes(weight=6222,address_family="v6")
	myixia.topologies[2].change_bgp_routes_attributes(weight=6333,address_family="v6")
	myixia.topologies[3].change_bgp_routes_attributes(weight=6444,address_family="v6")

	myixia.topologies[0].change_bgp_routes_attributes(weight=4111,address_family="v4")
	myixia.topologies[1].change_bgp_routes_attributes(weight=4222,address_family="v4")
	myixia.topologies[2].change_bgp_routes_attributes(weight=4333,address_family="v4")
	myixia.topologies[3].change_bgp_routes_attributes(weight=4444,address_family="v4")

	myixia.topologies[0].change_bgp_routes_attributes_v6(weight=6111,address_family="v6")
	myixia.topologies[1].change_bgp_routes_attributes_v6(weight=6222,address_family="v6")
	myixia.topologies[2].change_bgp_routes_attributes_v6(weight=6333,address_family="v6")
	myixia.topologies[3].change_bgp_routes_attributes_v6(weight=6444,address_family="v6")

	myixia.topologies[0].change_bgp_routes_attributes_v6(weight=4111,address_family="v4")
	myixia.topologies[1].change_bgp_routes_attributes_v6(weight=4222,address_family="v4")
	myixia.topologies[2].change_bgp_routes_attributes_v6(weight=4333,address_family="v4")
	myixia.topologies[3].change_bgp_routes_attributes_v6(weight=4444,address_family="v4")


	myixia.start_protocol(wait=40)

	check_bgp_test_result_v6(testcase,description,sw6_switch)

if testcase == 6144 or test_all:
	testcase = 6144
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGPv6 Best Routes Selection: Local Preference. Run the test at the last switch: switches[-1] "
	print_test_subject(testcase,description)

	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	portList_v4_v6 = [
	[ixChassisIpList[0], 2, 11,"00:11:01:01:01:01","10.1.1.211/24","10.1.1.1","2001:10:1:1::211/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.1.1.212/24","10.1.1.1","2001:10:1:1::212/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.1.1.213/24","10.1.1.1","2001:10:1:1::213/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.1.1.214/24","10.1.1.1","2001:10:1:1::214/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.1.1.215/24","10.1.1.1","2001:10:1:1::215/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.1.1.216/24","10.1.1.1","2001:10:1:1::216/64","2001:10:1:1::1",1]
    ]
	
	ixia_ipv6_as_list = [101,102,103,104,105,106]
	ipv6_networks = ["2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:102:1:1::1","2001:102:1:1::1"]
	ipv4_networks = ["10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1","10.10.2.1","10.10.2.1"]

	cisco_switch = switches[0]
	sw6_switch = switches[-1]
	my_ixia_ports = portList_v4_v6[-4:]
	

	sw6_ixia_ports = portList_v4_v6[-2:]
	sw6_as_lists = ixia_ipv6_as_list[-2:]
	sw6_ipv6_networks = ipv6_networks[-2:]
	sw6_ipv4_networks = ipv4_networks[-2:]


	cisco_ixia_ports = portList_v4_v6[-4:-2]
	cisco_as_lists = ixia_ipv6_as_list[-4:-2]
	cisco_ipv6_networks = ipv6_networks[-4:-2]
	cisco_ipv4_networks = ipv4_networks[-4:-2]

	fsw_switches =switches[1:]
	network = BGP_networks(switches)

	if test_config:
		test_clean_config(switches =fsw_switches)
		test_config_igp_ipv6(switches =fsw_witches)
		network.biuld_ibgp_mesh_topo_sys_intf_v6()
		network.biuld_ibgp_mesh_topo_sys_intf()
		console_timer(20,msg=f"Test case {testcase}: After configuring fully mesh iBGP across all IPv6 system interfaces, wait....")
	network.show_summary_v6()

	#This has to be iBGP to compare local preference
	test_config_single_switch2ixia_all(switch=sw6_switch,ixia_ports=sw6_ixia_ports,as_lists=sw6_as_lists,protocol="ibgp")

	myixia = IXIA(apiServerIp,ixChassisIpList,my_ixia_ports)

	test_config_ixia_ibgp_all_one_switch_compare(myixia.topologies[:2],cisco_ipv6_networks,cisco_ipv4_networks,cisco_switch,cisco_as_lists)
	test_config_ixia_ibgp_all_one_switch_compare(myixia.topologies[-2:],sw6_ipv6_networks,sw6_ipv4_networks,sw6_switch,sw6_as_lists)

	myixia.topologies[0].change_bgp_routes_attributes(local=610,address_family="v6")
	myixia.topologies[1].change_bgp_routes_attributes(local=620,address_family="v6")
	myixia.topologies[2].change_bgp_routes_attributes(local=630,address_family="v6")
	myixia.topologies[3].change_bgp_routes_attributes(local=640,address_family="v6")


	myixia.topologies[0].change_bgp_routes_attributes(local=410,address_family="v4")
	myixia.topologies[1].change_bgp_routes_attributes(local=420,address_family="v4")
	myixia.topologies[2].change_bgp_routes_attributes(local=430,address_family="v4")
	myixia.topologies[3].change_bgp_routes_attributes(local=440,address_family="v4")


	# myixia.topologies[0].change_bgp_routes_attributes_v6(local=610,address_family="v6")
	# myixia.topologies[1].change_bgp_routes_attributes_v6(local=620,address_family="v6")
	# myixia.topologies[2].change_bgp_routes_attributes_v6(local=630,address_family="v6")
	# myixia.topologies[3].change_bgp_routes_attributes_v6(local=640,address_family="v6")

	# myixia.topologies[0].change_bgp_routes_attributes_v6(local=410,address_family="v4")
	# myixia.topologies[1].change_bgp_routes_attributes_v6(local=420,address_family="v4")
	# myixia.topologies[2].change_bgp_routes_attributes_v6(local=430,address_family="v4")
	# myixia.topologies[3].change_bgp_routes_attributes_v6(local=440,address_family="v4")

	myixia.start_protocol(wait=40)

	check_bgp_test_result_v6(testcase,description,sw6_switch)

if testcase == 6145 or test_all:
	testcase = 6145
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGPv6 Best Routes Selection: Community. Run the test at the last switch: switches[-1] "
	print_test_subject(testcase,description)

	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	portList_v4_v6 = [
	[ixChassisIpList[0], 2, 11,"00:11:01:01:01:01","10.1.1.211/24","10.1.1.1","2001:10:1:1::211/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.1.1.212/24","10.1.1.1","2001:10:1:1::212/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.1.1.213/24","10.1.1.1","2001:10:1:1::213/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.1.1.214/24","10.1.1.1","2001:10:1:1::214/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.1.1.215/24","10.1.1.1","2001:10:1:1::215/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.1.1.216/24","10.1.1.1","2001:10:1:1::216/64","2001:10:1:1::1",1]
    ]

	ixia_ipv6_as_list = [101,102,103,104,105,106]
	ipv6_networks = ["2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:102:1:1::1","2001:102:1:1::1"]
	ipv4_networks = ["10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1","10.10.2.1","10.10.2.1"]

	cisco_switch = switches[0]
	sw6_switch = switches[-1]
	my_ixia_ports = portList_v4_v6[-4:]
	

	sw6_ixia_ports = portList_v4_v6[-2:]
	sw6_as_lists = ixia_ipv6_as_list[-2:]
	sw6_ipv6_networks = ipv6_networks[-2:]
	sw6_ipv4_networks = ipv4_networks[-2:]


	cisco_ixia_ports = portList_v4_v6[-4:-2]
	cisco_as_lists = ixia_ipv6_as_list[-4:-2]
	cisco_ipv6_networks = ipv6_networks[-4:-2]
	cisco_ipv4_networks = ipv4_networks[-4:-2]

	fsw_switches =switches[1:]
	network = BGP_networks(fsw_switches)

	if test_config:
		test_clean_config(switches =fsw_switches)
		test_config_igp_ipv6(switches =fsw_switches)
		network.biuld_ibgp_mesh_topo_sys_intf_v6()
		network.biuld_ibgp_mesh_topo_sys_intf()
	
		console_timer(20,msg=f"Test case {testcase}: After configuring fully mesh iBGP across all IPv6 system interfaces, wait....")
	
	network.show_summary_v6()

	test_config_single_switch2ixia_all(switch=sw6_switch,ixia_ports=sw6_ixia_ports,as_lists=sw6_as_lists)

	myixia = IXIA(apiServerIp,ixChassisIpList,my_ixia_ports)

	test_config_ixia_bgp_all_one_switch_compare(myixia.topologies[:2],cisco_ipv6_networks,cisco_ipv4_networks,cisco_switch,cisco_as_lists)
	test_config_ixia_bgp_all_one_switch_compare(myixia.topologies[-2:],sw6_ipv6_networks,sw6_ipv4_networks,sw6_switch,sw6_as_lists)


	myixia.topologies[0].change_bgp_routes_attributes(community=6,comm_base=6100,address_family="v6")
	myixia.topologies[1].change_bgp_routes_attributes(community=5,comm_base=6200,address_family="v6")
	myixia.topologies[2].change_bgp_routes_attributes(community=6,comm_base=6300,address_family="v6")
	myixia.topologies[3].change_bgp_routes_attributes(community=5,comm_base=6400,address_family="v6")

	myixia.topologies[0].change_bgp_routes_attributes(community=4,comm_base=4100,address_family="v4")
	myixia.topologies[1].change_bgp_routes_attributes(community=3,comm_base=4200,address_family="v4")
	myixia.topologies[2].change_bgp_routes_attributes(community=4,comm_base=4300,address_family="v4")
	myixia.topologies[3].change_bgp_routes_attributes(community=3,comm_base=4400,address_family="v4")

	myixia.topologies[0].change_bgp_routes_attributes_v6(community=6,comm_base=6100,address_family="v6")
	myixia.topologies[1].change_bgp_routes_attributes_v6(community=5,comm_base=6200,address_family="v6")
	myixia.topologies[2].change_bgp_routes_attributes_v6(community=6,comm_base=6300,address_family="v6")
	myixia.topologies[3].change_bgp_routes_attributes_v6(community=5,comm_base=6400,address_family="v6")

	myixia.topologies[0].change_bgp_routes_attributes_v6(community=4,comm_base=4100,address_family="v4")
	myixia.topologies[1].change_bgp_routes_attributes_v6(community=3,comm_base=4200,address_family="v4")
	myixia.topologies[2].change_bgp_routes_attributes_v6(community=4,comm_base=4300,address_family="v4")
	myixia.topologies[3].change_bgp_routes_attributes_v6(community=3,comm_base=4400,address_family="v4")
	 
	myixia.start_protocol(wait=40)

	check_bgp_test_result_v6(testcase,description,sw6_switch)


if testcase == 6146 or test_all:
	testcase = 6146
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGPv6 Best Routes Selection: AS Path. Run the test at the last switch: switches[-1] "
	print_test_subject(testcase,description)

	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	portList_v4_v6 = [
	[ixChassisIpList[0], 2, 11,"00:11:01:01:01:01","10.1.1.211/24","10.1.1.1","2001:10:1:1::211/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.1.1.212/24","10.1.1.1","2001:10:1:1::212/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.1.1.213/24","10.1.1.1","2001:10:1:1::213/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.1.1.214/24","10.1.1.1","2001:10:1:1::214/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.1.1.215/24","10.1.1.1","2001:10:1:1::215/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.1.1.216/24","10.1.1.1","2001:10:1:1::216/64","2001:10:1:1::1",1]
    ]
	
	ixia_ipv6_as_list = [101,102,103,104,105,106]
	ipv6_networks = ["2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:102:1:1::1","2001:102:1:1::1"]
	ipv4_networks = ["10.10.1.1","10.10.1.1","10.10.1.1","10.10.2.1","10.10.2.1","10.10.2.1"]

	cisco_switch = switches[0]
	sw6_switch = switches[-1]
	my_ixia_ports = portList_v4_v6[-4:]
	

	sw6_ixia_ports = portList_v4_v6[-2:]
	sw6_as_lists = ixia_ipv6_as_list[-2:]
	sw6_ipv6_networks = ipv6_networks[-2:]
	sw6_ipv4_networks = ipv4_networks[-2:]


	cisco_ixia_ports = portList_v4_v6[-4:-2]
	cisco_as_lists = ixia_ipv6_as_list[-4:-2]
	cisco_ipv6_networks = ipv6_networks[-4:-2]
	cisco_ipv4_networks = ipv4_networks[-4:-2]

	fsw_switches =switches[1:]
	network = BGP_networks(fsw_switches)

	if test_config:
		test_clean_config(switches =fsw_switches)
		test_config_igp_ipv6(switches =fsw_switches)
		network.biuld_ibgp_mesh_topo_sys_intf_v6()
		console_timer(20,msg=f"Test case {testcase}: After configuring fully mesh iBGP across all IPv6 system interfaces, wait....")
	
	network.show_summary_v6()

	test_config_single_switch2ixia_all(switch=sw6_switch,ixia_ports=sw6_ixia_ports,as_lists=sw6_as_lists)


	myixia = IXIA(apiServerIp,ixChassisIpList,my_ixia_ports)

	test_config_ixia_bgp_all_one_switch_compare(myixia.topologies[:2],cisco_ipv6_networks,cisco_ipv4_networks,cisco_switch,cisco_as_lists)
	test_config_ixia_bgp_all_one_switch_compare(myixia.topologies[-2:],sw6_ipv6_networks,sw6_ipv4_networks,sw6_switch,sw6_as_lists)

	myixia.topologies[0].change_bgp_routes_attributes(num_path=6,as_base=65010,address_family="v6")
	myixia.topologies[1].change_bgp_routes_attributes(num_path=5,as_base=65020,address_family="v6")
	myixia.topologies[2].change_bgp_routes_attributes(num_path=6,as_base=65030,address_family="v6")
	myixia.topologies[3].change_bgp_routes_attributes(num_path=5,as_base=65040,address_family="v6")

	myixia.topologies[0].change_bgp_routes_attributes(num_path=4,as_base=64010,address_family="v4")
	myixia.topologies[1].change_bgp_routes_attributes(num_path=3,as_base=64020,address_family="v4")
	myixia.topologies[2].change_bgp_routes_attributes(num_path=4,as_base=64030,address_family="v4")
	myixia.topologies[3].change_bgp_routes_attributes(num_path=3,as_base=64040,address_family="v4")


	myixia.topologies[0].change_bgp_routes_attributes_v6(num_path=6,as_base=65010,address_family="v6")
	myixia.topologies[1].change_bgp_routes_attributes_v6(num_path=5,as_base=65020,address_family="v6")
	myixia.topologies[2].change_bgp_routes_attributes_v6(num_path=6,as_base=65030,address_family="v6")
	myixia.topologies[3].change_bgp_routes_attributes_v6(num_path=5,as_base=65040,address_family="v6")
	myixia.topologies[0].change_bgp_routes_attributes_v6(num_path=4,as_base=64010,address_family="v4")
	myixia.topologies[1].change_bgp_routes_attributes_v6(num_path=3,as_base=64020,address_family="v4")
	myixia.topologies[2].change_bgp_routes_attributes_v6(num_path=4,as_base=64030,address_family="v4")
	myixia.topologies[3].change_bgp_routes_attributes_v6(num_path=3,as_base=64040,address_family="v4")
	 
	myixia.start_protocol(wait=40)

	check_bgp_test_result_v6(testcase,description,sw6_switch)

if testcase == 6147 or test_all:
	testcase = 6147
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGPv6 Best Routes Selection: Aggreator. Run the test at the last switch: switches[-1] "
	print_test_subject(testcase,description)

	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	portList_v4_v6 = [
	[ixChassisIpList[0], 2, 11,"00:11:01:01:01:01","10.1.1.211/24","10.1.1.1","2001:10:1:1::211/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.1.1.212/24","10.1.1.1","2001:10:1:1::212/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.1.1.213/24","10.1.1.1","2001:10:1:1::213/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.1.1.214/24","10.1.1.1","2001:10:1:1::214/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.1.1.215/24","10.1.1.1","2001:10:1:1::215/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.1.1.216/24","10.1.1.1","2001:10:1:1::216/64","2001:10:1:1::1",1]
    ]
	
	ixia_ipv6_as_list = [101,102,103,104,105,106]
	ipv6_networks = ["2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:102:1:1::1","2001:102:1:1::1"]
	ipv4_networks = ["10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1","10.10.2.1","10.10.2.1"]

	cisco_switch = switches[0]
	sw6_switch = switches[-1]
	my_ixia_ports = portList_v4_v6[-4:]
	

	sw6_ixia_ports = portList_v4_v6[-2:]
	sw6_as_lists = ixia_ipv6_as_list[-2:]
	sw6_ipv6_networks = ipv6_networks[-2:]
	sw6_ipv4_networks = ipv4_networks[-2:]


	cisco_ixia_ports = portList_v4_v6[-4:-2]
	cisco_as_lists = ixia_ipv6_as_list[-4:-2]
	cisco_ipv6_networks = ipv6_networks[-4:-2]
	cisco_ipv4_networks = ipv4_networks[-4:-2]

	fsw_switches =switches[1:]
	network = BGP_networks(fsw_switches)


	if test_config:
		test_clean_config(switches =fsw_switches)
		test_config_igp_ipv6(switches =fsw_switches)
		network.biuld_ibgp_mesh_topo_sys_intf_v6()
		console_timer(20,msg=f"Test case {testcase}: After configuring fully mesh iBGP across all IPv6 system interfaces, wait....")
	
	network.show_summary_v6()

	test_config_single_switch2ixia_all(switch=sw6_switch,ixia_ports=sw6_ixia_ports,as_lists=sw6_as_lists)

	myixia = IXIA(apiServerIp,ixChassisIpList,my_ixia_ports)

	test_config_ixia_bgp_all_one_switch_compare(myixia.topologies[:2],cisco_ipv6_networks,cisco_ipv4_networks,cisco_switch,cisco_as_lists)
	test_config_ixia_bgp_all_one_switch_compare(myixia.topologies[-2:],sw6_ipv6_networks,sw6_ipv4_networks,sw6_switch,sw6_as_lists)

	myixia.topologies[0].change_bgp_routes_attributes(aggregator="106.106.106.106",aggregator_as=66660,address_family="v6")
	myixia.topologies[1].change_bgp_routes_attributes(aggregator="106.106.106.107",aggregator_as=66661,address_family="v6")
	myixia.topologies[2].change_bgp_routes_attributes(aggregator="106.106.106.108",aggregator_as=66662,address_family="v6")
	myixia.topologies[3].change_bgp_routes_attributes(aggregator="106.106.106.109",aggregator_as=66663,address_family="v6")

	myixia.topologies[0].change_bgp_routes_attributes(aggregator="104.104.104.104",aggregator_as=44440,address_family="v4")
	myixia.topologies[1].change_bgp_routes_attributes(aggregator="104.104.104.105",aggregator_as=44441,address_family="v4")
	myixia.topologies[2].change_bgp_routes_attributes(aggregator="104.104.104.105",aggregator_as=44442,address_family="v4")
	myixia.topologies[3].change_bgp_routes_attributes(aggregator="104.104.104.107",aggregator_as=44443,address_family="v4")

	myixia.topologies[0].change_bgp_routes_attributes_v6(aggregator="106.106.106.106",aggregator_as=66660,address_family="v6")
	myixia.topologies[1].change_bgp_routes_attributes_v6(aggregator="106.106.106.107",aggregator_as=66661,address_family="v6")
	myixia.topologies[2].change_bgp_routes_attributes_v6(aggregator="106.106.106.108",aggregator_as=66662,address_family="v6")
	myixia.topologies[3].change_bgp_routes_attributes_v6(aggregator="106.106.106.109",aggregator_as=66663,address_family="v6")

	myixia.topologies[0].change_bgp_routes_attributes_v6(aggregator="104.104.104.104",aggregator_as=44440,address_family="v4")
	myixia.topologies[1].change_bgp_routes_attributes_v6(aggregator="104.104.104.105",aggregator_as=44441,address_family="v4")
	myixia.topologies[2].change_bgp_routes_attributes_v6(aggregator="104.104.104.105",aggregator_as=44442,address_family="v4")
	myixia.topologies[3].change_bgp_routes_attributes_v6(aggregator="104.104.104.107",aggregator_as=44443,address_family="v4")

	 
	myixia.start_protocol(wait=40)

	check_bgp_test_result_v6(testcase,description,sw6_switch)


if testcase == 6148 or test_all:
	testcase = 6148
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGPv6 Best Routes Selection: Ext-Community. Run the test at the last switch: switches[-1] "
	print_test_subject(testcase,description)

	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	portList_v4_v6 = [
	[ixChassisIpList[0], 2, 11,"00:11:01:01:01:01","10.1.1.211/24","10.1.1.1","2001:10:1:1::211/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.1.1.212/24","10.1.1.1","2001:10:1:1::212/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.1.1.213/24","10.1.1.1","2001:10:1:1::213/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.1.1.214/24","10.1.1.1","2001:10:1:1::214/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.1.1.215/24","10.1.1.1","2001:10:1:1::215/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.1.1.216/24","10.1.1.1","2001:10:1:1::216/64","2001:10:1:1::1",1]
    ]
	
	ixia_ipv6_as_list = [101,102,103,104,105,106]
	ipv6_networks = ["2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:102:1:1::1","2001:102:1:1::1"]
	ipv4_networks = ["10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1","10.10.2.1","10.10.2.1"]

	cisco_switch = switches[0]
	sw6_switch = switches[1]
	my_ixia_ports = portList_v4_v6[-4:]
	

	sw6_ixia_ports = portList_v4_v6[-2:]
	sw6_as_lists = ixia_ipv6_as_list[-2:]
	sw6_ipv6_networks = ipv6_networks[-2:]
	sw6_ipv4_networks = ipv4_networks[-2:]


	cisco_ixia_ports = portList_v4_v6[-4:-2]
	cisco_as_lists = ixia_ipv6_as_list[-4:-2]
	cisco_ipv6_networks = ipv6_networks[-4:-2]
	cisco_ipv4_networks = ipv4_networks[-4:-2]

	fsw_switches =switches[1:]
	network = BGP_networks(switches)

	if test_config:
		test_clean_config(switches =fsw_switches)
		test_config_igp_ipv6(switches =fsw_switches)
		network.biuld_ibgp_mesh_topo_sys_intf_v6()
		network.biuld_ibgp_mesh_topo_sys_intf()
		console_timer(20,msg=f"Test case {testcase}: After configuring fully mesh iBGP across all IPv6 system interfaces, wait....")
	network.show_summary_v6()

	test_config_single_switch2ixia_all(switch=sw6_switch,ixia_ports=sw6_ixia_ports,as_lists=sw6_as_lists)


	myixia = IXIA(apiServerIp,ixChassisIpList,my_ixia_ports)

	test_config_ixia_bgp_all_one_switch_compare(myixia.topologies[:2],cisco_ipv6_networks,cisco_ipv4_networks,cisco_switch,cisco_as_lists)
	test_config_ixia_bgp_all_one_switch_compare(myixia.topologies[-2:],sw6_ipv6_networks,sw6_ipv4_networks,sw6_switch,sw6_as_lists)

	typecode = " 0=administratoras2octet 1=administratorip 2=administratoras4octet 3=opaque 6=evpn 64=administratoras2octetlinkbw"
	myixia.topologies[0].change_bgp_routes_attributes(ext_community=6,excomm_base=66000,com_type="routetarget",address_family="v6")
	myixia.topologies[1].change_bgp_routes_attributes(ext_community=6,excomm_base=66001,com_type="routetarget",address_family="v6")
	myixia.topologies[2].change_bgp_routes_attributes(ext_community=6,excomm_base=66002,com_type="routetarget",address_family="v6")
	myixia.topologies[3].change_bgp_routes_attributes(ext_community=6,excomm_base=66003,com_type="routetarget",address_family="v6")

	myixia.topologies[0].change_bgp_routes_attributes(ext_community=4,excomm_base=64000,com_type="routetarget",address_family="v4")
	myixia.topologies[1].change_bgp_routes_attributes(ext_community=4,excomm_base=64001,com_type="routetarget",address_family="v4")
	myixia.topologies[2].change_bgp_routes_attributes(ext_community=4,excomm_base=64002,com_type="routetarget",address_family="v4")
	myixia.topologies[3].change_bgp_routes_attributes(ext_community=4,excomm_base=64003,com_type="routetarget",address_family="v4")

	myixia.topologies[0].change_bgp_routes_attributes(ext_community=6,excomm_base=66000,com_type="routetarget",address_family="v6")
	myixia.topologies[1].change_bgp_routes_attributes(ext_community=6,excomm_base=66001,com_type="routetarget",address_family="v6")
	myixia.topologies[2].change_bgp_routes_attributes(ext_community=6,excomm_base=66002,com_type="routetarget",address_family="v6")
	myixia.topologies[3].change_bgp_routes_attributes(ext_community=6,excomm_base=66003,com_type="routetarget",address_family="v6")

	myixia.topologies[0].change_bgp_routes_attributes(ext_community=4,excomm_base=64000,com_type="routetarget",address_family="v4")
	myixia.topologies[1].change_bgp_routes_attributes(ext_community=4,excomm_base=64001,com_type="routetarget",address_family="v4")
	myixia.topologies[2].change_bgp_routes_attributes(ext_community=4,excomm_base=64002,com_type="routetarget",address_family="v4")
	myixia.topologies[3].change_bgp_routes_attributes(ext_community=4,excomm_base=64003,com_type="routetarget",address_family="v4")
	 
	myixia.start_protocol(wait=40)

	check_bgp_test_result_v6(testcase,description,sw6_switch)

if testcase == 6149 or test_all:
	testcase = 6149
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGPv6 Best Routes Selection: Put all attributes together. Run the test at the last switch: switches[-1] "
	print_test_subject(testcase,description)

	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	portList_v4_v6 = [
	[ixChassisIpList[0], 2, 11,"00:11:01:01:01:01","10.1.1.211/24","10.1.1.1","2001:10:1:1::211/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.1.1.212/24","10.1.1.1","2001:10:1:1::212/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.1.1.213/24","10.1.1.1","2001:10:1:1::213/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.1.1.214/24","10.1.1.1","2001:10:1:1::214/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.1.1.215/24","10.1.1.1","2001:10:1:1::215/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.1.1.216/24","10.1.1.1","2001:10:1:1::216/64","2001:10:1:1::1",1]
    ]
	
	ixia_ipv6_as_list = [101,102,103,104,105,106]
	ipv6_networks = ["2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:102:1:1::1","2001:102:1:1::1"]
	ipv4_networks = ["10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1","10.10.2.1","10.10.2.1"]

	cisco_switch = switches[0]
	sw6_switch = switches[3]
	my_ixia_ports = portList_v4_v6[-4:]
	

	sw6_ixia_ports = portList_v4_v6[-2:]
	sw6_as_lists = ixia_ipv6_as_list[-2:]
	sw6_ipv6_networks = ipv6_networks[-2:]
	sw6_ipv4_networks = ipv4_networks[-2:]


	cisco_ixia_ports = portList_v4_v6[-4:-2]
	cisco_as_lists = ixia_ipv6_as_list[-4:-2]
	cisco_ipv6_networks = ipv6_networks[-4:-2]
	cisco_ipv4_networks = ipv4_networks[-4:-2]

	fsw_switches =switches[1:]
	network = BGP_networks(switches)

	if test_config:
		test_clean_config(switches =fsw_switches)
		test_config_igp_ipv6(switches =fsw_switches)
		network.biuld_ibgp_mesh_topo_sys_intf_v6()
		console_timer(20,msg=f"Test case {testcase}: After configuring fully mesh iBGP across all IPv6 system interfaces, wait....")
	network.show_summary_v6()

	test_config_single_switch2ixia_all(switch=sw6_switch,ixia_ports=sw6_ixia_ports,as_lists=sw6_as_lists)


	myixia = IXIA(apiServerIp,ixChassisIpList,my_ixia_ports)

	test_config_ixia_bgp_all_one_switch_compare(myixia.topologies[:2],cisco_ipv6_networks,cisco_ipv4_networks,cisco_switch,cisco_as_lists)
	test_config_ixia_bgp_all_one_switch_compare(myixia.topologies[-2:],sw6_ipv6_networks,sw6_ipv4_networks,sw6_switch,sw6_as_lists)


	myixia.topologies[0].change_bgp_routes_attributes(origin="egp",med=6111,community=6,comm_base=6100,num_path=6,as_base=65010,aggregator="106.106.106.106",aggregator_as=66660,ext_community=6,excomm_base=65010,com_type="routetarget",address_family="v4")
	myixia.topologies[1].change_bgp_routes_attributes(origin="incomplete",med=6222,community=5,comm_base=6200,num_path=5,as_base=65020,aggregator="106.106.106.107",aggregator_as=66661,ext_community=6,excomm_base=65020,com_type="routetarget",address_family="v4")
	myixia.topologies[2].change_bgp_routes_attributes(origin="egp",med=6333,community=6,comm_base=6300,num_path=6,as_base=65030,aggregator="106.106.106.108",aggregator_as=66662,ext_community=6,excomm_base=65030,com_type="routetarget",address_family="v4")
	myixia.topologies[3].change_bgp_routes_attributes(origin="incomplete",med=6444,community=5,comm_base=6400,num_path=6,as_base=65040,aggregator="106.106.106.109",aggregator_as=66663,ext_community=6,excomm_base=65040,com_type="routetarget",address_family="v4")


	myixia.topologies[0].change_bgp_routes_attributes_v6(origin="egp",med=6111,community=6,comm_base=6100,num_path=6,as_base=65010,aggregator="106.106.106.106",aggregator_as=66660,ext_community=6,excomm_base=65010,com_type="routetarget",address_family="v6")
	myixia.topologies[1].change_bgp_routes_attributes_v6(origin="incomplete",med=6222,community=5,comm_base=6200,num_path=5,as_base=65020,aggregator="106.106.106.107",aggregator_as=66661,ext_community=6,excomm_base=65020,com_type="routetarget",address_family="v6")
	myixia.topologies[2].change_bgp_routes_attributes_v6(origin="egp",med=6333,community=6,comm_base=6300,num_path=6,as_base=65030,aggregator="106.106.106.108",aggregator_as=66662,ext_community=6,excomm_base=65030,com_type="routetarget",address_family="v6")
	myixia.topologies[3].change_bgp_routes_attributes_v6(origin="incomplete",med=6444,community=5,comm_base=6400,num_path=6,as_base=65040,aggregator="106.106.106.109",aggregator_as=66663,ext_community=6,excomm_base=65040,com_type="routetarget",address_family="v6")
	 
	myixia.start_protocol(wait=40)

	check_bgp_test_result_v6(testcase,description,sw6_switch)


if testcase == 61410 or test_all:
	testcase = 61410
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGPv6 Best Routes Selection: eBGP over iBGP. Run the test at the last switch: switches[-1] "
	print_test_subject(testcase,description)

	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	portList_v4_v6 = [
	[ixChassisIpList[0], 2, 11,"00:11:01:01:01:01","10.1.1.211/24","10.1.1.1","2001:10:1:1::211/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.1.1.212/24","10.1.1.1","2001:10:1:1::212/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.1.1.213/24","10.1.1.1","2001:10:1:1::213/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.1.1.214/24","10.1.1.1","2001:10:1:1::214/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.1.1.215/24","10.1.1.1","2001:10:1:1::215/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.1.1.216/24","10.1.1.1","2001:10:1:1::216/64","2001:10:1:1::1",1]
    ]
	
	ixia_ipv6_as_list = [101,102,103,104,105,106]
	# Have the same IPv4 and IPv6 advertised via eBGP and iBGP. Look at sw6 to pick eBGP route
	ipv6_networks = ["2001:101:1:1::1","2001:101:1:1::1","2001:102:1:1::1","2001:102:1:1::1","2001:102:1:1::1","2001:102:1:1::1"]
	ipv4_networks = ["10.10.1.1","10.10.1.1","10.10.2.1","10.10.2.1","10.10.2.1","10.10.2.1"]

	cisco_switch = switches[0]
	sw6_switch = switches[-1]
	my_ixia_ports = portList_v4_v6[-4:]
	# my_as_lists = ixia_ipv6_as_list[-4:]
	# my_ipv6_networks = ipv6_networks[-4:]
	# my_ipv4_networks = ipv4_networks[-4:]

	sw6_ixia_ports = portList_v4_v6[-2:]
	sw6_as_lists = ixia_ipv6_as_list[-2:]
	sw6_ipv6_networks = ipv6_networks[-2:]
	sw6_ipv4_networks = ipv4_networks[-2:]


	cisco_ixia_ports = portList_v4_v6[-4:-2]
	cisco_as_lists = ixia_ipv6_as_list[-4:-2]
	cisco_ipv6_networks = ipv6_networks[-4:-2]
	cisco_ipv4_networks = ipv4_networks[-4:-2]

	fsw_switches =switches[1:]
	network = BGP_networks(fsw_switches)

	if test_config:
		test_clean_config(switches =fsw_switches)
		test_config_igp_ipv6(switches =fsw_switches)
		network.biuld_ibgp_mesh_topo_sys_intf_v6()
		test_config_single_switch2ixia_all(switch=sw6_switch,ixia_ports=sw6_ixia_ports,as_lists=sw6_as_lists)
		console_timer(20,msg=f"Test case {testcase}: After configuring fully mesh iBGP across all IPv6 system interfaces, wait....")
	
	network.show_summary_v6()
	test_config_single_switch2ixia_all(switch=sw6_switch,ixia_ports=sw6_ixia_ports,as_lists=sw6_as_lists)

	myixia = IXIA(apiServerIp,ixChassisIpList,my_ixia_ports)
 
	#test_config_ixia_bgp_all_one_switch_cisco(myixia,sw6_ipv6_networks,sw6_ipv4_networks,sw6_switch,sw6_as_lists,cisco_ipv6_networks,cisco_ipv4_networks,cisco_switch,cisco_as_lists)
	test_config_ixia_bgp_all_one_switch_compare(myixia.topologies[:2],cisco_ipv6_networks,cisco_ipv4_networks,cisco_switch,cisco_as_lists)
	test_config_ixia_bgp_all_one_switch_compare(myixia.topologies[-2:],sw6_ipv6_networks,sw6_ipv4_networks,sw6_switch,sw6_as_lists)

	myixia.start_protocol(wait=40)

	check_bgp_test_result_v6(testcase,description,sw6_switch)

if testcase == 61411 or test_all:
	testcase = 61411
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGPv6 Best Routes Selection: ECMP over the 1048D - switches[4] "
	print_test_subject(testcase,description)

	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	portList_v4_v6 = [
	[ixChassisIpList[0], 2, 11,"00:11:01:01:01:01","10.1.1.211/24","10.1.1.1","2001:10:1:1::211/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.1.1.212/24","10.1.1.1","2001:10:1:1::212/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.1.1.213/24","10.1.1.1","2001:10:1:1::213/64","2001:10:1:1::1",1], 
    [ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.1.1.214/24","10.1.1.1","2001:10:1:1::214/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.1.1.215/24","10.1.1.1","2001:10:1:1::215/64","2001:10:1:1::1",1],
    [ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.1.1.216/24","10.1.1.1","2001:10:1:1::216/64","2001:10:1:1::1",1]
    ]
	
	ixia_ipv6_as_list = [101,102,103,104,105,106]
	ipv6_networks = ["2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:102:1:1::1","2001:102:1:1::1"]
	ipv4_networks = ["10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1","10.10.2.1","10.10.2.1"]

	cisco_switch = switches[0]
	sw6_switch = switches[4]
	my_ixia_ports = portList_v4_v6[-4:]
	

	sw6_ixia_ports = portList_v4_v6[-2:]
	sw6_as_lists = ixia_ipv6_as_list[-2:]
	sw6_ipv6_networks = ipv6_networks[-2:]
	sw6_ipv4_networks = ipv4_networks[-2:]


	cisco_ixia_ports = portList_v4_v6[-4:-2]
	cisco_as_lists = ixia_ipv6_as_list[-4:-2]
	cisco_ipv6_networks = ipv6_networks[-4:-2]
	cisco_ipv4_networks = ipv4_networks[-4:-2]

	fsw_switches =switches[1:]
	network = BGP_networks(switches)

	if test_config:
		#test_clean_config(switches =fsw_switches)
		test_config_igp_ipv6(switches =fsw_switches)
		network.biuld_ibgp_mesh_topo_sys_intf_v6()
		network.biuld_ibgp_mesh_topo_sys_intf()
		console_timer(20,msg=f"Test case {testcase}: After configuring fully mesh iBGP across all IPv6 system interfaces, wait....")
	network.show_summary_v6()

	#This has to be iBGP to compare local preference
	test_config_single_switch2ixia_all(switch=sw6_switch,ixia_ports=sw6_ixia_ports,as_lists=sw6_as_lists,protocol="ibgp")
	cisco_switch.cisco_config_ibgp_ixia()

	myixia = IXIA(apiServerIp,ixChassisIpList,my_ixia_ports)

	test_config_ixia_ibgp_all_one_switch_compare(myixia.topologies[:2],cisco_ipv6_networks,cisco_ipv4_networks,cisco_switch,cisco_as_lists)
	test_config_ixia_ibgp_all_one_switch_compare(myixia.topologies[-2:],sw6_ipv6_networks,sw6_ipv4_networks,sw6_switch,sw6_as_lists)

	# myixia.topologies[0].change_bgp_routes_attributes(local=610,address_family="v6")
	# myixia.topologies[1].change_bgp_routes_attributes(local=620,address_family="v6")
	# myixia.topologies[2].change_bgp_routes_attributes(local=630,address_family="v6")
	# myixia.topologies[3].change_bgp_routes_attributes(local=640,address_family="v6")


	# myixia.topologies[0].change_bgp_routes_attributes(local=410,address_family="v4")
	# myixia.topologies[1].change_bgp_routes_attributes(local=420,address_family="v4")
	# myixia.topologies[2].change_bgp_routes_attributes(local=430,address_family="v4")
	# myixia.topologies[3].change_bgp_routes_attributes(local=440,address_family="v4")


	# myixia.topologies[0].change_bgp_routes_attributes_v6(local=610,address_family="v6")
	# myixia.topologies[1].change_bgp_routes_attributes_v6(local=620,address_family="v6")
	# myixia.topologies[2].change_bgp_routes_attributes_v6(local=630,address_family="v6")
	# myixia.topologies[3].change_bgp_routes_attributes_v6(local=640,address_family="v6")

	# myixia.topologies[0].change_bgp_routes_attributes_v6(local=410,address_family="v4")
	# myixia.topologies[1].change_bgp_routes_attributes_v6(local=420,address_family="v4")
	# myixia.topologies[2].change_bgp_routes_attributes_v6(local=430,address_family="v4")
	# myixia.topologies[3].change_bgp_routes_attributes_v6(local=440,address_family="v4")

	myixia.start_protocol(wait=40)

	check_bgp_test_result_v6(testcase,description,sw6_switch)

if testcase == 15 or test_all:
	testcase = 15
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGP policy and route filtering: 'Local Preference' "
	print_test_subject(testcase,description)

	if CLEAN_ALL:
		switches_clean_up(switches)
	else:
		for switch in switches:
			switch.router_bgp.clear_config()
	 
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

	portList = [[ixChassisIpList[0], 2,11,"00:11:01:01:01:01","10.10.1.1",65000,"10.1.1.101/24","10.1.1.1"], 
	[ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.10.1.1",65000,"10.1.1.102/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.10.1.1",65000,"10.1.1.103/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.20.1.1",65000,"10.1.1.104/24","10.1.1.1"], 
	[ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.20.1.1",65000,"10.1.1.105/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.20.1.1",65000,"10.1.1.106/24","10.1.1.1"]]

	switch = switches[0]
	for ixia_port in portList:
		switch.router_bgp.add_ebgp_peer(ip = ixia_port[6],remote_as = ixia_port[5])
	
	 
	myixia = IXIA(apiServerIp,ixChassisIpList,portList)

 	
	for topo in myixia.topologies:
		topo.add_ipv4()
	 
	myixia.topologies[0].add_bgp(dut_ip='10.1.1.1',bgp_type='internal',num=10)
	myixia.topologies[1].add_bgp(dut_ip='10.1.1.1',bgp_type='internal',num=10)
	myixia.topologies[2].add_bgp(dut_ip='10.1.1.1',bgp_type='internal',num=10)
	myixia.topologies[3].add_bgp(dut_ip='10.1.1.1',bgp_type='internal',num=10)
	myixia.topologies[4].add_bgp(dut_ip='10.1.1.1',bgp_type='internal',num=10)
	myixia.topologies[5].add_bgp(dut_ip='10.1.1.1',bgp_type='internal',num=10)

	myixia.topologies[0].change_local_pref(1111)
	myixia.topologies[1].change_local_pref(2222)
	myixia.topologies[2].change_local_pref(3333)
	myixia.topologies[3].change_local_pref(4444)
	myixia.topologies[4].change_local_pref(5555)
	myixia.topologies[5].change_local_pref(6666)
	 
	 

	myixia.start_protocol(wait=50)

	check_bgp_test_result(testcase,description,switches)

if testcase == 16 or test_all:
	testcase = 16
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGP Route_map: match actions:next_hop,as,network,origin,metric"
	print_test_subject(testcase,description)

	if restore_config:
		if CLEAN_ALL:
			switches_cleanup_4_restore(switches)
		for switch in switches:
			file = f"{switch.cfg_file}_case_{testcase}.txt" 
			switch.restore_config(file)

		console_timer(300,msg="wait for 300s after restore config from tftp server")
		for switch in switches:
			switch.relogin()

	###################################################################
	#   Step by Step setup 
	###################################################################

	if test_setup: 
		# ########################################################
		# #   Configure OSPF infratructure
		# ########################################################
		for switch in switches:
			switch.show_switch_info()
			switch.router_ospf.basic_config()
		console_timer(20,msg="After configuring ospf, wait for 20 sec")

		# ########################################################
		# #   Configure iBGP mesh infratructure
		# ########################################################
		for switch in switches:
			switch.router_ospf.neighbor_discovery()
			switch.router_bgp.update_ospf_neighbors()
			switch.router_bgp.clear_config()
			switch.router_bgp.config_ibgp_mesh_loopback()

		console_timer(30,msg="After configuring iBGP sessions via loopbacks, wait for 30s")
		for switch in switches:
			switch.router_ospf.show_ospf_neighbors()
			switch.router_bgp.show_bgp_summary()

		# ########################################################
		# #   configure ACL and Route-map
		# ########################################################
		for switch in switches:
			switch.route_map.clean_up()
			switch.access_list.basic_config()
			switch.route_map.basic_config()
		 
		########################################################
		#   Backup the switch's configuration
		########################################################
		tprint("============= Backing up configurations at the start of the test ============")

		for switch in switches:
			file = f"{switch.cfg_file}_case_{testcase}.txt" 
			switch.backup_config(file)

	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	portList = [[ixChassisIpList[0], 2,11,"00:11:01:01:01:01","10.10.1.1",101,"10.1.1.101/24","10.1.1.1"], 
	[ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.20.1.1",102,"10.1.1.102/24","10.1.1.1"]]

	########################################################
	#   Configure eBGP to IXIA ports  
	########################################################
	for switch,ixia_port_info in zip(switches,portList):
		if switch.router_bgp.config_ebgp_ixia(ixia_port_info) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP peers ==============")
			exit()
	
	 
	myixia = IXIA(apiServerIp,ixChassisIpList,portList)

 	
	for topo in myixia.topologies:
		topo.add_ipv4()
	 
	myixia.topologies[0].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=10)
	myixia.topologies[1].add_bgp(dut_ip='10.1.1.2',bgp_type='external',num=10)
	 
	myixia.topologies[0].change_med(1000)
	myixia.topologies[1].change_med(2000)
	 
	 

	myixia.start_protocol(wait=50)

	myixia.create_traffic(src_topo=myixia.topologies[0].topology, dst_topo=myixia.topologies[1].topology,traffic_name="t1_to_t2",tracking_name="Tracking_1")
	myixia.create_traffic(src_topo=myixia.topologies[1].topology, dst_topo=myixia.topologies[0].topology,traffic_name="t2_to_t1",tracking_name="Tracking_2")

	
	myixia.start_traffic()
	myixia.collect_stats()
	myixia.check_traffic()

	myixia.stop_traffic()
	#myixia.clear_stats()

	switch_1 = switches[0]
	switch_2 = switches[1]
	for switch in switches:
		switch.router_bgp.get_neighbors_summary()
		for nei in switch.router_bgp.bgp_neighbors_objs:
			nei.remove_all_filters()
	neighbors = switch_1.router_bgp.bgp_neighbors_objs
	#find out switch_1's ixia neighbor
	for nei in neighbors:
		if nei.id == seperate_ip_mask(portList[0][6])[0]:
			the_neighbor = nei
			break
	print(the_neighbor.id)

	other_switches_2_sw1 = []
	for i in range(1,7):
		neighbors = switches[i].router_bgp.bgp_neighbors_objs
		for nei in neighbors:
			if nei.id == switch_1.rid:
				other_switches_2_sw1.append(nei)
				break
	# ########################################################
	# #   Start testing route-map: match network 
	# ########################################################
	the_neighbor.add_route_map_in(route_map="match-network-10-10")
	console_timer(20,msg=f"After configuring route-map(match-network) on neighbor {the_neighbor.id}, wait for 20 sec")

	switch_1.router_bgp.clear_bgp_all()
	switch_2.router_bgp.clear_bgp_all()

	switch_1.router_bgp.show_bgp_network()
	switch_1.show_routing_table()

	switch_2.router_bgp.show_bgp_network()
	switch_2.show_routing_table()

	myixia.start_traffic()
	myixia.collect_stats()
	myixia.check_traffic()

	myixia.stop_traffic()
	myixia.clear_stats()
	the_neighbor.remove_route_map_in(route_map="match-network-10-10")
	console_timer(20,msg=f"After removing route-map(match-network) on neighbor {the_neighbor.id}, wait for 20 sec")

	switch_1.router_bgp.clear_bgp_all()
	switch_2.router_bgp.clear_bgp_all()
	
	switch_1.router_bgp.show_bgp_network()
	switch_1.show_routing_table()

	switch_2.router_bgp.show_bgp_network()
	switch_2.show_routing_table()

	myixia.start_traffic()
	myixia.collect_stats()
	if myixia.check_traffic():
		msg = "============= Passed: BGP route-map: match network =========="
		tprint(msg)
		send_Message(msg)
	else:
		msg = "============= Failed: BGP route-map: match network =========="
		tprint(msg)
		send_Message(msg)
	myixia.stop_traffic()
	myixia.clear_stats()

	########################################################
	#   Start testing route-map: match aspath
	########################################################
	the_neighbor.add_route_map_in(route_map="match-aspath-101")
	console_timer(20,msg=f"After configuring route-map(match-network) on neighbor {the_neighbor.id}, wait for 20 sec")

	switch_1.router_bgp.clear_bgp_all()
	switch_2.router_bgp.clear_bgp_all()

	switch_1.router_bgp.show_bgp_network()
	switch_1.show_routing_table()

	switch_2.router_bgp.show_bgp_network()
	switch_2.show_routing_table()

	myixia.start_traffic()
	myixia.collect_stats()
	myixia.check_traffic()

	myixia.stop_traffic()
	myixia.clear_stats()
	the_neighbor.remove_route_map_in(route_map="match-aspath-101")
	console_timer(20,msg=f"After removing route-map(match-network) on neighbor {the_neighbor.id}, wait for 20 sec")

	switch_1.router_bgp.clear_bgp_all()
	switch_2.router_bgp.clear_bgp_all()
	
	switch_1.router_bgp.show_bgp_network()
	switch_1.show_routing_table()

	switch_2.router_bgp.show_bgp_network()
	switch_2.show_routing_table()

	myixia.start_traffic()
	myixia.collect_stats()
	if myixia.check_traffic():
		msg = "============= Passed: BGP route-map: match aspath =========="
		tprint(msg)
		send_Message(msg)
	else:
		msg = "============= Failed: BGP route-map: match aspath =========="
		tprint(msg)
		send_Message(msg)

	myixia.stop_traffic()
	myixia.clear_stats()
	########################################################
	#   Start testing route-map: match next_hop
	########################################################
	the_neighbor.add_route_map_in(route_map="match-med-1000")
	console_timer(20,msg=f"After configuring route-map(match-network) on neighbor {the_neighbor.id}, wait for 20 sec")

	switch_1.router_bgp.clear_bgp_all()
	switch_2.router_bgp.clear_bgp_all()

	switch_1.router_bgp.show_bgp_network()
	switch_1.show_routing_table()

	switch_2.router_bgp.show_bgp_network()
	switch_2.show_routing_table()

	myixia.start_traffic()
	myixia.collect_stats()
	myixia.check_traffic()

	myixia.stop_traffic()
	myixia.clear_stats()
	the_neighbor.remove_route_map_in(route_map="match-med-1000")
	console_timer(20,msg=f"After removing route-map(match-network) on neighbor {the_neighbor.id}, wait for 20 sec")

	switch_1.router_bgp.clear_bgp_all()
	switch_2.router_bgp.clear_bgp_all()
	
	switch_1.router_bgp.show_bgp_network()
	switch_1.show_routing_table()

	switch_2.router_bgp.show_bgp_network()
	switch_2.show_routing_table()

	myixia.start_traffic()
	myixia.collect_stats()
	if myixia.check_traffic():
		msg = "============= Passed: BGP route-map: match metric =========="
		tprint(msg)
		send_Message(msg)
	else:
		msg = "============= Failed: BGP route-map: match metric =========="
		tprint(msg)
		send_Message(msg)
	myixia.stop_traffic()
	myixia.clear_stats()
	########################################################
	#   Start testing route-map: match next_hop
	########################################################
	the_neighbor.add_route_map_in(route_map="match-next-hop-ixia-1")
	console_timer(20,msg=f"After configuring route-map(match-network) on neighbor {the_neighbor.id}, wait for 20 sec")

	switch_1.router_bgp.clear_bgp_all()
	switch_2.router_bgp.clear_bgp_all()

	switch_1.router_bgp.show_bgp_network()
	switch_1.show_routing_table()

	switch_2.router_bgp.show_bgp_network()
	switch_2.show_routing_table()

	myixia.start_traffic()
	myixia.collect_stats()
	myixia.check_traffic()

	myixia.stop_traffic()
	myixia.clear_stats()
	the_neighbor.remove_route_map_in(route_map="match-next-hop-ixia-1")
	console_timer(20,msg=f"After removing route-map(match-network) on neighbor {the_neighbor.id}, wait for 20 sec")

	switch_1.router_bgp.clear_bgp_all()
	switch_2.router_bgp.clear_bgp_all()
	
	switch_1.router_bgp.show_bgp_network()
	switch_1.show_routing_table()

	switch_2.router_bgp.show_bgp_network()
	switch_2.show_routing_table()

	myixia.start_traffic()
	myixia.collect_stats()
	if myixia.check_traffic():
		msg = "============= Passed: BGP route-map: match next_hop =========="
		tprint(msg)
		send_Message(msg)
	else:
		msg = "============= Failed: BGP route-map: match next_hop =========="
		tprint(msg)
		send_Message(msg)
	myixia.stop_traffic()
	myixia.clear_stats()

	########################################################
	#   Start testing route-map: match origin
	########################################################
	the_neighbor.add_route_map_in(route_map="match-origin")
	console_timer(20,msg=f"After configuring route-map(match-network) on neighbor {the_neighbor.id}, wait for 20 sec")

	switch_1.router_bgp.clear_bgp_all()
	switch_2.router_bgp.clear_bgp_all()

	switch_1.router_bgp.show_bgp_network()
	switch_1.show_routing_table()

	switch_2.router_bgp.show_bgp_network()
	switch_2.show_routing_table()

	myixia.start_traffic()
	myixia.collect_stats()
	myixia.check_traffic()

	myixia.stop_traffic()
	myixia.clear_stats()
	the_neighbor.remove_route_map_in(route_map="match-origin")
	console_timer(20,msg=f"After removing route-map(match-network) on neighbor {the_neighbor.id}, wait for 20 sec")

	switch_1.router_bgp.clear_bgp_all()
	switch_2.router_bgp.clear_bgp_all()
	
	switch_1.router_bgp.show_bgp_network()
	switch_1.show_routing_table()

	switch_2.router_bgp.show_bgp_network()
	switch_2.show_routing_table()

	myixia.start_traffic()
	myixia.collect_stats()
	if myixia.check_traffic():
		msg = "============= Passed: BGP route-map: match origin =========="
		tprint(msg)
		send_Message(msg)
	else:
		msg = "============= Failed: BGP route-map: match origin =========="
		tprint(msg)
		send_Message(msg)
	myixia.stop_traffic()

	#########################################################################################################
	#   Start testing route-map-in: set metric, set origin, set nexthop, set aspath, set weight, set local_pref
	#########################################################################################################
	set_clause_list = [("change-med-1000","match-med-10000","permit-med-10000","set metric"),
						("change-origin","match-origin-egp","permit-origin-egp","set origin"),
						("change-next-hop-1","match-next-hop-sw1","permit-next-hop-sw1","set nexthop"),
						("change-aspath-101","match-aspath-1001","permit-aspath-1001","set aspath"),
						("change-weight-1","match-aspath-101","permit-aspath-101","set weight"),
						("set-local-pref-1111","match-aspath-101","permit-aspath-101","set local perference"),
						]
	for clause in set_clause_list:	
		for neighbor_2 in other_switches_2_sw1:
			neighbor_2.remove_route_map_in()
		the_neighbor.remove_route_map_in()
		the_neighbor.add_route_map_in(route_map=clause[0])
		for neighbor_2 in other_switches_2_sw1:
			neighbor_2.add_route_map_in(route_map=clause[1])

		for switch in switches:
			switch.router_bgp.clear_bgp_all()
		 
		console_timer(10,msg=f"After clearing BGP, wait for 10 sec")

		for switch in switches: 
			switch.router_bgp.show_bgp_network()
			switch.show_routing_table()

		networks = ["10.10.1.1"]

		step_1 = True
		for i in range(1,7):
			if switches[i].check_route_exist(networks) or switches[i].router_bgp.check_network_exist(networks):
				msg = f"============= Step 1 Failed: BGP route-map-in: {clause[3]}.{networks} still exist at {switches[i].rid} =========="
				tprint(msg)
				send_Message(msg)
				step_1 = False
		if step_1: 
			msg = f"============= Step 1 Passed: BGP route-map-in: {clause[3]}, {networks} does NOT exist at other switches =========="
			tprint(msg)
			send_Message(msg)

		myixia.stop_traffic()
		#myixia.clear_stats()

		for neighbor_2 in other_switches_2_sw1:
			neighbor_2.remove_route_map_in()
			neighbor_2.add_route_map_in(route_map=clause[2])

		for switch in switches:
			switch.router_bgp.clear_bgp_all()

		for switch in switches: 
			switch.router_bgp.show_bgp_network()
			switch.show_routing_table()

		myixia.start_traffic()
		myixia.collect_stats()
		if myixia.check_traffic():
			msg = f"============= Step 2 Passed: BGP route-map-in: {clause[3]} with IXIA traffic =========="
			tprint(msg)
			send_Message(msg)
		else:
			msg = f"============= Step 2 Passed: BGP route-map-in: {clause[3]} with IXIA traffic =========="
			tprint(msg)
			send_Message(msg)
		myixia.stop_traffic()
		#myixia.clear_stats()
		for neighbor_2 in other_switches_2_sw1:
			neighbor_2.remove_route_map_in()
		the_neighbor.remove_route_map_in()

	########################################################################################################
	# 	Start testing route-map-out: set metric, set origin, set nexthop, set aspath, set weight, set local_pref
	########################################################################################################

	switch_1 = switches[0]
	switch_2 = switches[1]
	for switch in switches:
		switch.router_bgp.get_neighbors_summary()
	neighbors = switch_1.router_bgp.bgp_neighbors_objs
	#find out switch_1's ixia neighbor
	for nei in neighbors:
		if nei.id == switch_2.rid:
			the_neighbor = nei
			break
	print(the_neighbor.id)

	other_switches_2_sw1 = []
	for i in range(1,7):
		neighbors = switches[i].router_bgp.bgp_neighbors_objs
		for nei in neighbors:
			if nei.id == switch_1.rid:
				other_switches_2_sw1.append(nei)
				break

	other_switches_ids = []
	for i in range(1,7):
		other_switches_ids.append(switches[i].rid)

	switch1_2_others_neighbor_list = []
	for nei in neighbors:
		if nei.id in other_switches_ids:
			switch1_2_others_neighbor_list.append(nei)

	set_clause_list = [("change-med-1000","match-med-10000","permit-med-10000","set metric"),
						("change-origin","match-origin-egp","permit-origin-egp","set origin"),
						("change-next-hop-1","match-next-hop-sw1","permit-next-hop-sw1","set nexthop"),
						("change-aspath-101","match-aspath-1001","permit-aspath-1001","set aspath"),
						("change-weight-1","match-aspath-101","permit-aspath-101","set weight"),
						("set-local-pref-1111","match-aspath-101","permit-aspath-101","set local perference"),
						]
	for clause in set_clause_list:	
		 
		for nei in switch1_2_others_neighbor_list:
			nei.remove_route_map_out()
			nei.remove_route_map_in()
			nei.add_route_map_out(route_map=clause[0])
		for neighbor_2 in other_switches_2_sw1:
			neighbor_2.remove_route_map_out()
			neighbor_2.remove_route_map_in()
			neighbor_2.add_route_map_in(route_map=clause[1])

		for switch in switches:
			switch.router_bgp.clear_bgp_all()
		 
		console_timer(10,msg=f"After clearing BGP, wait for 10 sec")

		for switch in switches: 
			switch.router_bgp.show_bgp_network()
			switch.show_routing_table()

		networks = ["10.10.1.1"]

		step_1 = True
		for i in range(1,7):
			if switches[i].check_route_exist(networks) or switches[i].router_bgp.check_network_exist(networks):
				msg = f"============= Step 1 Failed: BGP route-map-out: {clause[3]}.{networks} still exist at {switches[i].rid} =========="
				tprint(msg)
				send_Message(msg)
				step_1 = False
		if step_1: 
			msg = f"============= Step 1 Passed: BGP route-map-out: {clause[3]}, {networks} does NOT exist at all other switches =========="
			tprint(msg)
			send_Message(msg)

		myixia.stop_traffic()
		#myixia.clear_stats()

		for neighbor_2 in other_switches_2_sw1:
			neighbor_2.remove_route_map_in()
			neighbor_2.add_route_map_in(route_map=clause[2])

		for switch in switches:
			switch.router_bgp.clear_bgp_all()

		for switch in switches: 
			switch.router_bgp.show_bgp_network()
			switch.show_routing_table()

		myixia.start_traffic()
		myixia.collect_stats()
		if myixia.check_traffic():
			msg = f"============= Step 2 Passed: BGP route-map-out: {clause[3]} with IXIA traffic =========="
			tprint(msg)
			send_Message(msg)
		else:
			msg = f"============= Step 2 Passed: BGP route-map-out: {clause[3]} with IXIA traffic =========="
			tprint(msg)
			send_Message(msg)
		myixia.stop_traffic()
		#clean up all route-map in and out on all switches 
		for neighbor_2 in other_switches_2_sw1:
			neighbor_2.remove_route_map_out()
			neighbor_2.remove_route_map_in()
		for nei in switch1_2_others_neighbor_list:
			nei.remove_route_map_out()
			nei.remove_route_map_in()

if testcase == 17 or test_all:
	testcase = 17
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGP distribute-list, prefix-list, aspath-filter-list: IN & OUT"
	print_test_subject(testcase,description)

	if restore_config:
		if CLEAN_ALL:
			switches_cleanup_4_restore(switches)
		for switch in switches:
			file = f"{switch.cfg_file}_case_{testcase}.txt" 
			switch.restore_config(file)

		console_timer(300,msg="wait for 300s after restore config from tftp server")
		for switch in switches:
			switch.relogin()

	###################################################################
	#   Step by Step setup 
	###################################################################

	if test_config: 
		########################################################
		#   Configure OSPF infratructure
		########################################################
		for switch in switches:
			switch.show_switch_info()
			switch.router_ospf.basic_config()
		console_timer(20,msg="After configuring ospf, wait for 20 sec")

		# ########################################################
		# #   Configure iBGP mesh infratructure
		# ########################################################
		for switch in switches:
			switch.router_ospf.neighbor_discovery()
			switch.router_bgp.update_ospf_neighbors()
			switch.router_bgp.clear_config()
			switch.router_bgp.config_ibgp_mesh_loopback()

		console_timer(30,msg="After configuring iBGP sessions via loopbacks, wait for 30s")
		for switch in switches:
			switch.router_ospf.show_ospf_neighbors()
			switch.router_bgp.show_bgp_summary()

		########################################################
		#   configure ACL and Route-map
		########################################################
		 
		for switch in switches:
			switch.prefix_list.basic_config()
			switch.aspath_list.basic_config()
			switch.route_map.clean_up()
			switch.access_list.basic_config()
			# switch.route_map.basic_config()
	
		########################################################
		#   Backup the switch's configuration
		########################################################
		tprint("============= Backing up configurations at the start of the test ============")

		for switch in switches:
			file = f"{switch.cfg_file}_case_{testcase}.txt" 
			switch.backup_config(file)

	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	portList = [[ixChassisIpList[0], 2,11,"00:11:01:01:01:01","10.10.1.1",101,"10.1.1.101/24","10.1.1.1"], 
	[ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.20.1.1",102,"10.1.1.102/24","10.1.1.1"]]

	########################################################
	#   Configure eBGP to IXIA ports  
	########################################################
	for switch,ixia_port_info in zip(switches,portList):
		if switch.router_bgp.config_ebgp_ixia(ixia_port_info) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP peers ==============")
			exit()
	
	 
	myixia = IXIA(apiServerIp,ixChassisIpList,portList)

 	
	for topo in myixia.topologies:
		topo.add_ipv4()
	 
	myixia.topologies[0].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=10)
	myixia.topologies[1].add_bgp(dut_ip='10.1.1.2',bgp_type='external',num=10)
	 
	myixia.topologies[0].change_med(1000)
	myixia.topologies[1].change_med(2000)
	 
	 

	myixia.start_protocol(wait=50)

	myixia.create_traffic(src_topo=myixia.topologies[0].topology, dst_topo=myixia.topologies[1].topology,traffic_name="t1_to_t2",tracking_name="Tracking_1")
	myixia.create_traffic(src_topo=myixia.topologies[1].topology, dst_topo=myixia.topologies[0].topology,traffic_name="t2_to_t1",tracking_name="Tracking_2")

	
	myixia.start_traffic()
	myixia.collect_stats()
	myixia.check_traffic()

	myixia.stop_traffic()
	#myixia.clear_stats()

	switch_1 = switches[0]
	switch_2 = switches[1]
	for switch in switches:
		switch.router_bgp.get_neighbors_summary()
		for nei in switch.router_bgp.bgp_neighbors_objs:
			nei.remove_all_filters()

	neighbors = switch_1.router_bgp.bgp_neighbors_objs
	#find out switch_1's ixia neighbor
	for nei in neighbors:
		if nei.id == seperate_ip_mask(portList[0][6])[0]:
			neighbor_ixia_1 = nei
			break
	print(neighbor_ixia_1.id)


	other_switches_2_sw1 = []
	for i in range(1,7):
		neighbors = switches[i].router_bgp.bgp_neighbors_objs
		for nei in neighbors:
			if nei.id == switch_1.rid:
				other_switches_2_sw1.append(nei)
				break
	########################################################################################################
	   
	########################################################################################################
	set_clause_list = [("prefix","deny-prefix-10-10","bgp prefix list in "),
					("aspath","deny-as-101","bgp aspth list in "),
					("distribute","deny-network-10-10","bgp distribute list in "),    
					]
	for clause in set_clause_list:
		if clause[0] == "prefix":
			neighbor_ixia_1.remove_all_filters()
			neighbor_ixia_1.add_prefix_list_in(prefix=clause[1])
		elif clause[0] == "aspath":
			neighbor_ixia_1.remove_all_filters()
			neighbor_ixia_1.add_aspath_in(aspath=clause[1])
		elif clause[0] == "distribute":
			neighbor_ixia_1.remove_all_filters()
			neighbor_ixia_1.add_distribute_list_in(distribute=clause[1])
	 
		for switch in switches:
			switch.router_bgp.clear_bgp_all()
		 
		console_timer(10,msg=f"After clearing BGP, wait for 10 sec")

		for switch in switches: 
			switch.router_bgp.show_bgp_network()
			switch.show_routing_table()

		networks = ["10.10.1.1"]

		step_1 = True
		for i in range(1,7):
			if switches[i].check_route_exist(networks) or switches[i].router_bgp.check_network_exist(networks):
				msg = f"============= Step 1 Failed: BGP {clause[2]}: {networks} still exist at {switches[i].rid} =========="
				tprint(msg)
				send_Message(msg)
				step_1 = False
		if step_1: 
			msg = f"============= Step 1 Passed: BGP {clause[2]}:{networks} does NOT exist at other switches =========="
			tprint(msg)
			send_Message(msg)

		myixia.stop_traffic()
		#myixia.clear_stats()

		neighbor_ixia_1.remove_all_filters()
		 

		for switch in switches:
			switch.router_bgp.clear_bgp_all()

		for switch in switches: 
			switch.router_bgp.show_bgp_network()
			switch.show_routing_table()

		step_2 = True
		for i in range(1,7):
			if not switches[i].check_route_exist(networks) or not switches[i].router_bgp.check_network_exist(networks):
				msg = f"============= Step 2 Failed: BGP {clause[2]}: {networks} NOT exist at {switches[i].rid} =========="
				tprint(msg)
				send_Message(msg)
				step_2 = False
		if step_2: 
			msg = f"============= Step 2 Passed: BGP {clause[2]}:{networks} exist at ALL other switches =========="
			tprint(msg)
			send_Message(msg)

		myixia.start_traffic()
		myixia.collect_stats()
		if myixia.check_traffic():
			msg = f"============= Step 3 Passed: {clause[2]} with IXIA traffic =========="
			tprint(msg)
			send_Message(msg)
		else:
			msg = f"============= Step 3 Failed:  {clause[2]} with IXIA traffic =========="
			tprint(msg)
			send_Message(msg)
		myixia.stop_traffic()
	

	########################################################################################################
	# distribute-list-out, prefix-list-out, aspath-filter-list-out
	########################################################################################################
	set_clause_list = [("prefix","deny-prefix-10-10","bgp prefix list out "),
					("aspath","deny-as-101","bgp aspth list out "),
					("distribute","deny-network-10-10","bgp distribute list out"),    
					]

	# set_clause_list = [ ("distribute","deny-network-10-10","bgp distribute list out")]

	switch_1 = switches[0]
	switch_2 = switches[1]
	for switch in switches:
		switch.router_bgp.get_neighbors_summary()
	neighbors = switch_1.router_bgp.bgp_neighbors_objs
	switch_1_neighbors = neighbors
	#find out switch_1's ixia neighbor
	for nei in neighbors:
		if nei.id == switch_2.rid:
			the_neighbor = nei
			break
	print(the_neighbor.id)

	other_switches_2_sw1 = []
	for i in range(1,7):
		neighbors = switches[i].router_bgp.bgp_neighbors_objs
		for nei in neighbors:
			if nei.id == switch_1.rid:
				other_switches_2_sw1.append(nei)
				break

	other_switches_ids = []
	for i in range(1,7):
		other_switches_ids.append(switches[i].rid)

	switch1_2_others_neighbor_list = []
	for nei in switch_1_neighbors:
		if nei.id in other_switches_ids:
			switch1_2_others_neighbor_list.append(nei)
 
	for clause in set_clause_list:	
		for nei in switch1_2_others_neighbor_list:
			if clause[0] == "prefix":
				nei.remove_all_filters()
				nei.add_prefix_list_out(prefix=clause[1])
			elif clause[0] == "aspath":
				nei.remove_all_filters()
				nei.add_aspath_out(aspath=clause[1])
			elif clause[0] == "distribute":
				nei.remove_all_filters()
				nei.add_distribute_list_out(distribute=clause[1])
		 
		for switch in switches:
			switch.router_bgp.clear_bgp_all()
		 
		console_timer(10,msg=f"After clearing BGP, wait for 10 sec")

		for switch in switches: 
			switch.router_bgp.show_bgp_network()
			switch.show_routing_table()

		networks = ["10.10.1.1"]

		step_1 = True
		for i in range(1,7):
			if switches[i].check_route_exist(networks) or switches[i].router_bgp.check_network_exist(networks):
				msg = f"============= Step 1 Failed: {clause[2]}:{networks} still exist at {switches[i].rid} =========="
				tprint(msg)
				send_Message(msg)
				step_1 = False
		if step_1: 
			msg = f"============= Step 1 Passed: {clause[2]}: {networks} does NOT exist at all other switches =========="
			tprint(msg)
			send_Message(msg)

		myixia.stop_traffic()
		#myixia.clear_stats()

		for nei in switch1_2_others_neighbor_list:
			nei.remove_all_filters()

		for switch in switches:
			switch.router_bgp.clear_bgp_all()

		for switch in switches: 
			switch.router_bgp.show_bgp_network()
			switch.show_routing_table()

		step_2 = True
		for i in range(1,7):
			if not switches[i].check_route_exist(networks) or not switches[i].router_bgp.check_network_exist(networks):
				msg = f"============= Step 2 Failed: BGP {clause[2]}: {networks} NOT exist at {switches[i].rid} =========="
				tprint(msg)
				send_Message(msg)
				step_2 = False
		if step_2: 
			msg = f"============= Step 2 Passed: BGP {clause[2]}:{networks} exist at ALL other switches =========="
			tprint(msg)
			send_Message(msg)

if testcase == 18 or test_all:
	testcase = 18
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGP community no-advertise"
	print_test_subject(testcase,description)

	if restore_config:
		if CLEAN_ALL:
			switches_cleanup_4_restore(switches)
		for switch in switches:
			file = f"{switch.cfg_file}_case_{testcase}.txt" 
			switch.restore_config(file)

		console_timer(300,msg="wait for 300s after restore config from tftp server")
		for switch in switches:
			switch.relogin()

	###################################################################
	#   Step by Step setup 
	###################################################################

	if test_config: 
		########################################################
		#   Configure OSPF infratructure
		########################################################
		for switch in switches:
			switch.show_switch_info()
			switch.router_ospf.basic_config()
		console_timer(20,msg="After configuring ospf, wait for 20 sec")

		# ########################################################
		# #   Configure iBGP mesh infratructure
		# ########################################################
		for switch in switches:
			switch.router_ospf.neighbor_discovery()
			switch.router_bgp.update_ospf_neighbors()
			switch.router_bgp.clear_config()
			switch.router_bgp.config_ibgp_mesh_loopback()

		console_timer(30,msg="After configuring iBGP sessions via loopbacks, wait for 30s")
		for switch in switches:
			switch.router_ospf.show_ospf_neighbors()
			switch.router_bgp.show_bgp_summary()

		# ########################################################
		# #   configure ACL and Route-map
		# ########################################################
		 
		for switch in switches:
			switch.prefix_list.basic_config()
			switch.aspath_list.basic_config()
			switch.access_list.basic_config()
			switch.community_list.basic_config()
			switch.route_map.clean_up()
			switch.route_map.community_config()
	
		########################################################
		#   Backup the switch's configuration
		########################################################
		tprint("============= Backing up configurations at the start of the test ============")

		for switch in switches:
			file = f"{switch.cfg_file}_case_{testcase}.txt" 
			switch.backup_config(file)

	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	portList = [[ixChassisIpList[0], 2,11,"00:11:01:01:01:01","10.10.1.1",101,"10.1.1.101/24","10.1.1.1"], 
	[ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.20.1.1",102,"10.1.1.102/24","10.1.1.1"]]

	########################################################
	#   Configure eBGP to IXIA ports  
	########################################################
	for switch,ixia_port_info in zip(switches,portList):
		if switch.router_bgp.config_ebgp_ixia(ixia_port_info) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP peers ==============")
			exit()
	
	 
	myixia = IXIA(apiServerIp,ixChassisIpList,portList)

 	
	for topo in myixia.topologies:
		topo.add_ipv4()
	 
	myixia.topologies[0].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=10)
	myixia.topologies[1].add_bgp(dut_ip='10.1.1.2',bgp_type='external',num=10)
	 
	myixia.topologies[0].change_med(1000)
	myixia.topologies[1].change_med(2000)
	 
	 

	myixia.start_protocol(wait=50)

	myixia.create_traffic(src_topo=myixia.topologies[0].topology, dst_topo=myixia.topologies[1].topology,traffic_name="t1_to_t2",tracking_name="Tracking_1")
	myixia.create_traffic(src_topo=myixia.topologies[1].topology, dst_topo=myixia.topologies[0].topology,traffic_name="t2_to_t1",tracking_name="Tracking_2")

	
	myixia.start_traffic()
	myixia.collect_stats()
	myixia.check_traffic()

	myixia.stop_traffic()
	#myixia.clear_stats()

	switch_1 = switches[0]
	switch_2 = switches[1]
	for switch in switches:
		switch.router_bgp.get_neighbors_summary()
		for nei in switch.router_bgp.bgp_neighbors_objs:
			nei.remove_all_filters()

	neighbors = switch_1.router_bgp.bgp_neighbors_objs
	#find out switch_1's ixia neighbor
	for nei in neighbors:
		if nei.id == seperate_ip_mask(portList[0][6])[0]:
			neighbor_ixia_1 = nei
			break
	print(neighbor_ixia_1.id)


	other_switches_2_sw1 = []
	for i in range(1,7):
		neighbors = switches[i].router_bgp.bgp_neighbors_objs
		for nei in neighbors:
			if nei.id == switch_1.rid:
				other_switches_2_sw1.append(nei)
				break
	########################################################################################################
	   
	########################################################################################################
	set_clause_list = [("prefix","deny-prefix-10-10","bgp prefix list in "),
					("aspath","deny-as-101","bgp aspth list in "),
					("distribute","deny-network-10-10","bgp distribute list in "),    
					]
	for clause in set_clause_list:
		if clause[0] == "prefix":
			neighbor_ixia_1.remove_all_filters()
			neighbor_ixia_1.add_prefix_list_in(prefix=clause[1])
		elif clause[0] == "aspath":
			neighbor_ixia_1.remove_all_filters()
			neighbor_ixia_1.add_aspath_in(aspath=clause[1])
		elif clause[0] == "distribute":
			neighbor_ixia_1.remove_all_filters()
			neighbor_ixia_1.add_distribute_list_in(distribute=clause[1])
	 
		for switch in switches:
			switch.router_bgp.clear_bgp_all()
		 
		console_timer(10,msg=f"After clearing BGP, wait for 10 sec")

		for switch in switches: 
			switch.router_bgp.show_bgp_network()
			switch.show_routing_table()

		networks = ["10.10.1.1"]

		step_1 = True
		for i in range(1,7):
			if switches[i].check_route_exist(networks) or switches[i].router_bgp.check_network_exist(networks):
				msg = f"============= Step 1 Failed: BGP {clause[2]}: {networks} still exist at {switches[i].rid} =========="
				tprint(msg)
				send_Message(msg)
				step_1 = False
		if step_1: 
			msg = f"============= Step 1 Passed: BGP {clause[2]}:{networks} does NOT exist at other switches =========="
			tprint(msg)
			send_Message(msg)

		myixia.stop_traffic()
		#myixia.clear_stats()

		neighbor_ixia_1.remove_all_filters()
		 

		for switch in switches:
			switch.router_bgp.clear_bgp_all()

		for switch in switches: 
			switch.router_bgp.show_bgp_network()
			switch.show_routing_table()

		step_2 = True
		for i in range(1,7):
			if not switches[i].check_route_exist(networks) or not switches[i].router_bgp.check_network_exist(networks):
				msg = f"============= Step 2 Failed: BGP {clause[2]}: {networks} NOT exist at {switches[i].rid} =========="
				tprint(msg)
				send_Message(msg)
				step_2 = False
		if step_2: 
			msg = f"============= Step 2 Passed: BGP {clause[2]}:{networks} exist at ALL other switches =========="
			tprint(msg)
			send_Message(msg)

		myixia.start_traffic()
		myixia.collect_stats()
		if myixia.check_traffic():
			msg = f"============= Step 3 Passed: {clause[2]} with IXIA traffic =========="
			tprint(msg)
			send_Message(msg)
		else:
			msg = f"============= Step 3 Failed:  {clause[2]} with IXIA traffic =========="
			tprint(msg)
			send_Message(msg)
		myixia.stop_traffic()
	

	########################################################################################################
	# distribute-list-out, prefix-list-out, aspath-filter-list-out
	########################################################################################################
	set_clause_list = [("prefix","deny-prefix-10-10","bgp prefix list out "),
					("aspath","deny-as-101","bgp aspth list out "),
					("distribute","deny-network-10-10","bgp distribute list out"),    
					]

	# set_clause_list = [ ("distribute","deny-network-10-10","bgp distribute list out")]

	switch_1 = switches[0]
	switch_2 = switches[1]
	for switch in switches:
		switch.router_bgp.get_neighbors_summary()
	neighbors = switch_1.router_bgp.bgp_neighbors_objs
	switch_1_neighbors = neighbors
	#find out switch_1's ixia neighbor
	for nei in neighbors:
		if nei.id == switch_2.rid:
			the_neighbor = nei
			break
	print(the_neighbor.id)

	other_switches_2_sw1 = []
	for i in range(1,7):
		neighbors = switches[i].router_bgp.bgp_neighbors_objs
		for nei in neighbors:
			if nei.id == switch_1.rid:
				other_switches_2_sw1.append(nei)
				break

	other_switches_ids = []
	for i in range(1,7):
		other_switches_ids.append(switches[i].rid)

	switch1_2_others_neighbor_list = []
	for nei in switch_1_neighbors:
		if nei.id in other_switches_ids:
			switch1_2_others_neighbor_list.append(nei)
 
	for clause in set_clause_list:	
		for nei in switch1_2_others_neighbor_list:
			if clause[0] == "prefix":
				nei.remove_all_filters()
				nei.add_prefix_list_out(prefix=clause[1])
			elif clause[0] == "aspath":
				nei.remove_all_filters()
				nei.add_aspath_out(aspath=clause[1])
			elif clause[0] == "distribute":
				nei.remove_all_filters()
				nei.add_distribute_list_out(distribute=clause[1])
		 
		for switch in switches:
			switch.router_bgp.clear_bgp_all()
		 
		console_timer(10,msg=f"After clearing BGP, wait for 10 sec")

		for switch in switches: 
			switch.router_bgp.show_bgp_network()
			switch.show_routing_table()

		networks = ["10.10.1.1"]

		step_1 = True
		for i in range(1,7):
			if switches[i].check_route_exist(networks) or switches[i].router_bgp.check_network_exist(networks):
				msg = f"============= Step 1 Failed: {clause[2]}:{networks} still exist at {switches[i].rid} =========="
				tprint(msg)
				send_Message(msg)
				step_1 = False
		if step_1: 
			msg = f"============= Step 1 Passed: {clause[2]}: {networks} does NOT exist at all other switches =========="
			tprint(msg)
			send_Message(msg)

		myixia.stop_traffic()
		#myixia.clear_stats()

		for nei in switch1_2_others_neighbor_list:
			nei.remove_all_filters()

		for switch in switches:
			switch.router_bgp.clear_bgp_all()

		for switch in switches: 
			switch.router_bgp.show_bgp_network()
			switch.show_routing_table()

		step_2 = True
		for i in range(1,7):
			if not switches[i].check_route_exist(networks) or not switches[i].router_bgp.check_network_exist(networks):
				msg = f"============= Step 2 Failed: BGP {clause[2]}: {networks} NOT exist at {switches[i].rid} =========="
				tprint(msg)
				send_Message(msg)
				step_2 = False
		if step_2: 
			msg = f"============= Step 2 Passed: BGP {clause[2]}:{networks} exist at ALL other switches =========="
			tprint(msg)
			send_Message(msg)


if testcase == 19 or test_all:
	testcase = 19
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGP router reflector"
	print_test_subject(testcase,description)

	if test_config:
		network = BGP_networks(switches)
		network.clear_bgp_config()
		network.build_router_reflector_topo()


	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	portList = [
	[ixChassisIpList[0], 2, 11,"00:11:01:01:01:01","10.10.1.1",101,"10.1.1.101/24","10.1.1.1"], 
	[ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.10.1.1",102,"10.1.1.102/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.20.1.1",103,"10.1.1.103/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.20.1.1",104,"10.1.1.104/24","10.1.1.1"], 
	[ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.20.1.1",105,"10.1.1.105/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.20.1.1",106,"10.1.1.106/24","10.1.1.1"]
	]


	for switch,ixia_port_info in zip(switches,portList):
		if switch.router_bgp.config_ebgp_ixia(ixia_port_info) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP peers ==============")
			exit()
	 

	myixia = IXIA(apiServerIp,ixChassisIpList,portList)

 	
	for topo in myixia.topologies:
		topo.add_ipv4()
	 
	myixia.topologies[0].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=100)
	myixia.topologies[1].add_bgp(dut_ip='10.1.1.2',bgp_type='external',num=100)
	myixia.topologies[2].add_bgp(dut_ip='10.1.1.3',bgp_type='external',num=100)
	myixia.topologies[3].add_bgp(dut_ip='10.1.1.4',bgp_type='external',num=100)
	myixia.topologies[4].add_bgp(dut_ip='10.1.1.5',bgp_type='external',num=100)
	myixia.topologies[5].add_bgp(dut_ip='10.1.1.6',bgp_type='external',num=100)

	 
	myixia.topologies[2].change_med(1000)
	myixia.topologies[5].change_med(2000)
	 
	 

	myixia.start_protocol(wait=50)

	myixia.create_traffic(src_topo=myixia.topologies[0].topology, dst_topo=myixia.topologies[5].topology,traffic_name="t1_to_t6",tracking_name="Tracking_1")
	myixia.create_traffic(src_topo=myixia.topologies[5].topology, dst_topo=myixia.topologies[0].topology,traffic_name="t6_to_t1",tracking_name="Tracking_2")

	
	myixia.start_traffic()
	myixia.collect_stats()
	if myixia.check_traffic():
		msg = f"============= Passed: {description} with IXIA traffic =========="
		tprint(msg)
		send_Message(msg)
	else:
		msg = f"============= Failed:  {description} with IXIA traffic =========="
		tprint(msg)
		send_Message(msg)
	myixia.stop_traffic()


if testcase == 20 or test_all:
	testcase = 20
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGP confederation"
	print_test_subject(testcase,description)

	if test_config:
		network = BGP_networks(switches)
		network.clear_bgp_config()
		network.build_confed_topo_1()

	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	portList = [
	[ixChassisIpList[0], 2, 11,"00:11:01:01:01:01","10.10.1.1",101,"10.1.1.101/24","10.1.1.1"], 
	[ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.10.1.1",102,"10.1.1.102/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.20.1.1",103,"10.1.1.103/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.20.1.1",104,"10.1.1.104/24","10.1.1.1"], 
	[ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.20.1.1",105,"10.1.1.105/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.20.1.1",106,"10.1.1.106/24","10.1.1.1"]
	]


	for switch,ixia_port_info in zip(switches,portList):
		if switch.router_bgp.config_ebgp_ixia(ixia_port_info) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP peers ==============")
			exit()
	 

	myixia = IXIA(apiServerIp,ixChassisIpList,portList)

 	
	for topo in myixia.topologies:
		topo.add_ipv4()
	 
	myixia.topologies[0].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=100)
	myixia.topologies[1].add_bgp(dut_ip='10.1.1.2',bgp_type='external',num=100)
	myixia.topologies[2].add_bgp(dut_ip='10.1.1.3',bgp_type='external',num=100)
	myixia.topologies[3].add_bgp(dut_ip='10.1.1.4',bgp_type='external',num=100)
	myixia.topologies[4].add_bgp(dut_ip='10.1.1.5',bgp_type='external',num=100)
	myixia.topologies[5].add_bgp(dut_ip='10.1.1.6',bgp_type='external',num=100)

	 
	#myixia.topologies[2].change_med(1000)
	myixia.topologies[5].add_aspath(5,65300)
	 
	 

	myixia.start_protocol(wait=50)

	myixia.create_traffic(src_topo=myixia.topologies[0].topology, dst_topo=myixia.topologies[5].topology,traffic_name="t1_to_t6",tracking_name="Tracking_1")
	myixia.create_traffic(src_topo=myixia.topologies[5].topology, dst_topo=myixia.topologies[0].topology,traffic_name="t6_to_t1",tracking_name="Tracking_2")

	
	myixia.start_traffic()
	myixia.collect_stats()
	if myixia.check_traffic():
		msg = f"============= Passed: {description} with IXIA traffic =========="
		tprint(msg)
		send_Message(msg)
	else:
		msg = f"============= Failed:  {description} with IXIA traffic =========="
		tprint(msg)
		send_Message(msg)
	myixia.stop_traffic()


if testcase == 21 or test_all:
	testcase = 21
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGP always compare MED"
	print_test_subject(testcase,description)

	if test_config:
		network = BGP_networks(switches)
		network.clear_bgp_config()
		network.build_ibgp_mesh_topo()

	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	portList = [
	[ixChassisIpList[0], 2, 11,"00:11:01:01:01:01","10.10.1.1",101,"10.1.1.101/24","10.1.1.1"], 
	[ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.10.1.1",102,"10.1.1.102/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.10.1.1",103,"10.1.1.103/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.10.1.1",104,"10.1.1.104/24","10.1.1.1"], 
	[ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.10.1.1",105,"10.1.1.105/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.10.1.1",106,"10.1.1.106/24","10.1.1.1"]
	]

	sw = switches[0]
	for ixia_port_info in portList:
		if sw.router_bgp.config_ebgp_ixia(ixia_port_info) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP peers ==============")
			exit()
	 

	myixia = IXIA(apiServerIp,ixChassisIpList,portList)

 	
	for topo in myixia.topologies:
		topo.add_ipv4()
	 
	myixia.topologies[0].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=10)
	myixia.topologies[1].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=10)
	myixia.topologies[2].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=10)
	myixia.topologies[3].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=10)
	myixia.topologies[4].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=10)
	myixia.topologies[5].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=10)

	 
	myixia.topologies[0].change_med(1000)
	myixia.topologies[1].change_med(2000)
	myixia.topologies[2].change_med(3000)
	myixia.topologies[3].change_med(4000)
	myixia.topologies[4].change_med(5000)
	myixia.topologies[5].change_med(6000)
	#myixia.topologies[5].add_aspath(5,65300)
	 
	myixia.start_protocol(wait=50)

if testcase == 22 or test_all:
	testcase = 22
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGP ignore as path length and strip private AS"
	print_test_subject(testcase,description)

	network = BGP_networks(switches)
	if test_config:	
		network.clear_bgp_config()
		network.build_ibgp_mesh_topo()

	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	portList = [
	[ixChassisIpList[0], 2, 11,"00:11:01:01:01:01","10.10.1.1",101,"10.1.1.101/24","10.1.1.1"], 
	[ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.10.1.1",102,"10.1.1.102/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.10.1.1",103,"10.1.1.103/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.10.1.1",104,"10.1.1.104/24","10.1.1.1"], 
	[ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.10.1.1",105,"10.1.1.105/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.10.1.1",106,"10.1.1.106/24","10.1.1.1"]
	]


	sw = switches[0]
	for ixia_port_info in portList:
		if sw.router_bgp.config_ebgp_ixia(ixia_port_info) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP peers ==============")
			exit()
	 
	 

	myixia = IXIA(apiServerIp,ixChassisIpList,portList)

 	
	for topo in myixia.topologies:
		topo.add_ipv4()
	 
	myixia.topologies[0].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=10)
	myixia.topologies[1].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=10)
	myixia.topologies[2].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=10)
	myixia.topologies[3].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=10)
	myixia.topologies[4].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=10)
	myixia.topologies[5].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=10)

	myixia.topologies[0].change_bgp_routes_attributes(num_path=1,as_base=65010,med=6000,flapping="random",community=3,comm_base=101,weight=111)
	myixia.topologies[1].change_bgp_routes_attributes(num_path=2,as_base=65020,med=5000,flapping="random",community=3,comm_base=102,weight=222)
	myixia.topologies[2].change_bgp_routes_attributes(num_path=3,as_base=65030,med=4000,flapping="random",community=3,comm_base=103,weight=333)
	myixia.topologies[3].change_bgp_routes_attributes(num_path=4,as_base=65040,med=3000,flapping="random",community=3,comm_base=104,weight=444)
	myixia.topologies[4].change_bgp_routes_attributes(num_path=5,as_base=65050,med=2000,flapping="random",community=3,comm_base=105,weight=555)
	myixia.topologies[5].change_bgp_routes_attributes(num_path=6,as_base=65060,med=1000,flapping="random",community=3,comm_base=106,weight=666)
	 

	myixia.start_protocol(wait=50)

if testcase == 23 or test_all:
	testcase = 23
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGP Longevity Test"
	print_test_subject(testcase,description)

	network = BGP_networks(switches)
	if test_config:
		network.clear_bgp_config()
		network.build_ibgp_mesh_topo()

	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	portList = [
	[ixChassisIpList[0], 2, 11,"00:11:01:01:01:01","10.10.1.1",101,"10.1.1.101/24","10.1.1.1"], 
	[ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.20.1.1",102,"10.1.1.102/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.30.1.1",103,"10.1.1.103/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.40.1.1",104,"10.1.1.104/24","10.1.1.1"], 
	[ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.50.1.1",105,"10.1.1.105/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.60.1.1",106,"10.1.1.106/24","10.1.1.1"]
	]


	for switch,ixia_port_info in zip(switches,portList):
		if switch.router_bgp.config_ebgp_ixia(ixia_port_info) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP peers ==============")
			exit()
	 
	myixia = IXIA(apiServerIp,ixChassisIpList,portList)

	for topo in myixia.topologies:
		topo.add_ipv4()
	 
	myixia.topologies[0].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=2000)
	myixia.topologies[1].add_bgp(dut_ip='10.1.1.2',bgp_type='external',num=2000)
	myixia.topologies[2].add_bgp(dut_ip='10.1.1.3',bgp_type='external',num=1000)
	myixia.topologies[3].add_bgp(dut_ip='10.1.1.4',bgp_type='external',num=1000)
	myixia.topologies[4].add_bgp(dut_ip='10.1.1.5',bgp_type='external',num=1000)
	myixia.topologies[5].add_bgp(dut_ip='10.1.1.6',bgp_type='external',num=1000)

	myixia.topologies[0].change_bgp_routes_attributes(num_path=20,as_base=65010,med=6000,flapping="random",community=30,comm_base=101,weight=111)
	myixia.topologies[1].change_bgp_routes_attributes(num_path=21,as_base=65020,med=5000,flapping="random",community=30,comm_base=102,weight=222)
	myixia.topologies[2].change_bgp_routes_attributes(num_path=22,as_base=65030,med=4000,flapping="random",community=30,comm_base=103,weight=333)
	myixia.topologies[3].change_bgp_routes_attributes(num_path=23,as_base=65040,med=3000,flapping="random",community=30,comm_base=104,weight=444)
	myixia.topologies[4].change_bgp_routes_attributes(num_path=24,as_base=65050,med=2000,flapping="random",community=30,comm_base=105,weight=555)
	myixia.topologies[5].change_bgp_routes_attributes(num_path=25,as_base=65060,med=1000,flapping="random",community=30,comm_base=106,weight=666)
	 

	myixia.start_protocol(wait=50)

	myixia.create_traffic(src_topo=myixia.topologies[0].topology, dst_topo=myixia.topologies[1].topology,traffic_name="t1_to_t2",tracking_name="Tracking_1")
	myixia.create_traffic(src_topo=myixia.topologies[1].topology, dst_topo=myixia.topologies[0].topology,traffic_name="t2_to_t1",tracking_name="Tracking_2")

	myixia.create_traffic(src_topo=myixia.topologies[2].topology, dst_topo=myixia.topologies[3].topology,traffic_name="t2_to_t3",tracking_name="Tracking_3")
	myixia.create_traffic(src_topo=myixia.topologies[3].topology, dst_topo=myixia.topologies[2].topology,traffic_name="t3_to_t2",tracking_name="Tracking_4")

	myixia.create_traffic(src_topo=myixia.topologies[4].topology, dst_topo=myixia.topologies[5].topology,traffic_name="t4_to_t5",tracking_name="Tracking_5")
	myixia.create_traffic(src_topo=myixia.topologies[5].topology, dst_topo=myixia.topologies[4].topology,traffic_name="t5_to_t4",tracking_name="Tracking_6")


	myixia.start_traffic()
	myixia.collect_stats()
	myixia.check_traffic()

	while True:
		for router_bgp in network.routers:
			router_bgp.clear_bgp_all()

		console_timer(30,msg="Wait for 30s to clear ip bgp all")

		for router_bgp in network.routers:
			router_bgp.switch.show_log()
			 

if testcase == 24 or test_all:
	testcase = 24
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGP Dynamic Configuration Change"
	print_test_subject(testcase,description)

	network = BGP_networks(switches)
	if test_config:
		network.clear_bgp_config
		network.build_ibgp_mesh_topo()

	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	portList = [
	[ixChassisIpList[0], 2, 11,"00:11:01:01:01:01","10.10.1.1",101,"10.1.1.101/24","10.1.1.1"], 
	[ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.20.1.1",102,"10.1.1.102/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.30.1.1",103,"10.1.1.103/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.40.1.1",104,"10.1.1.104/24","10.1.1.1"], 
	[ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.50.1.1",105,"10.1.1.105/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.60.1.1",106,"10.1.1.106/24","10.1.1.1"]
	]


	for switch,ixia_port_info in zip(switches,portList):
		if switch.router_bgp.config_ebgp_ixia(ixia_port_info) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP peers ==============")
			exit()
	 
	myixia = IXIA(apiServerIp,ixChassisIpList,portList)

	for topo in myixia.topologies:
		topo.add_ipv4()
	 
	myixia.topologies[0].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=2000)
	myixia.topologies[1].add_bgp(dut_ip='10.1.1.2',bgp_type='external',num=2000)
	myixia.topologies[2].add_bgp(dut_ip='10.1.1.3',bgp_type='external',num=1000)
	myixia.topologies[3].add_bgp(dut_ip='10.1.1.4',bgp_type='external',num=1000)
	myixia.topologies[4].add_bgp(dut_ip='10.1.1.5',bgp_type='external',num=1000)
	myixia.topologies[5].add_bgp(dut_ip='10.1.1.6',bgp_type='external',num=1000)

	myixia.topologies[0].change_bgp_routes_attributes(num_path=1,as_base=65010,med=6000,flapping="random",community=10,comm_base=101,weight=111)
	myixia.topologies[1].change_bgp_routes_attributes(num_path=2,as_base=65020,med=5000,flapping="random",community=10,comm_base=102,weight=222)
	myixia.topologies[2].change_bgp_routes_attributes(num_path=3,as_base=65030,med=4000,flapping="random",community=10,comm_base=103,weight=333)
	myixia.topologies[3].change_bgp_routes_attributes(num_path=4,as_base=65040,med=3000,flapping="random",community=10,comm_base=104,weight=444)
	myixia.topologies[4].change_bgp_routes_attributes(num_path=5,as_base=65050,med=2000,flapping="random",community=10,comm_base=105,weight=555)
	myixia.topologies[5].change_bgp_routes_attributes(num_path=6,as_base=65060,med=1000,flapping="random",community=10,comm_base=106,weight=666)
	 

	myixia.start_protocol(wait=50)

	myixia.create_traffic(src_topo=myixia.topologies[0].topology, dst_topo=myixia.topologies[1].topology,traffic_name="t1_to_t2",tracking_name="Tracking_1")
	myixia.create_traffic(src_topo=myixia.topologies[1].topology, dst_topo=myixia.topologies[0].topology,traffic_name="t2_to_t1",tracking_name="Tracking_2")

	myixia.create_traffic(src_topo=myixia.topologies[2].topology, dst_topo=myixia.topologies[3].topology,traffic_name="t2_to_t3",tracking_name="Tracking_3")
	myixia.create_traffic(src_topo=myixia.topologies[3].topology, dst_topo=myixia.topologies[2].topology,traffic_name="t3_to_t2",tracking_name="Tracking_4")

	myixia.create_traffic(src_topo=myixia.topologies[4].topology, dst_topo=myixia.topologies[5].topology,traffic_name="t4_to_t5",tracking_name="Tracking_5")
	myixia.create_traffic(src_topo=myixia.topologies[5].topology, dst_topo=myixia.topologies[4].topology,traffic_name="t5_to_t4",tracking_name="Tracking_6")


	myixia.start_traffic()
	myixia.collect_stats()
	myixia.check_traffic()

	while True:
		network.clear_bgp_config
		network.build_confed_topo_1
		for switch,ixia_port_info in zip(switches,portList):
			if switch.router_bgp.config_ebgp_ixia(ixia_port_info) == False:
				tprint("================= !!!!! Not able to configure IXIA BGP peers ==============")
				exit()

		console_timer(300,msg="Run BGP traffic for 300s on one topology ")
		for router_bgp in network.routers:
			router_bgp.switch.show_log()

		network.clear_bgp_config
		network.build_router_reflector_topo
		for switch,ixia_port_info in zip(switches,portList):
			if switch.router_bgp.config_ebgp_ixia(ixia_port_info) == False:
				tprint("================= !!!!! Not able to configure IXIA BGP peers ==============")
				exit()


		console_timer(300,msg="Run BGP traffic for 300s on one topology ")
		for router_bgp in network.routers:
			router_bgp.switch.show_log()

		network.clear_bgp_config
		network.build_ibgp_mesh_topo
		for switch,ixia_port_info in zip(switches,portList):
			if switch.router_bgp.config_ebgp_ixia(ixia_port_info) == False:
				tprint("================= !!!!! Not able to configure IXIA BGP peers ==============")
				exit()

		for router_bgp in network.routers:
			router_bgp.switch.show_log()

if testcase == 25 or test_all:
	testcase = 25
	description = "BGP multi-path and ibgp over internal/vlan1_2nd"
	print_test_subject(testcase,description)

	network = BGP_networks(switches)
	if test_config:
		network.config_ospf_networks()
		network.clear_bgp_config()
		network.biuld_ibgp_mesh_topo_sys_intf()
		console_timer(20)
	network.show_summary()

	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	portList = [
	[ixChassisIpList[0], 2, 11,"00:11:01:01:01:01","10.10.1.1",101,"10.1.1.101/24","10.1.1.1"], 
	[ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.20.1.1",102,"10.1.1.102/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.30.1.1",103,"10.1.1.103/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.40.1.1",104,"10.1.1.104/24","10.1.1.1"], 
	[ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.50.1.1",105,"10.1.1.105/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.60.1.1",106,"10.1.1.106/24","10.1.1.1"]
	]


	for switch,ixia_port_info in zip(switches,portList):
		if switch.router_bgp.config_ebgp_ixia(ixia_port_info) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP peers ==============")
			exit()
	 
	myixia = IXIA(apiServerIp,ixChassisIpList,portList)

	for topo in myixia.topologies:
		topo.add_ipv4()
	 
	myixia.topologies[0].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=2000)
	myixia.topologies[1].add_bgp(dut_ip='10.1.1.2',bgp_type='external',num=2000)
	myixia.topologies[2].add_bgp(dut_ip='10.1.1.3',bgp_type='external',num=1000)
	myixia.topologies[3].add_bgp(dut_ip='10.1.1.4',bgp_type='external',num=1000)
	myixia.topologies[4].add_bgp(dut_ip='10.1.1.5',bgp_type='external',num=1000)
	myixia.topologies[5].add_bgp(dut_ip='10.1.1.6',bgp_type='external',num=1000)

	myixia.topologies[0].change_bgp_routes_attributes(num_path=1,as_base=65010,med=6000,flapping="random",community=10,comm_base=101,weight=111)
	myixia.topologies[1].change_bgp_routes_attributes(num_path=2,as_base=65020,med=5000,flapping="random",community=10,comm_base=102,weight=222)
	myixia.topologies[2].change_bgp_routes_attributes(num_path=3,as_base=65030,med=4000,flapping="random",community=10,comm_base=103,weight=333)
	myixia.topologies[3].change_bgp_routes_attributes(num_path=4,as_base=65040,med=3000,flapping="random",community=10,comm_base=104,weight=444)
	myixia.topologies[4].change_bgp_routes_attributes(num_path=5,as_base=65050,med=2000,flapping="random",community=10,comm_base=105,weight=555)
	myixia.topologies[5].change_bgp_routes_attributes(num_path=6,as_base=65060,med=1000,flapping="random",community=10,comm_base=106,weight=666)
	 

	myixia.start_protocol(wait=50)

	myixia.create_traffic(src_topo=myixia.topologies[0].topology, dst_topo=myixia.topologies[1].topology,traffic_name="t1_to_t2",tracking_name="Tracking_1")
	myixia.create_traffic(src_topo=myixia.topologies[1].topology, dst_topo=myixia.topologies[0].topology,traffic_name="t2_to_t1",tracking_name="Tracking_2")

	myixia.create_traffic(src_topo=myixia.topologies[2].topology, dst_topo=myixia.topologies[3].topology,traffic_name="t2_to_t3",tracking_name="Tracking_3")
	myixia.create_traffic(src_topo=myixia.topologies[3].topology, dst_topo=myixia.topologies[2].topology,traffic_name="t3_to_t2",tracking_name="Tracking_4")

	myixia.create_traffic(src_topo=myixia.topologies[4].topology, dst_topo=myixia.topologies[5].topology,traffic_name="t4_to_t5",tracking_name="Tracking_5")
	myixia.create_traffic(src_topo=myixia.topologies[5].topology, dst_topo=myixia.topologies[4].topology,traffic_name="t5_to_t4",tracking_name="Tracking_6")


	myixia.start_traffic()
	myixia.collect_stats()
	myixia.check_traffic()


if testcase == 26 or test_all:
	testcase = 26
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGP aggregate route and suppress map"
	print_test_subject(testcase,description)

	network = BGP_networks(switches)
	if test_config:
		network.config_ospf_networks()
		network.clear_bgp_config()
		network.biuld_ibgp_mesh_topo_sys_intf()
		console_timer(20)
	network.show_summary()

	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	portList = [
	[ixChassisIpList[0], 2, 11,"00:11:01:01:01:01","10.10.1.1",101,"10.1.1.101/24","10.1.1.1"], 
	[ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.20.1.1",102,"10.1.1.102/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.30.1.1",103,"10.1.1.103/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.40.1.1",104,"10.1.1.104/24","10.1.1.1"], 
	[ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.50.1.1",105,"10.1.1.105/24","10.1.1.1"],
	[ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.60.1.1",106,"10.1.1.106/24","10.1.1.1"],
	]

	#Assign ixia port to BGP router 
	for bgp_router,ixia_port in zip(network.routers,portList):
		print(ixia_port)
		# bgp_router.ixia_port_info = bgp_router.attach_ixia(ixia_port)
		bgp_router.attach_ixia(ixia_port)

	for router in network.routers:
		if router.ixia_port_info == None:
			continue
		mask_length = 16
		agg_net = find_subnet(router.ixia_network,mask_length)
		router.config_aggregate_summary_only(agg_net,mask_length)

	for switch,ixia_port_info in zip(switches,portList):
		print(switch.router_bgp.ixia_port_info)
		if switch.router_bgp.config_ebgp_ixia(ixia_port_info) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP peers ==============")
			exit()
	
	#configure aggregated address
	
	route_map_name = "unsuppress_1"
	switches[0].route_map.clean_up()
	switches[0].route_map.aspath_map(name=route_map_name,as_num = 101)

	switches[0].router_bgp.bgp_config_unsuppress_map(route_map_name)
		
	myixia = IXIA(apiServerIp,ixChassisIpList,portList)

	for topo in myixia.topologies:
		topo.add_ipv4()
	 
	myixia.topologies[0].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=20)
	myixia.topologies[1].add_bgp(dut_ip='10.1.1.2',bgp_type='external',num=20)
	myixia.topologies[2].add_bgp(dut_ip='10.1.1.3',bgp_type='external',num=10)
	myixia.topologies[3].add_bgp(dut_ip='10.1.1.4',bgp_type='external',num=10)
	myixia.topologies[4].add_bgp(dut_ip='10.1.1.5',bgp_type='external',num=10)
	myixia.topologies[5].add_bgp(dut_ip='10.1.1.6',bgp_type='external',num=10)

	myixia.topologies[0].change_bgp_routes_attributes(num_path=1,as_base=65010,med=6000,flapping="random",community=10,comm_base=101,weight=111)
	myixia.topologies[1].change_bgp_routes_attributes(num_path=2,as_base=65020,med=5000,flapping="random",community=10,comm_base=102,weight=222)
	myixia.topologies[2].change_bgp_routes_attributes(num_path=3,as_base=65030,med=4000,flapping="random",community=10,comm_base=103,weight=333)
	myixia.topologies[3].change_bgp_routes_attributes(num_path=4,as_base=65040,med=3000,flapping="random",community=10,comm_base=104,weight=444)
	myixia.topologies[4].change_bgp_routes_attributes(num_path=5,as_base=65050,med=2000,flapping="random",community=10,comm_base=105,weight=555)
	myixia.topologies[5].change_bgp_routes_attributes(num_path=6,as_base=65060,med=1000,flapping="random",community=10,comm_base=106,weight=666)
	 

	myixia.start_protocol(wait=50)

	myixia.create_traffic(src_topo=myixia.topologies[0].topology, dst_topo=myixia.topologies[1].topology,traffic_name="t1_to_t2",tracking_name="Tracking_1")
	myixia.create_traffic(src_topo=myixia.topologies[1].topology, dst_topo=myixia.topologies[0].topology,traffic_name="t2_to_t1",tracking_name="Tracking_2")

	myixia.create_traffic(src_topo=myixia.topologies[2].topology, dst_topo=myixia.topologies[3].topology,traffic_name="t2_to_t3",tracking_name="Tracking_3")
	myixia.create_traffic(src_topo=myixia.topologies[3].topology, dst_topo=myixia.topologies[2].topology,traffic_name="t3_to_t2",tracking_name="Tracking_4")

	myixia.create_traffic(src_topo=myixia.topologies[4].topology, dst_topo=myixia.topologies[5].topology,traffic_name="t4_to_t5",tracking_name="Tracking_5")
	myixia.create_traffic(src_topo=myixia.topologies[5].topology, dst_topo=myixia.topologies[4].topology,traffic_name="t5_to_t4",tracking_name="Tracking_6")


	myixia.start_traffic()
	myixia.collect_stats()
	myixia.check_traffic()

	# while True:
	# 	network.clear_bgp_config()
	# 	network.build_confed_topo_1()
	# 	for switch,ixia_port_info in zip(switches,portList):
	# 		if switch.router_bgp.config_ebgp_ixia(ixia_port_info) == False:
	# 			tprint("================= !!!!! Not able to configure IXIA BGP peers ==============")
	# 			exit()

	# 	console_timer(300,msg="Run BGP traffic for 300s on one topology ")
	# 	for router_bgp in network.routers:
	# 		router_bgp.switch.show_log()

	# 	network.clear_bgp_config()
	# 	network.build_router_reflector_topo()
	# 	for switch,ixia_port_info in zip(switches,portList):
	# 		if switch.router_bgp.config_ebgp_ixia(ixia_port_info) == False:
	# 			tprint("================= !!!!! Not able to configure IXIA BGP peers ==============")
	# 			exit()


	# 	console_timer(300,msg="Run BGP traffic for 300s on one topology ")
	# 	for router_bgp in network.routers:
	# 		router_bgp.switch.show_log()

	# 	network.clear_bgp_config
	# 	network.build_ibgp_mesh_topo
	# 	for switch,ixia_port_info in zip(switches,portList):
	# 		if switch.router_bgp.config_ebgp_ixia(ixia_port_info) == False:
	# 			tprint("================= !!!!! Not able to configure IXIA BGP peers ==============")
	# 			exit()

	# 	for router_bgp in network.routers:
	# 		router_bgp.switch.show_log()

	# myixia.create_traffic(src_topo=myixia.topologies[0].topology, dst_topo=myixia.topologies[5].topology,traffic_name="t1_to_t6",tracking_name="Tracking_1")
	# myixia.create_traffic(src_topo=myixia.topologies[5].topology, dst_topo=myixia.topologies[0].topology,traffic_name="t6_to_t1",tracking_name="Tracking_2")

	
	# myixia.start_traffic()
	# myixia.collect_stats()
	# if myixia.check_traffic():
	# 	msg = f"============= Passed: {description} with IXIA traffic =========="
	# 	tprint(msg)
	# 	send_Message(msg)
	# else:
	# 	msg = f"============= Failed:  {description} with IXIA traffic =========="
	# 	tprint(msg)
	# 	send_Message(msg)
	# myixia.stop_traffic()

		# myixia.start_traffic()
		# myixia.collect_stats()
		# if myixia.check_traffic():
		# 	msg = f"============= Step 2 Passed: {clause[2]} with IXIA traffic =========="
		# 	tprint(msg)
		# 	send_Message(msg)
		# else:
		# 	msg = f"============= Step 2 Passed:  {clause[2]} with IXIA traffic =========="
		# 	tprint(msg)
		# 	send_Message(msg)
		# myixia.stop_traffic()
	 


	# check_bgp_test_result(testcase,description,switches)
	# result = "Passed"
	# for switch in switches:
	# 	#switch.router_bgp.get_neighbors_summary()
	# 	if not switch.router_bgp.check_neighbor_status():
	# 		result = "Failed"
	# tprint(f"====================== Test case {testcase} is {result} ==========")		




print("###################")
tprint("Test run is DONE")
print("###################")


##################################################################################################################################################
##################################################################################################################################################
