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



if __name__ == "__main__":

	sys.stdout = Logger("Log/fortilink_perf_Auto_Module.log")
	
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
	file = 'tbinfo_fortilink.xml'
	tb = parse_tbinfo_untangle(file)
	testtopo_file = 'topo_fortilink_automodule.xml'
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
		elif d.type == "FGT" and d.active == True and d.role == "FGT_Active-1":
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

	for fgt in fortigates:
		if fgt.mode == "Active":
			fgt_active = fgt
			fgta = fgt # build another easy alias
		else:
		 	fgt_passive = fgt
		 	fgtp = fgt


	#fortilink_name = "Myswitch"
	fortilink_name = "Myfortilink"

	########################### FTG and FSW discoveries, many things need to disvoer here######
	#discover managed switches. updated some information such ftg console in each switch.
	managed_sw_list = fgta.discover_managed_switches(topology=tb)

	for sw in switches:
		sw.sw_network_discovery()
		print_attributes(sw)

	for fgt in fortigates:
		print_attributes(fgt)

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


	if upgrade_fgt:
		v,b = sw_build.split('-')
		for sw in switches:
			if sw.tier == None:
				continue
			tprint(f"========  Upgrading SW on Tier{sw.tier}: {sw.name}({sw.hostname}) to version:{v} build {b} ============\n")
			sw.ftg_sw_upgrade_no_wait(build=b,version=v,tftp_server="10.105.252.120")
			console_timer(400,msg=f"Wait for 400s after starting to upgrade {sw.name}({sw.hostname}) ")
		 
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

		# Discover LLDP neighbors of fortigates
		for fgt in fortigates:
			fgt.fgt_network_discovery()

		#Configure FW HA 
		for fgt in fortigates:
			fgt.config_ha()

		#Configure default policy to allow all traffic 
		for fgt in fortigates:
			if fgt.mode == "Active":
				fgt.config_default_policy()

		for fgt in fortigates:
			fgt.ha_sync(action="start")

		console_timer(100,msg='configuring firewall policy and sync, wait for 100 seconds')
         
		fortilink_name = "Myfortilink"
		addr = f"192.168.1.1 255.255.255.0"
		for fgt in fortigates:
			fgt.config_fortilink(name=fortilink_name,ip_addr=addr)
			#fgt.config_fortilink_switch()

		for fgt in fortigates:
			fgt.ha_sync(action="start")

		console_timer(600,msg='After configuring FSW and FGT, wait for 10 minutes for network to discover topology')

		for fgt in fortigates:
			if fgt.mode == "Active":
				fgt_active = fgt
			else:
			 	fgt_passive = fgt
	
		for sw in switches:
			sw.switch_reboot()
		console_timer(600,msg='After switches are rebooted, wait for 600 seconds')

		for sw in switches:
			print_attributes(sw)
		for fgt in fortigates:
			print_attributes(fgt)

		#fgt_active.fgt_relogin()
		managed_sw_list = fgt_active.discover_managed_switches(topology=tb)
		#fgt_active.config_custom_timeout()
		fgt_active.config_switch_custom_cmds()

		for sw in managed_sw_list:
			sw.print_managed_sw_info()
			if sw.authorized and sw.up:
				print(f"{sw.switch_id} is authorized and Up")
				fgt_active.execute_custom_command(switch_name=sw.switch_id,cmd="timeout")
				fgt_active.execute_custom_command(switch_name=sw.switch_id,cmd="console_output")
			else:
				print(f"{sw.switch_id} is Not authorized or Not up. Authorized={sw.authorized}, Up={sw.up}")

		#Configure mclag_icl links
		fgt_active.config_msw_mclag_icl()

		console_timer(400,msg='After configuring MCLAG ICL LLDP Profile via Fortigate, wait for 400 seconds for network to discover topology')

		#Configure auto isl port group
		for sw in switches:
			#sw.sw_relogin()
			sw.config_auto_isl_port_group()
		
		console_timer(400,msg='After configuring all Fortigte related stuff, wait for 400 seconds for network to discover topology')
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
		fgt_active.config_ftg_ixia_port(port=fgt_active.ixia_ports[0],ip="172.168.1.1",mask="255.255.255.0",dhcp_start="172.168.1.2",dhcp_end="172.168.1.254")
		if testcase == 0:
			print("Set up only, Wait for 400 seconds and exit.....")
			console_timer(600,msg='After configuring everything, wait for 400 seconds for network to discover topology')
			exit(0)
		else:
			console_timer(600,msg='After configuring everything, wait for 400 seconds for network to discover topology')
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


	
	

	###########################################################################################

	# for sw in switches:
	# 	sw.ftg_sw_upgrade(build=55,version='v7',tftp_server="10.105.252.120")
	# 	exit()

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
		myixia.start_protocol(wait=20)

		for i in range(0,len(tb.ixia.port_active_list)-1):
			for j in range(i+1,len(tb.ixia.port_active_list)):
				myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=1)
				myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=1)

		myixia.start_traffic()
		myixia.collect_stats()
		myixia.check_traffic()
		myixia.stop_traffic()

	myixia.start_traffic()

	################################# repeated test steps ################################
	def reboot_testing():
		for sw in switches:
			## !!! Need to change to == None
			if sw.tier == None:
			#if sw.tier != 3:
				continue
			test_log.write(f"========   Performance on Reboot Testing on Tier{sw.tier}: {sw.name}({sw.hostname}) ============\n")
			sw.print_show_interesting("diagnose switch mclag icl","dormant candidate","split-brain",logger=test_log)
			sw.print_show_command("diag switch trunk summary")
			sw.print_show_command("diag switch trunk list")
			myixia.clear_stats()
			sw.switch_reboot()
			console_timer(30,msg=f"After rebooting switch, wait for 30s and log traffic stats")
			myixia.collect_stats()
			for flow in myixia.flow_stats_list:
				test_log.write(f"Loss Time rebooting Tier{sw.tier}:{sw.name}-{sw.hostname} ===>{flow['Flow Group']}: {flow['Loss Time']}\n")

			#console_timer(20,msg=f"After rebooting , wait for 20s before measuring stats while device reboots")

			myixia.clear_stats()
			console_timer(360,msg=f"After rebooting, wait for 360s and log traffic stats")
			myixia.collect_stats()
			for flow in myixia.flow_stats_list:
				test_log.write(f"Loss Time restore from reboot Tier{sw.tier}:{sw.name}-{sw.hostname} ===> {flow['Flow Group']}: {flow['Loss Time']}\n")
				
	def power_cycle_testing():
		for sw in switches:
			if sw.tier == None:
				continue
			test_log.write(f"========   Performance on Power Cycle Testing on Tier{sw.tier}: {sw.name}({sw.hostname}) ============\n")
			sw.print_show_interesting("diagnose switch mclag icl","dormant candidate","split-brain",logger=test_log)
			myixia.clear_stats()
			sw.pdu_cycle()
			console_timer(10,msg=f"After power cycle switch, wait for 10s and log traffic stats")
			myixia.collect_stats()
			for flow in myixia.flow_stats_list:
				test_log.write(f"Loss Time power cycle Tier{sw.tier}:{sw.name}-{sw.hostname} ===>{flow['Flow Group']}: {flow['Loss Time']}\n")

			#console_timer(20,msg=f"After rebooting , wait for 20s before measuring stats while device reboots")
			myixia.clear_stats()
			console_timer(360,msg=f"After power cycle, wait for 360s and log traffic stats")
			myixia.collect_stats()
			for flow in myixia.flow_stats_list:
				test_log.write(f"Loss Time restore from power cycle Tier{sw.tier}:{sw.name}-{sw.hostname} ===> {flow['Flow Group']}: {flow['Loss Time']}\n")
				

	def icl_testing():
		for sw in switches:
			if len(sw.icl_links) > 0:
				test_log.write(f"======== Shut/Unshut ICL Testing on Tier{sw.tier}: {sw.name}({sw.hostname}) ========\n")
				sw.print_show_interesting("diagnose switch mclag icl","dormant candidate","split-brain",logger=test_log)
				myixia.clear_stats()
				for port in sw.icl_links:
					sw.shut_port(port)
				console_timer(10,msg=f"After shutting ICL port {port}, wait for 10s and log traffic stats")
				try:
					myixia.collect_stats()
					for flow in myixia.flow_stats_list:
						test_log.write(f"Loss Time shutting ICL ports at Tier{sw.tier}:{sw.name}-{sw.hostname} ===>{flow['Flow Group']}:{flow['Loss Time']}\n")
				except Exception as e:
					tprint("Something is wrong in collecting traffic stats, try it again in 10 seconds.......")
					sleep(10)
					myixia.collect_stats()
					for flow in myixia.flow_stats_list:
						test_log.write(f"Loss Time shutting ICL ports at Tier{sw.tier}:{sw.name}-{sw.hostname} ===> {flow['Flow Group']}:{flow['Loss Time']}\n")
				#console_timer(30,msg=f"After shutting ICL port {port}, wait for 30s before unshut ICL ports")
				sw.print_show_interesting("diagnose switch mclag icl","dormant candidate","split-brain",logger=test_log)
				myixia.clear_stats()
				for port in sw.icl_links:
					sw.unshut_port(port)
				console_timer(10,msg=f"After unshutting ICL port {port}, wait for 10s and log traffic stats")
				myixia.collect_stats()
				for flow in myixia.flow_stats_list:
					test_log.write(f"Loss Time unshutting ICL ports at Tier{sw.tier}:{sw.name}-{sw.hostname} ===> {flow['Flow Group']}:{flow['Loss Time']}\n")

				console_timer(300,msg=f"After shut/unshut ICL at one switch wait for 300s for ICL to recover")

	def upgrade_testing(*args,**kwargs):
		for sw in switches:
			if sw.tier == None:
				continue
			if sw.tier > 1: #Only test tier#1 switches upgrade
				return

			cmds = f"""
			conf switch physical-port
				edit port49
					set speed {kwargs['speed']}
				end
			"""
			config_cmds_lines(sw.console,cmds)

		sleep(10)

		for sw in switches:
			if sw.tier == None:
				continue
			if sw.tier > 1: #Only test tier#1 switches upgrade
				return
			test_log.write(f"========   Performance on Upgrade Testing on Tier{sw.tier}: {sw.name}({sw.hostname}) ============\n")
			sw.print_show_interesting("show switch physical-port port49","speed",logger=test_log)
			myixia.clear_stats()
			sw.ftg_sw_upgrade_no_wait(build=55,version='v7',tftp_server="10.105.252.120")
			console_timer(60,msg=f"After start upgrading switch, wait for 30s and log traffic stats")
			myixia.collect_stats()
			for flow in myixia.flow_stats_list:
				test_log.write(f"Loss Time upgrading Tier{sw.tier}:{sw.name}-{sw.hostname} ===>{flow['Flow Group']}: {flow['Loss Time']}\n")

			#console_timer(20,msg=f"After rebooting , wait for 20s before measuring stats while device reboots")
			myixia.clear_stats()
			console_timer(360,msg=f"After rebooting, wait for 360s and log traffic stats")
			myixia.collect_stats()
			for flow in myixia.flow_stats_list:
				test_log.write(f"Loss Time restore from upgrading Tier{sw.tier}:{sw.name}-{sw.hostname} ===> {flow['Flow Group']}: {flow['Loss Time']}\n")
			console_timer(360,msg=f"After upgrading one switch, wait for 360s to start another switch upgrade")


	cmds = f"""
	conf vdom
	edit root
			config switch-controller  managed-switch
				edit S548DF4K16000653
					config ports
						edit port49
						set speed auto-module
					end

				next
			edit S548DN4K17000133
					config ports
					edit port49
					set speed auto-module
					end
				end
		end
	"""
	config_cmds_lines(fgta.console,cmds)
	console_timer(300,msg=f"After configuring speed auto-module, wait for 300s ")
	cmds = f"""
	conf vdom
	edit root
			config switch-controller  managed-switch
				edit S548DF4K16000653
					config ports
						edit port49
						show
					end

				next
			edit S548DN4K17000133
					config ports
					edit port49
						show
					end
				end
		end
	"""
	config_cmds_lines(fgta.console,cmds)
	for i in range(1,3):
		test_log = Logger(f"Log/perf_automodule_{i}.log")
		################################# Port speed Auto-Module vs 10000sr Testing ########################## 

		test_log.write(f"===========================================================================================\n")
		test_log.write(f"					Test#{i}:Use Speed Automodule for two Tier#1 switches 			\n")
		test_log.write(f"===========================================================================================\n")
		 
		upgrade_testing(speed="auto-module")

	cmds = f"""
	conf vdom
	edit root
			config switch-controller  managed-switch
				edit S548DF4K16000653
					config ports
						edit port49
						set speed 10000sr
					end

				next
			edit S548DN4K17000133
					config ports
					edit port49
					set speed 10000sr
					end
				end
		end
	"""
	config_cmds_lines(fgta.console,cmds)
	console_timer(300,msg=f"After configuring speed 10000sr, wait for 300s ")
	cmds = f"""
	conf vdom
	edit root
			config switch-controller  managed-switch
				edit S548DF4K16000653
					config ports
						edit port49
						show
					end

				next
			edit S548DN4K17000133
					config ports
					edit port49
						show
					end
				end
		end
	"""
	config_cmds_lines(fgta.console,cmds)

	for i in range(1,3):
		test_log = Logger(f"Log/perf_10KSR_{i}.log")
		################################# Port speed Auto-Module vs 10000sr Testing ########################## 

		test_log.write(f"===========================================================================================\n")
		test_log.write(f"					 Test#{i}:Use Speed 10000sr for two Tier#1 switches 			\n")
		test_log.write(f"===========================================================================================\n")
		 
		upgrade_testing(speed="10000sr")

	
	exit(0)

	 
		# ####################################### Enable Slit-brin-detect/No Shut ports Perf Testing ###########################
		# index = 0
		# for sw in switches:
		# 	if sw.tier == None:
		# 		continue
		# 	appendex = index%2
		# 	config = f"""
		# 	config switch global
		# 	set  mclag-split-brain-detect enable
		# 	set mclag-split-brain-priority {int(sw.tier)*10 + appendex}
		# 	end
		# 	"""
		# 	config_cmds_lines(sw.console,config)
		# 	index += 1
		# console_timer(300,msg=f"After enabling split-brain-detect, wait for 300s ")
		# test_log.write(f"============================================================================================================\n")
		# test_log.write(f"				Enable split-brian-detect/Disable shut ports.  			\n")
		# test_log.write(f"=============================================================================================================\n")
		# console_timer(300,msg=f"After enabling split-brain without shut-down ports wait for 300s to start testing")
		# power_cycle_testing()
		# upgrade_testing()
		# reboot_testing()
		# icl_testing()

		# ###################################### Enable Slit-brin-detect/Enable Shut ports ###########################
		# index = 0
		# for sw in switches:
		# 	if sw.tier == None:
		# 		continue
		# 	appendex = index%2
		# 	config = f"""
		# 	config switch global
		# 	set mclag-split-brain-all-ports-down enable
		# 	end
		# 	"""
		# 	config_cmds_lines(sw.console,config)
		# 	index += 1
		# console_timer(300,msg=f"After enabling split-brain-detect, wait for 300s ")
		# test_log.write(f"============================================================================================================\n")
		# test_log.write(f"		 Enable split-brian-detect/ Enable shut-ports 			\n")
		# test_log.write(f"=============================================================================================================\n")
		# console_timer(300,msg=f"After enabling split-brain without shut-down ports wait for 300s to start testing")
		# power_cycle_testing()
		# upgrade_testing()
		# reboot_testing()
		# icl_testing()