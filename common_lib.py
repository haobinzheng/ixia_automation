import telnetlib
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
from ixia_ngfp_lib import *
import settings
from console_util  import  *
import pexpect
from threading import Thread
import subprocess
import spur
import multiprocessing

from ixia_ngfp_lib import *
from utils import *
from settings import *
 

def check_route_exist(*args,**kwargs):
	cmd = kwargs['cmd']
	dut = kwargs['dut']
	networks = kwargs['networks']
	result = collect_show_cmd(dut,cmd)

	for net in networks:
		for line in result:
			if net in line:
				return True

	return False

def collect_edit_items(dut,cmd):
 	switch_exec_cmd(dut,cmd)
 	result = collect_edit_question_cmd(dut,"edit ?")
 	switch_exec_cmd(dut,"end")
 	result.pop(0)
 	result.pop(0)
 	new_result = []
 	for item in result:
 		if item == '':
 			continue
 		elif "route-map" in item or "access-list" in item:
 			continue
 		else:
 			new_result.append(item)
 	return new_result


def switches_clean_up(switches):
    for switch in switches:
        switch.factory_reset_nologin()

    console_timer(150,msg = "After factory reset, wait for 150 seconds")

    for switch in switches:
        switch.relogin_after_factory()
        switch.init_config()

def check_bgp_test_result(testcase,description,switches,**kwargs):
    if "test1" in kwargs:
        result1 = kwargs["test1"]
    else:
        result1 = True
    result = True
    for switch in switches:
        #switch.router_bgp.get_neighbors_summary()
        if not switch.router_bgp.check_neighbor_status():
            result = False
    if result1 and result:
        final_result = "Passed"
    else:
        final_result = "Failed"

    tprint(f"====================== Test case #{testcase}:{description} has been {final_result} ==========\n\n")   

def basic_config_aspath_list(dut):
	config = """
	config router aspath-list
    edit "as-101"
            config rule
                edit 1
                    set action permit
                    set regexp "101"
                next
            end
    next
    edit "as-102"
            config rule
                edit 1
                    set action permit
                    set regexp "102"
                next
            end
    next
    edit "as-103"
            config rule
                edit 1
                    set action permit
                    set regexp "103"
                next
            end
    next

    edit "as-104"
            config rule
                edit 1
                    set action permit
                    set regexp "104"
                next
            end
    next


    edit "as-105"
            config rule
                edit 1
                    set action permit
                    set regexp "105"
                next
            end
    next

    edit "as-106"
            config rule
                edit 1
                    set action permit
                    set regexp "106"
                next
            end
    next

     edit "as-65001"
            config rule
                edit 1
                    set action permit
                    set regexp "^65001 65006$
                next
            end
    next
end

	"""


def basic_config_access_list(dut):

	config = """
	config router access-list
    edit "network-10-10"
            config rule
                edit 1
                    set prefix 10.10.0.0 255.255.0.0
                    set exact-match disable
                next
            end
    next
    edit "network-10-20"
            config rule
                edit 1
                    set prefix 10.20.0.0 255.255.0.0
                    set exact-match disable
                next
            end
    next
    edit "network-10-30"
            config rule
                edit 1
                    set prefix 10.30.0.0 255.255.0.0
                    set exact-match disable
                next
            end
    next
    edit "network-10-40"
            config rule
                edit 1
                    set prefix 10.40.0.0 255.255.0.0
                    set exact-match disable
                next
            end
    next
    edit "network-10-50"
            config rule
                edit 1
                    set prefix 10.50.0.0 255.255.0.0
                    set exact-match disable
                next
            end
    next
    edit "network-10-60"
            config rule
                edit 1
                    set prefix 10.60.0.0 255.255.0.0
                    set exact-match disable
                next
            end
    next
    edit "next-hop-ixia-1"
            config rule
                edit 1
                    set prefix 10.1.1.101 255.255.255.255
                    set exact-match enable
                next
            end
    	next

    edit "next-hop-ixia-2"
            config rule
                edit 1
                    set prefix 10.1.1.102 255.255.255.255
                    set exact-match enable
                next
            end
    	next

    edit "next-hop-ixia-3"
            config rule
                edit 1
                    set prefix 10.1.1.103 255.255.255.255
                    set exact-match enable
                next
            end
    	next

    edit "next-hop-ixia-4"
            config rule
                edit 1
                    set prefix 10.1.1.104 255.255.255.255
                    set exact-match enable
                next
            end
    	next

    edit "next-hop-ixia-5"
            config rule
                edit 1
                    set prefix 10.1.1.105 255.255.255.255
                    set exact-match enable
                next
            end
    	next

    edit "next-hop-ixia-6"
            config rule
                edit 1
                    set prefix 10.1.1.106 255.255.255.255
                    set exact-match enable
                next
            end
    	next

    edit "next-hop-sw1"
            config rule
                edit 1
                    set prefix 1.1.1.1 255.255.255.255
                    set exact-match enable
                next
            end
    	next
	end

	

	edit "next-hop-sw2"
            config rule
                edit 1
                    set prefix 2.2.2.2 255.255.255.255
                    set exact-match enable
                next
            end
    	next
	end

	edit "next-hop-sw3"
            config rule
                edit 1
                    set prefix 3.3.3.3 255.255.255.255
                    set exact-match enable
                next
            end
    	next
	end

	edit "next-hop-sw4"
            config rule
                edit 1
                    set prefix 4.4.4.4 255.255.255.255
                    set exact-match enable
                next
            end
    	next
	end

	edit "next-hop-sw5"
            config rule
                edit 1
                    set prefix 5.5.5.5 255.255.255.255
                    set exact-match enable
                next
            end
    	next
	end

	edit "next-hop-sw6"
            config rule
                edit 1
                    set prefix 6.6.6.6 255.255.255.255
                    set exact-match enable
                next
            end
    	next
	end

	"""
	config_cmds_lines(dut,config)

def basic_config_route_map(dut):
	config = """
	config router route-map
    edit "match-network-10-10"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-ip-address "network-10-10"
                next
            end
    next
    edit "match-network-10-20"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-ip-address "network-10-20"
                next
            end
    next
    edit "match-network-10-30"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-ip-address "network-10-30"
                next
            end
    next
    edit "match-network-10-40"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-ip-address "network-10-40"
                next
            end
    next
    edit "match-network-10-50"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-ip-address "network-10-50"
                next
            end
    next
    edit "match-network-10-60"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-ip-address "network-10-60"
                next
            end
    next
 
	edit "match-next-hop-sw1"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-ip-nexthop "next-hop-sw1"
                next
            end
    next

    

    edit "match-next-hop-sw2"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-ip-nexthop "next-hop-sw2"
                next
            end
    next

    edit "match-next-hop-sw3"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-ip-nexthop "next-hop-sw3"
                next
            end
    next

    edit "match-next-hop-sw4"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-ip-nexthop "next-hop-sw4"
                next
            end
    next

    edit "match-next-hop-sw5"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-ip-nexthop "next-hop-sw5"
                next
            end
    next

	edit "match-next-hop-sw6"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-ip-nexthop "next-hop-sw6"
                next
            end
    next

	edit "permit-next-hop-sw1"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-nexthop "next-hop-sw1"
                next
            end
    next

    

    edit "permit-next-hop-sw2"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-nexthop "next-hop-sw2"
                next
            end
    next

    edit "permit-next-hop-sw3"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-nexthop "next-hop-sw3"
                next
            end
    next

    edit "permit-next-hop-sw4"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-nexthop "next-hop-sw4"
                next
            end
    next

    edit "permit-next-hop-sw5"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-nexthop "next-hop-sw5"
                next
            end
    next

	edit "permit-next-hop-sw6"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-nexthop "next-hop-sw6"
                next
            end
    next


    edit "match-next-hop-ixia-1"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-ip-nexthop "next-hop-ixia-1"
                next
            end
    next
    edit "match-next-hop-ixia-2"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-ip-nexthop "next-hop-ixia-2"
                next
            end
    next
    edit "match-next-hop-ixia-3"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-ip-nexthop "next-hop-ixia-3"
                next
            end
    next
    edit "match-next-hop-ixia-4"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-ip-nexthop "next-hop-ixia-4"
                next
            end
    next
    edit "match-next-hop-ixia-5"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-ip-nexthop "next-hop-ixia-5"
                next
            end
    next
    edit "match-next-hop-ixia-6"
        set protocol bgp
            config rule
                edit 1
                    set action deny
                    set match-ip-nexthop "next-hop-ixia-6"
                next
            end
    next

    edit "match-next-hop-sw1"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-ip-nexthop "next-hop-sw1"
                next
            end
    next

    edit "match-next-hop-sw2"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-ip-nexthop "next-hop-sw2"
                next
            end
    next

    edit "match-next-hop-sw3"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-ip-nexthop "next-hop-sw3"
                next
            end
    next

    edit "match-next-hop-sw4"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-ip-nexthop "next-hop-sw4"
                next
            end
    next

    edit "match-next-hop-sw5"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-ip-nexthop "next-hop-sw5"
                next
            end
    next

    edit "match-next-hop-sw6"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-ip-nexthop "next-hop-sw6"
                next
            end
    next


    edit "set-weight-10"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-address "network-10-10"
                    set set-weight 91111
                next
            end
    next

	edit "set-weight-20"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-address "network-10-20"
                    set set-weight 92222
                next
            end
    next

    edit "set-weight-30"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-address "network-10-30"
                    set set-weight 93333
                next
            end
    next
    edit "set-weight-40"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-address "network-10-40"
                    set set-weight 94444
                next
            end
    next

    edit "set-weight-50"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-address "network-10-50"
                    set set-weight 95555
                next
            end
    next

    edit "set-weight-60"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-address "network-10-60"
                    set set-weight 96666
                next
            end
    next
    edit "origin-igp"
        set protocol bgp
            config rule
                edit 1
                    set action deny
                    set set-origin igp
                next
            end
    next
    edit "change-origin-igp-2-egp"
        set protocol bgp
            config rule
                edit 1
                    set set match-origin igp
                    set action permit
                    set set-origin egp
                next
            end
    next

    edit "change-origin-igp-2-incomplete"
        set protocol bgp
            config rule
                edit 1
                    set set match-origin igp
                    set action permit
                    set set-origin incomplete
                next
            end
    next

	edit "change-origin-igp-2-None"
        set protocol bgp
            config rule
                edit 1
                    set set match-origin igp
                    set action permit
                    set set-origin none
                next
            end
    next


    edit "as-path-101"
        set protocol bgp
            config rule
                edit 1
                    set action deny
                        set set-aspath "101"                         
                next
            end
    next
    edit "as-path-102"
        set protocol bgp
            config rule
                edit 1
                    set action deny
                        set set-aspath "102"                         
                next
            end
    next
    edit "as-path-103"
        set protocol bgp
            config rule
                edit 1
                    set action deny
                        set set-aspath "103"                         
                next
            end
    next
    edit "as-path-104"
        set protocol bgp
            config rule
                edit 1
                    set action deny
                        set set-aspath "104"                         
                next
            end
    next
    edit "as-path-105"
        set protocol bgp
            config rule
                edit 1
                    set action deny
                        set set-aspath "105"                         
                next
            end
    next
    edit "as-path-106"
        set protocol bgp
            config rule
                edit 1
                    set action deny
                        set set-aspath "106"                         
                next
            end
    next
    edit "set-local-pref-1111"
        set protocol bgp
            config rule
                edit 1
                	set match-ip-address "network-10-10"
                    set set-local-preference 1111
                next
            end
    next

    edit "set-local-pref-2222"
        set protocol bgp
            config rule
                edit 1
                	set match-ip-address "network-10-20"
                    set set-local-preference 2222
                next
            end
    next

    edit "set-local-pref-3333"
        set protocol bgp
            config rule
                edit 1
					set match-ip-address "network-10-30"
                    set set-local-preference 3333
                next
            end
    next

	edit "set-local-pref-4444"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-address "network-10-40"
                    set set-local-preference 4444
                next
            end
    next
    edit "set-local-pref-5555"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-address "network-10-50"
                    set set-local-preference 5555
                next
            end
    next

    edit "set-local-pref-6666"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-address "network-10-60"
                    set set-local-preference 6666
                next
            end
    next

    edit "as-path-101"
        set protocol bgp
            config rule
                edit 1                    
                set match-as-path "as-101"
                set set-aspath "10001"                         
                next
            end
    next
    edit "as-path-102"
        set protocol bgp
            config rule
                edit 1                    
                set match-as-path "as-102"
                set set-aspath "10002"                         
                next
            end
    next

    edit "as-path-103"
        set protocol bgp
            config rule
                edit 1                    
                set match-as-path "as-103"
                set set-aspath "10003"                         
                next
            end
    next

    edit "as-path-104"
        set protocol bgp
            config rule
                edit 1                    
                set match-as-path "as-104"
                set set-aspath "10004"                         
                next
            end
    next

    edit "as-path-105"
        set protocol bgp
            config rule
                edit 1                    
                set match-as-path "as-105"
                set set-aspath "10005"                         
                next
            end
    next

    edit "as-path-106"
        set protocol bgp
            config rule
                edit 1                    
                set match-as-path "as-106"
                set set-aspath "10006"                         
                next
            end
    next

    edit "match-med-1000"
        set protocol bgp
            config rule
                edit 1
                   	set action deny
                    set match-metric 1000
                next
            end
    next

    edit "match-med-10000"
        set protocol bgp
            config rule
                edit 1
                   	set action deny
                    set match-metric 10000
                next
            end
    next

    edit "permit-med-10000"
        set protocol bgp
            config rule
                edit 1
                    set match-metric 10000
                next
            end
    next

    edit "match-med-2000"
        set protocol bgp
            config rule
                edit 1
                   	set action deny
                    set match-metric 2000
                next
            end
    next

    edit "match-med-20000"
        set protocol bgp
            config rule
                edit 1
                   	set action deny
                    set match-metric 20000
                next
            end
    next

    edit "permit-med-20000"
        set protocol bgp
            config rule
                edit 1
                    set match-metric 20000
                next
            end
    next

    edit "match-med-3000"
        set protocol bgp
            config rule
                edit 1
                   	set action deny
                    set match-metric 3000
                next
            end
    next

    edit "match-med-30000"
        set protocol bgp
            config rule
                edit 1
                   	set action deny
                    set match-metric 30000
                next
            end
    next

    edit "permit-med-30000"
        set protocol bgp
            config rule
                edit 1
                    set match-metric 30000
                next
            end
    next

    edit "match-med-4000"
        set protocol bgp
            config rule
                edit 1
                   	set action deny
                    set match-metric 4000
                next
            end
    next

    edit "match-med-40000"
        set protocol bgp
            config rule
                edit 1
                   	set action deny
                    set match-metric 40000
                next
            end
    next

    edit "permit-med-40000"
        set protocol bgp
            config rule
                edit 1
                    set match-metric 40000
                next
            end
    next

    edit "match-med-5000"
        set protocol bgp
            config rule
                edit 1
                   	set action deny
                    set match-metric 5000
                next
            end
    next

    edit "match-med-50000"
        set protocol bgp
            config rule
                edit 1
                   	set action deny
                    set match-metric 50000
                next
            end
    next

    edit "permit-med-50000"
        set protocol bgp
            config rule
                edit 1
                    set match-metric 50000
                next
            end
    next

    edit "match-med-6000"
        set protocol bgp
            config rule
                edit 1
                   	set action deny
                    set match-metric 6000
                next
            end
    next

    edit "match-med-60000"
        set protocol bgp
            config rule
                edit 1
                   	set action deny
                    set match-metric 60000
                next
            end
    next
    edit "permit-med-60000"
        set protocol bgp
            config rule
                edit 1
                    set match-metric 60000
                next
            end
    next

    edit "change-med-1000"
        set protocol bgp
            config rule
                edit 1
                    set match-metric 1000
                    set set-metric 10000
                next
            end
    next

    edit "change-med-2000"
        set protocol bgp
            config rule
                edit 1
                    set match-metric 2000
                    set set-metric 20000
                next
            end
    next

    edit "change-med-3000"
        set protocol bgp
            config rule
                edit 1
                    set match-metric 2000
                    set set-metric 30000
                next
            end
    next


    edit "change-med-4000"
        set protocol bgp
            config rule
                edit 1
                    set match-metric 4000
                    set set-metric 40000
                next
            end
    next

    edit "change-med-5000"
        set protocol bgp
            config rule
                edit 1
                    set match-metric 5000
                    set set-metric 50000
                next
            end
    next

    edit "change-med-6000"
        set protocol bgp
            config rule
                edit 1
                    set match-metric 6000
                    set set-metric 60000
                next
            end
    next



	edit "permit-origin-egp"
        set protocol bgp
            config rule
                edit 1
                	set action permit
                    set match-origin egp
                 next
            end
    next

    edit "match-origin-egp"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-origin egp
                 next
            end
    next

    edit "match-origin"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-origin igp
                 next
            end
    next

    edit "change-origin"
        set protocol bgp
            config rule
                edit 1
                    set match-origin igp
                    set set-origin egp
                next
            end
    next

    edit "change-aspath-101"
        set protocol bgp
            config rule
                edit 1
                    set match-as-path "as-101"
                        set set-aspath "1001"                         
                next
            end
    next

    edit "change-aspath-102"
        set protocol bgp
            config rule
                edit 1
                    set match-as-path "as-102"
                        set set-aspath "1002"                         
                next
            end
    next

    edit "change-aspath-103"
        set protocol bgp
            config rule
                edit 1
                    set match-as-path "as-103"
                        set set-aspath "1003"                         
                next
            end
    next

    edit "change-aspath-104"
        set protocol bgp
            config rule
                edit 1
                    set match-as-path "as-104"
                        set set-aspath "1004"                         
                next
            end
    next

    edit "change-aspath-105"
        set protocol bgp
            config rule
                edit 1
                    set match-as-path "as-105"
                        set set-aspath "1005"                         
                next
            end
    next

    edit "change-aspath-106"
        set protocol bgp
            config rule
                edit 1
                    set match-as-path "as-106"
                        set set-aspath "1006"                         
                next
            end
    next

    edit "match-aspath-101"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-as-path "as-101"                         
                next
            end
    next

	edit "match-aspath-102"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-as-path "as-102"                         
                next
            end
    next

    edit "match-aspath-103"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-as-path "as-103"                         
                next
            end
    next

	edit "match-aspath-104"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-as-path "as-104"                         
                next
            end
    next

    edit "match-aspath-105"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-as-path "as-105"                         
                next
            end
    next

    edit "match-aspath-106"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-as-path "as-106"                         
                next
            end
    next

    edit "match-aspath-1001"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-as-path "as-1001"                         
                next
            end
    next

	edit "match-aspath-1002"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-as-path "as-1002"                         
                next
            end
    next

    edit "match-aspath-1003"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-as-path "as-1003"                         
                next
            end
    next

    edit "match-aspath-1004"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-as-path "as-1004"                         
                next
            end
    next

    edit "match-aspath-1005"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-as-path "as-1005"                         
                next
            end
    next

    edit "match-aspath-1006"
        set protocol bgp
            config rule
                edit 1
                	set action deny
                    set match-as-path "as-1006"                         
                next
            end
    next

    edit "permit-aspath-1001"
        set protocol bgp
            config rule
                edit 1
                    set match-as-path "as-1001"                         
                next
            end
    next


    edit "permit-aspath-1002"
        set protocol bgp
            config rule
                edit 1
                    set match-as-path "as-1002"                         
                next
            end
    next

    edit "permit-aspath-1003"
        set protocol bgp
            config rule
                edit 1
                    set match-as-path "as-1003"                         
                next
            end
    next

    edit "permit-aspath-1004"
        set protocol bgp
            config rule
                edit 1
                    set match-as-path "as-1004"                         
                next
            end
    next

    edit "permit-aspath-1005"
        set protocol bgp
            config rule
                edit 1
                    set match-as-path "as-1005"                         
                next
            end
    next

    edit "permit-aspath-1006"
        set protocol bgp
            config rule
                edit 1
                    set match-as-path "as-1006"                         
                next
            end
    next

    edit "change-next-hop-1"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-nexthop "next-hop-ixia-1"
                    set set-ip-nexthop 1.1.1.1
                next
            end
    next

    edit "change-next-hop-2"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-nexthop "next-hop-ixia-2"
                    set set-ip-nexthop 2.2.2.2
                next
            end
    next

    edit "change-next-hop-3"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-nexthop "next-hop-ixia-3"
                    set set-ip-nexthop 3.3.3.3
                next
            end
    next

    edit "change-next-hop-4"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-nexthop "next-hop-ixia-4"
                    set set-ip-nexthop 4.4.4.4
                next
            end
    next

    edit "change-next-hop-5"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-nexthop "next-hop-ixia-5"
                    set set-ip-nexthop 5.5.5.5
                next
            end
    next

    edit "change-next-hop-6"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-nexthop "next-hop-ixia-6"
                    set set-ip-nexthop 6.6.6.6
                next
            end
    next

    edit "change-weight-1"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-address "network-10-10"
                    set set-weight 1
                next
            end
    next

    edit "change-weight-2"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-address "network-10-20"
                    set set-weight 2
                next
            end
    next

    edit "change-weight-3"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-address "network-10-30"
                    set set-weight 3
                next
            end
    next

    edit "change-weight-4"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-address "network-10-40"
                    set set-weight 4
                next
            end
    next

    edit "change-weight-5"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-address "network-10-50"
                    set set-weight 5
                next
            end
    next
    edit "change-weight-6"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-address "network-10-60"
                    set set-weight 6
                next
            end
    next
    edit "change-atomic-1"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-address "network-10-10"
                    set set-atomic-aggregate enable
                next
            end
    next

    edit "change-atomic-2"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-address "network-10-20"
                    set set-atomic-aggregate enable
                next
            end
    next


    edit "change-atomic-3"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-address "network-10-30"
                    set set-atomic-aggregate enable
                next
            end
    next

    edit "change-atomic-4"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-address "network-10-40"
                    set set-atomic-aggregate enable
                next
            end
    next

    edit "change-atomic-5"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-address "network-10-50"
                    set set-atomic-aggregate enable
                next
            end
    next

    edit "change-atomic-6"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-address "network-10-60"
                    set set-atomic-aggregate enable
                next
            end
    next

    edit "change-originator-1"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-address "network-10-10"
                    set set-originator-id 172.168.1.1
                next
            end
    next

    edit "change-originator-2"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-address "network-10-20"
                    set set-originator-id 172.168.1.2
                next
            end
    next

    edit "change-originator-3"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-address "network-10-30"
                    set set-originator-id 172.168.1.3
                next
            end
    next

    edit "change-originator-4"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-address "network-10-40"
                    set set-originator-id 172.168.1.4
                next
            end
    next

    edit "change-originator-5"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-address "network-10-50"
                    set set-originator-id 172.168.1.5
                next
            end
    next

    edit "change-originator-6"
        set protocol bgp
            config rule
                edit 1
                    set match-ip-address "network-10-60"
                    set set-originator-id 172.168.1.6
                next
            end
    next

	end
	"""
	config_cmds_lines(dut,config)

def show_flapguard_cmds(dut4,flap_port):
	output = switch_show_cmd(dut4, f"show switch global")
	output = switch_show_cmd(dut4, f"show switch physical-port {flap_port}")
	press_any_key()
	output = switch_show_cmd(dut4, "diag flapguard status")
	press_any_key()
	output = switch_show_cmd(dut4,"diag switch physical-ports summary")
	press_any_key()

def get_system_status(dut):
	pass

def dut_background_proc(ip,dut_name,cmd_list,event):
	tprint("================== Start running dut_background_proc to generate background activites =================")
	dut = reliable_telnet(ip,sig=event) 
	while not event.is_set():
		try:
			for cmd in cmd_list:
				switch_run_cmd(dut,cmd,t=2)
		except (BrokenPipeError,EOFError,UnicodeDecodeError) as e:
			debug(f"Having problem telnet to {dut_name}")
			dut = reliable_telnet(ip,sig=event)
			continue

def dut_commands_proc(ip,dut_name,cmds_list,show_cmds_list,filename, event):
	dut_dir = {}
	tprint("================== Start running dut_commands_proc to generate exercise commands activites =================")
	dut = reliable_telnet(ip,sig=event) 
	dut_dir['telnet'] = dut
	dut_dir['name'] = dut_name
	while not event.is_set():
		try:
			for block in cmds_list:
				for show_cmd in show_cmds_list:
					result = collect_show_cmd(dut,show_cmd,t=10)
					print_collect_show(result)
					print_file(result,filename,dut_name = dut_name)
				config_block_cmds(dut_dir, block)
				sleep(10)
		except (BrokenPipeError,EOFError,UnicodeDecodeError) as e:
			debug(f"Having problem telnet to {dut_name}")
			dut = reliable_telnet(ip,sig=event)
			continue

def ixia_monitor_traffic(monitor_file,stop):
	while not stop():
		ixia_clear_traffic_stats()
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats_3rd(flow_stat_list)
		print_file("Logging traffic stats #{}".format(counter),monitor_file)
		print_flow_stats_3rd_log(flow_stat_list,monitor_file)

def dut_process_cpu(ip,dut_name,filename,proc_name,event,**kwargs):
	
	if "cmds" in kwargs:
		cmd_list = kwargs['cmds']
	else:
		cmd_list = []
	debug(f"dut_process_cpu: cmd_list = {cmd_list}")
	counter = 0
	dut_proc_highest = {}
	
	dut = reliable_telnet(ip,sig=event)
	 
	dut_proc_highest[dut_name] = {}
	dut_proc_highest[dut_name]['cpu'] = 0.0
	dut_proc_highest[dut_name]['line'] = ''


	counter = 0
	tprint("================== Start running dut_process_cpu process to measure CPU utils =================")
	dut_ctrld = {}
	login_counter = 0
	while not event.is_set():
		#result = loop_command_output(dut,cmd)
		size = get_mac_table_size(dut)
		if size  == 0:
			continue
		try:
			for cmd in cmd_list:
				tprint(f"dut_process_cpu: executing {cmd} on {dut_name}")
				switch_run_cmd(dut,cmd,t=2)
		except (BrokenPipeError,EOFError,UnicodeDecodeError) as e:
			debug(f"Having problem telnet to {dut_name}")
			dut = reliable_telnet(ip,sig=event)
			continue
		cmd = "diagnose sys top"
		try:
			result = loop_command_output(dut,cmd)
		except (BrokenPipeError,EOFError,UnicodeDecodeError) as e:
			debug(f"Having problem telnet to {dut_name}")
			dut = reliable_telnet(ip,sig=event)
			continue
		tprint("==============dut_process_cpu process: CPU utilization at {}=======".format(dut_name))
		print_cmd_output(result,dut_name,cmd)
		top = parse_sys_top(result)
		debug(result)
		if top[0]:
			tprint("!!!!!!!!!!!!!!!!! The following processes' CPU utilization is high!!!!!!!!!!")
			print_cmd_output(top[1],dut_name,cmd)
			print_file(top[1], filename, dut_name=dut_name)
		cpu_dict = top[2]

		debug(cpu_dict)
		#every process data structure has the same record for the CPU idle number, and if need to be shown only once. 
		#showed is a valuable to record whether it has been shown before
		showed = False
		if proc_name in cpu_dict:
			proc_cpu = cpu_dict[proc_name]['cpu']
			proc_line = cpu_dict[proc_name]['line']
			headline = cpu_dict[proc_name]['headline']
			busy_dict = cpu_dict[proc_name]['headline_dict'] 
			idle = busy_dict['idle'] 

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
				f.write(time_str(f"{dut_name}:highest sample for {proc_name} cpu utilization ={dut_proc_highest[dut_name]['cpu']}\n"))
					 
				f.write(time_str(f"{dut_name}: {dut_proc_highest[dut_name]['line']}\n"))
				f.write("-------------------------------------------------------------------------------------\n")
			if idle < 5 and not showed:
				switch_show_cmd_log(dut,"diagnose switch mclag peer-consistency-check",filename)
				switch_show_cmd_log(dut,"diagnose stp vlan list ",filename)
				print_file(result,filename,dut_name = dut_name)
				showed = True

		#sleep(2)
		counter += 1
		# if counter == 10:
		# 	break
	debug("Exit event is set by parent process, exiting")
	tprint("===============================Exiting dut_proc_cpu process ===================")

def sw_display_log(dut,*args, **kwargs):
	if 'lines' in kwargs:
		display_lines = kwargs['lines']
	else:
		display_lines = 1000
	switch_exec_cmd(dut,"execute log filter start-line 1")
	switch_exec_cmd(dut,f"execute log filter view-lines {display_lines}")
	result = collect_show_cmd(dut,'execute log display',t=3)
	print_collect_show(result)

def sw_delete_log(dut,*args,**kwargs):
	switch_interactive_exec(dut,'execute log delete-all',"Do you want to continue? (y/n)")
	

def dut_process_log(ip,dut_name,filename,intf_name,event_config,event_done,**kwargs):
	
	if "cmds" in kwargs:
		cmd_list = kwargs['cmds']
	else:
		cmd_list = []
	debug(f"dut_process_log: cmd_list = {cmd_list}")
	doubleline = "======================================================================================================\n"
	singleline = "------------------------------------------------------------------------------------------------------\n"
	cmd1 = 'execute log delete-all'
	cmd = 'execute log display'
	dut = reliable_telnet(ip,sig=event_done)
	 
	tprint("================== Start running dut_process_log process to monitor syslog =================\n")
	clear_print = False
	switch_exec_cmd(dut,"execute log filter start-line 1")
	switch_exec_cmd(dut,"execute log filter view-lines 100")
	
	while not event_done.is_set():
		if clear_print == False:
			tprint("dut_process_log: waiting for signal from main process to start monitor syslog \n")
			clear_print = True
		clear_log = False


		while event_config.is_set():
			if clear_log == False:
				switch_interactive_exec(dut,cmd1,"Do you want to continue? (y/n)")
				append_file_collect_show(filename,doubleline)
				clear_log = True
			result = collect_show_cmd(dut,cmd,t=3)
			append_file_collect_show(filename,result)
			# print_collect_show(result)
	 
	debug("Exit event is set by parent process, exiting")
	tprint("===============================Exiting dut_process_log process ===================")

def config_qinq_port(*args,**kwargs):
	dut = kwargs['dut']
	c_vlan = kwargs['c_vlan']
	s_vlan = kwargs['s_vlan']
	port = kwargs['port']

	config = f"""
	config switch interface 
	edit {port}
		set vlan-tpid default 
		config qnq
			set status enable
			set vlan-mapping-miss-drop enable 
			set add-inner {c_vlan}
			set edge-type customer
			set stp-qnq-admin enable
			set priority follow-c-tag 
			set remove-inner enable
		config vlan-mapping
			edit 1
			set description 'vlan-mapping-1' 
			set match-c-vlan {c_vlan}
			set new-s-vlan {s_vlan}
		next end
		end next
		end
	"""
	config_block_cmds_new(dut,config)

def get_switch_port_summary(dut):
	result = collect_show_cmd(dut,"diag switch physical-ports summary")
	port_list = []
	for line in result:
		if "Portname" in line:
			heads = re.split('\\s+',line)
		elif "port" in line and "8100" in line:
			port_line_dict = {}
			items = re.split('\\s+',line)
			for k,v in zip(heads,items):
				port_line_dict[k] = v

			port_list.append(port_line_dict)
		else:
			pass
	return port_list

def get_router_info_ospf_neighbor_template(dut):
	cmd = "get router info ospf neighbor all"
	head1 = "Neighbor"
	head2 = "State"
	line1 = "2-Way"
	line2 = "Full"
	return get_table_with_heading(dut,cmd,head1,head2,line1,line2)

def get_table_with_heading(dut,cmd,head_id1,head_id2,*args):
	result = collect_show_cmd(dut,cmd)
	table_list = []
	for line in result:
		if head_id1 in line and head_id2 in line:
			heads = re.split('\\s+',line)
			continue
		for item in args:
			if item in line:
				port_line_dict = {}
				items = re.split('\\s+',line)
				for k,v in zip(heads,items):
					port_line_dict[k] = v

				table_list.append(port_line_dict)
				continue
	return table_list

def get_router_bgp_summary(dut):
# IPv4 Unicast Summary:
# BGP router identifier 1.1.1.1, local AS number 65000 vrf-id 0
# BGP table version 0
# RIB entries 0, using 0 bytes of memory
# Peers 4, using 83 KiB of memory

# Neighbor        V         AS MsgRcvd MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd
# 2.2.2.2         4      65000      70      76        0    0    0 00:08:17            0
# 3.3.3.3         4      65000      71      77        0    0    0 00:08:17            0
# 4.4.4.4         4      65000      71      83        0    0    0 00:08:17            0
# 5.5.5.5         4      65000      66      75        0    0    0 00:08:17            0

# Total number of neighbors 4

	result = collect_show_cmd(dut,"get router info bgp summary")
	items_list = []
	headline_found = False
	for line in result:
		line = line.strip()
		if "Neighbor" in line and "AS" in line and "MsgRcvd" in line:
			heads = re.split('\\s+',line)
			headline_found = True
		elif headline_found == True and re.match(r'([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)',line):
			port_line_dict = {}
			items = re.split('\\s+',line)
			for k,v in zip(heads,items):
				port_line_dict[k] = v
			items_list.append(port_line_dict)
		else:
			pass
	#print(items_list)
	return items_list

def get_router_info_ospf_neighbor(dut):
	result = collect_show_cmd(dut,"get router info ospf neighbor all")
	neighbor_list = []
	for line in result:
		if "2-Way" in line or "Full" in line or "DR" in line or "Backup" in line or "DROther" in line:
			items = re.split('\\s+',line)
			neighbor_dict = {}
			neighbor_dict["id"] = items[0]
			neighbor_dict["pri"] = items[1]
			neighbor_dict["state"] = items[2]
			neighbor_dict["dead"] = items[3]
			neighbor_dict['address']= items[4]
			neighbor_dict["interface"]= items[5]
			neighbor_list.append(neighbor_dict) 
	return neighbor_list

def get_switch_show_bgp(dut):
	result = collect_show_cmd(dut,"show router bgp")
	neighbor_list = []
	found_neighbor = False
	for line in result:
		if "config neighbor" in line:
			found_neighbor = True
			continue
		elif found_neighbor and "edit" in line:
			line = line.replace('\"','')
			regex = r'edit\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)'
			matched = re.search(regex,line)
			if matched:
				neighbor = matched.group(1)
				neighbor_list.append(neighbor)
		else:
			pass
 
	return neighbor_list

def get_bgp_network_config(dut):
	result = collect_show_cmd(dut,"show router bgp")
	item_list = []
	found_item = False
	for line in result:
		if "config network" in line:
			found_item = True
			continue
		elif found_item and "edit" in line:
			regex = r'edit\s+([0-9]+)'
			matched = re.search(regex,line)
			if matched:
				item = matched.group(1)
				item_list.append(item)
		else:
			pass
 
	return item_list

def get_switch_lldp_summary(dut):
	result = collect_show_cmd(dut,"get switch lldp neighbors-summary")
	lldp_list = []
	for line in result:
		if "Portname" in line and "TTL" in line:
			heads = re.split('\\s+',line)
		elif "Up" in line or "Down" in line:
			port_line_dict = {}
			items = re.split('\\s+',line)
			for k,v in zip(heads,items):
				port_line_dict[k] = v

			lldp_list.append(port_line_dict)
		else:
			pass
	return lldp_list


def delete_mirror_ports(*args,**kwargs):
	dut = kwargs['dut']
	config = f"""
	config switch mirror
		delete 1
	end
	"""
	config_block_cmds_new(dut,config)


def config_mirror_ports(*args,**kwargs):
	dut = kwargs['dut']
	dst_port = kwargs['dst_port']
	src_port = kwargs['src_port']
	config = f"""
	config switch mirror
		edit 1
			set status active
			set dst {dst_port}
			set switching-packet enable
			set src-ingress {src_port}
			set src-egress {src_port}
		next
	end
	"""
	config_block_cmds_new(dut,config)

def dut_process_flap_port(dut2,dut3,dut4):
	while True:
		switch_shut_port(dut2,"port47")
		switch_shut_port(dut2,"port48")
		switch_shut_port(dut3,"port1")
		switch_shut_port(dut3,"port2")
		switch_shut_port(dut3,"port43")
		switch_shut_port(dut4,"port3")
		switch_shut_port(dut4,"port4")
		sleep(2)
		switch_unshut_port(dut2,"port47")
		switch_unshut_port(dut2,"port48")
		switch_unshut_port(dut3,"port1")
		switch_unshut_port(dut3,"port2")
		switch_unshut_port(dut4,"port3")
		switch_unshut_port(dut4,"port4")
		switch_unshut_port(dut3,"port43")
		sleep(20)
		


def dut_process_interface(ip,dut_name,filename,intf_name_list,event_config,event_done,**kwargs):
	
	if "cmds" in kwargs:
		cmd_list = kwargs['cmds']
	else:
		cmd_list = []
	debug(f"dut_process_interface: cmd_list = {cmd_list}")
	
	
	dut = reliable_telnet(ip,sig=event_done)
	 
	tprint("================== Start running dut_process_interface process to monitor inerface up/down =================")
	clear_print = False
	while not event_done.is_set():
		if clear_print == False:
			tprint("dut_process_interface: waiting for signal from main process to start monitor interface up/down")
			clear_print = True
		while event_config.is_set():
			clear_print = False
			for intf_name in intf_name_list:
				cmd = f'diagnose switch physical-ports summary | grep {intf_name}'
				result = collect_show_cmd_fast(dut,cmd)
				append_file_collect_show(filename,result)
			# print_collect_show(result)
	 
	debug("Exit event is set by parent process, exiting")
	tprint("===============================Exiting dut_proc_interface process ===================")


class Test_Monitor_Process(multiprocessing.Process):
	def __init__(self, q, style):
		multiprocessing.Process.__init__(self)
		self.q = q
		self.style = style

	def run(self):
		monitor_dut()


# This section should contain the connect procedure values (device ip, port list etc) and, of course, the connect procedure		
def period_login(dut_list,lock,stop):
	tprint("Staring period_login thread at background\n")
	while not stop():
		sleep(300)
		debug("******Login thread: relogin after 300 seconds ")
		for dut in dut_list:
			relogin_if_needed(dut)
			sleep(20)
	debug("*** Login thread: Main thread is done....Existing background DUT login activities")
			

def mac_log_stress(topology_handle_dict_list, dut_list, mac_table, stop, **kwargs):
	dut1 = dut_list[0]
	dut2 = dut_list[1]
	dut3 = dut_list[2]
	dut4 = dut_list[3]

	ethernet_1_handle = topology_handle_dict_list[0]['ethernet_handle']
	ethernet_2_handle = topology_handle_dict_list[1]['ethernet_handle']
	ethernet_3_handle = topology_handle_dict_list[2]['ethernet_handle']
	ethernet_4_handle = topology_handle_dict_list[3]['ethernet_handle']

	port_1_handle = topology_handle_dict_list[0]['port_handle']
	port_2_handle = topology_handle_dict_list[1]['port_handle']
	port_3_handle = topology_handle_dict_list[2]['port_handle']
	port_4_handle = topology_handle_dict_list[3]['port_handle']

	topology_1_handle = topology_handle_dict_list[0]['topology_handle']
	topology_2_handle = topology_handle_dict_list[1]['topology_handle']
	topology_3_handle = topology_handle_dict_list[2]['topology_handle']
	topology_4_handle = topology_handle_dict_list[3]['topology_handle']

	ipv4_1_handle = topology_handle_dict_list[0]['ipv4_handle']
	ipv4_2_handle = topology_handle_dict_list[1]['ipv4_handle']
	ipv4_3_handle = topology_handle_dict_list[2]['ipv4_handle']
	ipv4_4_handle = topology_handle_dict_list[3]['ipv4_handle']


	deviceGroup_1_handle = topology_handle_dict_list[0]['deviceGroup_handle']
	deviceGroup_2_handle = topology_handle_dict_list[1]['deviceGroup_handle']
	deviceGroup_3_handle = topology_handle_dict_list[2]['deviceGroup_handle']
	deviceGroup_4_handle = topology_handle_dict_list[3]['deviceGroup_handle']
	ip3 = "100.2.0.1"
	ip4 = "100.2.10.1"
	gw3 = "100.2.10.1"
	gw4 = "100.2.0.1"

	tprint("================================ Start running  mac_log_stress thread  ====================")
	counter = 1
	 
	MAC_CLEAR_TIME = 3
	SHORT_TIMEOUT = 5
	LONG_TIMEOUT = 10

	sleep(LONG_TIMEOUT)
	if "log" in kwargs:
		log_flag = kwargs['log']
	else:
		log_flag = True
	 
	while True:
		if stop():
			tprint("Main thread is done....Existing background mac_log_stress thread")
			break
		# ip3,ip4 = ip4,ip3
		# gw3,gw4 = gw4,gw3
		#keyin = input("testing....press any key")
		 
		tprint("=========  mac_log_stress thread: manually clear MAC table entries on DUT3 and DUT4")
		 
		#tprint("===== IXIA thread: Lock Acquired")
		for i in range(10):
			tprint("::::: mac_log_stress thread: clearing mac-address on DUT1")
			switch_show_cmd(dut1,"diagnose switch mac-address delete all")
			tprint("::::: mac_log_stress thread: clearing mac-address on DUT2")
			switch_show_cmd(dut2,"diagnose switch mac-address delete all")
			tprint("::::: mac_log_stress thread: clearing mac-address on DUT3")
			switch_show_cmd(dut3,"diagnose switch mac-address delete all")
			tprint("::::: mac_log_stress thread: clearing mac-address on DUT4")
			switch_show_cmd(dut4,"diagnose switch mac-address delete all")
			tprint("::::: mac_log_stress thread: Re-learn MAC")
			ixia_stop_one_protcol(ipv4_3_handle)
			ixia_stop_one_protcol(ipv4_4_handle)
			ixia_start_one_protcol(ipv4_3_handle)
			ixia_start_one_protcol(ipv4_4_handle)
			sleep(MAC_CLEAR_TIME)
		if stop():
			tprint("Main thread is done....Exiting background mac_log_stress thread")
			break
		# ip3,ip4 = 
		#keyin = input("testing....press any key")
		with lock:
			tprint("===== mac_log_stress thread: Lock Acquired")
			ixia_destroy_topology(topology_3_handle,deviceGroup_3_handle,mac_table)
			#ixia_destroy_topology(topology_4_handle,deviceGroup_4_handle,mac_table)
		#sleep(SHORT_TIMEOUT)
		#keyin = input("testing....press any key")
		#tprint("===== mac_log_stress thread: Lock Acquired")
		tprint("=====  mac_log_stress thread: Generating MAC move events. Now port3 is having the same MAC address as port4")
		handle_dict = ixia_static_ipv4_topo(
			port=port_3_handle,
			multiplier=mac_table,
			topology_name="Topology 3",
			device_group_name = "Device Group 3",
			intf_ip=ip3, 
			gateway = gw3,
			intf_mac="00.14.01.00.00.01",
			mask="255.255.0.0"
		)
		ethernet_3_handle = handle_dict['ethernet_handle']
		port_3_handle = handle_dict['port_handle']
		topology_3_handle = handle_dict['topology_handle']
		ipv4_3_handle = handle_dict['ipv4_handle']
		deviceGroup_3_handle = handle_dict['deviceGroup_handle']
		ixia_start_one_protcol(ipv4_3_handle)
		if stop():
			tprint("Main thread is done....Existing background mac_log_stress thread")
			break
			 
		for i in range(10):
			tprint("::::: mac_log_stress thread: Clear mac-address after having MAC move")
			tprint("::::: mac_log_stress thread: clearing mac-address on DUT3")
			switch_show_cmd(dut3,"diagnose switch mac-address delete all")
			tprint("::::: mac_log_stress thread: clearing mac-address on DUT4")
			switch_show_cmd(dut4,"diagnose switch mac-address delete all")
			tprint("::::: mac_log_stress thread: Re-learn MAC")
			ixia_stop_one_protcol(ipv4_3_handle)
			ixia_stop_one_protcol(ipv4_4_handle)
			ixia_start_one_protcol(ipv4_3_handle)
			ixia_start_one_protcol(ipv4_4_handle)
			sleep(MAC_CLEAR_TIME)
		if stop():
			tprint("Main thread is done....Existing background mac_log_stress thread")
			break

		tprint("=====  mac_log_stress thread:Restore original MAC address ")
		ixia_destroy_topology(topology_3_handle,deviceGroup_3_handle,mac_table)
		ixia_destroy_topology(topology_4_handle,deviceGroup_4_handle,mac_table)
		sleep(1)
		#keyin = input("testing....press any key")
		if stop():
			tprint("Main thread is done....Existing background mac_log_stress thread")
			break
		# with lock:
		# tprint("===== mac_log_stress thread: Lock Acquired")
		tprint("=====  mac_log_stress thread:Restore original MAC address ")
		handle_dict = ixia_static_ipv4_topo(
			port=port_3_handle,
			multiplier=mac_table,
			topology_name="Topology 3",
			device_group_name = "Device Group 3",
			intf_ip=ip3, 
			gateway = gw3,
			intf_mac="00.13.01.00.00.01",
			mask="255.255.0.0"
		)
		ethernet_3_handle = handle_dict['ethernet_handle']
		port_3_handle = handle_dict['port_handle']
		topology_3_handle = handle_dict['topology_handle']
		ipv4_3_handle = handle_dict['ipv4_handle']
		deviceGroup_3_handle = handle_dict['deviceGroup_handle']

		handle_dict = ixia_static_ipv4_topo(
			port=port_4_handle,
			multiplier=mac_table,
			topology_name="Topology 4",
			device_group_name = "Device Group 4",
			intf_ip=ip4, 
			gateway = gw4,
			intf_mac="00.14.01.00.00.01",
			mask="255.255.0.0"
		)
		ethernet_4_handle = handle_dict['ethernet_handle']
		port_4_handle = handle_dict['port_handle']
		topology_4_handle = handle_dict['topology_handle']
		ipv4_4_handle = handle_dict['ipv4_handle']
		deviceGroup_4_handle = handle_dict['deviceGroup_handle']

		ixia_start_one_protcol(ipv4_3_handle)
		ixia_start_one_protcol(ipv4_4_handle)
		tprint("=====  mac_log_stress thread: finished Restore original MAC address ")
		sleep(MAC_CLEAR_TIME)
		if stop():
			tprint("Main thread is done....Existing background mac_log_stress thread")
			break
		counter += 1
		if counter == 50:
			counter = 0
			with lock:
				tprint("mac_log stress: acquired lock to relogin")
				for dut in dut_list:
					relogin_if_needed(dut)

	tprint("===============================Exiting mac_log_stress thread ===================")

def ixia_topo_swap(topology_handle_dict_list, dut_list, mac_table,stop,traffic_list, \
	ip3,ip4,gw3,gw4,mac3,mac4,**kwargs):
	dut1 = dut_list[0]
	dut2 = dut_list[1]
	dut3 = dut_list[2]
	dut4 = dut_list[3]

	ethernet_1_handle = topology_handle_dict_list[0]['ethernet_handle']
	ethernet_2_handle = topology_handle_dict_list[1]['ethernet_handle']
	ethernet_3_handle = topology_handle_dict_list[2]['ethernet_handle']
	ethernet_4_handle = topology_handle_dict_list[3]['ethernet_handle']

	port_1_handle = topology_handle_dict_list[0]['port_handle']
	port_2_handle = topology_handle_dict_list[1]['port_handle']
	port_3_handle = topology_handle_dict_list[2]['port_handle']
	port_4_handle = topology_handle_dict_list[3]['port_handle']

	topology_1_handle = topology_handle_dict_list[0]['topology_handle']
	topology_2_handle = topology_handle_dict_list[1]['topology_handle']
	topology_3_handle = topology_handle_dict_list[2]['topology_handle']
	topology_4_handle = topology_handle_dict_list[3]['topology_handle']

	ipv4_1_handle = topology_handle_dict_list[0]['ipv4_handle']
	ipv4_2_handle = topology_handle_dict_list[1]['ipv4_handle']
	ipv4_3_handle = topology_handle_dict_list[2]['ipv4_handle']
	ipv4_4_handle = topology_handle_dict_list[3]['ipv4_handle']


	deviceGroup_1_handle = topology_handle_dict_list[0]['deviceGroup_handle']
	deviceGroup_2_handle = topology_handle_dict_list[1]['deviceGroup_handle']
	deviceGroup_3_handle = topology_handle_dict_list[2]['deviceGroup_handle']
	deviceGroup_4_handle = topology_handle_dict_list[3]['deviceGroup_handle']
	# ip3 = "100.2.0.1"
	# ip4 = "100.2.10.1"
	# gw3 = "100.2.10.1"
	# gw4 = "100.2.0.1"
	# mac3 ="00.13.01.00.00.01"
	# mac4 = "00.14.01.00.00.01"

	tprint("================================ Start ixia_topo_swap  ====================")
	counter = 1
	sleep(60)
	 
	MAC_CLEAR_TIME = 3
	SHORT_TIMEOUT = 5
	LONG_TIMEOUT = 10

	sleep(LONG_TIMEOUT)
	if "log" in kwargs:
		log_flag = kwargs['log']
	else:
		log_flag = True
	 
	# while not stop():
	# ip3,ip4 = ip4,ip3
	# gw3,gw4 = gw4,gw3
	# mac3,mac4 = mac4,mac3
	#tprint("=========  mac_log_stress thread: manually clear MAC table entries on DUT3 and DUT4")
	# for i in range(2):
	# 	tprint("::::: mac_log_stress thread: clearing mac-address on DUT1")
	# 	switch_run_cmd(dut1,"diagnose switch mac-address delete all")
	# 	tprint("::::: mac_log_stress thread: clearing mac-address on DUT2")
	# 	switch_run_cmd(dut2,"diagnose switch mac-address delete all")
	# 	tprint("::::: mac_log_stress thread: clearing mac-address on DUT3")
	# 	switch_run_cmd(dut3,"diagnose switch mac-address delete all")
	# 	tprint("::::: mac_log_stress thread: clearing mac-address on DUT4")
	# 	switch_run_cmd(dut4,"diagnose switch mac-address delete all")
	# 	tprint("::::: mac_log_stress thread: Re-learn MAC")
		# ixia_stop_one_protcol(ipv4_3_handle)
		# ixia_stop_one_protcol(ipv4_4_handle)
		# ixia_start_one_protcol(ipv4_3_handle)
		# ixia_start_one_protcol(ipv4_4_handle)
		# sleep(MAC_CLEAR_TIME)
	
	tprint("=====  ixia_topo_swap process: stop traffic before making topo changes")
	ixia_stop_traffic()
	ixia_destroy_topology(topology_3_handle,deviceGroup_3_handle,mac_table)
	ixia_destroy_topology(topology_4_handle,deviceGroup_4_handle,mac_table)

	id_4 = traffic_list.pop(3)
	id_3 = traffic_list.pop(2)
	tprint("=====  ixia_topo_swap : remove all traffic config ")
	tprint(f"id4 = {id_4}, id3 = {id_3}")
	ixia_remove_traffic_config(stream_id=str(id_4))
	ixia_remove_traffic_config(stream_id=str(id_3))

	sleep(SHORT_TIMEOUT)
 
	tprint("=====  ixia_topo_swap process: Generating MAC move events by swapping port3 and port4")
	topology_handle_dict_list.pop(3)
	topology_handle_dict_list.pop(2)

	handle_dict = ixia_static_ipv4_topo(
		port=port_3_handle,
		multiplier=mac_table,
		topology_name="Topology 3",
		device_group_name = "Device Group 3",
		intf_ip = ip3, 
		gateway = gw3,
		intf_mac = mac3,
		mask="255.255.0.0"
	)
	topology_handle_dict_list.append(handle_dict)

	ethernet_3_handle = handle_dict['ethernet_handle']
	port_3_handle = handle_dict['port_handle']
	topology_3_handle = handle_dict['topology_handle']
	ipv4_3_handle = handle_dict['ipv4_handle']
	deviceGroup_3_handle = handle_dict['deviceGroup_handle']
	 

	handle_dict = ixia_static_ipv4_topo(
		port=port_4_handle,
		multiplier=mac_table,
		topology_name="Topology 4",
		device_group_name = "Device Group 4",
		intf_ip=ip4, 
		gateway = gw4,
		intf_mac= mac4,
		mask="255.255.0.0"
	)
	topology_handle_dict_list.append(handle_dict)
	ethernet_4_handle = handle_dict['ethernet_handle']
	port_4_handle = handle_dict['port_handle']
	topology_4_handle = handle_dict['topology_handle']
	ipv4_4_handle = handle_dict['ipv4_handle']
	deviceGroup_4_handle = handle_dict['deviceGroup_handle']

	ixia_start_one_protcol(ipv4_3_handle)
	ixia_start_one_protcol(ipv4_4_handle)
	sleep(15)


	# tprint("ixia_top_swap:Creating traffic item I....")
	# traffic_status = ixia_create_ipv4_traffic(topology_1_handle,topology_2_handle,rate=50)
	# id = traffic_status['stream_id']
	# traffic_list.append(id)
	# tprint("ixia_top_swap:Creating traffic item II....")
	# traffic_status = ixia_create_ipv4_traffic(topology_2_handle,topology_1_handle,rate=50)
	# id = traffic_status['stream_id']
	# traffic_list.append(id)
	tprint("Creating traffic item III....")
	tprint("ixia_topo_swap: Creating traffic item III....")
	traffic_status = ixia_create_ipv4_traffic(topology_3_handle,topology_4_handle,rate=50)
	id = traffic_status['stream_id']
	traffic_list.append(id)
	tprint("ixia_topo_swap: Creating traffic item IV....")
	traffic_status = ixia_create_ipv4_traffic(topology_4_handle,topology_3_handle,rate=50)
	id = traffic_status['stream_id']
	traffic_list.append(id)
	sleep(2)
	ixia_start_traffic()

		#tprint("!!!!!!!!!!!!!!!!!!! ixia_topo_swap: Error running ixia")
	tprint("=====  ixia_topo_swap : After streaming traffic III and IV for 15 sec, collet stats ")
	sleep(15)
	tprint(" ixia_topo_swap: Collect statistics after running traffic for 15 seconds, Please take a look at printed traffic stats to make sure no packet loss..")
	traffic_stats = collect_ixia_traffic_stats()
	flow_stat_list = parse_traffic_stats(traffic_stats)
	print_flow_stats_3rd(flow_stat_list)
	tprint("ixia_topo_swap: Finish showing stats after swapping")
	#sleep(120)
	tprint("===============================Exiting ixia_topo_swap background activities ===================")

 

def dut_cpu_memory_proc(dut_dir_list,event,filename):
	
	counter = 0
	dut_list = []
	dut_name_list = []
	dut_location_list = []
	dut_ctrld_highest = {}
	for d in dut_dir_list:
		dut = d['telnet']
		dut_list.append(dut)
		dut_name = d['name']
		dut_name_list.append(dut_name)
		location = d['location']
		dut_location_list.append(location)
		dut_ctrld_highest[dut_name] = {}
		dut_ctrld_highest[dut_name]['cpu'] = 0.0
		dut_ctrld_highest[dut_name]['line'] = ''

	
	counter = 0
	tprint("================== Start running dut_cpu_memory thread to measure CPU utils =================")
	dut_ctrld = {}
	while not event.is_set():
		for dut in dut_list:
			tprint("!!!!!!!!!!! dut_cpu_memory_proc: relogin at the begining of process")
			relogin_if_needed(dut)
		for d in dut_dir_list:
			dut = d['telnet']
			dut_name = d['name']
			location = d['location']
			size=get_mac_table_size(dut)
			cmd = "diagnose sys top"
			result = loop_command_output(dut,cmd,timeout=2)
			debug(f'{cmd} output: {result}')  # this command has a output rate of 2 sec by default
			tprint("==============dut_cpu_memory thread: CPU utilization at {}=======".format(dut_name))
			print_cmd_output(result,dut_name,cmd)
			top = parse_sys_top(result)
			debug(top)
			if top[0]:
				tprint("!!!!!!!!!!!!!!!!! The following processes' CPU utilization is high!!!!!!!!!!")
				print_cmd_output(top[1],dut_name,cmd)
			cpu_dict = top[2]
			if 'ctrld' in cpu_dict:
				ctrld_cpu = cpu_dict['ctrld']['cpu']
				ctrld_line = cpu_dict['ctrld']['line']
				headline = cpu_dict['ctrld']['headline']
				if ctrld_cpu >= dut_ctrld_highest[dut_name]['cpu']:
					dut_ctrld_highest[dut_name]['cpu'] = ctrld_cpu
					dut_ctrld_highest[dut_name]['line'] = ctrld_line
				tprint(f"{dut_name}: Current MAC table size  = {size}")
				tprint("{}:current sample of ctrld cpu utilization = {}".format(dut_name,ctrld_cpu))
				tprint("{}:highest sample for ctrld cpu utilization = {}".format(dut_name,dut_ctrld_highest[dut_name]['cpu']))
				with open(filename,'a+') as f:
					f.write(time_str(f"{dut_name}: Current MAC table size  = {size}\n"))
					f.write(time_str(f'{dut_name}: {headline}\n'))
					f.write(time_str("{}:current sample of ctrld cpu utilization = {}\n".format(dut_name,ctrld_cpu)))
					f.write(time_str("{}: {}\n".format(dut_name,ctrld_line)))
					f.write(time_str("{}:highest sample for ctrld cpu utilization = {}\n".format(dut_name,dut_ctrld_highest[dut_name]['cpu'])))
					f.write(time_str("{}: {}\n".format(dut_name, dut_ctrld_highest[dut_name]['line'])))
					f.write("-------------------------------------------------------------------------------------\n")
		sleep(2)
		counter += 1
		if counter == 50:
			counter = 0
			for dut in dut_list:
				relogin_if_needed(dut)
	tprint("===============================Exiting dut_cpu_memory process ===================")


def dut_cpu_memory(dut_dir_list,stop,filename):
	sleep(10)
	cmd = "diagnose sys top"
	counter = 0
	dut_list = []
	dut_name_list = []
	dut_location_list = []
	dut_ctrld_highest = {}
	for d in dut_dir_list:
		dut = d['telnet']
		dut_list.append(dut)
		dut_name = d['name']
		dut_name_list.append(dut_name)
		location = d['location']
		dut_location_list.append(location)
		dut_ctrld_highest[dut_name] = {}
		dut_ctrld_highest[dut_name]['cpu'] = 0.0
		dut_ctrld_highest[dut_name]['line'] = ''


	counter = 0
	tprint("================== Start running dut_cpu_memory thread to measure CPU utils =================")
	dut_ctrld = {}
	while True:
		if stop():
			tprint("Main thread is done....Existing background CPU and memory monitoring activities")
			break
		for d in dut_dir_list:
			dut = d['telnet']
			dut_name = d['name']
			location = d['location']
			result = loop_command_output(dut,cmd,timeout=2)  # this command has a output rate of 2 sec by default
			tprint("==============dut_cpu_memory thread: CPU utilization at {}=======".format(dut_name))
			print_cmd_output(result,dut_name,cmd)
			top = parse_sys_top(result)
			debug(top)
			if top[0]:
				tprint("!!!!!!!!!!!!!!!!! The following processes' CPU utilization is high!!!!!!!!!!")
				print_cmd_output(top[1],dut_name,cmd)
			cpu_dict = top[2]
			if 'ctrld' in cpu_dict:
				ctrld_cpu = cpu_dict['ctrld']['cpu']
				ctrld_line = cpu_dict['ctrld']['line']
				headline = cpu_dict['ctrld']['headline']
				if ctrld_cpu >= dut_ctrld_highest[dut_name]['cpu']:
					dut_ctrld_highest[dut_name]['cpu'] = ctrld_cpu
					dut_ctrld_highest[dut_name]['line'] = ctrld_line
				tprint("{}:current sample of ctrld cpu utilization = {}".format(dut_name,ctrld_cpu))
				tprint("{}:highest sample for ctrld cpu utilization = {}".format(dut_name,dut_ctrld_highest[dut_name]['cpu']))
				with open(filename,'a+') as f:
					f.write(time_str(f'{dut_name}: {headline}\n'))
					f.write(time_str("{}:current sample of ctrld cpu utilization = {}\n".format(dut_name,ctrld_cpu)))
					f.write(time_str("{}: {}\n".format(dut_name,ctrld_line)))
					f.write(time_str("{}:highest sample for ctrld cpu utilization = {}\n".format(dut_name,dut_ctrld_highest[dut_name]['cpu'])))
					f.write(time_str("{}: {}\n".format(dut_name, dut_ctrld_highest[dut_name]['line'])))
					f.write("-------------------------------------------------------------------------------------\n")
		sleep(2)
		counter += 1
		if counter == 50:
			counter = 0
			for dut in dut_list:
				relogin_if_needed(dut)
	tprint("===============================Exiting dut_cpu_memory thread ===================")

 

def dut_polling(dut_list,stop):
	tprint("================================ Start running dut_polling ====================")
	dut1 = dut_list[0]
	dut2 = dut_list[1]
	dut3 = dut_list[2]
	dut4 = dut_list[3]
	counter = 0
	while True:
		if stop():
			tprint("Main thread is done....Existing background CLI show command activities")
			break
		tprint("================== CLI show commands for DUT1 =================")
		switch_show_cmd(dut1,"diagnose switch mac-address list")
		switch_show_cmd(dut1,"execute log display")
		switch_show_cmd(dut1,"diagnose stp vlan list")
		tprint("================== CLI show commands for DUT2 =================")
		switch_show_cmd(dut2,"diagnose switch mac-address list")
		switch_show_cmd(dut2,"execute log display")
		switch_show_cmd(dut2,"diagnose stp vlan list")
		tprint("================== CLI show commands for DUT3 =================")
		switch_show_cmd(dut3,"diagnose switch mac-address list")
		switch_show_cmd(dut3,"execute log display")
		switch_show_cmd(dut3,"diagnose stp vlan list")
		tprint("================== CLI show commands for DUT4 =================")
		switch_show_cmd(dut4,"diagnose switch mac-address list")
		switch_show_cmd(dut4,"execute log display")
		switch_show_cmd(dut4,"diagnose stp vlan list")
		sleep(20)
		counter += 1
		if counter == 50:
			counter = 0
			with lock:
				for dut in dut_list:
					relogin_if_needed(dut)


def background_ixia_activity(topology_handle_dict_list,dut_list,stop):
	dut3 = dut_list[2]
	dut4 = dut_list[3]

	ethernet_1_handle = topology_handle_dict_list[0]['ethernet_handle']
	ethernet_2_handle = topology_handle_dict_list[1]['ethernet_handle']
	ethernet_3_handle = topology_handle_dict_list[2]['ethernet_handle']
	ethernet_4_handle = topology_handle_dict_list[3]['ethernet_handle']

	port_1_handle = topology_handle_dict_list[0]['port_handle']
	port_2_handle = topology_handle_dict_list[1]['port_handle']
	port_3_handle = topology_handle_dict_list[2]['port_handle']
	port_4_handle = topology_handle_dict_list[3]['port_handle']

	topology_1_handle = topology_handle_dict_list[0]['topology_handle']
	topology_2_handle = topology_handle_dict_list[1]['topology_handle']
	topology_3_handle = topology_handle_dict_list[2]['topology_handle']
	topology_4_handle = topology_handle_dict_list[3]['topology_handle']

	ipv4_1_handle = topology_handle_dict_list[0]['ipv4_handle']
	ipv4_2_handle = topology_handle_dict_list[1]['ipv4_handle']
	ipv4_3_handle = topology_handle_dict_list[2]['ipv4_handle']
	ipv4_4_handle = topology_handle_dict_list[3]['ipv4_handle']


	deviceGroup_1_handle = topology_handle_dict_list[0]['deviceGroup_handle']
	deviceGroup_2_handle = topology_handle_dict_list[1]['deviceGroup_handle']
	deviceGroup_3_handle = topology_handle_dict_list[2]['deviceGroup_handle']
	deviceGroup_4_handle = topology_handle_dict_list[3]['deviceGroup_handle']
	ip3 = "100.2.0.1"
	ip4 = "100.2.10.1"
	gw3 = "100.2.10.1"
	gw4 = "100.2.0.1"

	tprint("================================ Start running thread at background ====================")
	counter = 1
	MAC_TIMEOUT = 350
	MAC_CLEAR_TIME = 30
	SHORT_TIMEOUT = 5
	LONG_TIMEOUT = 10

	sleep(LONG_TIMEOUT)
	while True:
		if stop():
			tprint("Main thread is done....Existing background IXIA activities")
			break
		ip3,ip4 = ip4,ip3
		gw3,gw4 = gw4,gw3
		#keyin = input("testing....press any key")
		with lock:
			tprint("===== IXIA thread: Lock Acquired")
			ixia_stop_one_protcol(ipv4_3_handle)
			ixia_stop_one_protcol(ipv4_4_handle)
		if counter%2 == 0:
			tprint("========= IXIA thread: Wait for MAC table entries to time out: {} seconds".format(MAC_TIMEOUT))
			sleep(MAC_TIMEOUT)

		else:
			sleep(MAC_CLEAR_TIME)
			tprint("========= IXIA thread: manually clear MAC table entries on DUT3 and DUT4")
			with lock:
				tprint("===== IXIA thread: Lock Acquired")
				relogin_if_needed(dut3)
				relogin_if_needed(dut4)
				tprint("::::: IXIA thread: clearing mac-address on DUT3")
				switch_show_cmd(dut3,"diagnose switch mac-address delete all")
				tprint("::::: IXIA thread: clearing mac-address on DUT3")
				switch_show_cmd(dut4,"diagnose switch mac-address delete all")
				
		sleep(MAC_CLEAR_TIME)
		with lock:		
			tprint("===== IXIA thread: Lock Acquired")
			ixia_start_one_protcol(ipv4_3_handle)
			ixia_start_one_protcol(ipv4_4_handle)
		tprint("========= IXIA thread: Wait time after start IP prtocols on port3 and port4: {}".format(MAC_TIMEOUT))
		sleep(MAC_TIMEOUT)
		#keyin = input("testing....press any key")
		with lock:
			tprint("===== IXIA thread: Lock Acquired")
			ixia_destroy_topology(topology_3_handle,deviceGroup_3_handle,1000)
			ixia_destroy_topology(topology_4_handle,deviceGroup_4_handle,1000)
		sleep(SHORT_TIMEOUT)
		#keyin = input("testing....press any key")
		with lock:
			tprint("===== IXIA thread: Lock Acquired")
			tprint("===== IXIA thread: Generating MAC move events")
			handle_dict = ixia_static_ipv4_topo(
				port=port_3_handle,
				multiplier=1000,
				topology_name="Topology 3",
				device_group_name = "Device Group 3",
				intf_ip=ip3, 
				gateway = gw3,
				intf_mac="00.13.01.00.00.01",
				mask="255.255.0.0"
			)
			ethernet_3_handle = handle_dict['ethernet_handle']
			port_3_handle = handle_dict['port_handle']
			topology_3_handle = handle_dict['topology_handle']
			ipv4_3_handle = handle_dict['ipv4_handle']
			deviceGroup_3_handle = handle_dict['deviceGroup_handle']

			handle_dict = ixia_static_ipv4_topo(
				port=port_4_handle,
				multiplier=1000,
				topology_name="Topology 4",
				device_group_name = "Device Group 4",
				intf_ip=ip4, 
				gateway = gw4,
				intf_mac="00.14.01.00.00.01",
				mask="255.255.0.0"
			)
			ethernet_4_handle = handle_dict['ethernet_handle']
			port_4_handle = handle_dict['port_handle']
			topology_4_handle = handle_dict['topology_handle']
			ipv4_4_handle = handle_dict['ipv4_handle']
			deviceGroup_4_handle = handle_dict['deviceGroup_handle']

			# keyin = input("testing....press any key")
			ixia_start_one_protcol(ipv4_3_handle)
			ixia_start_one_protcol(ipv4_4_handle)
		sleep(MAC_CLEAR_TIME)
		counter += 1
		if counter == 50:
			counter = 0
			with lock:
				for dut in dut_list:
					relogin_if_needed(dut)

def switch_show_cmd_log(dut,cmd,file):
	result = switch_show_cmd(dut,cmd)
	with open(file,'a+') as f:
		for line in result:
			f.write(time_str("{}\n".format(line)))
		#f.write("-------------------------------------------------------------------------------------\n")
	sleep(2)


def system_verification_log(dut_list,file):
	for dut in dut_list:
		print("########################################################################################")
		switch_show_cmd_log(dut,"get system status",file)
		switch_show_cmd_log(dut,"show switch trunk",file)
		switch_show_cmd_log(dut,"diagnose switch mclag peer-consistency-check",file)
		switch_show_cmd_log(dut,"get switch lldp neighbors-summary",file)
		switch_show_cmd_log(dut,"show switch interface port39",file)

def pre_test_verification(dut_list):
	for dut in dut_list:
		print("########################################################################################")
		switch_show_cmd(dut,"get system status")
		switch_show_cmd(dut,"show switch trunk")
		switch_show_cmd(dut,"diagnose switch mclag peer-consistency-check")
		switch_show_cmd(dut,"get switch lldp neighbors-summary")
		switch_show_cmd(dut,"show switch interface port39")

def topology_mclag_8(dut_list):
	print("--------------------------------------------------------------------------")
	print(" 		Configure a MCALG-8 Topology")
	print("--------------------------------------------------------------------------")
	for dut in dut_list:
		switch_unshut_port(dut,"port1")
		switch_unshut_port(dut,"port2")
		switch_unshut_port(dut,"port3")
		switch_unshut_port(dut,"port4")
		switch_configure_cmd(dut,"config switch trunk")
		switch_configure_cmd(dut,"edit mclag-core")
		switch_configure_cmd(dut,"set members port1 port2 port3 port4")
		switch_configure_cmd(dut,"end")

def topology_mclag_4(dut_list):
	print("--------------------------------------------------------------------------")
	print(" 		Configure a MCALG-4 Topology")
	print("--------------------------------------------------------------------------")
	for dut in dut_list:
		switch_unshut_port(dut,"port1")
		switch_unshut_port(dut,"port2")
		switch_unshut_port(dut,"port3")
		switch_unshut_port(dut,"port4")

		switch_shut_port(dut,"port1")
		switch_shut_port(dut,"port3")
		switch_configure_cmd(dut,"config switch trunk")
		switch_configure_cmd(dut,"edit mclag-core")
		switch_configure_cmd(dut,"set members port2 port4")
		switch_configure_cmd(dut,"end")
		time.sleep(2)

def dut_shut_test_mclag_4(dut2,dut4):
	wait_time = 10
	for i in range(2):
		tprint("========= Run Time #{}".format(i+1))
		tprint("Shut 1st active port on dut4 -- Rack20-22: port4")
		switch_shut_port(dut4,"port4")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to unplugging first active link on DUT4----------")
		with lock:
			tprint("==== Main thread: Acquired lock")
			traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
 
		tprint("Shut 2nd active port on dut4 -- Rack20-22: port2")
		switch_shut_port(dut4,"port2")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to unplugging 2nd active link on DUT4----------")
		with lock:
			tprint("==== Main thread: Acquired lock")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
 
		print("##### Test Case: Unshut 2nd active port on dut4 -- Rack20-22: port2")
		switch_unshut_port(dut4,"port2")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to reconnect 2nd active link on DUT4----------")
		with lock:
			tprint("==== Main thread: Acquired lock")
			traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
 		
		print("##### Test Case: Unshut first active port on dut4 -- Rack20-22: port4")
		switch_unshut_port(dut4,"port4")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to reconnect first active link on DUT4----------")
		with lock:
			tprint("==== Main thread: Acquired lock")
			traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
 
	for i in range(2):
		tprint("========= Run Time #{}".format(i))
		tprint("Shut 1st active port on dut2 -- Rack23-28: port4")
		switch_shut_port(dut2,"port4")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to unplugging first active link on DUT4----------")
		with lock:
			tprint("==== Main thread: Acquired lock")
			traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
 
		tprint("Shut 2nd active port on dut2 -- Rack23-28: port2")
		switch_shut_port(dut2,"port2")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to unplugging 2nd active link on DUT4----------")
		with lock:
			tprint("==== Main thread: Acquired lock")
			traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
 
		tprint("Unshut 2nd active port on dut2 -- Rack23-28: port2")
		switch_unshut_port(dut2,"port2")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to reconnect 2nd active link on DUT4----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
 		
		tprint("Unshut first active port on dut2 -- Rack23-28: port4")
		switch_unshut_port(dut2,"port4")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to reconnect first active link on DUT4----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
 
def dut_fibercut_test(dut_dir,mode,**kwargs):
	dut=dut_dir['telnet']
	location = dut_dir['location']
	dut_name = dut_dir['name']

	twargs = {}
	for k, v in kwargs.items():
		twargs[k] = v

	lag_mem = twargs["mem"]
	tier = twargs["tier"]
	runtime = twargs["runtime"]
	#mode = twargs["mode"]
	#location = "XXXXX" # future: location = dut["location"] or something like that
	test_list = []
	if mode == "auto":
		wait_time = 30
	else:
		wait_time = 15
	wait_time_long = 120
	wait_loss_time = 10

	tprint("Clearing traffic statistics before fiber-cut testing starts ....")
	ixia_clear_traffic_stats()
	for i in range(runtime):
		iterate_list = []
		#relogin_if_needed(dut)
		tprint("========= Run Time #{}: MCLAG-{}".format(i+1,lag_mem))
		first_active_port = "port4" # future: port=find_active_trunk_port(dut)
		first_active_port = find_active_trunk_port(dut)
		tprint("MCLAG-{}, Shut/unplug dut:{} 1st active port:{} on located at:{}".format(lag_mem,dut_name,first_active_port,location))  # this has to change to have location and port# dynamic
		if mode == 'auto':
			switch_shut_port(dut,first_active_port)
		else:
			print_interactive_line()
			tprint("Unplug 1st active port fiber on DUT: {} located at: {} port:{}".format(dut_name,location,first_active_port))
			keyin = input("Are you done with unplugging cable? if so press any key...")
		# tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		# time.sleep(wait_time)
		console_timer(wait_time,msg = f"Wait for {wait_time} seconds then measure packet loss")
		traffic_stats = collect_ixia_traffic_stats()
		 
		flow_stat_list_down_1 = parse_traffic_stats_new(traffic_stats,reason="1st-down")
		for f in flow_stat_list_down_1:
			f['dut'] = dut_name
			f['lag_mem'] = lag_mem
			f['test_num'] = i+1
			f['tier'] = tier
		# print_flow_stats_new(flow_stat_list_down_1)

		print_flow_stats_3rd(flow_stat_list_down_1)

		tprint("Clearing IXIA traffic statistics ....")
		ixia_clear_traffic_stats()
		if lag_mem == 8:
			lag8_inactive_port1 = "port1" # future: lag4_inactive_port1,lag4_inactive_port2 = find_inactive_trunk_port()
			lag8_inactive_port2 = "port3"
			try:
				lag8_inactive_port1,lag8_inactive_port2 = find_inactive_trunk_port(dut)
			except  Exception as e:
				tprint("something is wrong with getting inactive port on switch:{}".format(dut_name))
			tprint("MCLAG-8: Shut 2nd and 3rd inactive ports: {},{} on dut:{} located at {} ". \
				format(lag8_inactive_port1,lag8_inactive_port2,dut_name,location))
			if mode == "auto":
				switch_shut_port(dut,lag8_inactive_port1)
				switch_shut_port(dut,lag8_inactive_port2)
			elif mode == "manual":
				print_interactive_line()
				tprint("Unplug MCLAG-8 inactive port fibers on DUT: {} located at: {} ports:{} {}".\
					format(dut_name,location,lag8_inactive_port1,lag8_inactive_port2))
				keyin = input("Are you done with changing cable? if so press any key...")
		else:
			lag2_2nd_port = "port2" # future: port1  = find_active_trunk_port()
			lag2_2nd_port = find_active_trunk_port(dut)
			tprint("MCLAG-2: Shut 2nd active port: {} on dut:{} located at {} ".format(lag2_2nd_port,dut_name,location))
			if mode == "auto":
				switch_shut_port(dut,lag2_2nd_port)
			elif mode == "manual":
				print_interactive_line()
				tprint("Unplug MCLAG-2 2nd port fiber on DUT: {} located at: {} port:{}".format(dut_name,location,lag2_2nd_port))
				keyin = input("Are you done with changing cable? if so press any key...")
		#tprint("Wait for {} seconds before measuring traffic loss".format(wait_time))
		console_timer(wait_time,msg = f"Wait for {wait_time} seconds before measuring traffic loss")
		#time.sleep(wait_time)
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list_down_2 = parse_traffic_stats_new(traffic_stats,reason="2nd-down")
		for f in flow_stat_list_down_2:
			f['dut'] = dut_name
			f['lag_mem'] = lag_mem
			f['test_num'] = i+1
			f['tier'] = tier
		print_flow_stats_3rd(flow_stat_list_down_2)

		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
		if lag_mem == 8:
			tprint("MCLAG-8: UnSnshut 2nd and 3rd inactive ports:{},{} on dut:{} located at: {} ". \
				format(lag8_inactive_port1,lag8_inactive_port2,dut_name,location))	
			if mode == "auto":		 
				switch_unshut_port(dut,lag8_inactive_port1)
				switch_unshut_port(dut,lag8_inactive_port2)
			elif mode == "manual":
				print_interactive_line()
				tprint(" MCLAG-8: Reconnect inactive fibers on DUT:{} located at:{} ports:{} {}".\
					format(dut_name,location,lag8_inactive_port1,lag8_inactive_port2))
				keyin = input("Are you done with changing cable? if so press any key...")
		else:
			tprint("MCLAG-2: UnShut 2nd active port: {} on dut:{} located at {} ".format(lag2_2nd_port,dut_name,location))
			if mode == "auto":
				switch_unshut_port(dut,lag2_2nd_port)
			else:
				print_interactive_line()
				tprint(" MCLAG-2: Reconnect 2nd fiber on DUT: {} located at: {} port:{}".format(dut_name,location,lag2_2nd_port))
				keyin = input("Are you done with changing cable? if so press any key...")
	
		#tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		console_timer(wait_time,msg = f"Wait for {wait_time} seconds then measure packet loss")
		#time.sleep(wait_time)
		traffic_stats = collect_ixia_traffic_stats()
		 
		flow_stat_list_up_1 = parse_traffic_stats_new(traffic_stats,reason="2nd-up")
		for f in flow_stat_list_up_1:
			f['dut'] = dut_name
			f['lag_mem'] = lag_mem
			f['test_num'] = i+1
			f['tier'] = tier
		print_flow_stats_3rd(flow_stat_list_up_1)

		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
		if lag_mem == 8:
			tprint("MCLAG8: Unshut first active port:{} on dut: located at: {}".format(first_active_port,dut_name,location))
			if mode == "auto":
				switch_unshut_port(dut,first_active_port)
			else:
				print_interactive_line()
				tprint(" MCLAG-8: Reconnect 1st active fiber on DUT:{} located at:{} port:{}".\
					format(dut_name,location,first_active_port))
				keyin = input("Are you done with changing cable? if so press any key...")
		else:
			tprint("MCLAG2: Unshut first active port:{} on dut: {} located at: {}".format(first_active_port,dut_name,location))
			if mode == "auto":
				switch_unshut_port(dut,first_active_port)
			else:
				print_interactive_line()
				tprint("MCLAG-2: Reconnect 1st active fiber on DUT:{} located at:{} port:{}".format(dut_name,location,first_active_port))
				keyin = input("Are you done with changing cable? if so press any key...")
		
		#tprint("Wait for {} seconds and measure packet loss".format(wait_time_long))
		console_timer(wait_time,msg = f"Wait for {wait_time} seconds then measure packet loss")
		#time.sleep(wait_time)
		traffic_stats = collect_ixia_traffic_stats()

		
		count = 0
		while traffic_loss_2_flows(traffic_stats,20) == False:
			count += 1
			if count > 10:
				tprint("There is no traffic loss after {} tries, give up!".format(count))
				break
			debug("There is no traffic loss yet, wait for {} seconds and try again ".format(wait_loss_time))
			time.sleep(wait_loss_time)
			traffic_stats = collect_ixia_traffic_stats()
		end_test_active_port = find_active_trunk_port(dut)
		tprint("Before test starts, active port = {}".format(first_active_port))
		tprint("After test finishes, active port = {}".format(end_test_active_port))
		if end_test_active_port != first_active_port:
			tprint("!!!!!! After fiber_cut test, active port has been changed from: {} to: {}".format(first_active_port,end_test_active_port))
		flow_stat_list_up_2 = parse_traffic_stats_new(traffic_stats,reason="1st-up")
		for f in flow_stat_list_up_2:
			f['dut'] = dut_name
			f['lag_mem'] = lag_mem
			f['test_num'] = i+1
			f['tier'] = tier
		print_flow_stats_3rd(flow_stat_list_up_2)


		iterate_list = flow_stat_list_down_1 + flow_stat_list_down_2 + flow_stat_list_up_1 + flow_stat_list_up_2
		test_list.append(iterate_list)

		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
 
	return test_list

def dut_shut_test_mclag_8(dut2,dut4):
	wait_time = 10
	for i in range(2):
		tprint("========= Run Time #{}".format(i))
		tprint("Shut 1st active port on dut4 -- Rack20-22: port4")
		switch_shut_port(dut4,"port4")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to shutting first active port on DUT4----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
 
		tprint("Shut 2nd and 3rd inactive port on dut4 -- Rack20-22: port1, port3")
		switch_shut_port(dut4,"port1")
		switch_shut_port(dut4,"port3")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to shutting 2nd and 3rd inactive port on DUT4----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
 
		tprint("Unshut 2nd and 3rd inactive port on dut4 -- Rack20-22: port1 and port3")
		switch_unshut_port(dut4,"port1")
		switch_unshut_port(dut4,"port3")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to reconnect 2nd active link on DUT4----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
 		
		tprint("Unshut first active port on dut4 -- Rack20-22: port4")
		switch_unshut_port(dut4,"port4")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to reconnect first active link on DUT4----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
 
	for i in range(2):
		tprint("========= Run Time #{}".format(i))
		tprint("Shut 1st active port on dut2 -- Rack23-28: port4")
		switch_shut_port(dut2,"port4")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to shutting first active port on DUT4----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
 

		tprint("Shut 2nd and third inactive port on dut2 -- Rack23-28: port2")
		switch_shut_port(dut2,"port2")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to unplugging 2nd active link on DUT4----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()

		tprint("Unshut 2nd active port on dut2 -- Rack23-28: port2")
		switch_unshut_port(dut2,"port2")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to reconnect 2nd active link on DUT4----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
		
		tprint("Unshut first active port on dut2 -- Rack23-28: port4")
		switch_unshut_port(dut2,"port4")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to reconnect first active link on DUT4----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()

def dut_unplug_test_mclag_4(dut2,dut4):
	wait_time = 10
	for i in range(2):
		tprint("========= Run Time #{}".format(i))
		tprint("Unplug 1st active link on dut4 -- Rack20-22: port4")
		keyin = input("Are you done with unplugging cable? if so press any key...")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to unplugging first active link on DUT4----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()

		tprint("Unplug 2nd active link on dut4 -- Rack20-22: port2")
		keyin = input("Are you done with unplugging cable? if so press any key...")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to unplugging 2nd active link on DUT4----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()

		tprint("Reconnect 2nd active link on dut4 -- Rack20-22: port2")
		keyin = input("Are you done with changing cable? if so press any key...")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to reconnect 2nd active link on DUT4----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
		
		tprint("Reconnect first active link on dut4 -- Rack20-22: port4")
		keyin = input("Are you done with changing cable? if so press any key...")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to reconnect first active link on DUT4----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()

	for i in range(2):
		tprint("========= Run Time #{}".format(i))
		tprint("Unplug 1st active link on dut2 -- Rack23-28: port4")
		keyin = input("Are you done with changing cable? if so press any key...")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to unplugging first active link on DUT2----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()

		tprint("Unplug 2nd active link on dut4 -- Rack23-28: port2")
		keyin = input("Are you done with changing cable? if so press any key...")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to unplugging 2nd active link on DUT2----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()

		tprint("Reconnect 2nd active link on dut4 -- Rack23-28: port2")
		keyin = input("Are you done with changing cable? if so press any key...")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to reconnect 2nd active link on DUT2----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()
		
		tprint("Reconnect first active link on dut4 -- Rack23-28: port4")
		keyin = input("Are you done with changing cable? if so press any key...")
		tprint("Wait for {} seconds and measure packet loss".format(wait_time))
		time.sleep(wait_time)
		print("********* Measure packet loss due to reconnect first active link on DUT2----------")
		traffic_stats = collect_ixia_traffic_stats()
		flow_stat_list = parse_traffic_stats(traffic_stats)
		print_flow_stats(flow_stat_list)
		tprint("Clearing traffic statistics ....")
		ixia_clear_traffic_stats()

def dut_reboot_test_new(dut1,**kwargs):
	twargs = {}
	for k, v in kwargs.items():
		twargs[k] = v

	dut_name = twargs["dut"]
	lag_mem = twargs["mem"]
	runtime = twargs['runtime']
	test_list = []
	tprint("Clearing traffic statistics before reboot-testing starts ....")
	ixia_clear_traffic_stats()
	for i in range(runtime):
		iterate_list = []
		relogin_if_needed(dut1)
		tprint("========= Run Time #{}".format(i+1))
		tprint("Rebooting DUT :....".format(dut_name))
		switch_exec_reboot(dut1,device=dut_name)
		tprint("DUT is being rebooted, wait for 2 seconds before measuring traffic loss")
		time.sleep(2)
		tprint("After waiting for 2 seconds,collect ixia traffic stats")
		print("********* Measure packet loss right after DUT went down ----------")
		traffic_stats = collect_ixia_traffic_stats_stable()
		tprint("Clearing traffic statistics after collecting the down_stats....")
		ixia_clear_traffic_stats()
		flow_stat_list_down = parse_traffic_stats_new(traffic_stats,reason="down")
		for f in flow_stat_list_down:
			f['dut'] = dut_name
			f['lag_mem'] = lag_mem
			f['test_num'] = i+1
		print_flow_stats_3rd(flow_stat_list_down)

		tprint("Allow traffic to run for another 200 seconds after rebooting ....")
		time.sleep(200)
		tprint("Collect traffic stats 20 seconds after DUT1 rebooted")
		print("*********** Measure packet loss due to STP converage after DUT finished rebooting-------")
		traffic_stats = collect_ixia_traffic_stats_stable()
		flow_stat_list_up = parse_traffic_stats_new(traffic_stats,reason="up")
		for f in flow_stat_list_up:
			f['dut'] = dut_name
			f['lag_mem'] = lag_mem
			f['test_num'] = i+1
		print_flow_stats_3rd(flow_stat_list_up)
		iterate_list = flow_stat_list_up + flow_stat_list_down
		test_list.append(iterate_list)
		

		tprint("Clearing traffic statistics after collecting the up_stats....")
		ixia_clear_traffic_stats()
 
	return test_list
# def print_flow_stats(flow_stats_list):
# 	for flow in flow_stats_list:
# 		tprint("Flow ID:{}, RX_Port:{}, TX_Port:{}, TX packet rate:{}, TX packets:{}, RX packets:{},Pkt Loss:{}, Pkt Loss time:{}". \
# 			format(flow['id'],flow['rx_port'],flow['tx_port'],flow['total_pkt_rate'], \
# 				flow['total_tx_pkts'],flow['total_rx_pkts'],flow['loss_pkts'],flow["loss_time"]))
# 		tprint("")

# 		print("--------------------------------")

def collect_ixia_traffic_stats_stable():
	threshold = 30
	stats = collect_ixia_traffic_stats()
	parsed_stats = parse_traffic_stats(stats)
	#there is no packet loss, continue collecting stats
	count = 0
	while traffic_loss_2_flows(stats,threshold) == False and count < 20:
		count += 1
		flow_stat_list_down = parse_traffic_stats_new(stats,reason="down")
		debug("^^^^^^^^^^^^^^^^^^^^^^^^^ Waiting packet loss to show up ^^^^^^^^^^^^^^")
		print_flow_stats_3rd(flow_stat_list_down)
		time.sleep(3)
		stats = collect_ixia_traffic_stats()

		#parsed_stats = parse_traffic_stats(stats)
	#After packet loss begins to show up, wait for a few seconds to measure again
	time.sleep(3)
	while True:
		stats = collect_ixia_traffic_stats()
		parsed_stats_2 = parse_traffic_stats(stats)
		if abs(parsed_stats_2[0]["loss_pkts"] - parsed_stats[0]["loss_pkts"]) < 10 :
			return stats
		else:
			debug("1st check-point pkt loss= {}, 2nd check-point pkt loss = {}".format(parsed_stats[0]["loss_pkts"],parsed_stats_2[0]["loss_pkts"]))
			parsed_stats = parsed_stats_2
			time.sleep(3)

def traffic_loss_2_flows(traffic_stats,threshold):
	flow_list = parse_traffic_stats(traffic_stats)

	for flow_info in flow_list:
		if flow_info['loss_pkts'] > threshold:
			return True
	return False

def parse_traffic_stats_new(traffic_stats,**kwargs):
	tkwargs = {}
	for key, value in kwargs.items():
		tkwargs[key]=value

	for k, v in traffic_stats.items():
		if k == "flow":
			flow_stats = v
			break
	flow_num = list(flow_stats.keys())[0]

	 
	flow_stats_items = flow_stats[flow_num]
	#tprint(flow_stats_items)
	flow_list = []
	for k, v in flow_stats.items():
		flow_info = {}
		flow_info['reason'] = tkwargs["reason"]
		flow_info['id'] = k
		# flow_info['rx'] = rx_stats = v['rx']
		# flow_info['tx'] = tx_stats = v['tx']
		rx_stats = v['rx']
		tx_stats = v['tx']
		flow_info['rx_port'] = rx_stats['port']
		flow_info['total_pkts'] = int(rx_stats['total_pkts'])
		flow_info['total_pkts_bytes'] = int(rx_stats['total_pkts_bytes'])

		flow_info['loss_pkts'] = int(rx_stats['loss_pkts'])
		flow_info['max_delay'] = int(rx_stats['max_delay'])
		flow_info['total_pkt_rate'] =float(tx_stats['total_pkt_rate'])
		flow_info['total_tx_pkts'] = tx_stats['total_pkts']
		flow_info['total_rx_pkts'] = rx_stats['total_pkts']
		if flow_info['total_pkt_rate'] != 0:
			flow_info["loss_time"] = str(flow_info['loss_pkts']/flow_info['total_pkt_rate'])
		else:
			flow_info["loss_time"] = "0 seconds"
		flow_info['tx_port'] = tx_stats['port']
		flow_list.append(flow_info)

	return (flow_list)

def parse_traffic_stats(traffic_stats):
	for k, v in traffic_stats.items():
		if k == "flow":
			flow_stats = v
			break
	flow_num = list(flow_stats.keys())[0]

	 
	flow_stats_items = flow_stats[flow_num]
	#tprint(flow_stats_items)
	flow_list = []
	for k, v in flow_stats.items():
		flow_info = {}
		flow_info['id'] = k
		flow_info['rx'] = rx_stats = v['rx']
		flow_info['tx'] = tx_stats = v['tx']
		flow_info['rx_port'] = rx_stats['port']
		flow_info['total_pkts'] = int(rx_stats['total_pkts'])
		flow_info['total_pkts_bytes'] = int(rx_stats['total_pkts_bytes'])

		flow_info['loss_pkts'] = int(rx_stats['loss_pkts'])
		flow_info['max_delay'] = int(rx_stats['max_delay'])
		flow_info['total_pkt_rate'] =float(tx_stats['total_pkt_rate'])
		flow_info['total_tx_pkts'] = tx_stats['total_pkts']
		flow_info['total_rx_pkts'] = rx_stats['total_pkts']
		if flow_info['total_pkt_rate'] != 0:
			flow_info["loss_time"] = str(flow_info['loss_pkts']/flow_info['total_pkt_rate'])
		else:
			flow_info["loss_time"] = "0 seconds"
		flow_info['tx_port'] = tx_stats['port']
		flow_list.append(flow_info)

	return (flow_list)


def print_dict(obj, nested_level=0, output=sys.stdout):
    """
    Print each dict key with indentions for readability.
    """
    spacing = '   '
    if type(obj) == dict:
        #print >> output, '%s' % ((nested_level) * spacing)
        tprint('%s' % ((nested_level) * spacing),file=output)
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                #print >> output, '%s%s:' % ((nested_level + 1) * spacing, k)
                tprint('%s%s:' % ((nested_level + 1) * spacing, k),file=output)
                print_dict(v, nested_level + 1, output)
            else:
                #print >> output, '%s%s: %s' % ((nested_level + 1) * spacing, k, v)
                tprint('%s%s: %s' % ((nested_level + 1) * spacing, k, v),file = output)

        #print >> output, '%s' % (nested_level * spacing)
        tprint('%s' % (nested_level * spacing),file=output)
    elif type(obj) == list:
        #print >> output, '%s[' % ((nested_level) * spacing)
        tprint('%s[' % ((nested_level) * spacing),file=output)
        for v in obj:
            if hasattr(v, '__iter__'):
                print_dict(v, nested_level + 1, output)
            else:
                #print >> output, '%s%s' % ((nested_level + 1) * spacing, v)
                tprint('%s%s' % ((nested_level + 1) * spacing, v),file=output)
        #print >> output, '%s]' % ((nested_level) * spacing)
        tprint('%s]' % ((nested_level) * spacing),file=output)
    else:
        tprint('%s%s' % (nested_level * spacing, obj),file=output)

def telnet_login_hacking():
	dut1 = get_switch_telnet_connection(dut1_com,dut1_port)
	dut1_dir['name'] = dut1_name
	dut1_dir['location'] = dut1_location
	dut1_dir['telnet'] = dut1
	dut1_dir['cfg'] = dut1_cfg

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
	return dut_list,dut_dir_list

def parse_config_trunk(result):
	trunk_dict_list = []
	for item in result:
		for line in item:
			if 'edit' in line:
				debug(line)
				#regex = r'\s?edit\s+\"([0-9a-z0-9A-Z0-9.]+)\"'
				regex = r'\s?edit\s+\"(.+)\"'
				match = re.match(regex, line)
				if match:
					trunk = match.group(1)
					debug(trunk)
					trunk_dict = {}
					trunk_dict['name'] = trunk
				else:
					ErrorNotify("parse_config_trunk: not able to parse edit line")
					return "Error:<parse_config_trunk> not able to parse edit line"
				
			elif 'member' in line:
				debug(f"parse_config_trunk: parsing set member line... line ={line}")
				regex = r'.?\s?set members\s+(.+)'
				match = re.match(regex, line)
				if match:
					port_list = match.group(1)
					debug(f'port_list = {port_list}')
				else:
					ErrorNotify("parse_config_trunk: error passing member line")
					return "Error:<parse_config_trunk> error passing member line"
				regex = r'\"(port[0-9]+)\"'
				ports = re.findall(regex,port_list)
				debug(ports)
				trunk_dict['mem'] = ports
				trunk_dict_list.append(trunk_dict)
	debug(trunk_dict_list)
	return trunk_dict_list



def parse_config_output(result):

	# result = ['show switch trunk\r', 'config switch trunk', '    
	#edit "8DF4K17000028-0"', '        set mode lacp-active', '        set auto-isl 1', '        
	#set mclag-icl enable', '            set members "port47" "port48"', '    next', '    edit "G39E6T018900038"', '   
	#     set mode lacp-active', '        set auto-isl 1', '        set fortilink 1', '        set mclag enable', '         
	#   set members "port49"', '    next', '    edit "sw1-trunk"', '        set mode lacp-active', '       
	# set mclag enable', '            set members "port13"', '    next', '   
	# edit "G39E6T018900070"', '      
	#  set mode lacp-active', '        set auto-isl 1', '        set fortilink 1', '        set mclag enable',
	# '--More-- \r         \r            set members "port50"',
	# '    next', '    edit "core1"', '        set mode lacp-active', '        set auto-isl 1', '       
	# set mclag enable', '            set members "port1" "port2" "port3" "port4"', 
	#'    next', 'end', '', 'S548DF4K17000014 #']
	config = []
	for line in result:
		line = smooth_cli_line(line)
		if 'show' in line or 'config' in line:
			continue

		if 'end' in line:
			debug (config)
			return config
		if 'edit' in line:
			block = []
			block.append(line.strip())
			continue
		elif 'next' in line:
			config.append(block)
		else:
			try:
				block.append(line.strip())
			except Exception as e:
				debug(f"This is not a config line: {line}")
				pass
	debug(config)
	return config

def check_mclag_peer(dut):
	msg = "ICL is not configured!"

def check_icl_config(dut):
	result = collect_show_cmd(dut,'show switch trunk')
	tprint("================At check_icl_config, print <show switch trunk> ===============")
	print_collect_show(result)
	config = parse_config_output(result)
	for block in config:
		for line in block:
			if "set mclag-icl enable" in line:
				return True

	return False

def dut_switch_trunk(dut):
	result = collect_show_cmd(dut,'show switch trunk')
	config = parse_config_output(result)
	#print(f"!!!!!!!!! show switch trunk output: {config}")
	trunk_dict_list = parse_config_trunk(config)
	debug(trunk_dict_list)
	return trunk_dict_list

def enable_auto_isl(func):
	def inner_func(*args,**kwargs):
		tprint("reset all switch to factory")
		func(*args,**kwargs)
		console_timer(300,msg="After resetting switches to factory, wait for 300 seconds")
		if "dut_list" in kwargs:
			dut_list = kwargs['sw_list']
		# else:
		# 	return inner_func
		for dut in dut_list:
			neighbor_list = get_switch_lldp_summary(dut)
			for neighbor in neighbor_list:
				if neighbor["Status"] == "Up":
					port = neighbor["Portname"]
					sw_physical_port_cmd(dut,port,"set lldp-profile default-auto-isl")

		for dut in dut_list:
			switch_exec_reboot(dut)
		console_timer(300,msg="After setting auto isl on all up ports and reboot, wait for 300 seconds")
	return inner_func

@enable_auto_isl
def switch_factory_reset(*args, **kwargs):
	dut_list = kwargs['dut_list']
	for dut in dut_list:
		switch_interactive_exec(dut,"execute factoryreset","Do you want to continue? (y/n)")

def fgt_get_conn_status(dut):
	pass


# active-3960E (root) # execute switch-controller get-conn-status
# Managed-devices in current vdom root:
 
# STACK-NAME: FortiSwitch-Stack-fortilink
# SWITCH-ID         VERSION           STATUS         FLAG   ADDRESS              JOIN-TIME            NAME            
# S548DF4K17000014  v6.4.0 (384)      Authorized/Up   -   169.254.1.2     Fri Jan  3 14:02:14 2020    -               
# S548DF4K17000028  v6.4.0 (384)      Authorized/Up   C   169.254.1.3     Fri Jan  3 14:02:46 2020    -               
 
# 	 Flags: C=config sync, U=upgrading, S=staged, D=delayed reboot pending, E=configuration sync error
# 	 Managed-Switches: 2 (UP: 2 DOWN: 0)

def sw_physical_port_cmd(dut,port,cmd):
	switch_configure_cmd(dut,'end')
	switch_configure_cmd(dut,"config switch physical-port")
	switch_configure_cmd(dut,f"edit {port}")
	switch_configure_cmd(dut,cmd)
	switch_configure_cmd(dut,'end')


def enable_isl_neighbor(func):
	def inner_func(*args,**kwargs):
		if "sw_list" in kwargs:
			dut_list = kwargs['sw_list']
		# else:
		# 	return inner_func

		for dut in dut_list:
			neighbor_list = get_switch_lldp_summary(dut)
			for neighbor in neighbor_list:
				if neighbor["Status"] == "Up":
					port = neighbor["Portname"]
					sw_physical_port_cmd(dut,port,"set lldp-profile default-auto-isl")

		for dut in dut_list:
			switch_exec_reboot(dut)
		console_timer(300,msg="After enabling auto_isl lldp profile, wait for 300s for fgt to rediscover all managed switches")
		func(*args,**kwargs)
	return inner_func

def decorator_func(func):
	def inner_func(fgt1,fgt1_dir, **kwargs):
		print("Entering decorator function, before calling original function")
		func(fgt1,fgt1_dir,**kwargs)
		print("After calling original function")
	return inner_func


def enable_https_image_push(func):
	def inner_func(fgt1,fgt1_dir,**kwargs):
		cmds = """
		conf vdom
		edit root
		conf switch-controller global
		set https-image-push enable
		end
		"""
		config_cmds_lines(fgt1,cmds)
		func(fgt1,fgt1_dir,**kwargs)
	return inner_func

@enable_https_image_push
@enable_isl_neighbor			
def fgt_upgrade_548d_stages(fgt1,fgt1_dir,**kwargs):
	if "build" in kwargs:
		build = int(kwargs['build'])
	else:
		build = settings.build_548d
	if "sw_list" in kwargs:
		dut_list = kwargs['sw_list']
		reboot = True
	else:
		reboot = False
	tprint(f"================ Upgrading FSWs via Fortigate to {build} =============")
	switch_exec_cmd(fgt1, "config global")
	cmd = f"execute switch-controller switch-software upload tftp FSW_548D_FPOE-v6-build0{build}-FORTINET.out 10.105.19.19"
	switch_exec_cmd(fgt1, cmd,wait=30)
	sleep(30)
	cmd = f"execute switch-controller switch-software upload tftp FSW_548D-v6-build0{build}-FORTINET.out 10.105.19.19"
	switch_exec_cmd(fgt1, cmd,wait=30)
	sleep(30)
	switch_exec_cmd(fgt1, "end")
	switch_exec_cmd(fgt1, "config vdom")
	switch_exec_cmd(fgt1, "edit root")
	cmd = "execute switch-controller switch-software list-available"
	switch_show_cmd_name(fgt1_dir,cmd)
	sleep(2)
	cmd = "execute switch-controller switch-software stage all S548DN-IMG.swtp"
	switch_exec_cmd(fgt1, cmd,wait=30)
	console_timer(30,msg="upgrading all 548-D switches to S548DN-IMG.swtp")
	cmd = "execute switch-controller switch-software stage all S548DF-IMG.swtp"
	switch_exec_cmd(fgt1, cmd,wait=30)
	console_timer(400,msg="upgrading all 548-DF switches to S548DF-IMG.swtp, wait for 400 secs for all switches download image")

	relogin_dut_all(dut_list)
	# for dut in dut_list:
	# 	switch_exec_reboot(dut)
	# console_timer(300,msg ="After reboot,wait for 300 seconds")

@enable_https_image_push
def fgt_upgrade_548d(fgt1,fgt1_dir,**kwargs):
	if "build" in kwargs:
		build = int(kwargs['build'])
	else:
		build = settings.build_548d
	tprint("================ Upgrading FSWs via Fortigate =============")
	switch_exec_cmd(fgt1,'config global')
	cmd = f"execute switch-controller switch-software upload tftp FSW_548D_FPOE-v6-build0{build}-FORTINET.out 10.105.19.19"
	switch_exec_cmd(fgt1, cmd)
	cmd = f"execute switch-controller switch-software upload tftp FSW_548D-v6-build0{build}-FORTINET.out 10.105.19.19"
	switch_exec_cmd(fgt1, cmd)

	cmd = "execute switch-controller switch-software list-available"
	switch_show_cmd_name(fgt1_dir,cmd)

	switch_exec_cmd(fgt1, "end")
	switch_exec_cmd(fgt1, "config vdom")
	switch_exec_cmd(fgt1, "edit root")
	cmd = "execute switch-controller switch-software upgrade S548DN4K17000133 S548DN-IMG.swtp"
	switch_exec_cmd(fgt1, cmd,wait=30)
	console_timer(10,msg="upgrading S548DN4K17000133 S548DN-IMG.swtp")
	cmd = "execute switch-controller switch-software upgrade S548DF4K16000653 S548DF-IMG.swtp"
	switch_exec_cmd(fgt1, cmd,wait=30)
	console_timer(200,msg="upgrading S548DF4K16000653 S548DF-IMG.swtp, wait for 200 secs for tier-2 switches to download image")

	cmd = "execute switch-controller switch-software upgrade S548DF4K17000028 S548DF-IMG.swtp"
	switch_exec_cmd(fgt1, cmd,wait=30)
	console_timer(10,msg="upgrading S548DF4K17000028 S548DF-IMG.swtp")
	cmd = "execute switch-controller switch-software upgrade S548DF4K17000014 S548DF-IMG.swtp"
	switch_exec_cmd(fgt1, cmd,wait=30)
	console_timer(10,msg="upgrading S548DF4K17000014 S548DF-IMG.swtp")
	cmd = "execute switch-controller get-upgrade-status"
	switch_show_cmd_name(fgt1_dir,cmd)


def sa_upgrade_448d(dut,dut_dir,**kwargs):
	if "build" in kwargs:
		build = int(kwargs['build'])
	else:
		build = settings.build_448d

	dut_name = dut_dir['name']
	tprint(f"=================== Upgrading FSW {dut_name} to build # {build} =================")
	image_names = [f"FSW_448D_FPOE-v6-build0{build}-FORTINET.out",f"FSW_448D_POE-v6-build0{build}-FORTINET.out",f"FSW_448D-v6-build0{build}-FORTINET.out"]
	for image in image_names:
		dprint(f"image name = {image}")
		cmd = f"execute restore image tftp {image} 10.105.19.19"
		tprint(f"upgrade command = {cmd}")
		switch_interactive_exec(dut,cmd,"Do you want to continue? (y/n)")
		output = switch_read_console_output(dut,timeout = 60)
		dprint(output)
		for line in output: 
			if "Command fail" in line:
				dprint(f"upgrade with image {image} failed for {dut_name}")
				continue

			elif "Check image OK" in line:
				Info(f"At {dut_name} image {image} is downloaded and checked OK,upgrade should be fine")
				return True

	return False

def sw_config_port_speed(dut,port,speed):
	config = f"""
	config switch physical-port
	edit {port}
	set speed {speed}
	end
	"""
	config_cmds_lines(dut,config)

def sa_upgrade_548d(dut,dut_dir,**kwargs):
	if "build" in kwargs:
		build = int(kwargs['build'])
	else:
		build = settings.build_448d

	dut_name = dut_dir['name']
	tprint(f"=================== Upgrading FSW {dut_name} to build # {build} =================")
	image_names = [f"FSW_548D_FPOE-v6-build0{build}-FORTINET.out",f"FSW_548D-v6-build0{build}-FORTINET.out"]
	for image in image_names:
		dprint(f"image name = {image}")
		cmd = f"execute restore image tftp {image} 10.105.19.19"
		tprint(f"upgrade command = {cmd}")
		switch_interactive_exec(dut,cmd,"Do you want to continue? (y/n)")
		output = switch_read_console_output(dut,timeout = 60)
		dprint(output)
		for line in output: 
			if "Command fail" in line:
				dprint(f"upgrade with image {image} failed for {dut_name}")
				continue

			elif "Check image OK" in line:
				Info(f"At {dut_name} image {image} is downloaded and checked OK,upgrade should be fine")
				return True

	return False