
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
#import settings 
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
CLEAN_BGP = True
CONFIG_BGP = False
OSPF_NEIGHBORS = 6

apiServerIp = '10.105.19.19'
#ixChassisIpList = ['10.105.241.234']
ixChassisIpList = ['10.105.241.234']

portList_v4_v6 = [
[ixChassisIpList[0], 1, 7,"00:11:01:01:01:01","10.1.1.211/24","10.1.1.1","2001:10:1:1::211/64","2001:10:1:1::1",1], 
[ixChassisIpList[0], 1, 8,"00:12:01:01:01:01","10.1.1.212/24","10.1.1.1","2001:10:1:1::212/64","2001:10:1:1::1",1],
[ixChassisIpList[0], 1, 9,"00:13:01:01:01:01","10.1.1.213/24","10.1.1.1","2001:10:1:1::213/64","2001:10:1:1::1",1], 
[ixChassisIpList[0], 1, 10,"00:14:01:01:01:01","10.1.1.214/24","10.1.1.1","2001:10:1:1::214/64","2001:10:1:1::1",1],
[ixChassisIpList[0], 1, 11,"00:15:01:01:01:01","10.1.1.215/24","10.1.1.1","2001:10:1:1::215/64","2001:10:1:1::1",1],
[ixChassisIpList[0], 1, 12,"00:16:01:01:01:01","10.1.1.216/24","10.1.1.1","2001:10:1:1::216/64","2001:10:1:1::1",1]
]

#sys.stdout = Logger("Log/bgp_testing.log")

parser = argparse.ArgumentParser()
parser.add_argument("-r", "--restore", help="restore config file from tftp server", action="store_true")
parser.add_argument("-cb", "--clear_bgp", help="Clear BGP configuration", action="store_true")
parser.add_argument("-m", "--guide", help="print out simple user manual", action="store_true")
parser.add_argument("-c", "--config", help="Configure switches before starting testing", action="store_true")
parser.add_argument("-tc", "--test_config", help="For each test case,configure switches before starting testing", action="store_true")
#parser.add_argument("-a", "--auto", help="Run in fully automated mode without manually unplugging cables", action="store_true")
parser.add_argument("-u", "--fibercut", help="Run in manual mode when unplugging cables", action="store_true")
parser.add_argument("-t", "--testbed", type=str, help="Specific which testbed to run this test. Valid options:\
					1)548D 2)448D 3)FG-548D 4)FG-448D")
parser.add_argument("-file", "--file", type=str, help="Specific file name appendix when exporting to excel. Example:mac-1k. Default=none")
parser.add_argument("-x", "--ixia", help=" Use IXIA only, skipping login to devices",action="store_true")
parser.add_argument("-n", "--run_time", type=int, help="Specific how many times you want to run the test, default=2")
parser.add_argument("-test", "--testcase", type=str, help="Specific which test case you want to run. Example: 1/1-3/1,3,4,7 etc")
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
IPV6 = False
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
if args.clear_bgp:
	clear_bgp = True
	CLEAN_BGP = True
	print_title("Clear BGP Configuration Before Test Starts")
else:
	clear_bgp = False
if args.restore:
	restore_config = True
	print_title("Restore config from tftp server")
else:
	restore_config = False

if args.sa_upgrade:
	upgrade_sa = True
	sw_build = args.sa_upgrade
	print_title(f"**Upgrade FSW software in standalone mode to build {sw_build}")
else:
	upgrade_sa = False
if args.upgrade:
	upgrade_fgt = True
	sw_build = args.upgrade
	print_title(f"Upgrade FSW software via via Fortigate to build {sw_build}")
else:
	upgrade_fgt = False
if args.verbose:
	settings.DEBUG = True
	print_title("Running the test in verbose mode")
else:
	settings.DEBUG = False
	print_title("Running the test in silent mode") 
if args.config:
	setup = True
	print_title("Before starting testing, configure devices")
else:
	setup = False   
	print_title("Skip setting up testbed and configuring devices")  
if args.test_config:
	test_config = True
	print_title("Before starting each test case, configure devices based on each test case scenario")
else:
	test_config = False 
	CLEAN_BGP = False  
	 
# if args.auto:
# 	mode='auto'
if args.log_mac:
	log_mac_event = True
	print_title("Running test with port log-mac-event enabled")
else:
	print_title("Running test with port log-mac-event disable")
	log_mac_event = False
if args.factory:
	factory = True
	print_title("Will factory reset each FSW ")
else:
	factory = False
	print_title("Will NOT factory reset each FSW")
if args.fibercut:
	mode='manual'
	print_title("Fiber cut test will be in manual mode")
else:
	mode = 'auto'
	print_title("Fiber cut test will be in automated mode")
if args.testbed:
	test_setup = args.testbed
	print_title("Test Bed = {}".format(test_setup))
else:
	print_title("Not test bed is needed for this run" )
	test_setup = None
if args.ixia:
	ixia_only = True
	print_title("Only use IXIA setup without logging into devices ")
else:
	ixia_only = False
if args.file:
	file_appendix = args.file
	print_title("Export test ressult to file with appendix: {}".format(file_appendix))
if args.run_time:
	Run_time = args.run_time
	print_title("Test iterate numbers = {}".format(Run_time))
else:
	Run_time = 1
	print_title("Test iterate numbers = {}".format(Run_time))
if args.testcase:
	try:
		testcase = int(args.testcase)
	except:
		testcase = (args.testcase)
		if testcase == "ipv6":
			print_title("Test all IPv6 cases")
			IPV6 = True
		else:
			IPV6 = False
	test_all = False
	print_title("Test Case To Run: #{}".format(testcase))
else:
	test_all = True
	testcase = 0
	print_title("All Test Case To Be Run:{}".format(test_all))
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
		switch.router_ospf.remove_ospf_all()
	for switch in switches:
		switch.router_bgp.clear_config_all()

def test_config_igp_ipv6_fabric(*args,**kwargs):
	ospf_config_v4 = False
	ospf_config_v6 = False
	#Config OSPF infra
	for switch in switches:
		switch.show_switch_info()
		switch.router_ospf.neighbor_discovery_all()
		switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)
		if not switch.router_ospf.ospf_neighbor_all_up_v4(num=OSPF_NEIGHBORS):
			switch.router_ospf.basic_config_fabric()
			ospf_config_v4 = True
		else:
			Info(f"All OSPFv4 neighbors are up on switch {switch.loop0_ip}, No need to config OSPF ")
		if not switch.router_ospf.ospf_neighbor_all_up_v6(num=OSPF_NEIGHBORS):
			switch.router_ospf.basic_config_v6_fabric()
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

def update_igp_database_all(*args,**kwargs):
	dut_switches = kwargs["switches"]
	#Config OSPF infra
	for switch in dut_switches:
		switch.router_ospf.neighbor_discovery_all()
		switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)

def test_config_igp_ipv6(*args,**kwargs):
	ospf_config_v4 = False
	ospf_config_v6 = False
	#Config OSPF infra
	dut_switches = kwargs["switches"]

	for switch in dut_switches:
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
	for switch in dut_switches:
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

if not ixia_only:
	dut_dir_list = bgpv6_testbed_init()

##################################### Pre-Test setup and configuration #############################
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
	if testcase == 0:
		exit()

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
		dut_name = dut_dir['name']
		if platform == "fortinet":
			# dut = get_switch_telnet_connection_new(dut_com,dut_port,platform=dut_dir['platform'])
			# dut_dir['telnet'] = dut
			dut = dut_dir['telnet']
			relogin_factory_reset(dut=dut,host=dut_name)

	for dut_dir in dut_dir_list:
		dut = dut_dir['telnet']
		dut_name = dut_dir['name']
		platform = dut_dir['platform']
		if platform == "fortinet":
			image = find_dut_image(dut)
			tprint(f"============================ {dut_name} software image = {image}")
			sw_init_config_v6(device=dut_dir,config_split =True)

	if testcase == 0:
		exit()

if setup: 
	for dut_dir in dut_dir_list:
		dut = dut_dir['telnet']
		dut_name = dut_dir['name']
		platform = dut_dir['platform']
		if platform == "fortinet":
			image = find_dut_image(dut)
			tprint(f"============================ {dut_name} software image = {image}")
			sw_init_config_v6(device=dut_dir)
	if testcase == 0:
		exit()

	# console_timer(30,msg="After intial configuration, show switch related information")
	# switches = [FortiSwitch(dut_dir) for dut_dir in dut_dir_list]
	# for switch in switches:
	# 		switch.router_ospf.show_ospf_neighbors()
	# 		switch.router_bgp.show_bgp_summary()
	# 	# Develop new codes starts from here
	# 	# stop_threads = False
	# 	# dut_cpu_memory(dut_dir_list,lambda: stop_threads)


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
	
	if testcase == 0:
		exit()

if not ixia_only:
	switches = [FortiSwitch(dut_dir) for dut_dir in dut_dir_list]
	fsw_switches =switches[1:]

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

if testcase == 6011 or test_all or IPV6:
	testcase = 6011
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "Test IPv6 iBGP via loopbacks IPv6 address"
	print_test_subject(testcase,description)

	fsw_switches =switches[1:]
	if clear_bgp:
		test_clean_config(switches =fsw_switches)

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
		switch.router_bgp.config_ibgp_mesh_loopback_v6() 
		switch.router_bgp.config_ibgp_mesh_loopback_v4()  
	console_timer(30,msg="After configuring iBGPv6 sessions via loopbacks, wait for 30s")
	for switch in switches:
		switch.router_bgp.show_bgp_summary_v6()


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


if testcase == 6012 or test_all or IPV6:
	testcase = 6012
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "Test IPv6 iBGP via loopbacks IPv4 and IPv6 addresses"
	tags = ["basic ibgp","basic bfd"]
	print_test_subject(testcase,description)

	fsw_switches =switches[1:]

	if clear_bgp:
		test_clean_config(switches =fsw_switches)

	test_config_igp_ipv6_fabric(switches =fsw_switches)

	for switch in switches:  
		switch.router_bgp.config_ibgp_mesh_loopback_v6() 
		switch.router_bgp.config_ibgp_mesh_loopback_v4()  
	console_timer(30,msg="After configuring iBGPv6 sessions via loopbacks, wait for 30s")
	for switch in switches:
		switch.router_bgp.show_bgp_summary_v6()

	for switch in switches:
		switch.router_bgp.config_bgp_bfd_all_neighbors('enable')

	console_timer(20,msg="===== After configuring iBGPv6 sessions via loopbacks && enable BFD, wait for 20s =====")
	for switch in switches:
		switch.router_bgp.show_bgp_summary_v6()
		switch.router_bgp.show_bfd_neighbor_v6()
		router_bfd = Router_BFD(switch)
		router_bfd.counte_peers_v6()

	check_bgp_test_result_v6(testcase,description,fsw_switches)

	console_timer(20,msg="===== After configuring iBGPv6 sessions via loopbacks && enable BFD, wait for 20s =====")
	for switch in switches:
		switch.router_ospf.show_ospf_neighbors_v6()
		switch.router_bgp.show_bgp_summary_v6()
		switch.show_routing_v6()

	check_bgp_test_result_v6(testcase,description,switches)

	#Uncomment the following lines later
	for switch in switches:
		switch.router_bgp.config_bgp_bfd_all_neighbors('disable')

	console_timer(20,msg="=======After disable BFD, wait for 20s ======")
	for switch in switches:
		switch.router_bgp.show_bgp_summary_v6()
		switch.router_bgp.show_bfd_neighbor_v6()
		router_bfd = Router_BFD(switch)
		router_bfd.counte_peers_v6()

	check_bgp_test_result_v6(testcase,description,switches)


if testcase == 6013 or test_all or IPV6: #template for basic ipv4 and ipv6 iBGP
	testcase = 6013
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = """Test IPv6 iBGP via loopbacks IPv4 and IPv6 addresses, alternate activate and activate6
	This is for test cases: 952713,952715,952716,952717
	"""

	fsw_switches =switches[1:]
	if clear_bgp:
		test_clean_config(switches =fsw_switches)
	 
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

if testcase == 6014 or test_all or IPV6:
	testcase = 6014
	description = "iBGP mesh over internal_v6,vlan1_ipv6 and loop0_ipv6. "
	print_test_subject(testcase,description)

	fsw_switches =switches[1:]
	network = BGP_networks(fsw_switches)
	if clear_bgp:
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

if testcase == 6015 or test_all or IPV6:
	testcase = 6015
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "Test IPv6 iBGP via loopbacks IPv4 and IPv6 addresses and bfd flap, finally reboot the devices"
	tags = ["basic ibgp","flap bfd", "reboot"]
	print_test_subject(testcase,description)

	fsw_switches =switches[1:]

	if clear_bgp:
		test_clean_config(switches =fsw_switches)

	test_config_igp_ipv6_fabric(switches =fsw_switches)


	for switch in switches:  
		switch.router_bgp.config_ibgp_mesh_loopback_v6() 
		switch.router_bgp.config_ibgp_mesh_loopback_v4()  
	console_timer(30,msg="After configuring iBGPv6 sessions via loopbacks, wait for 30s")
	for switch in switches:
		switch.router_bgp.show_bgp_summary_v6()


	for i in range(1,100):
		Info(f"==================================== Iterating #{i}: Enable and Disable BFD over BGP ========================")
		for switch in switches:
			switch.router_bgp.config_bgp_bfd_all_neighbors('enable')

		console_timer(20,msg="===== After configuring iBGPv6 sessions via loopbacks && enable BFD, wait for 20s =====")
		for switch in switches:
			switch.router_bgp.show_bgp_summary_v6()
			switch.router_bgp.show_bfd_neighbor_v6()
			router_bfd = Router_BFD(switch)
			router_bfd.counte_peers_v6()

		for switch in switches:
			switch.router_ospf.show_ospf_neighbors_v6()
			switch.router_bgp.show_bgp_summary_v6()
			switch.show_routing_v6()

		
		#Uncomment the following lines later
		for switch in switches:
			switch.router_bgp.config_bgp_bfd_all_neighbors('disable')


	for switch in switches:
		switch.router_bgp.config_bgp_bfd_all_neighbors('enable')


	for sw in fsw_switches:
		sw.reboot()
	console_timer(300,msg="===== rebooting all switches, wait for 300s =====")
	for sw in fsw_switches:
		sw.relogin()

	check_bgp_test_result_v6(testcase,description,switches)

if testcase == 6016 or test_all or IPV6:
	testcase = 6016
	description = "iBGP mesh over 2nd IPv6 address over internal_v6,vlan1_ipv6 and loop0_ipv6, bfd, flap "
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	tags = "ipv6 2nd"
	print_test_subject(testcase,description)

	fsw_switches =switches[1:]
	network = BGP_networks(fsw_switches)

	if clear_bgp:
		test_clean_config(switches =fsw_switches)
	if test_config:
		test_config_igp_ipv6(switches =fsw_switches)
	else:
		update_igp_database_all(switches =fsw_switches)
		
	for sw in fsw_switches:
		sw.add_extra_ipv6_no_fw()

	exit()
	network.biuld_ibgp_mesh_topo_sys_intf_v6_2nd()
	console_timer(60,msg=f"!!!!!!!!!!! Step 0: Start From No FW Configured. After configuring fully mesh iBGP across all IPv6 system interfaces, check bgp neighbors")
	for sw in fsw_switches:
		sw.show_command("show system interface")

	network.ping_sweep_v6_extensive()
	for sw in fsw_switches:
		sw.collect_linux_cmd(sw_name=sw.name,cmd="ip6tables -L g_in_runn -nv  | grep 179")

	network.show_summary()

	for sw in fsw_switches:
		sw.turn_on_ipv6_fw()

	console_timer(60,msg=f"!!!!!!!!!!!  Step 1: Configure FSW. After configuring FW, check bgp neighbors")
	for sw in fsw_switches:
		sw.show_command("show system interface")
		 
	network.ping_sweep_v6_extensive()
	for sw in fsw_switches:
		sw.collect_linux_cmd(sw_name=sw.name,cmd="ip6tables -L g_in_runn -nv  | grep 179")

	network.show_summary()

	for sw in fsw_switches:
		sw.reboot()
	console_timer(300,msg="After configuring FW: rebooting all switches after configuring FW, wait for 300s =====")
	for sw in fsw_switches:
		sw.relogin()

	console_timer(60,msg=f"!!!!!!!!!!!!! Step 2: Reboot. After configuring FW and rebooting devices check bgp status....")
	for sw in fsw_switches:
		sw.show_command("show system interface")

	network.ping_sweep_v6_extensive()
	for sw in fsw_switches:
		sw.collect_linux_cmd(sw_name=sw.name,cmd="ip6tables -L g_in_runn -nv  | grep 179")

	network.show_summary()

	for sw in fsw_switches:
		sw.remove_firewall_sys_interface()

	console_timer(60,msg=f"!!!!!!!!!!!!! Step 3: Remove FW.  After removing firewall config, wait and check bgp status ")
	for sw in fsw_switches:
		sw.show_command("show system interface")


	network.ping_sweep_v6_extensive()
	for sw in fsw_switches:
		sw.collect_linux_cmd(sw_name=sw.name,cmd="ip6tables -L g_in_runn -nv  | grep 179")

	network.show_summary()

	for sw in fsw_switches:
		sw.reboot()
	console_timer(300,msg="===== rebooting all switches, wait for 300s =====")
	for sw in fsw_switches:
		sw.relogin()

	console_timer(20,msg=f"!!!!!!!!!!!! Step 4: Reboot: After removing FSW and rebooting devices,check bgp status....")
	for sw in fsw_switches:
		sw.show_command("show system interface")

	network.ping_sweep_v6_extensive()
	for sw in fsw_switches:
		sw.collect_linux_cmd(sw_name=sw.name,cmd="ip6tables -L g_in_runn -nv  | grep 179")
	network.show_summary()
	# for _ in range(20):
	# 	for switch in fsw_switches:
	# 		switch.router_bgp.config_bgp_bfd_all_neighbors('enable')

	# 	console_timer(20,msg="===== After configuring iBGPv6 sessions via loopbacks, svi and LLOC intf && enable BFD, wait for 20s =====")
	# 	for switch in fsw_switches:
	# 		switch.router_bgp.show_bgp_summary_v6()
	# 		switch.router_bgp.show_bfd_neighbor_v6()
	# 		router_bfd = Router_BFD(switch)
	# 		router_bfd.counte_peers_v6()

	# 	for switch in fsw_switches:
	# 		switch.router_bgp.config_bgp_bfd_all_neighbors('disable')

	# console_timer(20,msg="===== After configuring iBGPv6 sessions via loopbacks && disable BFD, wait for 20s =====")
	# for switch in fsw_switches:
	# 	switch.router_bgp.show_bgp_summary_v6()
	# 	switch.router_bgp.show_bfd_neighbor_v6()

	# console_timer(20,msg="=======After configuring iBGPv6 sessions via loopbacks && disable BFD, wait for 20s ======")
	# for switch in fsw_switches:
	# 	switch.router_ospf.show_ospf_neighbors_v6()
	# 	switch.router_bgp.show_bgp_summary_v6()
	# 	switch.show_routing_v6()

	# check_bgp_test_result_v6(testcase,description,fsw_switches)

if testcase == 6017 or test_all or IPV6:
	testcase = 6017
	description = "iBGP mesh over 2nd IPv6 address over single internal_v6,vlan1_ipv6 and loop0_ipv6, bfd, flap "
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	tags = "ipv6 2nd single"
	print_test_subject(testcase,description)

	fsw_switches =switches[1:]
	network = BGP_networks(fsw_switches)

	if clear_bgp:
		test_clean_config(switches =fsw_switches)
	if test_config:
		test_config_igp_ipv6(switches =fsw_switches)
	else:
		update_igp_database_all(switches =fsw_switches)
		
	for sw in fsw_switches:
		sw.add_extra_ipv6_no_fw()

	SKIP = True
	interface_list = ["vlan1","loop0"]
	for intf in interface_list:
		network.biuld_ibgp_mesh_topo_sys_intf_v6_2nd(interface=intf)
		console_timer(120,msg=f"!!!!!!!!!!! Step 0: Start From No FW Configured. After configuring fully mesh iBGP across {intf}, check bgp neighbors")

		network.show_summary()

		for sw in fsw_switches:
			sw.reboot()
		console_timer(300,msg="===== rebooting all switches, wait for 300s =====")
		for sw in fsw_switches:
			sw.relogin()
		network.show_summary()

		for switch in switches:
			switch.router_bgp.delete_all_neighbors_v6()

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

if testcase == 6021 or test_all or IPV6:
	testcase = 6021
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "iBGP v6 SVI interface"
	print_test_subject(testcase,description)

	fsw_switches =switches[1:]
	 
	if clear_bgp:
		test_clean_config(switches =fsw_switches)

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

 
if testcase == 6022 or test_all or IPV6:
	testcase = 6022
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "iBGP v6 and v4 SVI interface"
	print_test_subject(testcase,description)

	fsw_switches =switches[1:]
	if clear_bgp:
		test_clean_config(switches =fsw_switches)

	 
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

if testcase == 6023 or test_all or IPV6:
	testcase = 6023
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "iBGP on v6 and v4 SVI interface, alternate address faimily"
	print_test_subject(testcase,description)

	fsw_switches =switches[1:]
	if clear_bgp:
		test_clean_config(switches =fsw_switches)


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
 
if testcase == 6024 or test_all or IPV6:
	testcase = 6024
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "iBGP on Link Local Address + iBGP over SVI + BFD"
	tags ["basic link local", "bfd"]
	print_test_subject(testcase,description)

	fsw_switches =switches[1:]
	if clear_bgp:
		test_clean_config(switches =fsw_switches)

	if clear_bgp:
		test_clean_config(switches =fsw_switches)


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

 
if testcase == 6025 or test_all or IPV6:
	testcase = 6025
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "Negative Testing: iBGP on all interfaces: loopback,SVI And Link Local Address, Enable BFD"
	tags = ["link local bfd","all interfaces bfd"]
	print_test_subject(testcase,description)


	fsw_switches =switches[1:]
	network = BGP_networks(fsw_switches)

	if clear_bgp:
		test_clean_config(switches =fsw_switches)
	if test_config:
		test_config_igp_ipv6(switches =fsw_switches)
	else:
		update_igp_database_all(switches =fsw_switches)
	network.ping_sweep_v6()

	for switch in fsw_switches:
		switch.router_ospf.show_ospf_neighbors_v6()

	for switch in fsw_switches:  
		# switch.router_ospf.neighbor_discovery_all()
		# switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)
		switch.discover_ipv6_neighbors()
		switch.router_bgp.config_ibgp_mesh_svi_v6() #config IPv6 over svi 
		switch.router_bgp.config_ibgp_mesh_direct() #config IPv4 over svi 
		switch.router_bgp.update_ipv6_neighbor_cache()
		switch.router_bgp.config_ibgp_mesh_link_local() #config link local
		switch.router_bgp.config_ibgp_mesh_loopback_v6() #config IPv6 over loopback
		switch.router_bgp.config_ibgp_mesh_loopback_v4()  #config IPv4 over loopback

	console_timer(60,msg="After configuring iBGP sessions over loopback, svi and link local address, wait for 60s")

	for switch in fsw_switches:
		switch.router_bgp.config_bgp_bfd_all_neighbors('enable')

	console_timer(20,msg="===== After configuring iBGPv6 sessions via loopbacks, svi and LLOC intf && enable BFD, wait for 20s =====")
	for switch in fsw_switches:
		switch.router_bgp.show_bgp_summary_v6()
		switch.router_bgp.show_bfd_neighbor_v6()
		router_bfd = Router_BFD(switch)
		router_bfd.counte_peers_v6()

	check_bgp_test_result_v6(testcase,description,fsw_switches)

	for switch in switches:
		switch.router_bgp.config_bgp_bfd_all_neighbors('disable')

	console_timer(20,msg="===== After configuring iBGPv6 sessions via loopbacks && disable BFD, wait for 20s =====")
	for switch in switches:
		switch.router_bgp.show_bgp_summary_v6()
		switch.router_bgp.show_bfd_neighbor_v6()

if testcase == 60250 or test_all or IPV6:
	testcase = 60250
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "Negative Testing: iBGP on all interfaces: loopback,SVI Except Link Local Address, Enable BFD"
	tags = ["Exclude link local bfd","all interfaces bfd"]
	print_test_subject(testcase,description)


	fsw_switches =switches[1:]
	network = BGP_networks(fsw_switches)

	if clear_bgp:
		test_clean_config(switches =fsw_switches)
	if test_config:
		test_config_igp_ipv6(switches =fsw_switches)

	update_igp_database_all(switches =fsw_switches)
	network.ping_sweep_v6()

	for switch in fsw_switches:
		switch.router_ospf.show_ospf_neighbors_v6()

	for switch in fsw_switches:  
		# switch.router_ospf.neighbor_discovery_all()
		# switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)
		switch.discover_ipv6_neighbors()
		switch.router_bgp.config_ibgp_mesh_svi_v6() #config IPv6 over svi 
		switch.router_bgp.config_ibgp_mesh_direct() #config IPv4 over svi 
		switch.router_bgp.update_ipv6_neighbor_cache()
		#switch.router_bgp.config_ibgp_mesh_link_local() #config link local
		switch.router_bgp.config_ibgp_mesh_loopback_v6() #config IPv6 over loopback
		switch.router_bgp.config_ibgp_mesh_loopback_v4()  #config IPv4 over loopback

	console_timer(60,msg="After configuring iBGP sessions over loopback, svi and link local address, wait for 60s")

	for switch in fsw_switches:
		switch.router_bgp.config_bgp_bfd_all_neighbors('enable')

	console_timer(20,msg="===== After configuring iBGPv6 sessions via loopbacks, svi and LLOC intf && enable BFD, wait for 20s =====")
	for switch in fsw_switches:
		switch.router_bgp.show_bgp_summary_v6()
		switch.router_bgp.show_bfd_neighbor_v6()
		router_bfd = Router_BFD(switch)
		router_bfd.counte_peers_v6()

	#check_bgp_test_result_v6(testcase,description,fsw_switches)

	# for switch in switches:
	# 	switch.router_bgp.config_bgp_bfd_all_neighbors('disable')

	# console_timer(20,msg="===== After configuring iBGPv6 sessions via loopbacks && disable BFD, wait for 20s =====")
	# for switch in switches:
	# 	switch.router_bgp.show_bgp_summary_v6()
	# 	switch.router_bgp.show_bfd_neighbor_v6()

if testcase == 60251 or test_all or IPV6:
	testcase = 60251
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "Negative Testing: iBGP on all interfaces: loopback,SVI And Link Local Address, Enable and Delete BFD"
	tags = ["link local bfd","all interfaces bfd", "delete bfd sessions"]
	print_test_subject(testcase,description)


	fsw_switches =switches[1:]

	if clear_bgp:
		test_clean_config(switches =fsw_switches)
	if test_config:
		test_config_igp_ipv6(switches =fsw_switches)

	update_igp_database_all(switches =fsw_switches)

	for switch in fsw_switches:
		switch.router_ospf.show_ospf_neighbors_v6()

	for switch in fsw_switches:  
		# switch.router_ospf.neighbor_discovery_all()
		# switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)
		switch.discover_ipv6_neighbors()
		switch.router_bgp.config_ibgp_mesh_svi_v6() #config IPv6 over svi 
		switch.router_bgp.config_ibgp_mesh_direct() #config IPv4 over svi 
		switch.router_bgp.update_ipv6_neighbor_cache()
		switch.router_bgp.config_ibgp_mesh_link_local() #config link local
		switch.router_bgp.config_ibgp_mesh_loopback_v6() #config IPv6 over loopback
		switch.router_bgp.config_ibgp_mesh_loopback_v4()  #config IPv4 over loopback

	for switch in fsw_switches:
		switch.clear_crash_log()
       

	console_timer(60,msg="After configuring iBGP sessions over loopback, svi and link local address, wait for 60s")

	for switch in fsw_switches:
		switch.router_bgp.config_bgp_bfd_all_neighbors('enable')

	console_timer(20,msg="===== After configuring iBGPv6 sessions via loopbacks, svi and LLOC intf && enable BFD, wait for 20s =====")
	for switch in fsw_switches:
		switch.router_bgp.show_bgp_summary_v6()
		switch.router_bgp.show_bfd_neighbor_v6()
		router_bfd = Router_BFD(switch)
		router_bfd.counte_peers_v6()

	#check_bgp_test_result_v6(testcase,description,fsw_switches)

	for switch in switches:
		switch.router_bgp.delete_all_neighbors_v6()

	for switch in fsw_switches:
		switch.find_crash()
       

	console_timer(20,msg="===== After configuring iBGPv6 sessions via loopbacks && disable BFD, wait for 20s =====")
	for switch in switches:
		switch.router_bgp.show_bgp_summary_v6()
		switch.router_bgp.show_bfd_neighbor_v6()


if testcase == 6026 or test_all or IPV6:
	testcase = 6026
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "Negative Testing: iBGP on all interfaces: loopback,SVI And Link Local Address, Enable BFD and Flap"
	tags = ["link local bfd","all interfaces bfd", "bfd flapping"]
	print_test_subject(testcase,description)


	fsw_switches =switches[1:]

	if clear_bgp:
		test_clean_config(switches =fsw_switches)
	if test_config:
		test_config_igp_ipv6(switches =fsw_switches)

	for switch in fsw_switches:
		switch.router_ospf.show_ospf_neighbors_v6()

	for switch in fsw_switches:  
		# switch.router_ospf.neighbor_discovery_all()
		# switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)
		switch.discover_ipv6_neighbors()
		switch.router_bgp.config_ibgp_mesh_svi_v6() #config IPv6 over svi 
		switch.router_bgp.config_ibgp_mesh_direct() #config IPv4 over svi 
		switch.router_bgp.update_ipv6_neighbor_cache()
		switch.router_bgp.config_ibgp_mesh_link_local() #config link local
		switch.router_bgp.config_ibgp_mesh_loopback_v6() #config IPv6 over loopback
		switch.router_bgp.config_ibgp_mesh_loopback_v4()  #config IPv4 over loopback

	console_timer(60,msg="After configuring iBGP sessions over loopback, svi and link local address, wait for 60s")

	for _ in range(10):

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
			switch.find_crash()

if testcase == 6027 or test_all or IPV6:
	testcase = 6027
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "Negative Testing: iBGP on 2nd IPv6: Enable BFD and Flap"
	tags = ["2nd ipv6","bfd flapping"]
	print_test_subject(testcase,description)


	fsw_switches =switches[1:]

	if clear_bgp:
		test_clean_config(switches =fsw_switches)
	if test_config:
		test_config_igp_ipv6(switches =fsw_switches)

	for switch in fsw_switches:
		switch.router_ospf.show_ospf_neighbors_v6()

	for switch in fsw_switches:  
		# switch.router_ospf.neighbor_discovery_all()
		# switch.router_bgp.update_ospf_neighbors_all(sw_list=switches)
		switch.discover_ipv6_neighbors()
		switch.router_bgp.config_ibgp_mesh_svi_v6() #config IPv6 over svi 
		switch.router_bgp.config_ibgp_mesh_direct() #config IPv4 over svi 
		switch.router_bgp.update_ipv6_neighbor_cache()
		switch.router_bgp.config_ibgp_mesh_link_local() #config link local
		switch.router_bgp.config_ibgp_mesh_loopback_v6() #config IPv6 over loopback
		switch.router_bgp.config_ibgp_mesh_loopback_v4()  #config IPv4 over loopback

	console_timer(60,msg="After configuring iBGP sessions over loopback, svi and link local address, wait for 60s")

	for _ in range(10):

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
			switch.find_crash()


	
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

if testcase == 6031 or test_all or IPV6:
	testcase = 6031
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "Test IPv6 redistrubted connected"
	print_test_subject(testcase,description)

	fsw_switches =switches[1:]
	if clear_bgp:
		test_clean_config(switches =fsw_switches)
	 

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

if testcase == 6 or test_all :
	testcase = 6
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "eBGP direct connection"
	print_test_subject(testcase,description)

	if clear_bgp:
		test_clean_config(switches =fsw_switches)

	for switch in switches:
		switch.vlan_neighors(switches)
		switch.show_vlan_neighbors()
		switch.router_bgp.config_ebgp_mesh_direct()
	console_timer(60,msg="After configuring eBGP sessions, wait for 60s")
	for switch in switches:
		switch.show_routing()

if testcase == 6061 or test_all or IPV6:
	testcase = 6061
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "eBGP v6 only direct connection via SVI interfaces"
	print_test_subject(testcase,description)

	# Clean up configuration before start testing
	fsw_switches =switches[1:]
	if clear_bgp:
		test_clean_config(switches =fsw_switches)
	

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

if testcase == 6062 or test_all or IPV6:
	testcase = 6062
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "eBGP v4 and v6 direct connection via SVI interfaces"
	tag = "ebgp mesh"
	print_test_subject(testcase,description)

	# Clean up configuration before start testing

	fsw_switches =switches[1:]
	if clear_bgp:
		test_clean_config(switches =fsw_switches)
	if clear_bgp:
		test_clean_config(switches =fsw_switches)


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


if testcase == 6063 or test_all or IPV6:
	testcase = 6063
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "eBGP v4 and v6 direct connection via SVI interfaces"
	print_test_subject(testcase,description)

	# Clean up configuration before start testing
	if clear_bgp:
		test_clean_config(switches =fsw_switches)

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

if testcase == 6064 or test_all or IPV6:
	testcase = 6064
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "eBGP v6 direct connection via SVI interfaces, remove private AS, delete community"
	tag1 = ["remove private as","change community","delete community"]
	print_test_subject(testcase,description)


	ixia_ipv6_as_list = [65101,65102,65103,65104,65105,65106]
	ipv6_networks = ["2001:101:1:1::1","2001:102:1:1::1","2001:103:1:1::1","2001:104:1:1::1","2001:105:1:1::1","2001:106:1:1::1"]
	ipv4_networks = ["10.10.1.1","10.10.2.1","10.10.3.1","10.10.4.1","10.10.5.1","10.10.6.1"]

	fsw_switches =switches[1:]

	if clear_bgp:
		test_clean_config(switches =fsw_switches)

	test_config_igp_ipv6(switches =fsw_switches)
	for switch in fsw_switches:
		switch.router_bgp.config_ebgp_mesh_svi_v4()
		switch.router_bgp.config_ebgp_mesh_svi_v6()
	console_timer(60,msg="After configuring eBGP sessions, wait for 60s")
	# for switch in switches:
	# 	switch.show_routing_v6()
	for switch, ixia_port_info, ixia_as in zip(fsw_switches,portList_v4_v6,ixia_ipv6_as_list):
		if switch.router_bgp.config_ebgp_ixia_v6(ixia_port=ixia_port_info,ixia_as=ixia_as,sw_as=switch.ebgp_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v6 peers ==============")
			exit()
		if switch.router_bgp.config_ebgp_ixia_v4(ixia_port=ixia_port_info,ixia_as=ixia_as,sw_as=switch.ebgp_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v4 peers ==============")
			exit()

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
		topo.add_bgp(dut_ip=fsw_switches[i].vlan1_ip,bgp_type='external',num=1)
		topo.add_bgp_v6(dut_ip=fsw_switches[i].vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=1)
		i += 1

	#This is DUT #5, don't get confused!!!!
	ixia_topology = myixia.topologies[4]
	dut_switch = fsw_switches[4]
	ixia_topology.change_bgp_routes_attributes(origin="egp",med=6111,community=6,comm_base=6100,num_path=6,as_base=65011,aggregator="106.106.106.106",aggregator_as=66660,ext_community=6,excomm_base=1,com_type="routetarget",address_family="v4",next_hop="200.200.200.200")
	# myixia.topologies[1].change_bgp_routes_attributes(origin="incomplete",med=6222,community=5,comm_base=6200,num_path=5,as_base=65012,aggregator="106.106.106.107",aggregator_as=66661,ext_community=6,excomm_base=2,com_type="routetarget",address_family="v4")
	# myixia.topologies[2].change_bgp_routes_attributes(origin="egp",med=6333,community=6,comm_base=6300,num_path=6,as_base=65013,aggregator="106.106.106.108",aggregator_as=66662,ext_community=6,excomm_base=3,com_type="routetarget",address_family="v4")
	# myixia.topologies[3].change_bgp_routes_attributes(origin="incomplete",med=6444,community=5,comm_base=6400,num_path=6,as_base=65014,aggregator="106.106.106.109",aggregator_as=66663,ext_community=6,excomm_base=4,com_type="routetarget",address_family="v4")
	# myixia.topologies[4].change_bgp_routes_attributes(origin="egp",med=6555,community=6,comm_base=6500,num_path=6,as_base=6500,aggregator="106.106.106.110",aggregator_as=66662,ext_community=6,excomm_base=5,com_type="routetarget",address_family="v4")
	# myixia.topologies[5].change_bgp_routes_attributes(origin="incomplete",med=6666,community=5,comm_base=6600,num_path=6,as_base=65015,aggregator="106.106.106.112",aggregator_as=66663,ext_community=6,excomm_base=6,com_type="routetarget",address_family="v4")


	ixia_topology.change_bgp_routes_attributes_v6(origin="egp",med=6111,community=6,comm_base=6100,num_path=6,as_base=65011,aggregator="106.106.106.106",aggregator_as=64101,ext_community=6,excomm_base=1,com_type="routetarget",address_family="v6",next_hop="2001:200:200:200::200")
	# myixia.topologies[1].change_bgp_routes_attributes_v6(origin="incomplete",med=6222,community=5,comm_base=6200,num_path=5,as_base=66012,aggregator="106.106.106.107",aggregator_as=64102,ext_community=6,excomm_base=2,com_type="routetarget",address_family="v6")
	# myixia.topologies[2].change_bgp_routes_attributes_v6(origin="egp",med=6333,community=6,comm_base=6300,num_path=6,as_base=66013,aggregator="106.106.106.108",aggregator_as=64103,ext_community=6,excomm_base=3,com_type="routetarget",address_family="v6")
	# myixia.topologies[3].change_bgp_routes_attributes_v6(origin="incomplete",med=6444,community=5,comm_base=6400,num_path=6,as_base=65014,aggregator="106.106.106.109",aggregator_as=64014,ext_community=6,excomm_base=4,com_type="routetarget",address_family="v6")
	# myixia.topologies[4].change_bgp_routes_attributes_v6(origin="egp",med=6333,community=6,comm_base=6300,num_path=6,as_base=65015,aggregator="106.106.106.110",aggregator_as=64105,ext_community=6,excomm_base=5,com_type="routetarget",address_family="v6")
	# myixia.topologies[5].change_bgp_routes_attributes_v6(origin="incomplete",med=6444,community=5,comm_base=6400,num_path=6,as_base=65016,aggregator="106.106.106.112",aggregator_as=64106,ext_community=6,excomm_base=6,com_type="routetarget",address_family="v6")
	 

	myixia.start_protocol(wait=40)

	print("Test Instruction: Manually configure route-map-in add-com and add-community-1 to neighbor 2001:10:1:1::211 and 10.1.1.211")
	
	config = """
	config router community-list
	    edit "com_list_1"
	            config rule
	                edit 1
	                    set action permit
	                    set match "6100:1 6100:2 6100:3 6100:4 6100:5 6100:6"
	                next
	            end
	    next
	    edit "6100-1"
	            config rule
	                edit 1
	                    set action permit
	                    set match "6100:1"
	                next
	            end
	    next
	    edit "7000-1"
	            config rule
	                edit 1
	                    set action permit
	                    set match "7000:1"
	                next
	            end
	    next
	    edit "6100-6"
	            config rule
	                edit 1
	                    set action permit
	                    set match "6100:6"
	                next
	            end
	    next
	    edit "6100-5-6100-6"
	            config rule
	                edit 1
	                    set action permit
	                    set match "6100:5 6100:6"
	                next
	            end
	    next
	end

	config router route-map
	    edit "dele-community"
	        set protocol bgp
	            config rule
	                edit 1
	                    set match-community "com_list_1"
	                    set set-community-delete "6100-6"
	                next
	            end
	    next
	    edit "change-community"
	        set protocol bgp
	            config rule
	                edit 1
	                    set match-community "com_list_1"
	                        set set-community "8000:1"
	                next
	            end
	    next
	    edit "add-community"
	        set protocol bgp
	            config rule
	                edit 1
	                    set match-community "com_list_1"
	                        set set-community "8100:1"
	                    set set-community-additive enable
	                next
	            end
	    next
	end
		"""
	dut_switch.config_commands(config)

if testcase == 6065 or test_all or IPV6:
	testcase = 6065
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "eBGP v6  allow-as-in as-override6"
	topology = "R1(65001) ---- R2(1) ----- R3(1) ----- R4[65001)"
	tag1 = "allow as in"
	tag2 = "as override"
	print_test_subject(testcase,description)

	if clear_bgp:
		test_clean_config(switches =fsw_switches)

	test_config_igp_ipv6(switches =fsw_switches)

	bgp1 = network.routers[0]
	bgp2 = network.routers[1]
	bgp3 = network.routers[2]
	bgp4 = network.routers[3]

	network.build_bgp_peer(bgp1,65001,bgp2,1)
	network.build_bgp_peer(bgp2,1,bgp3,1)
	network.build_bgp_peer(bgp3,1,bgp4,65001)

	ixia_ipv6_as_list = [65101,65102,65103,65104,65105,65106]
	ipv6_networks = ["2001:101:1:1::1","2001:102:1:1::1","2001:103:1:1::1","2001:104:1:1::1","2001:105:1:1::1","2001:106:1:1::1"]
	ipv4_networks = ["10.10.1.1","10.10.2.1","10.10.3.1","10.10.4.1","10.10.5.1","10.10.6.1"]

	fsw_switches =switches[1:]


if testcase == 6066 or test_all or IPV6:
	testcase = 6066
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "4 nodes topology + 1 IXIA, filter-list"
	topology = "R1(65001) ---- R2(1) ----- R3(1) ----- R4[65001)"
	tag1 = "4 nodes topology 1 IXIA, filter-list, filter list"
	print_test_subject(testcase,description)

	ixia_port_info = [
	[ixChassisIpList[0], 1, 7,"00:11:01:01:01:01","10.1.1.211/24","10.1.1.4","2001:10:1:1::211/64","2001:10:1:1::4",1]
	]

	if clear_bgp:
		test_clean_config(switches =fsw_switches)

	ixia_ipv6_as_list = [65104]
	ipv6_networks = ["2001:104:1:1::1"]
	ipv4_networks = ["10.10.4.1"]


	fsw_switches =switches[1:]
	network = BGP_networks(fsw_switches)
	if test_config:
		test_clean_config(switches =fsw_switches)
	test_config_igp_ipv6_fabric(switches =fsw_switches)

	bgp1 = network.routers[0]
	bgp2 = network.routers[1]
	bgp3 = network.routers[2]
	bgp4 = network.routers[3]

	sw1 = fsw_switches[0]
	sw2 = fsw_switches[1]
	sw3 = fsw_switches[2]
	sw4 = fsw_switches[3]

	network.build_bgp_peer(bgp1,65001,bgp2,1)
	network.build_bgp_peer(bgp2,1,bgp3,1)
	network.build_bgp_peer(bgp3,1,bgp4,65001)

	if bgp4.config_ebgp_ixia_v6(ixia_port=ixia_port_info[0],ixia_as=ixia_ipv6_as_list[0],sw_as=65001) == False:
		tprint("================= !!!!! Not able to configure IXIA BGP v6 peers ==============")
		exit()
	if bgp4.config_ebgp_ixia_v4(ixia_port=ixia_port_info[0],ixia_as=ixia_ipv6_as_list[0],sw_as=65001) == False:
		tprint("================= !!!!! Not able to configure IXIA BGP v4 peers ==============")
		exit()

	myixia = IXIA(apiServerIp,ixChassisIpList,ixia_port_info)

	for topo in myixia.topologies:
		topo.add_ipv6()
		topo.add_ipv4()
	 
	for topo,net6,net4,as_num in zip(myixia.topologies,ipv6_networks,ipv4_networks,ixia_ipv6_as_list):
		topo.bgpv6_network = net6
		topo.bgpv4_network = net4
		topo.bgp_as = as_num

	i = 0
	for topo in myixia.topologies:
		topo.add_bgp(dut_ip=sw4.vlan1_ip,bgp_type='external',num=1)
		topo.add_bgp_v6(dut_ip=sw4.vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=1)
		i += 1

	#This is DUT #5, don't get confused!!!!
	ixia_topology = myixia.topologies[0]
	dut_switch = sw4
	ixia_topology.change_bgp_routes_attributes(origin="egp",med=6111,community=6,comm_base=6100,num_path=6,as_base=65011,aggregator="106.106.106.106",aggregator_as=66660,ext_community=6,excomm_base=1,com_type="routetarget",address_family="v4",next_hop="200.200.200.200") 

	ixia_topology.change_bgp_routes_attributes_v6(origin="egp",med=6111,community=6,comm_base=6100,num_path=6,as_base=65011,aggregator="106.106.106.106",aggregator_as=64101,ext_community=6,excomm_base=1,com_type="routetarget",address_family="v6",next_hop="2001:200:200:200::200")
	 
	myixia.start_protocol(wait=40)

	config = """
	config router aspath-list
    edit "deny-65011"
            config rule
                edit 1
                    set action deny
                    set regexp "65001"
                next
            end
    next
	end
	"""

	sw4.config_commands(config)
	bgp4.config_neighbor_command(neighbor="2001:10:1:1::211",command="set filter-list-in6 deny-65011")
	bgp4.config_neighbor_command(neighbor="10.1.1.211",command="set filter-list-in deny-65011")
	bgp4.clear_bgp_all()

	bgp4.show_bgp_network_v64()
	sw4.show_routing_table_v64()

	bgp4.config_neighbor_command(neighbor="2001:10:1:1::211",command="unset filter-list-in6  ")
	bgp4.config_neighbor_command(neighbor="10.1.1.211",command="unset filter-list-in")
	bgp4.clear_bgp_all()

	bgp4.show_bgp_network_v64()
	sw4.show_routing_table_v64()


	bgp4.config_neighbor_command(neighbor="2001:200:30:1::1",command="set filter-list-out6 deny-65011")
	bgp4.config_neighbor_command(neighbor="2001:200:30:1::1",command="set filter-list-out deny-65011")
	bgp4.clear_bgp_all()

	bgp3.show_bgp_network_v64()
	sw3.show_routing_table_v64()

if testcase == 6067 or test_all or IPV6:
	testcase = 6067
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "Next Hop Self"
	topology = "R1(65001) ---- R2(1) ----- R3(1) ----- R4[65001)"
	tag1 = "4 nodes, next hop self"
	print_test_subject(testcase,description)

	ixia_port_info = [
	[ixChassisIpList[0], 1, 7,"00:11:01:01:01:01","10.1.1.211/24","10.1.1.1","2001:10:1:1::211/64","2001:10:1:1::1",1]
	]

	if clear_bgp:
		test_clean_config(switches =fsw_switches)

	ixia_ipv6_as_list = [65104]
	ipv6_networks = ["2001:104:1:1::1"]
	ipv4_networks = ["10.10.4.1"]


	fsw_switches =switches[1:]

	network = BGP_networks(fsw_switches)
	if test_config:
		test_clean_config(switches =fsw_switches)

	for sw in fsw_switches:
		sw.router_ospf.remove_ospf_v4()
		sw.router_ospf.remove_ospf_v6()
	# for sw in fsw_switches:
	# 	sw.delete_all_vlan_interfaces()

	bgp1 = network.routers[0]
	bgp2 = network.routers[1]
	bgp3 = network.routers[2]
	bgp4 = network.routers[3]

	sw1 = fsw_switches[0]
	sw2 = fsw_switches[1]
	sw3 = fsw_switches[2]
	sw4 = fsw_switches[3]

	sw1.config_stp(root=True)  # In this topology, it is a MUST to config this switch as a ROOT

	sw1.add_vlan_interface(vlan=10,vlan_name="vlan10",ipv4_addr="200.10.1.1",ipv6_addr="2001:200:10:1::1/64")
	sw2.add_vlan_interface(vlan=10,vlan_name="vlan10",ipv4_addr="200.10.1.2",ipv6_addr="2001:200:10:1::2/64")
	sw2.add_vlan_interface(vlan=20,vlan_name="vlan20",ipv4_addr="200.20.1.1",ipv6_addr="2001:200:20:1::1/64")
	sw3.add_vlan_interface(vlan=20,vlan_name="vlan20",ipv4_addr="200.20.1.2",ipv6_addr="2001:200:20:1::2/64")
	sw3.add_vlan_interface(vlan=30,vlan_name="vlan30",ipv4_addr="200.30.1.1",ipv6_addr="2001:200:30:1::1/64")
	sw4.add_vlan_interface(vlan=30,vlan_name="vlan30",ipv4_addr="200.30.1.2",ipv6_addr="2001:200:30:1::2/64")
	

	network.build_bgp_peer_address(bgp1,65001,"2001:200:10:1::1",bgp2,1,"2001:200:10:1::2")
	network.build_bgp_peer_address(bgp2,1,"2001:200:20:1::1",bgp3,1,"2001:200:20:1::2")
	network.build_bgp_peer_address(bgp3,1,"2001:200:30:1::1",bgp4,65001,"2001:200:30:1::2")

	bgp4.config_redistribute_connected()
	bgp4.config_redistribute_connected_v6()
	bgp2.clear_bgp_all()
	bgp3.clear_bgp_all()
	console_timer(10,msg="After redistributed connected to BGP, wait for 10s")

	Info(" ================= Next hop self NOT set yet, should not see any routes ======================")
	bgp2.show_bgp_network_v64()
	sw2.show_routing_table_v64()
	
	bgp3.config_neighbor_command(neighbor="2001:200:20:1::1",command="set next-hop-self enable")
	bgp3.config_neighbor_command(neighbor="2001:200:20:1::1",command="set next-hop-self6 enable")
	bgp4.clear_bgp_all()
	console_timer(10,msg="After configuring next-hop-self, wait for 10s")
	Info(" ================= Next hop self set yet, should see all routes ======================")
	bgp2.show_bgp_network_v64()
	sw2.show_routing_table_v64()

	Info(" ================= Config OSPF and OSPFv3 ======================")
	test_config_igp_ipv6_fabric(switches =fsw_switches)
	sw2.router_ospf.show_ospf_neighbors_all()

	bgp3.config_neighbor_command(neighbor="2001:200:20:1::1",command="set next-hop-self disable")
	bgp3.config_neighbor_command(neighbor="2001:200:20:1::1",command="set next-hop-self6 disable")
	bgp2.clear_bgp_all()
	bgp3.clear_bgp_all()

	console_timer(10,msg="After disabling next-hop-self, wait for 10s")

	Info(" ================= After Config OSPF and OSPFv3, All routes with R4 as Next hop should be seen by R2 and R3 ======================")
	bgp2.show_bgp_network_v64()
	sw2.show_routing_table_v64()

	Info(" ================= Remove OSPF and OSPFv3 ======================")
	for sw in fsw_switches:
		sw.router_ospf.remove_ospf_v4()
		sw.router_ospf.remove_ospf_v6()

	sw2.router_ospf.show_ospf_neighbors_all()
	sw3.router_ospf.show_ospf_neighbors_all()

	console_timer(10,msg="After removing ospf wait for 10s")
	bgp4.clear_bgp_all()
	Info(" ================= After removing OSPF and OSPFv3, All routes with R4 as Next hop should be NOT seen by R2 and R3 ======================")
	bgp2.show_bgp_network_v64()
	sw2.show_routing_table_v64()

	Info(" ================= Enable nexhop self on R3 ======================")
	bgp3.config_neighbor_command(neighbor="2001:200:20:1::1",command="set next-hop-self enable")
	bgp3.config_neighbor_command(neighbor="2001:200:20:1::1",command="set next-hop-self6 enable")
	bgp2.clear_bgp_all()
	bgp3.clear_bgp_all()
	console_timer(10,msg="After configuring next-hop-self, wait for 10s")

	Info(" ================= After configing nexthop self, All routes with R4 as Next hop should be seen by R2 and R3 ======================")
	bgp2.show_bgp_network_v64()
	sw2.show_routing_table_v64()

	Info(" ================= Finally disabling next hop self and re-enable ospf ======================")
	bgp3.config_neighbor_command(neighbor="2001:200:20:1::1",command="set next-hop-self disable")
	bgp3.config_neighbor_command(neighbor="2001:200:20:1::1",command="set next-hop-self6 disable")
	bgp2.clear_bgp_all()
	bgp3.clear_bgp_all()

	console_timer(10,msg="After disabling next-hop-self, wait for 10s")

	bgp2.show_bgp_network_v64()
	sw2.show_routing_table_v64()

	Info(" ================= Config OSPF and OSPFv3 ======================")
	test_config_igp_ipv6_fabric(switches =fsw_switches)
	sw2.router_ospf.show_ospf_neighbors_all()

	console_timer(10,msg="After enabling ospf, wait for 10s")

	bgp2.show_bgp_network_v64()
	sw2.show_routing_table_v64()

if testcase == 6068 or test_all or IPV6:
	testcase = 6068
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "prefix list"
	topology = "R1(65001) ---- R2(1) ----- R3(1) ----- R4[65001)"
	tag1 = " 4 nodes,prefix list"
	print_test_subject(testcase,description)

	ixia_port_info = [
	[ixChassisIpList[0], 1, 7,"00:11:01:01:01:01","10.1.1.211/24","10.1.1.1","2001:10:1:1::211/64","2001:10:1:1::1",1]
	]

	if clear_bgp:
		test_clean_config(switches =fsw_switches)

	ixia_ipv6_as_list = [65104]
	ipv6_networks = ["2001:104:1:1::1"]
	ipv4_networks = ["10.10.4.1"]


	fsw_switches =switches[1:]

	network = BGP_networks(fsw_switches)
	if test_config:
		test_clean_config(switches =fsw_switches)

	for sw in fsw_switches:
		sw.router_ospf.remove_ospf_v4()
		sw.router_ospf.remove_ospf_v6()
	# for sw in fsw_switches:
	# 	sw.delete_all_vlan_interfaces()

	bgp1 = network.routers[0]
	bgp2 = network.routers[1]
	bgp3 = network.routers[2]
	bgp4 = network.routers[3]

	sw1 = fsw_switches[0]
	sw2 = fsw_switches[1]
	sw3 = fsw_switches[2]
	sw4 = fsw_switches[3]

	sw1.config_stp(root=True)  # In this topology, it is a MUST to config this switch as a ROOT

	sw1.add_vlan_interface(vlan=10,vlan_name="vlan10",ipv4_addr="200.10.1.1",ipv6_addr="2001:200:10:1::1/64")
	sw2.add_vlan_interface(vlan=10,vlan_name="vlan10",ipv4_addr="200.10.1.2",ipv6_addr="2001:200:10:1::2/64")
	sw2.add_vlan_interface(vlan=20,vlan_name="vlan20",ipv4_addr="200.20.1.1",ipv6_addr="2001:200:20:1::1/64")
	sw3.add_vlan_interface(vlan=20,vlan_name="vlan20",ipv4_addr="200.20.1.2",ipv6_addr="2001:200:20:1::2/64")
	sw3.add_vlan_interface(vlan=30,vlan_name="vlan30",ipv4_addr="200.30.1.1",ipv6_addr="2001:200:30:1::1/64")
	sw4.add_vlan_interface(vlan=30,vlan_name="vlan30",ipv4_addr="200.30.1.2",ipv6_addr="2001:200:30:1::2/64")
	

	network.build_bgp_peer_address(bgp1,65001,"2001:200:10:1::1",bgp2,1,"2001:200:10:1::2")
	network.build_bgp_peer_address(bgp2,1,"2001:200:20:1::1",bgp3,1,"2001:200:20:1::2")
	network.build_bgp_peer_address(bgp3,1,"2001:200:30:1::1",bgp4,65001,"2001:200:30:1::2")

	bgp4.config_redistribute_connected()
	bgp4.config_redistribute_connected_v6()
	bgp4.clear_bgp_all()
	console_timer(10,msg="After redistributed connected to BGP, wait for 10s")
	bgp3.show_bgp_network_v6()


	config = """
	config router prefix-list
    edit "r4-loopback4"
            config rule
                edit 1
                    set action deny
                    set prefix 4.4.4.4 255.255.255.255
                    unset ge
                    unset le
                next
                edit 2
                    set prefix any
                    unset ge
                    unset le
                next
            end
    next
	end

	config router prefix-list6
    edit "r4-loopback6"
            config rule
                edit 1
                    set action deny
                    set prefix6 "2001:4:4:4::4/128"
                    unset ge
                    unset le
                next
                edit 2
                    set prefix6 "any"
                    unset ge
                    unset le
                next
            end
    next
	end

	"""
	sw3.config_commands(config)
	sw4.config_commands(config)
	
	# clear out all prefix configs
	Info("=========== Clean up all neighbor prefix config and R3 and R4 ========")
	bgp3.config_neighbor_command(neighbor="2001:200:30:1::2",command="unset prefix-list-in6")
	bgp3.config_neighbor_command(neighbor="2001:200:30:1::2",command="unset prefix-list-in")
	bgp3.config_neighbor_command(neighbor="2001:200:30:1::2",command="unset prefix-list-out6")
	bgp3.config_neighbor_command(neighbor="2001:200:30:1::2",command="unset prefix-list-out")

	bgp4.config_neighbor_command(neighbor="2001:200:30:1::1",command="unset prefix-list-in6")
	bgp4.config_neighbor_command(neighbor="2001:200:30:1::1",command="unset prefix-list-in")
	bgp4.config_neighbor_command(neighbor="2001:200:30:1::1",command="unset prefix-list-out6")
	bgp4.config_neighbor_command(neighbor="2001:200:30:1::1",command="unset prefix-list-out")

	
	#config prefix out on R4
	Info("=========== Config prefix out on R4 ===========")
	bgp4.config_neighbor_command(neighbor="2001:200:30:1::1",command="set prefix-list-out6 r4-loopback6")
	bgp4.config_neighbor_command(neighbor="2001:200:30:1::1",command="set prefix-list-out r4-loopback4")

	bgp4.clear_bgp_all()
	console_timer(10,msg="After configuring prefix-out on R4, wait for 10s")
	Info("============ After R4 config prefix-out, R3 should only see 3 routes from R4 ============")
	bgp3.show_bgp_network_v6()
	bgp3.show_bgp_network()
 
	Info("============ Clean up all config on R4 for prefix ============")
	bgp4.config_neighbor_command(neighbor="2001:200:30:1::1",command="unset prefix-list-in6")
	bgp4.config_neighbor_command(neighbor="2001:200:30:1::1",command="unset prefix-list-in")
	bgp4.config_neighbor_command(neighbor="2001:200:30:1::1",command="unset prefix-list-out6")
	bgp4.config_neighbor_command(neighbor="2001:200:30:1::1",command="unset prefix-list-out")
	bgp4.clear_bgp_all()

	console_timer(10,msg="After cleaning up prefix config on R4, wait for 10s")
	Info("============== All 4 bgp routes from R4 should be seen on R3 ============")
	bgp3.show_bgp_network_v6()
	bgp3.show_bgp_network()

	Info("============== Config prefix-in on R3 ============")
	bgp3.config_neighbor_command(neighbor="2001:200:30:1::2",command="set prefix-list-in6 r4-loopback6 ")
	bgp3.config_neighbor_command(neighbor="2001:200:30:1::2",command="set prefix-list-in r4-loopback4")

	bgp3.clear_bgp_all()
	console_timer(10,msg="After configuring prefix-in on R3, wait for 10s")
	Info("============== Only 4 routes from R4 should be seen on R3 after prefix in is configured on R3  ============")
	bgp3.show_bgp_network_v6()
	bgp3.show_bgp_network()

if testcase == 6069 or test_all or IPV6:
	testcase = 6069
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "distribute list"
	topology = "R1(65001) ---- R2(1) ----- R3(1) ----- R4[65001)"
	tag1 = "4 nodes,distribute list"
	print_test_subject(testcase,description)

	ixia_port_info = [
	[ixChassisIpList[0], 1, 7,"00:11:01:01:01:01","10.1.1.211/24","10.1.1.1","2001:10:1:1::211/64","2001:10:1:1::1",1]
	]

	if clear_bgp:
		test_clean_config(switches =fsw_switches)

	ixia_ipv6_as_list = [65104]
	ipv6_networks = ["2001:104:1:1::1"]
	ipv4_networks = ["10.10.4.1"]


	fsw_switches =switches[1:]

	network = BGP_networks(fsw_switches)
	if test_config:
		test_clean_config(switches =fsw_switches)

	bgp1 = network.routers[0]
	bgp2 = network.routers[1]
	bgp3 = network.routers[2]
	bgp4 = network.routers[3]

	sw1 = fsw_switches[0]
	sw2 = fsw_switches[1]
	sw3 = fsw_switches[2]
	sw4 = fsw_switches[3]

	sw3.config_stp(root=True)  # In this topology, it is a MUST to config this switch as a ROOT

	sw1.add_vlan_interface(vlan=10,vlan_name="vlan10",ipv4_addr="200.10.1.1",ipv6_addr="2001:200:10:1::1/64")
	sw2.add_vlan_interface(vlan=10,vlan_name="vlan10",ipv4_addr="200.10.1.2",ipv6_addr="2001:200:10:1::2/64")
	sw2.add_vlan_interface(vlan=20,vlan_name="vlan20",ipv4_addr="200.20.1.1",ipv6_addr="2001:200:20:1::1/64")
	sw3.add_vlan_interface(vlan=20,vlan_name="vlan20",ipv4_addr="200.20.1.2",ipv6_addr="2001:200:20:1::2/64")
	sw3.add_vlan_interface(vlan=30,vlan_name="vlan30",ipv4_addr="200.30.1.1",ipv6_addr="2001:200:30:1::1/64")
	sw4.add_vlan_interface(vlan=30,vlan_name="vlan30",ipv4_addr="200.30.1.2",ipv6_addr="2001:200:30:1::2/64")
	

	network.build_bgp_peer_address(bgp1,65001,"2001:200:10:1::1",bgp2,1,"2001:200:10:1::2")
	network.build_bgp_peer_address(bgp2,1,"2001:200:20:1::1",bgp3,1,"2001:200:20:1::2")
	network.build_bgp_peer_address(bgp3,1,"2001:200:30:1::1",bgp4,65001,"2001:200:30:1::2")

	bgp4.config_redistribute_connected()
	bgp4.config_redistribute_connected_v6()
	bgp4.clear_bgp_all()
	console_timer(10,msg="After redistributed connected to BGP, wait for 10s")
	bgp3.show_bgp_network_v6()


	config = """
	config router access-list6
    edit "1"
            config rule
                edit 1
                    set action deny
                    set prefix6 "2001:4:4:4::4/128"
                    set exact-match disable
                next
                edit 2
                    set exact-match disable
                next
            end
    next
	end

	config router access-list
    edit "deny-r4-loop"
            config rule
                edit 1
                    set action deny
                    set prefix 4.4.4.4 255.255.255.255
                    set exact-match disable
                next
                edit 2
                    set exact-match disable
                next
            end
    next
end


	"""
	sw3.config_commands(config)
	sw4.config_commands(config)
	
	# clear out all prefix configs
	Info("=========== Clean up all neighbor prefix config and R3 and R4 ========")
	bgp3.config_neighbor_command(neighbor="2001:200:30:1::2",command="unset distribute-list-out6")
	bgp3.config_neighbor_command(neighbor="2001:200:30:1::2",command="unset distribute-list-in6")
	bgp3.config_neighbor_command(neighbor="2001:200:30:1::2",command="unset distribute-list-out")
	bgp3.config_neighbor_command(neighbor="2001:200:30:1::2",command="unset distribute-list-in")

	bgp4.config_neighbor_command(neighbor="2001:200:30:1::1",command="unset distribute-list-out6")
	bgp4.config_neighbor_command(neighbor="2001:200:30:1::1",command="unset distribute-list-in6")
	bgp4.config_neighbor_command(neighbor="2001:200:30:1::1",command="unset distribute-list-out")
	bgp4.config_neighbor_command(neighbor="2001:200:30:1::1",command="unset distribute-list-in")
 
	 
	
	#config prefix out on R4
	Info("=========== Config prefix out on R4 ===========")
	bgp4.config_neighbor_command(neighbor="2001:200:30:1::1",command="set distribute-list-out6 1")
	bgp4.config_neighbor_command(neighbor="2001:200:30:1::1",command="set distribute-list-out deny-r4-loop")

	bgp4.clear_bgp_all()
	console_timer(10,msg="After configuring prefix-out on R4, wait for 10s")
	Info("============ After R4 config prefix-out, R3 should only see 3 routes from R4 ============")
	bgp3.show_bgp_network_v6()
	bgp3.show_bgp_network()
 
	Info("============ Clean up all config on R4 for prefix ============")
	bgp4.config_neighbor_command(neighbor="2001:200:30:1::1",command="unset distribute-list-out6")
	bgp4.config_neighbor_command(neighbor="2001:200:30:1::1",command="unset distribute-list-in6")
	bgp4.config_neighbor_command(neighbor="2001:200:30:1::1",command="unset distribute-list-out")
	bgp4.config_neighbor_command(neighbor="2001:200:30:1::1",command="unset distribute-list-in")
	bgp4.clear_bgp_all()

	console_timer(10,msg="After cleaning up prefix config on R4, wait for 10s")
	Info("============== All 4 bgp routes from R4 should be seen on R3 ============")
	bgp3.show_bgp_network_v6()
	bgp3.show_bgp_network()

	Info("============== Config prefix-in on R3 ============")
	bgp3.config_neighbor_command(neighbor="2001:200:30:1::2",command="set distribute-list-in6 1")
	bgp3.config_neighbor_command(neighbor="2001:200:30:1::2",command="set distribute-list-in deny-r4-loop")

	bgp3.clear_bgp_all()
	console_timer(10,msg="After configuring prefix-in on R3, wait for 10s")
	Info("============== Only 4 routes from R4 should be seen on R3 after prefix in is configured on R3  ============")
	bgp3.show_bgp_network_v6()
	bgp3.show_bgp_network()

if testcase == 60610 or test_all or IPV6:
	testcase = 60610
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "4 nodes topology + 1 IXAA, aggregate,next_hop,policy, unsuppress, manually apply route-map or filter list"
	topology = "R1(65001) ---- R2(1) ----- R3(1) ----- R4[65001)"
	tag1 = "4 nodes topology 1 IXIA, filter-list, aggregate6, next_hop, policy,unsuppress"
	print_test_subject(testcase,description)

	ixia_port_info = [
	[ixChassisIpList[0], 1, 7,"00:11:01:01:01:01","10.1.1.211/24","10.1.1.4","2001:10:1:1::211/64","2001:10:1:1::4",1],
	[ixChassisIpList[0], 1, 9,"00:13:01:01:01:01","10.1.1.213/24","10.1.1.1","2001:10:1:1::213/64","2001:10:1:1::1",1]
	]

	if clear_bgp:
		test_clean_config(switches =fsw_switches)

	ixia_ipv6_as_list = [65104,103] # IXIA's AS numbers
	ipv6_networks = ["2001:104:1:1::1","2001:105:1:1::1"]
	ipv4_networks = ["10.10.4.1","10.10.5.1"]


	fsw_switches =switches[1:]
	network = BGP_networks(fsw_switches)
	if clear_bgp:
		test_clean_config(switches =fsw_switches)
	test_config_igp_ipv6_fabric(switches =fsw_switches)

	cisco = switches[0]

	bgp1 = network.routers[0]
	bgp2 = network.routers[1]
	bgp3 = network.routers[2]
	bgp4 = network.routers[3]

	sw1 = fsw_switches[0]
	sw2 = fsw_switches[1]
	sw3 = fsw_switches[2]
	sw4 = fsw_switches[3]


	for sw in fsw_switches:
		sw.prefix_list.prefix_unsuppress_v4()
		sw.prefix_list.prefix_unsuppress_v6()
		sw.route_map.unsuppress_map()

	network.build_bgp_peer(bgp1,65001,bgp2,1)
	network.build_bgp_peer(bgp2,1,bgp3,1)
	network.build_bgp_peer(bgp3,1,bgp4,65001)

	config = """
	config router static6
    edit 1
        set dst 2001:200:200:200::200/128
        set gateway 2001:10:1:1::211
    next
	end

	config router static
    edit 2
        set dst 200.200.200.200 255.255.255.255
        set gateway 10.1.1.211
    next
	end
	"""
	sw4.config_commands(config)

	config = """
	config router access-list6
    edit "1"
            config rule
                edit 1
                    set action deny
                    set prefix6 "2001:4:4:4::4/128"
                    set exact-match disable
                next
                edit 2
                    set exact-match disable
                next
            end
    next
    edit "deny-loop4"
            config rule
                edit 1
                    set prefix6 "2001:10:1:1::1/128"
                    set exact-match disable
                next
            end
    next
    edit "any-routes"
            config rule
                edit 1
                    set exact-match disable
                next
            end
    next
	end

	config router access-list
    edit "deny-r4-loop"
            config rule
                edit 1
                    set action deny
                    set prefix 4.4.4.4 255.255.255.255
                    set exact-match disable
                next
                edit 2
                    set exact-match disable
                next
            end
    next
    edit "any"
            config rule
                edit 1
                    set exact-match disable
                next
            end
    next
	end

	config router route-map
    edit "set-nh"
        set protocol bgp
            config rule
                edit 1
                    set match-ip6-address "any-routes"
                    set set-ip6-nexthop 2001:3:3:3::3
                next
            end
    next
    edit "set-nh-ipv4"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-address "any"
                    set set-ip-nexthop 3.3.3.3
                next
            end
    next
	end

	"""
	sw3.config_commands(config)

	if bgp4.config_ebgp_ixia_v6(ixia_port=ixia_port_info[0],ixia_as=ixia_ipv6_as_list[0],sw_as=65001) == False:
		tprint("================= !!!!! Not able to configure IXIA BGP v6 peers ==============")
		exit()
	if bgp4.config_ebgp_ixia_v4(ixia_port=ixia_port_info[0],ixia_as=ixia_ipv6_as_list[0],sw_as=65001) == False:
		tprint("================= !!!!! Not able to configure IXIA BGP v4 peers ==============")
		exit()

	myixia = IXIA(apiServerIp,ixChassisIpList,ixia_port_info)

	for topo in myixia.topologies:
		topo.add_ipv6()
		topo.add_ipv4()
	 
	for topo,net6,net4,as_num in zip(myixia.topologies,ipv6_networks,ipv4_networks,ixia_ipv6_as_list):
		topo.bgpv6_network = net6    #ipv6 network ixia advertises to switch 
		topo.bgpv4_network = net4    #ipv4 networks ixia advertises to switch
		topo.bgp_as = as_num         #This is ixia local bgp as

	
	topos = myixia.topologies
	topos[0].add_bgp(dut_ip=sw4.vlan1_ip,bgp_type='external',num=30)
	topos[0].add_bgp_v6(dut_ip=sw4.vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=30)

	topos[1].add_bgp(dut_ip=cisco.vlan1_ip,bgp_type='external',num=30)
	topos[1].add_bgp_v6(dut_ip=cisco.vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=30)

	#This is DUT #5, don't get confused!!!!
	ixia_topology = myixia.topologies[0]
	dut_switch = sw4
	# topos[0].change_bgp_routes_attributes(origin="egp",med=4111,community=6,comm_base=6100,num_path=6,as_base=65011,aggregator="106.106.106.106",aggregator_as=66660,ext_community=6,excomm_base=1,com_type="routetarget",address_family="v4") 
	# topos[0].change_bgp_routes_attributes_v6(origin="egp",med=6111,community=6,comm_base=6100,num_path=6,as_base=65011,aggregator="106.106.106.106",aggregator_as=64101,ext_community=6,excomm_base=1,com_type="routetarget",address_family="v6")
	 

	# topos[1].change_bgp_routes_attributes(origin="egp",med=4211,community=5,comm_base=6200,num_path=5,as_base=65021,aggregator="107.107.107.107",aggregator_as=66661,ext_community=5,excomm_base=1,com_type="routetarget",address_family="v4",next_hop="201.201.201.201") 
	# topos[1].change_bgp_routes_attributes_v6(origin="egp",med=6211,community=5,comm_base=6200,num_path=5,as_base=65021,aggregator="107.107.107.107",aggregator_as=64102,ext_community=5,excomm_base=1,com_type="routetarget",address_family="v6",next_hop="2001:201:201:201::201")
	 

	topos[0].change_bgp_routes_attributes(origin="egp",med=6111,community=6,comm_base=6100,num_path=6,as_base=65011,aggregator="106.106.106.106",aggregator_as=66660,ext_community=6,excomm_base=1,com_type="routetarget",address_family="v4",next_hop="200.200.200.200") 
	topos[0].change_bgp_routes_attributes_v6(origin="egp",med=6111,community=6,comm_base=6100,num_path=6,as_base=65011,aggregator="106.106.106.106",aggregator_as=64101,ext_community=6,excomm_base=1,com_type="routetarget",address_family="v6",next_hop="2001:200:200:200::200")
	 
	topos[1].change_bgp_routes_attributes(origin="egp",med=6211,community=5,comm_base=6200,num_path=5,as_base=65021,aggregator="107.107.107.107",aggregator_as=66661,ext_community=5,excomm_base=1,com_type="routetarget",address_family="v4",next_hop="201.201.201.201") 
	topos[1].change_bgp_routes_attributes_v6(origin="egp",med=6211,community=5,comm_base=6200,num_path=5,as_base=65021,aggregator="107.107.107.107",aggregator_as=64102,ext_community=5,excomm_base=1,com_type="routetarget",address_family="v6",next_hop="2001:201:201:201::201")
	 
	myixia.start_protocol(wait=40)

	# config = """
	# config router aspath-list
 #    edit "deny-65011"
 #            config rule
 #                edit 1
 #                    set action deny
 #                    set regexp "65001"
 #                next
 #            end
 #    next
	# end
	# """

	# sw4.config_commands(config)
	# bgp4.config_neighbor_command(neighbor="2001:10:1:1::211",command="set filter-list-in6 deny-65011")
	# bgp4.config_neighbor_command(neighbor="10.1.1.211",command="set filter-list-in deny-65011")
	# bgp4.clear_bgp_all()

	# bgp4.show_bgp_network_v64()
	# sw4.show_routing_table_v64()

	# bgp4.config_neighbor_command(neighbor="2001:10:1:1::211",command="unset filter-list-in6  ")
	# bgp4.config_neighbor_command(neighbor="10.1.1.211",command="unset filter-list-in")
	# bgp4.clear_bgp_all()

	# bgp4.show_bgp_network_v64()
	# sw4.show_routing_table_v64()


	# bgp4.config_neighbor_command(neighbor="2001:200:30:1::1",command="set filter-list-out6 deny-65011")
	# bgp4.config_neighbor_command(neighbor="2001:200:30:1::1",command="set filter-list-out deny-65011")
	# bgp4.clear_bgp_all()

	# bgp3.show_bgp_network_v64()
	# sw3.show_routing_table_v64()

if testcase == 60611 or test_all or IPV6:
	testcase = 60611
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "4 nodes topology + 1 IXAA, enforce-first-as, as_prepend doesn't serve the purpose. Need ingress route-map to prepend an AS"
	topology = "(103)IXIA ---- Cisco(65000) ----- R1(1) ---- R2(2) ----- R3(3) ----- R4[4) ---- IXIA (65104) "
	tag1 = "4 nodes topology 1 IXIA, enforce-first-as"
	print_test_subject(testcase,description)

	ixia_port_info = [
	[ixChassisIpList[0], 1, 7,"00:11:01:01:01:01","10.1.1.211/24","10.1.1.4","2001:10:1:1::211/64","2001:10:1:1::4",1],
	[ixChassisIpList[0], 1, 9,"00:13:01:01:01:01","10.1.1.213/24","10.1.1.1","2001:10:1:1::213/64","2001:10:1:1::1",1]
	]

	if clear_bgp:
		test_clean_config(switches =fsw_switches)

	ixia_ipv6_as_list = [65104,103] # IXIA's AS numbers
	ipv6_networks = ["2001:104:1:1::1","2001:105:1:1::1"]
	ipv4_networks = ["10.10.4.1","10.10.5.1"]


	fsw_switches =switches[1:]
	network = BGP_networks(switches)
	if clear_bgp:
		test_clean_config(switches =fsw_switches)
	#test_config_igp_ipv6_fabric(switches =fsw_switches)

	cisco = switches[0]
	cisco_bgp = network.routers[0]
	bgp1 = network.routers[1]
	bgp2 = network.routers[2]
	bgp3 = network.routers[3]
	bgp4 = network.routers[4]

	sw1 = fsw_switches[0]
	sw2 = fsw_switches[1]
	sw3 = fsw_switches[2]
	sw4 = fsw_switches[3]

	dut_switches = fsw_switches[0:4]

	# for sw in fsw_switches:
	# 	sw.prefix_list.prefix_unsuppress_v4()
	# 	sw.prefix_list.prefix_unsuppress_v6()
	# 	sw.route_map.unsuppress_map()

	network.build_bgp_peer(cisco_bgp,65000,bgp1,1)
	network.build_bgp_peer(bgp1,1,bgp2,2)
	network.build_bgp_peer(bgp2,2,bgp3,3)
	network.build_bgp_peer(bgp3,3,bgp4,4)


	if bgp4.config_ebgp_ixia_v6(ixia_port=ixia_port_info[0],ixia_as=ixia_ipv6_as_list[0],sw_as=4) == False:
		tprint("================= !!!!! Not able to configure IXIA BGP v6 peers ==============")
		exit()
	if bgp4.config_ebgp_ixia_v4(ixia_port=ixia_port_info[0],ixia_as=ixia_ipv6_as_list[0],sw_as=4) == False:
		tprint("================= !!!!! Not able to configure IXIA BGP v4 peers ==============")
		exit()

	if cisco_bgp.config_ebgp_ixia_v6(ixia_port=ixia_port_info[1],ixia_as=ixia_ipv6_as_list[1],sw_as=65000) == False:
		tprint("================= !!!!! Not able to configure IXIA BGP v6 peers ==============")
		exit()
	if cisco_bgp.config_ebgp_ixia_v4(ixia_port=ixia_port_info[1],ixia_as=ixia_ipv6_as_list[1],sw_as=65000) == False:
		tprint("================= !!!!! Not able to configure IXIA BGP v4 peers ==============")
		exit()

	# for switch in dut_switches:
	# 	switch.router_bgp.config_all_neighbor_commands("set attribute-unchanged6 next-hop as-path med")
	# 	switch.router_bgp.config_all_neighbor_commands("set attribute-unchanged next-hop as-path med")

	myixia = IXIA(apiServerIp,ixChassisIpList,ixia_port_info)

	for topo in myixia.topologies:
		topo.add_ipv6()
		topo.add_ipv4()
	 
	for topo,net6,net4,as_num in zip(myixia.topologies,ipv6_networks,ipv4_networks,ixia_ipv6_as_list):
		topo.bgpv6_network = net6    #ipv6 network ixia advertises to switch 
		topo.bgpv4_network = net4    #ipv4 networks ixia advertises to switch
		topo.bgp_as = as_num         #This is ixia local bgp as

	
	topos = myixia.topologies
	topos[0].add_bgp(dut_ip=sw4.vlan1_ip,bgp_type='external',num=30)
	topos[0].add_bgp_v6(dut_ip=sw4.vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=1)

	topos[1].add_bgp(dut_ip=cisco.vlan1_ip,bgp_type='external',num=30)
	topos[1].add_bgp_v6(dut_ip=cisco.vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=1)

	#This is DUT #5, don't get confused!!!!
	ixia_topology = myixia.topologies[0]
	dut_switch = sw4
	 
	topos[0].change_bgp_routes_attributes(origin="egp",med=6111,community=6,comm_base=6100,num_path=6,as_base=65011,aggregator="106.106.106.106",aggregator_as=66660,ext_community=6,excomm_base=1,com_type="routetarget",address_family="v4" ) 
	topos[0].change_bgp_routes_attributes_v6(origin="egp",med=6111,community=6,comm_base=6100,num_path=6,as_base=65011,aggregator="106.106.106.106",aggregator_as=64101,ext_community=6,excomm_base=1,com_type="routetarget",address_family="v6")
	topos[1].change_bgp_routes_attributes(origin="egp",med=6211,community=5,comm_base=6200,num_path=5,as_base=65021,aggregator="107.107.107.107",aggregator_as=66661,ext_community=5,excomm_base=1,com_type="routetarget",address_family="v4") 
	topos[1].change_bgp_routes_attributes_v6(origin="egp",med=6211,community=5,comm_base=6200,num_path=5,as_base=65021,aggregator="107.107.107.107",aggregator_as=64102,ext_community=5,excomm_base=1,com_type="routetarget",address_family="v6")
	 
	myixia.start_protocol(wait=40)

	config = """
	config router route-map
    edit "change-as"
        set protocol bgp
            config rule
                edit 1
                        set set-aspath "1111"
                next
            end
    next
	end

	"""
	sw1.config_commands(config)

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

if testcase == 6091 or test_all or IPV6:
	testcase = 6091
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "Basic eBGP traffic forwarding - IPv4 And IPv6 peered to IXIA and traffic forwarding, ipv6 scale"
	tag = "basic traffic forwarding, ipv6 scale"
	print_test_subject(testcase,description)

 
	ixia_ipv6_as_list = [101,102,103,104,105,106]
	ipv4_networks = ["10.10.1.1","10.10.2.1","10.10.3.1","10.10.4.1","10.10.5.1","10.10.6.1"]
	ipv6_networks = ["2001:101:1:1::1","2001:102:1:1::1","2001:103:1:1::1","2001:104:1:1::1","2001:105:1:1::211","2001:106:1:1::1"]

	if clear_bgp:
		test_clean_config(switches =fsw_switches)
	
	fsw_switches =switches[1:]
	sw5 = switches[5]
	sw6 = switches[6]
	network = BGP_networks(switches)
	#Infra configuration
	if clear_bgp:
		test_clean_config(switches =fsw_switches)
	if test_config:
		test_config_igp_ipv6_fabric(switches =fsw_switches)
	else:
		update_igp_database_all(switches =fsw_switches)

	network.biuld_ibgp_mesh_topo_sys_intf_v6()
	network.biuld_ibgp_mesh_topo_sys_intf()
	console_timer(20,msg=f"Test case {testcase}: After configuring fully mesh iBGP across all IPv6 system interfaces, wait....")
	network.show_summary()
	
	# FSW configuration
	for switch, ixia_port_info, ixia_as in zip(fsw_switches,portList_v4_v6,ixia_ipv6_as_list):
		if switch.router_bgp.config_ebgp_ixia_v6(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v6 peers ==============")
			exit()
		if switch.router_bgp.config_ebgp_ixia_v4(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v4 peers ==============")
			exit()

	print_title("Get crash information before injecting routes")
	sw5.get_crash_debug()
	sw6.get_crash_debug()


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
		topo.add_bgp(dut_ip=fsw_switches[i].vlan1_ip,bgp_type='external',num=2000)
		topo.add_bgp_v6(dut_ip=fsw_switches[i].vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=2000)
		i += 1

	for i in range(6):
		myixia.topologies[i].change_bgp_routes_attributes(flapping="RANDOM",address_family="v4")
		myixia.topologies[i].change_bgp_routes_attributes_v6(flapping="RANDOM",address_family="v6")

	myixia.start_protocol(wait=40)


	myixia.create_traffic(src_topo=myixia.topologies[0].topology, dst_topo=myixia.topologies[1].topology,traffic_name="t1_to_t2",tracking_name="Tracking_1")
	myixia.create_traffic(src_topo=myixia.topologies[1].topology, dst_topo=myixia.topologies[0].topology,traffic_name="t2_to_t1",tracking_name="Tracking_2")

	myixia.create_traffic(src_topo=myixia.topologies[2].topology, dst_topo=myixia.topologies[3].topology,traffic_name="t2_to_t3",tracking_name="Tracking_3")
	myixia.create_traffic(src_topo=myixia.topologies[3].topology, dst_topo=myixia.topologies[2].topology,traffic_name="t3_to_t2",tracking_name="Tracking_4")

	myixia.create_traffic(src_topo=myixia.topologies[4].topology, dst_topo=myixia.topologies[5].topology,traffic_name="t4_to_t5",tracking_name="Tracking_5")
	myixia.create_traffic(src_topo=myixia.topologies[5].topology, dst_topo=myixia.topologies[4].topology,traffic_name="t5_to_t4",tracking_name="Tracking_6")


	myixia.create_traffic_v6(src_topo=myixia.topologies[0].topology, dst_topo=myixia.topologies[1].topology,traffic_name="t1_to_t2_v6",tracking_name="Tracking_1_v6")
	myixia.create_traffic_v6(src_topo=myixia.topologies[1].topology, dst_topo=myixia.topologies[0].topology,traffic_name="t2_to_t1_v6",tracking_name="Tracking_2_v6")

	myixia.create_traffic_v6(src_topo=myixia.topologies[2].topology, dst_topo=myixia.topologies[3].topology,traffic_name="t2_to_t3_v6",tracking_name="Tracking_3_v6")
	myixia.create_traffic_v6(src_topo=myixia.topologies[3].topology, dst_topo=myixia.topologies[2].topology,traffic_name="t3_to_t2_v6",tracking_name="Tracking_4_v6")

	myixia.create_traffic_v6(src_topo=myixia.topologies[4].topology, dst_topo=myixia.topologies[5].topology,traffic_name="t4_to_t5_v6",tracking_name="Tracking_5_v6")
	myixia.create_traffic_v6(src_topo=myixia.topologies[5].topology, dst_topo=myixia.topologies[4].topology,traffic_name="t5_to_t4_v6",tracking_name="Tracking_6_v6")


	myixia.start_traffic()
	myixia.collect_stats()
	myixia.check_traffic()

	print_title("Get crash information after injecting routes")

	sw5.get_crash_debug()
	sw6.get_crash_debug()

	#check_bgp_test_result(testcase,description,switches)

	# print_title("Get crash information after show bgp commands")
	# sw5.get_crash_debug()
	# sw6.get_crash_debug()


if testcase == 6092 or test_all or IPV6:
	testcase = 6092
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "Basic eBGP IPv4 And IPv6 ECMP peered to IXIA and traffic forwarding"
	print_test_subject(testcase,description)

	# IXIA and switch information
	


	ixia_ipv6_as_list = [101,102,103,104,105,106]
	ipv4_networks = ["10.10.1.1","10.10.1.1","10.10.1.1","10.10.2.1","10.10.2.1","10.10.2.1"]
	ipv6_networks = ["2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:102:1:1::1","2001:102:1:1::1","2001:102:1:1::1"]

	fsw_switches =switches[1:]
	network = BGP_networks(switches)

	# Infra configuration

	if clear_bgp:
		test_clean_config(switches =fsw_switches)

	if test_config:
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


if testcase == 6093 or test_all or IPV6:
	testcase = 6093
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "Basic eBGP traffic forwarding - IPv4 And IPv6 peered to IXIA and traffic forwarding, ipv6 scale and route flapping,longevity"
	tag = "basic traffic forwarding, ipv6 scale, route flapping,longevity"
	print_test_subject(testcase,description)

 
	ixia_ipv6_as_list = [101,102,103,104,105,106]
	ipv4_networks = ["10.10.1.1","10.10.2.1","10.10.3.1","10.10.4.1","10.10.5.1","10.10.6.1"]
	ipv6_networks = ["2001:101:1:1::1","2001:102:1:1::1","2001:103:1:1::1","2001:104:1:1::1","2001:105:1:1::211","2001:106:1:1::1"]

	if clear_bgp:
		test_clean_config(switches =fsw_switches)
	
	fsw_switches =switches[1:]
	sw5 = switches[5]
	sw6 = switches[6]
	network = BGP_networks(switches)
	#Infra configuration
	if clear_bgp:
		test_clean_config(switches =fsw_switches)
	if test_config:
		test_config_igp_ipv6_fabric(switches =fsw_switches)
	else:
		update_igp_database_all(switches =fsw_switches)

	network.biuld_ibgp_mesh_topo_sys_intf_v6()
	network.biuld_ibgp_mesh_topo_sys_intf()
	console_timer(20,msg=f"Test case {testcase}: After configuring fully mesh iBGP across all IPv6 system interfaces, wait....")
	network.show_summary()
	
	# FSW configuration
	for switch, ixia_port_info, ixia_as in zip(fsw_switches,portList_v4_v6,ixia_ipv6_as_list):
		if switch.router_bgp.config_ebgp_ixia_v6(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v6 peers ==============")
			exit()
		if switch.router_bgp.config_ebgp_ixia_v4(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v4 peers ==============")
			exit()

	print_title("Get crash information before injecting routes")
	for sw in fsw_switches:
		sw.clear_crash_log()


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
		topo.add_bgp(dut_ip=fsw_switches[i].vlan1_ip,bgp_type='external',num=2000)
		topo.add_bgp_v6(dut_ip=fsw_switches[i].vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=2000)
		i += 1

	for i in range(6):
		myixia.topologies[i].change_bgp_routes_attributes(flapping="RANDOM",address_family="v4")
		myixia.topologies[i].change_bgp_routes_attributes_v6(flapping="RANDOM",address_family="v6")

	myixia.start_protocol(wait=40)


	myixia.create_traffic(src_topo=myixia.topologies[0].topology, dst_topo=myixia.topologies[1].topology,traffic_name="t1_to_t2",tracking_name="Tracking_1")
	myixia.create_traffic(src_topo=myixia.topologies[1].topology, dst_topo=myixia.topologies[0].topology,traffic_name="t2_to_t1",tracking_name="Tracking_2")

	myixia.create_traffic(src_topo=myixia.topologies[2].topology, dst_topo=myixia.topologies[3].topology,traffic_name="t2_to_t3",tracking_name="Tracking_3")
	myixia.create_traffic(src_topo=myixia.topologies[3].topology, dst_topo=myixia.topologies[2].topology,traffic_name="t3_to_t2",tracking_name="Tracking_4")

	myixia.create_traffic(src_topo=myixia.topologies[4].topology, dst_topo=myixia.topologies[5].topology,traffic_name="t4_to_t5",tracking_name="Tracking_5")
	myixia.create_traffic(src_topo=myixia.topologies[5].topology, dst_topo=myixia.topologies[4].topology,traffic_name="t5_to_t4",tracking_name="Tracking_6")


	myixia.create_traffic_v6(src_topo=myixia.topologies[0].topology, dst_topo=myixia.topologies[1].topology,traffic_name="t1_to_t2_v6",tracking_name="Tracking_1_v6")
	myixia.create_traffic_v6(src_topo=myixia.topologies[1].topology, dst_topo=myixia.topologies[0].topology,traffic_name="t2_to_t1_v6",tracking_name="Tracking_2_v6")

	myixia.create_traffic_v6(src_topo=myixia.topologies[2].topology, dst_topo=myixia.topologies[3].topology,traffic_name="t2_to_t3_v6",tracking_name="Tracking_3_v6")
	myixia.create_traffic_v6(src_topo=myixia.topologies[3].topology, dst_topo=myixia.topologies[2].topology,traffic_name="t3_to_t2_v6",tracking_name="Tracking_4_v6")

	myixia.create_traffic_v6(src_topo=myixia.topologies[4].topology, dst_topo=myixia.topologies[5].topology,traffic_name="t4_to_t5_v6",tracking_name="Tracking_5_v6")
	myixia.create_traffic_v6(src_topo=myixia.topologies[5].topology, dst_topo=myixia.topologies[4].topology,traffic_name="t5_to_t4_v6",tracking_name="Tracking_6_v6")


	myixia.start_traffic()
	while True:
		myixia.collect_stats()
		myixia.check_traffic()

		print_title("Get crash information after injecting routes and start traffic, check crash every 60 sec")

		for sw in fsw_switches:
			sw.find_crash()
			sw.clear_crash_log()
		console_timer(60,msg="Let traffic run another 60 seconds")



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

if testcase == 6101 or test_all or IPV6:
	testcase = 6101
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "Basic eBGP IPv6 peered to IXIA and traffic forwarding"
	print_test_subject(testcase,description)

	if clear_bgp:
		test_clean_config(switches =fsw_switches)

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


if testcase == 6111 or test_all or IPV6:
	testcase = 6111
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "eBGP multi-hop v6 via loopback interfaces"
	print_test_subject(testcase,description)

	# Clean up configuration before start testing
	if clear_bgp:
		test_clean_config(switches =fsw_switches)

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



if testcase == 6112 or test_all or IPV6:
	testcase = 6112
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "eBGP multi-hop v4 and v6 via loopback interfaces"
	print_test_subject(testcase,description)

	# Clean up configuration before start testing
	if clear_bgp:
		test_clean_config(switches =fsw_switches)

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

if testcase == 6113 or test_all or IPV6:
	testcase = 6113
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "eBGP multi-hop v6 attribute-unchanged"
	tags = "ebgp attribute-unchanged"
	print_test_subject(testcase,description)


	if clear_bgp:
		test_clean_config(switches =fsw_switches)

	if test_config:
		test_config_igp_ipv6_fabric(switches =fsw_switches)
		console_timer(20,msg=f"Test case {testcase}: After configuring ospf and ospfv6 routing protocols, wait for 20 seconds")
	
	fsw_switches =switches[1:]
	network = BGP_networks(fsw_switches)

	network.show_summary_v6()

	for switch in fsw_switches:
		switch.router_bgp.config_ebgp_mesh_multihop_v6()
	console_timer(60,msg="After configuring eBGP sessions, wait for 60s")

	for switch in fsw_switches:
		switch.router_bgp.config_all_neighbor_commands("set attribute-unchanged6 next-hop as-path med")
		switch.router_bgp.config_all_neighbor_commands("set attribute-unchanged next-hop as-path med")

	#For IPv4 use static entry index 2, as index 1 is being used for mgmt default route
	fsw_switches[0].config_static_route_host(index=2,dst="200.200.200.201",gw="10.1.1.211")
	fsw_switches[1].config_static_route_host(index=2,dst="200.200.200.202",gw="10.1.1.212")
	fsw_switches[2].config_static_route_host(index=2,dst="200.200.200.203",gw="10.1.1.213")
	fsw_switches[3].config_static_route_host(index=2,dst="200.200.200.204",gw="10.1.1.214")
	fsw_switches[4].config_static_route_host(index=2,dst="200.200.200.205",gw="10.1.1.215")
	fsw_switches[5].config_static_route_host(index=2,dst="200.200.200.206",gw="10.1.1.216")

	fsw_switches[0].config_static6_route_host(index=1,dst="2001:200:200:200::201",gw="2001:10:1:1::211")
	fsw_switches[1].config_static6_route_host(index=1,dst="2001:200:200:200::202",gw="2001:10:1:1::212")
	fsw_switches[2].config_static6_route_host(index=1,dst="2001:200:200:200::203",gw="2001:10:1:1::213")
	fsw_switches[3].config_static6_route_host(index=1,dst="2001:200:200:200::204",gw="2001:10:1:1::214")
	fsw_switches[4].config_static6_route_host(index=1,dst="2001:200:200:200::205",gw="2001:10:1:1::215")
	fsw_switches[5].config_static6_route_host(index=1,dst="2001:200:200:200::206",gw="2001:10:1:1::216")


	# for switch in switches:
	# 	switch.show_routing_v6()
	#check_bgp_test_result_v6(testcase,description,switches)

	ixia_ipv6_as_list = [65101,65102,65103,65104,65105,65106]
	ipv6_networks = ["2001:101:1:1::1","2001:102:1:1::1","2001:103:1:1::1","2001:104:1:1::1","2001:105:1:1::1","2001:106:1:1::1"]
	ipv4_networks = ["10.10.1.1","10.10.2.1","10.10.3.1","10.10.4.1","10.10.5.1","10.10.6.1"]

	for switch in switches:
		switch.show_routing_v6()
	for switch, ixia_port_info, ixia_as in zip(fsw_switches,portList_v4_v6,ixia_ipv6_as_list):
		if switch.router_bgp.config_ebgp_ixia_v6(ixia_port=ixia_port_info,ixia_as=ixia_as,sw_as=switch.ebgp_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v6 peers ==============")
			exit()
		if switch.router_bgp.config_ebgp_ixia_v4(ixia_port=ixia_port_info,ixia_as=ixia_as,sw_as=switch.ebgp_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v4 peers ==============")
			exit()

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
		topo.add_bgp(dut_ip=fsw_switches[i].vlan1_ip,bgp_type='external',num=1)
		topo.add_bgp_v6(dut_ip=fsw_switches[i].vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=1)
		i += 1

	 
	myixia.topologies[0].change_bgp_routes_attributes(origin="incomplete",med=4220,community=4,comm_base=4200,num_path=4,as_base=15012,aggregator="106.106.106.107",aggregator_as=66661,ext_community=6,excomm_base=2,com_type="routetarget",address_family="v4",next_hop="200.200.200.201")
	myixia.topologies[1].change_bgp_routes_attributes(origin="igp",med=4221,community=4,comm_base=4200,num_path=4,as_base=25012,aggregator="106.106.106.107",aggregator_as=66661,ext_community=6,excomm_base=2,com_type="routetarget",address_family="v4",next_hop="200.200.200.202")
	myixia.topologies[2].change_bgp_routes_attributes(origin="egp",med=4222,community=4,comm_base=4200,num_path=4,as_base=35012,aggregator="106.106.106.108",aggregator_as=66662,ext_community=6,excomm_base=3,com_type="routetarget",address_family="v4",next_hop="200.200.200.203")
	myixia.topologies[3].change_bgp_routes_attributes(origin="incomplete",med=4223,community=4,comm_base=4200,num_path=4,as_base=45012,aggregator="106.106.106.109",aggregator_as=66663,ext_community=6,excomm_base=4,com_type="routetarget",address_family="v4",next_hop="200.200.200.204")
	myixia.topologies[4].change_bgp_routes_attributes(origin="igp",med=4224,community=4,comm_base=4200,num_path=4,as_base=55012,aggregator="106.106.106.110",aggregator_as=66662,ext_community=6,excomm_base=5,com_type="routetarget",address_family="v4",next_hop="200.200.200.205")
	myixia.topologies[5].change_bgp_routes_attributes(origin="egp",med=4225,community=4,comm_base=4200,num_path=4,as_base=65012,aggregator="106.106.106.112",aggregator_as=66663,ext_community=6,excomm_base=6,com_type="routetarget",address_family="v4",next_hop="200.200.200.206")


	myixia.topologies[0].change_bgp_routes_attributes_v6(origin="incomplete",med=6220,community=6,comm_base=6200,num_path=5,as_base=61012,aggregator="106.106.106.107",aggregator_as=64102,ext_community=6,excomm_base=2,com_type="routetarget",address_family="v6",next_hop="2001:200:200:200::201")
	myixia.topologies[1].change_bgp_routes_attributes_v6(origin="igp",med=6221,community=6,comm_base=6200,num_path=5,as_base=61012,aggregator="106.106.106.108",aggregator_as=64102,ext_community=6,excomm_base=2,com_type="routetarget",address_family="v6",next_hop="2001:200:200:200::202")
	myixia.topologies[2].change_bgp_routes_attributes_v6(origin="egp",med=622,community=6,comm_base=6300,num_path=6,as_base=61013,aggregator="106.106.106.109",aggregator_as=64103,ext_community=6,excomm_base=3,com_type="routetarget",address_family="v6",next_hop="2001:200:200:200::203")
	myixia.topologies[3].change_bgp_routes_attributes_v6(origin="incomplete",med=6223,community=6,comm_base=6400,num_path=6,as_base=61014,aggregator="106.106.106.110",aggregator_as=64014,ext_community=6,excomm_base=4,com_type="routetarget",address_family="v6",next_hop="2001:200:200:200::204")
	myixia.topologies[4].change_bgp_routes_attributes_v6(origin="igp",med=6224,community=6,comm_base=6300,num_path=6,as_base=61015,aggregator="106.106.106.111",aggregator_as=64105,ext_community=6,excomm_base=5,com_type="routetarget",address_family="v6",next_hop="2001:200:200:200::205")
	myixia.topologies[5].change_bgp_routes_attributes_v6(origin="egp",med=6225,community=6,comm_base=6400,num_path=6,as_base=61016,aggregator="106.106.106.112",aggregator_as=64106,ext_community=6,excomm_base=6,com_type="routetarget",address_family="v6",next_hop="2001:200:200:200::206")

	myixia.start_protocol(wait=40)

	check_bgp_test_result_v6(testcase,description,fsw_switches)

if testcase == 6114 or test_all or IPV6:
	testcase = 6114
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "eBGP multi-hop v6 attribute-unchanged, back door"
	tags = "ebgp attribute-unchanged, backdoor"
	print_test_subject(testcase,description)

	fsw_switches =switches[1:]
	network = BGP_networks(fsw_switches)

	if clear_bgp:
		test_clean_config(switches =fsw_switches)

	if test_config:
		test_config_igp_ipv6_fabric(switches =fsw_switches)
		console_timer(20,msg=f"Test case {testcase}: After configuring ospf and ospfv6 routing protocols, wait for 20 seconds")
	else:
		update_igp_database_all(switches =fsw_switches)

	network.show_summary_v6()

	for switch in fsw_switches:
		switch.router_bgp.config_ebgp_mesh_multihop_v6()
	console_timer(60,msg="After configuring eBGP sessions, wait for 60s")

	for switch in fsw_switches:
		switch.router_bgp.config_all_neighbor_commands("set attribute-unchanged6 next-hop as-path med")
		switch.router_bgp.config_all_neighbor_commands("set attribute-unchanged next-hop as-path med")

	#For IPv4 use static entry index 2, as index 1 is being used for mgmt default route
	fsw_switches[0].config_static_route_host(index=2,dst="200.200.200.201",gw="10.1.1.211")
	fsw_switches[1].config_static_route_host(index=2,dst="200.200.200.202",gw="10.1.1.212")
	fsw_switches[2].config_static_route_host(index=2,dst="200.200.200.203",gw="10.1.1.213")
	fsw_switches[3].config_static_route_host(index=2,dst="200.200.200.204",gw="10.1.1.214")
	fsw_switches[4].config_static_route_host(index=2,dst="200.200.200.205",gw="10.1.1.215")
	fsw_switches[5].config_static_route_host(index=2,dst="200.200.200.206",gw="10.1.1.216")

	fsw_switches[0].config_static6_route_host(index=1,dst="2001:200:200:200::201",gw="2001:10:1:1::211")
	fsw_switches[1].config_static6_route_host(index=1,dst="2001:200:200:200::202",gw="2001:10:1:1::212")
	fsw_switches[2].config_static6_route_host(index=1,dst="2001:200:200:200::203",gw="2001:10:1:1::213")
	fsw_switches[3].config_static6_route_host(index=1,dst="2001:200:200:200::204",gw="2001:10:1:1::214")
	fsw_switches[4].config_static6_route_host(index=1,dst="2001:200:200:200::205",gw="2001:10:1:1::215")
	fsw_switches[5].config_static6_route_host(index=1,dst="2001:200:200:200::206",gw="2001:10:1:1::216")



	# for switch in switches:
	# 	switch.show_routing_v6()
	#check_bgp_test_result_v6(testcase,description,switches)

	ixia_ipv6_as_list = [65101,65102,65103,65104,65105,65106]
	ipv6_networks = ["2001:101:1:1::1","2001:102:1:1::1","2001:103:1:1::1","2001:104:1:1::1","2001:105:1:1::1","2001:106:1:1::1"]
	ipv4_networks = ["10.10.1.1","10.10.2.1","10.10.3.1","10.10.4.1","10.10.5.1","10.10.6.1"]

	for switch in switches:
		switch.show_routing_v6()
	for switch, ixia_port_info, ixia_as in zip(fsw_switches,portList_v4_v6,ixia_ipv6_as_list):
		if switch.router_bgp.config_ebgp_ixia_v6(ixia_port=ixia_port_info,ixia_as=ixia_as,sw_as=switch.ebgp_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v6 peers ==============")
			exit()
		if switch.router_bgp.config_ebgp_ixia_v4(ixia_port=ixia_port_info,ixia_as=ixia_as,sw_as=switch.ebgp_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v4 peers ==============")
			exit()

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
		topo.add_bgp(dut_ip=fsw_switches[i].vlan1_ip,bgp_type='external',num=1)
		topo.add_bgp_v6(dut_ip=fsw_switches[i].vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=1)
		i += 1

	#This is DUT #5, don't get confused!!!!
	# ixia_topology = myixia.topologies[4]
	# dut_switch = fsw_switches[4]
	# ixia_topology.change_bgp_routes_attributes(origin="egp",med=6111,community=6,comm_base=6100,num_path=6,as_base=65011,aggregator="106.106.106.106",aggregator_as=66660,ext_community=6,excomm_base=1,com_type="routetarget",address_family="v4",next_hop="200.200.200.200")
	myixia.topologies[0].change_bgp_routes_attributes(origin="incomplete",med=4220,community=4,comm_base=4200,num_path=4,as_base=15012,aggregator="106.106.106.107",aggregator_as=66661,ext_community=6,excomm_base=2,com_type="routetarget",address_family="v4",next_hop="200.200.200.201")
	myixia.topologies[1].change_bgp_routes_attributes(origin="igp",med=4221,community=4,comm_base=4200,num_path=4,as_base=25012,aggregator="106.106.106.107",aggregator_as=66661,ext_community=6,excomm_base=2,com_type="routetarget",address_family="v4",next_hop="200.200.200.202")
	myixia.topologies[2].change_bgp_routes_attributes(origin="egp",med=4222,community=4,comm_base=4200,num_path=4,as_base=35012,aggregator="106.106.106.108",aggregator_as=66662,ext_community=6,excomm_base=3,com_type="routetarget",address_family="v4",next_hop="200.200.200.203")
	myixia.topologies[3].change_bgp_routes_attributes(origin="incomplete",med=4223,community=4,comm_base=4200,num_path=4,as_base=45012,aggregator="106.106.106.109",aggregator_as=66663,ext_community=6,excomm_base=4,com_type="routetarget",address_family="v4",next_hop="200.200.200.204")
	myixia.topologies[4].change_bgp_routes_attributes(origin="igp",med=4224,community=4,comm_base=4200,num_path=4,as_base=55012,aggregator="106.106.106.110",aggregator_as=66662,ext_community=6,excomm_base=5,com_type="routetarget",address_family="v4",next_hop="200.200.200.205")
	myixia.topologies[5].change_bgp_routes_attributes(origin="egp",med=4225,community=4,comm_base=4200,num_path=4,as_base=65012,aggregator="106.106.106.112",aggregator_as=66663,ext_community=6,excomm_base=6,com_type="routetarget",address_family="v4",next_hop="200.200.200.206")


	# ixia_topology.change_bgp_routes_attributes_v6(origin="egp",med=6111,community=6,comm_base=6100,num_path=6,as_base=65011,aggregator="106.106.106.106",aggregator_as=64101,ext_community=6,excomm_base=1,com_type="routetarget",address_family="v6",next_hop="2001:200:200:200::200")
	myixia.topologies[0].change_bgp_routes_attributes_v6(origin="incomplete",med=6220,community=6,comm_base=6200,num_path=5,as_base=61012,aggregator="106.106.106.107",aggregator_as=64102,ext_community=6,excomm_base=2,com_type="routetarget",address_family="v6",next_hop="2001:200:200:200::201")
	myixia.topologies[1].change_bgp_routes_attributes_v6(origin="igp",med=6221,community=6,comm_base=6200,num_path=5,as_base=61012,aggregator="106.106.106.108",aggregator_as=64102,ext_community=6,excomm_base=2,com_type="routetarget",address_family="v6",next_hop="2001:200:200:200::202")
	myixia.topologies[2].change_bgp_routes_attributes_v6(origin="egp",med=622,community=6,comm_base=6300,num_path=6,as_base=61013,aggregator="106.106.106.109",aggregator_as=64103,ext_community=6,excomm_base=3,com_type="routetarget",address_family="v6",next_hop="2001:200:200:200::203")
	myixia.topologies[3].change_bgp_routes_attributes_v6(origin="incomplete",med=6223,community=6,comm_base=6400,num_path=6,as_base=61014,aggregator="106.106.106.110",aggregator_as=64014,ext_community=6,excomm_base=4,com_type="routetarget",address_family="v6",next_hop="2001:200:200:200::204")
	myixia.topologies[4].change_bgp_routes_attributes_v6(origin="igp",med=6224,community=6,comm_base=6300,num_path=6,as_base=61015,aggregator="106.106.106.111",aggregator_as=64105,ext_community=6,excomm_base=5,com_type="routetarget",address_family="v6",next_hop="2001:200:200:200::205")
	myixia.topologies[5].change_bgp_routes_attributes_v6(origin="egp",med=6225,community=6,comm_base=6400,num_path=6,as_base=61016,aggregator="106.106.106.112",aggregator_as=64106,ext_community=6,excomm_base=6,com_type="routetarget",address_family="v6",next_hop="2001:200:200:200::206")

	myixia.start_protocol(wait=40)


	vlans = [10,11,12,13,14,15]
	for ipv4,ipv6,v in zip(ipv4_networks,ipv6_networks,vlans):
		fsw_switches[0].config_sys_vlan_v6(ipv6=ipv6,ipv4=ipv4,vlan=v)

	index_list = [100,101,102,103,104,105]
	for sw in fsw_switches:
		for ipv4,ipv6,index in zip(ipv4_networks,ipv6_networks,index_list):
			sw.router_bgp.bgp_network_cmd(network=ipv4,cmd="set backdoor enable",index=index)
			sw.router_bgp.bgp_network6_cmd(network=ipv6,cmd="set backdoor enable",index=index)
 	
	check_bgp_test_result_v6(testcase,description,fsw_switches)

if testcase == 6115 or test_all or IPV6:
	testcase = 6115
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "Direct eBGP, attribute-unchanged, next_hop recursive"
	tags = "direct ebgp attribute-unchanged, next_hop recursive"
	print_test_subject(testcase,description)

	fsw_switches =switches[1:]
	network = BGP_networks(fsw_switches)

	if clear_bgp:
		test_clean_config(switches =fsw_switches)

	if test_config:
		test_config_igp_ipv6(switches =fsw_switches)
		console_timer(20,msg=f"Test case {testcase}: After configuring ospf and ospfv6 routing protocols, wait for 20 seconds")
	else:
		update_igp_database_all(switches =fsw_switches)

	network.show_summary_v6()

	for switch in fsw_switches:
		switch.router_bgp.config_ebgp_mesh_svi_v6()
	console_timer(60,msg="After configuring eBGP sessions, wait for 60s")

	for switch in fsw_switches:
		switch.router_bgp.config_all_neighbor_commands("set attribute-unchanged6 next-hop as-path med")
		switch.router_bgp.config_all_neighbor_commands("set attribute-unchanged next-hop as-path med")

	#For IPv4 use static entry index 2, as index 1 is being used for mgmt default route
	fsw_switches[0].config_static_route_host(index=2,dst="200.200.200.201",gw="10.1.1.211")
	fsw_switches[1].config_static_route_host(index=2,dst="200.200.200.202",gw="10.1.1.212")
	fsw_switches[2].config_static_route_host(index=2,dst="200.200.200.203",gw="10.1.1.213")
	fsw_switches[3].config_static_route_host(index=2,dst="200.200.200.204",gw="10.1.1.214")
	fsw_switches[4].config_static_route_host(index=2,dst="200.200.200.205",gw="10.1.1.215")
	fsw_switches[5].config_static_route_host(index=2,dst="200.200.200.206",gw="10.1.1.216")

	fsw_switches[0].config_static6_route_host(index=1,dst="2001:200:200:200::201",gw="2001:10:1:1::211")
	fsw_switches[1].config_static6_route_host(index=1,dst="2001:200:200:200::202",gw="2001:10:1:1::212")
	fsw_switches[2].config_static6_route_host(index=1,dst="2001:200:200:200::203",gw="2001:10:1:1::213")
	fsw_switches[3].config_static6_route_host(index=1,dst="2001:200:200:200::204",gw="2001:10:1:1::214")
	fsw_switches[4].config_static6_route_host(index=1,dst="2001:200:200:200::205",gw="2001:10:1:1::215")
	fsw_switches[5].config_static6_route_host(index=1,dst="2001:200:200:200::206",gw="2001:10:1:1::216")

	ixia_ipv6_as_list = [65101,65102,65103,65104,65105,65106]
	ipv6_networks = ["2001:101:1:1::1","2001:102:1:1::1","2001:103:1:1::1","2001:104:1:1::1","2001:105:1:1::1","2001:106:1:1::1"]
	ipv4_networks = ["10.10.1.1","10.10.2.1","10.10.3.1","10.10.4.1","10.10.5.1","10.10.6.1"]

	for switch in switches:
		switch.show_routing_v6()
	for switch, ixia_port_info, ixia_as in zip(fsw_switches,portList_v4_v6,ixia_ipv6_as_list):
		if switch.router_bgp.config_ebgp_ixia_v6(ixia_port=ixia_port_info,ixia_as=ixia_as,sw_as=switch.ebgp_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v6 peers ==============")
			exit()
		if switch.router_bgp.config_ebgp_ixia_v4(ixia_port=ixia_port_info,ixia_as=ixia_as,sw_as=switch.ebgp_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v4 peers ==============")
			exit()

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
		topo.add_bgp(dut_ip=fsw_switches[i].vlan1_ip,bgp_type='external',num=1)
		topo.add_bgp_v6(dut_ip=fsw_switches[i].vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=1)
		i += 1

	#This is DUT #5, don't get confused!!!!
	# ixia_topology = myixia.topologies[4]
	# dut_switch = fsw_switches[4]
	# ixia_topology.change_bgp_routes_attributes(origin="egp",med=6111,community=6,comm_base=6100,num_path=6,as_base=65011,aggregator="106.106.106.106",aggregator_as=66660,ext_community=6,excomm_base=1,com_type="routetarget",address_family="v4",next_hop="200.200.200.200")
	myixia.topologies[0].change_bgp_routes_attributes(origin="incomplete",med=4220,community=4,comm_base=4200,num_path=4,as_base=15012,aggregator="106.106.106.107",aggregator_as=66661,ext_community=6,excomm_base=2,com_type="routetarget",address_family="v4",next_hop="200.200.200.201")
	myixia.topologies[1].change_bgp_routes_attributes(origin="igp",med=4221,community=4,comm_base=4200,num_path=4,as_base=25012,aggregator="106.106.106.107",aggregator_as=66661,ext_community=6,excomm_base=2,com_type="routetarget",address_family="v4",next_hop="200.200.200.202")
	myixia.topologies[2].change_bgp_routes_attributes(origin="egp",med=4222,community=4,comm_base=4200,num_path=4,as_base=35012,aggregator="106.106.106.108",aggregator_as=66662,ext_community=6,excomm_base=3,com_type="routetarget",address_family="v4",next_hop="200.200.200.203")
	myixia.topologies[3].change_bgp_routes_attributes(origin="incomplete",med=4223,community=4,comm_base=4200,num_path=4,as_base=45012,aggregator="106.106.106.109",aggregator_as=66663,ext_community=6,excomm_base=4,com_type="routetarget",address_family="v4",next_hop="200.200.200.204")
	myixia.topologies[4].change_bgp_routes_attributes(origin="igp",med=4224,community=4,comm_base=4200,num_path=4,as_base=55012,aggregator="106.106.106.110",aggregator_as=66662,ext_community=6,excomm_base=5,com_type="routetarget",address_family="v4",next_hop="200.200.200.205")
	myixia.topologies[5].change_bgp_routes_attributes(origin="egp",med=4225,community=4,comm_base=4200,num_path=4,as_base=65012,aggregator="106.106.106.112",aggregator_as=66663,ext_community=6,excomm_base=6,com_type="routetarget",address_family="v4",next_hop="200.200.200.206")


	# ixia_topology.change_bgp_routes_attributes_v6(origin="egp",med=6111,community=6,comm_base=6100,num_path=6,as_base=65011,aggregator="106.106.106.106",aggregator_as=64101,ext_community=6,excomm_base=1,com_type="routetarget",address_family="v6",next_hop="2001:200:200:200::200")
	myixia.topologies[0].change_bgp_routes_attributes_v6(origin="incomplete",med=6220,community=6,comm_base=6200,num_path=5,as_base=61012,aggregator="106.106.106.107",aggregator_as=64102,ext_community=6,excomm_base=2,com_type="routetarget",address_family="v6",next_hop="2001:200:200:200::201")
	myixia.topologies[1].change_bgp_routes_attributes_v6(origin="igp",med=6221,community=6,comm_base=6200,num_path=5,as_base=61012,aggregator="106.106.106.108",aggregator_as=64102,ext_community=6,excomm_base=2,com_type="routetarget",address_family="v6",next_hop="2001:200:200:200::202")
	myixia.topologies[2].change_bgp_routes_attributes_v6(origin="egp",med=622,community=6,comm_base=6300,num_path=6,as_base=61013,aggregator="106.106.106.109",aggregator_as=64103,ext_community=6,excomm_base=3,com_type="routetarget",address_family="v6",next_hop="2001:200:200:200::203")
	myixia.topologies[3].change_bgp_routes_attributes_v6(origin="incomplete",med=6223,community=6,comm_base=6400,num_path=6,as_base=61014,aggregator="106.106.106.110",aggregator_as=64014,ext_community=6,excomm_base=4,com_type="routetarget",address_family="v6",next_hop="2001:200:200:200::204")
	myixia.topologies[4].change_bgp_routes_attributes_v6(origin="igp",med=6224,community=6,comm_base=6300,num_path=6,as_base=61015,aggregator="106.106.106.111",aggregator_as=64105,ext_community=6,excomm_base=5,com_type="routetarget",address_family="v6",next_hop="2001:200:200:200::205")
	myixia.topologies[5].change_bgp_routes_attributes_v6(origin="egp",med=6225,community=6,comm_base=6400,num_path=6,as_base=61016,aggregator="106.106.106.112",aggregator_as=64106,ext_community=6,excomm_base=6,com_type="routetarget",address_family="v6",next_hop="2001:200:200:200::206")

	myixia.start_protocol(wait=40)

	check_bgp_test_result_v6(testcase,description,fsw_switches)

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

if testcase == 6121 or test_all or IPV6:
	testcase = 6121
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGPv6 policy and route filtering:duplicated routes were injected from IXIA."
	print_test_subject(testcase,description)

	if clear_bgp:
		test_clean_config(switches =fsw_switches)

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


if testcase == 6131 or test_all or IPV6:
	testcase = 6131
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGPv6 policy and route filtering: Origin attribute. "
	print_test_subject(testcase,description)

	apiServerIp = '10.105.19.19'
	ixChassisIpList = ['10.105.241.234']

	if clear_bgp:
		test_clean_config(switches =fsw_switches)
	 
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
	
	for switch,ixia_port_info in zip(switches,portList_v4_v6):
		if switch.router_bgp.config_ebgp_ixia(ixia_port_info) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP peers ==============")
			exit()

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

 
if testcase == 6140 or test_all or IPV6:
	testcase = 6140
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGPv6 Best Routes Selection: Router ID and Next Hop. eBGP path with smallest MED will be elected "
	print_test_subject(testcase,description)

 
	
	if clear_bgp:
		test_clean_config(switches =fsw_switches)

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

if testcase == 6141 or test_all or IPV6:
	testcase = 6141
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGPv6 Best Routes Selection: MED. eBGP path with smallest MED will be elected "
	print_test_subject(testcase,description)

	fsw_switches =switches[1:]
	if clear_bgp:
		test_clean_config(switches =fsw_switches)
	
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

if testcase == 6142 or test_all or IPV6:
	testcase = 6142
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGPv6 Best Routes Selection: Origin. Run the test at the last 2 switches: switches[-2:] "
	print_test_subject(testcase,description)

	
	fsw_switches =switches[1:]
	if clear_bgp:
		test_clean_config(switches =fsw_switches)

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


if testcase == 6143 or test_all or IPV6:
	testcase = 6143
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGPv6 Best Routes Selection: Weight. Run the test at the last switch: switches[-1] "
	print_test_subject(testcase,description)

	fsw_switches =switches[1:]
	if clear_bgp:
		test_clean_config(switches =fsw_switches)
 
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

if testcase == 6144 or test_all or IPV6:
	testcase = 6144
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGPv6 Best Routes Selection: Local Preference. Run the test at the last switch: switches[-1] "
	print_test_subject(testcase,description)

	fsw_switches =switches[1:]
	if clear_bgp:
		test_clean_config(switches =fsw_switches)

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


	myixia.topologies[0].change_bgp_routes_attributes_v6(local=610,address_family="v6")
	myixia.topologies[1].change_bgp_routes_attributes_v6(local=620,address_family="v6")
	myixia.topologies[2].change_bgp_routes_attributes_v6(local=630,address_family="v6")
	myixia.topologies[3].change_bgp_routes_attributes_v6(local=640,address_family="v6")

	myixia.topologies[0].change_bgp_routes_attributes_v6(local=410,address_family="v4")
	myixia.topologies[1].change_bgp_routes_attributes_v6(local=420,address_family="v4")
	myixia.topologies[2].change_bgp_routes_attributes_v6(local=430,address_family="v4")
	myixia.topologies[3].change_bgp_routes_attributes_v6(local=440,address_family="v4")

	myixia.start_protocol(wait=40)

	check_bgp_test_result_v6(testcase,description,sw6_switch)

if testcase == 6145 or test_all or IPV6:
	testcase = 6145
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGPv6 Best Routes Selection: Community. Run the test at the last switch: switches[-1] "
	print_test_subject(testcase,description)

	fsw_switches =switches[1:]
	if clear_bgp:
		test_clean_config(switches =fsw_switches)

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


if testcase == 6146 or test_all or IPV6:
	testcase = 6146
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGPv6 Best Routes Selection: AS Path. Run the test at the last switch: switches[-1] "
	tags = "IPv6 as path, multipath-relax"
	print_test_subject(testcase,description)


	fsw_switches =switches[1:]
	if clear_bgp:
		test_clean_config(switches =fsw_switches)

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

	if clear_bgp:
		test_clean_config(switches =fsw_switches)
	if test_config:
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

if testcase == 6147 or test_all or IPV6:
	testcase = 6147
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGPv6 Best Routes Selection: Aggreator. Run the test at the last switch: switches[-1] "
	print_test_subject(testcase,description)

	fsw_switches =switches[1:]
	if clear_bgp:
		test_clean_config(switches =fsw_switches)
	
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


if testcase == 6148 or test_all or IPV6:
	testcase = 6148
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGPv6 Best Routes Selection: Ext-Community. Run the test at the last switch: switches[-1] "
	print_test_subject(testcase,description)


	fsw_switches =switches[1:]
	if clear_bgp:
		test_clean_config(switches =fsw_switches)

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

if testcase == 6149 or test_all or IPV6:
	testcase = 6149
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGPv6 Best Routes Selection: Put all attributes together. Run the test at the last switch: switches[-1] "
	tag = "all attributes,route-map"
	print_test_subject(testcase,description)

	fsw_switches =switches[1:]
	if clear_bgp:
		test_clean_config(switches =fsw_switches)
 
	ixia_ipv6_as_list = [101,102,103,104,105,106]
	#what matters are the last 4 elements of the list.  
	ipv6_networks = ["2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:102:1:1::1","2001:102:1:1::1"]
	ipv4_networks = ["10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1","10.10.2.1","10.10.2.1"]

	cisco_switch = switches[0]
	sw6_switch = switches[1]
	dut_switch = sw6_switch
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

	if clear_bgp:
		test_clean_config(switches =fsw_switches)
	if test_config:
		test_config_igp_ipv6(switches =fsw_switches)
		#network.biuld_ibgp_mesh_topo_sys_intf_v6()
		#network.biuld_ibgp_mesh_topo_sys_intf_one()
		network.biuld_ibgp_mesh_topo_sys_intf_v6_one()
		console_timer(20,msg=f"Test case {testcase}: After configuring fully mesh iBGP across all IPv6 system interfaces, wait....")
	network.show_summary_v6()

	test_config_single_switch2ixia_all(switch=sw6_switch,ixia_ports=sw6_ixia_ports,as_lists=sw6_as_lists)
	cisco_switch.cisco_config_ebgp_ixia()

	myixia = IXIA(apiServerIp,ixChassisIpList,my_ixia_ports)

	test_config_ixia_bgp_all_one_switch_compare(myixia.topologies[:2],cisco_ipv6_networks,cisco_ipv4_networks,cisco_switch,cisco_as_lists)
	test_config_ixia_bgp_all_one_switch_compare(myixia.topologies[-2:],sw6_ipv6_networks,sw6_ipv4_networks,sw6_switch,sw6_as_lists)


	myixia.topologies[0].change_bgp_routes_attributes(origin="egp",med=6111,community=6,comm_base=6100,num_path=6,as_base=65010,aggregator="106.106.106.106",aggregator_as=66660,originator="114.114.114.114",ext_community=6,excomm_base=65010,com_type="routetarget",address_family="v4")
	myixia.topologies[1].change_bgp_routes_attributes(origin="incomplete",med=6222,community=5,comm_base=6200,num_path=5,as_base=65020,aggregator="106.106.106.107",aggregator_as=66661,originator="114.114.114.115",ext_community=6,excomm_base=65020,com_type="routetarget",address_family="v4")
	myixia.topologies[2].change_bgp_routes_attributes(origin="egp",med=6333,community=6,comm_base=6300,num_path=6,as_base=65030,aggregator="106.106.106.108",aggregator_as=66662,originator="114.114.114.116",ext_community=6,excomm_base=65030,com_type="routetarget",address_family="v4")
	myixia.topologies[3].change_bgp_routes_attributes(origin="incomplete",med=6444,community=5,comm_base=6400,num_path=6,as_base=65040,aggregator="106.106.106.109",aggregator_as=66663,originator="114.114.114.117",ext_community=6,excomm_base=65040,com_type="routetarget",address_family="v4")


	myixia.topologies[0].change_bgp_routes_attributes_v6(origin="egp",med=6111,community=6,comm_base=6100,num_path=6,as_base=65010,aggregator="106.106.106.106",aggregator_as=66660,originator="116.116.116.116",ext_community=6,excomm_base=65010,com_type="routetarget",address_family="v6")
	myixia.topologies[1].change_bgp_routes_attributes_v6(origin="incomplete",med=6222,community=5,comm_base=6200,num_path=5,as_base=65020,aggregator="106.106.106.107",aggregator_as=66661,originator="116.116.116.117",ext_community=6,excomm_base=65020,com_type="routetarget",address_family="v6")
	myixia.topologies[2].change_bgp_routes_attributes_v6(origin="egp",med=6333,community=6,comm_base=6300,num_path=6,as_base=65030,aggregator="106.106.106.108",aggregator_as=66662,originator="116.116.116.118",ext_community=6,excomm_base=65030,com_type="routetarget",address_family="v6")
	myixia.topologies[3].change_bgp_routes_attributes_v6(origin="incomplete",med=6444,community=5,comm_base=6400,num_path=6,as_base=65040,aggregator="106.106.106.109",aggregator_as=66663,originator="116.116.116.119",ext_community=6,excomm_base=65040,com_type="routetarget",address_family="v6")
	 
	myixia.start_protocol(wait=40)

	config = """
	config router prefix-list6
    edit "ixia_routes6"
            config rule
                edit 1
                    set prefix6 "any"
                    unset ge
                    unset le
                next
            end
    next
	end

	config router prefix-list
    edit "ixia-routes"
            config rule
                edit 1
                    set prefix any
                    unset ge
                    unset le
                next
            end
    next
	end

	config router route-map
    edit "rt"
        set protocol bgp
            config rule
                edit 1
                    set match-ip6-address "ixia_routes6"
                        set set-extcommunity-rt "3002:1"
                next
            end
    next
    edit "rt4"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-address "ixia-routes"
                        set set-extcommunity-rt "3004:1"
                next
            end
    next
    edit "soo6"
        set protocol bgp
            config rule
                edit 1
                    set match-ip6-address "ixia_routes6"
                        set set-extcommunity-soo "5000:1"
                next
            end
    next
    edit "aggregator-as"
        set protocol bgp
            config rule
                edit 1
                    set match-ip6-address "ixia_routes6"
                    set set-aggregator-as 77777
                    set set-aggregator-ip 77.77.77.77
                next
            end
    next
    edit "atomic-aggregate"
        set protocol bgp
            config rule
                edit 1
                    set match-ip6-address "ixia_routes6"
                    set set-atomic-aggregate enable
                next
            end
    next
    edit "originator-id"
        set protocol bgp
            config rule
                edit 1
                    set match-ip6-address "ixia_routes6"
                    set set-originator-id 91.91.91.91
                next
            end
    next
    edit "next_hop_local"
        set protocol bgp
            config rule
                edit 1
                    set match-ip6-address "ixia_routes6"
                    set set-ip6-nexthop-local fe80::9999:1ff:fe01:101
                next
            end
    next
	end

	"""
	dut_switch.config_commands(config)


	route_map_list = ["rt","soo6","aggregator-as","atomic-aggregate","originator-id","next_hop_local"]

	for rm in route_map_list:
		config = f"""
		config router bgp
			config neighbor
				edit "2001:10:1:1::215"
					set route-map-in6 {rm}
				next
				edit "2001:10:1:1::216"
					set route-map-in6 {rm}
				next
			end
		end
		"""
		dut_switch.config_commands(config)
		dut_switch.router_bgp.clear_bgp_all()
		sleep(5)
		dut_switch.show_command("get router info6 bgp network 2001:102:1:1::9/128")


if testcase == 61410 or test_all or IPV6:
	testcase = 61410
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGPv6 Best Routes Selection: eBGP over iBGP. Run the test at the last switch: switches[-1] "
	print_test_subject(testcase,description)


	fsw_switches =switches[1:]
	if clear_bgp:
		test_clean_config(switches =fsw_switches)
	
	ixia_ipv6_as_list = [101,102,103,104,105,106]
	# Have the same IPv4 and IPv6 advertised via eBGP and iBGP. Look at sw6 to pick eBGP route
	ipv6_networks = ["2001:101:1:1::1","2001:101:1:1::1","2001:102:1:1::1","2001:102:1:1::1","2001:102:1:1::1","2001:102:1:1::1"]
	ipv4_networks = ["10.10.1.1","10.10.1.1","10.10.2.1","10.10.2.1","10.10.2.1","10.10.2.1"]

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
 
	#test_config_ixia_bgp_all_one_switch_cisco(myixia,sw6_ipv6_networks,sw6_ipv4_networks,sw6_switch,sw6_as_lists,cisco_ipv6_networks,cisco_ipv4_networks,cisco_switch,cisco_as_lists)
	test_config_ixia_bgp_all_one_switch_compare(myixia.topologies[:2],cisco_ipv6_networks,cisco_ipv4_networks,cisco_switch,cisco_as_lists)
	test_config_ixia_bgp_all_one_switch_compare(myixia.topologies[-2:],sw6_ipv6_networks,sw6_ipv4_networks,sw6_switch,sw6_as_lists)

	myixia.start_protocol(wait=40)

	check_bgp_test_result_v6(testcase,description,sw6_switch)

if testcase == 61411 or test_all or IPV6:
	testcase = 61411
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGPv6 Best Routes Selection: ECMP over the 548D - switches[6] "
	print_test_subject(testcase,description)

	fsw_switches =switches[1:]
	if clear_bgp:
		test_clean_config(switches =fsw_switches)
	
	ixia_ipv6_as_list = [101,102,103,104,105,106]
	ipv6_networks = ["2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:102:1:1::1","2001:102:1:1::1"]
	ipv4_networks = ["10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1","10.10.2.1","10.10.2.1"]

	cisco_switch = switches[0]
	sw6_switch = switches[6]
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

	myixia.topologies[0].change_bgp_routes_attributes(local=610,address_family="v6")
	myixia.topologies[1].change_bgp_routes_attributes(local=620,address_family="v6")
	myixia.topologies[2].change_bgp_routes_attributes(local=630,address_family="v6")
	myixia.topologies[3].change_bgp_routes_attributes(local=640,address_family="v6")


	myixia.topologies[0].change_bgp_routes_attributes(local=410,address_family="v4")
	myixia.topologies[1].change_bgp_routes_attributes(local=420,address_family="v4")
	myixia.topologies[2].change_bgp_routes_attributes(local=430,address_family="v4")
	myixia.topologies[3].change_bgp_routes_attributes(local=440,address_family="v4")


	myixia.topologies[0].change_bgp_routes_attributes_v6(local=610,address_family="v6")
	myixia.topologies[1].change_bgp_routes_attributes_v6(local=620,address_family="v6")
	myixia.topologies[2].change_bgp_routes_attributes_v6(local=630,address_family="v6")
	myixia.topologies[3].change_bgp_routes_attributes_v6(local=640,address_family="v6")

	myixia.topologies[0].change_bgp_routes_attributes_v6(local=410,address_family="v4")
	myixia.topologies[1].change_bgp_routes_attributes_v6(local=420,address_family="v4")
	myixia.topologies[2].change_bgp_routes_attributes_v6(local=430,address_family="v4")
	myixia.topologies[3].change_bgp_routes_attributes_v6(local=440,address_family="v4")

	myixia.start_protocol(wait=40)

	check_bgp_test_result_v6(testcase,description,sw6_switch)


if testcase == 61412 or test_all:
	testcase = 61412
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "BGPv6 Best Routes Selection: Well-known Community. Run the test at the first FSW switch: switches[1] "
	print_test_subject(testcase,description)

	# apiServerIp = '10.105.19.19'
	# ixChassisIpList = ['10.105.241.234']

	# portList_v4_v6 = [
	# [ixChassisIpList[0], 2, 11,"00:11:01:01:01:01","10.1.1.211/24","10.1.1.1","2001:10:1:1::211/64","2001:10:1:1::1",1], 
 #    [ixChassisIpList[0], 2, 12,"00:12:01:01:01:01","10.1.1.212/24","10.1.1.1","2001:10:1:1::212/64","2001:10:1:1::1",1],
 #    [ixChassisIpList[0], 2, 13,"00:13:01:01:01:01","10.1.1.213/24","10.1.1.1","2001:10:1:1::213/64","2001:10:1:1::1",1], 
 #    [ixChassisIpList[0], 2, 14,"00:14:01:01:01:01","10.1.1.214/24","10.1.1.1","2001:10:1:1::214/64","2001:10:1:1::1",1],
 #    [ixChassisIpList[0], 2, 15,"00:15:01:01:01:01","10.1.1.215/24","10.1.1.1","2001:10:1:1::215/64","2001:10:1:1::1",1],
 #    [ixChassisIpList[0], 2, 16,"00:16:01:01:01:01","10.1.1.216/24","10.1.1.1","2001:10:1:1::216/64","2001:10:1:1::1",1]
 #    ]

	ixia_ipv6_as_list = [101,102,103,104,105,106]
	ipv6_networks = ["2001:101:1:1::1","2001:103:1:1::1","2001:103:1:1::1","2001:104:1:1::1","2001:105:1:1::1","2001:106:1:1::1"]
	ipv4_networks = ["10.10.1.1","10.10.2.1","10.10.3.1","10.10.4.1","10.10.5.1","10.10.6.1"]

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


	# myixia.topologies[0].change_bgp_routes_attributes(community=6,comm_base=6100,address_family="v6")
	# myixia.topologies[1].change_bgp_routes_attributes(community=5,comm_base=6200,address_family="v6")
	# myixia.topologies[2].change_bgp_routes_attributes(community=6,comm_base=6300,address_family="v6")
	# myixia.topologies[3].change_bgp_routes_attributes(community=5,comm_base=6400,address_family="v6")

	myixia.start_protocol(wait=40)

	IANA_WELL_KNOWNS = """
		0xFFFF0000	GRACEFUL_SHUTDOWN	[RFC8326]
		0xFFFF0001	ACCEPT_OWN	[RFC7611]
		0xFFFF0002	ROUTE_FILTER_TRANSLATED_v4	[draft-l3vpn-legacy-rtc]
		0xFFFF0003	ROUTE_FILTER_v4	[draft-l3vpn-legacy-rtc]
		0xFFFF0004	ROUTE_FILTER_TRANSLATED_v6	[draft-l3vpn-legacy-rtc]
		0xFFFF0005	ROUTE_FILTER_v6	[draft-l3vpn-legacy-rtc]
		0xFFFF0006	LLGR_STALE	[draft-uttaro-idr-bgp-persistence]
		0xFFFF0007	NO_LLGR	[draft-uttaro-idr-bgp-persistence]
		0xFFFF0008	accept-own-nexthop	[draft-agrewal-idr-accept-own-nexthop]
		0xFFFF0009-0xFFFF0299	Unassigned	
		0xFFFF029A	BLACKHOLE	[RFC7999]
		0xFFFF029B-0xFFFFFF00	Unassigned	
		0xFFFFFF01	NO_EXPORT	[RFC1997]
		0xFFFFFF02	NO_ADVERTISE	[RFC1997]
		0xFFFFFF03	NO_EXPORT_SUBCONFED	[RFC1997]
		0xFFFFFF04	NOPEER	[RFC3765]

	"""

	well_known_list = [
						"GRACEFUL_SHUTDOWN", "ACCEPT_OWN", "ROUTE_FILTER_TRANSLATED_v4", "NO_EXPORT_SUBCONFED", "ROUTE_FILTER_v4", "ROUTE_FILTER_TRANSLATED_v6",
						"ROUTE_FILTER_v6", "LLGR_STALE","NO_LLGR","accept-own-nexthop","BLACKHOLE",
						"NO_ADVERTISE", "NO_EXPORT", "NOPEER"
						]
	for comm in well_known_list:
		myixia.stop_protocol(wait=40)

		myixia.topologies[0].change_bgp_routes_attributes(known_community=comm,address_family="v4")
		myixia.topologies[1].change_bgp_routes_attributes(known_community=comm,address_family="v4")
		myixia.topologies[2].change_bgp_routes_attributes(known_community=comm,address_family="v4")
		myixia.topologies[3].change_bgp_routes_attributes(cknown_community=comm,address_family="v4")

		myixia.topologies[0].change_bgp_routes_attributes_v6(known_community=comm,address_family="v6")
		myixia.topologies[1].change_bgp_routes_attributes_v6(known_community=comm,address_family="v6")
		myixia.topologies[2].change_bgp_routes_attributes_v6(known_community=comm,address_family="v6")
		myixia.topologies[3].change_bgp_routes_attributes_v6(known_community=comm,address_family="v6")
		 
		myixia.start_protocol(wait=60)
		
		sw6_switch.fsw_show_cmd("get router info6 bgp network 2001:106:1:1::a/128")

	cisco_config = """
	route-map known-community permit 10
  		match ipv6 address prefix-list loop2
  		set community 1001:100 local-AS additive
	"""

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
			switch.route_map.routemap_clean_up()
			switch.access_list.acl_basic_config()
			switch.route_map.routemap_basic_config()
		 
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

if testcase == 6190 or test_all or IPV6:
	testcase = 6190
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "IPv6 BGP router reflector"
	tag = "IPv6 router reflector,client_to_client"
	print_test_subject(testcase,description)

	ixia_ipv6_as_list = [101,102,103,104,105,106]
	ipv4_networks = ["10.10.1.1","10.10.2.1","10.10.3.1","10.10.4.1","10.10.5.1","10.10.6.1"]
	ipv6_networks = ["2001:101:1:1::1","2001:102:1:1::1","2001:103:1:1::1","2001:104:1:1::1","2001:105:1:1::1","2001:106:1:1::1"]

	fsw_switches =switches[1:]
	network = BGP_networks(fsw_switches)

	#Infra configuration

	if clear_bgp:
		test_clean_config(switches =fsw_switches)
	if test_config:
		test_config_igp_ipv6_fabric(switches =fsw_switches)
	# network.biuld_ibgp_mesh_topo_sys_intf_v6()
	# network.biuld_ibgp_mesh_topo_sys_intf_one()
	network.build_router_reflector_topo_v6()
	console_timer(20,msg=f"Test case {testcase}: After configuring fully IPv6 router reflector in the BGP network, wait....")
	network.show_summary_v6()

	# FSW configuration
	for sw,ixia_port_info, ixia_as in zip(fsw_switches,portList_v4_v6,ixia_ipv6_as_list):
		if sw.router_bgp.config_ebgp_ixia_v6(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v6 peers ==============")
			exit()
		if sw.router_bgp.config_ebgp_ixia_v4(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v4 peers ==============")
			exit()
	 

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

	for i in range(0,5):
		for j in range(i+1,6):
			myixia.create_traffic_v6(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i}_to_t{j}_v6",tracking_name=f"Tracking_{i}_{j}_v6",rate=1)
			myixia.create_traffic_v6(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j}_to_t{i}_v6",tracking_name=f"Tracking_{j}_{i}_v6",rate=1)
			myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i}_to_t{j}_v4",tracking_name=f"Tracking_{i}_{j}_v4",rate=1)
			myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j}_to_t{i}_v4",tracking_name=f"Tracking_{j}_{i}_v4",rate=1)

	myixia.start_traffic()
	myixia.collect_stats()
	myixia.check_traffic()

if testcase == 6191 or test_all or IPV6:
	testcase = 6191
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "IPv6 BGP route server reflector"
	tag = "IPv6 route server reflector,route server client"
	print_test_subject(testcase,description)

	ixia_ipv6_as_list = [101,102,103,104,105,106]
	ipv4_networks = ["10.10.1.1","10.10.2.1","10.10.3.1","10.10.4.1","10.10.5.1","10.10.6.1"]
	ipv6_networks = ["2001:101:1:1::1","2001:102:1:1::1","2001:103:1:1::1","2001:104:1:1::1","2001:105:1:1::1","2001:106:1:1::1"]

	fsw_switches =switches[1:]
	network = BGP_networks(fsw_switches)
	#Infra configuration

	if clear_bgp:
		test_clean_config(switches =fsw_switches)
	if test_config:
		test_config_igp_ipv6_fabric(switches =fsw_switches)
	# network.biuld_ibgp_mesh_topo_sys_intf_v6()
	# network.biuld_ibgp_mesh_topo_sys_intf_one()
	network.build_route_server_topo_v6()
	console_timer(20,msg=f"Test case {testcase}: After configuring IPv6 route server in the BGP network, wait....")
	network.show_summary_v6()

	# FSW configuration

	for sw,ixia_port_info, ixia_as in zip(fsw_switches,portList_v4_v6,ixia_ipv6_as_list):
		if sw.router_bgp.config_ebgp_ixia_v6(sw_as = None,ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v6 peers ==============")
			exit()
		if sw.router_bgp.config_ebgp_ixia_v4(sw_as = None,ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v4 peers ==============")
			exit()


	for sw,ixia_port_info, ixia_as in zip(fsw_switches,portList_v4_v6,ixia_ipv6_as_list):
		if sw.router_bgp.config_ebgp_ixia_v6(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v6 peers ==============")
			exit()
		if sw.router_bgp.config_ebgp_ixia_v4(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v4 peers ==============")
			exit()
	 

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

	for i in range(0,5):
		for j in range(i+1,6):
			myixia.create_traffic_v6(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i}_to_t{j}_v6",tracking_name=f"Tracking_{i}_{j}_v6",rate=1)
			myixia.create_traffic_v6(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j}_to_t{i}_v6",tracking_name=f"Tracking_{j}_{i}_v6",rate=1)
			myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i}_to_t{j}_v4",tracking_name=f"Tracking_{i}_{j}_v4",rate=1)
			myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j}_to_t{i}_v4",tracking_name=f"Tracking_{j}_{i}_v4",rate=1)

	myixia.start_traffic()
	myixia.collect_stats()
	myixia.check_traffic()

if testcase == 6192 or test_all or IPV6:
	testcase = 6192
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "IPv4 BGP route server reflector"
	tag = "IPv4 route server reflector,route server client"
	print_test_subject(testcase,description)

	ixia_ipv6_as_list = [101,102,103,104,105,106]
	ipv4_networks = ["10.10.1.1","10.10.2.1","10.10.3.1","10.10.4.1","10.10.5.1","10.10.6.1"]
	ipv6_networks = ["2001:101:1:1::1","2001:102:1:1::1","2001:103:1:1::1","2001:104:1:1::1","2001:105:1:1::1","2001:106:1:1::1"]

	fsw_switches =switches[1:]
	network = BGP_networks(fsw_switches)
	#Infra configuration

	if clear_bgp:
		test_clean_config(switches =fsw_switches)
	if test_config:
		test_config_igp_ipv6_fabric(switches =fsw_switches)
	# network.biuld_ibgp_mesh_topo_sys_intf_v6()
	# network.biuld_ibgp_mesh_topo_sys_intf_one()
	network.build_route_server_topo()
	console_timer(20,msg=f"Test case {testcase}: After configuring fully IPv6 router reflector in the BGP network, wait....")
	network.show_summary_v6()

	# FSW configuration
	for sw,ixia_port_info, ixia_as in zip(fsw_switches,portList_v4_v6,ixia_ipv6_as_list):
		if sw.router_bgp.config_ebgp_ixia_v6(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v6 peers ==============")
			exit()
		if sw.router_bgp.config_ebgp_ixia_v4(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v4 peers ==============")
			exit()
	 

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

	for i in range(0,5):
		for j in range(i+1,6):
			myixia.create_traffic_v6(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i}_to_t{j}_v6",tracking_name=f"Tracking_{i}_{j}_v6",rate=1)
			myixia.create_traffic_v6(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j}_to_t{i}_v6",tracking_name=f"Tracking_{j}_{i}_v6",rate=1)
			myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i}_to_t{j}_v4",tracking_name=f"Tracking_{i}_{j}_v4",rate=1)
			myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j}_to_t{i}_v4",tracking_name=f"Tracking_{j}_{i}_v4",rate=1)

	myixia.start_traffic()
	myixia.collect_stats()
	myixia.check_traffic()


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


if testcase == 6200 or test_all or IPV6:
	testcase = 6200
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "IPv6 BGP basic confederation"
	tags = "IPv6 BGP basic confederation"
	print_test_subject(testcase,description)


	ixia_ipv6_as_list = [101,102,103,104,105,106]
	ipv4_networks = ["10.10.1.1","10.20.1.1","10.30.1.1","10.40.1.1","10.50.1.1","10.60.1.1"]
	ipv6_networks = ["2001:101:1:1::1","2001:102:1:1::1","2001:103:1:1::1","2001:104:1:1::1","2001:105:1:1::211","2001:106:1:1::1"]

	fsw_switches =switches[1:]
	network = BGP_networks(fsw_switches)

	#Infra configuration

	if test_config:
		test_clean_config(switches =fsw_switches)
	test_config_igp_ipv6_fabric(switches =fsw_switches)
	# network.biuld_ibgp_mesh_topo_sys_intf_v6()
	# network.biuld_ibgp_mesh_topo_sys_intf_one()
	network.build_confed_topo_1_v6()
	console_timer(20,msg=f"Test case {testcase}: After configuring fully mesh iBGP across all IPv6 system interfaces, wait....")
	network.show_summary_v6()

	
	# FSW configuration
	for sw,ixia_port_info, ixia_as in zip(fsw_switches,portList_v4_v6,ixia_ipv6_as_list):
		if sw.router_bgp.config_ebgp_ixia_v6(sw_as = None,ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v6 peers ==============")
			exit()
		if sw.router_bgp.config_ebgp_ixia_v4(sw_as = None,ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v4 peers ==============")
			exit()

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
		topo.add_bgp_v6(dut_ip=fsw_switches[i].vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=1000)
		i += 1

	myixia.start_protocol(wait=40)


	myixia.create_traffic(src_topo=myixia.topologies[0].topology, dst_topo=myixia.topologies[1].topology,traffic_name="t1_to_t2",tracking_name="Tracking_1")
	myixia.create_traffic(src_topo=myixia.topologies[1].topology, dst_topo=myixia.topologies[0].topology,traffic_name="t2_to_t1",tracking_name="Tracking_2")

	myixia.create_traffic(src_topo=myixia.topologies[2].topology, dst_topo=myixia.topologies[3].topology,traffic_name="t2_to_t3",tracking_name="Tracking_3")
	myixia.create_traffic(src_topo=myixia.topologies[3].topology, dst_topo=myixia.topologies[2].topology,traffic_name="t3_to_t2",tracking_name="Tracking_4")

	myixia.create_traffic(src_topo=myixia.topologies[4].topology, dst_topo=myixia.topologies[5].topology,traffic_name="t4_to_t5",tracking_name="Tracking_5")
	myixia.create_traffic(src_topo=myixia.topologies[5].topology, dst_topo=myixia.topologies[4].topology,traffic_name="t5_to_t4",tracking_name="Tracking_6")


	myixia.create_traffic_v6(src_topo=myixia.topologies[0].topology, dst_topo=myixia.topologies[1].topology,traffic_name="t1_to_t2_v6",tracking_name="Tracking_1_v6")
	myixia.create_traffic_v6(src_topo=myixia.topologies[1].topology, dst_topo=myixia.topologies[0].topology,traffic_name="t2_to_t1_v6",tracking_name="Tracking_2_v6")

	myixia.create_traffic_v6(src_topo=myixia.topologies[2].topology, dst_topo=myixia.topologies[3].topology,traffic_name="t2_to_t3_v6",tracking_name="Tracking_3_v6")
	myixia.create_traffic_v6(src_topo=myixia.topologies[3].topology, dst_topo=myixia.topologies[2].topology,traffic_name="t3_to_t2_v6",tracking_name="Tracking_4_v6")

	myixia.create_traffic_v6(src_topo=myixia.topologies[4].topology, dst_topo=myixia.topologies[5].topology,traffic_name="t4_to_t5_v6",tracking_name="Tracking_5_v6")
	myixia.create_traffic_v6(src_topo=myixia.topologies[5].topology, dst_topo=myixia.topologies[4].topology,traffic_name="t5_to_t4_v6",tracking_name="Tracking_6_v6")


	myixia.start_traffic()
	myixia.collect_stats()
	myixia.check_traffic()

if testcase == 6201 or test_all or IPV6:
	testcase = 6201
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "IPv6 BGP confederation as_path and med "
	tags = "IPv6 BGP basic confederation as_path and med"
	print_test_subject(testcase,description)


	ixia_ipv6_as_list = [101,101,101,101,101,101]
	ipv4_networks = ["10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1"]
	ipv6_networks = ["2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1"]

	fsw_switches =switches[1:]
	dut_switch = fsw_switches[0]  # At the switch_1, create 6 ebgp sessions with IXIA

	fsw_switches =switches[1:]
	network = BGP_networks(fsw_switches)

	#Infra configuration

	if clear_bgp:
		test_clean_config(switches =fsw_switches)
	if test_config:
		test_config_igp_ipv6_fabric(switches =fsw_switches)
	network.build_confed_topo_1_v6()
	console_timer(20,msg=f"Test case {testcase}: After configuring fully mesh iBGP across all IPv6 system interfaces, wait....")
	network.show_summary_v6()

	
	# FSW configuration

	# for ixia_port_info, ixia_as in zip(portList_v4_v6,ixia_ipv6_as_list):
	# 	if dut_switch.router_bgp.config_ebgp_ixia_v6(sw_as = None,ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
	# 		tprint("================= !!!!! Not able to configure IXIA BGP v6 peers ==============")
	# 		exit()
	# 	if dut_switch.router_bgp.config_ebgp_ixia_v4(sw_as = None,ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
	# 		tprint("================= !!!!! Not able to configure IXIA BGP v4 peers ==============")
	# 		exit()


	for sw,ixia_port_info, ixia_as in zip(fsw_switches,portList_v4_v6,ixia_ipv6_as_list):
		if sw.router_bgp.config_ebgp_ixia_v6(sw_as = None,ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v6 peers ==============")
			exit()
		if sw.router_bgp.config_ebgp_ixia_v4(sw_as = None,ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v4 peers ==============")
			exit()

	myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)

	for topo in myixia.topologies:
		topo.add_ipv6()
		topo.add_ipv4()
	 
	for topo,net6,net4,as_num in zip(myixia.topologies,ipv6_networks,ipv4_networks,ixia_ipv6_as_list):
		topo.bgpv6_network = net6
		topo.bgpv4_network = net4
		topo.bgp_as = as_num

	# i = 0
	# for topo in myixia.topologies:
	# 	topo.add_bgp(dut_ip=dut_switch.vlan1_ip,bgp_type='external',num=1)
	# 	topo.add_bgp_v6(dut_ip=dut_switch.vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=1)
	# 	i += 1
		 
	i = 0
	for topo in myixia.topologies:
		topo.add_bgp(dut_ip=fsw_switches[i].vlan1_ip,bgp_type='external',num=2)
		topo.add_bgp_v6(dut_ip=fsw_switches[i].vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=2)
		i += 1


	for i in range(6):
		myixia.topologies[i].change_bgp_routes_attributes(med=4111+i, num_path=6-i,as_base=45010,address_family="v4")
		myixia.topologies[i].change_bgp_routes_attributes_v6(med=6111+i,num_path=6-i,as_base=35010,address_family="v6")

	myixia.start_protocol(wait=40)


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



if testcase == 6210 or test_all or IPV6:
	testcase = 6210
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "ipv6 Always compare med - different eBGP AS "
	tag = "ipv6 always compare med "
	print_test_subject(testcase,description)

 
	ixia_ipv6_as_list = [101,102,103,104,105,106]
	ipv4_networks = ["10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1"]
	ipv6_networks = ["2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1"]

	fsw_switches =switches[1:]
	dut_switch = fsw_switches[0]  # At the switch_1, create 6 ebgp sessions with IXIA
	network = BGP_networks(switches)

	#Infra configuration

	if test_config:
		test_clean_config(switches =fsw_switches)
	test_config_igp_ipv6_fabric(switches =fsw_switches)
	network.biuld_ibgp_mesh_topo_sys_intf_v6()
	network.biuld_ibgp_mesh_topo_sys_intf_one()
	console_timer(20,msg=f"Test case {testcase}: After configuring fully mesh iBGP across all IPv6 system interfaces, wait....")
	network.show_summary_v6()
	
	# FSW configuration
	for ixia_port_info, ixia_as in zip(portList_v4_v6,ixia_ipv6_as_list):
		if dut_switch.router_bgp.config_ebgp_ixia_v6(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v6 peers ==============")
			exit()
		if dut_switch.router_bgp.config_ebgp_ixia_v4(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
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
		topo.add_bgp(dut_ip=dut_switch.vlan1_ip,bgp_type='external',num=1)
		topo.add_bgp_v6(dut_ip=dut_switch.vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=1)
		i += 1

	for i in range(6):
		myixia.topologies[i].change_bgp_routes_attributes(med=4111+i, address_family="v4")
		myixia.topologies[i].change_bgp_routes_attributes_v6(med=6111+i,address_family="v6")

	myixia.start_protocol(wait=40)
	 
	check_bgp_test_result(testcase,description,switches)

if testcase == 6211 or test_all or IPV6:
	testcase = 6211
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "ipv6 deterministic med - same eBGP AS "
	tag = "ipv6 deterministic med "
	print_test_subject(testcase,description)

 
	ixia_ipv6_as_list = [101,101,101,101,101,101]
	ipv4_networks = ["10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1"]
	ipv6_networks = ["2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1"]

	fsw_switches =switches[1:]
	dut_switch = fsw_switches[0]  # At the switch_1, create 6 ebgp sessions with IXIA
	network = BGP_networks(switches)

	#Infra configuration
	if test_config:
		test_clean_config(switches =fsw_switches)
	test_config_igp_ipv6_fabric(switches =fsw_switches)
	network.biuld_ibgp_mesh_topo_sys_intf_v6()
	#network.biuld_ibgp_mesh_topo_sys_intf()
	console_timer(20,msg=f"Test case {testcase}: After configuring fully mesh iBGP across all IPv6 system interfaces, wait....")
	network.show_summary_v6()
	
	# FSW configuration
	for ixia_port_info, ixia_as in zip(portList_v4_v6,ixia_ipv6_as_list):
		if dut_switch.router_bgp.config_ebgp_ixia_v6(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v6 peers ==============")
			exit()
		if dut_switch.router_bgp.config_ebgp_ixia_v4(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
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
		topo.add_bgp(dut_ip=dut_switch.vlan1_ip,bgp_type='external',num=1)
		topo.add_bgp_v6(dut_ip=dut_switch.vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=1)
		i += 1

	for i in range(6):
		myixia.topologies[i].change_bgp_routes_attributes(med=4111+i, address_family="v4")
		myixia.topologies[i].change_bgp_routes_attributes_v6(med=6111+i,address_family="v6")

	myixia.start_protocol(wait=40)
	 
	check_bgp_test_result(testcase,description,switches)


if testcase == 6212 or test_all or IPV6:
	testcase = 6212
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "ipv6 orf "
	tag = "orf"
	print_test_subject(testcase,description)

 
	ixia_ipv6_as_list = [101,102,103,104,105,106]
	ipv4_networks = ["10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1"]
	ipv6_networks = ["2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1"]

	fsw_switches =switches[1:]
	dut_switch = fsw_switches[0]  # At the switch_1, create 6 ebgp sessions with IXIA
	network = BGP_networks(switches)

	#Infra configuration

	if test_config:
		test_clean_config(switches =fsw_switches)
	test_config_igp_ipv6_fabric(switches =fsw_switches)
	network.biuld_ibgp_mesh_topo_sys_intf_v6()
	network.biuld_ibgp_mesh_topo_sys_intf_one()
	console_timer(20,msg=f"Test case {testcase}: After configuring fully mesh iBGP across all IPv6 system interfaces, wait....")
	network.show_summary_v6()
	
	for sw in fsw_switches:
		sw.prefix_list.prefix_orf_v4()
		sw.prefix_list.prefix_orf_v6()

	orf_cmds = f"""
	set capability-orf both
    set capability-orf6 both
    set prefix-list-in orf-list
    set prefix-list-in6 orf-list-v6
	"""

	for sw in fsw_switches:
		sw.router_bgp.config_all_neighbor_commands(orf_cmds)

	# FSW configuration
	# for ixia_port_info, ixia_as in zip(portList_v4_v6,ixia_ipv6_as_list):
	# 	if dut_switch.router_bgp.config_ebgp_ixia_v6(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
	# 		tprint("================= !!!!! Not able to configure IXIA BGP v6 peers ==============")
	# 		exit()
	# 	if dut_switch.router_bgp.config_ebgp_ixia_v4(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
	# 		tprint("================= !!!!! Not able to configure IXIA BGP v4 peers ==============")
	# 		exit()

	# IXIA configuration
	# myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)

	# for topo in myixia.topologies:
	# 	topo.add_ipv6()
	# 	topo.add_ipv4()
	 
	# for topo,net6,net4,as_num in zip(myixia.topologies,ipv6_networks,ipv4_networks,ixia_ipv6_as_list):
	# 	topo.bgpv6_network = net6
	# 	topo.bgpv4_network = net4
	# 	topo.bgp_as = as_num
		 
	# i = 0
	# for topo in myixia.topologies:
	# 	topo.add_bgp(dut_ip=fsw_switches[i].vlan1_ip,bgp_type='external',num=1)
	# 	topo.add_bgp_v6(dut_ip=fsw_switches[i].vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=1)
	# 	i += 1

	# for i in range(6):
	# 	myixia.topologies[i].change_bgp_routes_attributes(med=4111+i, address_family="v4")
	# 	myixia.topologies[i].change_bgp_routes_attributes_v6(med=6111+i,address_family="v6")

	# myixia.start_protocol(wait=40)
	 
	check_bgp_test_result(testcase,description,switches)

if testcase == 6213 or test_all or IPV6:
	testcase = 6213
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "ipv6 deterministic and always compare med - different eBGP AS and iBGP"
	tag = "ipv6 deterministic and always compare med, always and deterministic med "
	print_test_subject(testcase,description)

 
	ixia_ipv6_as_list = [101,101,102,102,65000,65000]
	ipv4_networks = ["10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1"]
	ipv6_networks = ["2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1"]

	fsw_switches =switches[1:]
	dut_switch = fsw_switches[0]  # At the switch_1, create 6 ebgp sessions with IXIA
	network = BGP_networks(switches)

	#Infra configuration
	if test_config:
		test_clean_config(switches =fsw_switches)
		test_config_igp_ipv6_fabric(switches =fsw_switches)
		network.biuld_ibgp_mesh_topo_sys_intf_v6()
	#network.biuld_ibgp_mesh_topo_sys_intf()
	console_timer(20,msg=f"Test case {testcase}: After configuring fully mesh iBGP across all IPv6 system interfaces, wait....")
	network.show_summary_v6()
	
	# FSW configuration
	for ixia_port_info, ixia_as in zip(portList_v4_v6,ixia_ipv6_as_list):
		if dut_switch.router_bgp.config_ebgp_ixia_v6(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v6 peers ==============")
			exit()
		if dut_switch.router_bgp.config_ebgp_ixia_v4(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
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
		if i < 4:
			topo.add_bgp(dut_ip=dut_switch.vlan1_ip,bgp_type='external',num=1)
			topo.add_bgp_v6(dut_ip=dut_switch.vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=1)
		else:
			topo.add_bgp(dut_ip=dut_switch.vlan1_ip,bgp_type='internal',num=1)
			topo.add_bgp_v6(dut_ip=dut_switch.vlan1_ipv6.split("/")[0],bgp_type='internal',prefix_num=1)
		i += 1

	for i in range(6):
		myixia.topologies[i].change_bgp_routes_attributes(med=4116-i, address_family="v4")
		myixia.topologies[i].change_bgp_routes_attributes_v6(med=6116-i,address_family="v6")

	myixia.start_protocol(wait=40)


if testcase == 6214 or test_all or IPV6:
	testcase = 6214
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "Cisco ipv6 deterministic and always compare med - different eBGP AS and iBGP"
	tag = "Cisco ipv6 deterministic and always compare med "
	print_test_subject(testcase,description)

 
	ixia_ipv6_as_list = [101,101,102,102,65000,65000]
	ipv4_networks = ["10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1"]
	ipv6_networks = ["2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1"]

	fsw_switches =switches[1:]
	dut_switch = switches[0]  # Dut switch is cisco
	network = BGP_networks(switches)

	fsw_switches =switches[1:]
	if clear_bgp:
		test_clean_config(switches =fsw_switches)

	#Infra configuration
	if test_config:
		test_clean_config(switches =fsw_switches)
		test_config_igp_ipv6_fabric(switches =fsw_switches)
		network.biuld_ibgp_mesh_topo_sys_intf_v6()
	#network.biuld_ibgp_mesh_topo_sys_intf()
	console_timer(20,msg=f"Test case {testcase}: After configuring fully mesh iBGP across all IPv6 system interfaces, wait....")
	network.show_summary_v6()
	
	# FSW configuration
	for ixia_port_info, ixia_as in zip(portList_v4_v6,ixia_ipv6_as_list):
		if dut_switch.router_bgp.cisco_bgp_ixia_v6(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v6 peers ==============")
			exit()
		if dut_switch.router_bgp.cisco_bgp_ixia_v4(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
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
		if i < 4:
			topo.add_bgp(dut_ip=dut_switch.vlan1_ip,bgp_type='external',num=1)
			topo.add_bgp_v6(dut_ip=dut_switch.vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=1)
		else:
			topo.add_bgp(dut_ip=dut_switch.vlan1_ip,bgp_type='internal',num=1)
			topo.add_bgp_v6(dut_ip=dut_switch.vlan1_ipv6.split("/")[0],bgp_type='internal',prefix_num=1)
		i += 1

	for i in range(6):
		myixia.topologies[i].change_bgp_routes_attributes(med=4116-i, address_family="v4")
		myixia.topologies[i].change_bgp_routes_attributes_v6(med=6116-i,address_family="v6")

	myixia.start_protocol(wait=40)
	 
	#check_bgp_test_result(testcase,description,switches)

if testcase == 6215 or test_all or IPV6:
	testcase = 6215
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "ignore as_path "
	tag = "ignore as_path"
	print_test_subject(testcase,description)

 
	ixia_ipv6_as_list = [101,101,101,101,101,101]
	ipv4_networks = ["10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1"]
	ipv6_networks = ["2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1"]

	fsw_switches =switches[1:]
	dut_switch = fsw_switches[0]  # At the switch_1, create 6 ebgp sessions with IXIA
	network = BGP_networks(switches)

	#Infra configuration
	if clear_bgp:
		test_clean_config(switches =fsw_switches)
	if test_config:
		test_config_igp_ipv6_fabric(switches =fsw_switches)
	network.biuld_ibgp_mesh_topo_sys_intf_v6()
	#network.biuld_ibgp_mesh_topo_sys_intf()
	console_timer(20,msg=f"Test case {testcase}: After configuring fully mesh iBGP across all IPv6 system interfaces, wait....")
	network.show_summary_v6()
	
	# FSW configuration
	for ixia_port_info, ixia_as in zip(portList_v4_v6,ixia_ipv6_as_list):
		if dut_switch.router_bgp.config_ebgp_ixia_v6(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v6 peers ==============")
			exit()
		if dut_switch.router_bgp.config_ebgp_ixia_v4(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
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
		topo.add_bgp(dut_ip=dut_switch.vlan1_ip,bgp_type='external',num=1)
		topo.add_bgp_v6(dut_ip=dut_switch.vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=1)
		i += 1

	for i in range(6):
		myixia.topologies[i].change_bgp_routes_attributes(med=4111+i, num_path=6-i,as_base=45010,address_family="v4")
		myixia.topologies[i].change_bgp_routes_attributes_v6(med=6111+i,num_path=6-i,as_base=65010,address_family="v6")

	myixia.start_protocol(wait=40)
	 
	check_bgp_test_result(testcase,description,switches)

if testcase == 6216 or test_all or IPV6:
	testcase = 6216
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "ipv6 best path missing med worst - different eBGP AS "
	tag = "ipv6 best path missing med worst "
	print_test_subject(testcase,description)

 
	ixia_ipv6_as_list = [101,102,103,104,105,106]
	ipv4_networks = ["10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1"]
	ipv6_networks = ["2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1"]

	fsw_switches =switches[1:]
	dut_switch = fsw_switches[0]  # At the switch_1, create 6 ebgp sessions with IXIA
	network = BGP_networks(switches)

	#Infra configuration

	if clear_bgp:
		test_clean_config(switches =fsw_switches)
	test_config_igp_ipv6_fabric(switches =fsw_switches)
	network.biuld_ibgp_mesh_topo_sys_intf_v6()
	network.biuld_ibgp_mesh_topo_sys_intf_one()
	console_timer(20,msg=f"Test case {testcase}: After configuring fully mesh iBGP across all IPv6 system interfaces, wait....")
	network.show_summary_v6()
	
	# FSW configuration
	for ixia_port_info, ixia_as in zip(portList_v4_v6,ixia_ipv6_as_list):
		if dut_switch.router_bgp.config_ebgp_ixia_v6(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v6 peers ==============")
			exit()
		if dut_switch.router_bgp.config_ebgp_ixia_v4(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
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
		topo.add_bgp(dut_ip=dut_switch.vlan1_ip,bgp_type='external',num=1)
		topo.add_bgp_v6(dut_ip=dut_switch.vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=1)
		i += 1

	for i in range(3):
		myixia.topologies[i].change_bgp_routes_attributes_v6(med=4111+i, address_family="v4")
		myixia.topologies[i].change_bgp_routes_attributes_v6(med=6111+i,address_family="v6")

	myixia.start_protocol(wait=40)
	 
	check_bgp_test_result(testcase,description,switches)


if testcase == 6217 or test_all or IPV6:
	testcase = 6217
	sys.stdout = Logger(f"Log/bgp_test_{testcase}.log")
	description = "multipath-relax "
	tag = "multipath-relax"
	print_test_subject(testcase,description)

 
	ixia_ipv6_as_list = [101,102,102,104,105,106]
	ipv4_networks = ["10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1","10.10.1.1"]
	ipv6_networks = ["2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1","2001:101:1:1::1"]

	fsw_switches =switches[1:]
	dut_switch = fsw_switches[0]  # At the switch_1, create 6 ebgp sessions with IXIA
	network = BGP_networks(switches)

	#Infra configuration
	if clear_bgp:
		test_clean_config(switches =fsw_switches)
	if test_config:
		test_config_igp_ipv6_fabric(switches =fsw_switches)
	network.biuld_ibgp_mesh_topo_sys_intf_v6()
	#network.biuld_ibgp_mesh_topo_sys_intf()
	console_timer(20,msg=f"Test case {testcase}: After configuring fully mesh iBGP across all IPv6 system interfaces, wait....")
	network.show_summary_v6()
	
	# FSW configuration
	for ixia_port_info, ixia_as in zip(portList_v4_v6,ixia_ipv6_as_list):
		if dut_switch.router_bgp.config_ebgp_ixia_v6(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
			tprint("================= !!!!! Not able to configure IXIA BGP v6 peers ==============")
			exit()
		if dut_switch.router_bgp.config_ebgp_ixia_v4(ixia_port=ixia_port_info,ixia_as=ixia_as) == False:
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
		topo.add_bgp(dut_ip=dut_switch.vlan1_ip,bgp_type='external',num=1)
		topo.add_bgp_v6(dut_ip=dut_switch.vlan1_ipv6.split("/")[0],bgp_type='external',prefix_num=1)
		i += 1

	for i in range(6):
		myixia.topologies[i].change_bgp_routes_attributes(med=4111, num_path=6-i,as_base=45010,address_family="v4")
		myixia.topologies[i].change_bgp_routes_attributes_v6(med=6111,num_path=6-i,as_base=65010,address_family="v6")

	myixia.start_protocol(wait=40)
	 
	check_bgp_test_result(testcase,description,switches)

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
