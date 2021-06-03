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

from utils import *
#import settings 
from test_process import * 
from common_lib import *
from common_codes import *
from cli_functions import *
from device_config import *
from protocols_class import *
from ixia_restpy_lib_v2 import *



if __name__ == "__main__":

	sys.stdout = Logger("Log/fortilink_system.log")
	parser = argparse.ArgumentParser()
	parser.add_argument("-c", "--config", help="Configure switches before starting testing", action="store_true")
	parser.add_argument("-m", "--maintainence", help="Bring switches into standalone for maintainence", action="store_true")
	parser.add_argument("-test", "--testcase", type=str, help="Specific which test case you want to run. Example: 1/1-3/1,3,4,7 etc")
	parser.add_argument("-b", "--boot", help="Perform reboot test", action="store_true")
	parser.add_argument("-f", "--factory", help="Run the test after factory resetting all devices", action="store_true")
	parser.add_argument("-v", "--verbose", help="Run the test in verbose mode with amble debugs info", action="store_true")
	parser.add_argument("-s", "--setup_only", help="Setup testbed and IXIA only for manual testing", action="store_true")
	parser.add_argument("-i", "--interactive", help="Enter interactive mode for test parameters", action="store_true")
	parser.add_argument("-ug", "--sa_upgrade", type = str,help="FSW software upgrade in standlone mode. For debug image enter -1. Example: v6-193,v7-5,-1(debug image)")
	parser.add_argument("-fg", "--fgt_upgrade", type = str,help="Fortigate software upgrade. For debug image enter -1. Example: v6-193,v7-5,-1(debug image)")


	global DEBUG
	initial_testing = False
	
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

	if args.setup_only:
		Setup_only = True
		print_title("Set up Only:Yes")
	else:
		Setup_only = False
		print_title("Set up Only:No")
	file = 'tbinfo_fortilink.xml'
	tb = parse_tbinfo_untangle(file)
	testtopo_file = 'fortilink_topo.xml'
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
		elif d.type == "FGT" and d.active == True:
			fgt = FortiGate_XML(d,topo_db=tb)
			fortigates.append(fgt)
			devices.append(fgt)
		else:
			pass

	for c in tb.connections:
		c.update_devices_obj(devices)

	tb.switches = switches
	tb.fortigates = fortigates

	# for c in tb.connections:
	# 	c.shut_unused_ports()


	##################################### Pre-Test setup and configuration #############################

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


	if upgrade_fgt:
		for fgt in fortigates:
			v,b = sw_build.split('-')
			result = fgt.fgt_upgrade_v2(build=b,version=v)
			if not result:
				tprint(f"############# Upgrade {fgt.name} to build #{sw_build} Fails ########### ")
			else:
				tprint(f"############# Upgrade {fgt.name} to build #{sw_build} is successful ############")

		console_timer(400,msg="Wait for 400s after started upgrading all switches")
		for fgt in fortigates:
			dut = fgt.console
			dut_name = fgt.name
			fgt.fgt_relogin()

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
		for fgt in fortigates:
			#print_attributes(fgt)
			fgt.change_fortilink_ports(state="up")

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
		################ Will be uncommented this blocks
		for sw in switches:
			sw.switch_factory_reset()

		console_timer(600,msg='After switches are factory reset, wait for 600 seconds')

		for sw in switches:
			sw.sw_relogin()
			dut = sw.console
			dut_name = sw.name
			image = find_dut_image(dut)
			tprint(f"============================ {dut_name} software image = {image} ============")
			sw.sw_network_discovery()
			sw.config_lldp_profile_auto_isl()
		#console_timer(100,msg='After switches are factory reset and configure lldp profile auto_isl, wait for 100 seconds')
		#################
		for fgt in fortigates:
			fgt.fgt_factory_reset()
		console_timer(400,msg='After fortigates are factory reset, wait for 400 seconds')
		for fgt in fortigates:
			fgt.fgt_relogin()
			fgt.config_after_factory()

		console_timer(200,msg='After FGT intial configuration, wait for 200 seconds and discover network topology')

		for fgt in fortigates:
			fgt.fgt_network_discovery()

		for fgt in fortigates:
			fgt.config_ha()


		for fgt in fortigates:
			if fgt.mode == "Active":
				fgt.config_default_policy()

		for fgt in fortigates:
			fgt.ha_sync(action="start")

		console_timer(100,msg='configuring firewall policy and sync, wait for 100 seconds')
         
		fortilink_name = f"Myfortilink"
		addr = f"192.168.1.1 255.255.255.0"
		for fgt in fortigates:
			fgt.config_fortilink(name=fortilink_name,ip_addr=addr)

		for fgt in fortigates:
			fgt.ha_sync(action="start")

		console_timer(600,msg='After configuring FSW and FGT, wait for 10 minutes for network to discover topology')

		for fgt in fortigates:
			if fgt.mode == "Active":
				fgt_active = fgt
		############## Move this blocks to the beginning later ############################
		# for sw in switches:
		# 	sw.switch_factory_reset()

		# console_timer(600,msg='After switches are factory reset, wait for 600 seconds')

		
		# for sw in switches:
		# 	sw.sw_relogin()
		# 	dut = sw.console
		# 	dut_name = sw.name
		# 	image = find_dut_image(dut)
		# 	tprint(f"============================ {dut_name} software image = {image} ============")
		# 	sw.sw_network_discovery()
		# 	sw.config_lldp_profile_auto_isl()
		# console_timer(500,msg='After switches are factory reset and configure lldp profile auto_isl, wait for 500 seconds')
		###########################################
		for sw in switches:
			sw.switch_reboot()
		console_timer(600,msg='After switches are rebooted, wait for 600 seconds')

		for sw in switches:
			print_attributes(sw)
		for fgt in fortigates:
			print_attributes(fgt)

		#fgt_active.fgt_relogin()
		managed_sw_list = fgt_active.discover_managed_switches(topology=tb)
		fgt_active.config_custom_timeout()
		for sw in managed_sw_list:
			sw.print_managed_sw_info()
			if sw.authorized and sw.up:
				print(f"{sw.switch_id} is authorized and Up")
				fgt_active.execute_custom_command(switch_name=sw.switch_id,cmd="timeout")
			else:
				print(f"{sw.switch_id} is Not authorized or Not up. Authorized={sw.authorized}, Up={sw.up}")

		fgt_active.config_msw_mclag_icl()

		console_timer(400,msg='After configuring MCLAG ICL LLDP Profile via Fortigate, wait for 400 seconds for network to discover topology')

		for sw in switches:
			#sw.sw_relogin()
			sw.config_auto_isl_port_group()
		exit()
		
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
	
	for fgt in fortigates:
		fgt.fgt_network_discovery()
		print_attributes(fgt)
	
	for sw in switches:
		sw.sw_network_discovery()
		print_attributes(sw)

	for sw in switches:
		sw.discover_switch_trunk()

	for fgt in fortigates:
		if fgt.mode == "Active":
			managed_sw_list = fgt.discover_managed_switches(topology=tb)
			fgt.config_custom_timeout()
			for sw in managed_sw_list:
				sw.print_managed_sw_info()
				if sw.authorized and sw.up:
					print(f"{sw.switch_id} is authorized and Up")
					fgt.execute_custom_command(switch_name=sw.switch_id,cmd="timeout")
				else:
					print(f"{sw.switch_id} is Not authorized or Not up. Authorized={sw.authorized}, Up={sw.up}")

	exit()
	apiServerIp = tb.ixia.ixnetwork_server_ip
	#ixChassisIpList = ['10.105.241.234']
	ixChassisIpList = [tb.ixia.chassis_ip]
 

	mac_list = ["00:11:01:01:01:01","00:12:01:01:01:01","00:13:01:01:01:01","00:14:01:01:01:01","00:15:01:01:01:01","00:16:01:01:01:01","00:17:01:01:01:01","00:18:01:01:01:01"]
	net4_list = ["10.1.1.211/24","10.1.1.212/24","10.1.1.213/24","10.1.1.214/24","10.1.1.215/24","10.1.1.216/24","10.1.1.217/24","10.1.1.218/24","10.1.1.219/24","10.1.1.220/24"]
	gw4_list = ["10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1"]
	net6_list = ["2001:10:1:1::211/64","2001:10:1:1::212/64","2001:10:1:1::213/64","2001:10:1:1::214/64","2001:10:1:1::215/64","2001:10:1:1::216/64","2001:10:1:1::217/64","2001:10:1:1::218/64"]
	gw6_list = ["2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1"]

	portList_v4_v6 = []
	for p,m,n4,g4,n6,g6 in zip(tb.ixia.port_active_list,mac_list,net4_list,gw4_list,net6_list,gw6_list):
		module,port = p.split("/")
		portList_v4_v6.append([ixChassisIpList[0], int(module),int(port),m,n4,g4,n6,g6,1])

	print(portList_v4_v6)

	myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)
	for topo in myixia.topologies:
		topo.add_dhcp_client()


	if initial_testing:
		myixia.start_protocol(wait=200)

		for i in range(0,len(tb.ixia.port_active_list)-1):
			for j in range(i+1,len(tb.ixia.port_active_list)):
				myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=1)
				myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=1)

		myixia.start_traffic()
		myixia.collect_stats()
		myixia.check_traffic()
		myixia.stop_traffic()

	if testcase == 1 or test_all:
		testcase = 1
		myixia.start_traffic()
		for sw in switches:
			for trunk in sw.trunk_list:
				config = f"""
				config switch trunk
					edit {trunk.name}
						set static-isl enable
					next 
					end
				"""
				config_cmds_lines(sw.console,config)
		console_timer(400,msg=f"Testcase #{testcase}:After enabling static-isl, wait for 20s")
		myixia.collect_stats()
		if myixia.check_traffic() == True:
			print(f"Test Case #{testcase} Passed: Enable static-isl")
		else:
			print(f"Test Case #{testcase} Failed: Enable static-isl")
		print_double_line()
		myixia.stop_traffic()

	if testcase == 2 or test_all:
		testcase = 2
		myixia.start_traffic()
		for sw in switches:
			for trunk in sw.trunk_list:
				config = f"""
				config switch trunk
					edit {trunk.name}
						set static-isl disable
					next 
					end
				"""
				config_cmds_lines(sw.console,config)
		console_timer(400,msg=f"Testcase #{testcase}:After disabling static-isl, wait for 20s")
		myixia.collect_stats()
		if myixia.check_traffic() == True:
			print(f"Test Case #{testcase} Passed: Disable static-isl")
		else:
			print(f"Test Case #{testcase} Failed: Disable static-isl")
		print_double_line()
		myixia.stop_traffic()


	if testcase == 3 or test_all:
		testcase = 3
		myixia.start_traffic()
		for sw in switches:
			for trunk in sw.trunk_list:
				config = f"""
				config switch trunk
					edit {trunk.name}
						set static-isl enable
						set static-isl-auto-vlan disable
					next 
					end
				"""
				config_cmds_lines(sw.console,config)
		console_timer(400,msg=f"Testcase #{testcase}:After enabling static-isl, wait for 20s")
		myixia.collect_stats()
		if myixia.check_traffic() == True:
			print(f"Test Case #{testcase} Passed: Enable static-isl and disable static-isl-auto-vlan")
		else:
			print(f"Test Case #{testcase} Failed: Enable static-isl and disable static-isl-auto-vlan")
		print_double_line()
		myixia.stop_traffic()

	if testcase == 4 or test_all:
		testcase = 4
		myixia.start_traffic()
		for sw in switches:
			for trunk in sw.trunk_list:
				config = f"""
				config switch trunk
					edit {trunk.name}
						set static-isl enable
						set static-isl-auto-vlan enable
					next 
					end
				"""
				config_cmds_lines(sw.console,config)
		console_timer(400,msg=f"Testcase #{testcase}:After enabling static-isl, wait for 20s")
		myixia.collect_stats()
		if myixia.check_traffic() == True:
			print(f"Test Case #{testcase} Passed: Enable static-isl and enable static-isl-auto-vlan")
		else:
			print(f"Test Case #{testcase} Failed: Enable static-isl and enable static-isl-auto-vlan")
		print_double_line()
		myixia.stop_traffic()

	if testcase == 5 or test_all:
		testcase = 5
		myixia.start_traffic()
		for sw in switches:
			for trunk in sw.trunk_list:
				config = f"""
				config switch trunk
					edit {trunk.name}
						set static-isl disable
						set static-isl-auto-vlan enable
					next 
					end
				"""
				config_cmds_lines(sw.console,config)
		console_timer(400,msg=f"Testcase #{testcase}:After Disable static-isl and enable static-isl-auto-vlan, wait for 20s")
		myixia.collect_stats()
		if myixia.check_traffic() == True:
			print(f"Test Case #{testcase} Passed: Disable static-isl and enable static-isl-auto-vlan")
		else:
			print(f"Test Case #{testcase} Failed: Disable static-isl and enable static-isl-auto-vlan")
		print_double_line()
		myixia.stop_traffic()

	if testcase == 6 or test_all:
		testcase = 6
		description = "Delete static ISL Trunk Test: delete static ISL trunk, reboot. System will create a dynamic trunk"
		print_test_subject(testcase,description)
		for sw in switches:
			if sw.role == "tier1-sw1":
				tier1_sw1 = sw
			elif sw.role == "tier1-sw2":
				tier1_sw2 = sw


		for trunk in tier1_sw1.trunk_list:
			tier1_sw1.show_command("show switch trunk")
			if "my" in trunk.name:
				config = f"""
				config switch trunk
					delete {trunk.name}
				end
				end
				"""
				config_cmds_lines(tier1_sw1.console,config)
				tier1_sw1.show_command("show switch trunk")
				tier1_sw1.reboot()
				break
		for trunk in tier1_sw2.trunk_list:
			tier1_sw2.show_command("show switch trunk")
			if "my" in trunk.name:
				config = f"""
				config switch trunk
					delete {trunk.name}
				end
				end
				"""
				config_cmds_lines(tier1_sw2.console,config)
				tier1_sw2.show_command("show switch trunk")
				tier1_sw2.reboot()
				break
			
		console_timer(300,msg=f"Testcase #{testcase}:After reboot devices, wait for 300s")
		tier1_sw1.switch_relogin()
		tier1_sw2.switch_relogin()

		tier1_sw1.show_command("show switch trunk")
		tier1_sw2.show_command("show switch trunk")

		myixia.start_protocol(wait=200)

		for i in range(0,len(tb.ixia.port_active_list)-1):
			traffic_list = []
			for j in range(i+1,len(tb.ixia.port_active_list)):
				traffic = myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=1)
				traffic_list.append(traffic)
				traffic = myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=1)
				traffic_list.append(traffic)
		myixia.start_traffic()

		console_timer(30,msg=f"Testcase #{testcase}:After start ixia traffic, wait for 30s")
		myixia.collect_stats()
		if myixia.check_traffic() == True:
			print(f"Test Case #{testcase} Passed: Delete static ISL trunk and reboot")
		else:
			print(f"Test Case #{testcase} Failed: Delete static ISL trunk and reboot")
		print_double_line()
		myixia.stop_traffic()
		myixia.stop_protocol()
		try:
			for traffic in traffic_list:
				traffic.remove()
		except Exception as e:
			ErrorNotify("Not able to remove traffic elements")

	if testcase == 7 or test_all:
		testcase = 7
		description = "Manually create static ISL Trunk Test: delete system created Fortilink Trunk, then manually created static ISL trunk"
		print_test_subject(testcase,description)
		for sw in switches:
			if sw.role == "tier1-sw1":
				tier1_sw1 = sw
			elif sw.role == "tier1-sw2":
				tier1_sw2 = sw


		for trunk in tier1_sw1.trunk_list:
			if "GT3KD" in trunk.name:
				config = f"""
				config switch trunk
					delete {trunk.name}
				end
				end
				"""
				config_cmds_lines(tier1_sw1.console,config)
				tier1_sw1.show_command("show switch trunk")

				config = f"""
				config switch trunk
					edit mytrunk
					set auto-isl 1
					 set fortilink 1
					 set mclag enable
					 set members {tier1_sw1.uplink_port}
					 set static-isl enable
					 end
				"""
				config_cmds_lines(tier1_sw1.console,config,wait=2)
				console_timer(10,msg=f"Testcase #{testcase}:After configuring static ISL manually on one device, wait for 10s")
				tier1_sw1.show_command("show switch trunk")
				break
		for trunk in tier1_sw2.trunk_list:
			if "GT3KD" in trunk.name:
				config = f"""
				config switch trunk
					delete {trunk.name}
				end
				end
				"""
				config_cmds_lines(tier1_sw2.console,config)
				tier1_sw2.show_command("show switch trunk")
				config = f"""
				config switch trunk
					edit mytrunk
					set auto-isl 1
					 set fortilink 1
					 set mclag enable
					 set static-isl enable
					 set members {tier1_sw2.uplink_port}
					 end
				"""
				config_cmds_lines(tier1_sw2.console,config,wait=2)
				console_timer(10,msg=f"Testcase #{testcase}:After configuring static ISL manually on one device, wait for 10s")
				tier1_sw2.show_command("show switch trunk")
				break
			
		console_timer(200,msg=f"Testcase #{testcase}:After configuring static ISL manually on all devices, wait for 200s")

		tier1_sw1.show_command("show switch trunk")
		tier1_sw2.show_command("show switch trunk")

		myixia.start_protocol(wait=200)

		for i in range(0,len(tb.ixia.port_active_list)-1):
			for j in range(i+1,len(tb.ixia.port_active_list)):
				myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=1)
				myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=1)

		myixia.start_traffic()

		console_timer(400,msg=f"Testcase #{testcase}:After Disable static-isl and enable static-isl-auto-vlan, wait for 20s")
		myixia.collect_stats()
		if myixia.check_traffic() == True:
			print(f"Test Case #{testcase} Passed: Disable static-isl and enable static-isl-auto-vlan")
		else:
			print(f"Test Case #{testcase} Failed: Disable static-isl and enable static-isl-auto-vlan")
		print_double_line()
		myixia.stop_traffic()
		myixia.stop_protocol()
		try:
			for traffic in traffic_list:
				traffic.remove()
		except Exception as e:
			ErrorNotify("Not able to remove traffic elements")

##################################################################################################################################################
##################################################################################################################################################