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
from test_process import *



if __name__ == "__main__":
	sys.stdout = Logger("Log/mem_cpu.log")
	parser = argparse.ArgumentParser()
	parser.add_argument("-c", "--config", help="Configure switches before starting testing", action="store_true")
	parser.add_argument("-test", "--testcase", type=str, help="Specific which test case you want to run. Example: 1/1-3/1,3,4,7 etc")
	parser.add_argument("-b", "--boot", help="Perform reboot test", action="store_true")
	parser.add_argument("-f", "--factory", help="Run the test after factory resetting all devices", action="store_true")
	parser.add_argument("-v", "--verbose", help="Run the test in verbose mode with amble debugs info", action="store_true")
	parser.add_argument("-s", "--setup_only", help="Setup testbed and IXIA only for manual testing", action="store_true")
	parser.add_argument("-i", "--interactive", help="Enter interactive mode for test parameters", action="store_true")
	parser.add_argument("-ug", "--sa_upgrade", type = str,help="FSW software upgrade in standlone mode. For debug image enter -1. Example: v6-193,v7-5,-1(debug image)")


	global DEBUG
	
	args = parser.parse_args()

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
				testcase_range = testcase.split("-")
				testcase_list = [i for i in range(int(testcase_range[0]),int(testcase_range[1]+1))]
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
	file = 'tbinfo_single_sw.xml'
	tb = parse_tbinfo_untangle(file)
	testtopo_file = 'single_sw_topo.xml'
	parse_testtopo_untangle(testtopo_file,tb)
	tb.show_tbinfo()

	######## skipping it for ixia trouble shooting
	switches = []
	for d in tb.devices:
		switch = FortiSwitch_XML(d,topo_db=tb)
		switches.append(switch)
	for c in tb.connections:
		c.update_devices_obj(switches)
	####### skipping it for ixia trouble shooting 
	# for c in tb.connections:
	# 	c.shut_unused_ports()


	##################################### Pre-Test setup and configuration #############################
	if upgrade_sa:
		for sw in switches:
			v,b = sw_build.split('-')
			result = sw.fsw_upgrade(build=b,version=v)
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
			config = """
			config system interface
				edit "vlan1"
				    set ip 10.1.1.1 255.255.255.0
				            config ipv6
				                set ip6-address 2001:10:1:1::1/64
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
			switch_exec_reboot(dut,device=dut_name)

		console_timer(400,msg="Wait for 400s after started rebooting all switches")
		for sw in switches:
			dut = sw.console
			dut_name = sw.name
			sw.switch_relogin()
			image = find_dut_image(dut)
			tprint(f"============================ {dut_name} software image = {image} ============")

		# if testcase == 0:
		# 	exit()
	lw_old_dict = {}
	# while True:
	# 	for sw in switches:
	# 		tprint(f"---------------------------------- cpu-memory-iostats: {sw.name} --------------------------------------")
	# 		try:
	# 			result = loop_command_output(sw.console,"fnsysctl top")
	# 		except (BrokenPipeError,EOFError,UnicodeDecodeError) as e:
	# 			debug(f"Having problem to collect fnsysctl top command on {sw.name}")
	# 			continue

	# 		#sw.fsw_show_cmd("diagnose test application fpmd 1")
	# 		lw_list = sw.fsw_show_cmd("fnsysctl ps -lw")
	# 		lw_current_dict = sw.sw_fnsysctl_process(lw_list)
	# 		if bool(lw_old_dict):
	# 			for k,v in lw_current_dict.items():
	# 				if lw_old_dict[k] < lw_current_dict[k]:
	# 					print(f"Potential memory leak | {k}: before ={lw_old_dict[k]}, now = {v}")
	# 				else:
	# 					print(f"No memory leak | {k}: before ={lw_old_dict[k]}, now = {v}")
	# 		lw_old_dict = lw_current_dict
	# 		# sw.fsw_show_cmd("diagnose switch physical-ports io-stats cumulative")
	# 	sleep(300)
	# 	print_double_line()
	
	sw = switches[0]
	
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

	initial_testing = False
	myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)
	for topo in myixia.topologies:
		topo.add_ipv4()
		
	myixia.start_protocol(wait=20)

	for i in range(0,len(tb.ixia.port_active_list)-1):
		for j in range(i+1,len(tb.ixia.port_active_list)):
			myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=1)
			#myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=1)

	
	if initial_testing:
		myixia.start_traffic()
		myixia.collect_stats()
		myixia.check_traffic()
		myixia.stop_traffic()


	cmd = "execute acl clear-counter all"
	sw.exec_command(cmd)
	sleep(10)

	final_results = []
	if testcase == 1 or test_all:
		testcase = 1
		sys.stdout = Logger(f"Log/ACL_counter_{testcase}.log")
		description = "Ingress 4 Color counter types for 3032E: only ingress policer"
		print(description)

		results = []
		for i in range(1):
			cmds = """
			config switch acl ingress
			delete 1
			delete 2
			end
			config switch acl egress
			delete 1
			delete 2
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl policer
   			delete 1
    		delete 2
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl policer
   			edit 1
       			set guaranteed-bandwidth 2000
        		set type ingress
    		next
    		edit 2
        		set guaranteed-bandwidth 1000
        		set type egress
    		next
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl ingress
		    edit 1
		        config action
		            set count enable
		            set count-type all green yellow red
		            set policer 1
		        end
		        set ingress-interface "port1.1"         
		    next
			end
			config switch acl egress
		    edit 1
		        config action
		            set count enable
		            set count-type green yellow 
		        end
		        set interface "port1.2"         
		    next
			end
			
			"""
			sw.config_cmds(cmds)
			sleep(3)

			cmd = "execute acl clear-counter all"
			sw.exec_command(cmd)
			sleep(3)
			sw.show_command("get switch acl counters all")
			myixia.start_traffic()
			myixia.stop_traffic()
			ixia_stats_list = myixia.collect_stats()
			sleep(10)
			ixia_tx = ixia_stats_list[0]['Tx Frames']
			ixia_rx = ixia_stats_list[0]['Rx Frames']
			ixia_drop = ixia_stats_list[0]['Frames Delta']
			print(f"Total IXIA transmitted Packets = {ixia_tx}")
			print(f"Total IXIA received Packets = {ixia_rx}")
			print(f"Total packet dropped = {ixia_drop}")

			cmd_output = sw.show_command("get switch acl counters all")
			#print(cmd_output)
			acl_counter_obj = acl_counter_class(cmd_output)
			acl_counter_obj.print_acl_counters()
			test_result = False
			for obj in acl_counter_obj.acl_counter_list:
				if obj.all_pkts == 0:
					continue 
				else:
					if ixia_tx  == obj.all_pkts and ixia_rx ==obj.green_pkts and abs(ixia_drop - obj.yellow_pkts - obj.red_pkts) < 10:
						test_result = True 
			results.append(f"#{i} Testing on 3032E with 4 color ingress counter-types successful: {test_result}")
			print(f"#{i} Testing on 3032E with 4 color ingress counter-types successful: {test_result}")
		final_results.append(f"Testcase #{testcase} Testing on 3032E with 4 color ingress counter-types successful: {test_result}")
		for r in results:
			print(r)

	
	if testcase == 2 or test_all:
		testcase = 2
		sys.stdout = Logger(f"Log/ACL_counter_{testcase}.log")
		description = "Ingress 4 Color counter types for 3032E: Ingress and egress have different policers"
		print(description)

		results = []
		for i in range(1):
			cmds = """
			config switch acl ingress
			delete 1
			delete 2
			end
			config switch acl egress
			delete 1
			delete 2
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl policer
			delete 1
			delete 2
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl policer
			edit 1
				set guaranteed-bandwidth 2000
				set type ingress
				next
			edit 2
				set guaranteed-bandwidth 1000
				set type egress
				next
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl ingress
		    edit 1
		        config action
		            set count enable
		            set count-type all green yellow red
		            set policer 1
		        end
		        set ingress-interface "port1.1"         
		    next
			end
			
			config switch acl egress
		    edit 1
		        config action
		            set count enable
		            set count-type green yellow 
		            set policer 2
		        end
		        set interface "port1.2"         
		    next
			end
			
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmd = "execute acl clear-counter all"
			sw.exec_command(cmd)
			sleep(3)

			sw.show_command("get switch acl counters all")
			myixia.start_traffic()
			sleep(20)
			myixia.stop_traffic()
			ixia_stats_list = myixia.collect_stats()
			sleep(10)
			ixia_tx = ixia_stats_list[0]['Tx Frames']
			ixia_rx = ixia_stats_list[0]['Rx Frames']
			ixia_drop = ixia_stats_list[0]['Frames Delta']
			print(f"Total IXIA transmitted Packets = {ixia_tx}")
			print(f"Total IXIA received Packets = {ixia_rx}")
			print(f"Total packet dropped = {ixia_drop}")

			cmd_output = sw.show_command("get switch acl counters all")
			#print(cmd_output)
			acl_counter_obj = acl_counter_class(cmd_output)
			acl_counter_obj.print_acl_counters()
			test_result = False
			ingress_result = False
			egress_result = False
			for obj in acl_counter_obj.acl_counter_list:
				if obj.type == "ingress" and obj.all_pkts == 0:
					continue
				if obj.type == "egress" and obj.green_pkts == 0:
					continue

				if obj.type == "ingress" and ixia_tx  == obj.all_pkts:
					ingress_result = True 
					print(f"Ingress result: {ingress_result}")
					ingress_green_pkts = obj.green_pkts
					continue

				if obj.type == "egress" and ixia_rx ==obj.green_pkts and abs(ingress_green_pkts - obj.green_pkts - obj.yellow_pkts) < 10:
					egress_result = True 
					print(f"Egress result: {egress_result}")
			if ingress_result and egress_result:
				test_result = True
			results.append(f"#{i} Testing on 3032E with 4 color ingress counter-types/Ingress and egress have different policers successful: {test_result}")
			print(f"#{i} Testing on 3032E with 4 color ingress counter-types/Ingress and egress have different policers successful successful: {test_result}")

		final_results.append(f"Testcase #{testcase} Testing on 3032E with 4 color ingress counter-types/Ingress and egress have different policers successful: {test_result}")
		for r in results:
			print(r)
			 
	if testcase == 3 or test_all:
		testcase = 3
		sys.stdout = Logger(f"Log/ACL_counter_{testcase}.log")
		description = "Ingress 4 Color counter types for 3032E: ingress policer + Green counter"
		print(description)

		results = []
		for i in range(1):
			cmds = """
			config switch acl ingress
			delete 1
			delete 2
			end
			config switch acl egress
			delete 1
			delete 2
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl policer
   			delete 1
    		delete 2
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl policer
   			edit 1
       			set guaranteed-bandwidth 2000
        		set type ingress
    		next
    		edit 2
        		set guaranteed-bandwidth 1000
        		set type egress
    		next
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl ingress
		    edit 1
		        config action
		            set count enable
		            set count-type green
		            set policer 1
		        end
		        set ingress-interface "port1.1"         
		    next
			end
			
			"""
			sw.config_cmds(cmds)
			sleep(3)

			cmd = "execute acl clear-counter all"
			sw.exec_command(cmd)
			sleep(3)
			sw.show_command("get switch acl counters all")
			myixia.start_traffic()
			myixia.stop_traffic()
			ixia_stats_list = myixia.collect_stats()
			sleep(10)
			ixia_tx = ixia_stats_list[0]['Tx Frames']
			ixia_rx = ixia_stats_list[0]['Rx Frames']
			ixia_drop = ixia_stats_list[0]['Frames Delta']
			print(f"Total IXIA transmitted Packets = {ixia_tx}")
			print(f"Total IXIA received Packets = {ixia_rx}")
			print(f"Total packet dropped = {ixia_drop}")

			cmd_output = sw.show_command("get switch acl counters all")
			#print(cmd_output)
			acl_counter_obj = acl_counter_class(cmd_output)
			acl_counter_obj.print_acl_counters()
			test_result = False
			for obj in acl_counter_obj.acl_counter_list:
				if obj.green_pkts == 0:
					continue 
				else:
					if ixia_rx ==obj.green_pkts:
						test_result = True 
			results.append(f"#{i} Testing on 3032E with 4 color ingress/ingress policer + Green counter counter-types successful: {test_result}")
			print(f"#{i} Testing on 3032E with 4 color ingress counter-types successful: {test_result}")
		
		final_results.append(f"Testcase #{testcase} Testing on 3032E with 4 color ingress/ingress policer + Green counter counter-types successful: {test_result}")
		for r in results:
			print(r)

	if testcase == 4 or test_all:
		testcase = 4
		sys.stdout = Logger(f"Log/ACL_counter_{testcase}.log")
		description = "Ingress 4 Color counter types for 3032E: ingress policer + yellow + red"
		print(description)

		results = []
		for i in range(1):
			cmds = """
			config switch acl ingress
			delete 1
			delete 2
			end
			config switch acl egress
			delete 1
			delete 2
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl policer
   			delete 1
    		delete 2
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl policer
   			edit 1
       			set guaranteed-bandwidth 2000
        		set type ingress
    		next
    		edit 2
        		set guaranteed-bandwidth 1000
        		set type egress
    		next
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl ingress
		    edit 1
		        config action
		            set count enable
		            set count-type yellow red
		            set policer 1
		        end
		        set ingress-interface "port1.1"         
		    next
			end
			config switch acl egress
		    edit 1
		        config action
		            set count enable
		            set count-type green yellow 
		        end
		        set interface "port1.2"         
		    next
			end
			
			"""
			sw.config_cmds(cmds)
			sleep(3)

			cmd = "execute acl clear-counter all"
			sw.exec_command(cmd)
			sleep(3)
			sw.show_command("get switch acl counters all")
			myixia.start_traffic()
			myixia.stop_traffic()
			ixia_stats_list = myixia.collect_stats()
			sleep(10)
			ixia_tx = ixia_stats_list[0]['Tx Frames']
			ixia_rx = ixia_stats_list[0]['Rx Frames']
			ixia_drop = ixia_stats_list[0]['Frames Delta']
			print(f"Total IXIA transmitted Packets = {ixia_tx}")
			print(f"Total IXIA received Packets = {ixia_rx}")
			print(f"Total packet dropped = {ixia_drop}")

			cmd_output = sw.show_command("get switch acl counters all")
			#print(cmd_output)
			acl_counter_obj = acl_counter_class(cmd_output)
			acl_counter_obj.print_acl_counters()
			test_result = False
			for obj in acl_counter_obj.acl_counter_list:
				if obj.yellow_pkts == 0:
					continue 
				else:
					if abs(ixia_drop - obj.yellow_pkts - obj.red_pkts) < 10:
						test_result = True 
			results.append(f"#{i} Testing on 3032E with 4 color ingress yellow + red counter-types successful: {test_result}")
			print(f"#{i} Testing on 3032E with 4 color ingress counter-types successful: {test_result}")

		final_results.append(f"Testcase #{testcase} Testing on 3032E with 4 color ingress yellow + red counter-types successful: {test_result}")
		for r in results:
			print(r)

	if testcase == 5 or test_all:
		testcase = 5
		sys.stdout = Logger(f"Log/ACL_counter_{testcase}.log")
		description = "Ingress 4 Color counter types for 3032E: ingress policer + green + yellow + red"
		print(description)

		results = []
		for i in range(1):
			cmds = """
			config switch acl ingress
			delete 1
			delete 2
			end
			config switch acl egress
			delete 1
			delete 2
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl policer
   			delete 1
    		delete 2
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl policer
   			edit 1
       			set guaranteed-bandwidth 2000
        		set type ingress
    		next
    		edit 2
        		set guaranteed-bandwidth 1000
        		set type egress
    		next
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl ingress
		    edit 1
		        config action
		            set count enable
		            set count-type yellow red green
		            set policer 1
		        end
		        set ingress-interface "port1.1"         
		    next
			end
			
			"""
			sw.config_cmds(cmds)
			sleep(3)

			cmd = "execute acl clear-counter all"
			sw.exec_command(cmd)
			sleep(3)
			sw.show_command("get switch acl counters all")
			myixia.start_traffic()
			myixia.stop_traffic()
			ixia_stats_list = myixia.collect_stats()
			sleep(10)
			ixia_tx = ixia_stats_list[0]['Tx Frames']
			ixia_rx = ixia_stats_list[0]['Rx Frames']
			ixia_drop = ixia_stats_list[0]['Frames Delta']
			print(f"Total IXIA transmitted Packets = {ixia_tx}")
			print(f"Total IXIA received Packets = {ixia_rx}")
			print(f"Total packet dropped = {ixia_drop}")

			cmd_output = sw.show_command("get switch acl counters all")
			#print(cmd_output)
			acl_counter_obj = acl_counter_class(cmd_output)
			acl_counter_obj.print_acl_counters()
			test_result = False
			for obj in acl_counter_obj.acl_counter_list:
				if obj.green_pkts == 0:
					continue 
				else:
					if ixia_rx == obj.green_pkts and abs(ixia_drop - obj.yellow_pkts - obj.red_pkts) < 10:
						test_result = True 
			results.append(f"#{i} Testing on 3032E with 4 color ingress green + yellow + red counter-types successful: {test_result}")
			print(f"#{i} Testing on 3032E with 4 color ingress counter-types successful: {test_result}")

		final_results.append(f"Testcase #{testcase} Testing on 3032E with 4 color ingress yellow + red counter-types successful: {test_result}")
		for r in results:
			print(r)

	print("================================== Final Results ====================================")
	for r in final_results:
		print(r)


	if testcase == 6 or test_all:
		testcase = 6
		sys.stdout = Logger(f"Log/ACL_counter_{testcase}.log")
		description = "Egress 2 Color counter types for 3032E: egress policer All counter"
		print(description)

		results = []
		for i in range(1):
			cmds = """
			config switch acl ingress
			delete 1
			delete 2
			end
			config switch acl egress
			delete 1
			delete 2
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl policer
   			delete 1
    		delete 2
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl policer
   			edit 1
       			set guaranteed-bandwidth 2000
        		set type ingress
    		next
    		edit 2
        		set guaranteed-bandwidth 1000
        		set type egress
    		next
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl egress
		    edit 1
		        config action
		            set count enable
		            set count-type all
		            set policer 2
		        end
		        set interface "port1.2"         
		    next
			end
			
			"""
			sw.config_cmds(cmds)
			sleep(3)

			cmd = "execute acl clear-counter all"
			sw.exec_command(cmd)
			sleep(3)
			sw.show_command("get switch acl counters all")
			myixia.start_traffic()
			myixia.stop_traffic()
			ixia_stats_list = myixia.collect_stats()
			sleep(10)
			ixia_tx = ixia_stats_list[0]['Tx Frames']
			ixia_rx = ixia_stats_list[0]['Rx Frames']
			ixia_drop = ixia_stats_list[0]['Frames Delta']
			print(f"Total IXIA transmitted Packets = {ixia_tx}")
			print(f"Total IXIA received Packets = {ixia_rx}")
			print(f"Total packet dropped = {ixia_drop}")

			cmd_output = sw.show_command("get switch acl counters all")
			#print(cmd_output)
			acl_counter_obj = acl_counter_class(cmd_output)
			acl_counter_obj.print_acl_counters()
			test_result = False
			for obj in acl_counter_obj.acl_counter_list:
				if obj.all_pkts == 0:
					continue 
				else:
					if abs(obj.all_pkts - ixia_tx) < 10:
						test_result = True 
			results.append(f"#{i} Testing on 3032E with 2 color egress All counte-type successful: {test_result}")
			print(f"#{i} Testing on 3032E with 2 color egress All counte-type successful: {test_result}")

		final_results.append(f"Testcase #{testcase} Testing on 3032E with 2 color egress All counte-type successful: {test_result}")
		for r in results:
			print(r)

	if testcase == 7 or test_all:
		testcase = 7
		sys.stdout = Logger(f"Log/ACL_counter_{testcase}.log")
		description = "Egress 2 Color counter types for 3032E: egress policer green counter"
		print(description)

		results = []
		for i in range(1):
			cmds = """
			config switch acl ingress
			delete 1
			delete 2
			end
			config switch acl egress
			delete 1
			delete 2
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl policer
   			delete 1
    		delete 2
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl policer
   			edit 1
       			set guaranteed-bandwidth 2000
        		set type ingress
    		next
    		edit 2
        		set guaranteed-bandwidth 1000
        		set type egress
    		next
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl egress
		    edit 1
		        config action
		            set count enable
		            set count-type green
		            set policer 2
		        end
		        set interface "port1.2"         
		    next
			end
			
			"""
			sw.config_cmds(cmds)
			sleep(3)

			cmd = "execute acl clear-counter all"
			sw.exec_command(cmd)
			sleep(3)
			sw.show_command("get switch acl counters all")
			myixia.start_traffic()
			myixia.stop_traffic()
			ixia_stats_list = myixia.collect_stats()
			sleep(10)
			ixia_tx = ixia_stats_list[0]['Tx Frames']
			ixia_rx = ixia_stats_list[0]['Rx Frames']
			ixia_drop = ixia_stats_list[0]['Frames Delta']
			print(f"Total IXIA transmitted Packets = {ixia_tx}")
			print(f"Total IXIA received Packets = {ixia_rx}")
			print(f"Total packet dropped = {ixia_drop}")

			cmd_output = sw.show_command("get switch acl counters all")
			#print(cmd_output)
			acl_counter_obj = acl_counter_class(cmd_output)
			acl_counter_obj.print_acl_counters()
			test_result = False
			for obj in acl_counter_obj.acl_counter_list:
				if obj.green_pkts == 0:
					continue 
				else:
					if abs(ixia_rx - obj.green_pkts) < 10:
						test_result = True 
			results.append(f"#{i} Testing on 3032E with 2 color egress green counte-type successful: {test_result}")
			print(f"#{i} Testing on 3032E with 2 color egress green counte-type successful: {test_result}")

		final_results.append(f"Testcase #{testcase} Testing on 3032E with 2 color egress green counte-type successful: {test_result}")
		for r in results:
			print(r)


	if testcase == 8 or test_all:
		testcase = 8
		sys.stdout = Logger(f"Log/ACL_counter_{testcase}.log")
		description = "Egress 2 Color counter types for 3032E: egress policer yellow counter"
		print(description)

		results = []
		for i in range(1):
			cmds = """
			config switch acl ingress
			delete 1
			delete 2
			end
			config switch acl egress
			delete 1
			delete 2
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl policer
   			delete 1
    		delete 2
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl policer
   			edit 1
       			set guaranteed-bandwidth 2000
        		set type ingress
    		next
    		edit 2
        		set guaranteed-bandwidth 1000
        		set type egress
    		next
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl egress
		    edit 1
		        config action
		            set count enable
		            set count-type yellow
		            set policer 2
		        end
		        set interface "port1.2"         
		    next
			end
			
			"""
			sw.config_cmds(cmds)
			sleep(3)

			cmd = "execute acl clear-counter all"
			sw.exec_command(cmd)
			sleep(3)
			sw.show_command("get switch acl counters all")
			myixia.start_traffic()
			myixia.stop_traffic()
			ixia_stats_list = myixia.collect_stats()
			sleep(10)
			ixia_tx = ixia_stats_list[0]['Tx Frames']
			ixia_rx = ixia_stats_list[0]['Rx Frames']
			ixia_drop = ixia_stats_list[0]['Frames Delta']
			print(f"Total IXIA transmitted Packets = {ixia_tx}")
			print(f"Total IXIA received Packets = {ixia_rx}")
			print(f"Total packet dropped = {ixia_drop}")

			cmd_output = sw.show_command("get switch acl counters all")
			#print(cmd_output)
			acl_counter_obj = acl_counter_class(cmd_output)
			acl_counter_obj.print_acl_counters()
			test_result = False
			for obj in acl_counter_obj.acl_counter_list:
				if obj.yellow_pkts == 0:
					continue 
				else:
					if abs(ixia_drop - obj.yellow_pkts) < 10:
						test_result = True 
			results.append(f"#{i} Testing on 3032E with 2 color egress yellow counter-types successful: {test_result}")
			print(f"#{i} Testing on 3032E with 2 color egress yellow counter-types successful: {test_result}")

		final_results.append(f"Testcase #{testcase} Testing on 3032E with 2 color egress yellow counte-type successful: {test_result}")
		for r in results:
			print(r)

	if testcase == 9 or test_all:
		testcase = 9
		sys.stdout = Logger(f"Log/ACL_counter_{testcase}.log")
		description = "Egress 2 Color counter types for 3032E: egress policer green + yellow counter"
		print(description)

		results = []
		for i in range(1):
			cmds = """
			config switch acl ingress
			delete 1
			delete 2
			end
			config switch acl egress
			delete 1
			delete 2
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl policer
   			delete 1
    		delete 2
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl policer
   			edit 1
       			set guaranteed-bandwidth 2000
        		set type ingress
    		next
    		edit 2
        		set guaranteed-bandwidth 1000
        		set type egress
    		next
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl egress
		    edit 1
		        config action
		            set count enable
		            set count-type yellow green
		            set policer 2
		        end
		        set interface "port1.2"         
		    next
			end
			
			"""
			sw.config_cmds(cmds)
			sleep(3)

			cmd = "execute acl clear-counter all"
			sw.exec_command(cmd)
			sleep(3)
			sw.show_command("get switch acl counters all")
			myixia.start_traffic()
			myixia.stop_traffic()
			ixia_stats_list = myixia.collect_stats()
			sleep(10)
			ixia_tx = ixia_stats_list[0]['Tx Frames']
			ixia_rx = ixia_stats_list[0]['Rx Frames']
			ixia_drop = ixia_stats_list[0]['Frames Delta']
			print(f"Total IXIA transmitted Packets = {ixia_tx}")
			print(f"Total IXIA received Packets = {ixia_rx}")
			print(f"Total packet dropped = {ixia_drop}")

			cmd_output = sw.show_command("get switch acl counters all")
			#print(cmd_output)
			acl_counter_obj = acl_counter_class(cmd_output)
			acl_counter_obj.print_acl_counters()
			test_result = False
			for obj in acl_counter_obj.acl_counter_list:
				if obj.yellow_pkts == 0:
					continue 
				else:
					if abs(ixia_drop - obj.yellow_pkts) < 10 and abs(ixia_rx - obj.green_pkts) < 10:
						test_result = True 
			results.append(f"#{i} Testing on 3032E with 2 color egress green + yellow counter-types successful: {test_result}")
			print(f"#{i} Testing on 3032E with 2 color egress green + yellow counter-types successful: {test_result}")

		final_results.append(f"Testcase #{testcase} Testing on 3032E with 2 color egress green + yellow counte-type successful: {test_result}")
		for r in results:
			print(r)

	if testcase == 10 or test_all:
		testcase = 10
		sys.stdout = Logger(f"Log/ACL_counter_{testcase}.log")
		description = "Egress 2 Color counter types for 3032E: egress change policer with green + yellow counter"
		print(description)

		results = []
		for i in range(1):
			cmds = """
			config switch acl ingress
			delete 1
			delete 2
			end
			config switch acl egress
			delete 1
			delete 2
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl policer
   			delete 1
    		delete 2
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl policer
   			edit 1
       			set guaranteed-bandwidth 2000
        		set type ingress
    		next
    		edit 2
        		set guaranteed-bandwidth 1000
        		set type egress
    		next
    		edit 3
        		set guaranteed-bandwidth 900
        		set type egress
    		next
    		edit 4
        		set guaranteed-bandwidth 800
        		set type egress
    		next
			end
			edit 5
        		set guaranteed-bandwidth 700
        		set type egress
    		next
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			policer_results = []
			for p in [2,3,4,5]:
				cmds = f"""
				config switch acl egress
			    edit 1
			        config action
			            set count enable
			            set count-type yellow green
			            set policer {p}
			        end
			        set interface "port1.2"         
			    next
				end
				
				"""
				sw.config_cmds(cmds)
				sleep(10)

				cmd = "execute acl clear-counter all"
				sw.exec_command(cmd)
				sleep(3)
				sw.show_command("get switch acl counters all")
				myixia.start_traffic()
				myixia.stop_traffic()
				ixia_stats_list = myixia.collect_stats()
				sleep(10)
				ixia_tx = ixia_stats_list[0]['Tx Frames']
				ixia_rx = ixia_stats_list[0]['Rx Frames']
				ixia_drop = ixia_stats_list[0]['Frames Delta']
				print(f"Total IXIA transmitted Packets = {ixia_tx}")
				print(f"Total IXIA received Packets = {ixia_rx}")
				print(f"Total packet dropped = {ixia_drop}")

				cmd_output = sw.show_command("get switch acl counters all")
				#print(cmd_output)
				acl_counter_obj = acl_counter_class(cmd_output)
				acl_counter_obj.print_acl_counters()
				test_result = False
				for obj in acl_counter_obj.acl_counter_list:
					if obj.yellow_pkts == 0:
						continue 
					else:
						if abs(ixia_drop - obj.yellow_pkts) < 10 and abs(ixia_rx - obj.green_pkts) < 10:
							test_result = True 
							policer_results.append(test_result)
				results.append(f"#{i} Testing on 3032E with 2 color egress change policers green + yellow counter-types successful: {test_result}")
				print(f"#Testing on 3032E with 2 color egress change policers green + yellow counter-types successful: {test_result}")

		if policer_results.count(True) == len(policer_results):
			test_result = True 
		else:
			test_result = False
		final_results.append(f"Testcase #{testcase} Testing on 3032E with 2 color egress change policers green + yellow counte-type successful: {test_result}")
		for r in results:
			print(r)

	if testcase == 11 or test_all:
		testcase = 11
		sys.stdout = Logger(f"Log/ACL_counter_{testcase}.log")
		description = "Ingress 4 Color counter types for 3032E: ingress enable/disable count-type"
		print(description)

		cmds = """
		config switch acl ingress
		delete 1
		delete 2
		delete 3
		delete 4
		end
		config switch acl egress
		delete 1
		delete 2
		delete 3
		delete 4
		end
		"""
		sw.config_cmds(cmds)
		sleep(10)

		cmds = """
		config switch acl policer
			delete 1
		delete 2
		delete 3
		delete 4
		delete 5
		delete 6
		delete 7
		end
		"""
		sw.config_cmds(cmds)
		sleep(10)

		cmds = """
		config switch acl policer
			edit 1
   			set guaranteed-bandwidth 2000
    		set type ingress
		next
		edit 2
    		set guaranteed-bandwidth 1000
    		set type egress
		next
		end
		"""
		sw.config_cmds(cmds)
		sleep(10)

		list_results = []
		for i in range(10):

			cmds = """
			config switch acl ingress
		    edit 1
		        config action
		            unset count-type
		            end
		        end
		    config switch acl egress
		    edit 1
		        config action
		            unset count-type
		        end
			end
			"""
			sw.config_cmds(cmds)
			sleep(3)

			cmds = """
			config switch acl ingress
		    edit 1
		        config action
		            set count enable
		            set count-type all green yellow red
		            set policer 1
		        end
		        set ingress-interface "port1.1"         
		    next
			end
			config switch acl egress
		    edit 1
		        config action
		            set count enable
		            set count-type green yellow 
		        end
		        set interface "port1.2"         
		    next
			end
			
			"""
			sw.config_cmds(cmds)
			sleep(3)

			cmd = "execute acl clear-counter all"
			sw.exec_command(cmd)
			sleep(3)
			sw.show_command("get switch acl counters all")
			myixia.start_traffic()
			myixia.stop_traffic()
			ixia_stats_list = myixia.collect_stats()
			sleep(10)
			ixia_tx = ixia_stats_list[0]['Tx Frames']
			ixia_rx = ixia_stats_list[0]['Rx Frames']
			ixia_drop = ixia_stats_list[0]['Frames Delta']
			print(f"Total IXIA transmitted Packets = {ixia_tx}")
			print(f"Total IXIA received Packets = {ixia_rx}")
			print(f"Total packet dropped = {ixia_drop}")

			cmd_output = sw.show_command("get switch acl counters all")
			#print(cmd_output)
			acl_counter_obj = acl_counter_class(cmd_output)
			acl_counter_obj.print_acl_counters()
			test_result = False
			for obj in acl_counter_obj.acl_counter_list:
				if obj.all_pkts == 0:
					continue 
				else:
					if ixia_tx  == obj.all_pkts and ixia_rx ==obj.green_pkts and abs(ixia_drop - obj.yellow_pkts - obj.red_pkts) < 10:
						test_result = True 
				list_results.append(test_result)
				results.append(f"#{i} Testing on 3032E with 4 color ingress counter-type enable/disable successful: {test_result}")

		if list_results.count(True) == len(list_results):
			test_result = True 
		else:
			test_result = False

		final_results.append(f"Testcase #{testcase} Testing on 3032E with 4 color ingress counter-type enable/disable successful: {test_result}")
		for r in results:
			print(r)
		 

	if testcase == 12 or test_all:
		testcase = 12
		sys.stdout = Logger(f"Log/ACL_counter_{testcase}.log")
		description = "Egress 2 Color counter types for 3032E: egress policer enable/disable counter-type"
		print(description)

		cmds = """
		config switch acl ingress
		delete 1
		delete 2
		delete 3
		delete 4
		end
		config switch acl egress
		delete 1
		delete 2
		delete 3
		delete 4
		end
		"""
		sw.config_cmds(cmds)
		sleep(10)

		cmds = """
		config switch acl policer
			delete 1
		delete 2
		delete 3
		delete 4
		delete 5
		delete 6
		delete 7
		end
		"""
		sw.config_cmds(cmds)
		sleep(10)

		cmds = """
		config switch acl policer
			edit 1
   			set guaranteed-bandwidth 2000
    		set type ingress
		next
		edit 2
    		set guaranteed-bandwidth 1000
    		set type egress
		next
		end
		"""
		sw.config_cmds(cmds)
		sleep(10)

		list_results = []
		results = []
		for i in range(10):

			cmds = """
			config switch acl egress
		    edit 1
		        config action
 		            unset count-type  
 		        end
 			end
			"""
			sw.config_cmds(cmds)
			sleep(3)

			cmds = """
			config switch acl egress
		    edit 1
		        config action
		            set count enable
		            set count-type yellow green
		            set policer 2
		        end
		        set interface "port1.2"         
		    next
			end
			
			"""
			sw.config_cmds(cmds)
			sleep(3)

			cmd = "execute acl clear-counter all"
			sw.exec_command(cmd)
			sleep(3)
			sw.show_command("get switch acl counters all")
			myixia.start_traffic()
			myixia.stop_traffic()
			ixia_stats_list = myixia.collect_stats()
			sleep(10)
			ixia_tx = ixia_stats_list[0]['Tx Frames']
			ixia_rx = ixia_stats_list[0]['Rx Frames']
			ixia_drop = ixia_stats_list[0]['Frames Delta']
			print(f"Total IXIA transmitted Packets = {ixia_tx}")
			print(f"Total IXIA received Packets = {ixia_rx}")
			print(f"Total packet dropped = {ixia_drop}")

			cmd_output = sw.show_command("get switch acl counters all")
			#print(cmd_output)
			acl_counter_obj = acl_counter_class(cmd_output)
			acl_counter_obj.print_acl_counters()
			test_result = False
			for obj in acl_counter_obj.acl_counter_list:
				if obj.yellow_pkts == 0:
					continue 
				else:
					if abs(ixia_drop - obj.yellow_pkts) < 10 and abs(ixia_rx - obj.green_pkts) < 10:
						test_result = True 
				list_results.append(test_result)

			results.append(f"#{i} Testing on 3032E with 2 color egress enable/disable counter-types successful: {test_result}")
			print(f"#{i} Testing on 3032E egress enable/disable counter-type successful: {test_result}")
		if list_results.count(True) == len(list_results):
			test_result = True 
		else:
			test_result = False

		final_results.append(f"Testcase #{testcase} Testing on 3032E engress counter-type enable/disable successful: {test_result}")
		for r in results:
			print(r)
	print("================================== Final Results ====================================")
	for r in final_results:
		print(r)


	if testcase == 13 or test_all or testcase_range:
		testcase = 13
		if testcase_range and testcase in testcase_list:
		
			sys.stdout = Logger(f"Log/ACL_counter_{testcase}.log")
			description = "Ingress 4 Color counter types for 3032E: ingress enable/disable count"
			print(description)

			cmds = """
			config switch acl ingress
			delete 1
			delete 2
			delete 3
			delete 4
			end
			config switch acl egress
			delete 1
			delete 2
			delete 3
			delete 4
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl policer
				delete 1
			delete 2
			delete 3
			delete 4
			delete 5
			delete 6
			delete 7
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl policer
				edit 1
	   			set guaranteed-bandwidth 2000
	    		set type ingress
			next
			edit 2
	    		set guaranteed-bandwidth 1000
	    		set type egress
			next
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			list_results = []
			results = []
			for i in range(1):

				cmds = """
				config switch acl ingress
			    edit 1
			        config action
			            set count disable
			            end
			        end
			    config switch acl egress
			    edit 1
			        config action
			            set count disable
			        end
				end
				"""
				sw.config_cmds(cmds)
				sleep(3)

				cmds = """
				config switch acl ingress
			    edit 1
			        config action
			            set count enable
			            set count-type all green yellow red
			            set policer 1
			        end
			        set ingress-interface "port1.1"         
			    next
				end
				config switch acl egress
			    edit 1
			        config action
			            set count enable
			            set count-type green yellow 
			        end
			        set interface "port1.2"         
			    next
				end
				
				"""
				sw.config_cmds(cmds)
				sleep(3)

				cmd = "execute acl clear-counter all"
				sw.exec_command(cmd)
				sleep(3)
				sw.show_command("get switch acl counters all")
				myixia.start_traffic()
				myixia.stop_traffic()
				ixia_stats_list = myixia.collect_stats()
				sleep(10)
				ixia_tx = ixia_stats_list[0]['Tx Frames']
				ixia_rx = ixia_stats_list[0]['Rx Frames']
				ixia_drop = ixia_stats_list[0]['Frames Delta']
				print(f"Total IXIA transmitted Packets = {ixia_tx}")
				print(f"Total IXIA received Packets = {ixia_rx}")
				print(f"Total packet dropped = {ixia_drop}")

				cmd_output = sw.show_command("get switch acl counters all")
				#print(cmd_output)
				acl_counter_obj = acl_counter_class(cmd_output)
				acl_counter_obj.print_acl_counters()
				test_result = False
				for obj in acl_counter_obj.acl_counter_list:
					if obj.all_pkts == 0:
						continue 
					else:
						if ixia_tx  == obj.all_pkts and ixia_rx ==obj.green_pkts and abs(ixia_drop - obj.yellow_pkts - obj.red_pkts) < 10:
							test_result = True 
					list_results.append(test_result)
					results.append(f"#{i} Testing on 3032E with 4 color ingress counter-type enable/disable successful: {test_result}")

			if list_results.count(True) == len(list_results):
				test_result = True 
			else:
				test_result = False

			final_results.append(f"Testcase #{testcase} Testing on 3032E with 4 color ingress counter-type enable/disable successful: {test_result}")
			for r in results:
				print(r)
			 

	if testcase == 14 or test_all or testcase_range:
		testcase = 14
		if testcase_range and testcase in testcase_list:
			sys.stdout = Logger(f"Log/ACL_counter_{testcase}.log")
			description = "Egress 2 Color counter types for 3032E: egress policer enable/disable counter"
			print(description)

			cmds = """
			config switch acl ingress
			delete 1
			delete 2
			delete 3
			delete 4
			end
			config switch acl egress
			delete 1
			delete 2
			delete 3
			delete 4
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl policer
				delete 1
			delete 2
			delete 3
			delete 4
			delete 5
			delete 6
			delete 7
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			cmds = """
			config switch acl policer
				edit 1
	   			set guaranteed-bandwidth 2000
	    		set type ingress
			next
			edit 2
	    		set guaranteed-bandwidth 1000
	    		set type egress
			next
			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			list_results = []
			results = []
			for i in range(1):

				cmds = """
				config switch acl egress
			    edit 1
			        config action
	 		            set count disable  
	 		        end
	 			end
				"""
				sw.config_cmds(cmds)
				sleep(3)

				cmds = """
				config switch acl egress
			    edit 1
			        config action
			            set count enable
			            set count-type yellow green
			            set policer 2
			        end
			        set interface "port1.2"         
			    next
				end
				
				"""
				sw.config_cmds(cmds)
				sleep(3)

				cmd = "execute acl clear-counter all"
				sw.exec_command(cmd)
				sleep(3)
				sw.show_command("get switch acl counters all")
				myixia.start_traffic()
				myixia.stop_traffic()
				ixia_stats_list = myixia.collect_stats()
				sleep(10)
				ixia_tx = ixia_stats_list[0]['Tx Frames']
				ixia_rx = ixia_stats_list[0]['Rx Frames']
				ixia_drop = ixia_stats_list[0]['Frames Delta']
				print(f"Total IXIA transmitted Packets = {ixia_tx}")
				print(f"Total IXIA received Packets = {ixia_rx}")
				print(f"Total packet dropped = {ixia_drop}")

				cmd_output = sw.show_command("get switch acl counters all")
				#print(cmd_output)
				acl_counter_obj = acl_counter_class(cmd_output)
				acl_counter_obj.print_acl_counters()
				test_result = False
				for obj in acl_counter_obj.acl_counter_list:
					if obj.yellow_pkts == 0:
						continue 
					else:
						if abs(ixia_drop - obj.yellow_pkts) < 10 and abs(ixia_rx - obj.green_pkts) < 10:
							test_result = True 
					list_results.append(test_result)

				results.append(f"#{i} Testing on 3032E with 2 color egress enable/disable counter  successful: {test_result}")
				print(f"#{i} Testing on 3032E egress enable/disable counter  successful: {test_result}")
			if list_results.count(True) == len(list_results):
				test_result = True 
			else:
				test_result = False

			final_results.append(f"Testcase #{testcase} Testing on 3032E engress counter-type enable/disable successful: {test_result}")
			for r in results:
				print(r)

	print("================================== Final Results ====================================")
	for r in final_results:
		print(r)


##################################################################################################################################################
##################################################################################################################################################