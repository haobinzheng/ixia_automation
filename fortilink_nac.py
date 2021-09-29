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
	file = 'tbinfo_fortilink_expanded.xml'
	tb = parse_tbinfo_untangle(file)
	testtopo_file = 'fortilink_topo_expanded.xml'
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

		console_timer(1200,msg='After switches are factory reset, wait for 600 seconds')

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
		console_timer(1200,msg='After switches are rebooted, wait for 900 seconds')

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
				tprint(f"{sw.switch_id} is authorized and Up")
				fgt_active.execute_custom_command(switch_name=sw.switch_id,cmd="timeout")
				fgt_active.execute_custom_command(switch_name=sw.switch_id,cmd="console_output")
			else:
				tprint(f"{sw.switch_id} is Not authorized or Not up. Authorized={sw.authorized}, Up={sw.up}")

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
			print("After configurig everything, discover switch network again")
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

	global DEBUG

	for fgt in fortigates:
		if fgt.mode == "Active":
			fgt_active = fgt
			fgta = fgt
		else:
		 	fgt_passive = fgt
		 	fgtp = fgt


	#fortilink_name = "Myswitch"
	fortilink_name = "Myfortilink"

	end_end = f"""
		end
		end
	"""
	system_interfaces_config = f"""
		config vdom
			edit root
			config system interface
			edit "engvlan11"
		        set vdom "root"
		        set device-identification enable
		        set role lan
		        set switch-controller-access-vlan enable
		        set interface {fortilink_name}
		        set switch-controller-igmp-snooping disable
		        set switch-controller-dhcp-snooping enable
		        set vlanid 11
		    next
		    edit "marktingvlan12"
		        set vdom "root"
		        set device-identification enable
		        set role lan
		        set switch-controller-access-vlan enable
		        set switch-controller-igmp-snooping disable
		        set switch-controller-dhcp-snooping enable
		        set interface {fortilink_name}
		        set vlanid 12
		    next
		    edit "hrvlan13"
		        set vdom "root"
		        set device-identification enable
		        set role lan
		        set switch-controller-access-vlan enable
		        set switch-controller-igmp-snooping disable
		        set switch-controller-dhcp-snooping enable
		        set interface {fortilink_name}
		        set vlanid 13
		    next
		    edit "financevlan14"
		        set vdom "root"
		        set device-identification enable
		        set role lan
		        set switch-controller-access-vlan enable
		        set switch-controller-igmp-snooping disable
		        set switch-controller-dhcp-snooping enable
		        set interface {fortilink_name}
		        set vlanid 14
		    next
		    edit "tacvlan15"
		        set vdom "root"
		        set device-identification enable
		        set role lan
		        set switch-controller-access-vlan enable
		        set switch-controller-igmp-snooping disable
		        set switch-controller-dhcp-snooping enable
		        set interface {fortilink_name}
		        set vlanid 15
		    next
		    edit "salesvlan16"
		        set vdom "root"
		        set device-identification enable
		        set role lan
		        set switch-controller-access-vlan enable
		        set switch-controller-igmp-snooping disable
		        set switch-controller-dhcp-snooping enable
		        set interface {fortilink_name}
		        set vlanid 16
		    next
		    edit "acctvlan17"
		        set vdom "root"
		        set device-identification enable
		        set role lan
		        set switch-controller-access-vlan enable
		        set switch-controller-igmp-snooping disable
		        set switch-controller-dhcp-snooping enable
		        set interface {fortilink_name}
		        set vlanid 17
		    next
		    edit "secvlan18"
		        set vdom "root"
		        set device-identification enable
		        set role lan
		        set switch-controller-access-vlan enable
		        set switch-controller-igmp-snooping disable
		        set switch-controller-dhcp-snooping enable
		        set interface {fortilink_name}
		        set vlanid 18
		    edit {fgta.ixia_ports[0]}
		        set vdom "root"
		        set ip 172.168.1.1 255.255.255.0
		        set allowaccess ping https ssh snmp http fgfm speed-test
		        set type physical
		end
		end
		config vdom
			edit root
			conf system dhcp server
			edit 7
			        set dns-service default
			        set default-gateway 172.168.1.1
			        set netmask 255.255.255.0
			        set interface "port13"
			        config ip-range
			            edit 1
			                set start-ip 172.168.1.2
			                set end-ip 172.168.1.254
			            next
			        end
			    next
			end
		end
		end
		"""

	system_interfaces_config_scale = f"""
		config vdom
			edit root
			config system interface
		"""
	vlans = []
	for i in range(100,105):
		config = f"""
			edit vlan_{i}
		        set vdom "root"
		        set device-identification enable
		        set role lan
		        set switch-controller-access-vlan enable
		        set interface {fortilink_name}
		        set switch-controller-igmp-snooping enable
		        set dhcp-snooping trusted
		        set vlanid {i}
		    next
		"""
		system_interfaces_config_scale += config
		vlans.append(f"vlan_{i}")
	vlans_string = " ".join(vlans)

	config = f"""
	    edit {fgta.ixia_ports[0]}
	        set vdom "root"
	        set ip 172.168.1.1 255.255.255.0
	        set allowaccess ping https ssh snmp http fgfm speed-test
	        set type physical
	    next
	end
	end
	"""
	system_interfaces_config_scale += config

	delete_system_interfaces_config_scale = f"""
		config vdom
			edit root
			config system interface
		"""
	for v in vlans:
		config = f"""
		delete {v}
		"""
	delete_system_interfaces_config_scale += config

	delete_system_interfaces_config_scale += end_end

	fortilink_settings_config = f"""
		 config vdom
			edit root
			conf switch-controller fortilink-settings 
    			edit {fortilink_name}
        			config nac-ports
			            set onboarding-vlan "onboarding"
			            set lan-segment enabled
			            set nac-lan-interface "nac_segment"
			            set nac-segment-vlans "engvlan11" "financevlan14" "hrvlan13" "marktingvlan12" "tacvlan15" "salesvlan16" "acctvlan17" "voice" "secvlan18" "video"
			        end
			    next
			end
		end
		"""

	#vlans_string = vlans_string + " engvlan11 financevlan14 hrvlan13 marktingvlan12 tacvlan15 voice video"
	fortilink_settings_config_scale = f"""
		 config vdom
			edit root
			conf switch-controller fortilink-settings 
    			edit {fortilink_name}
        			config nac-ports
			            set onboarding-vlan "onboarding"
			            set lan-segment enabled
			            set nac-lan-interface "nac_segment"
			            set nac-segment-vlans {vlans_string}
			        end
			    next
			end
		end
		"""

	mac_policy_config = f"""
		config vdom
		edit root
		conf switch-controller  mac-policy 
		    edit "eng"
		        set fortilink {fortilink_name}
		        set vlan "engvlan11"
		    next
		    edit "marketing"
		        set fortilink {fortilink_name}
		        set vlan "marktingvlan12"
		    next
		    edit "hr"
		        set fortilink {fortilink_name}
		        set vlan "hrvlan13"
		    next
		    edit "finance"
		        set fortilink {fortilink_name}
		        set vlan "financevlan14"
		    next
		    edit "tac"
		        set fortilink {fortilink_name}
		        set vlan "tacvlan15"
		    next
		    edit "sales"
		        set fortilink {fortilink_name}
		        set vlan "salesvlan16"
		    next
		    edit "acct"
		        set fortilink {fortilink_name}
		        set vlan "acctvlan17"
		    next
		    edit "sec"
		        set fortilink {fortilink_name}
		        set vlan "secvlan18"
		    next
		    
		end
		end
		"""

	mac_policy_config_scale = f"""
		config vdom
		edit root
		conf switch-controller  mac-policy 
	"""
	for v in vlans:
		config = f"""
		    edit {v}
		        set fortilink {fortilink_name}
		        set vlan {v}
		    next
		"""
		
		mac_policy_config_scale += config

	config = f"""
		end
		end
	"""
	mac_policy_config_scale += config

	delete_mac_policy_config_scale = f"""
		config vdom
		edit root
		conf switch-controller  mac-policy 
	"""
	for v in vlans:
		config = f"""
		    delete {v}
		"""
		delete_mac_policy_config_scale += config

	 
	delete_mac_policy_config_scale += end_end

	user_nacpolicy_config = f"""
		config vdom
		edit root
		config user nac-policy
		    edit "eng-users"
		        set mac "00:11:**:**:**:**"
		        set switch-fortilink {fortilink_name}
		        set switch-mac-policy "eng"
		    next
		    edit "marketing-users"
		        set mac "00:12:**:**:**:**"
		        set switch-fortilink {fortilink_name}
		        set switch-mac-policy "marketing"
		    next
		    edit "hr-users"
		        set mac "00:13:**:**:**:**"
		        set switch-fortilink {fortilink_name}
		        set switch-mac-policy "hr"
		    next
		    edit "finance-users"
		        set mac "00:14:**:**:**:**"
		        set switch-fortilink {fortilink_name}
		        set switch-mac-policy "finance"
		    next
		    edit "tac-users"
		        set mac "00:15:**:**:**:**"
		        set switch-fortilink {fortilink_name}
		        set switch-mac-policy "tac"
		    next
		    edit "sales-users"
		        set mac "00:16:**:**:**:**"
		        set switch-fortilink {fortilink_name}
		        set switch-mac-policy "sales"
		    next
		    edit "acct-users"
		        set mac "00:17:**:**:**:**"
		        set switch-fortilink {fortilink_name}
		        set switch-mac-policy "acct"
		    next
		    edit "sec-users"
		        set mac "00:18:**:**:**:**"
		        set switch-fortilink {fortilink_name}
		        set switch-mac-policy "sec"
		    next
		end
		end
	"""

	macs = increment_mac_address(start_mac="00:11:00:00:00:00",num=500)

	user_nacpolicy_config_scale = f"""
		config vdom
		edit root
		config user nac-policy
	"""
	for v,m in zip(vlans,macs):
		config = f"""
		    edit {v}
		        set mac {m}
		        set switch-fortilink {fortilink_name}
		        set switch-mac-policy {v}
		    next
		"""
		user_nacpolicy_config_scale += config
	config = f"""
		end
		end
	"""
	user_nacpolicy_config_scale += config 

	delete_user_nacpolicy_config_scale = f"""
		config vdom
		edit root
		config user nac-policy
	"""
	for v,m in zip(vlans,macs):
		config = f"""
		    delete {v}
		"""
		delete_user_nacpolicy_config_scale += config
 
	delete_user_nacpolicy_config_scale += end_end

	user_nacpolicy_config_unmatched = f"""
		config vdom
		edit root
		config user nac-policy
		    edit "eng-users"
		        set mac "88:11:**:**:**:**"
		        set switch-fortilink {fortilink_name}
		        set switch-mac-policy "eng"
		    next
		    edit "marketing-users"
		        set mac "88:12:**:**:**:**"
		        set switch-fortilink {fortilink_name}
		        set switch-mac-policy "marketing"
		    next
		    edit "hr-users"
		        set mac "88:13:**:**:**:**"
		        set switch-fortilink {fortilink_name}
		        set switch-mac-policy "hr"
		    next
		    edit "finance-users"
		        set mac "88:14:**:**:**:**"
		        set switch-fortilink {fortilink_name}
		        set switch-mac-policy "finance"
		    next
		end
		end
	"""
	delete_system_interfaces_config = f"""
		config vdom
			edit root
			config system interface
			delete "engvlan11"
	 		delete "marktingvlan12"
		    delete "hrvlan13"
		 	delete "financevlan14"
		  	delete "tacvlan15"
		  	delete "salesvlan16"
		  	delete "acctvlan17"
		end
		end
	"""

	delete_fortilink_settings_config = f"""
		 config vdom
			edit root
			conf switch-controller fortilink-settings 
    			edit {fortilink_name}
        			config nac-ports
			            set onboarding-vlan "onboarding"
			            set lan-segment disable
			            unset set nac-lan-interface  
			            unset nac-segment-vlans 
			        end
			    next
			end
	"""
	delete_mac_policy_config = f"""
		config vdom
		edit root
		conf switch-controller mac-policy 
		    delete "eng"
		    delete "hr"
		    delete "marketing"
		    delete  "tac"
		    delete "finance"
		    delete "sales"
		    delete "acct"
		end
		end
	"""
	delete_user_nacpolicy_config = f"""
		config vdom
		edit root
		config user nac-policy
		    delete "eng-users"
		    delete "marketing-users"
		   	delete "hr-users"
		    delete "finance-users"
		    delete "sales-users"
		    delete "acct-users"
		end
		end
	"""

	initial_testing = True
	initial_config = True
	inital_testing_only = False


	if initial_config:
		nac_config = system_interfaces_config + fortilink_settings_config + mac_policy_config + user_nacpolicy_config
		config_cmds_lines(fgta.console,nac_config)
		
		managed_sw_list = fgta.discover_managed_switches(topology=tb)
		fgta.config_custom_timeout()
		for msw in managed_sw_list:
			msw.print_managed_sw_info()
			if msw.authorized and msw.up:
				print(f"{msw.switch_id} is authorized and Up")
				fgta.execute_custom_command(switch_name=msw.switch_id,cmd="timeout")
				if len(msw.switch_obj.ixia_ports) == 0:
					continue
				for port in msw.switch_obj.ixia_ports:
					config = f"""
					config vdom
						edit root
							config switch-controller managed-switch
								edit {msw.switch_id}
								config ports
									edit {port}
										set access-mode nac
									next
								end
							end
					end
					"""
					config_cmds_lines(fgta.console,config)

			else:
				print(f"{msw.switch_id} is Not authorized or Not up. Authorized={msw.authorized}, Up={msw.up}")

	
	for sw in switches:
		print_attributes(sw)

	for fgt in fortigates:
		print_attributes(fgt)

	apiServerIp = tb.ixia.ixnetwork_server_ip
	#ixChassisIpList = ['10.105.241.234']
	ixChassisIpList = [tb.ixia.chassis_ip]
 

	mac_list = ["00:11:01:01:01:01","00:12:01:01:01:01","00:13:01:01:01:01","00:14:01:01:01:01","00:15:01:01:01:01","00:16:01:01:01:01","00:17:01:01:01:01","00:18:01:01:01:01"]
	net4_list = ["10.1.1.211/24","10.1.1.212/24","10.1.1.213/24","10.1.1.214/24","10.1.1.215/24","10.1.1.216/24","10.1.1.217/24","10.1.1.218/24","10.1.1.219/24","10.1.1.220/24"]
	gw4_list = ["10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1"]
	net6_list = ["2001:10:1:1::211/64","2001:10:1:1::212/64","2001:10:1:1::213/64","2001:10:1:1::214/64","2001:10:1:1::215/64","2001:10:1:1::216/64","2001:10:1:1::217/64","2001:10:1:1::218/64"]
	gw6_list = ["2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1"]
	device_list = ["sw","sw","sw","fgt1","sw"]
	device_list = tb.ixia.device_list_active
	print(f"~~~~~~~~~~~~~~~~ device_list = {device_list}")

	portList_v4_v6 = []
	for p,m,n4,g4,n6,g6 in zip(tb.ixia.port_active_list,mac_list,net4_list,gw4_list,net6_list,gw6_list):
		module,port = p.split("/")
		portList_v4_v6.append([ixChassisIpList[0], int(module),int(port),m,n4,g4,n6,g6,200])

	print(portList_v4_v6)

	myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)
	for topo in myixia.topologies:
		topo.add_dhcp_client()

	for topo,dev in zip(myixia.topologies,device_list):
		topo.connected_device = dev

	if initial_testing:
		myixia.start_protocol(wait=200)

		for i in range(0,len(tb.ixia.port_active_list)-1):
			for j in range(i+1,len(tb.ixia.port_active_list)):
				if "FG2K" in myixia.topologies[i].connected_device or "FG2K" in myixia.topologies[j].connected_device:
					myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=1)
					myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=1)


		# for i in range(0,len(tb.ixia.port_active_list)-1):
		# 	for j in range(i+1,len(tb.ixia.port_active_list)):
		# 		myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=1)
		# 		myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=1)

		myixia.start_traffic()
		myixia.collect_stats()
		myixia.check_traffic()
		myixia.stop_traffic()
		if inital_testing_only:
			tprint("=============== Initial tesitng only, bye! ==================")
			exit()

	for sw in switches:
		sw.get_crash_log()

	if testcase == 0:
		print("Just do a intial_testing and exiting....")
		exit(0)

	if testcase == 1 or test_all:
		testcase = 1
		myixia.start_traffic()
		for sw in switches:
			sw.clear_crash_log()
		managed_sw_list = fgta.discover_managed_switches(topology=tb)
		fgta.config_custom_timeout()
		for msw in managed_sw_list:
			msw.print_managed_sw_info()
			if msw.authorized and msw.up:
				print(f"{msw.switch_id} is authorized and Up")
				fgta.execute_custom_command(switch_name=msw.switch_id,cmd="timeout")
				if len(msw.switch_obj.ixia_ports) == 0:
					continue
				for port in msw.switch_obj.ixia_ports:
					config = f"""
					config vdom
						edit root
							config switch-controller managed-switch
								edit {msw.switch_id}
								config ports
									edit {port}
										set access-mode static
									next
								end
							end
					end
					"""
					config_cmds_lines(fgta.console,config)
		console_timer(200,msg=f"Testcase #{testcase}:After disabling access-mode nac, wait for 200s")
		for msw in managed_sw_list:
			msw.print_managed_sw_info()
			if msw.authorized and msw.up:
				print(f"{msw.switch_id} is authorized and Up")
				fgta.execute_custom_command(switch_name=msw.switch_id,cmd="timeout")
				if len(msw.switch_obj.ixia_ports) == 0:
					continue
				for port in msw.switch_obj.ixia_ports:
					config = f"""
					config vdom
						edit root
							config switch-controller managed-switch
								edit {msw.switch_id}
								config ports
									edit {port}
										set access-mode nac
									next
								end
							end
					end
					"""
					config_cmds_lines(fgta.console,config)
		console_timer(20,msg=f"Testcase #{testcase}:After enabling access-mode nac, wait for 20s")
		myixia.stop_traffic()
		myixia.start_traffic()
		myixia.check_traffic()
		myixia.stop_traffic()
		for sw in switches:
			sw.get_crash_log()
	 
	if testcase == 2 or test_all:
		testcase = 2
		myixia.stop_protocol()
		for sw in switches:
			sw.clear_crash_log()
		managed_sw_list = fgta.discover_managed_switches(topology=tb)
		fgta.config_custom_timeout()
		for msw in managed_sw_list:
			msw.print_managed_sw_info()
			if msw.authorized and msw.up:
				print(f"{msw.switch_id} is authorized and Up")
				fgta.execute_custom_command(switch_name=msw.switch_id,cmd="timeout")
				if len(msw.switch_obj.ixia_ports) == 0:
					continue
				for port in msw.switch_obj.ixia_ports:
					config = f"""
					config vdom
						edit root
							config switch-controller managed-switch
								edit {msw.switch_id}
								config ports
									edit {port}
										set access-mode static
									next
								end
							end
					end
					"""
					config_cmds_lines(fgta.console,config)

		myixia.start_protocol(wait=200)

		console_timer(60,msg=f"Testcase #{testcase}:After start protocol with NAC mode disable, wait for 60s")
		myixia.stop_protocol()

		for msw in managed_sw_list:
			msw.print_managed_sw_info()
			if msw.authorized and msw.up:
				print(f"{msw.switch_id} is authorized and Up")
				fgta.execute_custom_command(switch_name=msw.switch_id,cmd="timeout")
				if len(msw.switch_obj.ixia_ports) == 0:
					continue
				for port in msw.switch_obj.ixia_ports:
					config = f"""
					config vdom
						edit root
							config switch-controller managed-switch
								edit {msw.switch_id}
								config ports
									edit {port}
										set access-mode nac
									next
								end
							end
					end
					"""
					config_cmds_lines(fgta.console,config)
		myixia.start_protocol(wait=200)
		console_timer(60,msg=f"Testcase #{testcase}:After start protocol with NAC mode enable, wait for 60s")
		myixia.start_traffic()
		myixia.check_traffic()
		myixia.stop_traffic()
		for sw in switches:
			sw.get_crash_log()

	if testcase == 3 or test_all:
		testcase = 3
		myixia.start_traffic()
		for sw in switches:
			sw.clear_crash_log()
		managed_sw_list = fgta.discover_managed_switches(topology=tb)
		fgta.config_custom_timeout()
		for msw in managed_sw_list:
			msw.print_managed_sw_info()
			if msw.authorized and msw.up:
				print(f"{msw.switch_id} is authorized and Up")
				fgta.execute_custom_command(switch_name=msw.switch_id,cmd="timeout")
				if len(msw.switch_obj.ixia_ports) == 0:
					continue
				for port in msw.switch_obj.ixia_ports:
					config = f"""
					config vdom
						edit root
							config switch-controller managed-switch
								edit {msw.switch_id}
								config ports
									edit {port}
										set access-mode static
									next
								end
							end
					end
					"""
					config_cmds_lines(fgta.console,config)
		console_timer(20,msg=f"Testcase #{testcase}:After disabling access-mode nac, wait for 20s")

		delete_nac_config = delete_user_nacpolicy_config + delete_mac_policy_config + delete_fortilink_settings_config + delete_system_interfaces_config 
		config_cmds_lines(fgta.console,delete_nac_config)

		console_timer(60,msg=f"Testcase #{testcase}:After deleting all the NAC configuration, wait for 60s")
 
		nac_config = system_interfaces_config + fortilink_settings_config + mac_policy_config + user_nacpolicy_config
		config_cmds_lines(fgta.console,nac_config)

		for msw in managed_sw_list:
			msw.print_managed_sw_info()
			if msw.authorized and msw.up:
				print(f"{msw.switch_id} is authorized and Up")
				fgta.execute_custom_command(switch_name=msw.switch_id,cmd="timeout")
				if len(msw.switch_obj.ixia_ports) == 0:
					continue
				for port in msw.switch_obj.ixia_ports:
					config = f"""
					config vdom
						edit root
							config switch-controller managed-switch
								edit {msw.switch_id}
								config ports
									edit {port}
										set access-mode nac
									next
								end
							end
					end
					"""
					config_cmds_lines(fgta.console,config)
		console_timer(20,msg=f"Testcase #{testcase}:After enabling access-mode nac, wait for 20s")
		myixia.stop_traffic()
		myixia.start_traffic()
		myixia.check_traffic()
		myixia.stop_traffic()
		for sw in switches:
			sw.get_crash_log()

	if testcase == 4 or test_all:
		testcase = 4
		description = "negative: change port nac--> static --> nac, user unmatched"
		myixia.start_traffic()
		for sw in switches:
			sw.clear_crash_log()
		managed_sw_list = fgta.discover_managed_switches(topology=tb)
		fgta.config_custom_timeout()
		for msw in managed_sw_list:
			msw.print_managed_sw_info()
			if msw.authorized and msw.up:
				print(f"{msw.switch_id} is authorized and Up")
				fgta.execute_custom_command(switch_name=msw.switch_id,cmd="timeout")
				if len(msw.switch_obj.ixia_ports) == 0:
					continue
				for port in msw.switch_obj.ixia_ports:
					config = f"""
					config vdom
						edit root
							config switch-controller managed-switch
								edit {msw.switch_id}
								config ports
									edit {port}
										set access-mode static
									next
								end
							end
					end
					"""
					config_cmds_lines(fgta.console,config)
		console_timer(20,msg=f"Testcase #{testcase}:After disabling access-mode nac, wait for 20s")

		delete_nac_config = delete_user_nacpolicy_config + delete_mac_policy_config + delete_fortilink_settings_config + delete_system_interfaces_config 
		config_cmds_lines(fgta.console,delete_nac_config)

		console_timer(60,msg=f"Testcase #{testcase}:After deleting all the NAC configuration, wait for 60s")
 
		nac_config = system_interfaces_config + fortilink_settings_config + mac_policy_config + user_nacpolicy_config_unmatched
		config_cmds_lines(fgta.console,nac_config)

		for msw in managed_sw_list:
			msw.print_managed_sw_info()
			if msw.authorized and msw.up:
				print(f"{msw.switch_id} is authorized and Up")
				fgta.execute_custom_command(switch_name=msw.switch_id,cmd="timeout")
				if len(msw.switch_obj.ixia_ports) == 0:
					continue
				for port in msw.switch_obj.ixia_ports:
					config = f"""
					config vdom
						edit root
							config switch-controller managed-switch
								edit {msw.switch_id}
								config ports
									edit {port}
										set access-mode nac
									next
								end
							end
					end
					"""
					config_cmds_lines(fgta.console,config)
		console_timer(20,msg=f"Testcase #{testcase}:After enabling access-mode nac, wait for 20s")
		myixia.stop_traffic()
		myixia.start_traffic()
		myixia.check_traffic()
		myixia.stop_traffic()
		for sw in switches:
			sw.get_crash_log()

	if testcase == 5 or test_all:
		testcase = 5
		description = "switch port changed from dynaic to nac, longevity"
		print_test_subject(testcase,description)
		myixia.start_traffic()
		for sw in switches:
			sw.clear_crash_log()
		managed_sw_list = fgta.discover_managed_switches(topology=tb)
		fgta.config_custom_timeout()
		for msw in managed_sw_list:
			msw.print_managed_sw_info()
			if msw.authorized and msw.up:
				print(f"{msw.switch_id} is authorized and Up")
				fgta.execute_custom_command(switch_name=msw.switch_id,cmd="timeout")
				if len(msw.switch_obj.ixia_ports) == 0:
					continue
				for port in msw.switch_obj.ixia_ports:
					config = f"""
					config vdom
						edit root
							config switch-controller managed-switch
								edit {msw.switch_id}
								config ports
									edit {port}
										set access-mode dynamic
									next
								end
							end
					end
					"""
					config_cmds_lines(fgta.console,config)
		console_timer(20,msg=f"Testcase #{testcase}:After disabling access-mode nac, wait for 20s")


		for i in range(2):
			delete_nac_config = delete_user_nacpolicy_config + delete_mac_policy_config + delete_fortilink_settings_config + delete_system_interfaces_config 
			config_cmds_lines(fgta.console,delete_nac_config)

			console_timer(60,msg=f"Testcase #{testcase}:After deleting all the NAC configuration, wait for 60s")
	 
			nac_config = system_interfaces_config + fortilink_settings_config + mac_policy_config + user_nacpolicy_config
			config_cmds_lines(fgta.console,nac_config)

			console_timer(120,msg=f"Testcase #{testcase}:After finishing all the NAC configuration, wait for 120s")

			for msw in managed_sw_list:
				msw.print_managed_sw_info()
				if msw.authorized and msw.up:
					print(f"{msw.switch_id} is authorized and Up")
					fgta.execute_custom_command(switch_name=msw.switch_id,cmd="timeout")
					if len(msw.switch_obj.ixia_ports) == 0:
						continue
					for port in msw.switch_obj.ixia_ports:
						config = f"""
						config vdom
							edit root
								config switch-controller managed-switch
									edit {msw.switch_id}
									config ports
										edit {port}
											set access-mode nac
										next
									end
								end
						end
						"""
						config_cmds_lines(fgta.console,config)
			console_timer(20,msg=f"Testcase #{testcase}:After enabling access-mode nac, wait for 20s")

			myixia.stop_traffic()
			myixia.stop_protocol()
			sleep(10)
			myixia.start_protocol(wait=200)
			myixia.start_traffic()
			myixia.check_traffic()
			for sw in switches:
				sw.get_crash_log()


	if testcase == 6 or test_all:
		testcase = 6
		description = "IGMP snooping"
		print_test_subject(testcase,description)
		myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)
		igmp_ports = ["source","host","host","querier"]
		for topo, role in zip(myixia.topologies,igmp_ports):
			topo.igmp_role = role
		for topo in myixia.topologies:
			topo.add_dhcp_client()
			if topo.igmp_role == "host":
				topo.add_igmp_host_v4(start_addr="239.1.1.1",num=10)
			elif topo.igmp_role == "querier":
				topo.add_igmp_querier_v4()

		myixia.start_protocol(wait=200)

		for sw in switches:
			sw.fsw_show_cmd("get switch igmp-snooping group")
			sw.fsw_show_cmd("get switch mld-snooping group")

		myixia.create_mcast_traffic_v4(src_topo=myixia.topologies[0].topology, start_group="239.1.1.1",traffic_name="t0_239_1_1_1",num=10,tracking_name="Tracking_1")
		myixia.start_traffic()
		console_timer(30,msg="Wait for 30s after started multicast traffic")
		myixia.collect_stats()
		myixia.check_traffic()

	if testcase == 7 or test_all:
		testcase = 7
		description = "Broadcast"
		print_test_subject(testcase,description)
		myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)
		for topo in myixia.topologies:
			topo.add_dhcp_client()

		myixia.start_protocol(wait=200)

		for i in range(0,len(tb.ixia.port_active_list)):
			myixia.create_traffic_destination_v4(src_topo=myixia.topologies[i].topology, dst="255.255.255.255",traffic_name=f"t{i}_broadcast",tracking_name=f"Tracking_{i+1}_v4",rate=1)
 
		myixia.start_traffic()
		myixia.collect_stats()
		myixia.check_traffic()
		myixia.stop_traffic()

	if testcase == 8 or test_all:
		testcase = 8
		description = "Broadcast testing using dhcp clients"
		portList_v4_v6 = []
		for p,m,n4,g4,n6,g6 in zip(tb.ixia.port_active_list,mac_list,net4_list,gw4_list,net6_list,gw6_list):
			module,port = p.split("/")
			portList_v4_v6.append([ixChassisIpList[0], int(module),int(port),m,n4,g4,n6,g6,50])

		print_test_subject(testcase,description)
		myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)
		for topo in myixia.topologies:
			topo.add_dhcp_client()

		myixia.start_protocol(wait=200)

	if testcase == 9 or test_all:
		testcase = 9
		description = "Scale MAC Policy and user nac-policy"
		while True:
			keyin = input(f"Do you want to configure the scaled configuration(Y/N): ")
			nac_config = system_interfaces_config_scale + fortilink_settings_config_scale + mac_policy_config_scale + user_nacpolicy_config_scale
			config_cmds_lines(fgta.console,nac_config,mode="fast")


		while True:
			keyin = input(f"Do you want to delete the scaled configuration(Y/N): ")
			if keyin.upper() == "Y":
				print("!!!!! Deleting all the scaled LAN Segment related configuration")
				delete_nac_config = delete_user_nacpolicy_config_scale + delete_mac_policy_config_scale + delete_fortilink_settings_config + delete_system_interfaces_config_scale
				config_cmds_lines(fgta.console,delete_nac_config,mode="fast")
				break
			else:
				break

		while True:
			keyin = input(f"Do you want to reboot all switches(Y/N): ")
			if keyin.upper() == "Y":
				for sw in switches:
					sw.switch_reboot()
					console_timer(600,msg='After switches are rebooted, wait for 600 seconds')
					break
			else:
				break

		while True:
			keyin = input(f"Do you want to delete the scaled configuration(Y/N): ")
			if keyin.upper() == "Y":
				print("!!!!! Deleting all the scaled LAN Segment related configuration")
				delete_nac_config = delete_user_nacpolicy_config_scale + delete_mac_policy_config_scale + delete_fortilink_settings_config + delete_system_interfaces_config_scale
				config_cmds_lines(fgta.console,delete_nac_config,mode="fast")
				break
		keyin = input(f"Do you want to configure the scaled configuration(Y/N): ")
		if keyin.upper() == "Y":
			print("Start to configure scaled mac policy and user policy")
			nac_config = system_interfaces_config_scale + fortilink_settings_config_scale + mac_policy_config_scale + user_nacpolicy_config_scale
			config_cmds_lines(fgta.console,nac_config,mode="fast")

		while True:
			keyin = input(f"Do you want to delete the scaled configuration(Y/N): ")
			if keyin.upper() == "Y":
				print("!!!!! Deleting all the scaled LAN Segment related configuration")
				delete_nac_config = delete_user_nacpolicy_config_scale + delete_mac_policy_config_scale + delete_fortilink_settings_config + delete_system_interfaces_config_scale
				config_cmds_lines(fgta.console,delete_nac_config,mode="fast")
				break


	if testcase == 10 or test_all:
		testcase = 10
		description = "Scale MAC Policy and user nac-policy and config and delete "
		 
		for sw in switches:
			sw.clear_crash_log()

		for i in range(2):
			print(f"================ This is the #{i+1} iterating config/delete =============== ")
			
			# nac_config = system_interfaces_config_scale + fortilink_settings_config_scale + mac_policy_config_scale + user_nacpolicy_config_scale
			# config_cmds_lines(fgta.console,nac_config,mode="slow")
			# sleep(30)

			print("!!!!! Deleting all the scaled LAN Segment related configuration")
			delete_nac_config = delete_user_nacpolicy_config_scale + delete_mac_policy_config_scale + delete_fortilink_settings_config + delete_system_interfaces_config_scale
			config_cmds_lines(fgta.console,delete_nac_config,mode="slow")

			nac_config = system_interfaces_config_scale + fortilink_settings_config_scale + mac_policy_config_scale + user_nacpolicy_config_scale
			config_cmds_lines(fgta.console,nac_config,mode="slow")
			sleep(30)

			i +=1

			# for sw in switches:
			# 	sw.get_crash_log()

	if testcase == 11 or test_all:
		testcase = 11
		description = "Fortigate HA failover"

		for i in range(0,len(tb.ixia.port_active_list)-1):
			for j in range(i+1,len(tb.ixia.port_active_list)):
				myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=1)
				myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=1)

		 
		myixia.stop_protocol()

		for i in range(10):

			fgt_active.ha_failover()
			sleep(60)

			myixia.start_protocol(wait=200)

			myixia.start_traffic()
			console_timer(30,msg="Wait for 30s after started multicast traffic")
			myixia.collect_stats()
			myixia.check_traffic()
			myixia.stop_traffic()

			myixia.stop_protocol()

			fgt_passive.ha_failover()
			sleep(60)
			myixia.start_protocol(wait=200)
			myixia.start_traffic()
			console_timer(30,msg="Wait for 30s after started multicast traffic")
			myixia.collect_stats()
			myixia.check_traffic()
			myixia.stop_traffic()
			myixia.stop_protocol()

	if testcase == 12 or test_all:
		testcase = 12
		description = "Same segment can communicate with each other"

		mac_list = ["00:11:01:01:01:01","00:11:02:01:01:01","00:11:03:01:01:01","00:11:04:01:01:01","00:11:05:01:01:01","00:11:06:01:01:01","00:11:07:01:01:01","00:11:08:01:01:01"]
		net4_list = ["10.1.1.211/24","10.1.1.212/24","10.1.1.213/24","10.1.1.214/24","10.1.1.215/24","10.1.1.216/24","10.1.1.217/24","10.1.1.218/24","10.1.1.219/24","10.1.1.220/24"]
		gw4_list = ["10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1"]
		net6_list = ["2001:10:1:1::211/64","2001:10:1:1::212/64","2001:10:1:1::213/64","2001:10:1:1::214/64","2001:10:1:1::215/64","2001:10:1:1::216/64","2001:10:1:1::217/64","2001:10:1:1::218/64"]
		gw6_list = ["2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1"]

		portList_v4_v6 = []
		for p,m,n4,g4,n6,g6 in zip(tb.ixia.port_active_list,mac_list,net4_list,gw4_list,net6_list,gw6_list):
			module,port = p.split("/")
			portList_v4_v6.append([ixChassisIpList[0], int(module),int(port),m,n4,g4,n6,g6,10])

		print(portList_v4_v6)

		myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)
		for topo in myixia.topologies:
			topo.add_dhcp_client()

		
		myixia.start_protocol(wait=200)

		
		for i in range(0,len(tb.ixia.port_active_list)-1):
			for j in range(i+1,len(tb.ixia.port_active_list)):
				myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=1)
				myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=1)

		myixia.start_traffic()
		myixia.collect_stats()
		myixia.check_traffic()
		myixia.stop_traffic()


	if testcase == 13 or test_all:
		testcase = 13
		description = "Each port is individually vlan tagged with its user vlan, won't work"

		mac_list = ["00:11:01:01:01:01","00:12:02:01:01:01","00:13:03:01:01:01","00:14:04:01:01:01","00:15:05:01:01:01","00:16:06:01:01:01","00:17:07:01:01:01","00:18:08:01:01:01"]
		net4_list = ["10.1.1.211/24","10.1.1.212/24","10.1.1.213/24","10.1.1.214/24","10.1.1.215/24","10.1.1.216/24","10.1.1.217/24","10.1.1.218/24","10.1.1.219/24","10.1.1.220/24"]
		gw4_list = ["10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1"]
		net6_list = ["2001:10:1:1::211/64","2001:10:1:1::212/64","2001:10:1:1::213/64","2001:10:1:1::214/64","2001:10:1:1::215/64","2001:10:1:1::216/64","2001:10:1:1::217/64","2001:10:1:1::218/64"]
		gw6_list = ["2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1"]
		vlan_list = [11,12,13,14,15,16,17,18]
		device_list = tb.ixia.device_list_active

		print(f"~~~~~~~~~~~~~~~~ device_list = {device_list}")

		portList_v4_v6 = []
		for p,m,n4,g4,n6,g6 in zip(tb.ixia.port_active_list,mac_list,net4_list,gw4_list,net6_list,gw6_list):
			module,port = p.split("/")
			portList_v4_v6.append([ixChassisIpList[0], int(module),int(port),m,n4,g4,n6,g6,1])


		print(portList_v4_v6)
		for ixia_port,dev,vlan in zip(portList_v4_v6,device_list,vlan_list):
			if "FG2K" not in dev:
				ixia_port.append(vlan)
			else:
				ixia_port.append("vlan_null")

		print(portList_v4_v6)

		myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6,different_vlan=True)
		for topo in myixia.topologies:
			topo.add_dhcp_client()

		for topo,dev in zip(myixia.topologies,device_list):
			topo.connected_device = dev
		
		myixia.start_protocol(wait=200)

		
		for sw in switches:
			if len(sw.ixia_ports) >= 1:
				sw.show_command("show switch vlan")
				sw.show_command("show switch acl ingress")
				for port in sw.ixia_ports:
					sw.show_command(f"show switch interface {port}")

		for i in range(0,len(tb.ixia.port_active_list)-1):
			for j in range(i+1,len(tb.ixia.port_active_list)):
				if "FG2K" in myixia.topologies[i].connected_device or "FG2K" in myixia.topologies[j].connected_device:
					myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=1)
					myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=1)

		myixia.start_traffic()
		myixia.collect_stats()
		myixia.check_traffic()
		myixia.stop_traffic()

	if testcase == 14 or test_all:
		testcase = 14
		description = "Each port is vlan tagged with primary vlan, won't work"

		mac_list = ["00:11:01:01:01:01","00:12:02:01:01:01","00:13:03:01:01:01","00:14:04:01:01:01","00:15:05:01:01:01","00:16:06:01:01:01","00:17:07:01:01:01","00:18:08:01:01:01"]
		net4_list = ["10.1.1.211/24","10.1.1.212/24","10.1.1.213/24","10.1.1.214/24","10.1.1.215/24","10.1.1.216/24","10.1.1.217/24","10.1.1.218/24","10.1.1.219/24","10.1.1.220/24"]
		gw4_list = ["10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1"]
		net6_list = ["2001:10:1:1::211/64","2001:10:1:1::212/64","2001:10:1:1::213/64","2001:10:1:1::214/64","2001:10:1:1::215/64","2001:10:1:1::216/64","2001:10:1:1::217/64","2001:10:1:1::218/64"]
		gw6_list = ["2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1"]
		vlan_list = [4088,4088,4088,4088,4088,4088,4088,4088]
		device_list = tb.ixia.device_list_active

		print(f"~~~~~~~~~~~~~~~~ device_list = {device_list}")

		portList_v4_v6 = []
		for p,m,n4,g4,n6,g6 in zip(tb.ixia.port_active_list,mac_list,net4_list,gw4_list,net6_list,gw6_list):
			module,port = p.split("/")
			portList_v4_v6.append([ixChassisIpList[0], int(module),int(port),m,n4,g4,n6,g6,1])


		print(portList_v4_v6)
		for ixia_port,dev,vlan in zip(portList_v4_v6,device_list,vlan_list):
			if "FG2K" not in dev:
				ixia_port.append(vlan)
			else:
				ixia_port.append("vlan_null")

		print(portList_v4_v6)

		myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6,different_vlan=True)
		for topo in myixia.topologies:
			topo.add_dhcp_client()

		for topo,dev in zip(myixia.topologies,device_list):
			topo.connected_device = dev
		
		myixia.start_protocol(wait=200)

		
		for sw in switches:
			if len(sw.ixia_ports) >= 1:
				sw.show_command("show switch vlan")
				sw.show_command("show switch acl ingress")
				for port in sw.ixia_ports:
					sw.show_command(f"show switch interface {port}")

		for i in range(0,len(tb.ixia.port_active_list)-1):
			for j in range(i+1,len(tb.ixia.port_active_list)):
				if "FG2K" in myixia.topologies[i].connected_device or "FG2K" in myixia.topologies[j].connected_device:
					myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=1)
					myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=1)

		myixia.start_traffic()
		myixia.collect_stats()
		myixia.check_traffic()
		myixia.stop_traffic()

	if testcase == 15 or test_all:
		testcase = 15
		description = "Same segment can communicate with each other"

		mac_list = ["00:11:01:01:01:01","00:12:02:01:01:01","00:13:03:01:01:01","00:14:04:01:01:01","00:15:05:01:01:01","00:16:06:01:01:01","00:17:07:01:01:01","00:18:08:01:01:01"]
		net4_list = ["10.1.1.211/24","10.1.1.212/24","10.1.1.213/24","10.1.1.214/24","10.1.1.215/24","10.1.1.216/24","10.1.1.217/24","10.1.1.218/24","10.1.1.219/24","10.1.1.220/24"]
		gw4_list = ["10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1"]
		net6_list = ["2001:10:1:1::211/64","2001:10:1:1::212/64","2001:10:1:1::213/64","2001:10:1:1::214/64","2001:10:1:1::215/64","2001:10:1:1::216/64","2001:10:1:1::217/64","2001:10:1:1::218/64"]
		gw6_list = ["2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1"]

		portList_v4_v6 = []
		for p,m,n4,g4,n6,g6 in zip(tb.ixia.port_active_list,mac_list,net4_list,gw4_list,net6_list,gw6_list):
			module,port = p.split("/")
			portList_v4_v6.append([ixChassisIpList[0], int(module),int(port),m,n4,g4,n6,g6,10])

		print(portList_v4_v6)

		myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)
		for topo in myixia.topologies:
			topo.add_dhcp_client()

		
		myixia.start_protocol(wait=200)

		
		for i in range(0,len(tb.ixia.port_active_list)-1):
			for j in range(i+1,len(tb.ixia.port_active_list)):
				myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=1)
				myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=1)

		myixia.start_traffic()
		myixia.collect_stats()
		myixia.check_traffic()
		myixia.stop_traffic()




	 