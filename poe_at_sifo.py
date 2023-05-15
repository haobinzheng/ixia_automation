import wexpect
from time import sleep
from protocols_class import *
from device_config import *
from jinja2 import Template
from jinja2 import Environment, FileSystemLoader
import jinja2.ext
import pprint
import threading
import signal
import logging
from threading import Thread
from time import sleep
import multiprocessing
from ixia_restpy_lib_v2 import *
from apc import *

TROUBLE_SHOOTING = False 
REBOOT = False
INIT_REBOOT = False
SW_LOGIN = True

def jinja_zip(*args):
	return zip(*args)

logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":

	def negative_smbus():
		pshell_dict[test.sifo_ip].tcl_send_simple_cmd(test.tcl_global)
		for tcl in test.tcl_procedure_list:
			if tcl.execute == False:
				continue
			for tcl_command in tcl.tcl_command_list:  
				pshell = pshell_dict[tcl_command.sifo_ip] 
				pshell.tcl_send_commands_direct(tcl_command.commands,tcl_command.name,wait=False)

			# pshell.tcl_execute(tcl,expect=False)
			poe_inline_dict = {}
			timer = 60*5 #15 minutes	
			start_time = time.time()
			while True:
				if time.time() - start_time >  timer:
					break
				sleep(10)
				#sw.print_show_command("get switch poe inline")
				output = collect_show_cmd(sw.console,"get switch poe inline")
				sw.exec_command("execute log filter start-line 1")
				sw.exec_command("execute log filter view-lines 100")
				output = collect_show_cmd(sw.console,"execute log display")

	def poe_max_power(mode = "auto"):
		dut_4pair_port_list_scale = ['port3','port4','port5','port6','port7','port8','port9', 'port10', 'port11','port12','port13','port14','port15','port16','port17','port18','port19','port20','port21','port22','port23','port24']
		for port in dut_4pair_port_list_scale:
			sw.exec_command(f"execute poe-reset {port}")
		sleep(10)

		for tcl in test.tcl_procedure_list:
			try:
				if tcl.execute == False:
					continue
				for tcl_command in tcl.tcl_command_list:  
					pshell = pshell_dict[tcl_command.sifo_ip] 
					pshell.tcl_send_commands_direct(tcl_command.commands,tcl_command.name,wait=False)
			except Exception as e:
				pass

		if mode == "interactive":
			while True:
				output = collect_show_cmd(sw.console,"get switch poe inline")
				keyin = input("Do you want to continue to show switch poe inline(Y/N)?:")
				if keyin.upper() == "Y":
					continue
				elif keyin.upper() == "N":
					return
				else:
					continue
		else:
			timer = 60*5 #15 minutes	
			start_time = time.time()
			while True:
				if time.time() - start_time >  timer:
					break
				sleep(10)
				output = collect_show_cmd(sw.console,"get switch poe inline")


	def bg_thread_traffic(exit_event):
		logging.info("Starting background traffic thread to monitor traffic forwarding during POE power provisioning")
		apiServerIp = tb.ixia.ixnetwork_server_ip
		ixChassisIpList = [tb.ixia.chassis_ip]
		TEST_VLAN_NAME = "vlan2"
		mac_list = ["00:11:01:01:01:01","00:12:01:01:01:01","00:13:01:01:01:01","00:14:01:01:01:01","00:15:01:01:01:01","00:16:01:01:01:01","00:17:01:01:01:01","00:18:01:01:01:01"]
		net4_list = ["10.1.1.211/24","10.1.1.212/24","10.1.1.213/24","10.1.1.214/24","10.1.1.215/24","10.1.1.216/24","10.1.1.217/24","10.1.1.218/24","10.1.1.219/24","10.1.1.220/24"]
		gw4_list = ["10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1"]
		net6_list = ["2001:10:1:1::211/64","2001:10:1:1::212/64","2001:10:1:1::213/64","2001:10:1:1::214/64","2001:10:1:1::215/64","2001:10:1:1::216/64","2001:10:1:1::217/64","2001:10:1:1::218/64"]
		gw6_list = ["2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1"]

		portList_v4_v6 = []
		for p,m,n4,g4,n6,g6 in zip(tb.ixia.port_active_list,mac_list,net4_list,gw4_list,net6_list,gw6_list):
			module,port = p.split("/")
			portList_v4_v6.append([ixChassisIpList[0], int(module),int(port),m,n4,g4,n6,g6,1])

		vlan=TEST_VLAN_NAME		 
		vlan_id=re.match(r'vlan([0-9]+)',vlan).group(1)
		cmds = f"""
		config system interface
		delete {vlan}
		end
		config system interface
		edit {vlan}
			set ip {gw4_list[0]} 255.255.255.0
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

		logging.info(portList_v4_v6)
		myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)
		for topo in myixia.topologies:
			topo.add_ipv4(gateway="fixed",ip_incremental="0.0.0.1")
			topo.add_ipv6(gateway="fixed")
			
		myixia.start_protocol(wait=20)
		 
		for i in range(0,1):
			for j in range(1,2):
				myixia.create_traffic(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v4",tracking_name=f"Tracking_{i+1}_{j+1}_v4",rate=5)
				myixia.create_traffic(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v4",tracking_name=f"Tracking_{j+1}_{i+1}_v4",rate=5)
				myixia.create_traffic_v6(src_topo=myixia.topologies[i].topology, dst_topo=myixia.topologies[j].topology,traffic_name=f"t{i+1}_to_t{j+1}_v6",tracking_name=f"Tracking_{i+1}_{j+1}_v6",rate=5)
				myixia.create_traffic_v6(src_topo=myixia.topologies[j].topology, dst_topo=myixia.topologies[i].topology,traffic_name=f"t{j+1}_to_t{i+1}_v6",tracking_name=f"Tracking_{j+1}_{i+1}_v6",rate=5)

		while not exit_event.is_set():
			myixia.start_traffic()
			sleep(5)
			myixia.stop_traffic()
			sleep(10)
			myixia.collect_stats()
			myixia.check_traffic()
		logging.info("Background thread received exit signal. Exiting...")

	def load_traffic():
		apiServerIp = tb.ixia.ixnetwork_server_ip
		ixChassisIpList = [tb.ixia.chassis_ip]
		TEST_VLAN_NAME = "vlan2"
		mac_list = ["00:11:01:01:01:01","00:12:01:01:01:01","00:13:01:01:01:01","00:14:01:01:01:01","00:15:01:01:01:01","00:16:01:01:01:01","00:17:01:01:01:01","00:18:01:01:01:01"]
		net4_list = ["10.1.1.211/24","10.1.1.212/24","10.1.1.213/24","10.1.1.214/24","10.1.1.215/24","10.1.1.216/24","10.1.1.217/24","10.1.1.218/24","10.1.1.219/24","10.1.1.220/24"]
		gw4_list = ["10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1","10.1.1.1"]
		net6_list = ["2001:10:1:1::211/64","2001:10:1:1::212/64","2001:10:1:1::213/64","2001:10:1:1::214/64","2001:10:1:1::215/64","2001:10:1:1::216/64","2001:10:1:1::217/64","2001:10:1:1::218/64"]
		gw6_list = ["2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1","2001:10:1:1::1"]

		portList_v4_v6 = []
		for p,m,n4,g4,n6,g6 in zip(tb.ixia.port_active_list,mac_list,net4_list,gw4_list,net6_list,gw6_list):
			module,port = p.split("/")
			portList_v4_v6.append([ixChassisIpList[0], int(module),int(port),m,n4,g4,n6,g6,1])

		vlan=TEST_VLAN_NAME		 
		vlan_id=re.match(r'vlan([0-9]+)',vlan).group(1)
		cmds = f"""
		config system interface
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

		print(portList_v4_v6)
		myixia = IXIA(apiServerIp,ixChassisIpList,portList_v4_v6)
		for topo in myixia.topologies:
			topo.add_ipv4(gateway="fixed",ip_incremental="0.0.0.1")
			topo.add_ipv6(gateway="fixed")
			
		myixia.start_protocol(wait=20)
		 
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

		pshell.tcl_psa_connect_testcase(test)
		pshell.tcl_send_simple_cmd(test.tcl_global)
		for tcl in test.tcl_procedure_list:
			if tcl.execute == False:
				continue
			pshell.tcl_execute(tcl,expect=False)
			poe_inline_dict = {}
			timer = 60*15 #15 minutes	
			start_time = time.time()
			while True:
				if time.time() - start_time >  timer:
					ErrorNotify(f"Failed After {timer} seconds:  test case {test.case_name} |  TCL procedure {tcl.proc_name} | POE Class {tcl.poe_class}: Not to deliever power to all switch ports {test.dut_port_list}")
					if TROUBLE_SHOOTING == True:
						exit(0)
					else:
						break
				sleep(10)
				#sw.print_show_command("get switch poe inline")
				output = collect_show_cmd(sw.console,"get switch poe inline")
				for line in output:
					#skip line with N/A such as Power Fault situation
					if "N/A" in line:
						continue
					for p in test.dut_port_list:
						#if p in line and "Delivering Power" in line and str(tcl.poe_class) in line :
						if p in line:
							if "Delivering Power" in line and str(tcl.poe_class) in line:
								items = line.split()
								dprint(items)
								portname = items[0]
								status = items[1]
								state = f"{items[2]} {items[3]}"
								max_power = items[4]
								power_comsumption = items[5]
								priority = items[6]
								poe_class = items[7]
								#Only port delivering power will be taken a record
								if portname not in poe_inline_dict:
									poe_inline_dict[portname] = {}
							else:
								items = line.split()
								dprint(items)
								portname = items[0]
								status = items[1]
								state = items[2]
								max_power = items[3]
								power_comsumption = items[4]
								priority = items[5]
								poe_class = items[6]
							if portname in poe_inline_dict:
								poe_inline_dict[portname]["status"] =status
								poe_inline_dict[portname]["state"] = state
								poe_inline_dict[portname]["max_power"] = max_power
								poe_inline_dict[portname]["power_comsumption"] = power_comsumption
								poe_inline_dict[portname]["priority"] = priority
								poe_inline_dict[portname]["poe_class"] = poe_class
								try:
									print(float(poe_inline_dict[portname]["max_power"]),float(tcl.max_power),poe_inline_dict[portname]["state"],poe_inline_dict[portname]["poe_class"])
									if float(poe_inline_dict[portname]["max_power"]) != float(tcl.max_power) \
									or poe_inline_dict[portname]["state"] != "Delivering Power" \
									or poe_inline_dict[portname]["poe_class"] != str(tcl.poe_class):
										poe_inline_dict[portname]["powered"] = False
									else:
										poe_inline_dict[portname]["powered"] = True
								except Exception as e:
									pass
										 
				print_dict(poe_inline_dict)
				ports = poe_inline_dict.keys()
				result = True
				if set(ports) != set(test.dut_port_list):
					result = False
					myixia.start_traffic()
					sleep(5)
					myixia.stop_traffic()
					sleep(10)
					myixia.collect_stats()
					myixia.check_traffic()
					continue
				for p,p_status in poe_inline_dict.items():
					if p_status["powered"] == False:
						print(f'{p} poe checking result = {p_status["powered"]}')
						result = False
						break
				if result == True:
					tprint(f"PASSED: test case {test.case_name} | TCL procedure {tcl.proc_name} | POE Class {tcl.poe_class}")
					console_timer(10,msg="wait for 10 sec after one TCL procedure has been successfuly executed")
					break
		

	def pdu_cycle_sifos():
		for tester in setup.yaml_obj.Tester_list:
			tprint(f"Power cycling Sifos Chassis {tester.pdu_ip}: {tester.pdu_line}")
			a = apc()
			Status = {}
			Status = a.set_reboot(tester.pdu_ip, str(tester.pdu_line))
			print(Status)
			try:
				pshell_dict[tester.mgmt_ip].tcl_psa_connect(tester.mgmt_ip)
				pshell_dict[tester.mgmt_ip].current_psa_reboot = True
			except Exception:
				print("This is the initial reboot, no Sifo TCL Power Shell is connected yet, No need to worry about re-launch TCL shell")
		sleep(120)
		 
	def show_lldp_trace():
		pshell.tcl_psa_connect_testcase(test)
		pshell.tcl_send_cmd_expect_prompt(test.tcl_global)
		for tcl in test.tcl_procedure_list:
			if tcl.execute == False:
				continue
			pshell.tcl_execute(tcl)

	def signal_handler(sig, frame):
		print("Signal received. Sending exit signal to background thread...")
		exit_event.set()
		raise KeyboardInterrupt

	def scan_get_poe_inline_traffic():
		global exit_event
		exit_event = threading.Event()

		# create a background thread
		bg_thread = threading.Thread(target=bg_thread_traffic, args=(exit_event,))
		bg_thread.start()
		# register a signal handler for SIGINT (Ctrl-C) and SIGTERM (kill)
		signal.signal(signal.SIGINT, signal_handler)
		signal.signal(signal.SIGTERM, signal_handler)

		
		# for tester in setup.yaml_obj.Tester_list:
		# 	pshell_dict[tester.mgmt_ip].tcl_psa_connect_testcase(test)
		pshell_dict[test.sifo_ip].tcl_send_simple_cmd(test.tcl_global)
		for tcl in test.tcl_procedure_list:
			try:
				if tcl.execute == False:
					continue
				for tcl_command in tcl.tcl_command_list:  
					pshell = pshell_dict[tcl_command.sifo_ip] 
					pshell.tcl_send_commands_direct(tcl_command.commands,tcl_command.name,wait=False)

				# pshell.tcl_execute(tcl,expect=False)
				poe_inline_dict = {}
				timer = 60*15 #15 minutes	
				start_time = time.time()
				while True:
					if time.time() - start_time >  timer:
						ErrorNotify(f"Failed After {timer} seconds:  test case {test.case_name} |  TCL procedure {tcl.proc_name} | POE Class {tcl.poe_class}: Not to deliever power to all switch ports {test.dut_port_list}")
						if TROUBLE_SHOOTING == True:
							exit(0)
						else:
							break
					sleep(10)
					#sw.print_show_command("get switch poe inline")
					output = collect_show_cmd(sw.console,"get switch poe inline")
					for line in output:
						#skip line with N/A such as Power Fault situation
						if "N/A" in line:
							continue
						for p in test.dut_port_list:
							#if p in line and "Delivering Power" in line and str(tcl.poe_class) in line :
							if p in line:
								if "Delivering Power" in line and str(tcl.poe_class) in line:
									items = line.split()
									dprint(items)
									portname = items[0]
									status = items[1]
									state = f"{items[2]} {items[3]}"
									max_power = items[4]
									power_comsumption = items[5]
									priority = items[6]
									poe_class = items[7]
									#Only port delivering power will be taken a record
									if portname not in poe_inline_dict:
										poe_inline_dict[portname] = {}
								else:
									items = line.split()
									dprint(items)
									portname = items[0]
									status = items[1]
									state = items[2]
									max_power = items[3]
									power_comsumption = items[4]
									priority = items[5]
									poe_class = items[6]
								if portname in poe_inline_dict:
									poe_inline_dict[portname]["status"] =status
									poe_inline_dict[portname]["state"] = state
									poe_inline_dict[portname]["max_power"] = max_power
									poe_inline_dict[portname]["power_comsumption"] = power_comsumption
									poe_inline_dict[portname]["priority"] = priority
									poe_inline_dict[portname]["poe_class"] = poe_class
									try:
										print(float(poe_inline_dict[portname]["max_power"]),float(tcl.max_power),poe_inline_dict[portname]["state"],poe_inline_dict[portname]["poe_class"])
										if float(poe_inline_dict[portname]["max_power"]) != float(tcl.max_power) \
										or poe_inline_dict[portname]["state"] != "Delivering Power" \
										or poe_inline_dict[portname]["poe_class"] != str(tcl.poe_class):
											poe_inline_dict[portname]["powered"] = False
										else:
											poe_inline_dict[portname]["powered"] = True
									except Exception as e:
										pass
											 
					print_dict(poe_inline_dict)
					ports = poe_inline_dict.keys()
					result = True
					if set(ports) != set(test.dut_port_list):
						result = False
						continue
					for p,p_status in poe_inline_dict.items():
						if p_status["powered"] == False:
							print(f'{p} poe checking result = {p_status["powered"]}')
							result = False
							break
					if result == True:
						tprint(f"PASSED: test case {test.case_name} | TCL procedure {tcl.proc_name} | POE Class {tcl.poe_class}")
						console_timer(10,msg="wait for 10 sec after one TCL procedure has been successfuly executed")
						break
			except KeyboardInterrupt:
				logging.info("Exiting program due to user interrupt...")
				exit_event.set()

		exit_event.set()
		# wait for the background thread to exit
		bg_thread.join()
		print("Background thread has exited. Exiting create_thread()...")
 
	def scan_get_poe_inline():
		pshell_dict[test.sifo_ip].tcl_send_simple_cmd(test.tcl_global)
		for tcl in test.tcl_procedure_list:
			if tcl.execute == False:
				continue

			for tcl_command in tcl.tcl_command_list:  
				pshell = pshell_dict[tcl_command.sifo_ip] 
				pshell.tcl_send_commands_direct(tcl_command.commands,tcl_command.name,wait=False)

			poe_inline_dict = {}
			timer = 60*15 #15 minutes	
			start_time = time.time()
			while True:
				if time.time() - start_time >  timer:
					ErrorNotify(f"Failed After {timer} seconds:  test case {test.case_name} |  TCL procedure {tcl.proc_name} | POE Class {tcl.poe_class}: Not to deliever power to all switch ports {test.dut_port_list}")
					if TROUBLE_SHOOTING == True:
						exit(0)
					else:
						break
				sleep(10)
				#sw.print_show_command("get switch poe inline")
				output = collect_show_cmd(sw.console,"get switch poe inline")
				for line in output:
					#skip line with N/A such as Power Fault situation
					if "N/A" in line:
						continue
					for p in test.dut_port_list:
						#if p in line and "Delivering Power" in line and str(tcl.poe_class) in line :
						if p in line:
							if "Delivering Power" in line and str(tcl.poe_class) in line:
								items = line.split()
								dprint(items)
								portname = items[0]
								status = items[1]
								state = f"{items[2]} {items[3]}"
								max_power = items[4]
								power_comsumption = items[5]
								priority = items[6]
								poe_class = items[7]
								#Only port delivering power will be taken a record
								if portname not in poe_inline_dict:
									poe_inline_dict[portname] = {}
							else:
								items = line.split()
								dprint(items)
								portname = items[0]
								status = items[1]
								state = items[2]
								max_power = items[3]
								power_comsumption = items[4]
								priority = items[5]
								poe_class = items[6]
							if portname in poe_inline_dict:
								poe_inline_dict[portname]["status"] =status
								poe_inline_dict[portname]["state"] = state
								poe_inline_dict[portname]["max_power"] = max_power
								poe_inline_dict[portname]["power_comsumption"] = power_comsumption
								poe_inline_dict[portname]["priority"] = priority
								poe_inline_dict[portname]["poe_class"] = poe_class
								try:
									print(float(poe_inline_dict[portname]["max_power"]),float(tcl.max_power),poe_inline_dict[portname]["state"],poe_inline_dict[portname]["poe_class"])
									if float(poe_inline_dict[portname]["max_power"]) != float(tcl.max_power) \
									or poe_inline_dict[portname]["state"] != "Delivering Power" \
									or poe_inline_dict[portname]["poe_class"] != str(tcl.poe_class):
										poe_inline_dict[portname]["powered"] = False
									else:
										poe_inline_dict[portname]["powered"] = True
								except Exception as e:
									pass
										 
				print_dict(poe_inline_dict)
				ports = poe_inline_dict.keys()
				result = True
				if set(ports) != set(test.dut_port_list):
					result = False
					continue
				for p,p_status in poe_inline_dict.items():
					if p_status["powered"] == False:
						print(f'{p} poe checking result = {p_status["powered"]}')
						result = False
						break
				if result == True:
					tprint(f"PASSED: test case {test.case_name} | TCL procedure {tcl.proc_name} | POE Class {tcl.poe_class}")
					console_timer(10,msg="wait for 10 sec after one TCL procedure has been successfuly executed")
					break


	def scan_get_poe_inline_poe_mode():
		cmds = f"""
		config switch global
		set poe-power-mode first-come-first-served
		end
		"""
		sw.config_cmds_fast(cmds)
		scan_get_poe_inline()

		cmds = f"""
		config switch global
		set poe-power-mode priority
		end
		"""
		sw.config_cmds_fast(cmds)
		scan_get_poe_inline()

	def scan_get_poe_inline_pdu():
		sw.dual_pdu_up_down(pdu_unit="pdu1",action="down")
		scan_get_poe_inline()

		sw.dual_pdu_up_down(pdu_unit="pdu1",action="up")
		sleep(30)
		sw.dual_pdu_up_down(pdu_unit="pdu2",action="down")
		scan_get_poe_inline()

		sw.dual_pdu_up_down(pdu_unit="pdu2",action="up")
		scan_get_poe_inline()


	sys.stdout = Logger(f'Log/poe_3at_testing_{current_date_time().replace(":","-")}.log')
	
	env = Environment(loader=FileSystemLoader('yaml_testcase'),extensions=[jinja2.ext.do])
	dprint(env.loader.list_templates())
	env.filters['jinja_zip'] = jinja_zip

	template = env.get_template('poe_testing_3at.yml.j2')
	yaml_str = template.render()
	dprint(yaml_str)
	yaml_dict = yaml.safe_load(yaml_str)
	 
	# Write the dictionary to a YAML file
	with open('yaml_testcase/poe_3at_testing.yaml', 'w') as f:
		yaml.dump(yaml_dict, f)
	#Use this newly generated yaml file to set up testing
	setup = poe_test_setup("yaml_testcase/poe_3at_testing.yaml")
	# print("======================= Pretty print ======================")
	# setup.pretty_print()

	for test in setup.yaml_obj.Test_Case_list:
		if test.execute == True:
			tprint(f"test case to be executed = {test.case_name}")
	# ###############################DONT DELETE,This is for future ##############################
	# topology = switch_poe_topology("yaml_testcase/poe_sifos_switch_connection.yaml")
	# topology.pretty_print()
	# for connection in topology.database.Switch_Sifos_Connections:
	# 	print(connection)
	###################################################################################

	file = 'tbinfo_poe_testing_3at.xml'
	tb = parse_tbinfo_untangle(file)
	testtopo_file = 'topo_poe_npi_6xx.xml'
	parse_testtopo_untangle(testtopo_file,tb)
	#tb.show_tbinfo()
	
	switches = []
	devices=[]

	if SW_LOGIN:
		for d in tb.devices:
			if d.type == "FSW" and d.active == True:
				switch = FortiSwitch_XML(d,topo_db=tb)
				switches.append(switch)
				devices.append(switch)

		for c in tb.connections:
			c.update_devices_obj(devices)

		sw = switches[0]
	
	#have to reboot first, sometimes PSA is too busy to respond
	if INIT_REBOOT:
		pdu_cycle_sifos()
		#sw.switch_reboot_login()

	tprint(f"Launching Power Shell TCL Command From GIT Bash Shell")
	pshell_dict = {}
	for tester in setup.yaml_obj.Tester_list:
		pshell_dict[tester.mgmt_ip] = power_shell_tcl(reboot=REBOOT)
		pshell_dict[tester.mgmt_ip].tcl_psa_connect(tester.mgmt_ip)
	for _ in range(1):
		for test in setup.yaml_obj.Test_Case_list:
			if test.execute == False:
				continue
			dprint(test.case_name)
			dprint(test.dut_port_list)
			dprint(test.class_list)
			dprint(test.poe_port_list)
			if type(test.python_verify_func) == list:
				for python_proc in test.python_verify_func:
					result = globals()[python_proc]()
			else:
				result = globals()[test.python_verify_func]()
			if REBOOT:
				pdu_cycle_sifos()
				# pshell.tcl_psa_reconnect_current()
	for tester in setup.yaml_obj.Tester_list:
		pshell_dict[tester.mgmt_ip].tcl_close_shell()



