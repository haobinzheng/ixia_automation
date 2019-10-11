
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
from common_lib import *
from common_codes import *
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
parser.add_argument("-sw", "--upgrade", help="FSW software upgrade via FGT,image build number at settings.py ", action="store_true")


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
	if args.upgrade:
		upgrade_fgt = True
		tprint("Upgrade FSW software via via Fortigate")
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
		tprint("** Test Case To Run:{}".format(testcase))
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
if dev_mode == False:
	tprint("============================== Pre-test setup and configuration ===================")
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
	
	if test_setup.lower() == "fg-548d":
		################################
		# FGT 548D Test setup
		################################
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

		dut1_com = "10.105.50.3"
		dut1_location = "Rack23-29"
		dut1_port = 2057
		dut1_name = "dut1-548d"
		dut1_cfg = "dut1_548d.cfg"
		dut1_cfg_basic = "dut1_548d_basic.cfg"

		dut2_com = "10.105.50.3"
		dut2_port = 2056
		dut2_location = "Rack23-28"
		dut2_name = "dut2-548d"
		dut2_cfg = "dut2_548d.cfg"
		dut2_cfg_basic = "dut2_548d_basic.cfg"

		dut3_com = "10.105.50.1"
		dut3_port = 2075
		dut3_name = "dut3-548d"
		dut3_location = "Rack20-23"
		dut3_cfg = "dut3_548d.cfg"
		dut3_cfg_basic = "dut3_548d_basic.cfg"

		dut4_com = "10.105.50.1"
		dut4_port = 2078
		dut4_location = "Rack20-22"
		dut4_name = "dut4-548d"
		dut4_cfg = "dut4_548d.cfg"	
		dut4_cfg_basic = "dut4_548d_basic.cfg"	

		dut1_telnet = "10.105.50.59"
		dut2_telnet = "10.105.50.60"
		dut3_telnet = "10.105.50.62"
		dut4_telnet = "10.105.50.63"
		ip_list = [dut1_telnet,dut2_telnet,dut3_telnet,dut4_telnet]

		if config_host_sw == True:
			sw1=get_switch_telnet_connection("10.105.50.3",2097)
			sw2=get_switch_telnet_connection("10.105.50.2",2092)
			tprint("======================== Configure SW1 and SW2 for FG-548D setup ===============")
			switch_shut_port(sw1,"port25")
			switch_shut_port(sw1,"port26")
			switch_shut_port(sw1,"port13")
			switch_shut_port(sw1,"port14")
			switch_unshut_port(sw1,"port7")

			switch_shut_port(sw2,"port23")
			switch_shut_port(sw2,"port24")
			switch_unshut_port(sw2,"port13")
			switch_unshut_port(sw2,"port14")
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
		dut1_cfg_basic = "dut1_548d_basic.cfg"

		dut2_com = "10.105.50.3"
		dut2_port = 2056
		dut2_location = "Rack23-28"
		dut2_name = "dut2-548d"
		dut2_cfg = "dut2_548d.cfg"
		dut2_cfg_basic = "dut2_548d_basic.cfg"

		dut3_com = "10.105.50.1"
		dut3_port = 2075
		dut3_name = "dut3-548d"
		dut3_location = "Rack20-23"
		dut3_cfg = "dut3_548d.cfg"
		dut3_cfg_basic = "dut3_548d_basic.cfg"

		dut4_com = "10.105.50.1"
		dut4_port = 2078
		dut4_location = "Rack20-22"
		dut4_name = "dut4-548d"
		dut4_cfg = "dut4_548d.cfg"	
		dut4_cfg_basic = "dut4_548d_basic.cfg"	

		dut1_telnet = "10.105.50.59"
		dut2_telnet = "10.105.50.60"
		dut3_telnet = "10.105.50.62"
		dut4_telnet = "10.105.50.63"
		ip_list = [dut1_telnet,dut2_telnet,dut3_telnet,dut4_telnet]
		 

		if config_host_sw == True:
			testbed_description = """
			1) SW1: shut port25
					shut port26
					shut port7
					unsht port 13
					unshut port14
			2)SW2: 	shut port23
					shut port24
					unshut port13
					unshut port14
			""" 
			print(testbed_description)
			sw1=get_switch_telnet_connection("10.105.50.3",2097)
			sw2=get_switch_telnet_connection("10.105.50.2",2092)
			tprint("======================== Configure SW1 and SW2 for 548D setup ===============")
			switch_shut_port(sw1,"port25")
			switch_shut_port(sw1,"port26")
			switch_unshut_port(sw1,"port13")
			switch_unshut_port(sw1,"port14")
			switch_shut_port(sw1,"port7")

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

		dut1_telnet = "10.105.50.64"
		dut2_telnet = "10.105.50.65"
		dut3_telnet = "10.105.50.66"
		dut4_telnet = "10.105.50.67"
		ip_list = [dut1_telnet,dut2_telnet,dut3_telnet,dut4_telnet]

		if config_host_sw == True:
			testbed_description = """
			1) SW1: unshut port25
					unshut port26
					shut port7
					sht port 13
					shut port14
			2)SW2: 	unshut port23
					unshut port24
					shut port13
					shut port14
			""" 
			print(testbed_description)
			tprint("======================== Configure SW1 and SW2 for 448D setup ===============")
			sw1=get_switch_telnet_connection("10.105.50.3",2097)
			sw2=get_switch_telnet_connection("10.105.50.2",2092)
			switch_unshut_port(sw1,"port25")
			switch_unshut_port(sw1,"port26")
			switch_shut_port(sw1,"port13")
			switch_shut_port(sw1,"port14")
			switch_shut_port(sw1,"port7")

			switch_unshut_port(sw2,"port23")
			switch_unshut_port(sw2,"port24")
			switch_shut_port(sw2,"port13")
			switch_shut_port(sw2,"port14")
			

	dut1_dir = {}
	dut2_dir = {}
	dut3_dir = {} 
	dut4_dir = {}
	dut1 = get_switch_telnet_connection_new(dut1_com,dut1_port)
	dut1_dir['name'] = dut1_name
	dut1_dir['location'] = dut1_location
	dut1_dir['telnet'] = dut1
	dut1_dir['cfg'] = dut1_cfg
	dut1_dir['cfg_b'] = dut1_cfg_basic

	dut2 = get_switch_telnet_connection_new(dut2_com,dut2_port)
	dut2_dir['name'] = dut2_name
	dut2_dir['location'] = dut2_location
	dut2_dir['telnet'] = dut2
	dut2_dir['cfg'] = dut2_cfg
	dut2_dir['cfg_b'] = dut2_cfg_basic

	dut3 = get_switch_telnet_connection_new(dut3_com,dut3_port)
	dut3_dir['name'] = dut3_name
	dut3_dir['location'] = dut3_location
	dut3_dir['telnet'] = dut3
	dut3_dir['cfg'] = dut3_cfg
	dut3_dir['cfg_b'] = dut3_cfg_basic

	dut4 = get_switch_telnet_connection_new(dut4_com,dut4_port)
	dut4_dir['name'] = dut4_name
	dut4_dir['location'] = dut4_location
	dut4_dir['telnet'] = dut4
	dut4_dir['cfg'] = dut4_cfg
	dut4_dir['cfg_b'] = dut4_cfg_basic

	dut_list = [dut1,dut2,dut3,dut4]
	dut_dir_list = [dut1_dir,dut2_dir,dut3_dir,dut4_dir]

	# Develop new codes starts from here
	# stop_threads = False
	# dut_cpu_memory(dut_dir_list,lambda: stop_threads)


	if no_fortigate:
		tprint("--------------------------Shutting down connetions to Fortigate nodes -------")
		fgt1_dir = {}
		fgt2_dir = {}
		fgt_dir_list = []
		fgt1 = get_switch_telnet_connection_new(fgt1_com,fgt1_port,password='admin')
		fgt1_dir['name'] = fgt1_name
		fgt1_dir['location'] = fgt1_location
		fgt1_dir['telnet'] = fgt1
		fgt1_dir['cfg'] = fgt1_cfg
		fgt_dir_list.append(fgt1_dir)

		fgt2 = get_switch_telnet_connection_new(fgt2_com,fgt2_port,password='admin')
		fgt2_dir['name'] = fgt2_name
		fgt2_dir['location'] = fgt2_location
		fgt2_dir['telnet'] = fgt2
		fgt2_dir['cfg'] = fgt2_cfg
		fgt_dir_list.append(fgt2_dir)

		if test_setup == "448D":
			pass
		if test_setup == "548D":
			fgt_shut_port(fgt1,"port13")		
			fgt_shut_port(fgt1,"port14")
			fgt_shut_port(fgt2,"port13")		
			fgt_shut_port(fgt2,"port14")
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

	# if factory == True:
	# 	print("------------------- Factory resetting FSWs ------------------")
	# 	for d in dut_dir_list:
	# 		dut = d['telnet']
	# 		dut_name = d['name']
	# 		location = d['location']
	# 		tprint("Factory reseting {} at {}......".format(dut_name,location))
	# 		switch_interactive_exec(dut,"execute factoryresetfull","Do you want to continue? (y/n)")

	# 	sleep(200)
	# 	for dut in dut_list:
	# 		relogin_if_needed(dut)

	for dut_dir in dut_dir_list:
		dut = dut_dir['telnet']
		dut_name = dut_dir['name']
		image = find_dut_image(dut)
		tprint(f"============================ {dut_name} software image = {image}")

	# if setup == True or Setup_only == True:
	# 	for d in dut_dir_list:
	# 		configure_switch_file(d['telnet'],d['cfg'])
 
	# 	tprint("++++Wait for 30 seconds before verifying configuration")
	# 	time.sleep(30)
	# 	print("*****************Reboot all DUTs to have a fresh start, it takes probably 3 minutes")
	# 	i=0
	# 	for dut in dut_list:
	# 		i+=1
	# 		switch_exec_reboot(dut,device="dut{}".format(i))

	# 	time.sleep(180)
	# for dut in dut_list:
	# 	relogin_if_needed(dut)
 
	# tprint("===================================== Pre-test Configuration Verification ============================")
	# for dut in dut_list:
	# 	print("########################################################################################")
	# 	switch_show_cmd(dut,"get system status")
	# 	switch_show_cmd(dut,"show switch trunk")
	# 	switch_show_cmd(dut,"diagnose switch mclag peer-consistency-check")
	# 	switch_show_cmd(dut,"get switch lldp neighbors-summary")
# chassis = "10.105.241.234"
# ixnetwork = "10.105.19.19:8004"
# #tcl_server=${Ixia Tcl Srv} | device=${Ixia Chasis} | ixnetwork_tcl_server=${Ixia IxNetwork Srv} | port_list=${Ixia ports} | reset=1 |
# portsList = ['1/1','1/2','1/3','1/4']

chassis_ip = '10.105.241.234'
tcl_server = '10.105.241.234'
ixnetwork_tcl_server = "10.105.19.19:8004"

if testcase == 4:
	if setup:
		fgt_548d_setup()
		multiplier = 100
		ixia_dhcp_codes(multiplier)
	port_file = f"Log/{test_setup}_port_monitor.log" 
	log_file = f"Log/{test_setup}_log_monitor.log"
	with open(port_file,'a+') as f:
		f.write("====================================================================================\n")
		f.write(" Monitoring port status for quarantine mac bounce\n ")
		f.write("====================================================================================\n")

	with open(log_file,'a+') as f:
		f.write("=====================================================================================\n")
		f.write("Monitoring syslog entries for quarantine mac bounce\n ")
		f.write("=====================================================================================\n")
	fgt1_dir = {}
	fgt2_dir = {}
	fgt_dir_list = []
	
	fgt1 = get_switch_telnet_connection(fgt1_com,fgt1_port,password='admin')
	fgt1_dir['name'] = fgt1_name
	fgt1_dir['location'] = fgt1_location
	fgt1_dir['telnet'] = fgt1
	fgt1_dir['cfg'] = fgt1_cfg
	fgt_dir_list.append(fgt1_dir)

	config_local_access = """
	config switch-controller security-policy local-access
    	edit "default"
        	set mgmt-allowaccess https ping ssh telnet
    	next
	end
	"""
	config_block_cmds(fgt1_dir, config_local_access)
	config_switch_log = """
	config switch-controller switch-log
    	set severity debug
	end
	"""
	config_block_cmds(fgt1_dir, config_switch_log)

	config_bounce = """
	config switch-controller global
   		set vlan-all-mode all
    	set bounce-quarantined-link enable
	end
	"""
	config_block_cmds(fgt1_dir, config_bounce)

	config_quarantine = """
	config user quarantine
		config targets
		    edit "m1"
		        config macs
		            edit 00:13:01:00:00:63
		            next
		            edit 00:13:01:00:00:17
		            next
		            edit 00:13:01:00:00:24
		            next
		            edit 00:13:01:00:00:04
		            next
		            edit 00:12:01:00:00:43
		            next
		            edit 00:12:01:00:00:04
		            next
		            edit 00:12:01:00:00:5a
		            next
		        end
		    next
		end
	end
	"""

	delete_quarantine = """
	config user quarantine
		config targets
		    delete "m1"
		end
	end
	"""
	event_config  = multiprocessing.Event()
	event_done  = multiprocessing.Event()
	dut_name_list = ["dut3"]
	intf_name_list = ["port39","port13"]
	ip_list = [dut3_telnet]
	dut_background_cmd_list = []
	proc_list1 = []
	proc_list2 = []
	proc_list1 = [multiprocessing.Process(name=f'monitor_interface_{dut_name}',\
		target = dut_process_interface,\
		args = (ip,dut_name,port_file,intf_name_list,event_config,event_done),\
		kwargs= {"cmds":dut_background_cmd_list}) \
		for (ip,dut_name) in zip(ip_list,dut_name_list) \
		]
	for proc in proc_list1:	
		proc.start()

	proc_list2 = [multiprocessing.Process(name=f'monitor_log_{dut_name}',\
		target = dut_process_log,\
		args = (ip,dut_name,log_file,intf_name_list,event_config,event_done),\
		kwargs= {"cmds":dut_background_cmd_list}) \
		for (ip,dut_name) in zip(ip_list,dut_name_list) \
		]
	for proc in proc_list2:	
		proc.start()

	sleep(5)
	while True:
		event_config.set()
		sleep(1)
		config_block_cmds(fgt1_dir, config_quarantine)
		sleep(10)
		event_config.clear()
		keyin = input("::::::::After config quarantine, check DUT3 log and port status. When done, press any key\n")
		event_config.set()
		sleep(2)
		config_block_cmds(fgt1_dir, delete_quarantine)
		sleep(10)
		event_config.clear()
		keyin = input("::::::::After delete quarantine, check DUT3 log and port status. When done, press any key\n")

if testcase == 3:
	test_steps = """
1. Reboot FGTs
2. Factory reset all switches
3. Configure physical ports to ldp-profile default-auto-isl
4. Configure mclag-isl and auto-isl-port-group
5. Configure switch trunk port via FGT
6. Upgrade switches 
7. Configure log-mac-event
8. Close consoles for FGT and FSW
9. Start test loops
for each mac_size:
	-setup ixia and ensure initial traffic flow is ok 
	-setup log files for process
	-start cpu monitoring process 
	-start background delete-mac process
	-Main process loop: 
		-measure traffic loss 
	"""
	print(test_steps)
	icl_ports = ['port47','port48']
	core_ports = ["port1","port2","port3","port4"]
	tprint('------------------------------ login Fortigate devices -----------------------')
	fgt1_dir = {}
	fgt2_dir = {}
	fgt_dir_list = []
	
	fgt1 = get_switch_telnet_connection_new(fgt1_com,fgt1_port,password='admin')
	fgt1_dir['name'] = fgt1_name
	fgt1_dir['location'] = fgt1_location
	fgt1_dir['telnet'] = fgt1
	fgt1_dir['cfg'] = fgt1_cfg
	fgt_dir_list.append(fgt1_dir)

	fgt2 = get_switch_telnet_connection_new(fgt2_com,fgt2_port,password='admin')
	fgt2_dir['name'] = fgt2_name
	fgt2_dir['location'] = fgt2_location
	fgt2_dir['telnet'] = fgt2
	fgt2_dir['cfg'] = fgt2_cfg
	fgt_dir_list.append(fgt2_dir)

	config_local_access = """
	config switch-controller security-policy local-access
    	edit "default"
        	set mgmt-allowaccess https ping ssh telnet
    	next
	end
	"""
	config_block_cmds(fgt1_dir, config_local_access)
	
	fgt_list = []
	for fgt_dir in fgt_dir_list:
		fgt = fgt_dir['telnet']
		name = fgt_dir['name']
		fgt_list.append(fgt)
		if settings.FGT_REBOOT: 
			switch_exec_reboot(fgt,device=name)

	#This is a workaround for a problem: when the both fgt are booted together, normal agg interface didn't go up and need toggling

	if settings.FGT_REBOOT:
		console_timer(600,msg="After rebooting FGTs, wait for 600 sec")
		relogin_dut_all(fgt_list)
		config_system_interface(fgt1,"Agg-424D-1","set status down")
		sleep(2)
		config_system_interface(fgt1,"Agg-424D-1","set status up")
		sleep(2)

	if upgrade_fgt and test_setup.lower() == "fg-548d" and not setup:
		tprint(f" ===================== upgrading managed FSW to build {settings.build_548d} ===============")
		fgt_upgrade_548d(fgt1,fgt1_dir)
		console_timer(200,msg = "After software upgrade, wait for 200 seconds") 

	if setup == True:
		if settings.FACTORY or factory:
			tprint("=============== resetting all switches to factory default ===========")
			for dut in dut_list:
				switch_interactive_exec(dut,"execute factoryresetfull","Do you want to continue? (y/n)")
			print("after reset sleep 5 min")
			console_timer(300,msg="Wait for 5 min after reset factory default")
			print("after sleep, relogin, should change password ")
		

			tprint('-------------------- re-login Fortigate devices after factory rest-----------------------')
			dut1 = get_switch_telnet_connection_new(dut1_com,dut1_port)
			dut2 = get_switch_telnet_connection_new(dut2_com,dut2_port)
			dut3 = get_switch_telnet_connection_new(dut3_com,dut3_port)
			dut4 = get_switch_telnet_connection_new(dut4_com,dut4_port)
			dut_list = [dut1,dut2,dut3,dut4]
			dut1_dir['telnet'] = dut1 
			dut2_dir['telnet'] = dut2
			dut3_dir['telnet'] = dut3
			dut4_dir['telnet'] = dut4

		###################################################################
		#   Start a background login thread to periodically activate prompt
		###################################################################
		stop_threads = False
		lock = threading.Lock()
		threads_list = []
		# thread2 = Thread(target = period_login,args = (dut_list,lock,lambda: stop_threads))
		# thread2.start()
		# threads_list.append(thread2)

		 
		tprint(" -------------- After factory reset, find out FSW images ------------------------")
		for dut_dir in dut_dir_list:
			dut = dut_dir['telnet']
			dut_name = dut_dir['name']
			image = find_dut_image(dut)
			tprint(f"============================ {dut_name} software image = {image}================")

		tprint("------------ configure port lldp profile to auto-isl --------------------")
		for dut_dir in dut_dir_list:
			switch_configure_cmd_name(dut_dir,"config switch physical-port")
			for port in core_ports:
				switch_configure_cmd_name(dut_dir,f"edit {port}")
				switch_configure_cmd_name(dut_dir,"set lldp-profile default-auto-isl")
				switch_configure_cmd_name(dut_dir,"next")
			switch_configure_cmd_name(dut_dir,"end")	
		tprint("------------  After configuring lldp profile to auto-isl, wait for 180 seconds  --------------------")
		console_timer(180)
		relogin_dut_all(dut_list)

		for dut_dir in dut_dir_list:
			image = find_dut_image(dut)
			tprint(f"============================ {dut_name} software image = {image}================")
		
		for dut_dir in dut_dir_list:
			dut_name = dut_dir['name']
			# switch_show_cmd_name(dut_dir,"get system status")
			dut = dut_dir['telnet']
			relogin_if_needed(dut)
			ICL_CONFIG = False
			sw_delete_log(dut)
			while not ICL_CONFIG: 
				sleep(10)
				tprint("Configuring MCLAG-ICL, if icl trunk is not found, maybe auto-discovery is not done yet")
				output = dut_switch_trunk(dut) 
				if "Error" in output:
					ErrorNotify(output)
					continue
				else:
					trunk_dict_list = output
					for trunk in trunk_dict_list:
						if set(trunk['mem']) == set(icl_ports):
							Info(f"ICL ports = {trunk['mem']}")
							switch_configure_cmd_name(dut_dir,"config switch trunk")
							switch_configure_cmd_name(dut_dir,f"edit {trunk['name']}")
							switch_configure_cmd_name(dut_dir,'set mclag-icl enable')
							switch_configure_cmd_name(dut_dir,'end')	
							break
					sleep(2)
					switch_show_cmd(dut,"show switch trunk")
					if check_icl_config(dut):
						Info(f"mclag-icl is configured correctly at {dut_name}")
						ICL_CONFIG = True
					else:
						ErrorNotify(f"mclag-icl is not configured properly at {dut_name} and need to re-do")
						ICL_CONFIG = False
						sw_display_log(dut)

			if 'dut1' in dut_name or 'dut2' in dut_name:
				switch_configure_cmd_name(dut_dir,"config switch auto-isl-port-group")
				switch_configure_cmd_name(dut_dir,"edit core1")
				switch_configure_cmd_name(dut_dir,f"set members {core_ports[0]} {core_ports[1]} {core_ports[2]} {core_ports[3]}")
				switch_configure_cmd_name(dut_dir,'end')
			#console_timer(10,msg="wait for 10 sec after mclag related config is done on one FSW")
		console_timer(300,msg="after configure auto-isl-port-group wait for 300s, check out the mclag-icl is NOT missing")
		relogin_dut_all(dut_list)

		tprint("After configuring MCLAG and wait for 5 min, check the configuration ")
		for dut_dir in dut_dir_list:
			dut_name = dut_dir['name']
			switch_show_cmd_name(dut_dir,"show switch trunk")
			switch_show_cmd_name(dut_dir,"show switch auto-isl-port-group")
		#relogin_dut_all(dut_list)
		
 
		tprint("------------  start configuring fortigate  --------------------")
		trunk_config = """
		config switch-controller managed-switch
   			edit S548DF4K16000653
				config ports
					delete trunk1
   					edit trunk1
				        set type trunk
				        set mode lacp-active
				        set mclag enable
				        set members port13
   					next
				end
			next
			edit S548DN4K17000133
				config ports
					delete trunk1
					edit trunk1
						set type trunk
						set mode lacp-active
						set mclag enable
						set members port13
				next
			end
		end
		"""
		config_block_cmds(fgt1_dir, trunk_config)
		console_timer(300,msg="after configuring managed FSW and FGT, wait for 300 sec")

		if upgrade_fgt and test_setup.lower() == "fg-548d":
			debug("Start to upgrade fsw")
			fgt_upgrade_548d(fgt1,fgt1_dir)
			console_timer(400,msg ="After software upgrade, wait for 400 seconds") 
		else: 
			tprint(" Not FSW software upgrade. After finished configuring, reboot all FSWs")
			for dut in dut_list:
				switch_exec_reboot(dut)
			console_timer(300,msg ="After reboot,wait for 300 seconds")
		relogin_dut_all(dut_list)

		for fgt_dir in fgt_dir_list:
			fgt = fgt_dir['telnet']
			fgt.close() 

		for d in dut_dir_list:
			configure_switch_file(d['telnet'],d['cfg_b'])

		tprint("------------  end of configuring fortigate and FSW  --------------------")
		pre_test_verification(dut_list)

	# Enable or disable log-mac-event on all trunk interface


	if log_mac_event:
		cmd = "set log-mac-event enable"
	else:
		cmd = "set log-mac-event disable"
	for dut_dir in dut_dir_list:
		dut_name = dut_dir['name']
		dut = dut_dir['telnet']
		trunk_dict_list = dut_switch_trunk(dut)
		
		if 'dut3' in dut_name or 'dut4' in dut_name:
			config_switch_port_cmd(dut,'port39',cmd)
		for trunk in trunk_dict_list:
			trunk_name = trunk['name']
			config_switch_port_cmd(dut,trunk_name,cmd)

	
	tprint("Test Case #{}: Start executing test case and generating activites".format(testcase))
	if log_mac_event:
		log_mac_flag = "LogMac"
	else:
		log_mac_flag = "NoLogMac"
	cpu_log = "Log/"+test_setup+ '_'+ log_mac_flag+'_'+'cpu.log'
	monitor_file = "Log/"+test_setup+ '_'+log_mac_flag+'_'+'monitor.txt'

	system_verification_log(dut_list,cpu_log)
	# top_threads = True
	# threads_exit(stop_threads,threads_list)
	for dut in dut_list:
		dut.close()

	init_tracking_loop(loop_count)
	for mac_table in mac_list:
		"""
		loop_position = 
		"End"
		"Penultimate"
		"Start"
		"""
		loop_position = tracking_loop(loop_count) 
		portsList_v4 = ['1/1','1/2','1/7','1/8']
		debug("Setup IXIA with ports running as dhcp client mode")
		ports = ixia_connect_ports(chassis_ip,portsList_v4,ixnetwork_tcl_server,tcl_server)
		topo_list = []
		multiplier = mac_table
		dhcp_handle_list = []
		counter = 1
		for port in ports:
			(topo_handle,device_group_handle) = ixia_port_topology(port,multiplier,topo_name="Topology "+str(counter))
			topo_list.append(topo_handle)
			dhcp_status = ixia_emulation_dhcp_group_config(handle=device_group_handle)	
			dhcp_client_handle = dhcp_status['dhcpv4client_handle']
			dhcp_handle_list.append(dhcp_client_handle)
			counter +=1 

		console_timer(10,msg="Wait for 10 sec after dhcp clients are created")
		topo_h1 = topo_list[0]
		topo_h2 = topo_list[1]
		topo_h3 = topo_list[2]
		topo_h4 = topo_list[3]
		ixia_start_protcols_verify(dhcp_handle_list,timeout=150)
		tprint("Creating traffic item I....")
		ixia_create_ipv4_traffic(topo_h1,topo_h2,rate=10)
		tprint("Creating traffic item II....")
		ixia_create_ipv4_traffic(topo_h2,topo_h1,rate=10)
		tprint("Creating traffic item III....")
		ixia_create_ipv4_traffic(topo_h3,topo_h4,rate=10)
		tprint("Creating traffic item IV....")
		ixia_create_ipv4_traffic(topo_h4,topo_h3,rate=10)

		console_timer(20,msg="Wait for 20 sec after traffics are created")
		ixia_start_traffic()
		console_timer(30,msg="Measure traffic for 30 sec and show stats")
		tprint("Collecting statistics, Please take a look at traffic stats to make sure no packet loss..")
	 
		traffic_stats = ixiangpf.traffic_stats(
		    mode = 'flow'
		    )
		if traffic_stats['status'] != '1':
		    tprint('\nError: Failed to get traffic flow stats.\n')
		    tprint(traffic_stats)
		    sys.exit()

		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats_3rd(flow_stat_list)
		if dev_mode == True:
			sys.exit()
		
		with open(cpu_log,'a+') as f:
			f.write("====================================================================================\n")
			f.write("Sample Ctrld cpu utilization during log_mac events, MAC table size = {}\n".format(mac_table * 2))
			f.write("====================================================================================\n")

		with open(monitor_file,'a+') as f:
			f.write("=====================================================================================\n")
			f.write("Sample traffic statistics to monitor pack loss , MAC table size = {}\n".format(mac_table * 2))
			f.write("=====================================================================================\n")
		#uncomment for official run
		
		if settings.THREADING == True:
			stop_threads = False
			threads_list = []
			tprint("====== Main thread TC#1: Creating multithread lock...")
			lock = threading.Lock()
			thread1 = Thread(target = mac_log_stress,args = (topology_handle_dict_list,dut_list,mac_table,lambda: stop_threads))
			thread1.start()
			threads_list.append(thread1)
			sleep(5)
			# thread2 = Thread(target = dut_polling,args = (dut_list,lambda: stop_threads))
			# thread2.start()
			thread3 = Thread(target = dut_cpu_memory,args = (dut_dir_list,lambda: stop_threads,cpu_log))
			thread3.start()
			threads_list.append(thread3)
			sleep(5)
		else:  # mix of multi-threading and multi-processing
			stop_threads = False
			threads_list = []
			tprint("====== Main proc TC#3: Creating multithread lock...")
			lock = threading.Lock()
			tprint("====== Main process for TC#3: Creating multiprocessing event...")
			event  = multiprocessing.Event()
			# thread1 = Thread(target = ixia_topo_swap,args = (topology_handle_dict_list,dut_list,mac_table,\
			# 	lambda: stop_threads,traffic_list))
			# thread1.start()
			# threads_list.append(thread1)
			# thread2 = Thread(target = dut_polling,args = (dut_list,lambda: stop_threads))
			# thread2.start()

			dut_background_cmd = "diagnose switch mac-address delete all"
			dut_background_cmd_list = [dut_background_cmd]

			dut_name_list = ["dut1","dut2","dut3","dut4"]
			proc_name = 'ctrld'
			file = cpu_log
			proc_list1 = []
			proc_list2 = []
			proc_list1 = [multiprocessing.Process(name=f'{proc_name}_cpu_{dut_name}',\
				target = dut_process_cpu,\
				args = (ip,dut_name,file, proc_name,event),\
				kwargs= {"cmds":dut_background_cmd_list}) \
				for (ip,dut_name) in zip(ip_list,dut_name_list) \
				]
			for proc in proc_list1:	
				proc.start()
			
			proc_list2 = [multiprocessing.Process(name=f'background_{dut_name}',target = dut_background_proc, \
				args = (ip,dut_name,dut_background_cmd_list,event)) for (ip,dut_name) in zip(ip_list,dut_name_list) ]
			for proc in proc_list2:	
				proc.start()
			try:
				while True:
					for _ in range(10):
						ixia_clear_traffic_stats()
						traffic_stats = collect_ixia_traffic_stats()
						flow_stat_list = parse_traffic_stats(traffic_stats)
						print_flow_stats_3rd(flow_stat_list)
						print_file("Logging traffic stats #{}".format(counter),monitor_file)
						print_flow_stats_3rd_log(flow_stat_list,monitor_file)
						sleep(10)
					counter += 1
					if counter == settings.TC1_RUNTIME:
						break
			except KeyboardInterrupt:
				print ("=== Main thread:Ctrl-c received! Sending kill to threads...")
				stop_threads = True
				event.set()
				for t in threads_list:
					t.kill_received = True
					t.join()
				for p in proc_list1:
					p.join()
				for p in proc_list2:
					p.join()
				tprint("=== Main thread received Ctrl-C, exiting the main")
				exit()
			#After each iteration is done.
			if settings.THREADING == True: #threading
				stop_threads = True
				for t in threads_list:
					t.join()
			else:  # mix of threading and process
				event.set()
				for t in threads_list:
					t.join()
				for p in proc_list1:
					p.join()
				for p in proc_list2:
					p.join()

			if loop_position != 'Penultimate':
				ixia_diconnect()
	filename = f"Log/{cpu_log}"
	scp_file(file=filename)

#########################################################################################
#    	Test Case #1
#########################################################################################
if testcase == 1:
	description = """
============================================================================================
Purpose: Measure CPU usage for ctrld process when log-mac-event is enabled and disabled. 
Command:	Edit run_test.sh to run this script with -lm (log enabled) and no -lm (log disabled)
			python mclag_v2.py -t 448D -mac 1000-10000-1000 -test 1 -lm      (log-mac enabled)
			python mclag_v2.py -t 448D -mac 1000-10000-1000 -test 1        	(log-mac disabled)
IXIA topology: two pairs for ports(4 ports total) running static IP mode
			pair #1 port_1 <----> port_2: running traffic stream constantly
			pair #2 port_3 <----> port_4: constantaly switching IP and MAC for MAC move events
			Total traffic streams between each pair: 1k - 10K 
			Total MAC addresses learned by switch: 	4k - 40k
FSW topology:  Two-tier MCLAG
===============================================================================================""" 
	#Uncomment for official 
	for dut in dut_list:
		switch_unshut_port(dut,"port1")
		switch_unshut_port(dut,"port2")
		switch_unshut_port(dut,"port3")
		switch_unshut_port(dut,"port4")
	if settings.REBOOT == True:
		for dut in dut_list:
			switch_exec_reboot(dut)
		sleep(200)
		relogin_dut_all(dut_list)
	#Uncomment later for official run
	pre_test_verification(dut_list)
	if log_mac_event:
		tprint(" ========== Configuring log-mac-event on all DUTs ========")
		config_switch_port_cmd(dut1,"mc-north","set log-mac-event enable")
		config_switch_port_cmd(dut2,"mc-north","set log-mac-event enable")
		config_switch_port_cmd(dut3,"mc-south","set log-mac-event enable")
		config_switch_port_cmd(dut3,"port39","set log-mac-event enable")
		config_switch_port_cmd(dut4,"mc-south","set log-mac-event enable")
		config_switch_port_cmd(dut4,"port39","set log-mac-event enable")
	else:
		cmd = "set log-mac-event disable"
		tprint("Diabling log-mac-event.........")
		config_switch_port_cmd(dut1,"mc-north",cmd)
		config_switch_port_cmd(dut2,"mc-north",cmd)
		config_switch_port_cmd(dut3,"mc-south",cmd)
		config_switch_port_cmd(dut3,"port39",cmd)
		config_switch_port_cmd(dut4,"mc-south",cmd)
		config_switch_port_cmd(dut4,"port39",cmd)

	portsList_v4 = ['1/1','1/2','1/7','1/8']
	
	print (description)
	# handle_list = ixia_static_ipv4_setup(chassis_ip,portsList_v4,ixnetwork_tcl_server,tcl_server)
	##### Connect to IXIA chassis and configure ports, topology and protocols
	iterate_counter = 0
	for mac_table in mac_list:
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
		traffic_list = []
		tprint("Creating traffic item I....")
		traffic_status = ixia_create_ipv4_traffic(topology_1_handle,topology_2_handle,rate=50)
		id = traffic_status['stream_id']
		traffic_list.append(id)
		tprint("Creating traffic item II....")
		traffic_status = ixia_create_ipv4_traffic(topology_2_handle,topology_1_handle,rate=50)
		id = traffic_status['stream_id']
		traffic_list.append(id)
		tprint("Creating traffic item III....")
		traffic_status = ixia_create_ipv4_traffic(topology_3_handle,topology_4_handle,rate=50)
		id = traffic_status['stream_id']
		traffic_list.append(id)
		tprint("Creating traffic item IV....")
		traffic_status = ixia_create_ipv4_traffic(topology_4_handle,topology_3_handle,rate=50)
		ixia_start_traffic()
		id = traffic_status['stream_id']
		traffic_list.append(id)
		tprint(f"traffic_list = {traffic_list}")

		time.sleep(15)
	

		tprint("Collect statistics after running traffic for 15 seconds, Please take a look at printed traffic stats to make sure no packet loss..")
	 
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats_3rd(flow_stat_list)

		tprint("Test Case #{}: Start executing test case and generating activites".format(testcase))
		if log_mac_event:
			log_mac_flag = "LogMac"
		else:
			log_mac_flag = "NoLogMac"
		cpu_log = "Log/"+test_setup+ '_'+ log_mac_flag+'_'+'cpu.log'
		monitor_file = "Log/"+test_setup+ '_'+log_mac_flag+'_'+'monitor.txt'
		
		with open(cpu_log,'a+') as f:
			f.write("====================================================================================\n")
			f.write("Sample Ctrld cpu utilization during log_mac events, MAC table size = {}\n".format(mac_table * 2))
			f.write("====================================================================================\n")

		with open(monitor_file,'a+') as f:
			f.write("=====================================================================================\n")
			f.write("Sample traffic statistics to monitor pack loss , MAC table size = {}\n".format(mac_table * 2))
			f.write("=====================================================================================\n")
		#uncomment for official run
		system_verification_log(dut_list,monitor_file)

		
		if settings.THREADING == True:
			stop_threads = False
			threads_list = []
			tprint("====== Main thread TC#1: Creating multithread lock...")
			lock = threading.Lock()
			thread1 = Thread(target = mac_log_stress,args = (topology_handle_dict_list,dut_list,mac_table,lambda: stop_threads))
			thread1.start()
			threads_list.append(thread1)
			sleep(5)
			# thread2 = Thread(target = dut_polling,args = (dut_list,lambda: stop_threads))
			# thread2.start()
			thread3 = Thread(target = dut_cpu_memory,args = (dut_dir_list,lambda: stop_threads,cpu_log))
			thread3.start()
			threads_list.append(thread3)
			sleep(5)
		else:  # mix of multi-threading and multi-processing
			stop_threads = False
			threads_list = []
			tprint("====== Main proc TC#1: Creating multithread lock...")
			lock = threading.Lock()
			tprint("====== Main process for TC#1: Creating multiprocessing event...")
			event  = multiprocessing.Event()
			# thread1 = Thread(target = ixia_topo_swap,args = (topology_handle_dict_list,dut_list,mac_table,\
			# 	lambda: stop_threads,traffic_list))
			# thread1.start()
			# threads_list.append(thread1)
			# thread2 = Thread(target = dut_polling,args = (dut_list,lambda: stop_threads))
			# thread2.start()

			dut_background_cmd = "diagnose switch mac-address delete all"
			dut_background_cmd_list = [dut_background_cmd]

			dut_name_list = ["dut1","dut2","dut3","dut4"]
			proc_name = 'ctrld'
			file = cpu_log
			proc_list1 = []
			proc_list2 = []
			proc_list1 = [multiprocessing.Process(name=f'{proc_name}_cpu_{dut_name}',\
				target = dut_process_cpu,\
				args = (ip,dut_name,file, proc_name,event),\
				kwargs= {"cmds":dut_background_cmd_list}) \
				for (ip,dut_name) in zip(ip_list,dut_name_list) \
				]
			for proc in proc_list1:	
				proc.start()
			
			proc_list2 = [multiprocessing.Process(name=f'background_{dut_name}',target = dut_background_proc, \
				args = (ip,dut_name,dut_background_cmd_list,event)) for (ip,dut_name) in zip(ip_list,dut_name_list) ]
			for proc in proc_list2:	
				proc.start()
		counter = 0
		login_counter = 0
		ip3 = "100.2.0.1"
		ip4 = "100.2.100.1"
		gw3 = "100.2.100.1"
		gw4 = "100.2.0.1"
		mac3 ="00.13.01.00.00.01"
		mac4 = "00.14.01.00.00.01"

		try:
			while True:
				ip3,ip4 = ip4,ip3
				gw3,gw4 = gw4,gw3
				mac3,mac4 = mac4,mac3
				ixia_topo_swap(topology_handle_dict_list, dut_list, mac_table,lambda: stop_threads,traffic_list,\
					ip3,ip4,gw3,gw4,mac3,mac4)
				for _ in range(10):
					ixia_clear_traffic_stats()
					traffic_stats = collect_ixia_traffic_stats()
					flow_stat_list = parse_traffic_stats(traffic_stats)
					print_flow_stats_3rd(flow_stat_list)
					print_file("Logging traffic stats #{}".format(counter),monitor_file)
					print_flow_stats_3rd_log(flow_stat_list,monitor_file)
					sleep(10)
				counter += 1
				login_counter += 1
				if login_counter == 60:
					login_counter = 0
					for dut in dut_list:
						relogin_if_needed(dut)
				if counter == settings.TC1_RUNTIME:
					break
		except KeyboardInterrupt:
			print ("=== Main thread:Ctrl-c received! Sending kill to threads...")
			stop_threads = True
			event.set()
			for t in threads_list:
				t.kill_received = True
				t.join()
			for p in proc_list1:
				p.join()
			for p in proc_list2:
				p.join()
			tprint("=== Main thread received Ctrl-C, exiting the main")
			exit()
		#After each iteration is done.
		if settings.THREADING == True: #threading
			stop_threads = True
			for t in threads_list:
				t.join()
		else:  # mix of threading and process
			stop_threads = True
			event.set()
			for t in threads_list:
				t.join()
			for p in proc_list1:
				p.join()
			for p in proc_list2:
				p.join()
		 
		ixia_diconnect()
		for dut in dut_list:
			relogin_if_needed(dut)

		#uncomment for official run
		#system_verification_log(dut_list,monitor_file)
		

#########################################################################################
#    	Test Case #2: MC-LAG Performance Measurement
#########################################################################################
if testcase == 2:
	description = """============================================================================================
Purpose: Measure packet loss performance for two-tier MCLAG . 
Command:python mclag_v2.py -t 548D -e -test 2 -n 1 (only firber-cut test)
	python mclag_v2.py -t 548D -e -test 2 -b -n 1 (reboot + firber-cut test)
	python mclag_v2.py -t 548D -e -test 2 -b -n 1 -lm (reboot + firber-cut test: log-mc)
	For help: python mclag_v2.py --help
IXIA topology: 1st pair for ports(2 ports total) running static IP mode	
			   2nd pair port for background activities		   
FSW topology:  Two-tier MCLAG
===============================================================================================""" 
	print(description)
	portsList_v4 = ['1/1','1/2','1/7','1/8']
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
		multiplier=2000,
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
		multiplier=2000,
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

	#Uncomment for offical run
	#pre_test_verification(dut_list) #temp
	# stat_dir_list = [{'member': 2, 'B1:H1': '2-member LACP trunk', 'B2:F2': 'image name to be filled', 'B3': 'No.', 'C3': 'Action', 'D3:E3': 'Frame Loss', 'F3': 'Loss Time Sec', 'B4': 'Test 1', 'C4': 'un-plug 1st active link', 'D4': 'host1', 'D5': 'host2', 'C7': 'un-plug 2nd active link', 'D7': 'host1', 'D8': 'host2', 'C10': 're-connect 2nd link', 'D10': 'host1', 'D11': 'host2', 'C13': 're-connect 1st active link', 'D13': 'host1', 'D14': 'host2', 'C16': 'Tier-1 DUT1 Down', 'D16': 'host1', 'D17': 'host2', 'C18': 'Tier-1 DUT2 Down', 'D18': 'host1', 'D19': 'host2', 'C21': 'Tier-1 DUT1 Up', 'D21': 'host1', 'D22': 'host2', 'C23': 'Tier-1 DUT2 Up', 'D23': 'host1', 'D24': 'host2', 'C26': 'Tier-2 DUT3 Down', 'D26': 'host1', 'D27': 'host2', 'C28': 'Tier-2 DUT4 Down', 'D28': 'host1', 'D29': 'host2', 'C31': 'Tier-2 DUT3 Up', 'D31': 'host1', 'D32': 'host2', 'C33': 'Tier-2 DUT4 Up', 'D33': 'host1', 'D34': 'host2', 'test': 1, 'sheetname': 'LACP-2 Test1'}, {'member': 2, 'B1:H1': '2-member LACP trunk', 'B2:F2': 'image name to be filled', 'B3': 'No.', 'C3': 'Action', 'D3:E3': 'Frame Loss', 'F3': 'Loss Time Sec', 'B4': 'Test 2', 'C4': 'un-plug 1st active link', 'D4': 'host1', 'D5': 'host2', 'C7': 'un-plug 2nd active link', 'D7': 'host1', 'D8': 'host2', 'C10': 're-connect 2nd link', 'D10': 'host1', 'D11': 'host2', 'C13': 're-connect 1st active link', 'D13': 'host1', 'D14': 'host2', 'C16': 'Tier-1 DUT1 Down', 'D16': 'host1', 'D17': 'host2', 'C18': 'Tier-1 DUT2 Down', 'D18': 'host1', 'D19': 'host2', 'C21': 'Tier-1 DUT1 Up', 'D21': 'host1', 'D22': 'host2', 'C23': 'Tier-1 DUT2 Up', 'D23': 'host1', 'D24': 'host2', 'C26': 'Tier-2 DUT3 Down', 'D26': 'host1', 'D27': 'host2', 'C28': 'Tier-2 DUT4 Down', 'D28': 'host1', 'D29': 'host2', 'C31': 'Tier-2 DUT3 Up', 'D31': 'host1', 'D32': 'host2', 'C33': 'Tier-2 DUT4 Up', 'D33': 'host1', 'D34': 'host2', 'sheetname': 'LACP-2 Test2', 'test': 2}, {'member': 8, 'B1:H1': '2-member LACP trunk', 'B2:F2': 'image name to be filled', 'B3': 'No.', 'C3': 'Action', 'D3:E3': 'Frame Loss', 'F3': 'Loss Time Sec', 'B4': 'Test 1', 'C4': 'un-plug 1st active link', 'D4': 'host1', 'D5': 'host2', 'C7': 'un-plug 3~4 active link', 'D7': 'host1', 'D8': 'host2', 'C10': 're-connect 3~4 link', 'D10': 'host1', 'D11': 'host2', 'C13': 're-connect 1st active link', 'D13': 'host1', 'D14': 'host2', 'C16': 'Tier-1 DUT1 Down', 'D16': 'host1', 'D17': 'host2', 'C18': 'Tier-1 DUT2 Down', 'D18': 'host1', 'D19': 'host2', 'C21': 'Tier-1 DUT1 Up', 'D21': 'host1', 'D22': 'host2', 'C23': 'Tier-1 DUT2 Up', 'D23': 'host1', 'D24': 'host2', 'C26': 'Tier-2 DUT3 Down', 'D26': 'host1', 'D27': 'host2', 'C28': 'Tier-2 DUT4 Down', 'D28': 'host1', 'D29': 'host2', 'C31': 'Tier-2 DUT3 Up', 'D31': 'host1', 'D32': 'host2', 'C33': 'Tier-2 DUT4 Up', 'D33': 'host1', 'D34': 'host2', 'sheetname': 'LACP-8 Test1', 'test': 1, 'E22': 9, 'F22': '7.344001175040188e-05 seconds', 'E21': 8, 'F21': '6.528001044480167e-05 seconds'}, {'member': 8, 'B1:H1': '2-member LACP trunk', 'B2:F2': 'image name to be filled', 'B3': 'No.', 'C3': 'Action', 'D3:E3': 'Frame Loss', 'F3': 'Loss Time Sec', 'B4': 'Test 2', 'C4': 'un-plug 1st active link', 'D4': 'host1', 'D5': 'host2', 'C7': 'un-plug 3~4 active link', 'D7': 'host1', 'D8': 'host2', 'C10': 're-connect 3~4 link', 'D10': 'host1', 'D11': 'host2', 'C13': 're-connect 1st active link', 'D13': 'host1', 'D14': 'host2', 'C16': 'Tier-1 DUT1 Down', 'D16': 'host1', 'D17': 'host2', 'C18': 'Tier-1 DUT2 Down', 'D18': 'host1', 'D19': 'host2', 'C21': 'Tier-1 DUT1 Up', 'D21': 'host1', 'D22': 'host2', 'C23': 'Tier-1 DUT2 Up', 'D23': 'host1', 'D24': 'host2', 'C26': 'Tier-2 DUT3 Down', 'D26': 'host1', 'D27': 'host2', 'C28': 'Tier-2 DUT4 Down', 'D28': 'host1', 'D29': 'host2', 'C31': 'Tier-2 DUT3 Up', 'D31': 'host1', 'D32': 'host2', 'C33': 'Tier-2 DUT4 Up', 'D33': 'host1', 'D34': 'host2', 'sheetname': 'LACP-8 Test2', 'test': 2, 'E22': 8, 'F22': '6.528001044480167e-05 seconds', 'E21': 8, 'F21': '6.528001044480167e-05 seconds'}]

	# filename = "LACP_Perf.xlsx"
	# dict_2_excel(stat_dir_list,filename)
	# exit()
	stat_dir_list = []   # this the data structure that has the final report
	create_excel_sheets(stat_dir_list,image,mem=2,runtime=Run_time)
	create_excel_sheets(stat_dir_list,image,mem=8,runtime=Run_time)
	stop_threads = False
	lock = threading.Lock()
	threads_list = []
	# thread = Thread(target = background_ixia_activity,args = (topology_handle_dict_list,dut_list,lambda: stop_threads))
	# thread.start()
	thread2 = Thread(target = period_login,args = (dut_list,lambda: stop_threads))
	thread2.start()
	threads_list.append(thread2)

	if log_mac_event:
		tprint("Enabling log-mac-event.........")
		config_switch_port_cmd(dut1,"mc-north","set log-mac-event enable")
		config_switch_port_cmd(dut2,"mc-north","set log-mac-event enable")
		config_switch_port_cmd(dut3,"mc-south","set log-mac-event enable")
		config_switch_port_cmd(dut3,"port39","set log-mac-event enable")
		config_switch_port_cmd(dut4,"mc-south","set log-mac-event enable")
		config_switch_port_cmd(dut4,"port39","set log-mac-event enable")
	else:
		cmd = "set log-mac-event disable"
		tprint("Diabling log-mac-event.........")
		config_switch_port_cmd(dut1,"mc-north",cmd)
		config_switch_port_cmd(dut2,"mc-north",cmd)
		config_switch_port_cmd(dut3,"mc-south",cmd)
		config_switch_port_cmd(dut3,"port39",cmd)
		config_switch_port_cmd(dut4,"mc-south",cmd)
		config_switch_port_cmd(dut4,"port39",cmd)

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

	tprint ("=============================== Start: Fiber Cut Test for 8-member MCLAG ===========================")
	for dut in dut_list:
		relogin_if_needed(dut)

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


	tprint ("=============================== Start: Fiber Cut Test  for 2-member MCLAG ===========================")	
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

	for t in threads_list:
		t.join()


if clean_up or settings.IXIA_CLEANUP:
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
