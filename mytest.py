import re
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

 
from ixia_ngfp_lib import *
from utils import *
from settings import *
from test_process import * 
from common_lib import *

def dut_process_cpu(ip,dut_name,filename,proc_name,event):
	
	counter = 0
	dut_proc_highest = {}
	
	dut = reliable_telnet(ip,sig=event)
	 
	dut_proc_highest[dut_name] = {}
	dut_proc_highest[dut_name]['cpu'] = 0.0
	dut_proc_highest[dut_name]['line'] = ''


	counter = 0
	tprint("================== Start running dut_cpu_memory thread to measure CPU utils =================")
	dut_ctrld = {}
	login_counter = 0
	while not event.is_set():
		#result = loop_command_output(dut,cmd)
		size = get_mac_table_size(dut)
		cmd = "diagnose sys top"
		try:
			result = loop_command_output(dut,cmd)
		except (BrokenPipeError,EOFError,UnicodeDecodeError) as e:
			login_counter += 1
			debug(f"Having problem telnet to {dut_name}")
			# if login_counter == 3:
			# 	exit()
			dut = reliable_telnet(ip,sig=event)
			continue
		tprint("==============dut_cpu_memory thread: CPU utilization at {}=======".format(dut_name))
		print_cmd_output(result,dut_name,cmd)
		top = parse_sys_top(result)
		debug(result)
		if top[0]:
			tprint("!!!!!!!!!!!!!!!!! The following processes' CPU utilization is high!!!!!!!!!!")
			print_cmd_output(top[1],dut_name,cmd)
		cpu_dict = top[2]
		debug(cpu_dict)
		if proc_name in cpu_dict:
			proc_cpu = cpu_dict[proc_name]['cpu']
			proc_line = cpu_dict[proc_name]['line']
			headline = cpu_dict[proc_name]['headline']
			if proc_cpu >= dut_proc_highest[dut_name]['cpu']:
				dut_proc_highest[dut_name]['cpu'] = proc_cpu
				dut_proc_highest[dut_name]['line'] = proc_line
			tprint(f"{dut_name}: Current MAC table size  = {size}")
			tprint(f"{dut_name}:current sample of {proc_name} cpu utilization = {proc_cpu}")
			tprint(f"{dut_name}:highest sample for {proc_name} cpu utilization = {dut_proc_highest[dut_name]['cpu']}")

			with open(filename,'a+') as f:
				f.write(time_str(f"{dut_name}: Current MAC table size  = {size}\n"))
				f.write(time_str(f'{dut_name}: {headline}\n'))
				f.write(time_str(f"{dut_name}:current sample of {proc_name} cpu utilization = {proc_cpu}\n"))
				f.write(time_str(f"{dut_name}: {proc_line}\n")) 
				f.write(time_str(f"{dut_name}:highest sample for {proc_name} cpu utilization = \
				                   {dut_proc_highest[dut_name]['cpu']}\n"))
					 
				f.write(time_str(f"{dut_name}: {dut_proc_highest[dut_name]['line']}\n"))
				f.write("-------------------------------------------------------------------------------------\n")
		#sleep(2)
		counter += 1
		# if counter == 10:
		# 	break
	debug("Exit event is set by parent process, exiting")
	tprint("===============================Exiting dut_proc_cpu process ===================")

def misc():
	ONBOARD_MSG = """=======================================================================================
	Please make sure to double check the following things before running the test:
		1)Make sure sensitive micro-usb console cables are connected well. 
		2)Make sure IXIA port connection is good. A bad connection will fail the script.
		3)Remember to move the 3rd and 4th IXIA port from 548D setup to 448D or visa versa
	========================================================================================""" 
	print(ONBOARD_MSG)
	dut_name = "dut1"
	headline = "this is a test"
	s = f'{dut_name}: {headline}\n'
	filename = "ttttt.log"
	with open(filename,'a+') as f:
		f.write(time_str(f'{dut_name}: {headline}\n'))

	line = "12U, 41S, 47I; 987T, 748F"
	if "U" in line and "S" in line and "I" in line:
		print("found it")
		items = re.split(';\\s+|,\\s+|\n',line)
		print(items)
		user = items[0]
		user = (re.match('([0-9]+)(U)',user)).group(1)
		system = items[1]
		system = (re.match('([0-9]+)(S)',system)).group(1)
		idle = items[2]
		idle = re.match('([0-9]+)(I)',idle).group(1)
		print(user,system,idle)

# def parse_config_trunk(result):
# 	trunk_dict_list = []
# 	for item in result:
# 		for line in item:
# 			if 'edit' in line:
# 				print(line)
# 				#regex = r'\s?edit\s+\"([0-9a-z0-9A-Z0-9.]+)\"'
# 				regex = r'\s?edit\s+\"(.+)\"'
# 				match = re.match(regex, line)
# 				trunk = match.group(1)
# 				print(trunk)
# 				trunk_dict = {}
# 				trunk_dict['name'] = trunk
				
# 			elif 'member' in line:
# 				print(f"parse_config_trunk: parsing set member line... line ={line}")
# 				regex = r'.?\s?set members\s+(.+)'
# 				match = re.match(regex, line)
# 				port_list = match.group(1)
# 				print(f'port_list = {port_list}')
# 				regex = r'\"(port[0-9]+)\"'
# 				ports = re.findall(regex,port_list)
# 				print(ports)
# 				trunk_dict['mem'] = ports
# 				trunk_dict_list.append(trunk_dict)
# 	debug(trunk_dict_list)
# 	return trunk_dict_list



# def parse_config_output(result):

# 	# result = ['show switch trunk\r', 'config switch trunk', '    
# 	#edit "8DF4K17000028-0"', '        set mode lacp-active', '        set auto-isl 1', '        
# 	#set mclag-icl enable', '            set members "port47" "port48"', '    next', '    edit "G39E6T018900038"', '   
# 	#     set mode lacp-active', '        set auto-isl 1', '        set fortilink 1', '        set mclag enable', '         
# 	#   set members "port49"', '    next', '    edit "sw1-trunk"', '        set mode lacp-active', '       
# 	# set mclag enable', '            set members "port13"', '    next', '   
# 	# edit "G39E6T018900070"', '      
# 	#  set mode lacp-active', '        set auto-isl 1', '        set fortilink 1', '        set mclag enable',
# 	# '--More-- \r         \r            set members "port50"',
# 	# '    next', '    edit "core1"', '        set mode lacp-active', '        set auto-isl 1', '       
# 	# set mclag enable', '            set members "port1" "port2" "port3" "port4"', 
# 	#'    next', 'end', '', 'S548DF4K17000014 #']
# 	config = []
# 	for line in result:
# 		debug(f'old line = {line}')
# 		if "More" in line:
# 			line = line.replace("--More--",'')
# 			line = line.replace("\r",'')
# 			line = line.strip()
# 		debug(f'new line = {line}')
# 		if 'show' in line or 'config' in line:
# 			continue

# 		if 'end' in line:
# 			debug (config)
# 			return config
# 		if 'edit' in line:
# 			block = []
# 			block.append(line.strip())
# 			continue
# 		elif 'next' in line:
# 			config.append(block)
# 		else:
# 			block.append(line.strip())
# 	debug(config)
# 	return config






# def dut_switch_trunk(dut):

# 	result = collect_show_cmd(dut,'show switch trunk')
# 	config = parse_config_output(result)
# 	trunk_dict_list = parse_config_trunk(config)
# 	print(trunk_dict_list)

if __name__ == "__main__":

	dut1_dir = {}
	dut2_dir = {}
	dut3_dir = {}
	dut4_dir = {}

	dut1_com = "10.105.50.3"
	dut1_location = "Rack23-29"
	dut1_port = 2057
	dut1_name = "dut1-548d"
	dut1_cfg = "dut1_548d.cfg"

	dut2_com = "10.105.50.3"
	dut2_port = 2056
	dut2_location = "Rack23-28"
	dut2_name = "dut2-548d"
	dut2_cfg = "dut2_548d.cfg"

	dut3_com = "10.105.50.1"
	dut3_port = 2075
	dut3_name = "dut3-548d"
	dut3_location = "Rack20-23"
	dut3_cfg = "dut3_548d.cfg"

	dut4_com = "10.105.50.1"
	dut4_port = 2078
	dut4_location = "Rack20-22"
	dut4_name = "dut4-548d"
	dut4_cfg = "dut4_548d.cfg"



	dut1 = get_switch_telnet_connection_new(dut1_com,dut1_port)
	dut1_dir['name'] = dut1_name
	dut1_dir['location'] = dut1_location
	dut1_dir['telnet'] = dut1
	dut1_dir['cfg'] = dut1_cfg

	switch_show_cmd(dut1,"get system status")
	print("factory reset...")
	switch_interactive_exec(dut1,"execute factoryresetfull","Do you want to continue? (y/n)")
	print("after reset sleep 200s")
	sleep(200)
	print("after sleep, relogin, should change password ")

	dut1 = get_switch_telnet_connection_new(dut1_com,dut1_port)

	switch_show_cmd(dut1,"get system status")
	exit()

	dut2 = get_switch_telnet_connection(dut2_com,dut2_port)
	dut2_dir['name'] = dut2_name
	dut2_dir['location'] = dut2_location
	dut2_dir['telnet'] = dut2
	dut2_dir['cfg'] = dut2_cfg

	dut3 = get_switch_telnet_connection(dut3_com,dut3_port)
	dut3_dir['name'] = dut3_name
	dut3_dir['location'] = dut3_location
	dut3_dir['telnet'] = dut3
	dut3_dir['cfg'] = dut3_cfg

	dut4 = get_switch_telnet_connection(dut4_com,dut4_port)
	dut4_dir['name'] = dut4_name
	dut4_dir['location'] = dut4_location
	dut4_dir['telnet'] = dut4
	dut4_dir['cfg'] = dut4_cfg

	dut_list = [dut1,dut2,dut3,dut4]
	dut_dir_list = [dut1_dir,dut2_dir,dut3_dir,dut4_dir]

	
	trunk_dict_list = dut_switch_trunk(dut1)
	trunk_dict_list = dut_switch_trunk(dut2)
	trunk_dict_list = dut_switch_trunk(dut3)
	trunk_dict_list = dut_switch_trunk(dut4)
	exit()

	file = "test_multipro.log"
	# ip = "10.105.50.64"
	# name = "dut1"
	dut1_telnet = "10.105.50.59"
	dut2_telnet = "10.105.50.60"
	dut3_telnet = "10.105.50.62"
	dut4_telnet = "10.105.50.63"
	ip_list = [dut2_telnet] 
	#ip_list = [dut1_telnet,dut2_telnet,dut3_telnet,dut4_telnet]
	#ip_list = ["10.105.50.64","10.105.50.65","10.105.50.66","10.105.50.67"]
	name_list = ["dut1","dut2","dut3","dut4"]
	event  = multiprocessing.Event()
	proc_name = 'fortilinkd'
	proc_list = [multiprocessing.Process(name=f'cpu_{name}',target = dut_process_cpu,args = \
		(ip,name,file, proc_name,event)) for (ip,name) in zip(ip_list,name_list) ]
	for proc in proc_list:	
		proc.start()
		 
	sleep(360000)
	event.set()
	debug("!!!!!!!!!!!!!!!!!!! event is set for child processes to exit")
	for proc in proc_list:
		proc.join()
	
	
	tprint("Finished!")
	# threads_list.append(thread3)
	#dut_cpu_memory_proc(ip,name,file)