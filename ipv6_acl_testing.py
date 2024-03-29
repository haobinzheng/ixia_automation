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
	sys.stdout = Logger(f"Log/ACL6_testing.log")
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
	file = 'tbinfo_multi_sw_acl6.xml'
	tb = parse_tbinfo_untangle(file)
	testtopo_file = 'topo_acl6.xml'
	parse_testtopo_untangle(testtopo_file,tb)
	tb.show_tbinfo()

	######## skipping it for ixia trouble shooting
	switches = []
	for d in tb.devices:
		#switch = FortiSwitch_XML(d,topo_db=tb,login_ssh=True,login_console=False)
		switch = FortiSwitch_XML(d,topo_db=tb,login_ssh=True)
		switches.append(switch)
	for c in tb.connections:
		c.update_devices_obj(switches)
	####### skipping it for ixia trouble shooting 
	# for c in tb.connections:
	# 	c.shut_unused_ports()

	sw = switches[0]
	sw1 = switches[1]
	
	apiServerIp = tb.ixia.ixnetwork_server_ip
	ixChassisIpList = [tb.ixia.chassis_ip]
 	
 	############################################### Static Data Are Define Here ########################################################################
	#  ixia_sub_intf can be overriden at each test case
	TEST_VLAN = 10
	TEST_VLAN_NAME = "vlan10"

	mac_list = ["00:11:01:01:01:01","00:12:01:01:01:01","00:13:01:01:01:01","00:14:01:01:01:01","00:15:01:01:01:01","00:16:01:01:01:01","00:17:01:01:01:01","00:18:01:01:01:01"]
	net4_list = ["10.1.1.10/16","10.1.2.10/16","10.1.3.10/16","10.1.4.10/16","10.1.5.10/16","10.1.6.10/16","10.1.7.10/16","10.1.8.10/16","10.1.9.10/16","10.1.10.10/16"]
	gw4_list = ["10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1"]
	net6_list = ["2001:10:1:1::1000/64","2001:10:1:1::2000/64","2001:10:1:1::3000/64","2001:10:1:1::4000/64","2001:10:1:1::5000/64","2001:10:1:1::6000/64","2001:10:1:1::7000/64","2001:10:1:1::8000/64"]
	gw6_list = ["2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1"]

	config_interfaces = False
	#config_interfaces = True
	clean_acl = False
	#clean_acl = True
	config_acl_ingress = False
	#config_acl_ingress = True
	
	# The following can be overriden at each test case based on 1) How many ixia ports you need  2) How many multiplier for each ixia port
	ixia_sub_intf = 10
	portList_v4_v6 = []
	for p,m,n4,g4,n6,g6 in zip(tb.ixia.port_active_list,mac_list,net4_list,gw4_list,net6_list,gw6_list):
		module,port = p.split("/")
		portList_v4_v6.append([ixChassisIpList[0], int(module),int(port),m,n4,g4,n6,g6,ixia_sub_intf])

	print(portList_v4_v6)

	############################################### Static Data Are Define Here ########################################################################
	 
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

	def config_sys_interfaces(sw,*args,**kwargs):
		if "vlan" in kwargs:
			vlan = kwargs["vlan"]
		else:
			vlan = "vlan2"
		vlan_id=re.match(r'vlan([0-9]+)',vlan).group(1)
		cmds = f"""
		config system interface
		delete rvi-1
		delete rvi-2
		edit {vlan}
			set ip {gw4_list[0]} 255.255.0.0
		    config ipv6
                set ip6-address {gw6_list[0]}/64
                set ip6-allowaccess ping https http ssh telnet
                set dhcp6-information-request enable
		        end
		        set vlanid {vlan_id}
		        set interface "internal"
		    next
		end
		end
		"""
		sw.config_cmds_fast(cmds)
		sleep(10)
		for port in sw.ixia_ports:
			cmds = f"""
			config switch interface
				edit {port}
			  	set native-vlan {vlan_id}
			  	end
			"""
			sw.config_cmds_fast(cmds)
			sleep(2)

 
	if config_interfaces == True:
		for dut in switches:
			dut.delete_vlan_interfaces()
			config_sys_interfaces(dut,vlan=TEST_VLAN_NAME)

	if clean_acl == True:
		acl.acl_ingress_clean_up()

	def classifier_combo_testing(*args,**kwargs):
		switch_num = kwargs["switch_num"] - 1 
		sw = switches[switch_num]
		acl = switch_acl_ingress(sw)
		acl.acl_ingress_clean_up()

		
		sample = f"""
		S424EPTF21001277 (1002) # config classifier

		S424EPTF21001277 (classifier) # set
		cos               802.1Q CoS value to be matched (0 - 7).
		dscp              DSCP value to be matched (0 - 63).
		dst-ip-prefix     Destination-ip address to be matched.
		dst-ip6-prefix    Destination-ip6 address to be matched.
		dst-mac           Destination mac address to be matched.
		ether-type        Ether type to be matched (0 - 65535).
		service           Service name.
		src-ip-prefix     Source-ip address to be matched.
		src-ip6-prefix    Source-ip6 address to be matched.
		src-mac           Source mac address to be matched.
		vlan-id           Vlan id to be matched (1 - 4094).
		"""
		classifiers = {}
		globals = {}
		actions = {}
		index = 1
		classifiers = {
		"dst-ip6-prefix": "2001::1/128",
		"src-ip6-prefix": "2001::100/128",
		"cos":"6",
		"dscp":"63",
		"dst-mac":"00:11:11:11:11:11",
		"src-mac":"00:22:22:22:22:22",
		"ether-type":"0x0320",
		"service":"SSH",
		"vlan-id":"1000"
		}

		globals = {
		"group":5,
		 "ingress-interface": sw.ixia_ports[0]
		}
		acl.config_acl6_generic(index,globals,classifiers,actions)
		sleep(3)
		output = collect_show_cmd_general(sw.console,"config switch acl ingress",f"edit {index}","config classifier","show")
		print(output)
		result = convert_config_dict(output)

		print(f"Classifier template = {classifiers}")
		print(f"Actual config result = {result}")
		if classifiers == result:
			Info("Configuration of Classifier was successful")
		else:
			Info("Configuration of Classifier failed")
		
		globals = {}
		actions = {}
		while True:
			key, value = random.choice(list(classifiers.items()))
			# if "vlan-id" in key:
			# 	continue
			# else:
			value =  classifiers.pop(key)
			Info(f"!!!!!!!!!!!!!!!! Popping key={key},value={value} !!!!!!!!!!!!!!!!!")
			cmd = f"""
			config switch acl ingress
			edit {index}
			config classifer
			unset {key}
			end
			end
			"""
			sw.config_cmds_fast(cmd)
			sleep(2)
			read_console(sw.console)
			sleep(2)
			output = collect_show_cmd_general(sw.console,"config switch acl ingress",f"edit {index}","config classifier","show")
			result = convert_config_dict(output)
			print(f"Classifier template = {classifiers}")
			print(f"Actual config result = {result}")
			if classifiers == result:
				Info(f"========= Popping key={key},value={value} was successful")
			else:
				Info(f"========== Popping key={key},value={value} failed")
			classifiers[key] = value
			acl.config_acl6_generic(index,globals,classifiers,actions)
			sleep(2)
			read_console(sw.console)
			output = collect_show_cmd_general(sw.console,"config switch acl ingress",f"edit {index}","config classifier","show")
			result = convert_config_dict(output)
			print(f"Classifier template = {classifiers}")
			print(f"Actual config result = {result}")
			if classifiers == result:
				Info(f"======== Putting back key={key},value={value} was successful")
			else:
				Info(f"========= Putting key={key},value={value} failed")

	def rvi_acl6_testing(*args,**kwargs):

		mac_list = ["00:11:01:01:01:01","00:12:01:01:01:01","00:13:01:01:01:01","00:14:01:01:01:01","00:15:01:01:01:01","00:16:01:01:01:01","00:17:01:01:01:01","00:18:01:01:01:01"]
		net4_list = ["200.1.1.10/24","200.1.2.10/24","200.1.3.10/24","200.1.4.10/24","200.1.5.10/24","200.1.6.10/24","200.1.7.10/24","200.1.8.10/24","200.1.9.10/24","200.1.10.10/24"]
		gw4_list = ["200.1.1.1","200.1.2.1","200.1.3.1","200.1.4.1","200.1.5.1","200.1.6.1","200.1.7.1","200.1.8.1","200.1.9.1","200.1.10.1","200.1.11.1","200.1.12.1","200.1.13.1"]
		net6_list = ["2002:10:1:1::1000/64","2002:10:1:2::1000/64","2002:10:3:1::1000/64","2002:10:1:4::1000/64","2002:10:1:5::1000/64","2002:10:1:6::1000/64","2002:10:1:7::1000/64","2002:10:1:8::1000/64"]
		gw6_list = ["2002:10:1:1::1","2002:10:1:2::1","2002:10:1:3::1","2002:10:1:4::1","2002:10:1:5::1","2002:10:1:6::1","2002:10:1:7::1","2002:10:1:8::1","2002:10:1:9::1"]

		switch_num_list = kwargs["switch_num_list"]
		if "factory" in kwargs:
			factory = kwargs["factory"]
		else:
			factory = False
		for switch_num in switch_num_list:
			#Designate the DUT being tested 
			switch_num = int(switch_num)-1
			sw = switches[switch_num]

			if factory == True:
				sw.factory_and_restore_config()
				config_sys_interfaces(sw,vlan=TEST_VLAN_NAME)

			#define valuables specific to the switch under testing 
			ixia_sub_intf = 10
			portList_v4_v6 = []
			for p,m,n4,g4,n6,g6 in zip(
				tb.ixia.port_active_list[switch_num*2:switch_num*2+2],\
				mac_list[switch_num*2:switch_num*2+2], \
				net4_list[switch_num*2:switch_num*2+2], \
				gw4_list[switch_num*2:switch_num*2+2], \
				net6_list[switch_num*2:switch_num*2+2], \
				gw6_list[switch_num*2:switch_num*2+2]):
				module,port = p.split("/")
				portList_v4_v6.append([ixChassisIpList[0], int(module),int(port),m,n4,g4,n6,g6,ixia_sub_intf])
			
			print(portList_v4_v6)
			mac_base_1=mac_list[switch_num*2]
			mac_base_2=mac_list[switch_num*2+1]
			
			#clean up all ACL (ingress and 802.1x) related configuration
			acl_ingress = switch_acl_ingress(switches[switch_num])
			acl_ingress.acl_ingress_clean_up()

			cmds = f"""
			config system interface
			edit rvi-1
			    set type physical
	        	set l2-interface {sw.ixia_ports[0]}
				set ip {gw4_list[switch_num*2]} 255.255.255.0
			    config ipv6
	                set ip6-address {gw6_list[switch_num*2]}/64
	                set ip6-allowaccess ping https http ssh telnet
	                set dhcp6-information-request enable
			        end
			    next
			edit rvi-2
			    set type physical
	        	set l2-interface {sw.ixia_ports[1]}
				set ip {gw4_list[switch_num*2+1]} 255.255.255.0
			    config ipv6
	                set ip6-address {gw6_list[switch_num*2+1]}/64
	                set ip6-allowaccess ping https http ssh telnet
	                set dhcp6-information-request enable
			        end
			    next
			 end
			end
			"""
			sw.config_cmds_fast(cmds)
			#start configuring ACL 802.1x related configuration
			for i in range(ixia_sub_intf):
				#start configuring ACL ingress configuration
				acl_yaml = f"""
                index: {1+i}
                classifiers:
                 dst-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2+1].split("/")[0])+i}
                 src-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2].split("/")[0])+i}
                 src-mac: {increment_macaddr(mac_base_1,i)}
                globals_config:
                  group: 4
                  ingress-interface: {sw.ixia_ports[0]}
                actions:
                  count: "enable"
                  count-type: "all green red yellow"
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)

				acl_yaml = f"""
                index: {1000+i}
                classifiers:
                 dst-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2].split("/")[0])+i}
                 src-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2+1].split("/")[0])+i}
                 src-mac: {increment_macaddr(mac_base_2,i)}
                globals_config:
                  group: 4
                  ingress-interface: {sw.ixia_ports[1]}
                actions:
                  count: "enable"
                  count-type: "all green red yellow"
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)	

				acl_yaml = f"""
                index: {500+i}
                classifiers:
                 dst-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2+1].split("/")[0])+i}/32
                 src-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2].split("/")[0])+i}/32
                 src-mac: {increment_macaddr(mac_base_1,i)}
                globals_config:
                  group: 1
                  ingress-interface: {sw.ixia_ports[0]}
                actions:
                  count: "enable"
                  count-type: "all green red yellow"
                """

				acl_ingress.config_acl_ingress_jinja(acl_yaml)	
				acl_yaml = f"""
                index: {1500+i}
                classifiers:
                 dst-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2].split("/")[0])+i}/32
                 src-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2+1].split("/")[0])+i}/32
                 src-mac: {increment_macaddr(mac_base_2,i)}
                globals_config:
                  group: 1
                  ingress-interface: {sw.ixia_ports[1]}
                actions:
                  count: "enable"
                  count-type: "all green red yellow"
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)		 
		 
			#format of this method: config_explicit_drop(self,index,group,intf)
			# acl.config_explicit_drop(ixia_sub_intf+2,3,sw.ixia_ports[0])
			# acl.config_explicit_drop(ixia_sub_intf+1002,3,sw.ixia_ports[1])
			

 			#Start configurating IXIA 
			#myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6[switch_num*2:switch_num*2+2])
			myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)
			for topo in myixia.topologies:
				topo.add_ipv4(gateway="fixed",ip_incremental="0.0.0.1")
				topo.add_ipv6(gateway="fixed")
				
			myixia.start_protocol(wait=20)

			# for i in range(0,len(tb.ixia.port_active_list)-1):
			# 	for j in range(i+1,len(tb.ixia.port_active_list)):
			 
			for i in range(0,1):
				for j in range(1,2):
					myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=5)
					myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=5)
					myixia.create_traffic_v6(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v6",tracking_name=f"Tracking_{i+1}_{j+1}_v6",rate=5)
					myixia.create_traffic_v6(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v6",tracking_name=f"Tracking_{j+1}_{i+1}_v6",rate=5)

			myixia.start_traffic()
			sleep(5)
			myixia.stop_traffic()
			sleep(10)
			myixia.collect_stats()
			myixia.check_traffic()
			sw.print_show_command(f"get switch acl usage",mode="fast")
			sw.print_show_command(f"get switch acl counter all",mode="fast")
			sw.print_show_command(f"show switch acl ingress",mode="fast")
			#sw.fnsysctl_bcm_output()

			Info("Shut down RVI interfaces.... then check ingress ACL works")
			cmds = f"""
			config system interface
			edit rvi-1
			    set status down
			    next
			edit rvi-2
			    set status down
			    next
			end
			end
			"""
			sw.config_cmds_fast(cmds)
			sleep(3)
			myixia.start_traffic()
			sleep(5)
			myixia.stop_traffic()
			sleep(10)
			myixia.collect_stats()
			myixia.check_traffic()
			print_double_line()
			k = input(f"Please verify all the command output,Do you want to remove RVIconfigurations(Y/N):")
			print_double_line()
			sleep(5)
			if k =="yes" or k=="y" or k=="Y" or k=="Yes":
				Info("Removing RVI interfaces configuration.......")
				cmds = f"""
				config system interface
				delete rvi-1    
				delete rvi-2
				end
				"""
				sw.config_cmds_fast(cmds)


	def multiple_rules_acl6_testing(*args,**kwargs):
		# switches = []
		# for d in tb.devices:
		# 	switch = FortiSwitch_XML(d,topo_db=tb)
		# 	switches.append(switch)
		# for c in tb.connections:
		# 	c.update_devices_obj(switches)

		switch_num_list = kwargs["switch_num_list"]
		if "factory" in kwargs:
			factory = kwargs["factory"]
		else:
			factory = False
		for switch_num in switch_num_list:
			#Designate the DUT being tested 
			switch_num = int(switch_num)-1
			sw = switches[switch_num]

			if factory == True:
				sw.factory_and_restore_config()
				config_sys_interfaces(sw,vlan=TEST_VLAN_NAME)
			else:
				acl_dot1x = switch_acl_dotonex(sw)
				acl_ingress = switch_acl_ingress(switches[switch_num])
				dot1x = DotOnex(sw,user_group="group_10",secrete="fortinet123",server="10.105.252.122",user="lab",port_list=[sw.ixia_ports[0],sw.ixia_ports[1]])
				acl_ingress.acl_ingress_clean_up()
				acl_dot1x.acl_dot1x_clean_up(f"dot1x_filter_{switch_num+1}")
				dot1x.dot1x_remove_config()
			#define valuables specific to the switch under testing 
			ixia_sub_intf = 1
			portList_v4_v6 = []
			for p,m,n4,g4,n6,g6 in zip(
				tb.ixia.port_active_list[switch_num*2:switch_num*2+2],\
				mac_list[switch_num*2:switch_num*2+2], \
				net4_list[switch_num*2:switch_num*2+2], \
				gw4_list[switch_num*2:switch_num*2+2], \
				net6_list[switch_num*2:switch_num*2+2], \
				gw6_list[switch_num*2:switch_num*2+2]):
				module,port = p.split("/")
				portList_v4_v6.append([ixChassisIpList[0], int(module),int(port),m,n4,g4,n6,g6,ixia_sub_intf])
			
			print(portList_v4_v6)
			mac_base_1=mac_list[switch_num*2]
			mac_base_2=mac_list[switch_num*2+1]
			

			#start configuring ACL ingress related configuration
			for i in range(ixia_sub_intf):
				#start configuring ACL ingress configuration
				acl_yaml = f"""
                index: {1+i}
                classifiers:
                 dst-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2+1].split("/")[0])+i}
                 src-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2].split("/")[0])+i}
                globals_config:
                 group: 4
                 ingress-interface: {sw.ixia_ports[0]}
                actions:
                  count: "enable"
                  drop: "enable"
                  count-type: "green red"
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)

				acl_yaml = f"""
                index: {200+i}
                classifiers:
                 dst-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2+1].split("/")[0])+i}
                globals_config:
                 group: 4
                 ingress-interface: {sw.ixia_ports[0]}
                actions:
                 count: "enable"
                 count-type: "green red"
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)

				acl_yaml = f"""
                index: {1000+i}
                classifiers:
                 dst-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2].split("/")[0])+i}
                 src-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2+1].split("/")[0])+i}
                globals_config:
                  group: 4
                  ingress-interface: {sw.ixia_ports[1]}
                actions:
                  count: "enable"
                  count-type: "green red"
                  drop: "enable"
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)	

				acl_yaml = f"""
                index: {1200+i}
                classifiers:
                 dst-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2].split("/")[0])+i}
                globals_config:
                  group: 4
                  ingress-interface: {sw.ixia_ports[1]}
                actions:
                  count: "enable"
                  count-type: "green red"
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)	

				acl_yaml = f"""
                index: {500+i}
                classifiers:
                 dst-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2+1].split("/")[0])+i}/32
                 src-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2].split("/")[0])+i}/32
                globals_config:
                  group: 1
                  ingress-interface: {sw.ixia_ports[0]}
                actions:
                  count: "enable"
                  drop: "enable"
                  count-type: "green red"
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)

				acl_yaml = f"""
                index: {700+i}
                classifiers:
                  dst-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2+1].split("/")[0])+i}/32
                globals_config:
                  group: 1
                  ingress-interface: {sw.ixia_ports[0]}
                actions:
                  count: "enable"
                  count-type: "green red"
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)		

				acl_yaml = f"""
                index: {1500+i}
                classifiers:
                 dst-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2].split("/")[0])+i}/32
                 src-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2+1].split("/")[0])+i}/32
                globals_config:
                  group: 1
                  ingress-interface: {sw.ixia_ports[1]}
                actions:
                  count: "enable"
                  count-type: "green red"
                  drop: "enable"
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)	

				acl_yaml = f"""
                index: {1700+i}
                classifiers:
                 dst-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2].split("/")[0])+i}/32
                globals_config:
                  group: 1
                  ingress-interface: {sw.ixia_ports[1]}
                actions:
                  count: "enable"
                  count-type: "green red"
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)		 
		 
			#format of this method: config_explicit_drop(self,index,group,intf)
			# acl.config_explicit_drop(ixia_sub_intf+2,3,sw.ixia_ports[0])
			# acl.config_explicit_drop(ixia_sub_intf+1002,3,sw.ixia_ports[1])
			

 			#Start configurating IXIA 
			#myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6[switch_num*2:switch_num*2+2])
			myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)
			for topo in myixia.topologies:
				#topo.add_ipv4(gateway="fixed",ip_incremental="0.0.0.1")
				topo.add_ipv6(gateway="fixed")
				
			myixia.start_protocol(wait=20)

			for i in range(0,1):
				for j in range(1,2):
					# myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=5)
					# myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=5)
					myixia.create_traffic_v6(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v6",tracking_name=f"Tracking_{i+1}_{j+1}_v6",rate=5)
					myixia.create_traffic_v6(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v6",tracking_name=f"Tracking_{j+1}_{i+1}_v6",rate=5)
			try:
				myixia.start_traffic()
				sleep(5)
				myixia.stop_traffic()
				sleep(10)
				myixia.collect_stats()
				myixia.check_traffic()
			except Exception:
				Info("Can not start traffic after multiple matched polices Drop/Forward")

			sw.print_show_command(f"get switch acl usage",mode="fast")
			sw.print_show_command(f"get switch acl counter all",mode="fast")
			sw.print_show_command(f"show switch acl ingress",mode="fast")
			#sw.fnsysctl_bcm_output()

			print_double_line()
			k = input(f"Please verify drop/count,Do you want to test count/drop config(Y/N):")
			print_double_line()
			sleep(5)
			if k =="No" or k=="n" or k=="N" or k=="No":
				exit()
			Info("Reconfig ingress ACL for count/drop rules matching the same packet .......")
			Info("First clean up ACL ingress.....")
			acl_ingress.acl_ingress_clean_up()
			sleep(5)
			acl_yaml = f"""
            index: {1+i}
            classifiers:
             dst-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2+1].split("/")[0])+i}
             src-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2].split("/")[0])+i}
            globals_config:
             group: 4
             ingress-interface: {sw.ixia_ports[0]}
            actions:
              count: "enable"
              count-type: "green red"
            """
			acl_ingress.config_acl_ingress_jinja(acl_yaml)

			acl_yaml = f"""
            index: {200+i}
            classifiers:
             dst-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2+1].split("/")[0])+i}
            globals_config:
             group: 4
             ingress-interface: {sw.ixia_ports[0]}
            actions:
             count: "enable"
             count-type: "green red"
             drop: "enable"
            """
			acl_ingress.config_acl_ingress_jinja(acl_yaml)

			acl_yaml = f"""
            index: {1000+i}
            classifiers:
             dst-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2].split("/")[0])+i}
             src-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2+1].split("/")[0])+i}
            globals_config:
              group: 4
              ingress-interface: {sw.ixia_ports[1]}
            actions:
              count: "enable"
              count-type: "green red"   
            """
			acl_ingress.config_acl_ingress_jinja(acl_yaml)	

			acl_yaml = f"""
            index: {1200+i}
            classifiers:
             dst-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2].split("/")[0])+i}
            globals_config:
              group: 4
              ingress-interface: {sw.ixia_ports[1]}
            actions:
              count: "enable"
              count-type: "green red"
              drop: "enable"
            """
			acl_ingress.config_acl_ingress_jinja(acl_yaml)	

			acl_yaml = f"""
            index: {500+i}
            classifiers:
             dst-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2+1].split("/")[0])+i}/32
             src-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2].split("/")[0])+i}/32
            globals_config:
              group: 1
              ingress-interface: {sw.ixia_ports[0]}
            actions:
              count: "enable"
              count-type: "green red"
            """
			acl_ingress.config_acl_ingress_jinja(acl_yaml)

			acl_yaml = f"""
            index: {700+i}
            classifiers:
              dst-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2+1].split("/")[0])+i}/32
            globals_config:
              group: 1
              ingress-interface: {sw.ixia_ports[0]}
            actions:
              count: "enable"
              drop: "enable"
              count-type: "green red"
            """
			acl_ingress.config_acl_ingress_jinja(acl_yaml)		

			acl_yaml = f"""
            index: {1500+i}
            classifiers:
             dst-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2].split("/")[0])+i}/32
             src-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2+1].split("/")[0])+i}/32
            globals_config:
              group: 1
              ingress-interface: {sw.ixia_ports[1]}
            actions:
              count: "enable"
              count-type: "green red"
            """
			acl_ingress.config_acl_ingress_jinja(acl_yaml)	

			acl_yaml = f"""
            index: {1700+i}
            classifiers:
             dst-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2].split("/")[0])+i}/32
            globals_config:
              group: 1
              ingress-interface: {sw.ixia_ports[1]}
            actions:
              count: "enable"
              count-type: "green red"
              drop: "enable"
            """
			acl_ingress.config_acl_ingress_jinja(acl_yaml)	

			myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)
			for topo in myixia.topologies:
				#topo.add_ipv4(gateway="fixed",ip_incremental="0.0.0.1")
				topo.add_ipv6(gateway="fixed")
				
			myixia.start_protocol(wait=20)

			for i in range(0,1):
				for j in range(1,2):
					# myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=5)
					# myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=5)
					myixia.create_traffic_v6(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v6",tracking_name=f"Tracking_{i+1}_{j+1}_v6",rate=5)
					myixia.create_traffic_v6(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v6",tracking_name=f"Tracking_{j+1}_{i+1}_v6",rate=5)

			try:
				myixia.start_traffic()
				sleep(5)
				myixia.stop_traffic()
				sleep(10)
				myixia.collect_stats()
				myixia.check_traffic() 
			except Exception:
				Info("!!!!!!!! Can not start traffic after multiple matched polices Forward/Drop!!!!!!!!!")

			k = input(f"Please verify drop/count,Do you want to delete all the drop clause and test again(Y/N):")
			if k =="No" or k=="n" or k=="N" or k=="No":
				return
			for i in range(ixia_sub_intf):
				cmds = f"""
				config switch acl ingress
				delete {200+i}
				delete {1200+i}
				delete {700+i}
				delete {1700+i}
				end
				"""
				sw.config_cmds_fast(cmds)

			myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)
			for topo in myixia.topologies:
				#topo.add_ipv4(gateway="fixed",ip_incremental="0.0.0.1")
				topo.add_ipv6(gateway="fixed")
				
			myixia.start_protocol(wait=20)

			for i in range(0,1):
				for j in range(1,2):
					# myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=5)
					# myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=5)
					myixia.create_traffic_v6(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v6",tracking_name=f"Tracking_{i+1}_{j+1}_v6",rate=5)
					myixia.create_traffic_v6(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v6",tracking_name=f"Tracking_{j+1}_{i+1}_v6",rate=5)

			try:
				myixia.start_traffic()
				sleep(5)
				myixia.stop_traffic()
				sleep(10)
				myixia.collect_stats()
				myixia.check_traffic() 
			except Exception:
				Info("!!!!!! Can not start traffic after deleting all drop polices!!!!!!!!!")

	def dot1x_acl6_testing_yaml(*args,**kwargs):
		switch_num_list = kwargs["switch_num_list"]
		if "factory" in kwargs:
			factory = kwargs["factory"]
		else:
			factory = False
		for switch_num in switch_num_list:
			#Designate the DUT being tested 
			switch_num = int(switch_num)-1
			sw = switches[switch_num]

			if factory == True:
				sw.factory_and_restore_config()
				config_sys_interfaces(sw,vlan=TEST_VLAN_NAME)

			#define valuables specific to the switch under testing 
			ixia_sub_intf = 2
			portList_v4_v6 = []
			for p,m,n4,g4,n6,g6 in zip(
				tb.ixia.port_active_list[switch_num*2:switch_num*2+2],\
				mac_list[switch_num*2:switch_num*2+2], \
				net4_list[switch_num*2:switch_num*2+2], \
				gw4_list[switch_num*2:switch_num*2+2], \
				net6_list[switch_num*2:switch_num*2+2], \
				gw6_list[switch_num*2:switch_num*2+2]):
				module,port = p.split("/")
				portList_v4_v6.append([ixChassisIpList[0], int(module),int(port),m,n4,g4,n6,g6,ixia_sub_intf])
			
			print(portList_v4_v6)
			mac_base_1=mac_list[switch_num*2]
			mac_base_2=mac_list[switch_num*2+1]
			
			#clean up all ACL (ingress and 802.1x) related configuration
			acl_dot1x = switch_acl_dotonex(sw)
			acl_ingress = switch_acl_ingress(switches[switch_num])
			dot1x = DotOnex(sw,user_group="group_10",secrete="fortinet123",server="10.105.252.122",user="lab")
			acl_ingress.acl_ingress_clean_up()
			acl_dot1x.acl_dot1x_clean_up(f"dot1x_filter_{switch_num+1}")
			dot1x.dot1x_remove_config()

			#start configuring 802.1x global and interface configuration
			dot1x.dot1x_global_config()
			dot1x.dot1x_interface_config(port_list=[sw.ixia_ports[0],sw.ixia_ports[1]])

			#start configuring ACL 802.1x related configuration
			for i in range(ixia_sub_intf):
				dot1x_yaml = f"""
                filter_name: dot1x_filter_{switch_num+1}
                acl_index: {1+i}
                entries: 
                  - index: 1
                    group_id: 3
                    classifiers:
                      src-mac: {increment_macaddr(mac_base_1,i)}
                    actions:
                      count: "enable"
                      drop: "enable"
                  - index: 2
                    group_id: 3
                    classifiers:
                      src-mac: {increment_macaddr(mac_base_2,i)}
                    actions:
                      count: "enable"
                      drop: "enable"
                globals_config:
                  filter-id: dot1x_filter_{switch_num+1}
                  description: acl_8021x_{i+1}
                """
				acl_dot1x.config_acl_dotonex_jinja(dot1x_yaml)

				#start configuring ACL ingress configuration
				acl_yaml = f"""
                index: {1+i}
                classifiers:
                 dst-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2+1].split("/")[0])+i}
                 src-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2].split("/")[0])+i}
                 src-mac: {increment_macaddr(mac_base_1,i)}
                globals_config:
                  group: 4
                  ingress-interface: {sw.ixia_ports[0]}
                actions:
                  count: "enable"
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)

				acl_yaml = f"""
                index: {1000+i}
                classifiers:
                 dst-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2].split("/")[0])+i}
                 src-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2+1].split("/")[0])+i}
                 src-mac: {increment_macaddr(mac_base_2,i)}
                globals_config:
                  group: 4
                  ingress-interface: {sw.ixia_ports[1]}
                actions:
                  count: "enable"
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)	

				acl_yaml = f"""
                index: {500+i}
                classifiers:
                 dst-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2+1].split("/")[0])+i}/32
                 src-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2].split("/")[0])+i}/32
                 src-mac: {increment_macaddr(mac_base_1,i)}
                globals_config:
                  group: 1
                  ingress-interface: {sw.ixia_ports[0]}
                actions:
                  count: "enable"
                """

				acl_ingress.config_acl_ingress_jinja(acl_yaml)	
				acl_yaml = f"""
                index: {1500+i}
                classifiers:
                 dst-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2].split("/")[0])+i}/32
                 src-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2+1].split("/")[0])+i}/32
                 src-mac: {increment_macaddr(mac_base_2,i)}
                globals_config:
                  group: 1
                  ingress-interface: {sw.ixia_ports[1]}
                actions:
                  count: "enable"
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)		 
		 
			#format of this method: config_explicit_drop(self,index,group,intf)
			# acl.config_explicit_drop(ixia_sub_intf+2,3,sw.ixia_ports[0])
			# acl.config_explicit_drop(ixia_sub_intf+1002,3,sw.ixia_ports[1])
			

 			#Start configurating IXIA 
			#myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6[switch_num*2:switch_num*2+2])
			myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)
			for topo in myixia.topologies:
				topo.add_dot1x_client()
				topo.add_ipv4(gateway="fixed",ip_incremental="0.0.0.1")
				topo.add_ipv6(gateway="fixed")
				
			myixia.start_protocol(wait=20)

			# for i in range(0,len(tb.ixia.port_active_list)-1):
			# 	for j in range(i+1,len(tb.ixia.port_active_list)):
			 
			for i in range(0,1):
				for j in range(1,2):
					myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=5)
					myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=5)
					myixia.create_traffic_v6(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v6",tracking_name=f"Tracking_{i+1}_{j+1}_v6",rate=5)
					myixia.create_traffic_v6(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v6",tracking_name=f"Tracking_{j+1}_{i+1}_v6",rate=5)

			myixia.start_traffic()
			sleep(5)
			myixia.stop_traffic()
			sleep(10)
			myixia.collect_stats()
			myixia.check_traffic()
			sw.print_show_command(f"get switch acl usage",mode="fast")
			sw.print_show_command(f"get switch acl counter all",mode="fast")
			sw.print_show_command(f"show switch acl ingress",mode="fast")
			sw.print_show_command(f"show switch acl 802-1X",mode="fast")
			sw.print_show_command(f"show switch acl service custom dot1x_filter_{switch_num+1}",mode="fast")
			sw.print_show_command(f"diagnose switch 802-1x status {sw.ixia_ports[0]}",mode="fast")
			sw.print_show_command(f"diagnose switch 802-1x status {sw.ixia_ports[1]}",mode="fast") 
			sw.print_show_command(f"diagnose switch 802-1x status-dacl {sw.ixia_ports[0]}",mode="fast")
			sw.print_show_command(f"diagnose switch 802-1x status-dacl {sw.ixia_ports[1]}",mode="fast") 
			sw.fnsysctl_bcm_output()
			print_double_line()
			k = input(f"Please verify all the command output,Do you want to remove 802.1x configurations(Y/N):")
			print_double_line()
			sleep(5)
			if k =="yes" or k=="y" or k=="Y" or k=="Yes":
				Info("Removing All 802.1x related configuration.......")
				# acl_dot1x.remove_acl_dotonex_simple(filter_name=f"dot1x_filter_{switch_num+1}",acl_index=1)
				dot1x_remove_yaml = f"""
	            filter_name: dot1x_filter_{switch_num+1}
	            acl_length: {ixia_sub_intf}
	            """

				#acl_dot1x.remove_acl_dot1x_jinja(dot1x_remove_yaml) #
				acl_dot1x.acl_dot1x_clean_up(f"dot1x_filter_{switch_num+1}") #this is more general way to remove all acl 802.1x config. Need to test
				dot1x.dot1x_remove_config()

	def cpu_queue_acl6_testing(*args,**kwargs):
		switch_num_list = kwargs["switch_num_list"]
		if "factory" in kwargs:
			factory = kwargs["factory"]
		else:
			factory = False
		for switch_num in switch_num_list:
			#Designate the DUT being tested 
			switch_num = int(switch_num)-1
			sw = switches[switch_num]
			#sw.switch_reboot_login()

			if factory == True:
				sw.factory_and_restore_config()
				config_sys_interfaces(sw,vlan=TEST_VLAN_NAME)

			#define valuables specific to the switch under testing 
			ixia_sub_intf = 1
			portList = []
			for p in tb.ixia.port_active_list[switch_num*2:switch_num*2+2]:
				module,port = p.split("/")
				portList.append([ixChassisIpList[0], int(module),int(port)])
			
			print(portList)
			mac_base_1=mac_list[switch_num*2]
			mac_base_2=mac_list[switch_num*2+1]
			
			#clean up all ACL (ingress and 802.1x) related configuration
			acl_dot1x = switch_acl_dotonex(sw)
			acl_ingress = switch_acl_ingress(switches[switch_num])
			dot1x = DotOnex(sw,user_group="group_10",secrete="fortinet123",server="10.105.252.122",user="lab")
			acl_ingress.acl_ingress_clean_up()
			acl_dot1x.acl_dot1x_clean_up(f"dot1x_filter_{switch_num+1}")
			dot1x.dot1x_remove_config()

			#start configuring ACL 802.1x related configuration
			dst_ipv6_list_1 = []
			dst_ipv6_list_2 = []
			src_ipv6_base_1 = str(ipaddress.IPv6Address(net6_list[switch_num*2].split("/")[0]))
			src_ipv6_base_2 = str(ipaddress.IPv6Address(net6_list[switch_num*2+1].split("/")[0]))
			print(f"src_ip6 = {src_ipv6_base_1},{src_ipv6_base_2} ")
			for i in range(ixia_sub_intf):
				#start configuring ACL ingress configuration
				dst_ipv6_list_1.append(str(ipaddress.IPv6Address(net6_list[switch_num*2+1].split("/")[0])+i))
				dst_ipv6_list_2.append(str(ipaddress.IPv6Address(net6_list[switch_num*2].split("/")[0])+i))
				acl_yaml = f"""
                index: {1+i}
                classifiers:
                 dst-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2+1].split("/")[0])+i}
                 src-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2].split("/")[0])+i}
                globals_config:
                  group: 4
                  ingress-interface: {sw.ixia_ports[0]}
                actions:
                  count: "enable"
                  cpu-cos-queue: 18
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)

				acl_yaml = f"""
                index: {1000+i}
                classifiers:
                 dst-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2].split("/")[0])+i}
                 src-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2+1].split("/")[0])+i}
                globals_config:
                  group: 4
                  ingress-interface: {sw.ixia_ports[1]}
                actions:
                  count: "enable"
                  cpu-cos-queue: 18
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)	

				acl_yaml = f"""
                index: {500+i}
                classifiers:
                 dst-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2+1].split("/")[0])+i}/32
                 src-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2].split("/")[0])+i}/32
                globals_config:
                  group: 1
                  ingress-interface: {sw.ixia_ports[0]}
                actions:
                  count: "enable"
                  cpu-cos-queue: 18
                """

				acl_ingress.config_acl_ingress_jinja(acl_yaml)	
				acl_yaml = f"""
                index: {1500+i}
                classifiers:
                 dst-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2].split("/")[0])+i}/32
                 src-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2+1].split("/")[0])+i}/32
                globals_config:
                  group: 1
                  ingress-interface: {sw.ixia_ports[1]}
                actions:
                  count: "enable"
                  cpu-cos-queue: 18
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)		 
		 
			#format of this method: config_explicit_drop(self,index,group,intf)
			# acl.config_explicit_drop(ixia_sub_intf+2,3,sw.ixia_ports[0])
			# acl.config_explicit_drop(ixia_sub_intf+1002,3,sw.ixia_ports[1])
			
			print(f"dst_ipv6_list = {dst_ipv6_list_1},{dst_ipv6_list_2} ")
			#Start configurating IXIA 
			myixia = IXIA_Raw_Traffic(apiServerIp,ixChassisIpList,portList)
		 
			myixia.generate_ipv6_raw_traffic(
			src_port="Port_1",
			dst_port="Port_2",
			dst_mac = "FF:FF:FF:FF:FF:FF",
			dst_mac_count = 1,
			src_mac="00:0c:29:68:05:14",
			src_mac_count = ixia_sub_intf,
			vlan_id = 10,
			dst_ipv6_list = dst_ipv6_list_1,
			src_ipv6 = src_ipv6_base_1,
			src_ipv6_count = ixia_sub_intf,
			l4_protocol = "udp"
			)

			myixia.generate_ipv6_raw_traffic(
			src_port="Port_2",
			dst_port="Port_1",
			dst_mac = "FF:FF:FF:FF:FF:FF",
			dst_mac_count = 1,
			src_mac="00:0c:29:68:05:14",
			src_mac_count = ixia_sub_intf,
			vlan_id = 10,
			dst_ipv6_list = dst_ipv6_list_2,
			src_ipv6 = src_ipv6_base_2,
			src_ipv6_count = ixia_sub_intf,
			l4_protocol = "tcp"
			)
			myixia.start_raw_traffic()
			sleep(5)
			
			sw.print_show_command(f"get switch acl usage",mode="fast")
			sw.print_show_command(f"get switch acl counter all",mode="fast")
			sw.print_show_command(f"show switch acl ingress",mode="fast")
			sw.print_show_command(f"diagnose switch physical-ports qos-stats non-zero",mode="fast")
			sw.print_show_command(f"diagnose switch physical-ports qos-stats non-zero",mode="fast")

			print_double_line()
			k = input(f"Please verify all the command output,press any key to finish:")
			print_double_line()
			myixia.stop_raw_traffic()
			sleep(10)
		 

	def pbr_acl6_testing(*args,**kwargs):
		switch_num_list = kwargs["switch_num_list"]
		if "factory" in kwargs:
			factory = kwargs["factory"]
		else:
			factory = False
		for switch_num in switch_num_list:
			#Designate the DUT being tested 
			switch_num = int(switch_num)-1
			sw = switches[switch_num]

			if factory == True:
				sw.factory_and_restore_config()
				config_sys_interfaces(sw,vlan=TEST_VLAN_NAME)

			#define valuables specific to the switch under testing 
			ixia_sub_intf = 1
			portList_v4_v6 = []
			for p,m,n4,g4,n6,g6 in zip(
				tb.ixia.port_active_list[switch_num*2:switch_num*2+2],\
				mac_list[switch_num*2:switch_num*2+2], \
				net4_list[switch_num*2:switch_num*2+2], \
				gw4_list[switch_num*2:switch_num*2+2], \
				net6_list[switch_num*2:switch_num*2+2], \
				gw6_list[switch_num*2:switch_num*2+2]):
				module,port = p.split("/")
				portList_v4_v6.append([ixChassisIpList[0], int(module),int(port),m,n4,g4,n6,g6,ixia_sub_intf])
			
			print(portList_v4_v6)
			mac_base_1=mac_list[switch_num*2]
			mac_base_2=mac_list[switch_num*2+1]
			
			#clean up all ACL (ingress and 802.1x) related configuration
			acl_dot1x = switch_acl_dotonex(sw)
			acl_ingress = switch_acl_ingress(switches[switch_num])
			dot1x = DotOnex(sw,user_group="group_10",secrete="fortinet123",server="10.105.252.122",user="lab")
			acl_ingress.acl_ingress_clean_up()
			acl_dot1x.acl_dot1x_clean_up(f"dot1x_filter_{switch_num+1}")
			dot1x.dot1x_remove_config()

			#start configuring ACL 802.1x related configuration
			for i in range(ixia_sub_intf):
				#start configuring ACL ingress configuration
				acl_yaml = f"""
                index: {1+i}
                classifiers:
                 dst-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2+1].split("/")[0])+i}
                 src-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2].split("/")[0])+i}
                 src-mac: {increment_macaddr(mac_base_1,i)}
                globals_config:
                  group: 4
                  ingress-interface: {sw.ixia_ports[0]}
                actions:
                  count: "enable"
                  cpu-cos-queue: 18
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)

				acl_yaml = f"""
                index: {1000+i}
                classifiers:
                 dst-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2].split("/")[0])+i}
                 src-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2+1].split("/")[0])+i}
                 src-mac: {increment_macaddr(mac_base_2,i)}
                globals_config:
                  group: 4
                  ingress-interface: {sw.ixia_ports[1]}
                actions:
                  count: "enable"
                  cpu-cos-queue: 18
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)	

				acl_yaml = f"""
                index: {500+i}
                classifiers:
                 dst-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2+1].split("/")[0])+i}/32
                 src-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2].split("/")[0])+i}/32
                 src-mac: {increment_macaddr(mac_base_1,i)}
                globals_config:
                  group: 1
                  ingress-interface: {sw.ixia_ports[0]}
                actions:
                  count: "enable"
                  cpu-cos-queue: 18
                """

				acl_ingress.config_acl_ingress_jinja(acl_yaml)	
				acl_yaml = f"""
                index: {1500+i}
                classifiers:
                 dst-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2].split("/")[0])+i}/32
                 src-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2+1].split("/")[0])+i}/32
                 src-mac: {increment_macaddr(mac_base_2,i)}
                globals_config:
                  group: 1
                  ingress-interface: {sw.ixia_ports[1]}
                actions:
                  count: "enable"
                  cpu-cos-queue: 18
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)		 
		 
			#format of this method: config_explicit_drop(self,index,group,intf)
			# acl.config_explicit_drop(ixia_sub_intf+2,3,sw.ixia_ports[0])
			# acl.config_explicit_drop(ixia_sub_intf+1002,3,sw.ixia_ports[1])
			

 			#Start configurating IXIA 
			#myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6[switch_num*2:switch_num*2+2])
			myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)
			for topo in myixia.topologies:
				topo.add_ipv4(gateway="fixed",ip_incremental="0.0.0.1")
				topo.add_ipv6(gateway="fixed")
				
			myixia.start_protocol(wait=20)

			# for i in range(0,len(tb.ixia.port_active_list)-1):
			# 	for j in range(i+1,len(tb.ixia.port_active_list)):
			 
			for i in range(0,1):
				for j in range(1,2):
					myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=5)
					myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=5)
					myixia.create_traffic_v6(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v6",tracking_name=f"Tracking_{i+1}_{j+1}_v6",rate=5)
					myixia.create_traffic_v6(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v6",tracking_name=f"Tracking_{j+1}_{i+1}_v6",rate=5)

			myixia.start_traffic()
			sleep(5)
			myixia.stop_traffic()
			sleep(10)
			myixia.collect_stats()
			myixia.check_traffic()
			sw.print_show_command(f"get switch acl usage",mode="fast")
			sw.print_show_command(f"get switch acl counter all",mode="fast")
			sw.print_show_command(f"show switch acl ingress",mode="fast")
			sw.print_show_command(f"diagnose switch  physical-ports qos-rates non-zero",mode="fast")
			 
			print_double_line()
			k = input(f"Please verify all the command output,press any key to finish:")
			print_double_line()


	def acl6_schedule_status_yaml(*args,**kwargs):
		switch_num_list = kwargs["switch_num_list"]
		if "factory" in kwargs:
			factory = kwargs["factory"]
		else:
			factory = False
		for switch_num in switch_num_list:
			#Designate the DUT being tested 
			switch_num = int(switch_num)-1
			sw = switches[switch_num]

			if factory == True:
				sw.factory_and_restore_config()
				config_sys_interfaces(sw,vlan=TEST_VLAN_NAME)

			#define valuables specific to the switch under testing 
			ixia_sub_intf = 2
			portList_v4_v6 = []
			for p,m,n4,g4,n6,g6 in zip(
				tb.ixia.port_active_list[switch_num*2:switch_num*2+2],\
				mac_list[switch_num*2:switch_num*2+2], \
				net4_list[switch_num*2:switch_num*2+2], \
				gw4_list[switch_num*2:switch_num*2+2], \
				net6_list[switch_num*2:switch_num*2+2], \
				gw6_list[switch_num*2:switch_num*2+2]):
				module,port = p.split("/")
				portList_v4_v6.append([ixChassisIpList[0], int(module),int(port),m,n4,g4,n6,g6,ixia_sub_intf])
			
			print(portList_v4_v6)
			mac_base_1=mac_list[switch_num*2]
			mac_base_2=mac_list[switch_num*2+1]
			
			#clean up all ACL (ingress and 802.1x) related configuration
			acl_dot1x = switch_acl_dotonex(sw)
			acl_ingress = switch_acl_ingress(switches[switch_num])
			acl_ingress.acl_ingress_clean_up()
			acl_dot1x.acl_dot1x_clean_up(f"dot1x_filter_{switch_num+1}")
 
			today = date.today()            
			d1 = today.strftime("%Y/%m/%d")
			 
			#configure scheduler 
			cmds = f"""
			config system schedule recurring
			edit schedule2
			set day monday tuesday wednesday thursday friday saturday sunday
			set start 17:00
			set end 23:00
			end

			config system schedule onetime
		    edit "schedule_one_time_midnight"
		        set end 23:59 {d1}
		        set start 23:00 {d1}
		    next
		    edit "schedule_one_time_day_time"
		        set end 22:00 {d1}
		        set start 9:00 {d1}
		    next
			end
			"""
			sw.config_cmds_fast(cmds)

			#start configuring ACL related configuration
			for i in range(ixia_sub_intf):
				#start configuring ACL ingress configuration
				acl_yaml = f"""
                index: {1+i}
                classifiers:
                 dst-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2+1].split("/")[0])+i}
                 src-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2].split("/")[0])+i}
                 src-mac: {increment_macaddr(mac_base_1,i)}
                globals_config:
                  group: 4
                  ingress-interface: {sw.ixia_ports[0]}
                  schedule: schedule2
                actions:
                  count: "enable"
                  drop: "enable"
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)

				acl_yaml = f"""
                index: {1000+i}
                classifiers:
                 dst-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2].split("/")[0])+i}
                 src-ip6-prefix: {ipaddress.IPv6Address(net6_list[switch_num*2+1].split("/")[0])+i}
                 src-mac: {increment_macaddr(mac_base_2,i)}
                globals_config:
                  group: 4
                  ingress-interface: {sw.ixia_ports[1]}
                  schedule: schedule2
                actions:
                  count: "enable"
                  drop: "enable"
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)	

				acl_yaml = f"""
                index: {500+i}
                classifiers:
                 dst-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2+1].split("/")[0])+i}/32
                 src-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2].split("/")[0])+i}/32
                 src-mac: {increment_macaddr(mac_base_1,i)}
                globals_config:
                  group: 1
                  ingress-interface: {sw.ixia_ports[0]}
                  schedule: schedule2
                actions:
                  count: "enable"
                  drop: "enable"
                """

				acl_ingress.config_acl_ingress_jinja(acl_yaml)	
				acl_yaml = f"""
                index: {1500+i}
                classifiers:
                 dst-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2].split("/")[0])+i}/32
                 src-ip-prefix: {ipaddress.IPv4Address(net4_list[switch_num*2+1].split("/")[0])+i}/32
                 src-mac: {increment_macaddr(mac_base_2,i)}
                globals_config:
                  group: 1
                  ingress-interface: {sw.ixia_ports[1]}
                  schedule: schedule2
                actions:
                  count: "enable"
                  drop: "enable"
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)		 
		 
			#format of this method: config_explicit_drop(self,index,group,intf)
			# acl.config_explicit_drop(ixia_sub_intf+2,3,sw.ixia_ports[0])
			# acl.config_explicit_drop(ixia_sub_intf+1002,3,sw.ixia_ports[1])
			

 			#Start configurating IXIA 
			#myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6[switch_num*2:switch_num*2+2])
			myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)
			for topo in myixia.topologies:
				topo.add_ipv4(gateway="fixed",ip_incremental="0.0.0.1")
				topo.add_ipv6(gateway="fixed")
				
			myixia.start_protocol(wait=20)

			# for i in range(0,len(tb.ixia.port_active_list)-1):
			# 	for j in range(i+1,len(tb.ixia.port_active_list)):
			 
			for i in range(0,1):
				for j in range(1,2):
					myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=5)
					myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=5)
					myixia.create_traffic_v6(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v6",tracking_name=f"Tracking_{i+1}_{j+1}_v6",rate=5)
					myixia.create_traffic_v6(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v6",tracking_name=f"Tracking_{j+1}_{i+1}_v6",rate=5)

			myixia.start_traffic()
			sleep(5)
			myixia.stop_traffic()
			sleep(10)
			myixia.collect_stats()
			myixia.check_traffic()
			sw.print_show_command(f"get switch acl usage",mode="fast")
			sw.print_show_command(f"get switch acl counter all",mode="fast")
			sw.print_show_command(f"show switch acl ingress",mode="fast")
			print_double_line()
			k = input(f"Please verify recurring mid night schedule,press any key to move to testing one time mid night schdule:")
			print_double_line()
			sleep(5)
			for i in range(ixia_sub_intf):
				#start configuring ACL ingress configuration
				acl_yaml = f"""
                index: {1+i}
                globals_config:
                  schedule: schedule_one_time_midnight
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)

				acl_yaml = f"""
                index: {1000+i}
                globals_config:
                  schedule: schedule_one_time_midnight
                 """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)	

				acl_yaml = f"""
                index: {500+i}
                globals_config:
                  schedule: schedule_one_time_midnight
                 """

				acl_ingress.config_acl_ingress_jinja(acl_yaml)	
				acl_yaml = f"""
                index: {1500+i}
                globals_config:
                   schedule: schedule_one_time_midnight
                 """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)	

			myixia.start_traffic()
			sleep(5)
			myixia.stop_traffic()
			sleep(10)
			myixia.collect_stats()
			myixia.check_traffic()
			sw.print_show_command(f"get switch acl usage",mode="fast")
			sw.print_show_command(f"get switch acl counter all",mode="fast")
			sw.print_show_command(f"show switch acl ingress",mode="fast")
			print_double_line()
			k = input(f"Please verify traffic should be forwarded in day time, press any key to move to testing one time day time taking effective:")
			print_double_line()
			sleep(5)

			for i in range(ixia_sub_intf):
				#start configuring ACL ingress configuration
				acl_yaml = f"""
                index: {1+i}
                globals_config:
                  schedule: schedule_one_time_day_time
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)

				acl_yaml = f"""
                index: {1000+i}
                globals_config:
                  schedule: schedule_one_time_day_time
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)	

				acl_yaml = f"""
                index: {500+i}
                globals_config:
                  schedule: schedule_one_time_day_time
                """

				acl_ingress.config_acl_ingress_jinja(acl_yaml)	
				acl_yaml = f"""
                index: {1500+i}
                globals_config:
                  schedule: schedule_one_time_day_time
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)	

			myixia.start_traffic()
			sleep(5)
			myixia.stop_traffic()
			sleep(10)
			myixia.collect_stats()
			myixia.check_traffic()
			sw.print_show_command(f"get switch acl usage",mode="fast")
			sw.print_show_command(f"get switch acl counter all",mode="fast")
			sw.print_show_command(f"show switch acl ingress",mode="fast")
			print_double_line()
			k = input(f"Please verify traffic should be DROPPED, next step is disable all ingress ACL, press any key to continue:")
			print_double_line()
			sleep(5)

			for i in range(ixia_sub_intf):
				#start configuring ACL ingress configuration
				acl_yaml = f"""
                index: {1+i}
                globals_config:
                  status: inactive
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)

				acl_yaml = f"""
                index: {1000+i}
                globals_config:
                  status: inactive
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)	

				acl_yaml = f"""
                index: {500+i}
                globals_config:
                  status: inactive
                """

				acl_ingress.config_acl_ingress_jinja(acl_yaml)	
				acl_yaml = f"""
                index: {1500+i}
                globals_config:
                  status: inactive
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)	

			myixia.start_traffic()
			sleep(5)
			myixia.stop_traffic()
			sleep(10)
			myixia.collect_stats()
			myixia.check_traffic()
			sw.print_show_command(f"get switch acl usage",mode="fast")
			sw.print_show_command(f"get switch acl counter all",mode="fast")
			sw.print_show_command(f"show switch acl ingress",mode="fast")
			print_double_line()
			k = input(f"Please verify traffic should be forwarded after set all ingress ACL inactive,press any key to finish testing:")
			print_double_line()
			sleep(5)


	def classifier_l2_testing_yaml(*args,**kwargs):
		switch_num_list = kwargs["switch_num_list"]
		
		for switch_num in switch_num_list:
			#Designate the DUT being tested 
			switch_num = int(switch_num)-1
			sw = switches[switch_num]

			#define valuables specific to the switch under testing 
			ixia_sub_intf = 1
			portList_v4_v6 = []
			for p,m,n4,g4,n6,g6 in zip(
				tb.ixia.port_active_list[switch_num*2:switch_num*2+2],\
				mac_list[switch_num*2:switch_num*2+2], \
				net4_list[switch_num*2:switch_num*2+2], \
				gw4_list[switch_num*2:switch_num*2+2], \
				net6_list[switch_num*2:switch_num*2+2], \
				gw6_list[switch_num*2:switch_num*2+2]):
				module,port = p.split("/")
				portList_v4_v6.append([ixChassisIpList[0], int(module),int(port),m,n4,g4,n6,g6,ixia_sub_intf])
			
			print(portList_v4_v6)
			mac_base_1=mac_list[switch_num*2]
			mac_base_2=mac_list[switch_num*2+1]
			
			#clean up all ACL (ingress and 802.1x) related configuration
			acl_dot1x = switch_acl_dotonex(sw)
			acl_ingress = switch_acl_ingress(switches[switch_num])
			dot1x = DotOnex(sw,user_group="group_10",secrete="fortinet123",server="10.105.252.122",user="lab")
			acl_ingress.acl_ingress_clean_up()
			dot1x.dot1x_remove_config()
			acl_dot1x.acl_dot1x_clean_up(f"dot1x_filter_{switch_num+1}")

			#start configuring ACL related configuration
			for i in range(ixia_sub_intf):
				#start configuring ACL ingress configuration
				acl_yaml = f"""
                index: {1+i}
                classifiers:
                 ether-type: "0x800"
                 src-mac: {increment_macaddr(mac_base_1,i)}
                globals_config:
                  group: 3
                  ingress-interface: {sw.ixia_ports[0]}
                actions:
                  count: "enable"
                  drop: "enable"
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)

				acl_yaml = f"""
                index: {1000+i}
                classifiers:
                 ether-type: "0x800"
                 src-mac: {increment_macaddr(mac_base_2,i)}
                globals_config:
                  group: 3
                  ingress-interface: {sw.ixia_ports[1]}
                actions:
                  count: "enable"
                  drop: "enable"
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)	 
		 
			#This two config has to removed. format of this method: config_explicit_drop(self,index,group,intf)
			# acl_ingress.config_explicit_drop(ixia_sub_intf+2,3,sw.ixia_ports[0])
			# acl_ingress.config_explicit_drop(ixia_sub_intf+1002,3,sw.ixia_ports[1])

 			#Start configurating IXIA 

			for port in sw.ixia_ports:
				cmds = f"""
				config switch interface
					edit {port}
					unset native-vlan
					set allowed-vlans {TEST_VLAN}
					end
				"""
				sw.config_cmds_fast(cmds)
			sleep(2)
				
			start_vlan = 10
			#myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6[switch_num*2:switch_num*2+2],vlan=start_vlan)
			myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6,vlan=start_vlan)
			for topo in myixia.topologies:
				topo.add_ipv4(gateway="fixed",ip_incremental="0.0.0.1")
				topo.add_ipv6(gateway="fixed")
				
			myixia.start_protocol(wait=20)

			# for i in range(0,len(tb.ixia.port_active_list)-1):
			# 	for j in range(i+1,len(tb.ixia.port_active_list)):
			 
			for i in range(0,1):
				for j in range(1,2):
					myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=5)
					myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=5)
					myixia.create_traffic_v6(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v6",tracking_name=f"Tracking_{i+1}_{j+1}_v6",rate=5)
					myixia.create_traffic_v6(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v6",tracking_name=f"Tracking_{j+1}_{i+1}_v6",rate=5)

			myixia.start_traffic()
			sw.print_show_command(f"get switch acl usage",mode="fast")
			sw.print_show_command(f"get switch acl counter all",mode="fast")
			sw.print_show_command(f"show switch acl ingress",mode="fast")
			print_double_line()
			keyin = input(f"Please check IPv4 packets are dropped, IPv6 traffic is forwarding,Press any key when done:")
			print_double_line()
			sleep(5)

			for i in range(ixia_sub_intf):
				#start configuring ACL ingress configuration
				acl_yaml = f"""
                index: {1+i}
                classifiers:
                 ether-type: "0x86dd"
                 src-mac: {increment_macaddr(mac_base_1,i)}
                globals_config:
                  group: 3
                  ingress-interface: {sw.ixia_ports[0]}
                actions:
                  count: "enable"
                  drop: "enable"
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)

				acl_yaml = f"""
                index: {1000+i}
                classifiers:
                 ether-type: "0x86dd"
                 src-mac: {increment_macaddr(mac_base_2,i)}
                globals_config:
                  group: 3
                  ingress-interface: {sw.ixia_ports[1]}
                actions:
                  count: "enable"
                  drop: "enable"
                """
				acl_ingress.config_acl_ingress_jinja(acl_yaml)	

			sw.print_show_command(f"get switch acl counter all",mode="fast")
			sw.print_show_command(f"show switch acl ingress",mode="fast")
			print_double_line()
			keyin = input(f"Please check IPv4 Passed and IPv6 Dropped,Press any key when done:")
			print_double_line()
			sleep(5)

			for port in sw.ixia_ports:
				cmds = f"""
				config switch interface
					edit {port}
					set native-vlan {TEST_VLAN}
					set allowed-vlans {TEST_VLAN}
					end
				"""
				sw.config_cmds_fast(cmds)
			sleep(2)
			 

	def dot1x_acl6_testing(*args,**kwargs):
		switch_num_list = kwargs["switch_num_list"]
		
		for switch_num in switch_num_list:
			switch_num = int(switch_num)-1

			ixia_sub_intf = 2
			portList_v4_v6 = []
			for p,m,n4,g4,n6,g6 in zip(
				tb.ixia.port_active_list[switch_num*2:switch_num*2+2],\
				mac_list[switch_num*2:switch_num*2+2], \
				net4_list[switch_num*2:switch_num*2+2], \
				gw4_list[switch_num*2:switch_num*2+2], \
				net6_list[switch_num*2:switch_num*2+2], \
				gw6_list[switch_num*2:switch_num*2+2]):
				module,port = p.split("/")
				portList_v4_v6.append([ixChassisIpList[0], int(module),int(port),m,n4,g4,n6,g6,ixia_sub_intf])
			
			print(portList_v4_v6)
			sw = switches[switch_num]


			acl_dot1x = switch_acl_dotonex(sw)
			acl_dot1x.config_acl_dotonex_simple(filter_name=f"dot1x_filter_{switch_num+1}",entry_index = 1,acl_index=1,mac_address=mac_list[switch_num*2])
			acl_dot1x.config_acl_dotonex_simple(filter_name=f"dot1x_filter_{switch_num+1}",entry_index = 2,acl_index=1,mac_address=mac_list[switch_num*2+1])
			dot1x = DotOnex(sw,user_group="group_10",secrete="fortinet123",server="10.105.252.122",user="lab")
			dot1x.dot1x_interface_config(port_list=[sw.ixia_ports[0],sw.ixia_ports[1]])

			#clean up all ACL ingress entries
			acl = switch_acl_ingress(switches[switch_num])
			acl.acl_ingress_clean_up()

			for i in range(ixia_sub_intf):
				classifiers = {}
				globals = {}
				actions = {}

				index=1+i
				classifiers = {
				"dst-ip6-prefix":str(ipaddress.IPv6Address(net6_list[switch_num*2+1].split("/")[0])+i),
				"src-ip6-prefix":str(ipaddress.IPv6Address(net6_list[switch_num*2].split("/")[0])+i)
				}
				
				globals = {
				"group":3,
	             "ingress-interface": sw.ixia_ports[0]
	            }
				
				actions = {
				"count":"enable"
				}
				
				acl.config_acl6_generic(index,globals,classifiers,actions)

				index=1001+i
				classifiers = {
				"dst-ip6-prefix":str(ipaddress.IPv6Address(net6_list[switch_num*2].split("/")[0])+i),
				"src-ip6-prefix":str(ipaddress.IPv6Address(net6_list[switch_num*2+1].split("/")[0])+i)
				}
				
				globals = {
				"group":3,
	             "ingress-interface": sw.ixia_ports[1]
	            }
				
				actions = {
				"count":"enable"
				}
				acl.config_acl6_generic(index,globals,classifiers,actions)

			#index += 1
			#format of this method: config_explicit_drop(self,index,group,intf)
			# acl.config_explicit_drop(index,5,sw.ixia_ports[0])
			# index += 1
			# acl.config_explicit_drop(index,5,sw.ixia_ports[1])

 		
			#myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6[switch_num*2:switch_num*2+2])
			myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)
			for topo in myixia.topologies:
				topo.add_dot1x_client()
				topo.add_ipv4(gateway="fixed",ip_incremental="0.0.0.1")
				topo.add_ipv6(gateway="fixed")
				
			myixia.start_protocol(wait=20)

			# for i in range(0,len(tb.ixia.port_active_list)-1):
			# 	for j in range(i+1,len(tb.ixia.port_active_list)):
			 
			for i in range(0,1):
				for j in range(1,2):
					myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=5)
					myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=5)
					myixia.create_traffic_v6(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v6",tracking_name=f"Tracking_{i+1}_{j+1}_v6",rate=5)
					myixia.create_traffic_v6(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v6",tracking_name=f"Tracking_{j+1}_{i+1}_v6",rate=5)

			myixia.start_traffic()
			sleep(5)
			myixia.stop_traffic()
			sleep(10)
			myixia.collect_stats()
			myixia.check_traffic()
			sw = switches[switch_num]
			sw.print_show_command(f"get switch acl usage",mode="fast")
			sw.print_show_command(f"get switch acl counter all",mode="fast")
			sw.print_show_command(f"show switch acl ingress",mode="fast")
			sw.print_show_command(f"show switch acl 802-1X",mode="fast")
			sw.print_show_command(f"show switch acl service custom dot1x_filter_{switch_num+1}",mode="fast")
			sw.print_show_command(f"diagnose switch 802-1x status-dacl {sw.ixia_ports[0]}",mode="fast")
			sw.print_show_command(f"diagnose switch 802-1x status-dacl {sw.ixia_ports[1]}",mode="fast") 
			print_double_line()
			k = input(f"Please verify all the command output,Do you want to remove 802.1x configurations(Y/N):")
			print_double_line()
			sleep(5)
			if k =="yes" or k=="y" or k=="Y" or k=="Yes":
				Info("Removing All 802.1x related configuration.......")
				acl_dot1x.remove_acl_dotonex_simple(filter_name=f"dot1x_filter_{switch_num+1}",acl_index=1)
				dot1x.dot1x_remove_config()

	def basic_acl6_testing(*args,**kwargs):
		switch_num_list = kwargs["switch_num_list"]
		
		ixia_sub_intf = 2
		portList_v4_v6 = []
		for p,m,n4,g4,n6,g6 in zip(tb.ixia.port_active_list,mac_list,net4_list,gw4_list,net6_list,gw6_list):
			module,port = p.split("/")
			portList_v4_v6.append([ixChassisIpList[0], int(module),int(port),m,n4,g4,n6,g6,ixia_sub_intf])

		print(portList_v4_v6)
		for switch_num in switch_num_list:
			switch_num = int(switch_num)-1
			sw = switches[switch_num]
			acl = switch_acl_ingress(switches[switch_num])
			acl.acl_ingress_clean_up()

			for i in range(ixia_sub_intf):
				classifiers = {}
				globals = {}
				actions = {}

				index=1+i
				classifiers = {
				"dst-ip6-prefix":str(ipaddress.IPv6Address(net6_list[switch_num*2+1].split("/")[0])+i),
				"src-ip6-prefix":str(ipaddress.IPv6Address(net6_list[switch_num*2].split("/")[0])+i)
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
				"dst-ip6-prefix":str(ipaddress.IPv6Address(net6_list[switch_num*2].split("/")[0])+i),
				"src-ip6-prefix":str(ipaddress.IPv6Address(net6_list[switch_num*2+1].split("/")[0])+i)
				}
				
				globals = {
				"group":5,
	             "ingress-interface": sw.ixia_ports[1]
	            }
				
				actions = {
				"count":"enable"
				}
				acl.config_acl6_generic(index,globals,classifiers,actions)

			index += 1
			#format of this method: config_explicit_drop(self,index,group,intf)
			acl.config_explicit_drop(index,5,sw.ixia_ports[0])
			index += 1
			acl.config_explicit_drop(index,5,sw.ixia_ports[1])

 		
		#myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6[switch_num*2:switch_num*2+2])
		myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)
		for topo in myixia.topologies:
			topo.add_ipv4(gateway="fixed",ip_incremental="0.0.0.1")
			topo.add_ipv6(gateway="fixed")
			
		myixia.start_protocol(wait=20)

		# for i in range(0,len(tb.ixia.port_active_list)-1):
		# 	for j in range(i+1,len(tb.ixia.port_active_list)):
		for switch_num in switch_num_list:
			switch_num -= 1
			for i in range(switch_num*2,switch_num*2+1):
				for j in range(i+1,switch_num*2+2):
					# myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=5)
					# myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=5)
					myixia.create_traffic_v6(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v6",tracking_name=f"Tracking_{i+1}_{j+1}_v6",rate=5)
					myixia.create_traffic_v6(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v6",tracking_name=f"Tracking_{j+1}_{i+1}_v6",rate=5)

			myixia.start_traffic()
			sleep(5)
			myixia.stop_traffic()
			sleep(10)
			myixia.collect_stats()
			myixia.check_traffic()
			sw = switches[switch_num]
			sw.print_show_command(f"get switch acl counter all",mode="fast")
			print_double_line()
			keyin = input(f"Please verify the ixia traffic counter and switch ingress acl counter,Press any key when done:")
			print_double_line()
			sleep(5)
			myixia.remove_all_traffic_v6()
			# myixia.remove_all_traffic_v4()


	def basic_acl6_rvi_testing(*args,**kwargs):
		switch_num_list = kwargs["switch_num_list"]
		

		mac_list = ["00:11:01:01:01:01","00:12:01:01:01:01","00:13:01:01:01:01","00:14:01:01:01:01","00:15:01:01:01:01","00:16:01:01:01:01","00:17:01:01:01:01","00:18:01:01:01:01"]
		net4_list = ["200.1.1.10/24","200.1.2.10/24","200.1.3.10/24","200.1.4.10/24","200.1.5.10/24","200.1.6.10/24","200.1.7.10/24","200.1.8.10/24","200.1.9.10/24","200.1.10.10/24"]
		gw4_list = ["200.1.1.1","200.1.2.1","200.1.3.1","200.1.4.1","200.1.5.1","200.1.6.1","200.1.7.1","200.1.8.1","200.1.9.1","200.1.10.1","200.1.11.1","200.1.12.1","200.1.13.1"]
		net6_list = ["2001:10:1:1::1000/64","2001:10:1:2::1000/64","2001:10:3:1::1000/64","2001:10:1:4::1000/64","2001:10:1:5::1000/64","2001:10:1:6::1000/64","2001:10:1:7::1000/64","2001:10:1:8::1000/64"]
		gw6_list = ["2001:10:1:1::1","2001:10:1:2::1","2001:10:1:3::1","2001:10:1:4::1","2001:10:1:5::1","2001:10:1:6::1","2001:10:1:7::1","2001:10:1:8::1","2001:10:1:9::1"]

		ixia_sub_intf = 2
		portList_v4_v6 = []
		for p,m,n4,g4,n6,g6 in zip(tb.ixia.port_active_list,mac_list,net4_list,gw4_list,net6_list,gw6_list):
			module,port = p.split("/")
			portList_v4_v6.append([ixChassisIpList[0], int(module),int(port),m,n4,g4,n6,g6,ixia_sub_intf])

		print(portList_v4_v6)
		for switch_num in switch_num_list:

			switch_num = int(switch_num)-1
			sw = switches[switch_num]
			acl = switch_acl_ingress(switches[switch_num])
			acl.acl_ingress_clean_up()

			cmds = f"""
			config system interface
			edit rvi-1
			    set type physical
	        	set l2-interface {sw.ixia_ports[0]}
				set ip {gw4_list[switch_num*2]} 255.255.255.0
			    config ipv6
	                set ip6-address {gw6_list[switch_num*2]}/64
	                set ip6-allowaccess ping https http ssh telnet
	                set dhcp6-information-request enable
			        end
			    next
			edit rvi-2
			    set type physical
	        	set l2-interface {sw.ixia_ports[1]}
				set ip {gw4_list[switch_num*2+1]} 255.255.255.0
			    config ipv6
	                set ip6-address {gw6_list[switch_num*2+1]}/64
	                set ip6-allowaccess ping https http ssh telnet
	                set dhcp6-information-request enable
			        end
			    next
			 end
			end
				"""
			sw.config_cmds_fast(cmds)
			sleep(10)
			for i in range(ixia_sub_intf):
				classifiers = {}
				globals = {}
				actions = {}

				index=1+i
				classifiers = {
				"dst-ip6-prefix":str(ipaddress.IPv6Address(net6_list[switch_num*2+1].split("/")[0])+i),
				"src-ip6-prefix":str(ipaddress.IPv6Address(net6_list[switch_num*2].split("/")[0])+i)
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
				"dst-ip6-prefix":str(ipaddress.IPv6Address(net6_list[switch_num*2].split("/")[0])+i),
				"src-ip6-prefix":str(ipaddress.IPv6Address(net6_list[switch_num*2+1].split("/")[0])+i)
				}
				
				globals = {
				"group":5,
	             "ingress-interface": sw.ixia_ports[1]
	            }
				
				actions = {
				"count":"enable"
				}
				acl.config_acl6_generic(index,globals,classifiers,actions)

			index += 1
			#format of this method: config_explicit_drop(self,index,group,intf)
			acl.config_explicit_drop(index,5,sw.ixia_ports[0])
			index += 1
			acl.config_explicit_drop(index,5,sw.ixia_ports[1])

 		
		#myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6[switch_num*2:switch_num*2+2])
		myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)
		for topo in myixia.topologies:
			topo.add_ipv4(gateway="fixed",ip_incremental="0.0.0.1")
			topo.add_ipv6(gateway="fixed")
			
		myixia.start_protocol(wait=20)

		# for i in range(0,len(tb.ixia.port_active_list)-1):
		# 	for j in range(i+1,len(tb.ixia.port_active_list)):
		for switch_num in switch_num_list:
			switch_num -= 1
			for i in range(switch_num*2,switch_num*2+1):
				for j in range(i+1,switch_num*2+2):
					# myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=5)
					# myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=5)
					myixia.create_traffic_v6(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v6",tracking_name=f"Tracking_{i+1}_{j+1}_v6",rate=5)
					myixia.create_traffic_v6(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v6",tracking_name=f"Tracking_{j+1}_{i+1}_v6",rate=5)

			myixia.start_traffic()
			sleep(5)
			myixia.stop_traffic()
			sleep(10)
			myixia.collect_stats()
			myixia.check_traffic()
			sw = switches[switch_num]
			sw.print_show_command(f"get switch acl counter all",mode="fast")
			print_double_line()
			keyin = input(f"Please verify the ixia traffic counter and switch ingress acl counter,Press any key when done:")
			print_double_line()
			sleep(5)
			myixia.remove_all_traffic_v6()
			# myixia.remove_all_traffic_v4()



	def traffic_acl6_testing(*args,**kwargs):
		switch_num_list = kwargs["switch_num_list"]
		
		ixia_sub_intf = 2
		portList_v4_v6 = []
		for p,m,n4,g4,n6,g6 in zip(tb.ixia.port_active_list,mac_list,net4_list,gw4_list,net6_list,gw6_list):
			module,port = p.split("/")
			portList_v4_v6.append([ixChassisIpList[0], int(module),int(port),m,n4,g4,n6,g6,ixia_sub_intf])

		print(portList_v4_v6)
		acl_list = []
		for switch_num in switch_num_list:
			switch_num = int(switch_num)-1
			sw = switches[switch_num]
			acl = switch_acl_ingress(switches[switch_num])
			acl_list.append(acl)
			acl.acl_ingress_clean_up()

			for i in range(ixia_sub_intf):
				classifiers = {}
				globals = {}
				actions = {}

				index=1+i
				classifiers = {
				"dst-ip6-prefix":str(ipaddress.IPv6Address(net6_list[switch_num*2+1].split("/")[0])+i),
				"src-ip6-prefix":str(ipaddress.IPv6Address(net6_list[switch_num*2].split("/")[0])+i)
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
				"dst-ip6-prefix":str(ipaddress.IPv6Address(net6_list[switch_num*2].split("/")[0])+i),
				"src-ip6-prefix":str(ipaddress.IPv6Address(net6_list[switch_num*2+1].split("/")[0])+i)
				}
				
				globals = {
				"group":5,
	             "ingress-interface": sw.ixia_ports[1]
	            }
				
				actions = {
				"count":"enable"
				}
				acl.config_acl6_generic(index,globals,classifiers,actions)

			# index = 2000
			# #format of this method: config_explicit_drop(self,index,group,intf)
			# acl.config_explicit_drop(index,5,sw.ixia_ports[0])
			# index = 2001
			# acl.config_explicit_drop(index,5,sw.ixia_ports[1])

 
		myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)
		for topo in myixia.topologies:
			topo.add_ipv4(gateway="fixed",ip_incremental="0.0.0.1")
			topo.add_ipv6(gateway="fixed")
			
		myixia.start_protocol(wait=20)

		# for acl in acl_list:
		# 	index = 2000
		# 	#format of this method: config_explicit_drop(self,index,group,intf)
		# 	acl.config_explicit_drop(index,5,sw.ixia_ports[0])
		# 	index = 2001
		# 	acl.config_explicit_drop(index,5,sw.ixia_ports[1])
		 
		for switch_num in switch_num_list:
			acl_num = 0
			switch_num -= 1
			sw = switches[switch_num]
			for i in range(switch_num*2,switch_num*2+1):
				for j in range(i+1,switch_num*2+2):
					# myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=5)
					# myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=5)
					myixia.create_traffic_v6(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v6",tracking_name=f"Tracking_{i+1}_{j+1}_v6",rate=5)
					myixia.create_traffic_v6(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v6",tracking_name=f"Tracking_{j+1}_{i+1}_v6",rate=5)

			sw.config_cmds_fast("execute acl clear-counter all")
			myixia.start_traffic()
			sleep(5)
			myixia.stop_traffic()
			sleep(10)
			myixia.collect_stats()
			myixia.check_traffic()
			
			sw.print_show_command(f"get switch acl counter all",mode="fast")
			print_double_line()
			keyin = input(f"Please verify without Explict denly, ixia traffic ALL PASSED,Press any key when done:")
			print_double_line()
			sleep(5)
			#myixia.remove_all_traffic_v6()
			# myixia.remove_all_traffic_v4()
			index = 2000
			#format of this method: config_explicit_drop(self,index,group,intf)
			acl_list[acl_num].config_explicit_drop(index,5,sw.ixia_ports[0])
			index = 2001
			acl_list[acl_num].config_explicit_drop(index,5,sw.ixia_ports[1])
			
			myixia.start_traffic()
			print_double_line()
			keyin = input(f"Please verify after ACL deny configured, ixia traffic ALL PASSED,Press any key when done:")
			print_double_line()
			myixia.stop_traffic()
			sleep(10)
			myixia.collect_stats()
			myixia.check_traffic()
			index = 2000
			#format of this method: config_explicit_drop(self,index,group,intf)
			acl_list[acl_num].config_explicit_allow(index,5,sw.ixia_ports[0])
			index = 2001
			acl_list[acl_num].config_explicit_allow(index,5,sw.ixia_ports[1])

			acl_num +=1
			sleep(5)

		############ Add more IXIA subports to verify ACL DROP behavior ###############
		ixia_sub_intf = 4  # previously this is 2
		portList_v4_v6 = []
		for p,m,n4,g4,n6,g6 in zip(tb.ixia.port_active_list,mac_list,net4_list,gw4_list,net6_list,gw6_list):
			module,port = p.split("/")
			portList_v4_v6.append([ixChassisIpList[0], int(module),int(port),m,n4,g4,n6,g6,ixia_sub_intf])
		myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)
		for topo in myixia.topologies:
			topo.add_ipv4(gateway="fixed",ip_incremental="0.0.0.1")
			topo.add_ipv6(gateway="fixed")
			
		myixia.start_protocol(wait=20)

		 
		for switch_num in switch_num_list:
			switch_num -= 1
			acl_num = 0
			sw = switches[switch_num]
			for i in range(switch_num*2,switch_num*2+1):
				for j in range(i+1,switch_num*2+2):
					myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=5)
					myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=5)
					myixia.create_traffic_v6(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v6",tracking_name=f"Tracking_{i+1}_{j+1}_v6",rate=5)
					myixia.create_traffic_v6(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v6",tracking_name=f"Tracking_{j+1}_{i+1}_v6",rate=5)

			sw.config_cmds_fast("execute acl clear-counter all")
			sleep(5)
			myixia.start_traffic()
			sleep(5)
			myixia.stop_traffic()
			sleep(10)
			myixia.collect_stats()
			myixia.check_traffic()
			
			sw.print_show_command(f"get switch acl counter all",mode="fast")
			print_double_line()
			keyin = input(f"Please verify without explicit deny, ALL packet PASSED,Press any key when done:")
			print_double_line()
			sleep(5)

			index = 2000
			#format of this method: config_explicit_drop(self,index,group,intf)
			acl_list[acl_num].config_explicit_drop(index,5,sw.ixia_ports[0])
			index = 2001
			acl_list[acl_num].config_explicit_drop(index,5,sw.ixia_ports[1])
			sleep(5)
		
			sw.config_cmds_fast("execute acl clear-counter all")
			sleep(5)
			myixia.start_traffic()
			print_double_line()
			keyin = input(f"Please verify after ACL deny configured, SOME packets dropped,Press any key when done:")
			print_double_line()
			myixia.stop_traffic()
			sleep(10)
			myixia.collect_stats()
			myixia.check_traffic()
			sw.print_show_command(f"get switch acl counter all",mode="fast")

			index = 2000
			#format of this method: config_explicit_drop(self,index,group,intf)
			acl_list[acl_num].config_explicit_allow(index,5,sw.ixia_ports[0])
			index = 2001
			acl_list[acl_num].config_explicit_allow(index,5,sw.ixia_ports[1])
			
			sw.config_cmds_fast("execute acl clear-counter all")
			sleep(5)
			myixia.start_traffic()
			sleep(5)
			sw.print_show_command(f"get switch acl counter all",mode="fast")
			print_double_line()
			keyin = input(f"Please verify after ACL deny is reversed, All PASSED,Press any key when done:")
			print_double_line()
			myixia.stop_traffic()
			sleep(10)
			myixia.collect_stats()
			myixia.check_traffic()
	
			acl_num +=1

	def acl6_redirect_mirror_testing():
		acl.acl_ingress_clean_up()
		ixia_sub_intf = 1
		portList_v4_v6 = []
		for p,m,n4,g4,n6,g6 in zip(tb.ixia.port_active_list,mac_list,net4_list,gw4_list,net6_list,gw6_list):
			module,port = p.split("/")
			portList_v4_v6.append([ixChassisIpList[0], int(module),int(port),m,n4,g4,n6,g6,ixia_sub_intf])

		print(portList_v4_v6)
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

		# for i in range(0,len(tb.ixia.port_active_list)-1):
		# 	for j in range(i+1,len(tb.ixia.port_active_list)):
		for i in range(0,1):
			for j in range(i+1,2):
				myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=5)
				myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=5)
				myixia.create_traffic_v6(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v6",tracking_name=f"Tracking_{i+1}_{j+1}_v6",rate=5)
				myixia.create_traffic_v6(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v6",tracking_name=f"Tracking_{j+1}_{i+1}_v6",rate=5)

		myixia.start_traffic()
		myixia.collect_stats()
		myixia.check_traffic()
		myixia.stop_traffic()

		for i in range(ixia_sub_intf):
			classifiers = {}
			globals = {}
			actions = {}

			index=1+i
			actions = {
			"redirect":sw.ixia_ports[2]
			}
			
			acl.config_acl6_generic(index,globals,classifiers,actions)

			index=1001+i
			
			actions = {
			"redirect":sw.ixia_ports[2]
			}
			acl.config_acl6_generic(index,globals,classifiers,actions)
		myixia.start_traffic()
		keyin = input(f"Please capture packets at IXIA topology #3 should have all redirected traffic,Press any key when done:")
		myixia.collect_stats()
		myixia.check_traffic()
		myixia.stop_traffic()

		cmds = f"""
		config switch mirror
		    edit "mirror1"
		        set status active
		        set dst {sw.ixia_ports[3]}
		        set switching-packet enable
		        set src-ingress {sw.ixia_ports[0]}
		    next
		end
		"""
		sw.config_cmds_fast(cmds)
		sleep(5)
		for i in range(ixia_sub_intf):
			classifiers = {}
			globals = {}
			actions = {}

			index=1+i
			actions = {
			"mirror":mirror1
			}
			
			acl.config_acl6_generic(index,globals,classifiers,actions)

		myixia.start_traffic()
		keyin = input(f"Please capture packets at IXIA topology #4, you should see both IPv4 and IPv6 trafic mirror from topo#1 to Topo#4,Press any key when done:")
		myixia.collect_stats()
		myixia.check_traffic()
		myixia.stop_traffic()

	def change_vlan_cos_dscp_testing():
		portList_v4_v6 = []
	
		ixia_sub_intf = 1
		for p,m,n4,g4,n6,g6 in zip(tb.ixia.port_active_list[:2],mac_list,net4_list,gw4_list,net6_list,gw6_list):
			module,port = p.split("/")
			portList_v4_v6.append([ixChassisIpList[0], int(module),int(port),m,n4,g4,n6,g6,ixia_sub_intf])

		print(portList_v4_v6)
		acl.acl_ingress_clean_up()

		for port in sw.ixia_ports:
			cmds = f"""
			config switch interface
				edit {port}
			  	unset native-vlan
			  	set allowed-vlans 2
			  	end
			"""
			sw.config_cmds_fast(cmds)
			sleep(2)

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

		start_vlan = 2
		myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6,vlan=start_vlan)
		for topo in myixia.topologies:
			topo.add_ipv4(gateway="fixed",ip_incremental="0.0.0.1")
			topo.add_ipv6(gateway="fixed")
			
		myixia.start_protocol(wait=20)

		for i in range(0,1):
			for j in range(i+1,2):
				myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=5)
				myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=5)
				myixia.create_traffic_v6(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v6",tracking_name=f"Tracking_{i+1}_{j+1}_v6",rate=5)
				myixia.create_traffic_v6(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v6",tracking_name=f"Tracking_{j+1}_{i+1}_v6",rate=5)
 
		myixia.start_traffic()
		myixia.collect_stats()
		myixia.check_traffic()
		myixia.stop_traffic()

		for i in range(ixia_sub_intf):
			classifiers = {}
			globals = {}
			actions = {}

			index=1+i
			
			actions = {
			"remark-cos":7
			}	
			acl.config_acl6_generic(index,globals,classifiers,actions)

			index=1001+i	
			actions = {
			"remark-cos":7
			}
			acl.config_acl6_generic(index,globals,classifiers,actions)

		myixia.start_traffic()
		keyin = input(f"Please capture packets at IXIA to verify COS has been set to 7,Press any key when done:")
		myixia.collect_stats()
		myixia.check_traffic()
		myixia.stop_traffic()

		for i in range(ixia_sub_intf):
			classifiers = {}
			globals = {}
			actions = {}

			index=1+i
			
			actions = {
			"remark-cos":7,
			"remark-dscp": 63
			}	
			acl.config_acl6_generic(index,globals,classifiers,actions)

			index=1001+i	
			actions = {
			"remark-cos":7,
			"remark-dscp": 63
			}
			acl.config_acl6_generic(index,globals,classifiers,actions)
		myixia.start_traffic()
		#For IPv6 DSCP, the first 6 bits are used
		keyin = input(f"Please capture packets at IXIA to verify IPv6 Traffic Class is set to 0x11111100,Press any key when done:")
		myixia.collect_stats()
		myixia.check_traffic()
		myixia.stop_traffic()

		for port in sw.ixia_ports:
			cmds = f"""
			config switch interface
				edit {port}
			  	set native-vlan 2
			  	set allowed-vlans 2
			  	end
			"""
			sw.config_cmds_fast(cmds)
			sleep(2)

			

	def qos_policy_testing():
		portList_v4_v6 = []
	
		ixia_sub_intf = 1
		for p,m,n4,g4,n6,g6 in zip(tb.ixia.port_active_list[:2],mac_list,net4_list,gw4_list,net6_list,gw6_list):
			module,port = p.split("/")
			portList_v4_v6.append([ixChassisIpList[0], int(module),int(port),m,n4,g4,n6,g6,ixia_sub_intf])

		print(portList_v4_v6)
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
			"group":3,
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
			"group":3,
             "ingress-interface": sw.ixia_ports[1]
            }
			
			actions = {
			"count":"enable"
			}
		acl.config_acl6_generic(index,globals,classifiers,actions)

		start_vlan = 2
		myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)
		for topo in myixia.topologies:
			topo.add_ipv4(gateway="fixed",ip_incremental="0.0.0.1")
			topo.add_ipv6(gateway="fixed")
			
		myixia.start_protocol(wait=20)

		for i in range(0,1):
			for j in range(i+1,2):
				myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=20)
				myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=20)
				myixia.create_traffic_v6(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v6",tracking_name=f"Tracking_{i+1}_{j+1}_v6",rate=20)
				myixia.create_traffic_v6(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v6",tracking_name=f"Tracking_{j+1}_{i+1}_v6",rate=20)
 
		myixia.start_traffic()
		keyin = input(f"Please verify no traffic loss before test starts. Press any key when done:")
		sw.print_show_command(f"diagnose switch physical-ports qos-stats list {sw.ixia_ports[0]}",mode="fast")
		sw.print_show_command(f"diagnose switch physical-ports qos-stats list {sw.ixia_ports[1]}",mode="fast")
		keyin = input(f"Please verify qos-stats, make sure no packet dropped. Press any key when done:")
		myixia.collect_stats()
		myixia.check_traffic()
		myixia.stop_traffic()

		cmds = f"""
		conf switch qos qos-policy
		delet ipv6
		edit ipv6
		config cos-queue
		  	edit queue-5
                set drop-policy weighted-random-early-detection
                set max-rate 10
                set min-rate 5
                set wred-slope 30
                end
            set rate-by kbps
            end
		"""
		sw.config_cmds_fast(cmds)
		sleep(5)

		for i in range(ixia_sub_intf):
			classifiers = {}
			globals = {}
			actions = {}

			index=1+i
			
			actions = {
			"cos-queue":5
			}	
			acl.config_acl6_generic(index,globals,classifiers,actions)

			index=1001+i	
			actions = {
			"cos-queue":5
			}
			acl.config_acl6_generic(index,globals,classifiers,actions)

		sleep(5)
		myixia.start_traffic()
		keyin = input(f"Please verify IXIA having traffic loss,Press any key when done:")
		sw.print_show_command(f"diagnose switch physical-ports qos-stats list {sw.ixia_ports[0]}",mode="fast")
		sw.print_show_command(f"diagnose switch physical-ports qos-stats list {sw.ixia_ports[1]}",mode="fast")
		keyin = input(f"Please verify qos-stats, make sure packet dropped at queue-5. Press any key when done:")
		myixia.collect_stats()
		myixia.check_traffic()
		myixia.stop_traffic()


 
	def acl_policer_testing():
		portList_v4_v6 = []
	
		ixia_sub_intf = 4
		for p,m,n4,g4,n6,g6 in zip(tb.ixia.port_active_list[:2],mac_list,net4_list,gw4_list,net6_list,gw6_list):
			module,port = p.split("/")
			portList_v4_v6.append([ixChassisIpList[0], int(module),int(port),m,n4,g4,n6,g6,ixia_sub_intf])

		print(portList_v4_v6)
		acl.acl_ingress_clean_up()

		cmds = """
			config switch acl policer
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
			edit 1
   			set guaranteed-bandwidth 100
    		set type ingress
		next
		edit 2
    		set guaranteed-bandwidth 200
    		set type egress
		next
		end
		"""
		sw.config_cmds(cmds)
		sleep(10)

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
			"group":3+i,
             "ingress-interface": sw.ixia_ports[0]
            }
			
			if i%2 == 0:
				actions = {
				"count":"enable"
				}
			else:
				actions = {
				"count":"enable",
				"policer":1
				}
			acl.config_acl6_generic(index,globals,classifiers,actions)

			index=1001+i
			classifiers = {
			"dst-ip6-prefix":str(ipaddress.IPv6Address(net6_list[0].split("/")[0])+i),
			"src-ip6-prefix":str(ipaddress.IPv6Address(net6_list[1].split("/")[0])+i)
			}
			
			globals = {
			"group":3+i,
             "ingress-interface": sw.ixia_ports[1]
            }
			
			if i%2 == 0:
				actions = {
				"count":"enable"
				}
			else:
				actions = {
				"count":"enable",
				"policer":1
				}
			acl.config_acl6_generic(index,globals,classifiers,actions)

		start_vlan = 2
		myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)
		for topo in myixia.topologies:
			topo.add_ipv4(gateway="fixed",ip_incremental="0.0.0.1")
			topo.add_ipv6(gateway="fixed")
			
		myixia.start_protocol(wait=20)

		for i in range(0,1):
			for j in range(i+1,2):
				myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=20)
				myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=20)
				myixia.create_traffic_v6(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v6",tracking_name=f"Tracking_{i+1}_{j+1}_v6",rate=20)
				myixia.create_traffic_v6(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v6",tracking_name=f"Tracking_{j+1}_{i+1}_v6",rate=20)
 
		myixia.start_traffic()
		keyin = input(f"Please verify IXIA traffic loss before test starts. Press any key when done:")
		sw.print_show_command(f"get switch acl counter all",mode="fast")
		sw.print_show_command(f"get switch acl counter all",mode="fast")
		keyin = input(f"Please verify acl ingress counter, you should see some packet dropped. Press any key when done:")
		myixia.collect_stats()
		myixia.check_traffic()
		myixia.stop_traffic()


	def basic_scale_acl6_testing(*args, **kwargs):
		#Change the switch that you want to scale
		switch_num = kwargs["switch_num"]
		sw = switches[1]
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
			try: 
				globals = {
				"group":try_group,
				 "ingress-interface": sw.ixia_ports[0]
				}
			except Exception as e:
				globals = {
				"group":try_group,
				 "ingress-interface": "port2"
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
						
						try: 
							globals = {
							"group":try_group,
					         "ingress-interface": sw.ixia_ports[0]
					        }
						except Exception as e:
							globals = {
							"group":try_group,
							"ingress-interface": "port2"
							}
						
						actions = {
						"count":"enable"
						}
						acl.config_acl6_generic(index,globals,classifiers,actions)
				sw.print_show_command("get switch acl usage",mode="fast")	
			acl.update_acl_usage()
			try_group += 1
		#Change back to switch 1.  Need to fix this later
		sw = switches[0]

	def real_scale_acl6_testing(*args,**kwargs):
		
		switch_num = int(kwargs["switch_num"]) - 1 
		sw_dut = switches[switch_num]
		if "longevity" in kwargs:
			longevity = kwargs['longevity']
		else:
			longevity = False

		acl = switch_acl_ingress(sw_dut)
		acl.acl_ingress_clean_up()
 
		try_group = 3
		index = 1
		dst_ip6_prefix = net6_list[switch_num*2+1].split("/")[0]
		src_ip6_prefix = net6_list[switch_num*2].split("/")[0]
		while(try_group < 7):
			classifiers = {
			"dst-ip6-prefix":str(ipaddress.IPv6Address(dst_ip6_prefix)),
			"src-ip6-prefix":str(ipaddress.IPv6Address(src_ip6_prefix))
			}
			globals = {
			"group":try_group,
			 "ingress-interface": sw_dut.ixia_ports[0]
			}
			actions = {
			"count":"enable"
			}
			acl.config_acl6_generic(index,globals,classifiers,actions)
			sleep(2)
			index +=1
			try_group +=1
		sleep(10)
		acl.update_acl_usage()
		acl.print_acl_usage()
		acl.acl_ingress_clean_up()
		sleep(5)
		
		acl.update_acl_usage()
		acl.print_acl_usage()

		index = 1
		total_acl = 0
		for entry in acl.acl_usage_list:
			group_id = entry.group_id
			if group_id < 3:
				continue
			group_total = 0
			for i in range(entry.rule_total):
				classifiers = {
				"dst-ip6-prefix":dst_ip6_prefix,
				"src-ip6-prefix":src_ip6_prefix
				}
				globals = {
				"group":group_id,
				 "ingress-interface": sw_dut.ixia_ports[0]
				}
				actions = {
				"count":"enable"
				}
				acl.config_acl6_generic(index,globals,classifiers,actions)
				dst_ip6_prefix = str(ipaddress.IPv6Address(dst_ip6_prefix)+1)
				src_ip6_prefix = str(ipaddress.IPv6Address(src_ip6_prefix)+1)	
				index +=1
				total_acl +=1
				group_total +=1 
				stop_adding_acl_group = False
				if group_total > entry.rule_total/2 + 5: # check at half way to ensure things are good. 
					acl_working = switch_acl_ingress(sw_dut)
					for en in acl_working.acl_usage_list:
						if en.group_id == group_id and en.rule_free == 0:
							Info(f"!!!!! Before finish creating ACL entries in the slice, slice ran out of free rules")
							stop_adding_acl_group = True 
							break
					if stop_adding_acl_group == True:
						break
					else:
						group_total = 0 # Won't check again 

			acl.update_acl_usage()
			acl.print_acl_usage()		  
		#total_acl = 512
		final_total_acl = total_acl
		ixia_sub_intf = total_acl
		portList_v4_v6 = []
		for p,m,n4,g4,n6,g6 in zip(tb.ixia.port_active_list,mac_list,net4_list,gw4_list,net6_list,gw6_list):
			module,port = p.split("/")
			portList_v4_v6.append([ixChassisIpList[0], int(module),int(port),m,n4,g4,n6,g6,ixia_sub_intf])

		print(portList_v4_v6)
		myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)
		for topo in myixia.topologies:
			topo.add_ipv4(gateway="fixed",ip_incremental="0.0.0.1")
			topo.add_ipv6(gateway="fixed")

		myixia.start_protocol(wait=20)
		src_topo = myixia.topologies[switch_num * 2].topology
		dst_topo = myixia.topologies[switch_num * 2+1].topology
		myixia.create_traffic_v6(src_topo=src_topo, dst_topo=dst_topo,traffic_name=f"acl6_scale_traffic",tracking_name=f"Tracking_port{switch_num * 2}_port{switch_num * 2+1}_6",rate=20)
		myixia.start_traffic()
		sleep(10)
		myixia.stop_traffic()
		sleep(10)
		myixia.collect_stats()
		myixia.check_traffic()
		sw.print_show_command(f"get switch acl counter all",mode="fast")
		
		if longevity == False:
			print_double_line()
			keyin = input(f"Please verify the ixia traffic counter and switch ingress acl counter,Press any key when done:")
			print_double_line()

		if longevity == True:
			myixia.start_traffic()
			for i in range(30):
				acl.acl_ingress_clean_up()
				sleep(10)
				acl.update_acl_usage()
				dst_ip6_prefix = net6_list[switch_num*2+1].split("/")[0]
				src_ip6_prefix = net6_list[switch_num*2].split("/")[0]
				index = 1
				total_acl = 1
				for entry in acl.acl_usage_list:
					group_id = entry.group_id
					if group_id < 3:
						continue
					for i in range(entry.rule_total):
						classifiers = {
						"dst-ip6-prefix":dst_ip6_prefix,
						"src-ip6-prefix":src_ip6_prefix
						}
						globals = {
						"group":group_id,
						 "ingress-interface": sw_dut.ixia_ports[0]
						}
						actions = {
						"count":"enable"
						}
						acl.config_acl6_generic(index,globals,classifiers,actions)
						dst_ip6_prefix = str(ipaddress.IPv6Address(dst_ip6_prefix)+1)
						src_ip6_prefix = str(ipaddress.IPv6Address(src_ip6_prefix)+1)	
						index +=1
						total_acl +=1	

				sleep(10)
				myixia.clear_stats()
				sleep(20)
				Info(f"======================= Check traffic after one round of adding ACL entries =================")
				myixia.stop_traffic()
				myixia.check_traffic()
				sw.print_show_command(f"get switch acl counter all",mode="fast")
				sleep(10)
				myixia.start_traffic()
 

	def longevity_scale_acl6_testing(*args,**kwargs):
		switch_num_list = kwargs["switch_num_list"]
		ixia_sub_intf_list = []
		for switch_num in switch_num_list:
			switch_num -= 1 
			sw_dut = switches[switch_num]
			if "longevity" in kwargs:
				longevity = kwargs['longevity']
			else:
				longevity = False

			acl = switch_acl_ingress(sw_dut)
			acl.acl_ingress_clean_up()
	 
			try_group = 3
			index = 1
			dst_ip6_prefix = net6_list[switch_num*2+1].split("/")[0]
			src_ip6_prefix = net6_list[switch_num*2].split("/")[0]
			while(try_group < 7):
				classifiers = {
				"dst-ip6-prefix":str(ipaddress.IPv6Address(dst_ip6_prefix)),
				"src-ip6-prefix":str(ipaddress.IPv6Address(src_ip6_prefix))
				}
				globals = {
				"group":try_group,
				 "ingress-interface": sw_dut.ixia_ports[0]
				}
				actions = {
				"count":"enable"
				}
				acl.config_acl6_generic(index,globals,classifiers,actions)
				sleep(2)
				index +=1
				try_group +=1
			sleep(10)
			acl.update_acl_usage()
			acl.print_acl_usage()
			acl.acl_ingress_clean_up()
			sleep(5)
			
			acl.update_acl_usage()
			acl.print_acl_usage()

			index = 1
			total_acl = 0
			for entry in acl.acl_usage_list:
				Info("Before configuring one group of ACL, update the acl usage...")
				acl.update_acl_usage()
				acl.print_acl_usage()
				group_id = entry.group_id
				if group_id < 3:
					continue
				group_total = 0
				#test_num = entry.rule_total - 1
				test_num = 0
				for i in range(entry.rule_total - test_num):
					classifiers = {
					"dst-ip6-prefix":dst_ip6_prefix,
					"src-ip6-prefix":src_ip6_prefix
					}
					globals = {
					"group":group_id,
					 "ingress-interface": sw_dut.ixia_ports[0]
					}
					actions = {
					"count":"enable",
 					}
					acl.config_acl6_generic(index,globals,classifiers,actions)
					dst_ip6_prefix = str(ipaddress.IPv6Address(dst_ip6_prefix)+1)
					src_ip6_prefix = str(ipaddress.IPv6Address(src_ip6_prefix)+1)	
					index +=1
					total_acl +=1
					group_total +=1 
					stop_adding_acl_group = False
					if group_total > 128: # check every 128 entries to ensure things are good. 
						acl_working = switch_acl_ingress(sw_dut)
						for en in acl_working.acl_usage_list:
							if en.group_id == group_id and en.rule_free == 0:
								Info(f"!!!!! At the half way of creating ACL entries in the slice, slice ran out of free rules")
								stop_adding_acl_group = True 
								break
						if stop_adding_acl_group == True:
							break
						else:
							group_total = 0 # Won't check again 

			Info("After configuring All ACL configuration, update the acl usage...")
			acl.update_acl_usage()
			acl.print_acl_usage()
			total_acl_rules = 0 
			for entry in acl.acl_usage_list:
				group_id = entry.group_id
				if group_id < 3:
					continue
				total_acl_rules += (entry.rule_total - entry.rule_free)
			ixia_sub_intf_list.append(total_acl_rules)	  
			#total_acl = 512

		Info(f"ixia_sub_intf+list = {ixia_sub_intf_list}")
		 
		portList_v4_v6 = []
		i = 0
		for p,m,n4,g4,n6,g6 in zip(tb.ixia.port_active_list,mac_list,net4_list,gw4_list,net6_list,gw6_list):
		#for p,m,n4,g4,n6,g6 in zip(tb.ixia.port_active_list[:4],mac_list,net4_list,gw4_list,net6_list,gw6_list):
			module,port = p.split("/")
			portList_v4_v6.append([ixChassisIpList[0], int(module),int(port),m,n4,g4,n6,g6,ixia_sub_intf_list[int(i/2)]])
			i += 1

		print(f"Important!!!!!! Final IXIA ports mapping: {portList_v4_v6}")
		myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)
		for topo in myixia.topologies:
			#topo.add_ipv4(gateway="fixed",ip_incremental="0.0.0.1")
			topo.add_ipv6(gateway="fixed")

		myixia.start_protocol(wait=20)

		for switch_num in switch_num_list:
			switch_num -= 1
			src_topo = myixia.topologies[switch_num * 2].topology
			dst_topo = myixia.topologies[switch_num * 2+1].topology
			myixia.create_traffic_v6(src_topo=src_topo, dst_topo=dst_topo,traffic_name=f"acl6_scale_traffic_{switch_num}",tracking_name=f"Tracking_port{switch_num * 2}_port{switch_num * 2+1}_6",rate=10)
			sleep(5)
		sleep(5)
		myixia.start_traffic()
		# src_topo = myixia.topologies[switch_num * 2].topology
		# dst_topo = myixia.topologies[switch_num * 2+1].topology
		# myixia.create_traffic_v6(src_topo=src_topo, dst_topo=dst_topo,traffic_name=f"acl6_scale_traffic",tracking_name=f"Tracking_port{switch_num * 2}_port{switch_num * 2+1}_6",rate=20)
 		
		for switch_num in switch_num_list:
			switch_num -= 1 
			sw = switches[switch_num]
			sw.clear_crash_log()

		while True:
			myixia.stop_traffic()
			sleep(10)
			myixia.collect_stats()
			myixia.check_traffic()
			
			for switch_num in switch_num_list:
				switch_num -= 1 
				sw = switches[switch_num]
				sw.print_show_command(f"get switch acl counter all")
				sw.exec_command("execute acl clear-counter all")
				sw.find_crash()
				sw.get_crash_debug()
				found = sw.get_crash_log()
				if found:
					Info(f"!!!!!!!!!!!!At switch:{sw.hostname}, crash was found!!!!!!!!!!!!!!!!!!!")
				sleep(3)

			for switch_num in switch_num_list:
				switch_num -= 1 
				sw = switches[switch_num]
				sw.switch_reboot()

			console_timer(300,msg="Wait for 300s after rebooting all switches")

			for switch_num in switch_num_list:
				switch_num -= 1 
				sw = switches[switch_num]
				sw.sw_relogin()

			myixia.start_traffic()	
			console_timer(40,msg="Wait for 400s after checking each switch again")

	def longevity_scale_deconfig_acl6_testing(*args,**kwargs):
		switch_num_list = kwargs["switch_num_list"]
		ixia_sub_intf_list = []
		for switch_num in switch_num_list:
			switch_num -= 1 
			sw_dut = switches[switch_num]
			if "longevity" in kwargs:
				longevity = kwargs['longevity']
			else:
				longevity = False

			acl = switch_acl_ingress(sw_dut)
			acl.acl_ingress_clean_up()
	 
			try_group = 3
			index = 1
			dst_ip6_prefix = net6_list[switch_num*2+1].split("/")[0]
			src_ip6_prefix = net6_list[switch_num*2].split("/")[0]
			while(try_group < 7):
				classifiers = {
				"dst-ip6-prefix":str(ipaddress.IPv6Address(dst_ip6_prefix)),
				"src-ip6-prefix":str(ipaddress.IPv6Address(src_ip6_prefix))
				}
				globals = {
				"group":try_group,
				 "ingress-interface": sw_dut.ixia_ports[0]
				}
				actions = {
				"count":"enable"
				}
				acl.config_acl6_generic(index,globals,classifiers,actions)
				sleep(2)
				index +=1
				try_group +=1
			sleep(10)
			acl.update_acl_usage()
			acl.print_acl_usage()
			acl.acl_ingress_clean_up()
			sleep(5)
			
			acl.update_acl_usage()
			acl.print_acl_usage()

			index = 1
			total_acl = 0
			for entry in acl.acl_usage_list:
				Info("Before configuring one group of ACL, update the acl usage...")
				acl.update_acl_usage()
				acl.print_acl_usage()
				group_id = entry.group_id
				if group_id < 3:
					continue
				group_total = 0
				test_num = entry.rule_total - 5
				test_num = 0
				for i in range(entry.rule_total - test_num):
					classifiers = {
					"dst-ip6-prefix":dst_ip6_prefix,
					"src-ip6-prefix":src_ip6_prefix
					}
					globals = {
					"group":group_id,
					 "ingress-interface": sw_dut.ixia_ports[0]
					}
					actions = {
					"count":"enable",
 					}
					acl.config_acl6_generic(index,globals,classifiers,actions)
					dst_ip6_prefix = str(ipaddress.IPv6Address(dst_ip6_prefix)+1)
					src_ip6_prefix = str(ipaddress.IPv6Address(src_ip6_prefix)+1)	
					index +=1
					total_acl +=1
					group_total +=1 
					stop_adding_acl_group = False
					if group_total > 128: # check every 128 entries to ensure things are good. 
						acl_working = switch_acl_ingress(sw_dut)
						for en in acl_working.acl_usage_list:
							if en.group_id == group_id and en.rule_free == 0:
								Info(f"!!!!! At the half way of creating ACL entries in the slice, slice ran out of free rules")
								stop_adding_acl_group = True 
								break
						if stop_adding_acl_group == True:
							break
						else:
							group_total = 0 # Won't check again 

			Info("After configuring All ACL configuration, update the acl usage...")
			acl.update_acl_usage()
			acl.print_acl_usage()
			total_acl_rules = 0 
			for entry in acl.acl_usage_list:
				group_id = entry.group_id
				if group_id < 3:
					continue
				total_acl_rules += (entry.rule_total - entry.rule_free)
			ixia_sub_intf_list.append(total_acl_rules)	  
			#total_acl = 512

		Info(f"ixia_sub_intf+list = {ixia_sub_intf_list}")
		 
		portList_v4_v6 = []
		i = 0
		for p,m,n4,g4,n6,g6 in zip(tb.ixia.port_active_list,mac_list,net4_list,gw4_list,net6_list,gw6_list):
		#for p,m,n4,g4,n6,g6 in zip(tb.ixia.port_active_list[:4],mac_list,net4_list,gw4_list,net6_list,gw6_list):
			module,port = p.split("/")
			portList_v4_v6.append([ixChassisIpList[0], int(module),int(port),m,n4,g4,n6,g6,ixia_sub_intf_list[int(i/2)]])
			i += 1

		print(f"Important!!!!!! Final IXIA ports mapping: {portList_v4_v6}")
		myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)
		for topo in myixia.topologies:
			#topo.add_ipv4(gateway="fixed",ip_incremental="0.0.0.1")
			topo.add_ipv6(gateway="fixed")

		myixia.start_protocol(wait=20)

		for switch_num in switch_num_list:
			switch_num -= 1
			src_topo = myixia.topologies[switch_num * 2].topology
			dst_topo = myixia.topologies[switch_num * 2+1].topology
			myixia.create_traffic_v6(src_topo=src_topo, dst_topo=dst_topo,traffic_name=f"acl6_scale_traffic_{switch_num}",tracking_name=f"Tracking_port{switch_num * 2}_port{switch_num * 2+1}_6",rate=30)
			sleep(5)
		sleep(5)
		myixia.start_traffic()
		# src_topo = myixia.topologies[switch_num * 2].topology
		# dst_topo = myixia.topologies[switch_num * 2+1].topology
		# myixia.create_traffic_v6(src_topo=src_topo, dst_topo=dst_topo,traffic_name=f"acl6_scale_traffic",tracking_name=f"Tracking_port{switch_num * 2}_port{switch_num * 2+1}_6",rate=20)
 		
		for switch_num in switch_num_list:
			switch_num -= 1 
			sw = switches[switch_num]
			sw.clear_crash_log()

		while True:
			for switch_num in switch_num_list:
				switch_num -= 1 
				sw_dut = switches[switch_num]
				if "longevity" in kwargs:
					longevity = kwargs['longevity']
				else:
					longevity = False

				acl = switch_acl_ingress(sw_dut)
				acl.acl_ingress_clean_up()
		 
				try_group = 3
				index = 1
				dst_ip6_prefix = net6_list[switch_num*2+1].split("/")[0]
				src_ip6_prefix = net6_list[switch_num*2].split("/")[0]
				while(try_group < 7):
					classifiers = {
					"dst-ip6-prefix":str(ipaddress.IPv6Address(dst_ip6_prefix)),
					"src-ip6-prefix":str(ipaddress.IPv6Address(src_ip6_prefix))
					}
					globals = {
					"group":try_group,
					 "ingress-interface": sw_dut.ixia_ports[0]
					}
					actions = {
					"count":"enable"
					}
					acl.config_acl6_generic(index,globals,classifiers,actions)
					sleep(2)
					index +=1
					try_group +=1
				sleep(10)
				acl.update_acl_usage()
				acl.print_acl_usage()
				acl.acl_ingress_clean_up()
				sleep(5)
				
				acl.update_acl_usage()
				acl.print_acl_usage()

				index = 1
				total_acl = 0
				for entry in acl.acl_usage_list:
					Info("Before configuring one group of ACL, update the acl usage...")
					acl.update_acl_usage()
					acl.print_acl_usage()
					group_id = entry.group_id
					if group_id < 3:
						continue
					group_total = 0
					test_num = entry.rule_total - 5
					test_num = 0
					for i in range(entry.rule_total - test_num):
						classifiers = {
						"dst-ip6-prefix":dst_ip6_prefix,
						"src-ip6-prefix":src_ip6_prefix
						}
						globals = {
						"group":group_id,
						 "ingress-interface": sw_dut.ixia_ports[0]
						}
						actions = {
						"count":"enable",
	 					}
						acl.config_acl6_generic(index,globals,classifiers,actions)
						dst_ip6_prefix = str(ipaddress.IPv6Address(dst_ip6_prefix)+1)
						src_ip6_prefix = str(ipaddress.IPv6Address(src_ip6_prefix)+1)	
						index +=1
						total_acl +=1
						group_total +=1 
						stop_adding_acl_group = False
						if group_total > 128: # check every 128 entries to ensure things are good. 
							acl_working = switch_acl_ingress(sw_dut)
							for en in acl_working.acl_usage_list:
								if en.group_id == group_id and en.rule_free == 0:
									Info(f"!!!!! At the half way of creating ACL entries in the slice, slice ran out of free rules")
									stop_adding_acl_group = True 
									break
							if stop_adding_acl_group == True:
								break
							else:
								group_total = 0 # Won't check again 

				Info("After configuring All ACL configuration, update the acl usage...")
				acl.update_acl_usage()
				acl.print_acl_usage()
				total_acl_rules = 0 
				for entry in acl.acl_usage_list:
					group_id = entry.group_id
					if group_id < 3:
						continue
					total_acl_rules += (entry.rule_total - entry.rule_free)
				ixia_sub_intf_list.append(total_acl_rules)	  

				for switch_num in switch_num_list:
					switch_num -= 1 
					sw = switches[switch_num]
					sw.print_show_command(f"get switch acl counter all")
					sw.exec_command("execute acl clear-counter all")
					sw.find_crash()
					sw.get_crash_debug()
					found = sw.get_crash_log()
					if found:
						Info(f"!!!!!!!!!!!!At switch:{sw.hostname}, crash was found!!!!!!!!!!!!!!!!!!!")
					sleep(3)

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
		keyin = input(f"Please capture packets at IXIA to verify NO IPv6 packets. Press any key when done:")
		myixia.collect_stats()
		myixia.check_traffic()
		myixia.stop_traffic()


	def acl6_basic_color_testing():
		description = "Ingress 2 Color counter types : only igress policer"
		print(description)
		sw = switches[1]
		acl = switch_acl_ingress(sw)
		acl.acl_ingress_clean_up()

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
		sw.config_cmds_fast(cmds)
		sleep(10)

		index = 1
		classifiers = {
			"dst-ip6-prefix":str(ipaddress.IPv6Address(net6_list[1].split("/")[0])),
			"src-ip6-prefix":str(ipaddress.IPv6Address(net6_list[0].split("/")[0]))
		}
			
		globals = {
		"group":6,
         "ingress-interface": sw.ixia_ports[0]
        }
		
		actions = {
		"count":"enable",
		"count-type":"all",
		"policer":1
		}
		
		acl.config_acl6_generic(index,globals,classifiers,actions)


		ixia_sub_intf = 1
		portList_v4_v6 = []
		for p,m,n4,g4,n6,g6 in zip(tb.ixia.port_active_list,mac_list,net4_list,gw4_list,net6_list,gw6_list):
			module,port = p.split("/")
			portList_v4_v6.append([ixChassisIpList[0], int(module),int(port),m,n4,g4,n6,g6,ixia_sub_intf])

		myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)
		for topo in myixia.topologies:
			topo.add_ipv4(gateway="fixed",ip_incremental="0.0.0.1")
			topo.add_ipv6(gateway="fixed")
			
		myixia.start_protocol(wait=20)

		
		myixia.create_traffic_v6(src_topo=myixia.topologies[0].topology, dst_topo=myixia.topologies[1].topology,traffic_name=f"t0_to_t1_v6",tracking_name=f"Tracking_0_1_v6",rate=20)
 
		cmd = "execute acl clear-counter all"
		sw.exec_command(cmd)
		sleep(3)
		sw.show_command("get switch acl counters all")

		myixia.start_traffic()
		sleep(5)
		
		myixia.stop_traffic()
		sleep(10)
		ixia_stats_list = myixia.collect_stats()
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

		print(f"IXIA TX packet = {ixia_tx}, Ingress All Pkt = {obj.all_pkts}")
		print(f"#testing 2 color ingress counter-types ALL successful: {test_result}")
		keyin = input(f"Please verify ingress counter-types ALL,Press any key to continue:")

		# Test yellow and red drop packets
		classifiers = {}
		globals = {}
		actions = {}

		actions = {
		"count-type":"red yellow",
		}
		
		acl.config_acl6_generic(index,globals,classifiers,actions)
		sw.show_command("get switch acl counters all")

		myixia.start_traffic()
		sleep(5)
		
		myixia.stop_traffic()
		sleep(10)
		ixia_stats_list = myixia.collect_stats()
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
			if obj.red_pkts == 0 or obj.red_pkts == None and obj.type == "ingress":
				continue 
			else:
				if abs(ixia_drop - obj.yellow_pkts - obj.red_pkts) < 10:
					test_result = True 
		print(f"IXIA dropped packet = {ixia_drop}, Ingress Red Pkt = {obj.red_pkts},Ingress Yellow Pkt = {obj.yellow_pkts}")
		print(f"#testing 2 color ingress counter-types yellow and red successful: {test_result}")
		keyin = input(f"Please verify ingress counter-types yellow and red,Press any key to continue:")

		# Test green and red drop packets
		classifiers = {}
		globals = {}
		actions = {}

		actions = {
		"count-type":"red green",
		}
		
		acl.config_acl6_generic(index,globals,classifiers,actions)
		sw.show_command("get switch acl counters all")

		myixia.start_traffic()
		sleep(5)
		
		myixia.stop_traffic()
		sleep(10)
		ixia_stats_list = myixia.collect_stats()
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
			if obj.green_pkts == 0 or obj.green_pkts == None and obj.type == "ingress":
				continue 
			else:
				if abs(ixia_rx - obj.green_pkts) < 10 and ixia_drop > obj.red_pkts:
					test_result = True 

		print(f"IXIA received packet = {ixia_rx}, Ingress Green Pkt = {obj.green_pkts},Ingress Red Pkt = {obj.red_pkts}")
		print(f"#testing 2 color ingress counter-types green and red successful: {test_result}")
		keyin = input(f"Please verify ingress counter-types green and red,Press any key to continue:")

		# Test green packets
		classifiers = {}
		globals = {}
		actions = {}

		actions = {
		"count-type":"green",
		}
		
		acl.config_acl6_generic(index,globals,classifiers,actions)
		sw.show_command("get switch acl counters all")

		myixia.start_traffic()
		sleep(5)
		
		myixia.stop_traffic()
		sleep(10)
		ixia_stats_list = myixia.collect_stats()
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
			if obj.green_pkts == 0 or obj.green_pkts == None and obj.type == "ingress":
				continue 
			else:
				if abs(ixia_rx - obj.green_pkts) < 10 :
					test_result = True 
		print(f"IXIA received packet = {ixia_rx}, Ingress Green Pkt = {obj.green_pkts}")
		print(f"#testing 2 color ingress counter-types green and red successful: {test_result}")
		keyin = input(f"Please verify ingress counter-types green and red,Press any key to continue:")

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
		sw.print_show_command("show switch acl ingress",mode="fast")
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
		sw.print_show_command("show switch acl ingress",mode="fast")
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
		sw.print_show_command("show switch acl ingress",mode="fast")
		myixia.start_traffic()
		keyin = input(f"Please verify both IPv4 and IPv6 are forwarding. Press any key when done:")
		myixia.collect_stats()
		myixia.check_traffic()
		myixia.stop_traffic()

	################### Execution starts here ###################
	#longevity_scale_deconfig_acl6_testing(switch_num_list = [1,2,3])
	cpu_queue_acl6_testing(switch_num_list = [3])
	#longevity_scale_acl6_testing(switch_num_list = [1,2,3])
	#acl6_schedule_status_yaml(switch_num_list = [1])
	#dot1x_acl6_testing_yaml(switch_num_list = [1,2],factory=True)
	#dot1x_acl6_testing(switch_num_list = [2,3])
	#classifier_combo_testing(switch_num=1)
	#real_scale_acl6_testing(switch_num=1,longevity=False)
	#acl6_basic_color_testing()
	#acl_policer_testing()
	#qos_policy_testing()
	#classifier_l2_testing_yaml(switch_num_list = [1])
	#change_vlan_cos_dscp_testing()
	#basic_scale_acl6_testing(switch_num=2)
	#acl6_priority_testing()
	#acl6_redirect_mirror_testing()
	#basic_acl6_testing(switch_num_list = [1,2,3])
	#multiple_rules_acl6_testing(switch_num_list = [1])
	#basic_acl6_testing(switch_num_list = [1])
	#rvi_acl6_testing(switch_num_list = [3])
	#traffic_acl6_testing(switch_num_list = [1])
	#basic_acl6_drop_testing()
	exit()
	cmd = "execute acl clear-counter all"
	sw.exec_command(cmd)
	sleep(10)

	final_results = []
	
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
		        set ingress-interface "port2"         
		    next
			end
			
			config switch acl egress
		    edit 1
		        config action
		            set count enable
		            set count-type green yellow 
		            set policer 2
		        end
		        set interface "port3"         
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
