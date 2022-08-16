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

	sys.stdout = Logger("Log/poe_testing.log")
	
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
	#file = 'tbinfo_poe_testing_124EP.xml'
	#file = 'tbinfo_poe_testing_148EP.xml'
	file = 'tbinfo_poe_testing_148_FPOE_Burn.xml'
	#file = 'tbinfo_poe_testing_108FF.xml'
	#file = 'tbinfo_poe_testing_108FP.xml'
	#file = 'tbinfo_poe_testing_108FP_2.xml'
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
	port_list = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]
	# sw.exect_boot_bios()
	# exit()
	# sw.pdu_cycle_bios()
	# sleep(30)
	# sw.reboot_bios()
	# exit()

	def compare_poe_inline(poe_inline_before, poe_inline_after):
		ports_dict_list_before = poe_inline_before["ports"]
		ports_dict_list_after = poe_inline_after["ports"]
		delta = {}
		for pb in ports_dict_list_before:
			for pa in ports_dict_list_after:
				if pb["Interface"] == pa["Interface"]:
					if pb["State"] != pa["State"]:
						delta["State"] = f'{pb["State"]}"" : {pa["State"]}'
					elif pb["Power-consumption(W)"] != pa["Power-consumption(W)"]:
						delta["Power-consumption(W)"] = f'{pb["Power-consumption(W)"]} vs {pa["Power-consumption(W)"]}'
					elif pb["Priority"] != pa["Priority"]:
						delta["Priority"] = f'{pb["Priority"]} vs {pa["Priority"]}'
					elif pb["Class"] != pa["Class"]:
						delta["Class"] = f'{pb["Class"]} vs {pa["Class"]}'

		return delta



	def find_poe_status(output_dict):
		ppoe_list_tester = []
		regex = r'p([0-9]+)'
		for k,v in output_dict.items():
			if v == "1":
				matched = re.search(regex,k)
				if matched:
					ppoe_list_tester.append(int(matched.group(1)))
		new_list = []
		for p in ppoe_list_tester:
			if p <= 8:
				new_list.append(p)
		return new_list

	def find_poe_measure(service_power_dict):
		ppoe_list_tester = []
		for k,v in service_power_dict.items():
			power = float(re.search(r"([0-9\.]+)V",v).group(1))
			if power > 1.0:
				ppoe_list_tester.append(k)
		return ppoe_list_tester

	def compare_boot_service_power(boot_power_dict,service_power_dict,ppoe_list_tester):
		for i in ppoe_list_tester:
			port=f"p{i}"
			if "V" in boot_power_dict[port]:
				boot_power_dict[port] = boot_power_dict[port].split("V")[0]
			if "V" in service_power_dict[port]:
				service_power_dict[port] = service_power_dict[port].split("V")[0]

			if abs(float(boot_power_dict[port]) - float(service_power_dict[port])) < 2:
				continue
			else:
				print(f"Power is different. Boot:{port}|{boot_power_dict[port]}, In Service:{port}|{service_power_dict[port]}")
				return False
		return True
		# for k,v in boot_power_dict.items():
		# 	power = float(re.search(r"([0-9\.]+)V",v).group(1))
		# 	print(f"power = {power}")
		# 	if power > :
		# 		if service_power_dict[k] == v:
		# 			continue
		# 		else:
		# 			print(f"Boot:{k}|{boot_power_dict[k]}, In Service:{k}|{service_power_dict[k]}")
		# 			return False
		#return True

	################################# debug_turn_on_poe_testing ################################
	def debug_turn_on_poe_testing(*args, **kwargs):
		if "boot" in kwargs:
			boot_mode = kwargs['boot']
		else: 
			boot_mode = "warm"

		if "poe_status" in kwargs:
			poe_status = kwargs['poe_status']
		else:
			poe_status = "enable"

		if "iteration" in kwargs:
			run_numbers = kwargs['iteration']
		else:
			run_numbers = 1

		print_double_line()
		print("				Start Turn On POE Power Testing		")
		print_double_line()

		turn_off_sample = f"diag debug unit_test 53 5 0x08 0x00 0x0 0x01 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff" 
		turn_on_sample =  f"diag debug unit_test 53 5 0x01 0x00 0x0 0x02 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff"

		poe_current_list = [100,200,300,400]
		print_title ("Change POE ports to Semi-auto mode")
		for j in range(run_numbers):
			for port_index in port_list:
				cmd = f"diag debug unit_test 53 5 0x08 0x00 {hex(port_index-1)} 0x01 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff" 
				config_cmds_lines(sw.console,cmd,check_prompt=True)
				sleep(2)
			sw.show_command("get switch poe inline")
			
			
			# ##############################################
			# #  Setup POE tester before test starts
			# ##############################################
			
			for poe_class in range(5):
				for poe_current in poe_current_list:
					tester.poe_reset(poe_class=poe_class,current=poe_current)
					sleep(60)
					output_list = tester.get_poe_command(cmd="status")
					output_dict = tester.parse_status_output(output_list)
					print(output_dict)

					sw.show_command("get switch poe inline")

			print_title ("Change POE ports to force-power-on mode")
			for port_index in port_list:
				cmd = f"diag debug unit_test 53 5 0x01 0x00 {hex(port_index-1)} 0x02 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff" 
				config_cmds_lines(sw.console,cmd,check_prompt=True)
				sleep(2)

			for poe_class in range(5):
				for poe_current in poe_current_list:
					tester.poe_reset(poe_class=poe_class,current=poe_current)
					sleep(60)
					output_list = tester.get_poe_command(cmd="status")
					output_dict = tester.parse_status_output(output_list)
					print(output_dict)

					sw.show_command("get switch poe inline")
			# result = True
			# regex = r'p([0-9]+)'
			# ppoe_list_tester = find_poe_status(output_dict)
			# all_poe_ports.sort()
			# ppoe_list_tester.sort()
			# print(all_poe_ports,ppoe_list_tester)


			# print_double_line()
			# if all_poe_ports != ppoe_list_tester:
			# 	print(f"Failed: Before power cyble to BIOS, Switch All POE ports list is NOT Equal to All POE Tester list")
			# 	result = False
			# 	return result
			# else:
			# 	print(f"Before {boot_mode} Boot, Switch POE ports list is Equal to POE Tester list, Continue.....")
			# print_double_line()

			# ##############################################
			# #  Bring switch to BIOS mode
			# ##############################################
			# sw.pdu_cycle_bios()
			# sleep(10)
			# for i in range(5):
			# 	tester.poe_reset()
			# 	sleep(10)
			# 	output_list = tester.get_poe_command(cmd="status")
			# 	output_dict = tester.parse_status_output(output_list)
			# 	print(output_dict)
			# 	ppoe_list_tester = find_poe_status(output_dict)

			# 	p_poe_ports = p_poe_fast  ### target ports

			# 	if poe_status == "disable":
			# 		p_poe_ports = []
					 
			# 	ppoe_list_tester.sort()
			# 	p_poe_ports.sort()
			# 	print(f"In BIOS. POE Tester ports = {ppoe_list_tester}. Switch perpetual POE ports = {p_poe_ports}, Switch PoE ports = {all_poe_ports}" )

			# 	if ppoe_list_tester == p_poe_ports:
			# 		print(f"Sucess: In BIOS mode, the POE Tester powered ports is Equal to All Switch POE port, Continue looping")		 
			# 	elif poe_status == "disable" and ppoe_list_tester == []:
			# 		print(f"Success: In BIOS mode, All Ports are POE disabled, No power drawn, continue...")
			# 	else:
			# 		print(f"Failed: In BIOS Mode, Switch perpetual ports list NOT Equal to POE Tester list. ")
			# 		result = False
			# 		break

			# if result == False:
			# 	print_double_line()
			# 	print(f"Failed: During switch {boot_mode} boots, POE Perpetual ports are not working")
			# 	print(f"Switch Perpetual ports = {p_poe}")
			# 	print(f"Switch Perpetual Fast ports = {p_poe_fast}")
			# 	print(f"POE Tester ports received power = {ppoe_list_tester}")
			# 	print_double_line()
				 
			# else:
			# 	print_double_line()
			# 	print(f"Successul: During switch boot to BIOS mode, POE Perpetual ports are working")
			# 	print(f"Switch Perpetual ports = {p_poe}")
			# 	print(f"Switch Perpetual Fast ports = {p_poe_fast}")
			# 	print(f"POE Tester ports received power = {ppoe_list_tester}")

			# console_timer(5,msg=f"wait for 5s and reboot from BIOS...")
			# sw.reboot_bios()
			# console_timer(180,msg=f"wait for 180s for a final check.....")
			# output_list = tester.get_poe_command(cmd="status")
			# output_dict = tester.parse_status_output(output_list)
			# print(output_dict)

			# ppoe_list_tester = find_poe_status(output_dict)
			# all_poe_ports.sort()
			# ppoe_list_tester.sort()
			# print(all_poe_ports,ppoe_list_tester)

			# print_double_line()
			# if all_poe_ports != ppoe_list_tester:
			# 	print("Failed: After Boot from BIOS, Switch perpetual ports list NOT Equal to All POE Tester list")
			# 	result = False
			# else:
			# 	print(f"Success={result}: finished #{j+1} round of basic BIOS testing")
			# print_double_line()
			# pass
		return True



	################################# power_buget_testing ################################
	def power_buget_testing(*args, **kwargs):
		if "boot" in kwargs:
			boot_mode = kwargs['boot']
		else: 
			boot_mode = "warm"

		if "poe_status" in kwargs:
			poe_status = kwargs['poe_status']
		else:
			poe_status = "enable"

		if "iteration" in kwargs:
			run_numbers = kwargs['iteration']
		else:
			run_numbers = 1

		print_double_line()
		print("				Start POE Power Budget Testing		")
		print_double_line()

		for j in range(run_numbers):
			
			##############################################
			# Configure DUT POE ports before test starts
			##############################################
			# for p in p_poe:
			# 	config = f"""
			# 	config switch physical-port
	  #   			edit port{p}
	  #        		set poe-port-power perpetual
	  #        		set poe-status {poe_status}
	  #   			next
			# 	end
			# 	"""
			# 	config_cmds_lines(sw.console,config,check_prompt=True)	
			# for p in p_poe_fast:
			# 	config = f"""
			# 	config switch physical-port
	  #   			edit port{p}
	  #        		set poe-port-power perpetual-fast
	  #        		set poe-status {poe_status}
	  #   			next
			# 	end
			# 	"""
			# 	config_cmds_lines(sw.console,config)

			# for p in normal:
			# 	config = f"""
			# 	config switch physical-port
	  #   			edit port{p}
	  #        		unset poe-port-power
	  #        		set poe-status {poe_status}
	  #   			next
			# 	end
			# 	"""
			# 	config_cmds_lines(sw.console,config)

			config = f"""
			conf switch global
			set poe-power-budget 370
			end
			"""
			config_cmds_lines(sw.console,config)
			sleep(2)

			for i in range(10):
				sw.show_command("get switch poe inline")
				sleep(5)

			config = f"""
				conf switch global
				set poe-power-budget 20
				end
			"""
			config_cmds_lines(sw.console,config)
			sleep(2)

			for i in range(10):
				sw.show_command("get switch poe inline")
				sleep(5)
			
			# ##############################################
			# #  Setup POE tester before test starts
			# ##############################################
			# tester.poe_reset()
			# sleep(5)
			# output_list = tester.get_poe_command(cmd="status")
			# output_dict = tester.parse_status_output(output_list)
			# print(output_dict)

			# sw.show_command("get switch poe inline")

			# result = True
			# regex = r'p([0-9]+)'
			# ppoe_list_tester = find_poe_status(output_dict)
			# all_poe_ports.sort()
			# ppoe_list_tester.sort()
			# print(all_poe_ports,ppoe_list_tester)


			# print_double_line()
			# if all_poe_ports != ppoe_list_tester:
			# 	print(f"Failed: Before power cyble to BIOS, Switch All POE ports list is NOT Equal to All POE Tester list")
			# 	result = False
			# 	return result
			# else:
			# 	print(f"Before {boot_mode} Boot, Switch POE ports list is Equal to POE Tester list, Continue.....")
			# print_double_line()

			# ##############################################
			# #  Bring switch to BIOS mode
			# ##############################################
			# sw.pdu_cycle_bios()
			# sleep(10)
			# for i in range(5):
			# 	tester.poe_reset()
			# 	sleep(10)
			# 	output_list = tester.get_poe_command(cmd="status")
			# 	output_dict = tester.parse_status_output(output_list)
			# 	print(output_dict)
			# 	ppoe_list_tester = find_poe_status(output_dict)

			# 	p_poe_ports = p_poe_fast  ### target ports

			# 	if poe_status == "disable":
			# 		p_poe_ports = []
					 
			# 	ppoe_list_tester.sort()
			# 	p_poe_ports.sort()
			# 	print(f"In BIOS. POE Tester ports = {ppoe_list_tester}. Switch perpetual POE ports = {p_poe_ports}, Switch PoE ports = {all_poe_ports}" )

			# 	if ppoe_list_tester == p_poe_ports:
			# 		print(f"Sucess: In BIOS mode, the POE Tester powered ports is Equal to All Switch POE port, Continue looping")		 
			# 	elif poe_status == "disable" and ppoe_list_tester == []:
			# 		print(f"Success: In BIOS mode, All Ports are POE disabled, No power drawn, continue...")
			# 	else:
			# 		print(f"Failed: In BIOS Mode, Switch perpetual ports list NOT Equal to POE Tester list. ")
			# 		result = False
			# 		break

			# if result == False:
			# 	print_double_line()
			# 	print(f"Failed: During switch {boot_mode} boots, POE Perpetual ports are not working")
			# 	print(f"Switch Perpetual ports = {p_poe}")
			# 	print(f"Switch Perpetual Fast ports = {p_poe_fast}")
			# 	print(f"POE Tester ports received power = {ppoe_list_tester}")
			# 	print_double_line()
				 
			# else:
			# 	print_double_line()
			# 	print(f"Successul: During switch boot to BIOS mode, POE Perpetual ports are working")
			# 	print(f"Switch Perpetual ports = {p_poe}")
			# 	print(f"Switch Perpetual Fast ports = {p_poe_fast}")
			# 	print(f"POE Tester ports received power = {ppoe_list_tester}")

			# console_timer(5,msg=f"wait for 5s and reboot from BIOS...")
			# sw.reboot_bios()
			# console_timer(180,msg=f"wait for 180s for a final check.....")
			# output_list = tester.get_poe_command(cmd="status")
			# output_dict = tester.parse_status_output(output_list)
			# print(output_dict)

			# ppoe_list_tester = find_poe_status(output_dict)
			# all_poe_ports.sort()
			# ppoe_list_tester.sort()
			# print(all_poe_ports,ppoe_list_tester)

			# print_double_line()
			# if all_poe_ports != ppoe_list_tester:
			# 	print("Failed: After Boot from BIOS, Switch perpetual ports list NOT Equal to All POE Tester list")
			# 	result = False
			# else:
			# 	print(f"Success={result}: finished #{j+1} round of basic BIOS testing")
			# print_double_line()
			# pass
		return True



	################################# basic_bios_poe_boot_testing ################################
	def basic_bios_poe_boot_testing(*args, **kwargs):
		if "boot" in kwargs:
			boot_mode = kwargs['boot']
		else: 
			boot_mode = "warm"

		if "poe_status" in kwargs:
			poe_status = kwargs['poe_status']
		else:
			poe_status = "enable"

		if "iteration" in kwargs:
			run_numbers = iteration
		else:
			run_numbers = 1

		print_double_line()
		print("				Start basic_bios_poe_boot_testing {boot_mode}		")
		print_double_line()


		port_list = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]
		# 
		for j in range(run_numbers):
			p_poe,p_poe_fast,normal = partition(port_list,3)

			all_ppoe_ports = p_poe + p_poe_fast
			all_poe_ports = p_poe + p_poe_fast + normal
			print(f"Perpetual POE Ports = {p_poe}")
			print(f"Perpetual Fast POE Ports = {p_poe_fast}")
			print(f"Normal POE Ports = {normal}")

			if poe_status == "disable":
				all_poe_ports = []
			##############################################
			# Configure DUT POE ports before test starts
			##############################################
			for p in p_poe:
				config = f"""
				config switch physical-port
	    			edit port{p}
	         		set poe-port-power perpetual
	         		set poe-status {poe_status}
	    			next
				end
				"""
				config_cmds_lines(sw.console,config,check_prompt=True)	
			for p in p_poe_fast:
				config = f"""
				config switch physical-port
	    			edit port{p}
	         		set poe-port-power perpetual-fast
	         		set poe-status {poe_status}
	    			next
				end
				"""
				config_cmds_lines(sw.console,config)

			for p in normal:
				config = f"""
				config switch physical-port
	    			edit port{p}
	         		unset poe-port-power
	         		set poe-status {poe_status}
	    			next
				end
				"""
				config_cmds_lines(sw.console,config)

			config = f"""
			conf switch global
			unset poe-power-budget
			unset poe-power-mode 
			end
			"""
			config_cmds_lines(sw.console,config)
			sleep(20)
			sw.show_command("diagnose hardware sysinfo bootenv")
			
			##############################################
			#  Setup POE tester before test starts
			##############################################
			tester.poe_reset()
			sleep(5)
			output_list = tester.get_poe_command(cmd="status")
			output_dict = tester.parse_status_output(output_list)
			print(output_dict)

			sw.show_command("get switch poe inline")

			result = True
			regex = r'p([0-9]+)'
			ppoe_list_tester = find_poe_status(output_dict)
			all_poe_ports.sort()
			ppoe_list_tester.sort()
			print(all_poe_ports,ppoe_list_tester)


			print_double_line()
			if all_poe_ports != ppoe_list_tester:
				print(f"Failed: Before power cyble to BIOS, Switch All POE ports list is NOT Equal to All POE Tester list")
				result = False
				return result
			else:
				print(f"Before {boot_mode} Boot, Switch POE ports list is Equal to POE Tester list, Continue.....")
			print_double_line()

			##############################################
			#  Bring switch to BIOS mode
			##############################################
			sw.pdu_cycle_bios()
			sleep(10)
			for i in range(5):
				tester.poe_reset()
				sleep(10)
				output_list = tester.get_poe_command(cmd="status")
				output_dict = tester.parse_status_output(output_list)
				print(output_dict)
				ppoe_list_tester = find_poe_status(output_dict)

				p_poe_ports = p_poe_fast  ### target ports

				if poe_status == "disable":
					p_poe_ports = []
					 
				ppoe_list_tester.sort()
				p_poe_ports.sort()
				print(f"In BIOS. POE Tester ports = {ppoe_list_tester}. Switch perpetual POE ports = {p_poe_ports}, Switch PoE ports = {all_poe_ports}" )

				if ppoe_list_tester == p_poe_ports:
					print(f"Sucess: In BIOS mode, the POE Tester powered ports is Equal to All Switch POE port, Continue looping")		 
				elif poe_status == "disable" and ppoe_list_tester == []:
					print(f"Success: In BIOS mode, All Ports are POE disabled, No power drawn, continue...")
				else:
					print(f"Failed: In BIOS Mode, Switch perpetual ports list NOT Equal to POE Tester list. ")
					result = False
					break

			if result == False:
				print_double_line()
				print(f"Failed: During switch {boot_mode} boots, POE Perpetual ports are not working")
				print(f"Switch Perpetual ports = {p_poe}")
				print(f"Switch Perpetual Fast ports = {p_poe_fast}")
				print(f"POE Tester ports received power = {ppoe_list_tester}")
				print_double_line()
				 
			else:
				print_double_line()
				print(f"Successul: During switch boot to BIOS mode, POE Perpetual ports are working")
				print(f"Switch Perpetual ports = {p_poe}")
				print(f"Switch Perpetual Fast ports = {p_poe_fast}")
				print(f"POE Tester ports received power = {ppoe_list_tester}")

			console_timer(5,msg=f"wait for 5s and reboot from BIOS...")
			sw.reboot_bios()
			console_timer(180,msg=f"wait for 180s for a final check.....")
			output_list = tester.get_poe_command(cmd="status")
			output_dict = tester.parse_status_output(output_list)
			print(output_dict)

			ppoe_list_tester = find_poe_status(output_dict)
			all_poe_ports.sort()
			ppoe_list_tester.sort()
			print(all_poe_ports,ppoe_list_tester)

			print_double_line()
			if all_poe_ports != ppoe_list_tester:
				print("Failed: After Boot from BIOS, Switch perpetual ports list NOT Equal to All POE Tester list")
				result = False
			else:
				print(f"Success={result}: finished #{j+1} round of basic BIOS testing")
			print_double_line()
			pass
		return result


	# ################################# compare_power_testing ################################
	# def compare_power_testing(*args, **kwargs):

	# 	if "boot" in kwargs:
	# 		boot_mode = kwargs['boot']
	# 	else: 
	# 		boot_mode = "warm"

	# 	if "poe_status" in kwargs:
	# 		poe_status = kwargs['poe_status']
	# 	else:
	# 		poe_status = "enable"

	# 	print_double_line()
	# 	print(f"				Start compare_power_testing	in {boot_mode} boot      ")
	# 	print_double_line()

	# 	if "iteration" in kwargs:
	# 		run_numbers = iteration
	# 	else:
	# 		run_numbers = 1

	# 	 
	# 	for j in range(run_numbers):
	# 		p_poe,p_poe_fast,normal = partition(port_list,3)

	# 		all_ppoe_ports = p_poe + p_poe_fast
	# 		all_poe_ports = p_poe + p_poe_fast + normal
	# 		print(f"Perpetual POE Ports = {p_poe}")
	# 		print(f"Perpetual Fast POE Ports = {p_poe_fast}")
	# 		print(f"Normal POE Ports = {normal}")
	# 		##############################################
	# 		# Configure DUT POE ports before test starts
	# 		##############################################
	# 		for p in p_poe:
	# 			config = f"""
	# 			config switch physical-port
	#     			edit port{p}
	#          		set poe-port-power perpetual
	#          		set poe-status {poe_status}
	#     			next
	# 			end
	# 			"""
	# 			config_cmds_lines(sw.console,config,check_prompt=True)	
	# 		for p in p_poe_fast:
	# 			config = f"""
	# 			config switch physical-port
	#     			edit port{p}
	#          		set poe-port-power perpetual-fast
	#          		set poe-status {poe_status}
	#     			next
	# 			end
	# 			"""
	# 			config_cmds_lines(sw.console,config)

	# 		for p in normal:
	# 			config = f"""
	# 			config switch physical-port
	#     			edit port{p}
	#          		unset poe-port-power
	#          		set poe-status {poe_status}
	#     			next
	# 			end
	# 			"""
	# 			config_cmds_lines(sw.console,config)

	# 		config = f"""
	# 		conf switch global
	# 		unset poe-power-budget
	# 		unset poe-power-mode 
	# 		end
	# 		"""
	# 		config_cmds_lines(sw.console,config)
	# 		sleep(20)
	# 		sw.show_command("diagnose hardware sysinfo bootenv")
	# 		sw.show_command("get switch poe inline")

	# 		##############################################
	# 		#  Setup POE tester before test starts
	# 		##############################################
	# 		tester.poe_reset()
	# 		sleep(5)
	# 		output_list = tester.get_poe_command(cmd="status")
	# 		output_dict = tester.parse_status_output(output_list)
	# 		print(output_dict)

	# 		result = True
			
	# 		ppoe_list_tester = find_poe_status(output_dict)
	# 		all_poe_ports.sort()
	# 		ppoe_list_tester.sort()
	# 		print(all_poe_ports,ppoe_list_tester)

	# 		print_double_line()
	# 		if all_poe_ports != ppoe_list_tester:
	# 			print(f"Failed: Before {boot_mode} Boot, Switch All POE ports list is NOT Equal to All POE Tester list")
	# 			result = False
	# 			return result
	# 		else:
	# 			print(f"Before {boot_mode} Boot, Switch POE ports list is Equal to POE Tester list, Continue.....")
	# 		print_double_line()

	# 		output_list = tester.get_poe_command(cmd="measure")
	# 		service_power_dict = tester.parse_measure_output(output_list)
	# 		print(f"power output in service:{service_power_dict}")
	# 		##############################################
	# 		#  Warm or Cold Boot Switch & check POE Tester
	# 		##############################################
	# 		if boot_mode == "warm":
	# 			sw.switch_reboot()
	# 		if boot_mode == "cold":
	# 			sw.pdu_cycle()
			
	# 		print_double_line()
	# 		while True:
	# 			tester.poe_reset()
	# 			sleep(10)
	# 			output_list = tester.get_poe_command(cmd="status")
	# 			output_dict = tester.parse_status_output(output_list)
	# 			print(output_dict)
	# 			ppoe_list_tester = find_poe_status(output_dict)

	# 			sleep(2)
	# 			output_list = tester.get_poe_command(cmd="measure")
	# 			boot_power_dict = tester.parse_measure_output(output_list)
	# 			print(f"power output in booting:{boot_power_dict}")
				
	# 			if boot_mode == "warm":
	# 				p_poe_ports = all_ppoe_ports
	# 			elif boot_mode == "cold":
	# 				p_poe_ports = p_poe_fast
	# 			else:
	# 				print("!!!!!!! Boot Mode Is Invalid, Something Is Wrong!!!!!!!!!!")
	# 				return False
	# 			ppoe_list_tester.sort()
	# 			p_poe_ports.sort()
	# 			print(f"Boot Mode = {boot_mode}. POE Tester ports = {ppoe_list_tester}. Switch perpetual POE ports = {p_poe_ports}, Switch PoE ports = {all_poe_ports}" )

	# 			if ppoe_list_tester != p_poe_ports:
	# 				if ppoe_list_tester == all_poe_ports:
	# 					print(f"Sucess: Switch has {boot_mode} booted up, the POE Tester powered ports is Equal to All Switch POE port, Continue to final check....")
	# 					break
	# 				else:
	# 					print(f"Failed: During {boot_mode} boot, Switch perpetual ports list NOT Equal to POE Tester list, STOP!")
	# 					result = False
	# 					break
	# 			else:
	# 				print(f"During {boot_mode} boot Switch perpetual ports list Equal to POE Tester list, Continue....")
			
	# 			if compare_boot_service_power(boot_power_dict,service_power_dict,ppoe_list_tester):
	# 				print(f"During {boot_mode} boot Switch perpetual ports power output Equal to in service mode, Continue....")
	# 			else:
	# 				print(f"Failed: During {boot_mode} boot Switch perpetual ports power output NOT Equal to in service mode")
	# 				result = False

	# 		if result == False:
	# 			print_double_line()
	# 			print(f"Failed: During switch {boot_mode} boots, POE Perpetual ports are not working")
	# 			print(f"Switch Perpetual ports = {p_poe}")
	# 			print(f"Switch Perpetual Fast ports = {p_poe_fast}")
	# 			print(f"POE Tester ports received power = {ppoe_list_tester}")
	# 			print_double_line()
	# 			return result
	# 		else:
	# 			console_timer(120,msg=f"{boot_mode} boot testing passed, wait for 120s for a final check ")

	# 			output_list = tester.get_poe_command(cmd="status")
	# 			output_dict = tester.parse_status_output(output_list)
	# 			print(output_dict)

	# 			ppoe_list_tester = find_poe_status(output_dict)
	# 			all_poe_ports.sort()
	# 			ppoe_list_tester.sort()
	# 			print(all_poe_ports,ppoe_list_tester)

	# 			print_double_line()
	# 			if all_poe_ports != ppoe_list_tester:
	# 				print("Failed: After Warm Boot, Switch perpetual ports list NOT Equal to All POE Tester list")
	# 				result = False
	# 				return result
	# 			else:
	# 				print(f"Successul: finished #{j+1} round of {boot_mode} boot testing")
	# 			print_double_line()
	# 	return result

	################################# basic_poe_boot_testing ################################
	def basic_poe_boot_testing(*args, **kwargs):

		if "boot" in kwargs:
			boot_mode = kwargs['boot']
		else: 
			boot_mode = "warm"

		if "poe_status" in kwargs:
			poe_status = kwargs['poe_status']
		else:
			poe_status = "enable"

		if "iteration" in kwargs:
			run_numbers = iteration
		else:
			run_numbers = 1

		print_double_line()
		print(f"				Start basic_poe_boot_testing {boot_mode}")
		print_double_line()
		for j in range(run_numbers):
			p_poe,p_poe_fast,normal = partition(port_list,3)

			all_ppoe_ports = p_poe + p_poe_fast
			all_poe_ports = p_poe + p_poe_fast + normal
			print(f"Perpetual POE Ports = {p_poe}")
			print(f"Perpetual Fast POE Ports = {p_poe_fast}")
			print(f"Normal POE Ports = {normal}")

			if poe_status == "disable":
				all_poe_ports = []
			##############################################
			# Configure DUT POE ports before test starts
			##############################################
			for p in p_poe:
				config = f"""
				config switch physical-port
	    			edit port{p}
	         		set poe-port-power perpetual
	         		set poe-status {poe_status}
	    			next
				end
				"""
				config_cmds_lines(sw.console,config,check_prompt=True)	
			for p in p_poe_fast:
				config = f"""
				config switch physical-port
	    			edit port{p}
	         		set poe-port-power perpetual-fast
	         		set poe-status {poe_status}
	    			next
				end
				"""
				config_cmds_lines(sw.console,config)

			for p in normal:
				config = f"""
				config switch physical-port
	    			edit port{p}
	         		unset poe-port-power
	         		set poe-status {poe_status}
	    			next
				end
				"""
				config_cmds_lines(sw.console,config)

			config = f"""
			conf switch global
			unset poe-power-budget
			unset poe-power-mode 
			end
			"""
			config_cmds_lines(sw.console,config)
			sleep(20)
			sw.show_command("diagnose hardware sysinfo bootenv")
			sw.show_command("get switch poe inline")

			##############################################
			#  Setup POE tester before test starts
			##############################################
			tester.poe_reset()
			sleep(5)
			output_list = tester.get_poe_command(cmd="status")
			output_dict = tester.parse_status_output(output_list)
			print(output_dict)

			result = True
			regex = r'p([0-9]+)'
			ppoe_list_tester = find_poe_status(output_dict)
			all_poe_ports.sort()
			ppoe_list_tester.sort()
			print(all_poe_ports,ppoe_list_tester)

			print_double_line()
			if all_poe_ports != ppoe_list_tester:
				print(f"Failed: Before {boot_mode} Boot, Switch All POE ports list is NOT Equal to All POE Tester list")
				result = False
				return result
			else:
				print(f"Before {boot_mode} Boot, Switch POE ports list is Equal to POE Tester list, Continue.....")
			print_double_line()

			##############################################
			#  Warm or Cold Boot Switch & check POE Tester
			##############################################
			if boot_mode == "warm":
				sw.switch_reboot()
			if boot_mode == "cold":
				sw.pdu_cycle()
			elif boot_mode == "bios":
				sw.pdu_cycle_bios()
				sleep(10)
			elif boot_mode == "warm_bios":
				sw.exect_boot_bios()
				sleep(10)

			print_double_line()
			good = 0 
			bad = 0
			for i in range(10):
				tester.poe_reset()
				sleep(10)
				output_list = tester.get_poe_command(cmd="status")
				output_dict = tester.parse_status_output(output_list)
				print(output_dict)
				ppoe_list_tester = find_poe_status(output_dict)

				if boot_mode == "warm":
					p_poe_ports = all_ppoe_ports
				elif boot_mode == "cold":
					p_poe_ports = p_poe_fast
				elif boot_mode == "bios":
					p_poe_ports = p_poe_fast
				elif boot_mode == "warm_bios":
					p_poe_ports = all_ppoe_ports
				else:
					print("!!!!!!! Boot Mode Is Invalid, Something Is Wrong!!!!!!!!!!")
					return False
				if poe_status == "disable":
					p_poe_ports = []
					all_ppoe_ports = []

				ppoe_list_tester.sort()
				p_poe_ports.sort()
				print(f"Boot Mode = {boot_mode}. POE Tester ports = {ppoe_list_tester}. Switch perpetual POE ports = {p_poe_ports}, Switch PoE ports = {all_poe_ports}" )

				if ppoe_list_tester != p_poe_ports:
					if ppoe_list_tester == all_poe_ports:
						print(f"Good in loop: Switch has {boot_mode} booted up, the POE Tester powered ports is Equal to All Switch POE port, Continue to final check....")
						break
					else:
						print(f"Bad in loop: During {boot_mode} boot, Switch perpetual ports list NOT Equal to POE Tester list!")
						bad += 1 
				else:
					print(f"During {boot_mode} boot Switch perpetual ports list Equal to POE Tester list, Continue....")
					good += 1
					if poe_status == "disable":
						print(f"All Ports are POE disabled, No power drawn, continue...")
						 

			if good >= 1 and bad <=2 :
				result = True 
			else:
				result = False 

			if result == False:
				print_double_line()
				print(f"Failed: During switch {boot_mode} boots, POE Perpetual ports are not working")
				print(f"Switch Perpetual ports = {p_poe}")
				print(f"Switch Perpetual Fast ports = {p_poe_fast}")
				print(f"POE Tester ports received power = {ppoe_list_tester}")
				print_double_line()
				if "bios" in boot_mode:
					sw.reboot_bios()
				return result
			else:
				if "bios" in boot_mode:
					sw.reboot_bios()
				console_timer(180,msg=f"{boot_mode} boot testing passed, wait for 180s for a final check ")

				output_list = tester.get_poe_command(cmd="status")
				output_dict = tester.parse_status_output(output_list)
				print(output_dict)

				ppoe_list_tester = find_poe_status(output_dict)
				all_poe_ports.sort()
				ppoe_list_tester.sort()
				print(all_poe_ports,ppoe_list_tester)

				print_double_line()
				if all_poe_ports != ppoe_list_tester:
					print("Failed: After {boot_mode} Boot, Switch perpetual ports list NOT Equal to All POE Tester list")
					result = False
					return result
				else:
					print(f"Successul: finished #{j+1} round of {boot_mode} boot testing")
				print_double_line()
		return result



	################################# flipping_poe_boot_testing ################################
	def flipping_poe_boot_testing(*args, **kwargs):


		if "boot" in kwargs:
			boot_mode = kwargs['boot']
		else: 
			boot_mode = "warm"

		if "poe_status" in kwargs:
			poe_status = kwargs['poe_status']
		else:
			poe_status = "enable"

		if "iteration" in kwargs:
			run_numbers = iteration
		else:
			run_numbers = 1

		print_double_line()
		print(f"				Start flipping_poe_boot_testing	{boot_mode}	")
		print_double_line()
		 
		for j in range(run_numbers):
			p_poe,p_poe_fast,normal = partition(port_list,3)

			all_ppoe_ports = p_poe + p_poe_fast
			all_poe_ports = p_poe + p_poe_fast + normal
			print(f"Perpetual POE Ports = {p_poe}")
			print(f"Perpetual Fast POE Ports = {p_poe_fast}")
			print(f"Normal POE Ports = {normal}")

			if poe_status == "disable":
				all_poe_ports = []
			##############################################
			# Configure DUT POE ports before test starts
			##############################################
			config = f"""
			conf switch global
			unset poe-power-budget
			unset poe-power-mode 
			end
			"""
			config_cmds_lines(sw.console,config)
			sleep(20)
			# start config
			for p in p_poe:
				config = f"""
				config switch physical-port
	    			edit port{p}
	         		set poe-port-power perpetual
	         		set poe-status {poe_status}
	    			next
				end
				"""
				config_cmds_lines(sw.console,config,check_prompt=True)	
			for p in p_poe_fast:
				config = f"""
				config switch physical-port
	    			edit port{p}
	         		set poe-port-power perpetual-fast
	         		set poe-status {poe_status}
	    			next
				end
				"""
				config_cmds_lines(sw.console,config)

			for p in normal:
				config = f"""
				config switch physical-port
	    			edit port{p}
	         		unset poe-port-power
	         		set poe-status {poe_status}
	    			next
				end
				"""
				config_cmds_lines(sw.console,config)

			sw.show_command("diagnose hardware sysinfo bootenv")
			poe_env_dict = sw.get_poe_env()
			print(poe_env_dict)

			result = True
			# if set(critical) != set(poe_env_dict["poe_priority_critical"]):
			# 	print(f"Critical priority is different, configured vs bootenv = {set(critical)}, set(poe_env_dict['poe_priority_critical'])")
			# 	result = False

			# if set(high) != set(poe_env_dict["poe_priority_high"]):
			# 	print("High priority is different, configured vs bootenv = {set(high)}, set(poe_env_dict['poe_priority_high')")
			# 	result = False

			# if set(low) != set(poe_env_dict["poe_priority_low"]):
			# 	print("Low priority is different, configured vs bootenv = {set(low)}, set(poe_env_dict['poe_priority_low')")
			# 	result = False

			if set(p_poe_fast) != set(poe_env_dict["poe_perpetual_fast"]):
				print(f"Perpetual Fast is different, configured vs bootenv = {set(p_fast)}, set(poe_env_dict['poe_perpetual_fast')")
				result = False

			if set(p_poe) != set(poe_env_dict["poe_perpetual"]):
				print(f"Perpetual Fast is different, configured vs bootenv = {set(perpetual)}, set(poe_env_dict['poe_perpetual')")
				result = False

			print_double_line()
			print(f"Success = {result}. #{j+1} Before flipping bootenv checking is done")
			print_double_line()

			#flip config
			sleep(30)
			for p in p_poe:
				config = f"""
				config switch physical-port
	    			edit port{p}
	         		unset poe-port-power  
	    			next
				end
				"""
				config_cmds_lines(sw.console,config,check_prompt=True)	
			for p in p_poe_fast:
				config = f"""
				config switch physical-port
	    			edit port{p}
	         		unset poe-port-power  
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

				sleep(20)
			# restore config
			for p in p_poe:
				config = f"""
				config switch physical-port
	    			edit port{p}
	         		set poe-port-power perpetual
	         		set poe-status {poe_status}
	    			next
				end
				"""
				config_cmds_lines(sw.console,config,check_prompt=True)	
			for p in p_poe_fast:
				config = f"""
				config switch physical-port
	    			edit port{p}
	         		set poe-port-power perpetual-fast
	         		set poe-status {poe_status}
	    			next
				end
				"""
				config_cmds_lines(sw.console,config)

			for p in normal:
				config = f"""
				config switch physical-port
	    			edit port{p}
	         		unset poe-port-power
	         		set poe-status {poe_status}
	    			next
				end
				"""
				config_cmds_lines(sw.console,config)

			sw.show_command("diagnose hardware sysinfo bootenv")
			poe_env_dict = sw.get_poe_env()
			print(poe_env_dict)

			result = True
			# if set(critical) != set(poe_env_dict["poe_priority_critical"]):
			# 	print(f"Critical priority is different, configured vs bootenv = {set(critical)}, set(poe_env_dict['poe_priority_critical'])")
			# 	result = False

			# if set(high) != set(poe_env_dict["poe_priority_high"]):
			# 	print("High priority is different, configured vs bootenv = {set(high)}, set(poe_env_dict['poe_priority_high')")
			# 	result = False

			# if set(low) != set(poe_env_dict["poe_priority_low"]):
			# 	print("Low priority is different, configured vs bootenv = {set(low)}, set(poe_env_dict['poe_priority_low')")
			# 	result = False

			if set(p_poe_fast) != set(poe_env_dict["poe_perpetual_fast"]):
				print(f"Perpetual Fast is different, configured vs bootenv = {set(p_fast)}, set(poe_env_dict['poe_perpetual_fast')")
				result = False

			if set(p_poe) != set(poe_env_dict["poe_perpetual"]):
				print(f"Perpetual Fast is different, configured vs bootenv = {set(perpetual)}, set(poe_env_dict['poe_perpetual')")
				result = False

			print_double_line()
			print(f"Success = {result}. #{j+1} After flipping bootenv checking is done,")
			print_double_line()
 
			##############################################
			#  Setup POE tester before test starts
			##############################################
			tester.poe_reset()
			sleep(5)
			output_list = tester.get_poe_command(cmd="status")
			output_dict = tester.parse_status_output(output_list)
			print(output_dict)

			regex = r'p([0-9]+)'
			ppoe_list_tester = find_poe_status(output_dict)
			all_poe_ports.sort()
			ppoe_list_tester.sort()
			print(all_poe_ports,ppoe_list_tester)

			print_double_line()
			if all_poe_ports != ppoe_list_tester:
				print(f"Failed: Before {boot_mode} Boot, Switch All POE ports list is NOT Equal to All POE Tester list")
				result = False
				return result
			else:
				print(f"Before {boot_mode} Boot, Switch POE ports list is Equal to POE Tester list, Continue.....")
			print_double_line()

			##############################################
			#  Warm or Cold Boot Switch & check POE Tester
			##############################################
			if boot_mode == "warm":
				sw.switch_reboot()
			if boot_mode == "cold":
				sw.pdu_cycle()
			
			print_double_line()
			good_start = False
			result = True
			while True:
				tester.poe_reset()
				sleep(10)
				output_list = tester.get_poe_command(cmd="status")
				output_dict = tester.parse_status_output(output_list)
				print(output_dict)
				ppoe_list_tester = find_poe_status(output_dict)

				if boot_mode == "warm":
					p_poe_ports = all_ppoe_ports
				elif boot_mode == "cold":
					p_poe_ports = p_poe_fast
				else:
					print("!!!!!!! Boot Mode Is Invalid, Something Is Wrong!!!!!!!!!!")
					return False
				if poe_status == "disable":
					p_poe_ports = []
					all_ppoe_ports = []

				ppoe_list_tester.sort()
				p_poe_ports.sort()
				print(f"Boot Mode = {boot_mode}. POE Tester ports = {ppoe_list_tester}. Switch perpetual POE ports = {p_poe_ports}, Switch PoE ports = {all_poe_ports}" )

				if ppoe_list_tester != p_poe_ports:
					if ppoe_list_tester == all_poe_ports:
						print(f"Sucess: Switch has {boot_mode} booted up, the POE Tester powered ports is Equal to All Switch POE port, Continue to final check....")
						break
					elif good_start:
						print(f"Switch started to boot up: During {boot_mode} boot, none perpetual ports start to diliver power, stop!")
						result = True
						break
					elif good_start == False: 
						print(f"Failed: During {boot_mode} boot, perpetual ports is NOT Equal to configuration, stop!")
						restul = False
						break

				else:
					print(f"During {boot_mode} boot Switch perpetual ports list Equal to POE Tester list, Continue....")
					if poe_status == "disable":
						print(f"All Ports are POE disabled, No power drawn, continue...")
						break
					else:
						good_start = True

			if result == False:
				print_double_line()
				print(f"Failed: During switch {boot_mode} boots, POE Perpetual ports are not working")
				print(f"Switch Perpetual ports = {p_poe}")
				print(f"Switch Perpetual Fast ports = {p_poe_fast}")
				print(f"POE Tester ports received power = {ppoe_list_tester}")
				print_double_line()
				return result
			else:
				console_timer(120,msg=f"{boot_mode} boot testing passed, wait for 120s for a final check ")

				output_list = tester.get_poe_command(cmd="status")
				output_dict = tester.parse_status_output(output_list)
				print(output_dict)

				ppoe_list_tester = find_poe_status(output_dict)
				all_poe_ports.sort()
				ppoe_list_tester.sort()
				print(all_poe_ports,ppoe_list_tester)

				print_double_line()
				if all_poe_ports != ppoe_list_tester:
					print("Failed: After {boot_mode} Boot, Switch perpetual ports list NOT Equal to All POE Tester list")
					result = False
					return result
				else:
					print(f"Successul: finished #{j+1} round of {boot_mode} boot flipping testing")
				print_double_line()
		return result


	################################# poe_cli_testing ################################
	def poe_cli_testing(*args, **kwargs):

		if "boot" in kwargs:
			boot_mode = kwargs['boot']
		else: 
			boot_mode = "warm"
		if boot_mode == "cold":
			p_mode = "perpetual-fast"
		else:
			p_mode = "perpetual"

		if "poe_status" in kwargs:
			poe_status = kwargs['poe_status']
		else:
			poe_status = "enable"

		print_double_line()
		print(f"			Start poe_cli_testing in {boot_mode} boot	")
		print_double_line()

		if "iteration" in kwargs:
			run_numbers = iteration
		else:
			run_numbers = 1

		 
		all_poe_ports = port_list
		for j in range(run_numbers):
			critical,high,low = partition(port_list,3)
			p_fast,perpetual,normal = partition(port_list,3)
			 
			print(f"Critical High Priority Ports = {critical}")
			print(f"High Priority Ports = {high}")
			print(f"Low Priority Ports = {low}")
			print(f"Perpetual Fast = {p_fast}")
			print(f"Perpetual Ports = {perpetual}")
			print(f"Normal Ports = {normal}")
			##############################################
			# Configure DUT POE ports before test starts
			##############################################
			begin = True
			for p in critical:
				config = f"""
				config switch physical-port
	    			edit port{p}
 	         		set poe-port-priority critical-priority
 	         		set poe-status {poe_status}
	    			next
				end
				"""
				config_cmds_lines(sw.console,config,check_prompt=begin)	
				if begin == True:
					begin = False
			for p in high:
				config = f"""
				config switch physical-port
	    			edit port{p}
 	         		set poe-port-priority high-priority
 	         		set poe-status {poe_status}
	    			next
				end
				"""
				config_cmds_lines(sw.console,config)

			for p in low:
				config = f"""
				config switch physical-port
	    			edit port{p}
 	         		set poe-port-priority low-priority
 	         		set poe-status {poe_status}
	    			next
				end
				"""
				config_cmds_lines(sw.console,config)

			for p in p_fast:
				config = f"""
				config switch physical-port
	    			edit port{p}
	         		set poe-port-power perpetual-fast
	         		set poe-status {poe_status}
	    			next
				end
				"""
				config_cmds_lines(sw.console,config)

			for p in perpetual:
				config = f"""
				config switch physical-port
	    			edit port{p}
	         		set poe-port-power perpetual
	         		set poe-status {poe_status}
	    			next
				end
				"""
				config_cmds_lines(sw.console,config)	

			for p in normal:
				config = f"""
				config switch physical-port
	    			edit port{p}
	         		set poe-port-power normal
	         		set poe-status {poe_status}
	    			next
				end
				"""
				config_cmds_lines(sw.console,config)	

			config = f"""
			conf switch global
			set poe-power-budget 70
			set poe-power-mode priority
			end
			"""
			config_cmds_lines(sw.console,config)

			sleep(20)

			sw.show_command("diagnose hardware sysinfo bootenv")
			poe_env_dict = sw.get_poe_env()
			print(poe_env_dict)

			result = True
			if set(critical) != set(poe_env_dict["poe_priority_critical"]):
				print(f"Critical priority is different, configured vs bootenv = {set(critical)}, set(poe_env_dict['poe_priority_critical'])")
				result = False

			if set(high) != set(poe_env_dict["poe_priority_high"]):
				print(f"High priority is different, configured vs bootenv = {set(high)}, set(poe_env_dict['poe_priority_high')")
				result = False

			if set(low) != set(poe_env_dict["poe_priority_low"]):
				print(f"Low priority is different, configured vs bootenv = {set(low)}, set(poe_env_dict['poe_priority_low')")
				result = False

			if set(p_fast) != set(poe_env_dict["poe_perpetual_fast"]):
				print(f"Perpetual Fast is different, configured vs bootenv = {set(p_fast)}, set(poe_env_dict['poe_perpetual_fast')")
				result = False

			if set(perpetual) != set(poe_env_dict["poe_perpetual"]):
				print(f"Perpetual Fast is different, configured vs bootenv = {set(perpetual)}, set(poe_env_dict['poe_perpetual')")
				result = False
			print_double_line()
			print(f"Success = {result}. #{j+1} before boot poe_cli_testing is done,")
			print_double_line()

			if boot_mode == "warm":
				sw.switch_reboot()
				console_timer(180,msg=f"{boot_mode} boot, wait for 180s to boot ")
			if boot_mode == "cold":
				sw.pdu_cycle()
				console_timer(180,msg=f"{boot_mode} boot, wait for 180s to boot ")
			if boot_mode == "bios":
				sw.pdu_cycle_bios()
				console_timer(20,msg=f"{boot_mode} boot, wait for 20s to bring to BIOS mode ")
				sw.reboot_bios()
				console_timer(180,msg=f"wait for 180s to boot from BIOS mode")

			print(f"poe_cli_testing: Verify bootenv after {boot_mode} boot")
			sw.show_command("diagnose hardware sysinfo bootenv")
			poe_env_dict = sw.get_poe_env()
			print(poe_env_dict)

			result = True
			if set(critical) != set(poe_env_dict["poe_priority_critical"]):
				print(f"Critical priority is different, configured vs bootenv = {set(critical)}, set(poe_env_dict['poe_priority_critical'])")
				result = False

			if set(high) != set(poe_env_dict["poe_priority_high"]):
				print(f"High priority is different, configured vs bootenv = {set(high)}, set(poe_env_dict['poe_priority_high')")
				result = False

			if set(low) != set(poe_env_dict["poe_priority_low"]):
				print(f"Low priority is different, configured vs bootenv = {set(low)}, set(poe_env_dict['poe_priority_low')")
				result = False

			if set(p_fast) != set(poe_env_dict["poe_perpetual_fast"]):
				print(f"Perpetual Fast is different, configured vs bootenv = {set(p_fast)}, set(poe_env_dict['poe_perpetual_fast')")
				result = False

			if set(perpetual) != set(poe_env_dict["poe_perpetual"]):
				print(f"Perpetual Fast is different, configured vs bootenv = {set(perpetual)}, set(poe_env_dict['poe_perpetual')")
				result = False
			print_double_line()
			print(f"Success = {result}. #{j+1} after boot poe_cli_testing is done,")
			print_double_line()


	################################# priority_power_testing ################################
	def priority_power_testing(*args, **kwargs):

		if "boot" in kwargs:
			boot_mode = kwargs['boot']
		else: 
			boot_mode = "warm"
		if boot_mode == "cold":
			p_mode = "perpetual-fast"
		elif boot_mode == "bios":
			p_mode = "perpetual-fast"
		elif boot_mode == "warm_bios":
			p_mode = "perpetual"
		else:
			p_mode = "perpetual"
		if "poe_status" in kwargs:
			poe_status = kwargs['poe_status']
		else:
			poe_status = "enable"

		print_double_line()
		print(f"			Start priority_power_testing in {boot_mode} boot	")
		print_double_line()

		if "iteration" in kwargs:
			run_numbers = iteration
		else:
			run_numbers = 1

		 
		all_poe_ports = port_list
		for j in range(run_numbers):
			critical,high,low = partition(port_list,3)
			 
			print(f"Critical High Priority Ports = {critical}")
			print(f"High Priority Ports = {high}")
			print(f"Low Priority Ports = {low}")
			##############################################
			# Configure DUT POE ports before test starts
			##############################################
			begin = True
			for p in critical:
				config = f"""
				config switch physical-port
	    			edit port{p}
	         		set poe-port-power {p_mode}
	         		set poe-port-priority critical-priority
	         		set poe-status {poe_status}
	    			next
				end
				"""
				config_cmds_lines(sw.console,config,check_prompt=begin)	
				if begin == True:
					begin = False
			for p in high:
				config = f"""
				config switch physical-port
	    			edit port{p}
	         		set poe-port-power {p_mode}
	         		set poe-port-priority high-priority
	         		set poe-status {poe_status}
	    			next
				end
				"""
				config_cmds_lines(sw.console,config)

			for p in low:
				config = f"""
				config switch physical-port
	    			edit port{p}
	         		set poe-port-power {p_mode}
	         		set poe-port-priority low-priority
	         		set poe-status {poe_status}
	    			next
				end
				"""
				config_cmds_lines(sw.console,config)

			config = f"""
			conf switch global
			set poe-power-budget 70
			set poe-power-mode priority
			end
			"""
			config_cmds_lines(sw.console,config)

			sleep(20)

			sw.show_command("diagnose hardware sysinfo bootenv")
			
			##############################################
			#  Setup POE tester before test starts
			##############################################
			tester.poe_reset(current=350,poe_class=4)
			sleep(5)
			output_list = tester.get_poe_command(cmd="status")
			output_dict = tester.parse_status_output(output_list)
			print(output_dict)

			sw.show_command("get switch poe inline")
			poe_inline_before = sw.get_poe_inline()

			result = True
			
			ppoe_list_tester = find_poe_status(output_dict)
			critical.sort()
			ppoe_list_tester.sort()
			print(critical,ppoe_list_tester)

			print_double_line()
			if critical != ppoe_list_tester:
				print(f"Failed: Before {boot_mode} Boot, critical POE ports list is NOT Equal to POE Tester list")
				result = False
				return result
			else:
				print(f"Before {boot_mode} Boot, critical POE ports list is Equal to POE Tester list, Continue.....")
			print_double_line()

			output_list = tester.get_poe_command(cmd="measure")
			service_power_dict = tester.parse_measure_output(output_list)
			print(f"power output in service:{service_power_dict}")
			##############################################
			#  Warm or Cold Boot Switch & check POE Tester
			##############################################
			if boot_mode == "warm":
				sw.switch_reboot()
			elif boot_mode == "cold":
				sw.pdu_cycle()
			elif boot_mode == "bios":
				sw.pdu_cycle_bios()
				sleep(10)
			elif boot_mode == "warm_bios":
				sw.exect_boot_bios()
				sleep(10)

			print_double_line()
			good = 0
			bad = 0
			good_power = 0
			bad_power = 0
			for i in range(5):
				tester.poe_reset(current=350,poe_class=4) #set current = 250, output = 55*350 = 19W
				sleep(10)
				output_list = tester.get_poe_command(cmd="status")
				output_dict = tester.parse_status_output(output_list)
				print(output_dict)
				ppoe_list_tester = find_poe_status(output_dict)
				sleep(2)
				output_list = tester.get_poe_command(cmd="measure")
				boot_power_dict = tester.parse_measure_output(output_list)
				print(f"power output in booting:{boot_power_dict}")
				
				p_poe_ports = critical
				 
				ppoe_list_tester.sort()
				p_poe_ports.sort()
				print(f"Boot Mode = {boot_mode}. POE Tester ports = {ppoe_list_tester}. Switch perpetual POE ports = {p_poe_ports}, Switch PoE ports = {all_poe_ports}" )

				if ppoe_list_tester == critical:
					print(f"Iteration Succeeded: Switch has {boot_mode} booted up, the POE Tester powered ports is Equal to All Switch POE port, Continue looping....")
					good +=1 
				else:
					print(f"Iteration Failed: During {boot_mode} boot, Switch perpetual ports list NOT Equal to POE Tester list!")
					bad += 1 
			
				if compare_boot_service_power(boot_power_dict,service_power_dict,ppoe_list_tester):
					print(f"During {boot_mode} boot Switch perpetual ports power output Equal to in service mode, Continue looping....")
					good_power += 1
				else:
					print(f"Failed: During {boot_mode} boot Switch perpetual ports power output NOT Equal to in service mode")
					bad_power += 1
			
			if good >= 1 and bad <= 2:
				result1 = True 
			else:
				result1 = False

			if good_power>= 1 and bad_power<=2: 
				result2 = True 
			else:
				result2 = False

			result = result1 & result2

			if result == False and "bios" not in boot_mode:
				print_double_line()
				print(f"Failed: During switch {boot_mode} boots, POE Perpetual ports are not working")
				print(f"Switch critical Perpetual ports = {critical}")
				print(f"Switch high Perpetual Fast ports = {high}")
				print(f"Switch low Perpetual Fast ports = {low}")
				print(f"POE Tester ports received power = {ppoe_list_tester}")
				print_double_line()
				return result
			elif result == True and "bios" not in boot_mode:
				console_timer(120,msg=f"{boot_mode} boot testing passed, wait for 120s for a final check ")
				output_list = tester.get_poe_command(cmd="status")
				output_dict = tester.parse_status_output(output_list)
				print(output_dict)

				ppoe_list_tester = find_poe_status(output_dict)
				all_poe_ports.sort()
				ppoe_list_tester.sort()
				print(all_poe_ports,ppoe_list_tester)

				print_double_line()
				if critical != ppoe_list_tester:
					print(f"Failed: After {boot_mode} Boot, Switch critical perpetual ports list NOT Equal to All POE Tester list")
					result = False
					return result
				
				poe_inline_after = sw.get_poe_inline()
				delta = compare_poe_inline(poe_inline_before, poe_inline_after)
				for k,v in delta.items():
					if k == "Priority" or k =="Class" or k=="State":
						compare_result = False
					else:
						compare_result = True
				if compare_result:
					print(f"Successul: finished #{j+1} round of {boot_mode} priority testing")
					print(f"poe_inline_before: {poe_inline_before}")
					print(f"poe_inline_after:{poe_inline_after}")
					print(delta)
				else:
					print(f"Failed: get switch poe inline is different between {boot_mode} boot")
					print(delta)
					print(f"poe_inline_before: {poe_inline_before}")
					print(f"poe_inline_after:{poe_inline_after}")
				print_double_line()

			elif result == True and "bios" in boot_mode:
				console_timer(20,msg=f"wait for 20s and reboot from BIOS...")
				sw.reboot_bios()
				console_timer(180,msg=f"wait for 180s for a final check.....")
				output_list = tester.get_poe_command(cmd="status")
				output_dict = tester.parse_status_output(output_list)
				print(output_dict)

				ppoe_list_tester = find_poe_status(output_dict)
				all_poe_ports.sort()
				ppoe_list_tester.sort()
				print(all_poe_ports,ppoe_list_tester)

				print_double_line()
				if all_poe_ports != ppoe_list_tester:
					print("Failed: After Boot from BIOS, Switch perpetual ports list NOT Equal to All POE Tester list")
					result = False
				else:
					print(f"{result}: finished #{j+1} round of basic BIOS testing")
				print_double_line()
				pass
			elif result == False and "bios" in boot_mode:
				print_double_line()
				print(f"Failed: During switch {boot_mode} boots, POE Perpetual ports are not working")
				print(f"Switch critical Perpetual ports = {critical}")
				print(f"Switch high Perpetual Fast ports = {high}")
				print(f"Switch low Perpetual Fast ports = {low}")
				print(f"POE Tester ports received power = {ppoe_list_tester}")
				print_double_line()
				console_timer(20,msg=f"wait for 20s and reboot from BIOS...")
				sw.reboot_bios()
				console_timer(180,msg=f"wait for 180s for switch to boot up.....")
				return result

		return result

	################################# none_ppoe_priority_power_testing: low priority port perpetual ################################
	def none_ppoe_priority_power_testing(*args, **kwargs):
		if "boot" in kwargs:
			boot_mode = kwargs['boot']
		else: 
			boot_mode = "warm"
		if boot_mode == "cold":
			p_mode = "perpetual-fast"
		elif boot_mode == "bios":
			p_mode = "perpetual-fast"
		else:
			p_mode = "perpetual"

		if "poe_status" in kwargs:
			poe_status = kwargs['poe_status']
		else:
			poe_status = "enable"

		print_double_line()
		print(f"				none_ppoe_priority_power_testing in {boot_mode}	boot	")
		print_double_line()

		if "iteration" in kwargs:
			run_numbers = iteration
		else:
			run_numbers = 1

		 
		all_poe_ports = port_list
		for j in range(run_numbers):
			critical,high,low = partition(port_list,3)

			 
			print(f"Critical High Priority Ports = {critical}")
			print(f"High Priority Ports = {high}")
			print(f"Low Priority Ports = {low}")
			##############################################
			# Configure DUT POE ports before test starts
			##############################################
			begin = True
			for p in critical:
				config = f"""
				config switch physical-port
	    			edit port{p}
	         		unset poe-port-power  
	         		set poe-port-priority critical-priority
	         		set poe-status {poe_status}
	    			next
				end
				"""
				config_cmds_lines(sw.console,config,check_prompt=begin)	
				if begin == True:
					begin = False
			for p in high:
				config = f"""
				config switch physical-port
	    			edit port{p}
	         		unset poe-port-power 
	         		set poe-port-priority high-priority
	         		set poe-status {poe_status}
	    			next
				end
				"""
				config_cmds_lines(sw.console,config)

			for p in low:
				config = f"""
				config switch physical-port
	    			edit port{p}
	         		set poe-port-power {p_mode}
	         		set poe-port-priority low-priority
	         		set poe-status {poe_status}
	    			next
				end
				"""
				config_cmds_lines(sw.console,config)

			config = f"""
			conf switch global
			set poe-power-budget 70
			set poe-power-mode priority
			end
			"""
			config_cmds_lines(sw.console,config)

			sleep(20)

			sw.show_command("diagnose hardware sysinfo bootenv")
			sw.show_command("get switch poe inline")
			##############################################
			#  Setup POE tester before test starts
			##############################################
			tester.poe_reset(current=350,poe_class=4)
			sleep(5)
			output_list = tester.get_poe_command(cmd="status")
			output_dict = tester.parse_status_output(output_list)
			print(output_dict)

			poe_inline_before = sw.get_poe_inline()

			result = True
			
			testing_ports = critical
			ppoe_list_tester = find_poe_status(output_dict)
			testing_ports.sort()
			ppoe_list_tester.sort()
			print(testing_ports,ppoe_list_tester)

			print_double_line()

			if testing_ports != ppoe_list_tester:
				print(f"Failed: Before {boot_mode} Boot, critical POE ports list is NOT Equal to POE Tester list")
				result = False
				return result
			else:
				print(f"Before {boot_mode} Boot, critical POE ports list is Equal to POE Tester list, Continue.....")
			print_double_line()

			output_list = tester.get_poe_command(cmd="measure")
			service_power_dict = tester.parse_measure_output(output_list)
			print(f"power output in service:{service_power_dict}")
			##############################################
			#  Warm or Cold Boot Switch & check POE Tester
			##############################################
			if boot_mode == "warm":
				sw.switch_reboot()
			if boot_mode == "cold":
				sw.pdu_cycle()
			if boot_mode == "bios":
				sw.pdu_cycle_bios()
				sleep(10)

			good = 0
			bad = 0
			print_double_line()
			for i in range(5):
				tester.poe_reset(current=350,poe_class=4) #set current = 250, output = 55*350 = 19W
				sleep(10)
				output_list = tester.get_poe_command(cmd="status")
				output_dict = tester.parse_status_output(output_list)
				print(output_dict)
				ppoe_list_tester = find_poe_status(output_dict)
				sleep(2)
				output_list = tester.get_poe_command(cmd="measure")
				boot_power_dict = tester.parse_measure_output(output_list)
				print(f"power output in booting:{boot_power_dict}")
				
				p_poe_ports = low
				 
				ppoe_list_tester.sort()
				p_poe_ports.sort()
				print(f"Boot Mode = {boot_mode}. POE Tester ports = {ppoe_list_tester}. Switch perpetual POE ports = {p_poe_ports}, Switch PoE ports = {all_poe_ports}" )

				poe_init_state = False
				if ppoe_list_tester == p_poe_ports:
					poe_init_state = True
					good +=1
					print(f"Sucess: Switch has {boot_mode} booted up, the POE Tester powered ports is Equal to All Switch POE port, Continue looping....")
				elif ppoe_list_tester == testing_ports:
					print(f"Final check good:Switch has finished {boot_mode} boot, power deleivered to critical high none perpetual modes")
					break
				elif ppoe_list_tester != p_poe_ports and poe_init_state == True:
					print(f"Switch is starting to boot up, exiting!")
					break
				else:
					print(f"Bad: During {boot_mode} boot, Switch perpetual ports list NOT Equal to POE Tester list, continue!")
					bad +=1 

			if good >=1 and bad <= 2:
				result = True 
			else:
				result = False


			if result == False and boot_mode != "bios":
				print_double_line()
				print(f"Failed: During switch {boot_mode} boots, POE Perpetual ports are not working: low priority perpetual ports no power")
				print(f"Switch critical Perpetual ports = {critical}")
				print(f"Switch high Perpetual Fast ports = {high}")
				print(f"Switch low Perpetual Fast ports = {low}")
				print(f"POE Tester ports received power = {ppoe_list_tester}")
				print_double_line()
				return result
			elif result == True and boot_mode != "bios":
				console_timer(120,msg=f"{boot_mode} boot testing passed, wait for 120s for a final check ")
				output_list = tester.get_poe_command(cmd="status")
				output_dict = tester.parse_status_output(output_list)
				print(output_dict)

				ppoe_list_tester = find_poe_status(output_dict)
				all_poe_ports.sort()
				ppoe_list_tester.sort()
				print(all_poe_ports,ppoe_list_tester)

				print_double_line()
				if critical != ppoe_list_tester:
					print(f"Failed: After {boot_mode} Boot, Switch critical perpetual ports list NOT Equal to All POE Tester list")
					result = False
					return result

				print(f"{result}: finished #{j+1} round of testing after {boot_mode}, comparing other POE characteristics between boot")
				poe_inline_after = sw.get_poe_inline()
				delta = compare_poe_inline(poe_inline_before, poe_inline_after)
				if delta == {}:
					compare_result = True
				else:
					for k,v in delta.items():
						if k == "Priority" or k =="Class" or k=="State":
							compare_result = False
						else:
							compare_result = True

				if compare_result:
					print(f"Successul: finished #{j+1} round of {boot_mode} priority testing")
					print(f"poe_inline_before: {poe_inline_before}")
					print(f"poe_inline_after:{poe_inline_after}")
					print(delta)
				else:
					print(f"Failed: get switch poe inline is different between {boot_mode} boot")
					print(delta)
					print(f"poe_inline_before: {poe_inline_before}")
					print(f"poe_inline_after:{poe_inline_after}")
				print_double_line()

			elif result == True and boot_mode == "bios":
				console_timer(20,msg=f"wait for 20s and reboot from BIOS...")
				sw.reboot_bios()
				console_timer(180,msg=f"wait for 180s for a final check.....")
				output_list = tester.get_poe_command(cmd="status")
				output_dict = tester.parse_status_output(output_list)
				print(output_dict)

				ppoe_list_tester = find_poe_status(output_dict)
				all_poe_ports.sort()
				ppoe_list_tester.sort()
				print(all_poe_ports,ppoe_list_tester)

				print_double_line()
				if critical != ppoe_list_tester:
					print("Failed: After Boot from BIOS, Switch perpetual ports list NOT critical POE Tester list")
					result = False
					return result
				 
				print(f"{result}: finished #{j+1} round of basic BIOS testing, comparing other POE characteristics between boot")				
				poe_inline_after = sw.get_poe_inline()
				delta = compare_poe_inline(poe_inline_before, poe_inline_after)
				for k,v in delta.items():
					if k == "Priority" or k =="Class" or k=="State":
						compare_result = False
					else:
						compare_result = True
				if compare_result:
					print(f"Successul: finished #{j+1} round of {boot_mode} priority testing")
					print(f"poe_inline_before: {poe_inline_before}")
					print(f"poe_inline_after:{poe_inline_after}")
					print(delta)
				else:
					print(f"Failed: get switch poe inline is different between {boot_mode} boot")
					print(delta)
					print(f"poe_inline_before: {poe_inline_before}")
					print(f"poe_inline_after:{poe_inline_after}")
				print_double_line()

			elif result == False and boot_mode == "bios":
				print_double_line()
				print(f"Failed: During switch {boot_mode} boots, POE Perpetual ports are not working")
				print(f"Switch critical Perpetual ports = {critical}")
				print(f"Switch high Perpetual Fast ports = {high}")
				print(f"Switch low Perpetual Fast ports = {low}")
				print(f"POE Tester ports received power = {ppoe_list_tester}")
				print_double_line()
				console_timer(20,msg=f"wait for 20s and reboot from BIOS...")
				sw.reboot_bios()
				console_timer(180,msg=f"wait for 180s for switch to boot up.....")
				return result

		return result

	while True:
		debug_turn_on_poe_testing(1)
		#power_buget_testing(iteration = 4)
		# flipping_poe_boot_testing()
		# sleep(180)
		# poe_cli_testing(boot="cold")
		# sleep(180)
		# poe_cli_testing(boot="bios")
		# sleep(180)
		# poe_cli_testing()
		# sleep(180)

		# basic_bios_poe_boot_testing()
		# sleep(180)
		# basic_poe_boot_testing(boot="warm")
		# sleep(180)
		# basic_poe_boot_testing(boot="cold")	
		# sleep(180)
		# basic_poe_boot_testing(boot="warm",poe_status="disable")
		# sleep(180)

		# basic_poe_boot_testing(boot="bios")
		# sleep(180)
		# basic_poe_boot_testing(boot="warm_bios")
		# sleep(180)

		# none_ppoe_priority_power_testing(boot="warm")
		# sleep(180)
		# none_ppoe_priority_power_testing(boot="cold")
		# sleep(180)

		# priority_power_testing(boot="bios")
		# sleep(180)
		# priority_power_testing(boot="warm_bios")
		# sleep(180)
		# priority_power_testing(boot="warm")
		# sleep(180)
		# priority_power_testing(boot="cold")
		# sleep(180)

	
	# compare_power_testing(boot="warm")
	# sleep(180)
	# compare_power_testing(boot="cold")
	