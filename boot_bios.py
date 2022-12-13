from pprint import pprint
import os
import sys
import time
import re
import argparse
import threading
from threading import Thread
from time import sleep
import ipaddress
import multiprocessing
import random
import yaml
from jinja2 import Environment, PackageLoader
from jinja2 import Template
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
from test_process import *
from datetime import date



if __name__ == "__main__":
	sys.stdout = Logger(f"Log/boot_to_bios.log")
	parser = argparse.ArgumentParser()
	parser.add_argument("-c", "--config", help="Configure switches before starting testing", action="store_true")
	parser.add_argument("-test", "--testcase", type=str, help="Specific which test case you want to run. Example: 1/1-3/1,3,4,7 etc")
	parser.add_argument("-b", "--boot", help="Perform reboot test", action="store_true")
	parser.add_argument("-f", "--factory", help="Run the test after factory resetting all devices", action="store_true")
	parser.add_argument("-v", "--verbose", help="Run the test in verbose mode with amble debugs info", action="store_true")
	parser.add_argument("-s", "--setup_only", help="Setup testbed and IXIA only for manual testing", action="store_true")
	parser.add_argument("-i", "--interactive", help="Enter interactive mode for test parameters", action="store_true")
	parser.add_argument("-ug", "--sa_upgrade", type = str,help="FSW software upgrade in standlone mode. For debug image enter -1. Example: v6-193,v7-5,-1(debug image)")
	parser.add_argument("-r", "--recovery", help="FSW recovery password.Example:python ipv6_acl_testing -r",action="store_true")
	#parser.add_argument("-r", "--recovery",help="FSW recovery password.Example:python ipv6_acl_testing -r FSW_3032E-v7-build0426-FORTINET.out")


	global DEBUG
	testcase_range = False

	
	args = parser.parse_args()

	if args.recovery:
		password_recovery = True
		print_title(f"Recover password and install image")
	else:
		password_recovery = False

	if args.sa_upgrade:
		upgrade_sa = True
		sw_build = args.sa_upgrade
		print_title(f"Upgrade FSW software in standalone: {sw_build}")
	else:
		upgrade_sa = False
	 
	if args.verbose:
		settings.DEBUG = True
		print_title("Running the test in verbose mode")
	else:
		settings.DEBUG = False
		print_title("Running the test in silent mode") 

	if args.config:
		setup = True
		print_title("Configure devices:Yes")
	else:
		setup = False   
		print_title("Configure devices:No")  
		 
	 
	if args.factory:
		factory = True
		print_title("Factory reset: Yes")
	else:
		factory = False
		print_title("Factory reset: No")


	if args.testcase:
		testcase_list = []
		testcase_range = False
		try:
			testcase = int(args.testcase)
		except:
			testcase = (args.testcase)
			if "," in testcase:
				testcase_list = testcase.split(",")
				testcase_list = [int(i) for i in testcase_list]
				print_title(f"Test cases are  {testcase_list} ")
				testcase_range = True
			elif "-" in testcase:
				testcase_list_str = testcase.split("-")
				print(testcase_list_str)
				start=int(testcase_list_str[0])
				end = int(testcase_list_str[1])
				for i in range(start,end+1):
					testcase_list.append(i)
				print_title(f"Test cases are  {testcase_list} ")
				testcase_range = True
		test_all = False
		print_title("Test Case To Run: #{}".format(testcase))
	else:
		test_all = True
		testcase = 0
		print_title("All Test Case To Be Run:{}".format(test_all))
 
 
	if args.boot:
		Reboot = True
		print_title("Reboot:Yes")
	else:
		Reboot = False
		print_title("Reboot:No")

	if args.setup_only:
		Setup_only = True
		print_title("Set up Only:Yes")
	else:
		Setup_only = False
		print_title("Set up Only:No")
	file = 'tbinfo_boot_bios.xml'
	tb = parse_tbinfo_untangle(file)
	testtopo_file = 'topo_boot_bios.xml'
	parse_testtopo_untangle(testtopo_file,tb)
	tb.show_tbinfo()

	######## skipping it for ixia trouble shooting
	switches = []
	for d in tb.devices:
		#switch = FortiSwitch_XML_SSH(d,topo_db=tb,ssh_login=True)
		switch = FortiSwitch_XML(d,topo_db=tb,login_ssh=True,login_console=False)
		switches.append(switch)
	for c in tb.connections:
		c.update_devices_obj(switches)
	####### skipping it for ixia trouble shooting 
	# for c in tb.connections:
	# 	c.shut_unused_ports()
	sw = switches[0]
 		
	apiServerIp = tb.ixia.ixnetwork_server_ip
	#ixChassisIpList = ['10.105.241.234']
	ixChassisIpList = [tb.ixia.chassis_ip]
 	 
	##################################### Pre-Test setup and configuration #############################
	if password_recovery: 
		i = len(switches)
		keyin = input(f"Please enter the switch number you want to do password discovery[1-{i}]:")
		recovery_switch = switches[int(keyin)-1]
		keyin = input(f"Please enter the image name you want to install, example:FSW_3032E-v7-build0426-FORTINET.out:")
		image_name = keyin
		recovery_switch.recover_password(image_name)
		exit()

	if upgrade_sa:
		for sw in switches:
			v,b = sw_build.split('-')
			result = sw.fsw_upgrade_v2(build=b,version=v)
			if not result:
				tprint(f"############# Upgrade {sw.name} to build #{sw_build} Fails ########### ")
			else:
				tprint(f"############# Upgrade {sw.name} to build #{sw_build} is successful ############")

		console_timer(400,msg="Wait for 400s after started upgrading all switches")
		for sw in switches:
			try:
				sw.switch_relogin()
			except Exception as e:
				debug("something is wrong with rlogin_if_needed at bgp, try again")
				sw.switch_relogin()
			image = find_dut_image(sw.console)
			tprint(f"===================software image = {image} =========================")
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

		# if testcase == 0:
		# 	exit()

	if setup: 
		for sw in switches:
			config = f"""
			config system interface
				edit "vlan1"
				    set ip {gw4_list[0]} 255.255.255.0
				            config ipv6
				                set ip6-address {gw6_list[0]}/64
				                set ip6-allowaccess ping https http ssh telnet
				                set dhcp6-information-request enable
				            end
				        set vlanid 1
				        set interface "internal"
				    next
				end
			config switch vlan
				delete 20 
				delete 1
			end
			config switch vlan
			    edit 20
			        set mld-snooping enable
					set igmp-snooping enable
			    next
			    edit 1
			        set igmp-snooping enable
			        set mld-snooping enable
			    next
			end
			conf switch igmp-snooping globals
				set aging-time 300
			end
			"""
			config_cmds_lines(sw.console,config)
		# if testcase == 0:
		# 	exit()

	if Reboot:
		for sw in switches:
			dut = sw.console
			dut_name = sw.name
			sw.switch_reboot()

		console_timer(400,msg="Wait for 400s after started rebooting all switches")
		for sw in switches:
			dut = sw.console
			dut_name = sw.name
			sw.switch_relogin()
			image = find_dut_image(dut)
			tprint(f"============================ {dut_name} software image = {image} ============")

		# if testcase == 0:
		# 	exit()
	boot_time = 100
	power_time = 80
	for i in range(1000):
		for sw in switches:
			sw.ssh_login_reliable()
			result = sw.fsw_upgrade_ssh(build=470,version=6)
			if not result:
				tprint(f"############# Upgrade {sw.hostname} to v6 build #470 Fails ########### ")
			else:
				tprint(f"############# Upgrade {sw.hostname} to v6 build #470 is successful ############")
			console_timer(boot_time,msg=f"Wait for {boot_time} for upgrading the {sw.hostname}")
			sw.ssh_login_reliable()

			sw.ssh_pdu_status()
			sw.ssh_pdu_cycle()
			console_timer(power_time,msg=f'After power cycling the switch, wait for {power_time} seconds')
			sw.ssh_login_reliable()

			result = sw.fsw_upgrade_ssh(build=86,version=7)
			if not result:
				tprint(f"############# Upgrade {sw.hostname} to v7 build #86 Fails ########### ")
			else:
				tprint(f"############# Upgrade {sw.hostname} to v7 build #86 is successful ############")
			console_timer(boot_time,msg=f"Wait for {boot_time} for upgrading the {sw.hostname}")
			sw.ssh_login_reliable() 
			 
			sw.ssh_pdu_status()
			sw.ssh_pdu_cycle()
			console_timer(power_time,msg=f'After power cycling the switch, wait for {power_time} seconds')
			sw.ssh_login_reliable()
		 