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



if __name__ == "__main__":

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
	file = 'tbinfo_mld.xml'
	tb = parse_tbinfo_untangle(file)
	testtopo_file = 'pim_topo.xml'
	parse_testtopo_untangle(testtopo_file,tb)
	tb.show_tbinfo()

	switches = []
	for d in tb.devices:
		if d.active:
			switch = FortiSwitch_XML(d,topo_db=tb)
			switches.append(switch)
	for c in tb.connections:
		c.update_devices_obj(switches)

	for c in tb.connections:
		c.shut_unused_ports()


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

		for sw in switches:
			sw.switch_factory_reset()

		console_timer(300,msg='After switches are factory reset, wait for 600 seconds')

		for sw in switches:
			sw.sw_relogin()
			dut = sw.console
			dut_name = sw.name
			image = find_dut_image(dut)
			tprint(f"============================ {dut_name} software image = {image} ============")
			sw.config_sw_after_factory()

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
	# for c in tb.connections:
	# 	c.unshut_all_ports()
	# switches = []
	# for d in tb.devices:
	# 	if d.active:
	# 		switch = FortiSwitch_XML(d)
	# 		switches.append(switch)
	apiServerIp = tb.ixia.ixnetwork_server_ip
	#ixChassisIpList = ['10.105.241.234']
	ixChassisIpList = [tb.ixia.chassis_ip]
 

	mac_list = ["00:11:01:01:01:01","00:12:01:01:01:01","00:13:01:01:01:01","00:14:01:01:01:01","00:15:01:01:01:01","00:16:01:01:01:01","00:17:01:01:01:01","00:18:01:01:01:01"]
	net4_list = ["10.1.1.2/16","10.1.100.2/16","10.1.1.213/24","10.1.1.214/24","10.1.1.215/24","10.1.1.216/24","10.1.1.217/24","10.1.1.218/24","10.1.1.219/24","10.1.1.220/24"]
	gw4_list = ["10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1"]
	net6_list = ["2001:10:1:1::211/64","2001:10:1:1::212/64","2001:10:1:1::213/64","2001:10:1:1::214/64","2001:10:1:1::215/64","2001:10:1:1::216/64","2001:10:1:1::217/64","2001:10:1:1::218/64"]
	gw6_list = ["2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1"]

	sw = switches[0]
	num = 10
	
	portList_v4_v6 = []
	for p,m,n4,g4,n6,g6 in zip(tb.ixia.port_active_list,mac_list,net4_list,gw4_list,net6_list,gw6_list):
		module,port = p.split("/")
		portList_v4_v6.append([ixChassisIpList[0], int(module),int(port),m,n4,g4,n6,g6,num])

	print(portList_v4_v6)

	vlan_ip = "10.1.1.1"
	iplist = increment_24(vlan_ip,num+1)
	start_vlan = 10
	i = 0
	svi_config = f"""
	config system interface
	"""
	for ip in iplist:
		config = f"""
		edit vlan{start_vlan+i}
		set ip {ip} 255.255.255.0
		set vlanid {start_vlan+i}
		set interface "internal"
		next
		"""
		i += 1
		svi_config += config
	config = f"""
	end
	"""
	svi_config += config

	print(svi_config)
	config_cmds_lines(sw.console,svi_config)

	start_vlan = 10
	myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6,vlan=start_vlan)
	for topo in myixia.topologies:
		#topo.add_ipv6()
		topo.add_ipv4()

	myixia.start_protocol(wait=200)


	ipgw = "10.1.1.2"
	iplist = increment_24(ipgw,num)

	num_mcast = 1000
	mcast_ip = "239.1.1.1"
	mcast_ip_list = increment_24(mcast_ip,num_mcast)
	flows_config = f"""
	config router multicast-flow
	"""
	i = 1
	for mcast_ip in mcast_ip_list:
		config = f"""
	    edit {i}
	            config flows
	                edit 1
	                    set group-addr {mcast_ip}
	                    set source-addr 10.1.1.2
	                next
	            end
	    next
		"""
		i += 1
		flows_config += config

	config = f"""
	end
	"""
	flows_config += config
	print(flows_config)
	config_cmds_lines(sw.console,flows_config)

	mcast_config = f"""
	config router multicast
       config interface
	"""

	for i in range(1,num+1):
		vlan_number = start_vlan + i
		config = f"""
            edit vlan11
                set pim-mode ssm-mode
                set multicast-flow {i}
            next
        """
		mcast_config += config
	config = f"""
		end
	set multicast-routing enable
	end
	"""
	mcast_config += config
	print(mcast_config)
	config_cmds_lines(sw.console,mcast_config)
	exit(0)
	for sw in switches:
		sw.fsw_show_cmd("get switch igmp-snooping group")
		sw.fsw_show_cmd("get switch mld-snooping group")

	myixia.create_mcast_traffic_v4(src_topo=myixia.topologies[0].topology, start_group="239.1.1.1",traffic_name="t0_239_1_1_1",num=10,tracking_name="Tracking_1")
	myixia.create_mcast_traffic_v6(src_topo=myixia.topologies[0].topology, start_group="ff3e::1:1:1",traffic_name="t0_ff3e_1_1_1",num=10,tracking_name="Tracking_2")
	myixia.start_traffic()
	console_timer(30,msg="Wait for 30s after started multicast traffic")
	myixia.collect_stats()
	myixia.check_traffic()

##################################################################################################################################################
##################################################################################################################################################
