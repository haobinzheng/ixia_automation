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
from random import seed                                                 
from random import randint 

# Append paths to python APIs (Linux and Windows)
from apc import *
from utils import *
#import settings 
from test_process import * 
from common_lib import *
from common_codes import *
from cli_functions import *
from device_config import *
from protocols_class import *
from ixia_restpy_lib_v2 import *

import random 
def partition (list_in, n):
    random.shuffle(list_in)
    return [list_in[i::n] for i in range(n)]


if __name__ == "__main__":

	sys.stdout = Logger("Log/fortilink_perf.log")
	
	parser = argparse.ArgumentParser()
	parser.add_argument("-c", "--config", help="Configure switches before starting testing", action="store_true")
	parser.add_argument("-m", "--maintainence", help="Bring switches into standalone for maintainence", action="store_true")
	parser.add_argument("-test", "--testcase", type=str, help="Specific which test case you want to run. Example: 1/1-3/1,3,4,7 etc")
	parser.add_argument("-b", "--boot", help="Perform reboot test", action="store_true")
	parser.add_argument("-p", "--power_cycle", help="Perform power cycle", action="store_true")
	parser.add_argument("-f", "--factory", help="Run the test after factory resetting all devices", action="store_true")
	parser.add_argument("-v", "--verbose", help="Run the test in verbose mode with amble debugs info", action="store_true")
	parser.add_argument("-s", "--setup_only", help="Setup testbed and IXIA only for manual testing", action="store_true")
	parser.add_argument("-i", "--interactive", help="Enter interactive mode for test parameters", action="store_true")
	parser.add_argument("-ug", "--sa_upgrade", type = str,help="FSW software upgrade in standlone mode. For debug image enter -1. Example: v6-193,v7-5,-1(debug image)")
	parser.add_argument("-fg", "--fgt_upgrade", type = str,help="Fortigate software upgrade. For debug image enter -1. Example: v6-193,v7-5,-1(debug image)")


	global DEBUG
	initial_testing = True
	initial_config = False
	
	args = parser.parse_args()

	if args.maintainence:
		maintainence = True
		print_title(f"Factory switches into standalone for maintainence purpose")
	else:
		maintainence = False

	if args.fgt_upgrade:
		upgrade_fgt = True
		sw_build = args.fgt_upgrade
		print_title(f"Upgrade FGT software: {sw_build}")
	else:
		upgrade_fgt = False

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
 
	if args.boot:
		Reboot = True
		print_title("Reboot:Yes")
	else:
		Reboot = False
		print_title("Reboot:No")

	if args.power_cycle:
		Power_cycle = True
		print_title("Power_cycle:Yes")
	else:
		Power_cycle = False
		print_title("Power_cycle:No")

	if args.setup_only:
		Setup_only = True
		print_title("Set up Only:Yes")
	else:
		Setup_only = False
		print_title("Set up Only:No")
	file = 'tbinfo_poe_testing.xml'
	tb = parse_tbinfo_untangle(file)
	testtopo_file = 'topo_poe_testing.xml'
	parse_testtopo_untangle(testtopo_file,tb)
	tb.show_tbinfo()

	switches = []
	fortigates = []
	devices=[]
	for d in tb.devices:
		if d.type == "FSW" and d.active == True:
			switch = FortiSwitch_XML(d,topo_db=tb)
			switches.append(switch)
			devices.append(switch)
		elif d.type == "POE":
			tester = POE_TESTER(d,topo_db=tb)
		else:
			pass

	for c in tb.connections:
		c.update_devices_obj(devices)

	tb.switches = switches
	tb.fortigates = fortigates

	# output_list = tester.get_poe_command(cmd="status")
	# output_dict = tester.parse_status_output(output_list)
	# print(output_dict)
	# output_list = tester.get_poe_command(cmd="measure")
	# output_dict = tester.parse_measure_output(output_list)
	# print(output_dict)
	 
	# for c in tb.connections:
	# 	c.shut_unused_ports()


	########################### FSW discoveries, many things need to disvoer here######
	#discover managed switches. updated some information such ftg console in each switch.
	for sw in switches:
		sw.sw_network_discovery()
		print_attributes(sw)

	##################################### Pre-Test setup and configuration #############################

	if Power_cycle: 
		for sw in switches:
			sw.pdu_status()
			sw.pdu_cycle()
		console_timer(400,msg='After power cycling all switches, wait for 400 seconds')

	if maintainence:
		for fgt in fortigates:
			#print_attributes(fgt)
			fgt.fgt_network_discovery()
			fgt.change_fortilink_ports(state="down")

		for sw in switches:
			sw.switch_factory_reset()

		console_timer(400,msg='After switches are factory reset, wait for 400 seconds')

		for sw in switches:
			sw.sw_relogin()
			dut = sw.console
			dut_name = sw.name
			image = find_dut_image(dut)
			tprint(f"============================ {dut_name} software image = {image} ============")

			sw.config_network_standalone()

		 
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
			dut = sw.console
			dut_name = sw.name
			try:
				sw.relogin()
			except Exception as e:
				debug("something is wrong with rlogin_if_needed at bgp, try again")
				relogin_new(dut,password="Fortinet123!")
			image = find_dut_image(dut)
			tprint(f"============================ {dut_name} software image = {image} ============")
		# if testcase == 0:
		# 	exit()

		console_timer(30,msg="Wait for 30 after upgrading all switches, re-enable fortilink ports at fortigates")

	if Reboot:
		for sw in switches:
			dut = sw.console
			dut_name = sw.name
			switch_exec_reboot(dut,device=dut_name)

		console_timer(400,msg="Wait for 400s after started rebooting all switches")
		for sw in switches:
			dut = sw.console
			dut_name = sw.name
			sw.login_factory_reset()
			image = find_dut_image(dut)
			tprint(f"============================ {dut_name} software image = {image} ============")

		# if testcase == 0:
		# 	exit()
	# for c in tb.connections:
	# 	c.unshut_all_ports()
	# switches = []
	# for d in tb.devices:
	# 	if d.active:
	# 		switch = FortiSwitch_XML(d)
	# 		switches.append(switch)

	sw = switches[0]
	################################# repeated test steps ################################
	def warm_boot_testing():

		port_list = [1,2,3,4,5,6,7,8]
		for j in range(100):
			p_poe,p_poe_fast,normal = partition(port_list,3)

			p_poe_ports = p_poe + p_poe_fast
			all_poe_ports = p_poe + p_poe_fast + normal
			print(f"Perpetual POE Ports = {p_poe}")
			print(f"Perpetual Fast POE Ports = {p_poe_fast}")
			print(f"Normal POE Ports = {normal}")
			##############################################
			# Configure DUT POE ports before test starts
			##############################################
			for p in p_poe:
				config = f"""
				config switch physical-port
	    			edit port{p}
	         		set poe-port-power PERPETUAL
	    			next
				end
				"""
				config_cmds_lines(sw.console,config)	
			for p in p_poe_fast:
				config = f"""
				config switch physical-port
	    			edit port{p}
	         		set poe-port-power PERPETUAL-FAST
	    			next
				end
				"""
				config_cmds_lines(sw.console,config)

			for p in normal:
				config = f"""
				config switch physical-port
	    			edit port{p}
	         		unset poe-port-power
	    			next
				end
				"""
				config_cmds_lines(sw.console,config)

			sleep(5)

			##############################################
			#  Setup POE tester before test starts
			##############################################
			tester.poe_reset()
			sleep(5)
			output_list = tester.get_poe_command(cmd="status")
			output_dict = tester.parse_status_output(output_list)
			print(output_dict)

			result = True
			ppoe_list_tester = []
			regex = r'p([0-9]+)'
			for k,v in output_dict.items():
				if v == "1":
					matched = re.search(regex,k)
					if matched:
						ppoe_list_tester.append(int(matched.group(1)))
			all_poe_ports.sort()
			ppoe_list_tester.sort()
			print(all_poe_ports,ppoe_list_tester)

			print_double_line()
			if all_poe_ports != ppoe_list_tester:
				print("Failed: Before Warm Boot, Switch All POE ports list is NOT Equal to All POE Tester list")
				result = False
				return result
			else:
				print("Before Warm Boot, Switch POE ports list is Equal to POE Tester list, Continue.....")
			print_double_line()

			##############################################
			#  Warm Boot Switch & check POE Tester
			##############################################
			sw.switch_reboot()
			
			print_double_line()
			for i in range(50):
				tester.poe_reset()
				sleep(3)
				output_list = tester.get_poe_command(cmd="status")
				output_dict = tester.parse_status_output(output_list)
				print(output_dict)
				ppoe_list_tester = []
				for k,v in output_dict.items():
					if v == "1":
						matched = re.search(regex,k)
						if matched:
							ppoe_list_tester.append(int(matched.group(1)))
				ppoe_list_tester.sort()
				p_poe_ports.sort()
				print(f"POE Tester ports = {ppoe_list_tester}. Switch perpetual POE ports = {p_poe_ports}, Switch PoE ports = {all_poe_ports}" )

				if ppoe_list_tester != p_poe_ports:
					if ppoe_list_tester == all_poe_ports:
						print("Sucess: Switch has booted up, the POE Tester powered ports is Equal to All Switch POE port")
						break
					else:
						print("Failed: Switch perpetual ports list NOT Equal to POE Tester list, STOP!")
						result = False
						return result
				else:
					print("Switch perpetual ports list Equal to POE Tester list, Continue....")

				sleep(2)
	 
			if result == False:
				print_double_line()
				print("Failed: During switch reboots, POE Perpetual ports are not working")
				print(f"Switch Perpetual ports = {p_poe}")
				print(f"Switch Perpetual Fast ports = {p_poe_fast}")
				print(f"POE Tester ports received power = {ppoe_list_tester}")
				print_double_line()
				return result

			console_timer(30,msg=f"Warm boot testing passed, wait for 30s for a final check ")

			output_list = tester.get_poe_command(cmd="status")
			output_dict = tester.parse_status_output(output_list)
			print(output_dict)

			ppoe_list_tester = []
			regex = r'p([0-9]+)'
			for k,v in output_dict.items():
				if v == "1":
					matched = re.search(regex,k)
					if matched:
						ppoe_list_tester.append(int(matched.group(1)))
			all_poe_ports.sort()
			ppoe_list_tester.sort()
			print(all_poe_ports,ppoe_list_tester)

			print_double_line()
			if all_poe_ports != ppoe_list_tester:
				print("Failed: After Warm Boot, Switch perpetual ports list NOT Equal to All POE Tester list")
				result = False
				return result
			else:
				print("Successul: finished one round of warm boot testing")
			print_double_line()
		

		return result

	warm_boot_testing()	
	exit()
	for i in range(1,2):
		test_log = Logger(f"Log/perf_result_fsw{i}.log")
		################################# Disable Slit-brin-detect Perf Testing ########################## 
		for sw in switches:
			if sw.tier == None:
				continue
			config = f"""
			config switch global
			unset mclag-split-brain-detect
			end
			"""
			config_cmds_lines(sw.console,config)
		console_timer(300,msg=f"After disabling split-brain-detect, wait for 300s ")

		test_log.write(f"===========================================================================================\n")
		test_log.write(f"					 Disable split-brian-detect.  			\n")
		test_log.write(f"===========================================================================================\n")
		power_cycle_testing()
		upgrade_testing()
		reboot_testing()
		icl_testing()

	 
		####################################### Enable Slit-brin-detect/No Shut ports Perf Testing ###########################
		index = 0
		for sw in switches:
			if sw.tier == None:
				continue
			appendex = index%2
			config = f"""
			config switch global
			set  mclag-split-brain-detect enable
			set mclag-split-brain-priority {int(sw.tier)*10 + appendex}
			end
			"""
			config_cmds_lines(sw.console,config)
			index += 1
		console_timer(300,msg=f"After enabling split-brain-detect, wait for 300s ")
		test_log.write(f"============================================================================================================\n")
		test_log.write(f"				Enable split-brian-detect/Disable shut ports.  			\n")
		test_log.write(f"=============================================================================================================\n")
		console_timer(300,msg=f"After enabling split-brain without shut-down ports wait for 300s to start testing")
		power_cycle_testing()
		upgrade_testing()
		reboot_testing()
		icl_testing()

		###################################### Enable Slit-brin-detect/Enable Shut ports ###########################
		index = 0
		for sw in switches:
			if sw.tier == None:
				continue
			appendex = index%2
			config = f"""
			config switch global
			set mclag-split-brain-all-ports-down enable
			end
			"""
			config_cmds_lines(sw.console,config)
			index += 1
		console_timer(300,msg=f"After enabling split-brain-detect, wait for 300s ")
		test_log.write(f"============================================================================================================\n")
		test_log.write(f"		 Enable split-brian-detect/ Enable shut-ports 			\n")
		test_log.write(f"=============================================================================================================\n")
		console_timer(300,msg=f"After enabling split-brain without shut-down ports wait for 300s to start testing")
		power_cycle_testing()
		upgrade_testing()
		reboot_testing()
		icl_testing()