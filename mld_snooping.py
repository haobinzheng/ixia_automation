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
	file = 'tbinfo_mld.xml'
	tb = parse_tbinfo_untangle(file)
	testtopo_file = 'threeSw7Trafgens3Links.xml'
	parse_testtopo_untangle(testtopo_file,tb)
	tb.show_tbinfo()

	switches = []
	for d in tb.devices:
		switch = FortiSwitch_XML(d)
		switches.append(switch)
	for c in tb.connections:
		c.update_devices_obj(switches)

	for c in tb.connections:
		c.shut_unused_ports()

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
	igmp_ports = ["source","querier","host","host","host","host","host","host"]
	for topo, role in zip(myixia.topologies,igmp_ports):
		topo.igmp_role = role
	for topo in myixia.topologies:
		topo.add_ipv6()
		topo.add_ipv4()
		if topo.igmp_role == "host":
			topo.add_igmp_host_v4(start_addr="239.1.1.1",num=10)
			topo.add_mld_host(start_addr="ff3e::1:1:1",num=10)
		elif topo.igmp_role == "querier":
			topo.add_igmp_querier_v4()
			topo.add_mld_querier()

	myixia.start_protocol(wait=100)

	myixia.create_mcast_traffic_v4(src_topo=myixia.topologies[0].topology, start_group="239.1.1.1",traffic_name="t0_239_1_1_1",num=10,tracking_name="Tracking_1")
	myixia.create_mcast_traffic_v6(src_topo=myixia.topologies[0].topology, start_group="ff3e::1:1:1",traffic_name="t0_ff3e_1_1_1",num=10,tracking_name="Tracking_2")
	myixia.start_traffic()
	myixia.collect_stats()
	myixia.check_traffic()

##################################################################################################################################################
##################################################################################################################################################
