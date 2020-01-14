
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
#from clear_console import *
#init()
################################################################################
# Connection to the chassis, IxNetwork Tcl Server                 			   #
################################################################################


sys.stdout = Logger("Log/mclag_perf.log")

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
parser.add_argument("-ug", "--sa_upgrade", type = int,help="FSW software upgrade in standlone mode,image build number at settings.py, example: 193")




global DEBUG
if len(sys.argv) > 1:
    #parser.print_help()
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
		tprint("** Test Case To Run: #{}".format(testcase))
	else:
		testcase = "all"
		tprint("** Test Case To Run:{}".format(testcase))
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
# print("Testing running in batch mode. comment out later")
# filename = "MCLAG_Perf_"+test_setup+file_appendix+".xlsx"
# touch(filename)
# sleep(5)
# scp_file(file=filename)
# exit()
print(settings.ONBOARD_MSG)
#If in code development mode, skipping loging into switches 
tprint("============================== Pre-test setup and configuration ===================")

testbed_description = """
1) SW1: shut down port13 and port14
2) sw1: enable port 7
3) 424D: enable port 1
4) DUT1: enable port49, port 50
5) DUT2: enable port49, port 50
6) TBD: FGT configuration
7) TBD: DUT1, DUT2, DUT3, DUT4 ICL and other configuration.  
"""
print(testbed_description)

dut1_com = "10.105.241.144"
dut1_location = "Rack7-19"
dut1_port = 2071
dut1_name = "3032E-R7-19"
dut1_cfg = "bgp/3032E-R7-19.cfg"
dut1_cfg_basic = "3032E_R7_19_basic.cfg"
dut1_mgmt_ip = "10.105.240.145"
dut1_mgmt_mask = "255.255.254.0"
dut1_loop0_ip = "1.1.1.1"
dut1_vlan1_ip = "10.1.1.1"
dut1_vlan1_subnet = "10.1.1.0"
dut1_vlan1_mask = "255.255.255.0"
dut1_split_ports = ["port2"]
dut1_40g_ports = ["port9","port19"]

dut2_com = "10.105.241.44"
dut2_location = "Rack7-40"
dut2_port = 2066
dut2_name = "3032D-R7-40"
dut2_cfg = "bgp/3032D-R7-40.cfg"
dut2_cfg_basic = "3032D_R7_40_basic.cfg"
dut2_mgmt_ip = "10.105.241.40"
dut2_mgmt_mask = "255.255.254.0"
dut2_loop0_ip = "2.2.2.2"
dut2_vlan1_ip = "10.1.1.2"
dut2_vlan1_subnet = "10.1.1.0"
dut2_vlan1_mask = "255.255.255.0"
dut2_split_ports = ["port5"]
dut2_40g_ports = ["port9","port13"]

dut3_com = "10.105.240.44"
dut3_location = "Rack4-41"
dut3_port = 2090
dut3_name = "1048E-R4-41"
dut3_cfg = "bgp/1048E-R4-41.cfg"
dut3_cfg_basic = "1048E_R4_41_basic.cfg"
dut3_mgmt_ip = "10.105.240.41"
dut3_mgmt_mask = "255.255.254.0"
dut3_loop0_ip = "3.3.3.3"
dut3_vlan1_ip = "10.1.1.3"
dut3_vlan1_subnet = "10.1.1.0"
dut3_vlan1_mask = "255.255.255.0"
dut3_split_ports = []
dut3_40g_ports = []

dut4_com = "10.105.240.44"
dut4_location = "Rack4-40"
dut4_port = 2007
dut4_name = "1048D-R4-40"
dut4_cfg = "bgp/1048D-R4-40.cfg"
dut4_cfg_basic = "1048D_R4_40_basic.cfg"
dut4_mgmt_ip = "10.105.240.40"
dut4_mgmt_mask = "255.255.254.0"
dut4_loop0_ip = "4.4.4.4"
dut4_vlan1_ip = "10.1.1.4"
dut4_vlan1_subnet = "10.1.1.0"
dut4_vlan1_mask = "255.255.255.0"
dut4_split_ports = []
dut4_40g_ports = []

dut5_com = "10.105.240.144"
dut5_location = "Rack5-38"
dut5_port = 2068
dut5_name = "1024D-R5-38"
dut5_cfg = "bgp/1024D-R5-38.cfg"
dut5_cfg_basic = "1024D_R5_38_basic.cfg"
dut5_mgmt_ip = "10.105.240.138"
dut5_mgmt_mask = "255.255.254.0"
dut5_loop0_ip = "5.5.5.5"
dut5_vlan1_ip = "10.1.1.5"
dut5_vlan1_subnet = "10.1.1.0"
dut5_vlan1_mask = "255.255.255.0"
dut5_split_ports = []
dut5_40g_ports = []


dut1_dir = {}
dut2_dir = {}
dut3_dir = {} 
dut4_dir = {}
dut5_dir = {}

dut1 = get_switch_telnet_connection_new(dut1_com,dut1_port)
dut1_dir['comm'] = dut1_com
dut1_dir['comm_port'] = dut1_port
dut1_dir['name'] = dut1_name
dut1_dir['location'] = dut1_location
dut1_dir['telnet'] = dut1
dut1_dir['cfg'] = dut1_cfg
dut1_dir['mgmt_ip'] = dut1_mgmt_ip
dut1_dir['mgmt_mask']= dut1_mgmt_mask  
dut1_dir['loop0_ip']= dut1_loop0_ip  
dut1_dir['vlan1_ip']= dut1_vlan1_ip  
dut1_dir['vlan1_subnet'] = dut1_vlan1_subnet
dut1_dir['vlan1_mask']= dut1_vlan1_mask  
dut1_dir['split_ports']= dut1_split_ports  
dut1_dir['40g_ports']= dut1_40g_ports  

 
dut2 = get_switch_telnet_connection_new(dut2_com,dut2_port)
dut2_dir['comm'] = dut2_com
dut2_dir['comm_port'] = dut2_port
dut2_dir['name'] = dut2_name
dut2_dir['location'] = dut2_location
dut2_dir['telnet'] = dut2
dut2_dir['cfg'] = dut2_cfg
dut2_dir['mgmt_ip'] = dut2_mgmt_ip
dut2_dir['mgmt_mask']= dut2_mgmt_mask  
dut2_dir['loop0_ip']= dut2_loop0_ip  
dut2_dir['vlan1_ip']= dut2_vlan1_ip  
dut2_dir['vlan1_subnet'] = dut2_vlan1_subnet
dut2_dir['vlan1_mask']= dut2_vlan1_mask  
dut2_dir['split_ports']= dut2_split_ports  
dut2_dir['40g_ports']= dut2_40g_ports  

dut3 = get_switch_telnet_connection_new(dut3_com,dut3_port)
dut3_dir['comm'] = dut3_com
dut3_dir['comm_port'] = dut3_port
dut3_dir['name'] = dut3_name
dut3_dir['location'] = dut3_location
dut3_dir['telnet'] = dut3
dut3_dir['cfg'] = dut3_cfg
dut3_dir['mgmt_ip'] = dut3_mgmt_ip
dut3_dir['mgmt_mask']= dut3_mgmt_mask  
dut3_dir['loop0_ip']= dut3_loop0_ip  
dut3_dir['vlan1_ip']= dut3_vlan1_ip  
dut3_dir['vlan1_subnet'] = dut3_vlan1_subnet
dut3_dir['vlan1_mask']= dut3_vlan1_mask  
dut3_dir['split_ports']= dut3_split_ports  
dut3_dir['40g_ports']= dut3_40g_ports  

dut4 = get_switch_telnet_connection_new(dut4_com,dut4_port)
dut4_dir['comm'] = dut4_com
dut4_dir['comm_port'] = dut4_port
dut4_dir['name'] = dut4_name
dut4_dir['location'] = dut4_location
dut4_dir['telnet'] = dut4
dut4_dir['cfg'] = dut4_cfg
dut4_dir['mgmt_ip'] = dut4_mgmt_ip
dut4_dir['mgmt_mask']= dut4_mgmt_mask  
dut4_dir['loop0_ip']= dut4_loop0_ip  
dut4_dir['vlan1_ip']= dut4_vlan1_ip  
dut4_dir['vlan1_subnet'] = dut4_vlan1_subnet
dut4_dir['vlan1_mask']= dut4_vlan1_mask  
dut4_dir['split_ports']= dut4_split_ports  
dut4_dir['40g_ports']= dut4_40g_ports  

dut5 = get_switch_telnet_connection_new(dut5_com,dut5_port)
dut5_dir['comm'] = dut5_com
dut5_dir['comm_port'] = dut5_port
dut5_dir['name'] = dut5_name
dut5_dir['location'] = dut5_location
dut5_dir['telnet'] = dut5
dut5_dir['cfg'] = dut5_cfg
dut5_dir['mgmt_ip'] = dut5_mgmt_ip
dut5_dir['mgmt_mask']= dut5_mgmt_mask  
dut5_dir['loop0_ip']= dut5_loop0_ip  
dut5_dir['vlan1_ip']= dut5_vlan1_ip  
dut5_dir['vlan1_subnet'] = dut5_vlan1_subnet
dut5_dir['vlan1_mask']= dut5_vlan1_mask  
dut5_dir['split_ports']= dut5_split_ports  
dut5_dir['40g_ports']= dut5_40g_ports  



dut_list = [dut1,dut2,dut3,dut4,dut5]
dut_dir_list = [dut1_dir,dut2_dir,dut3_dir,dut4_dir,dut5_dir]
#dut_dir_list = [dut1_dir]


if factory:
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
exit()
	
	######################################################################
	# DUT dependent Experiment code starts here
	######################################################################
	# for d in dut_dir_list:
	# 	configure_switch_file(d['telnet'],d['cfg'])
	# build_num = 194
	# for d in dut_dir_list:
	# 	dut = d['telnet']
	# 	if sa_upgrade_448d(d['telnet'],d,build = 194):
	# 		tprint(f"Upgrade FSW {d['name']} to build {build_num} is successful")
	# 	else:
	# 		tprint(f"Upgrade FSW {d['name']} to build {build_num} failed")
	# exit()
	######################################################################
	# End of DUT dependent Experiment code starts here
	######################################################################

	 
print("###################")
tprint("Test run is PASSED")
print("###################")


##################################################################################################################################################
##################################################################################################################################################
