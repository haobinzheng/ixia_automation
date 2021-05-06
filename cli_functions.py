import sys
import time
import logging
import traceback
import paramiko
import time
from time import sleep
import re
import os
from datetime import datetime
import xlsxwriter
from excel import *
#from ixia_ngfp_lib import *
import settings
from console_util  import  *
import pexpect
from threading import Thread
import subprocess
import spur
import multiprocessing
from collections import OrderedDict
from copy import deepcopy

from utils import *
from settings import *

def switch_config_flapguard_port(**kwargs):
	if 'disable' in kwargs:
		dut = kwargs['dut']
		port = kwargs['port']
		disable = kwargs['disable']
		if disable.upper() == "Y":
			config_flap = f"""
			config switch physical-port
			edit {port}
			set flapguard disable
			end
			"""
			config_cmds_lines(dut, config_flap)
			return 
	dut = kwargs['dut']
	port = kwargs['port']
	flap_duration = kwargs['duration']
	flap_timeout = kwargs['timeout']
	flap_rate = kwargs['rate']

	config_flap = f"""
		config switch physical-port
		edit {port}
		set flapguard enable
		set flap-timeout {flap_timeout}
		set flap-duration {flap_duration}
		set flap-rate {flap_rate}
		end
	"""
	config_cmds_lines(dut, config_flap)


def fgt_switch_controller_GetConnectionStatus():
	con_status_sample = """
	FortiGate-3960E # execute switch-controller get-conn-status 
	Managed-devices in current vdom root:
	 
	STACK-NAME: FortiSwitch-Stack-fortilink
	SWITCH-ID         VERSION           STATUS         FLAG   ADDRESS              JOIN-TIME            NAME            
	S448DP3X17000253  v6.2.0 (184)      Authorized/Up   -   169.254.1.7     Fri Oct 11 22:24:53 2019    -               
	S448DPTF18000161  v6.2.0 (184)      Authorized/Up   -   169.254.1.6     Fri Oct 11 22:24:45 2019    -               
	S548DF4K16000653  v6.2.0 (192)      Authorized/Up   E   169.254.1.5     Fri Oct 11 22:24:40 2019    -               
	S548DF4K17000014  v6.2.0 (192)      Authorized/Up   C   169.254.1.3     Fri Oct 11 22:04:48 2019    -               
	S548DF4K17000028  v6.2.0 (192)      Authorized/Up   -   169.254.1.4     Fri Oct 11 22:23:58 2019    -               
	S548DN4K17000133  v6.2.0 (192)      Authorized/Up   -   169.254.1.2     Fri Oct 11 22:24:30 2019    -               
	 
		 Flags: C=config sync, U=upgrading, S=staged, D=delayed reboot pending, E=configuration sync error
		 Managed-Switches: 6 (UP: 6 DOWN: 0)
	 
	"""

	dict_list = [] 
	
	lines = con_status_sample.split('\n')
	for line in lines:
		line = line.strip()
		if "SWITCH-ID" in line and "VERSION" in line:
			line_dict = OrderedDict()
			items = re.split('\\s+',line)
			print(items)
			if items:
				for i in items:
					line_dict[i] = '' 
			else:
				return False
		elif "169.254" in line:
			print(line)
			d = deepcopy(line_dict)
			matched_list = []
			chassis_regex = r"[S|s][0-9A-Za-z]+"
			version_regex = r"v6\.[0-9\.]+ \(.+\)"
			status_regex = r"[A-Za-z]+/[A-Za-z]+"
			flag_regex =r"\s+[CUSDE-]\s+"
			ip_regex = r"[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+"
			time_regex = r"\s+[0-9A-Za-z\s]+\s+[0-9][0-9]:[0-9][0-9]:[0-9][0-9]\s+20[0-9][0-9]"
			name_regex = r"\s+-\s+"
			regex_list = [chassis_regex,version_regex,status_regex,flag_regex,ip_regex,time_regex,name_regex]
			for regex in regex_list:
				matched= re.search(regex,line)
				if matched:
					matched_list.append(matched.group().strip())
				else:
					ErrorNotify(f"Error parsing : {line} for {regex}")
					continue

			for (k,v) in zip(d.keys(),matched_list):
				d[k] = v
			dict_list.append(d)
			 
	print(dict_list)
	return dict_list


def fgt_ssh_managed_chassis(fgt1):
	output = collect_show_cmd(fgt1,"execute dhcp lease-list fortilink",t=5)
	dhcp_dict_list = fgt_dhcp_lease(output)
	result = True
	for dhcp in dhcp_dict_list:
		ip = dhcp["IP"]
		chassis_id = dhcp["Hostname"]
		if fgt_ssh_chassis(fgt1,ip,chassis_id) == True:
			tprint(f"ssh to {chassis_id} at {ip} is successful")
		else:
			tprint(f"ssh to {chassis_id} at {ip} failed")
			result = False
	return result

def fgt_dhcp_lease(output):
	output = """

	FortiGate-3960E # execute dhcp lease-list fortilink
	fortilink
	  IP			MAC-Address		Hostname		VCI			Expiry
	  169.254.1.5		90:6c:ac:62:14:3f	S548DF4K16000653		FortiSwitch-548D-FPOE		Tue Oct 22 13:14:33 2019
	  169.254.1.2		70:4c:a5:79:22:5b	S548DN4K17000133		FortiSwitch-548D		Tue Oct 22 13:14:33 2019
	  169.254.1.4		70:4c:a5:82:99:83	S548DF4K17000028		FortiSwitch-548D-FPOE		Tue Oct 22 17:26:17 2019
	  169.254.1.3		70:4c:a5:82:96:73	S548DF4K17000014		FortiSwitch-548D-FPOE		Tue Oct 22 17:26:31 2019
	  169.254.1.7		70:4c:a5:65:93:65	S448DP3X17000253		FortiSwitch-448D-POE		Tue Oct 22 13:14:34 2019

	"""
	 
	dhcp_dict_list = [] 
	
	lines = output.split('\n')
	for line in lines:
		line = line.strip()
		if "IP" in line and "MAC-Address" in line:
			dhcp_lease_dict = OrderedDict()
			items = re.split('\\s+',line)
			#print(items)
			if items:
				for i in items:
					dhcp_lease_dict[i] = '' 
			else:
				return False
		elif "169.254" in line:
			d = deepcopy(dhcp_lease_dict)
			items_2 = re.split('\\s+',line)
			if items_2:
				for (k,v) in zip(d.keys(),items_2):
					d[k] = v
				dhcp_dict_list.append(d)
			else:
				return False
	dprint(dhcp_dict_list)
	return dhcp_dict_list


if __name__ == "__main__":
	fgt_switch_controller_GetConnectionStatus()
	dhcp_list = fgt_dhcp_lease()
	for dhcp in dhcp_list:
		print(dhcp["IP"], dhcp["MAC-Address"],dhcp["VCI"])
	

