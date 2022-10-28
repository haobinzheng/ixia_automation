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
	sys.stdout = Logger(f"Log/ACL_counter_generic.log")
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
	testcase_range = False

	
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
	file = 'tbinfo_multi_sw_acl6.xml'
	tb = parse_tbinfo_untangle(file)
	testtopo_file = 'topo_acl6.xml'
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

	sw = switches[0]
	sw1 = switches[1]
	
	apiServerIp = tb.ixia.ixnetwork_server_ip
	#ixChassisIpList = ['10.105.241.234']
	ixChassisIpList = [tb.ixia.chassis_ip]
 	
 	############################################### Static Data Are Define Here ########################################################################
	ixia_sub_intf = 1
	mac_list = ["00:11:01:01:01:01","00:12:01:01:01:01","00:13:01:01:01:01","00:14:01:01:01:01","00:15:01:01:01:01","00:16:01:01:01:01","00:17:01:01:01:01","00:18:01:01:01:01"]
	net4_list = ["10.1.1.10/16","10.1.2.10/16","10.1.3.10/16","10.1.4.10/16","10.1.5.10/16","10.1.6.10/16","10.1.7.10/16","10.1.8.10/16","10.1.9.10/16","10.1.10.10/16"]
	gw4_list = ["10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1"]
	net6_list = ["2001:10:1:1::1000/64","2001:10:1:1::2000/64","2001:10:1:1::3000/64","2001:10:1:1::4000/64","2001:10:1:1::5000/64","2001:10:1:1::6000/64","2001:10:1:1::7000/64","2001:10:1:1::8000/64"]
	gw6_list = ["2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1"]

	config_interfaces = False
	clean_acl = False
	config_acl_ingress = False
	############################################### Static Data Are Define Here ########################################################################
	 
	portList_v4_v6 = []
	
	for p,m,n4,g4,n6,g6 in zip(tb.ixia.port_active_list,mac_list,net4_list,gw4_list,net6_list,gw6_list):
		module,port = p.split("/")
		portList_v4_v6.append([ixChassisIpList[0], int(module),int(port),m,n4,g4,n6,g6,ixia_sub_intf])

	print(portList_v4_v6)


	##################################### Pre-Test setup and configuration #############################
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
	

	def memory_leak_test():
		lw_old_dict = {}
		while True:
			for sw in switches:
				tprint(f"---------------------------------- cpu-memory-iostats: {sw.name} --------------------------------------")
				try:
					result = loop_command_output(sw.console,"fnsysctl top")
				except (BrokenPipeError,EOFError,UnicodeDecodeError) as e:
					debug(f"Having problem to collect fnsysctl top command on {sw.name}")
					continue

				#sw.fsw_show_cmd("diagnose test application fpmd 1")
				lw_list = sw.fsw_show_cmd("fnsysctl ps -lw")
				lw_current_dict = sw.sw_fnsysctl_process(lw_list)
				if bool(lw_old_dict):
					for k,v in lw_current_dict.items():
						if lw_old_dict[k] < lw_current_dict[k]:
							print(f"Potential memory leak | {k}: before ={lw_old_dict[k]}, now = {v}")
						else:
							print(f"No memory leak | {k}: before ={lw_old_dict[k]}, now = {v}")
				lw_old_dict = lw_current_dict
				# sw.fsw_show_cmd("diagnose switch physical-ports io-stats cumulative")
			sleep(300)
			print_double_line()

	def delete_acl_policer():
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

	def config_sys_interfaces(sw):
		cmds = f"""
		config system interface
		edit "vlan2"
			set ip {gw4_list[0]} 255.255.0.0
		    config ipv6
                set ip6-address {gw6_list[0]}/64
                set ip6-allowaccess ping https http ssh telnet
                set dhcp6-information-request enable
		        end
		        set vlanid 2
		        set interface "internal"
		    next
		end
		end
		"""
		sw.config_cmds(cmds)
		sleep(10)
		for port in sw.ixia_ports:
			cmds = f"""
			config switch interface
				edit {port}
			  	set native-vlan 2
			  	end
			"""
			sw.config_cmds_fast(cmds)
			sleep(2)

	acl = switch_acl_ingress(sw)

	if config_interfaces == True:
		config_sys_interfaces(sw)

	if clean_acl == True:
		acl.acl_ingress_clean_up()

	def basic_acl6_testing():
		acl.acl_ingress_clean_up()
		for i in range(ixia_sub_intf):
			classifiers = {}
			globals = {}
			actions = {}

			index=1+i
			classifiers = {
			"dst-ip6-prefix":str(ipaddress.IPv6Address(net6_list[1].split("/")[0])+i),
			"src-ip6-prefix":str(ipaddress.IPv6Address(net6_list[0].split("/")[0])+i)
			}
			
			globals = {
			"group":5,
             "ingress-interface": sw.ixia_ports[0]
            }
			
			actions = {
			"count":"enable"
			}
			
			acl.config_acl6_generic(index,globals,classifiers,actions)

			index=1001+i
			classifiers = {
			"dst-ip6-prefix":str(ipaddress.IPv6Address(net6_list[0].split("/")[0])+i),
			"src-ip6-prefix":str(ipaddress.IPv6Address(net6_list[1].split("/")[0])+i)
			}
			
			globals = {
			"group":5,
             "ingress-interface": sw.ixia_ports[1]
            }
			
			actions = {
			"count":"enable"
			}
			acl.config_acl6_generic(index,globals,classifiers,actions)
 
		myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)
		for topo in myixia.topologies:
			topo.add_ipv4(gateway="fixed",ip_incremental="0.0.0.1")
			topo.add_ipv6(gateway="fixed")
			
		myixia.start_protocol(wait=20)

		for i in range(0,len(tb.ixia.port_active_list)-1):
			for j in range(i+1,len(tb.ixia.port_active_list)):
				# myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=5)
				# myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=5)
				myixia.create_traffic_v6(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v6",tracking_name=f"Tracking_{i+1}_{j+1}_v6",rate=5)
				myixia.create_traffic_v6(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v6",tracking_name=f"Tracking_{j+1}_{i+1}_v6",rate=5)


		initial_testing = True
		if initial_testing:
			myixia.start_traffic()
			myixia.collect_stats()
			myixia.check_traffic()
			myixia.stop_traffic()

	def scale_acl6_testing():
		acl = switch_acl_ingress(sw)
		acl.acl_ingress_clean_up()
		sw.switch_reboot_login()

		try_group = 3
		while (try_group < 7):
			acl.acl_ingress_clean_up()
			acl.update_acl_usage()
			acl.print_acl_usage()
			index = 1
			classifiers = {
			"dst-ip6-prefix":str(ipaddress.IPv6Address(net6_list[1].split("/")[0])),
			"src-ip6-prefix":str(ipaddress.IPv6Address(net6_list[0].split("/")[0]))
			}
			globals = {
			"group":try_group,
	         "ingress-interface": sw.ixia_ports[0]
	        }
			actions = {
			"count":"enable"
			}
			acl.config_acl6_generic(index,globals,classifiers,actions)
			sleep(5)
			acl.acl_ingress_clean_up()
			sleep(5)

			acl.update_acl_usage()
			acl.print_acl_usage()
			index = 0
			for entry in acl.acl_usage_list:
				if entry.group_id >= 3:
					Info(f"Group {entry.group_id}: Total Rules = {entry.rule_total}, Free Rules = {entry.rule_free}")
					for i in range(entry.rule_total):
						index += 1
						classifiers = {
						"dst-ip6-prefix":str(ipaddress.IPv6Address(net6_list[1].split("/")[0])+i),
						"src-ip6-prefix":str(ipaddress.IPv6Address(net6_list[0].split("/")[0])+i)
						}
						
						globals = {
						"group":entry.group_id,
			             "ingress-interface": sw.ixia_ports[0]
			            }
						
						actions = {
						"count":"enable"
						}
						acl.config_acl6_generic(index,globals,classifiers,actions)
				sw.print_show_command("get switch acl usage")	
			acl.update_acl_usage()
			try_group += 1


	def basic_acl6_drop_testing():
		acl.acl_ingress_clean_up()
		for i in range(ixia_sub_intf):
			classifiers = {}
			globals = {}
			actions = {}

			index=1+i
			classifiers = {
			"dst-ip6-prefix":str(ipaddress.IPv6Address(net6_list[1].split("/")[0])+i),
			"src-ip6-prefix":str(ipaddress.IPv6Address(net6_list[0].split("/")[0])+i)
			}
			
			globals = {
			"group":6,
             "ingress-interface": sw.ixia_ports[0]
            }
			
			actions = {
			"count":"enable",
			"remark-cos":7,
			}
			
			acl.config_acl6_generic(index,globals,classifiers,actions)

			index=1001+i
			classifiers = {
			"dst-ip6-prefix":str(ipaddress.IPv6Address(net6_list[0].split("/")[0])+i),
			"src-ip6-prefix":str(ipaddress.IPv6Address(net6_list[1].split("/")[0])+i)
			}
			
			globals = {
			"group":6,
             "ingress-interface": sw.ixia_ports[1]
            }
			
			actions = {
			"count":"enable",
			"remark-cos":7,
			}
			acl.config_acl6_generic(index,globals,classifiers,actions)

		myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)
		for topo in myixia.topologies:
			topo.add_ipv4(gateway="fixed",ip_incremental="0.0.0.1")
			topo.add_ipv6(gateway="fixed")
			
		myixia.start_protocol(wait=20)

		for i in range(0,len(tb.ixia.port_active_list)-1):
			for j in range(i+1,len(tb.ixia.port_active_list)):
				myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=5)
				myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=5)
				myixia.create_traffic_v6(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v6",tracking_name=f"Tracking_{i+1}_{j+1}_v6",rate=5)
				myixia.create_traffic_v6(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v6",tracking_name=f"Tracking_{j+1}_{i+1}_v6",rate=5)


		 
		myixia.start_traffic()
		keyin = input(f"Please capture packets at IXIA to verify NO packets,Press any key when done:")
		myixia.collect_stats()
		myixia.check_traffic()
		myixia.stop_traffic()

		for i in range(ixia_sub_intf):
			classifiers = {}
			globals = {}
			actions = {}

			index=1+i
			actions = {
			"drop":"enable"
			}
			
			acl.config_acl6_generic(index,globals,classifiers,actions)

			index=1001+i
			 
			
			actions = {
			"drop":"enable"
			}
			acl.config_acl6_generic(index,globals,classifiers,actions)
		sleep(10)
		myixia.start_traffic()
		keyin = input(f"Please capture packets at IXIA to verify All IPv6 packet dropped. Press any key when done:")
		myixia.collect_stats()
		myixia.check_traffic()
		myixia.stop_traffic()

		for i in range(ixia_sub_intf):
			classifiers = {}
			globals = {}
			actions = {}

			index=1+i
			actions = {
			"drop":"disable"
			}
			
			acl.config_acl6_generic(index,globals,classifiers,actions)

			index=1001+i
			 
			
			actions = {
			"drop":"disable"
			}
			acl.config_acl6_generic(index,globals,classifiers,actions)
		sleep(10)
		myixia.start_traffic()
		keyin = input(f"Please capture packets at IXIA to verify verify NO IPv6 packets. Press any key when done:")
		myixia.collect_stats()
		myixia.check_traffic()
		myixia.stop_traffic()

	def acl6_priority_testing():
		acl.acl_ingress_clean_up()
		
		classifiers = {}
		globals = {}
		actions = {}

		# configure an entry allow forarding
		index=1
		classifiers = {
		"dst-ip6-prefix":str(ipaddress.IPv6Address(net6_list[1].split("/")[0])),
		"src-ip6-prefix":str(ipaddress.IPv6Address(net6_list[0].split("/")[0]))
		}
		
		globals = {
		"group":3,
         "ingress-interface": sw.ixia_ports[0]
        }
		
		actions = {
		"count":"enable",
		}
		acl.config_acl6_generic(index,globals,classifiers,actions)

		# configure an entry drop traffic
		index=1000
		classifiers = {
		"dst-ip6-prefix":str(ipaddress.IPv6Address(net6_list[1].split("/")[0])),
		"src-ip6-prefix":str(ipaddress.IPv6Address(net6_list[0].split("/")[0]))
		}
		
		globals = {
		"group":3,
         "ingress-interface": sw.ixia_ports[0]
        }
		
		actions = {
		"count":"enable",
		"drop":"enable"
		}
		acl.config_acl6_generic(index,globals,classifiers,actions)
		sleep(5)
		sw.print_show_command("show switch acl ingress")
		myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)
		for topo in myixia.topologies:
			topo.add_ipv4(gateway="fixed",ip_incremental="0.0.0.1")
			topo.add_ipv6(gateway="fixed")
			
		myixia.start_protocol(wait=20)

		myixia.create_traffic(src_topo=myixia.topologies[0].topology, dst_topo=myixia.topologies[1].topology,traffic_name=f"t0_to_t1_v4",tracking_name=f"Tracking_0_1_v4",rate=5)
		myixia.create_traffic_v6(src_topo=myixia.topologies[0].topology, dst_topo=myixia.topologies[1].topology,traffic_name=f"t0_to_t1_v6",tracking_name=f"Tracking_0_1_v6",rate=5)

		myixia.start_traffic()
		myixia.collect_stats()
		myixia.check_traffic()
		myixia.stop_traffic()
		keyin = input(f"Please verify both IPv4 and IPv6 traffic are forwarding,Press any key to continue:")

		cmds = f"""
		conf switch acl ingress
			move 1000 before 1
		end
		"""
		sw.config_cmds(cmds)
		sleep(5)
		sw.print_show_command("show switch acl ingress")
		myixia.start_traffic()
		keyin = input(f"Please verify IPv4 traffic is forwarding, But All IPv6 packet dropped. Press any key when done:")
		myixia.collect_stats()
		myixia.check_traffic()
		myixia.stop_traffic()

		cmds = f"""
		conf switch acl ingress
			move 1000 after 1
		end
		"""
		sw.config_cmds(cmds)
		sleep(5)
		sw.print_show_command("show switch acl ingress")
		myixia.start_traffic()
		keyin = input(f"Please verify both IPv4 and IPv6 are forwarding. Press any key when done:")
		myixia.collect_stats()
		myixia.check_traffic()
		myixia.stop_traffic()

	scale_acl6_testing()
	#acl6_priority_testing()
	#basic_acl6_testing()
	#basic_acl6_drop_testing()
	exit()
	cmd = "execute acl clear-counter all"
	sw.exec_command(cmd)
	sleep(10)

	final_results = []
	if testcase == 1 or test_all:
		testcase = 1
		description = "Ingress 2 Color counter types : only igress policer"
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
		            set count-type all
		            set policer 1
		        end
		        set ingress-interface "port1"         
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
				if obj.all_pkts == 0 or obj.all_pkts == None and obj.type == "ingress":
					continue 
				else:
					if abs(ixia_tx - obj.all_pkts) < 10:
						test_result = True 
			results.append(f"#{i} Testing 2 color ingress counter-types ALL successful: {test_result}")
			print(f"#{i} Testing 2 color ingress counter-type ALL successful: {test_result}")
		final_results.append(f"Testcase #{testcase} Testing 2 color ingress counter-types ALL successful: {test_result}")
		for r in results:
			print(r)

	
	if testcase == 2 or test_all:
		testcase = 2
		description = "Ingress 2 Color counter types : Ingress and egress have different policers"
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
		            set count-type all
		            set policer 1
		        end
		        set ingress-interface "port1"         
		    next
			end
			
			config switch acl egress
		    edit 1
		        config action
		            set count enable
		            set count-type green yellow 
		            set policer 2
		        end
		        set interface "port2"         
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
			sleep(10)
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
					ingress_green_pkts = obj.green_pkts
					 
				print(f"Ingress result: {ingress_result}")
				if obj.type == "egress" and ixia_rx ==obj.green_pkts:
					egress_result = True 
				print(f"Egress result: {egress_result}")
			if ingress_result and egress_result:
				test_result = True
			results.append(f"Testcase {testcase} run #{i} Testing on 2 color ingress counter-types/Ingress and egress have different policers successful: {test_result}")
			print(f"Testcase {testcase} run #{i} Testing on 2 color ingress counter-types/Ingress and egress have different policers successful successful: {test_result}")

		final_results.append(f"Testcase #{testcase} Testing on 2 color ingress counter-types/Ingress and egress have different policers successful: {test_result}")
		for r in results:
			print(r)
			 
	if testcase == 3 or test_all:
		testcase = 3
		description = "Ingress 2 Color counter types: ingress policer + Green counter"
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
		        set ingress-interface "port1"         
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
			sleep(10)
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
			results.append(f"#{i} Testing on 2 color ingress/ingress policer + Green counter counter-types successful: {test_result}")
			print(f"#{i} Testing on 2 color ingress counter-types successful: {test_result}")
		
		final_results.append(f"Testcase #{testcase} Testing on 2 color ingress/ingress policer + Green counter counter-types successful: {test_result}")
		for r in results:
			print(r)

	if testcase == 4 or test_all:
		testcase = 4
		description = "Ingress 2 Color counter types: ingress policer + yellow + red"
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
		        set ingress-interface "port1"         
		    next
			end
			config switch acl egress
		    edit 1
		        config action
		            set count enable
		            set count-type green yellow 
		        end
		        set interface "port2"         
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
			sleep(10)
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
				if obj.red_pkts == 0:
					continue 
				else:
					if obj.type == "ingress" and abs(ixia_drop - obj.yellow_pkts - obj.red_pkts) < 10:
						test_result = True 
			results.append(f"#{i} Testing on 2 color ingress yellow + red counter-types successful: {test_result}")
			print(f"#{i} Testing on 2 color ingress counter-types yellow + red successful: {test_result}")

		final_results.append(f"Testcase #{testcase} Testing on 2 color ingress yellow + red counter-types successful: {test_result}")
		for r in results:
			print(r)

	if testcase == 5 or test_all:
		testcase = 5
		description = "Ingress 2 Color counter types: ingress policer + green"
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
		        set ingress-interface "port1"         
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
			results.append(f"#{i} Testing on 2 color ingress green counter-types successful: {test_result}")
			print(f"#{i} Testing on 2 color ingress counter-types green successful: {test_result}")

		final_results.append(f"Testcase #{testcase} Testing on 2 color ingress green counter-types successful: {test_result}")
		for r in results:
			print(r)


	if testcase == 6 or test_all:
		testcase = 6
		description = "Egress 2 Color counter types: egress policer All counter"
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
		        set interface "port2"         
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
			sleep(10)
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
			results.append(f"#{i} Testing on 2 color egress All counte-type successful: {test_result}")
			print(f"#{i} Testing on 2 color egress All counte-type successful: {test_result}")

		final_results.append(f"Testcase #{testcase} Testing on 2 color egress All counte-type successful: {test_result}")
		for r in results:
			print(r)

	if testcase == 7 or test_all:
		testcase = 7
		description = "Egress 2 Color counter types: egress policer green counter"
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
		        set interface "port2"         
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
			sleep(10)
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
			results.append(f"#{i} Testing 2 color egress green counte-type successful: {test_result}")
			print(f"#{i} Testing 2 color egress green counte-type successful: {test_result}")

		final_results.append(f"Testcase #{testcase} Testing on 2 color egress green counte-type successful: {test_result}")
		for r in results:
			print(r)


	if testcase == 8 or test_all:
		testcase = 8
		description = "Egress 2 Color counter types : egress policer yellow counter"
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
		        set interface "port2"         
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
			sleep(10)
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
			results.append(f"#{i} Testing 2 color egress yellow counter-types successful: {test_result}")
			print(f"#{i} Testing 2 color egress yellow counter-types successful: {test_result}")

		final_results.append(f"Testcase #{testcase} Testing 2 color egress yellow counte-type successful: {test_result}")
		for r in results:
			print(r)

	if testcase == 9 or test_all:
		testcase = 9
		description = "Egress 2 Color counter types: egress policer green + yellow counter"
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
		        set interface "port2"         
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
			sleep(10)
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
			results.append(f"#{i} Testing 2 color egress green + yellow counter-types successful: {test_result}")
			print(f"#{i} Testing 2 color egress green + yellow counter-types successful: {test_result}")

		final_results.append(f"Testcase #{testcase} Testing 2 color egress green + yellow counte-type successful: {test_result}")
		for r in results:
			print(r)

	if testcase == 10 or test_all:
		testcase = 10
		description = "Egress 2 Color counter types: egress change policer with green + yellow counter"
		print(description)

		results = []
		for i in range(100):
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
			        set interface "port2"         
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
				sleep(10)
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
				results.append(f"#{i} Testing 2 color egress change policers green + yellow counter-types successful: {test_result}")
				print(f"#Testing 2 color egress change policers green + yellow counter-types successful: {test_result}")

		if policer_results.count(True) == len(policer_results):
			test_result = True 
		else:
			test_result = False
		final_results.append(f"Testcase #{testcase} Testing 2 color egress change policers green + yellow counte-type successful: {test_result}")
		for r in results:
			print(r)

	if testcase == 11 or test_all:
		testcase = 11
		description = "Ingress 2 Color counter types: ingress enable/disable count-type"
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
		            set count-type all
		            set policer 1
		        end
		        set ingress-interface "port1"         
		    next
			end
			config switch acl egress
		    edit 1
		        config action
		            set count enable
		            set count-type green yellow 
		        end
		        set interface "port2"         
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
			sleep(10)
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
					if ixia_tx  == obj.all_pkts:
						test_result = True 
				list_results.append(test_result)
				results.append(f"#{i} Testing 2 color ingress counter-type enable/disable successful: {test_result}")

		if list_results.count(True) == len(list_results):
			test_result = True 
		else:
			test_result = False

		final_results.append(f"Testcase #{testcase} Testing 2 color ingress counter-type enable/disable successful: {test_result}")
		for r in results:
			print(r)
		 

	if testcase == 12 or test_all:
		testcase = 12
		description = "Egress 2 Color counter types: egress policer enable/disable counter-type"
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
		        set interface "port2"         
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
			sleep(10)
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

			results.append(f"#{i} Testing egress enable/disable counter-types successful: {test_result}")
			print(f"#{i} Testing egress enable/disable counter-type successful: {test_result}")
		if list_results.count(True) == len(list_results):
			test_result = True 
		else:
			test_result = False

		final_results.append(f"Testcase #{testcase} Testing engress counter-type enable/disable successful: {test_result}")
		for r in results:
			print(r)


	if testcase == 13 or test_all or testcase_range:
		local_id = 13
		if testcase == local_id or test_all:
			execute = True 		
		elif testcase_range and local_id in testcase_list:
			execute = True 
		else:
			execute = False 
		if execute:
			testcase = local_id
			description = "Ingress 2 Color counter types: ingress enable/disable count"
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
			            set count-type all
			            set policer 1
			        end
			        set ingress-interface "port1"         
			    next
				end
				config switch acl egress
			    edit 1
			        config action
			            set count enable
			            set count-type green yellow 
			        end
			        set interface "port2"         
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
				sleep(10)
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
					elif obj.type == "ingress" and ixia_tx  == obj.all_pkts:
						ingress_result = True

					elif obj.type == "egress" and ixia_rx ==obj.green_pkts:
						egress_result = True
				print(f"ingress_result = {ingress_result}")
				print(f"egress_result = {egress_result}")
				test_result = ingress_result and egress_result
				list_results.append(test_result)
				results.append(f"#{i} Testing 2 color ingress counter-type enable/disable successful: {test_result}")

			if list_results.count(True) == len(list_results):
				test_result = True 
			else:
				test_result = False

			final_results.append(f"Testcase #{testcase} Testing on 3032E with 4 color ingress counter-type enable/disable successful: {test_result}")
			for r in results:
				print(r)
			

	if testcase == 14 or test_all or testcase_range:
		local_id = 14
		if testcase == local_id or test_all:
			execute = True 		
		elif testcase_range and local_id in testcase_list:
			execute = True 
		else:
			execute = False 
		if execute:
			testcase = local_id
			description = "Egress 2 Color counter types: egress enable/disable counter"
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
			        set interface "port2"         
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
				sleep(10)
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
					elif obj.type == "egress" and ixia_rx ==obj.green_pkts and abs(ixia_drop - obj.yellow_pkts) < 10:
						test_result =  True
						list_results.append(test_result)

				results.append(f"#{i} Testing 2 color egress enable/disable counter  successful: {test_result}")
				print(f"#{i} Testing egress enable/disable counter  successful: {test_result}")
			if list_results.count(True) == len(list_results):
				test_result = True 
			else:
				test_result = False

			final_results.append(f"Testcase #{testcase} Testing egress counter-type enable/disable successful: {test_result}")
			for r in results:
				print(r)

	if testcase == 15 or test_all or testcase_range:
		local_id = 15
		if testcase == local_id or test_all:
			execute = True 		
		elif testcase_range and local_id in testcase_list:
			execute = True 
		else:
			execute = False 
		if execute:
			testcase = local_id
			description = "Ingress And Egress Multiple ACL counters on the same interface"
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
			            set count enable
			            set count-type all
			            set policer 1
			        end
			        set ingress-interface "port1"         
			    next

			    edit 2
			        config action
			            set count enable
			            set count-type green
			            set policer 1
			        end
			        set ingress-interface "port1"         
			    next

			    edit 3
			        config action
			            set count enable
			            set count-type yellow
			            set policer 1
			        end
			        set ingress-interface "port1"         
			    next

			    edit 4
			        config action
			            set count enable
			            set count-type red
			            set policer 1
			        end
			        set ingress-interface "port1"         
			    next

			    edit 5
			        config action
			            set count enable
			            set count-type green yellow
			            set policer 1
			        end
			        set ingress-interface "port1"         
			    next

			    edit 6
			        config action
			            set count enable
			            set count-type green red
			            set policer 1
			        end
			        set ingress-interface "port1"         
			    next

			    edit 7
			        config action
			            set count enable
			            set count-type yellow red
			            set policer 1
			        end
			        set ingress-interface "port1"         
			    next

				end

				config switch acl egress
			    edit 1
			        config action
			            set count enable
			            set count-type green yellow
			            set policer 2
			        end
			        set interface "port2"         
			    next


			    edit 2
			        config action
			            set count enable
			            set count-type green
			            set policer 2
			        end
			        set interface "port2"         
			    next

			    edit 3
			        config action
			            set count enable
			            set count-type yellow
			            set policer 2
			        end
			        set interface "port2"         
			    next


			   	edit 4
			        config action
			            set count enable
			            set count-type yellow
			            set policer 2
			        end
			        set interface "port2"         
			    next

			    edit 5
			        config action
			            set count enable
			            set count-type green yellow
			            set policer 2
			        end
			        set interface "port2"         
			    next

			    edit 6
			        config action
			            set count enable
			            set count-type green yellow
			            set policer 2
			        end
			        set interface "port2"         
			    next

			    edit 7
			        config action
			            set count enable
			            set count-type yellow green
			            set policer 2
			        end
			        set interface "port2"         
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
				sleep(10)
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
					elif obj.type == "egress" and ixia_rx ==obj.green_pkts:
						test_result =  True
						list_results.append(test_result)

				results.append(f"#{i} Ingress And Egress Multiple ACL counters on the same interfacesuccessful: {test_result}")
				print(f"#{i} Ingress And Egress Multiple ACL counters on the same interface successful: {test_result}")
			if list_results.count(True) == len(list_results):
				test_result = True 
			else:
				test_result = False

			final_results.append(f"Testcase #{testcase} Ingress And Egress Multiple ACL counters on the same interface successful: {test_result}")
			for r in results:
				print(r)

	if testcase == 16 or test_all or testcase_range:
		local_id = 16
		if testcase == local_id or test_all:
			execute = True 		
		elif testcase_range and local_id in testcase_list:
			execute = True 
		else:
			execute = False 
		if execute:
			testcase = local_id
			description = "Delete and configure Ingress and Egress ACL With Traffic"
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
			sw.clear_crash_log()
			myixia.start_traffic()
			for i in range(1):

				cmds = """
				config switch acl ingress

			    edit 1
			        config action
			            set count enable
			            set count-type all
			            set policer 1
			        end
			        set ingress-interface "port1"         
			    next

			    edit 2
			        config action
			            set count enable
			            set count-type green
			            set policer 1
			        end
			        set ingress-interface "port1"         
			    next

			    edit 3
			        config action
			            set count enable
			            set count-type yellow
			            set policer 1
			        end
			        set ingress-interface "port1"         
			    next

			    edit 4
			        config action
			            set count enable
			            set count-type red
			            set policer 1
			        end
			        set ingress-interface "port1"         
			    next

			    edit 5
			        config action
			            set count enable
			            set count-type green yellow
			            set policer 1
			        end
			        set ingress-interface "port1"         
			    next

			    edit 6
			        config action
			            set count enable
			            set count-type green red
			            set policer 1
			        end
			        set ingress-interface "port1"         
			    next

			    edit 7
			        config action
			            set count enable
			            set count-type yellow red
			            set policer 1
			        end
			        set ingress-interface "port1"         
			    next

				end

				config switch acl egress
			    edit 1
			        config action
			            set count enable
			            set count-type green yellow
			            set policer 2
			        end
			        set interface "port2"         
			    next


			    edit 2
			        config action
			            set count enable
			            set count-type green
			            set policer 2
			        end
			        set interface "port2"         
			    next

			    edit 3
			        config action
			            set count enable
			            set count-type yellow
			            set policer 2
			        end
			        set interface "port2"         
			    next


			   	edit 4
			        config action
			            set count enable
			            set count-type yellow
			            set policer 2
			        end
			        set interface "port2"         
			    next

			    edit 5
			        config action
			            set count enable
			            set count-type green yellow
			            set policer 2
			        end
			        set interface "port2"         
			    next

			    edit 6
			        config action
			            set count enable
			            set count-type green yellow
			            set policer 2
			        end
			        set interface "port2"         
			    next

			    edit 7
			        config action
			            set count enable
			            set count-type yellow green
			            set policer 2
			        end
			        set interface "port2"         
			    next

				end
				
				"""
				sw.config_cmds(cmds)
				sleep(3)

				cmd = "execute acl clear-counter all"
				sw.exec_command(cmd)
				sleep(3)
				sw.show_command("get switch acl counters all")
 
			myixia.stop_traffic()
			sw.find_crash()
			sw.get_crash_debug()
			found = sw.get_crash_log()
			test_result = False if found else True

			results.append(f"#{i} Delete and configure Ingress and Egress ACL With Traffic successful: {test_result}")

			final_results.append(f"Testcase #{testcase} Delete and configure Ingress and Egress ACL With Traffic successful: {test_result}")

	if testcase == 17 or test_all:
		testcase = 17
		description = "Ingress 2 Color counter types : Multiple Ingress ports in one ACL"
		print(description)

		results = []
		for i in range(1):
			cmds = """
			config switch acl ingress
				delete 1
				delete 2
				delete 3
				delete 4
				delete 5
				delete 6
				delete 7
				delete 8
			end
			config switch acl egress
				delete 1
				delete 2
				delete 3
				delete 4
				delete 5
				delete 6
				delete 7
				delete 8
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
		            set count-type all
		            set policer 1
		        end
		        set ingress-interface "port1" "port2" "port3" "port4" "port5" "port6" "port7" "port8" "port9"       
		    next
			end
			
			config switch acl egress
		    edit 1
		        config action
		            set count enable
		            set count-type green yellow 
		            set policer 2
		        end
		        set interface "port2"         
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
			sleep(10)
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
					ingress_green_pkts = obj.green_pkts
					 
				print(f"Ingress result: {ingress_result}")
				if obj.type == "egress" and ixia_rx ==obj.green_pkts:
					egress_result = True 
				print(f"Egress result: {egress_result}")
			if ingress_result and egress_result:
				test_result = True
			results.append(f"#{i} Multiple Ingress ports in one ACL successful: {test_result}")
			print(f"#{i} Multiple Ingress ports in one ACL successful: {test_result}")

		final_results.append(f"Testcase #{testcase} Multiple Ingress ports in one ACL successful: {test_result}")
		for r in results:
			print(r)

	if testcase == 18 or test_all or testcase_range:
		local_id = 18
		if testcase == local_id or test_all:
			execute = True 		
		elif testcase_range and local_id in testcase_list:
			execute = True 
		else:
			execute = False 
		if execute:
			testcase = local_id
			description = "Multiple Ingress And Egress ACL counters with different policers"
			print(f"===========Testcase #{testcase}: {description} ==========")

			cmds = """
			config switch acl ingress
				delete 1
				delete 2
				delete 3
				delete 4
				delete 5
				delete 6
				delete 7
				delete 8
			end
			config switch acl egress
				delete 1
				delete 2
				delete 3
				delete 4
				delete 5
				delete 6
				delete 7
				delete 8
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
	   			set guaranteed-bandwidth 10000
	    		set type ingress
			next
			edit 2
	    		set guaranteed-bandwidth 11000
	    		set type ingress
			next
			edit 3
	    		set guaranteed-bandwidth 12000
	    		set type ingress
			next

			edit 4
	    		set guaranteed-bandwidth 13000
	    		set type ingress
			next

			edit 5
	    		set guaranteed-bandwidth 15000
	    		set type ingress
			next

			edit 6
	    		set guaranteed-bandwidth 16000
	    		set type ingress
			next

			edit 7
	    		set guaranteed-bandwidth 17000
	    		set type ingress
			next

			edit 8
	    		set guaranteed-bandwidth 18000
	    		set type ingress
			next

			edit 11
	   			set guaranteed-bandwidth 5100
	    		set type egress
			next
			edit 12
	    		set guaranteed-bandwidth 5200
	    		set type egress
			next
			edit 13
	    		set guaranteed-bandwidth 5300
	    		set type egress
			next

			edit 14
	    		set guaranteed-bandwidth 5400
	    		set type egress
			next

			edit 15
	    		set guaranteed-bandwidth 5500
	    		set type egress
			next

			edit 16
	    		set guaranteed-bandwidth 5600
	    		set type egress
			next

			edit 17
	    		set guaranteed-bandwidth 5700
	    		set type egress
			next

			edit 18
	    		set guaranteed-bandwidth 5800
	    		set type egress
			next

			end
			"""
			sw.config_cmds(cmds)
			sleep(10)

			list_results = []
			results = []
			for i in range(2):

				cmds = """
				config switch acl ingress

			    edit 1
			        config action
			            set count enable
			            set count-type all
			            set policer 1
			        end
			        set ingress-interface "port1"       
			    next

			    edit 2
			        config action
			            set count enable
			            set count-type green
			            set policer 2
			        end
			        set ingress-interface "port1"         
			    next

			    edit 3
			        config action
			            set count enable
			            set count-type yellow
			            set policer 3
			        end
			        set ingress-interface "port1"         
			    next

			    edit 4
			        config action
			            set count enable
			            set count-type red
			            set policer 4
			        end
			        set ingress-interface "port1"         
			    next

			    edit 5
			        config action
			            set count enable
			            set count-type green yellow
			            set policer 5
			        end
			        set ingress-interface "port1"         
			    next

			    edit 6
			        config action
			            set count enable
			            set count-type green red
			            set policer 6
			        end
			        set ingress-interface "port1"         
			    next

			    edit 7
			        config action
			            set count enable
			            set count-type yellow red
			            set policer 7
			        end
			        set ingress-interface "port1"         
			    next

			    edit 8
			        config action
			            set count enable
			            set count-type yellow red
			            set policer 8
			        end
			        set ingress-interface "port1"         
			    next
				end

				config switch acl egress
			    edit 1
			        config action
			            set count enable
			            set count-type yellow green
			            set policer 11
			        end
			        set interface "port2"         
			    next


			    edit 2
			        config action
			            set count enable
			            set count-type green
			            set policer 12
			        end
			        set interface "port2"         
			    next

			    edit 3
			        config action
			            set count enable
			            set count-type yellow
			            set policer 13
			        end
			        set interface "port2"         
			    next


			   	edit 4
			        config action
			            set count enable
			            set count-type yellow
			            set policer 14
			        end
			        set interface "port2"         
			    next

			    edit 5
			        config action
			            set count enable
			            set count-type green yellow
			            set policer 15
			        end
			        set interface "port2"         
			    next

			    edit 6
			        config action
			            set count enable
			            set count-type green yellow
			            set policer 16
			        end
			        set interface "port2"         
			    next

			    edit 7
			        config action
			            set count enable
			            set count-type yellow green
			            set policer 17
			        end
			        set interface "port2"         
			    next

			    edit 8
			        config action
			            set count enable
			            set count-type yellow green
			            set policer 18
			        end
			        set interface "port2"         
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
				sleep(100)
				myixia.stop_traffic()
				sleep(10)
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
					print(f"obj.type,obj.all,obj.green,obj.yellow = {obj.type},{obj.all_pkts},{obj.green_pkts},{obj.yellow_pkts}")
					if obj.type == "ingress" and (obj.all_pkts == 0 or obj.all_pkts == None):
						continue 
					if obj.type == "egress" and (obj.green_pkts == 0 or (obj.green_pkts  == None)):
						continue
					if obj.type == "egress" and abs(ixia_rx- obj.green_pkts) < 20:
						egress_result = True
						continue
					if obj.type == "ingress" and abs(obj.all_pkts - ixia_tx) < 20:
						print("Found ingress none zero entry")
						ingress_result = True 
				print(f"ingress_result:{ingress_result}, egress_result:{egress_result}")
				test_result = ingress_result and egress_result
				results.append(f"#{i} Multiple Ingress And Egress ACL counters with different policers successful: {test_result}")
				print(f"#{i} Multiple Ingress And Egress ACL counters with different policers successful: {test_result}")


			final_results.append(f"Testcase #{testcase} Multiple Ingress And Egress ACL counters with different policers successful: {test_result}")
			for r in results:
				print(r)

	if testcase == 19 or test_all or testcase_range:
		local_id = 19
		if testcase == local_id or test_all:
			execute = True 		
		elif testcase_range and local_id in testcase_list:
			execute = True 
		else:
			execute = False 
		if execute:
			testcase = local_id
			description = "Longevity testing: Multiple Ingress And Egress ACL counters with different policers"
			print(f"===========Testcase #{testcase}: {description} ==========")

			cmds = """
			config switch acl ingress
				delete 1
				delete 2
				delete 3
				delete 4
				delete 5
				delete 6
				delete 7
				delete 8
			end
			config switch acl egress
				delete 1
				delete 2
				delete 3
				delete 4
				delete 5
				delete 6
				delete 7
				delete 8
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
	   			set guaranteed-bandwidth 10000
	    		set type ingress
			next
			edit 2
	    		set guaranteed-bandwidth 11000
	    		set type ingress
			next
			edit 3
	    		set guaranteed-bandwidth 12000
	    		set type ingress
			next

			edit 4
	    		set guaranteed-bandwidth 13000
	    		set type ingress
			next

			edit 5
	    		set guaranteed-bandwidth 15000
	    		set type ingress
			next

			edit 6
	    		set guaranteed-bandwidth 16000
	    		set type ingress
			next

			edit 7
	    		set guaranteed-bandwidth 17000
	    		set type ingress
			next

			edit 8
	    		set guaranteed-bandwidth 18000
	    		set type ingress
			next

			edit 11
	   			set guaranteed-bandwidth 5100
	    		set type egress
			next
			edit 12
	    		set guaranteed-bandwidth 5200
	    		set type egress
			next
			edit 13
	    		set guaranteed-bandwidth 5300
	    		set type egress
			next

			edit 14
	    		set guaranteed-bandwidth 5400
	    		set type egress
			next

			edit 15
	    		set guaranteed-bandwidth 5500
	    		set type egress
			next

			edit 16
	    		set guaranteed-bandwidth 5600
	    		set type egress
			next

			edit 17
	    		set guaranteed-bandwidth 5700
	    		set type egress
			next

			edit 18
	    		set guaranteed-bandwidth 5800
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
			            set count enable
			            set count-type all
			            set policer 1
			        end
			        set ingress-interface "port1"       
			    next

			    edit 2
			        config action
			            set count enable
			            set count-type green
			            set policer 2
			        end
			        set ingress-interface "port1"         
			    next

			    edit 3
			        config action
			            set count enable
			            set count-type yellow
			            set policer 3
			        end
			        set ingress-interface "port1"         
			    next

			    edit 4
			        config action
			            set count enable
			            set count-type red
			            set policer 4
			        end
			        set ingress-interface "port1"         
			    next

			    edit 5
			        config action
			            set count enable
			            set count-type green yellow
			            set policer 5
			        end
			        set ingress-interface "port1"         
			    next

			    edit 6
			        config action
			            set count enable
			            set count-type green red
			            set policer 6
			        end
			        set ingress-interface "port1"         
			    next

			    edit 7
			        config action
			            set count enable
			            set count-type yellow red
			            set policer 7
			        end
			        set ingress-interface "port1"         
			    next

			    edit 8
			        config action
			            set count enable
			            set count-type yellow red
			            set policer 8
			        end
			        set ingress-interface "port1"         
			    next
				end

				config switch acl egress
			    edit 1
			        config action
			            set count enable
			            set count-type yellow green
			            set policer 11
			        end
			        set interface "port2"         
			    next


			    edit 2
			        config action
			            set count enable
			            set count-type green
			            set policer 12
			        end
			        set interface "port2"         
			    next

			    edit 3
			        config action
			            set count enable
			            set count-type yellow
			            set policer 13
			        end
			        set interface "port2"         
			    next


			   	edit 4
			        config action
			            set count enable
			            set count-type yellow
			            set policer 14
			        end
			        set interface "port2"         
			    next

			    edit 5
			        config action
			            set count enable
			            set count-type green yellow
			            set policer 15
			        end
			        set interface "port2"         
			    next

			    edit 6
			        config action
			            set count enable
			            set count-type green yellow
			            set policer 16
			        end
			        set interface "port2"         
			    next

			    edit 7
			        config action
			            set count enable
			            set count-type yellow green
			            set policer 17
			        end
			        set interface "port2"         
			    next

			    edit 8
			        config action
			            set count enable
			            set count-type yellow green
			            set policer 18
			        end
			        set interface "port2"         
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
				sleep(100)
				myixia.stop_traffic()
				sleep(10)
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
					print(f"obj.type,obj.all,obj.green,obj.yellow = {obj.type},{obj.all_pkts},{obj.green_pkts},{obj.yellow_pkts}")
					if obj.type == "ingress" and (obj.all_pkts == 0 or obj.all_pkts == None):
						continue 
					if obj.type == "egress" and (obj.green_pkts == 0 or (obj.green_pkts  == None)):
						continue
					if obj.type == "egress" and abs(ixia_rx- obj.green_pkts) < 20:
						egress_result = True
						continue
					if obj.type == "ingress" and abs(obj.all_pkts - ixia_tx) < 20:
						print("Found ingress none zero entry")
						ingress_result = True 
				print(f"ingress_result:{ingress_result}, egress_result:{egress_result}")
				test_result = ingress_result and egress_result
				results.append(f"#{i} Longevity testing:Multiple Ingress And Egress ACL counters with different policers successful: {test_result}")
				print(f"#{i} Longevity testing:Multiple Ingress And Egress ACL counters with different policers successful: {test_result}")


			final_results.append(f"Testcase #{testcase} Longevity testing:Multiple Ingress And Egress ACL counters with different policers successful: {test_result}")
			for r in results:
				print(r)
 
	print("================================== Final Results ====================================")
	for r in final_results:
		print(r)


##################################################################################################################################################
##################################################################################################################################################
