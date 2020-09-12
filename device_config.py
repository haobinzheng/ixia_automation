from utils import *
import settings 
import xmltodict
import xml.etree.ElementTree as ET
from test_process import * 
from common_lib import *
from common_codes import *
from cli_functions import *


def _parse_xml(file):
    tree = ET.parse(file)
    # root = tree.getroot()
    # data = xmltodict.parse(ET.tostring(root))
    print("--------dir(tree)------------")
    print(dir(tree))
    #for item in tree.iterfind('dev1'):
    for item in tree.iter():
        print("----------- dir(item) -------")
        print(dir(item))
        print("---------- item.keys() ----------")
        print(item.keys())
        print("----------- item.getiterator() ----------")
        print(item.getiterator())
        print(" ----------- item.items() ----------")
        print(item.items())
        for i in item:
            print("-----------dir(i) -----------")
            print(dir(i))
            print("----------- i.tag -----------")
            print(i.tag)
            print("----------- i.items() -----------")
            print(i.items())
           
    # with open('tbinfo_bgpv6.xml','r') as tbinfo:
    #     result = xmltodict.parse(tbinfo)
    #     print(result)
    #     exit()

def bgp_testbed_init():
    dut1_com = "10.105.241.144"
    dut1_location = "Rack7-19"
    dut1_port = 2071
    dut1_name = "3032E-R7-19"
    dut1_cfg = "3032E-R7-19"
    dut1_cfg_basic = "3032E_R7_19_basic.cfg"
    dut1_mgmt_ip = "10.105.240.145"
    dut1_mgmt_mask = "255.255.254.0"
    dut1_loop0_ip = "1.1.1.1"
    dut1_vlan1_ip = "10.1.1.1"
    dut1_vlan1_subnet = "10.1.1.0"
    dut1_vlan1_mask = "255.255.255.0"
    dut1_split_ports = ["port3"]
    dut1_40g_ports = ["port9","port19"]
    dut1_static_route_base = "172.16.1"
    dut1_static_route_mask = "255.255.255.0"

    dut2_com = "10.105.241.44"
    dut2_location = "Rack7-40"
    dut2_port = 2066
    dut2_name = "3032D-R7-40"
    dut2_cfg = "3032D-R7-40"
    dut2_cfg_basic = "3032D_R7_40_basic.cfg"
    dut2_mgmt_ip = "10.105.241.40"
    dut2_mgmt_mask = "255.255.254.0"
    dut2_loop0_ip = "2.2.2.2"
    dut2_vlan1_ip = "10.1.1.2"
    dut2_vlan1_subnet = "10.1.1.0"
    dut2_vlan1_mask = "255.255.255.0"
    dut2_split_ports = ["port1","port5","port7"]
    dut2_40g_ports = ["port9","port13"]
    dut2_static_route_base = "172.16.2"
    dut2_static_route_mask = "255.255.255.0"

    dut3_com = "10.105.240.44"
    dut3_location = "Rack4-41"
    dut3_port = 2090
    dut3_name = "1048E-R4-41"
    dut3_cfg = "1048E-R4-41"
    dut3_cfg_basic = "1048E_R4_41_basic.cfg"
    dut3_mgmt_ip = "10.105.240.41"
    dut3_mgmt_mask = "255.255.254.0"
    dut3_loop0_ip = "3.3.3.3"
    dut3_vlan1_ip = "10.1.1.3"
    dut3_vlan1_subnet = "10.1.1.0"
    dut3_vlan1_mask = "255.255.255.0"
    dut3_split_ports = []
    dut3_40g_ports = []
    dut3_static_route_base = "172.16.3"
    dut3_static_route_mask = "255.255.255.0"

    dut4_com = "10.105.240.44"
    dut4_location = "Rack4-40"
    dut4_port = 2007
    dut4_name = "1048D-R4-40"
    dut4_cfg = "1048D-R4-40"
    dut4_cfg_basic = "1048D_R4_40_basic.cfg"
    dut4_mgmt_ip = "10.105.240.40"
    dut4_mgmt_mask = "255.255.254.0"
    dut4_loop0_ip = "4.4.4.4"
    dut4_vlan1_ip = "10.1.1.4"
    dut4_vlan1_subnet = "10.1.1.0"
    dut4_vlan1_mask = "255.255.255.0"
    dut4_split_ports = []
    dut4_40g_ports = []
    dut4_static_route_base = "172.16.4"
    dut4_static_route_mask = "255.255.255.0"

    dut5_com = "10.105.240.144"
    dut5_location = "Rack5-38"
    dut5_port = 2068
    dut5_name = "1024D-R5-38"
    dut5_cfg = "1024D-R5-38"
    dut5_cfg_basic = "1024D_R5_38_basic.cfg"
    dut5_mgmt_ip = "10.105.240.138"
    dut5_mgmt_mask = "255.255.254.0"
    dut5_loop0_ip = "5.5.5.5"
    dut5_vlan1_ip = "10.1.1.5"
    dut5_vlan1_subnet = "10.1.1.0"
    dut5_vlan1_mask = "255.255.255.0"
    dut5_split_ports = []
    dut5_40g_ports = []
    dut5_static_route_base = "172.16.5"
    dut5_static_route_mask = "255.255.255.0"


    dut1_dir = {}
    dut2_dir = {}
    dut3_dir = {} 
    dut4_dir = {}
    dut5_dir = {}
    dut6_dir = {}
    dut7_dir = {}
    dut8_dir = {}

    dut_dir_list = []
    dut_list = []

    dut1 = get_switch_telnet_connection_new(dut1_com,dut1_port)
    dut1_dir['comm'] = dut1_com
    dut1_dir['comm_port'] = dut1_port
    dut1_dir['name'] = dut1_name
    dut1_dir['label'] = 1
    dut1_dir['location'] = dut1_location
    dut1_dir['telnet'] = dut1
    dut1_dir['cfg'] = dut1_cfg
    dut1_dir['mgmt_ip'] = dut1_mgmt_ip
    dut1_dir['mgmt_mask']= dut1_mgmt_mask  
    dut1_dir['loop0_ip']= dut1_loop0_ip  
    dut1_dir['vlan1_ip']= dut1_vlan1_ip 
    dut1_dir['vlan1_2nd'] = "1.1.1.254"
    dut1_dir['internal'] = "1.1.1.100"
    dut1_dir['vlan1_subnet'] = dut1_vlan1_subnet
    dut1_dir['vlan1_mask']= dut1_vlan1_mask  
    dut1_dir['split_ports']= dut1_split_ports  
    dut1_dir['40g_ports']= dut1_40g_ports
    dut1_dir['static_route'] = dut1_static_route_base 
    dut1_dir['static_route_mask'] = dut1_static_route_mask 
    dut1_dir['ebgp_as']  = 65001
    
    dut_dir_list.append(dut1_dir)
    dut_list.append(dut1)
     
    dut2 = get_switch_telnet_connection_new(dut2_com,dut2_port)
    dut2_dir['comm'] = dut2_com
    dut2_dir['comm_port'] = dut2_port
    dut2_dir['name'] = dut2_name
    dut2_dir['label'] = 2
    dut2_dir['location'] = dut2_location
    dut2_dir['telnet'] = dut2
    dut2_dir['cfg'] = dut2_cfg
    dut2_dir['mgmt_ip'] = dut2_mgmt_ip
    dut2_dir['mgmt_mask']= dut2_mgmt_mask  
    dut2_dir['loop0_ip']= dut2_loop0_ip  
    dut2_dir['vlan1_ip']= dut2_vlan1_ip
    dut2_dir['vlan1_2nd'] = "2.2.2.254"  
    dut2_dir['internal'] = "2.2.2.100"
    dut2_dir['vlan1_subnet'] = dut2_vlan1_subnet
    dut2_dir['vlan1_mask']= dut2_vlan1_mask  
    dut2_dir['split_ports']= dut2_split_ports  
    dut2_dir['40g_ports']= dut2_40g_ports 
    dut2_dir['static_route'] = dut2_static_route_base 
    dut2_dir['static_route_mask'] = dut2_static_route_mask 
    dut2_dir['ebgp_as']  = 65002
    dut_dir_list.append(dut2_dir)
    dut_list.append(dut2)

    dut3 = get_switch_telnet_connection_new(dut3_com,dut3_port)
    dut3_dir['comm'] = dut3_com
    dut3_dir['comm_port'] = dut3_port
    dut3_dir['name'] = dut3_name
    dut3_dir['label'] = 3
    dut3_dir['location'] = dut3_location
    dut3_dir['telnet'] = dut3
    dut3_dir['cfg'] = dut3_cfg
    dut3_dir['mgmt_ip'] = dut3_mgmt_ip
    dut3_dir['mgmt_mask']= dut3_mgmt_mask  
    dut3_dir['loop0_ip']= dut3_loop0_ip  
    dut3_dir['vlan1_ip']= dut3_vlan1_ip
    dut3_dir['vlan1_2nd'] = "3.3.3.254"  
    dut3_dir['internal'] = "3.3.3.100"
    dut3_dir['vlan1_subnet'] = dut3_vlan1_subnet
    dut3_dir['vlan1_mask']= dut3_vlan1_mask  
    dut3_dir['split_ports']= dut3_split_ports  
    dut3_dir['40g_ports']= dut3_40g_ports 
    dut3_dir['static_route'] = dut3_static_route_base 
    dut3_dir['static_route_mask'] = dut3_static_route_mask 
    dut3_dir['ebgp_as']  = 65003
    dut_dir_list.append(dut3_dir)
    dut_list.append(dut3)

    dut4 = get_switch_telnet_connection_new(dut4_com,dut4_port)
    dut4_dir['comm'] = dut4_com
    dut4_dir['comm_port'] = dut4_port
    dut4_dir['name'] = dut4_name
    dut4_dir['label'] = 4
    dut4_dir['location'] = dut4_location
    dut4_dir['telnet'] = dut4
    dut4_dir['cfg'] = dut4_cfg
    dut4_dir['mgmt_ip'] = dut4_mgmt_ip
    dut4_dir['mgmt_mask']= dut4_mgmt_mask  
    dut4_dir['loop0_ip']= dut4_loop0_ip  
    dut4_dir['vlan1_ip']= dut4_vlan1_ip  
    dut4_dir['vlan1_2nd'] = "4.4.4.254"
    dut4_dir['internal'] = "4.4.4.100"
    dut4_dir['vlan1_subnet'] = dut4_vlan1_subnet
    dut4_dir['vlan1_mask']= dut4_vlan1_mask  
    dut4_dir['split_ports']= dut4_split_ports  
    dut4_dir['40g_ports']= dut4_40g_ports 
    dut4_dir['static_route'] = dut4_static_route_base 
    dut4_dir['static_route_mask'] = dut4_static_route_mask 
    dut4_dir['ebgp_as']  = 65004
    dut_dir_list.append(dut4_dir)
    dut_list.append(dut4)

    dut5 = get_switch_telnet_connection_new(dut5_com,dut5_port)
    dut5_dir['comm'] = dut5_com
    dut5_dir['comm_port'] = dut5_port
    dut5_dir['name'] = dut5_name
    dut5_dir['label'] = 5
    dut5_dir['location'] = dut5_location
    dut5_dir['telnet'] = dut5
    dut5_dir['cfg'] = dut5_cfg
    dut5_dir['mgmt_ip'] = dut5_mgmt_ip
    dut5_dir['mgmt_mask']= dut5_mgmt_mask  
    dut5_dir['loop0_ip']= dut5_loop0_ip  
    dut5_dir['vlan1_ip']= dut5_vlan1_ip  
    dut5_dir['vlan1_2nd'] = "5.5.5.254"
    dut5_dir['internal'] = "5.5.5.100"
    dut5_dir['vlan1_subnet'] = dut5_vlan1_subnet
    dut5_dir['vlan1_mask']= dut5_vlan1_mask  
    dut5_dir['split_ports']= dut5_split_ports  
    dut5_dir['40g_ports']= dut5_40g_ports 
    dut5_dir['static_route'] = dut5_static_route_base 
    dut5_dir['static_route_mask'] = dut5_static_route_mask 
    dut5_dir['ebgp_as']  = 65005
    dut_dir_list.append(dut5_dir) 
    dut_list.append(dut5)

    dut6 = get_switch_telnet_connection_new("10.105.241.144",2079)
    dut6_dir['comm'] = "10.105.241.144"
    dut6_dir['comm_port'] = 2079
    dut6_dir['name'] = "548D-R8-34"
    dut6_dir['label'] = 6
    dut6_dir['location'] = "Rack8-34"
    dut6_dir['telnet'] = dut6
    dut6_dir['cfg'] = "548D-R8-34"
    dut6_dir['mgmt_ip'] = "10.105.241.134"
    dut6_dir['mgmt_mask']= "255.255.254.0"  
    dut6_dir['loop0_ip']= "6.6.6.6" 
    dut6_dir['vlan1_ip']= "10.1.1.6"  
    dut6_dir['vlan1_2nd'] = "6.6.6.254"
    dut6_dir['internal'] = "6.6.6.100"
    dut6_dir['vlan1_subnet'] = "10.1.1.0"
    dut6_dir['vlan1_mask']= "255.255.255.0"  
    dut6_dir['split_ports']= []
    dut6_dir['40g_ports']= []
    dut6_dir['static_route'] = "172.16.6"
    dut6_dir['static_route_mask'] = "255.255.255.0"
    dut6_dir['ebgp_as']  = 65006
    dut_dir_list.append(dut6_dir) 
    dut_list.append(dut6)

    dut7 = get_switch_telnet_connection_new("10.105.240.44",2002)
    dut7_dir['comm'] = "10.105.240.44"
    dut7_dir['comm_port'] = 2002
    dut7_dir['name'] = "1048D-R4-39"
    dut7_dir['label'] = 7
    dut7_dir['location'] = "Rack4-39"
    dut7_dir['telnet'] = dut7
    dut7_dir['cfg'] = "1048D-R4-39"
    dut7_dir['mgmt_ip'] = "10.105.240.39"
    dut7_dir['mgmt_mask']= "255.255.254.0" 
    dut7_dir['loop0_ip']= "7.7.7.7" 
    dut7_dir['vlan1_ip']= "10.1.1.7"  
    dut7_dir['vlan1_2nd'] = "7.7.7.254"
    dut7_dir['internal'] = "7.7.7.100"
    dut7_dir['vlan1_subnet'] = "10.1.1.0"
    dut7_dir['vlan1_mask']= "255.255.255.0" 
    dut7_dir['split_ports']= []  
    dut7_dir['40g_ports']= [] 
    dut7_dir['static_route'] = "172.16.7"
    dut7_dir['static_route_mask'] = "255.255.255.0" 
    dut7_dir['ebgp_as']  = 65007
    dut_dir_list.append(dut7_dir) 
    dut_list.append(dut7)

    return dut_dir_list

def bgpv6_testbed_init():
    dut1_dir = {}
    dut2_dir = {}
    dut3_dir = {} 
    dut4_dir = {}
    dut5_dir = {}
    dut6_dir = {}
    dut7_dir = {}
    dut8_dir = {}

    dut_dir_list = []
    dut_list = []

    dut7 = get_switch_telnet_connection_new("10.105.241.243",2045,platform="n9k")
    dut7_dir['comm'] = "10.105.241.243"
    dut7_dir['comm_port'] = 2045
    dut7_dir['name'] = "cisco_n9k"
    dut7_dir['label'] = 10
    dut7_dir['location'] = "Rack7-41"
    dut7_dir['telnet'] = dut7
    dut7_dir['cfg'] = "cisco_n9k"
    dut7_dir['mgmt_ip'] = "10.105.241.41"
    dut7_dir['mgmt_mask']= "255.255.254.0"  
    dut7_dir['loop0_ip']= "10.10.10.10" 
    dut7_dir['loop0_ipv6'] = "2001:10:10:10::10/64" 
    dut7_dir['vlan1_ip']= "10.1.1.10"  
    dut7_dir['vlan1_ipv6']= "2001:10:1:1::10/64"
    dut7_dir['vlan1_2nd'] = "10.10.10.254" # Doesn't matter
    dut7_dir['internal'] = "1.1.1.100"  # Doesn't matter
    dut7_dir['internal_v6'] = "2001:1:1::100/64"
    dut7_dir['vlan1_subnet'] = "10.1.1.0"
    dut7_dir['vlan1_mask']= "255.255.255.0"  
    dut7_dir['split_ports']= [] 
    dut7_dir['40g_ports']= []
    dut7_dir['static_route'] = "172.16.10"
    dut7_dir['static_route_mask'] = "255.255.255.0"
    dut7_dir['ebgp_as']  = 65010
    dut7_dir['vendor']  = "cisco"
    dut7_dir['platform']  = "n9k"

    dut_dir_list.append(dut7_dir) 
    dut_list.append(dut7)

    dut1 = get_switch_telnet_connection_new("10.105.241.144",2071)
    dut1_dir['comm'] = "10.105.241.144"
    dut1_dir['comm_port'] = 2071
    dut1_dir['name'] = "3032E-R7-19"
    dut1_dir['label'] = 1
    dut1_dir['location'] = "Rack7-19"
    dut1_dir['telnet'] = dut1
    dut1_dir['cfg'] = "3032E-R7-19"
    dut1_dir['mgmt_ip'] =  "10.105.240.145"
    dut1_dir['mgmt_mask']= "255.255.254.0"
    dut1_dir['loop0_ip']= "1.1.1.1"
    dut1_dir['loop0_ipv6'] = "2001:1:1:1::1/64"  
    dut1_dir['vlan1_ip']= "10.1.1.1" 
    dut1_dir['vlan1_ipv6']= "2001:10:1:1::1/64"
    dut1_dir['vlan1_2nd'] = "1.1.1.254"
    dut1_dir['internal'] = "1.1.1.100"
    dut1_dir['internal_v6'] = "2001:1:1::100/64"
    dut1_dir['vlan1_subnet'] = "10.1.1.0"
    dut1_dir['vlan1_mask']= "255.255.255.0"  
    dut1_dir['split_ports']= ["port15"] 
    dut1_dir['40g_ports']= ["port1"]
    dut1_dir['static_route'] = "172.16.1" 
    dut1_dir['static_route_mask'] = "255.255.255.0"
    dut1_dir['ebgp_as']  = 65001
    dut1_dir['vendor']  = "fortinet"
    dut1_dir['platform']  = "fortinet"
    
    dut_dir_list.append(dut1_dir)
    dut_list.append(dut1)
     
    dut2 = get_switch_telnet_connection_new("10.105.241.44",2066)
    dut2_dir['comm'] = "10.105.241.44"
    dut2_dir['comm_port'] = 2066
    dut2_dir['name'] = "3032D-R7-40"
    dut2_dir['label'] = 2
    dut2_dir['location'] = "Rack7-40"
    dut2_dir['telnet'] = dut2
    dut2_dir['cfg'] = "3032D-R7-40"
    dut2_dir['mgmt_ip'] = "10.105.241.40"
    dut2_dir['mgmt_mask']= "255.255.254.0"  
    dut2_dir['loop0_ip']= "2.2.2.2"  
    dut2_dir['loop0_ipv6'] = "2001:2:2:2::2/64" 
    dut2_dir['vlan1_ip']= "10.1.1.2"
    dut2_dir['vlan1_ipv6']= "2001:10:1:1::2/64"
    dut2_dir['vlan1_2nd'] = "2.2.2.254"  
    dut2_dir['internal'] = "2.2.2.100"
    dut2_dir['internal_v6'] = "2001:2:2::100/64"
    dut2_dir['vlan1_subnet'] = "10.1.1.0"
    dut2_dir['vlan1_mask']= "255.255.255.0" 
    dut2_dir['split_ports']= []  
    dut2_dir['40g_ports']= ["port1"] 
    dut2_dir['static_route'] = "172.16.2" 
    dut2_dir['static_route_mask'] = "255.255.255.0"
    dut2_dir['ebgp_as']  = 65002
    dut2_dir['vendor']  = "fortinet"
    dut2_dir['platform']  = "fortinet"
    dut_dir_list.append(dut2_dir)
    dut_list.append(dut2)


    dut3 = get_switch_telnet_connection_new("10.105.240.44", 2020)
    dut3_dir['comm'] = "10.105.240.44"
    dut3_dir['comm_port'] = 2020
    dut3_dir['name'] =  "1048E-R3-40"
    dut3_dir['label'] = 3
    dut3_dir['location'] = "Rack3-40"
    dut3_dir['telnet'] = dut3
    dut3_dir['cfg'] = "1048E-R3-40"
    dut3_dir['mgmt_ip'] = "10.105.240.41"
    dut3_dir['mgmt_mask']= "255.255.254.0" 
    dut3_dir['loop0_ip']= "3.3.3.3" 
    dut3_dir['loop0_ipv6'] = "2001:3:3:3::3/64"  
    dut3_dir['vlan1_ip']= "10.1.1.3"
    dut3_dir['vlan1_ipv6']= "2001:10:1:1::3/64"
    dut3_dir['vlan1_2nd'] = "3.3.3.254"  
    dut3_dir['internal'] = "3.3.3.100"
    dut3_dir['internal_v6'] = "2001:3:3::100/64"
    dut3_dir['vlan1_subnet'] = "10.1.1.0"
    dut3_dir['vlan1_mask']= "255.255.255.0"  
    dut3_dir['split_ports']= []
    dut3_dir['40g_ports']= []
    dut3_dir['static_route'] = "172.16.3" 
    dut3_dir['static_route_mask'] = "255.255.255.0" 
    dut3_dir['ebgp_as']  = 65003
    dut3_dir['vendor']  = "fortinet"
    dut3_dir['platform']  = "fortinet"
    dut_dir_list.append(dut3_dir)
    dut_list.append(dut3)

    dut4 = get_switch_telnet_connection_new("10.105.240.44", 2007)
    dut4_dir['comm'] = "10.105.240.44"
    dut4_dir['comm_port'] = 2007
    dut4_dir['name'] = "1048D-R4-40"
    dut4_dir['label'] = 4
    dut4_dir['location'] = "Rack4-40"
    dut4_dir['telnet'] = dut4
    dut4_dir['cfg'] = "1048D-R4-40"
    dut4_dir['mgmt_ip'] = "10.105.240.40"
    dut4_dir['mgmt_mask']= "255.255.254.0" 
    dut4_dir['loop0_ip']= "4.4.4.4"  
    dut4_dir['loop0_ipv6'] = "2001:4:4:4::4/64" 
    dut4_dir['vlan1_ip']= "10.1.1.4" 
    dut4_dir['vlan1_ipv6']= "2001:10:1:1::4/64"
    dut4_dir['vlan1_2nd'] = "4.4.4.254"
    dut4_dir['internal'] = "4.4.4.100"
    dut4_dir['internal_v6'] = "2001:4:4::100/64"
    dut4_dir['vlan1_subnet'] = "10.1.1.0"
    dut4_dir['vlan1_mask']= "255.255.255.0" 
    dut4_dir['split_ports']= []
    dut4_dir['40g_ports']= []
    dut4_dir['static_route'] = "172.16.4" 
    dut4_dir['static_route_mask'] = "255.255.255.0" 
    dut4_dir['ebgp_as']  = 65004
    dut4_dir['vendor']  = "fortinet"
    dut4_dir['platform']  = "fortinet"
    dut_dir_list.append(dut4_dir)
    dut_list.append(dut4)

    dut5 = get_switch_telnet_connection_new("10.105.240.144",2070)
    dut5_dir['comm'] = "10.105.240.144"
    dut5_dir['comm_port'] = 2070
    dut5_dir['name'] = "548D-R5-33"
    dut5_dir['label'] = 5
    dut5_dir['location'] = "Rack5-33"
    dut5_dir['telnet'] = dut5
    dut5_dir['cfg'] = "548D-R5-33"
    dut5_dir['mgmt_ip'] = "10.105.240.133"
    dut5_dir['mgmt_mask']= "255.255.254.0" 
    dut5_dir['loop0_ip']= "5.5.5.5" 
    dut5_dir['loop0_ipv6'] = "2001:5:5:5::5/64" 
    dut5_dir['vlan1_ip']= "10.1.1.5"  
    dut5_dir['vlan1_ipv6']= "2001:10:1:1::5/64"
    dut5_dir['vlan1_2nd'] = "5.5.5.254"
    dut5_dir['internal'] = "5.5.5.100"
    dut5_dir['internal_v6'] = "2001:5:5::100/64"
    dut5_dir['vlan1_subnet'] = "10.1.1.0"
    dut5_dir['vlan1_mask']= "255.255.255.0"  
    dut5_dir['split_ports']= []  
    dut5_dir['40g_ports']= []
    dut5_dir['static_route'] = "172.16.5" 
    dut5_dir['static_route_mask'] = "255.255.255.0" 
    dut5_dir['ebgp_as']  = 65005
    dut5_dir['vendor']  = "fortinet"
    dut5_dir['platform']  = "fortinet"
    dut_dir_list.append(dut5_dir) 
    dut_list.append(dut5)

    dut6 = get_switch_telnet_connection_new("10.105.241.144",2090)
    dut6_dir['comm'] = "10.105.241.144"
    dut6_dir['comm_port'] = 2090
    dut6_dir['name'] = "548D-R8-33"
    dut6_dir['label'] = 6
    dut6_dir['location'] = "Rack8-33"
    dut6_dir['telnet'] = dut6
    dut6_dir['cfg'] = "548D-R8-33"
    dut6_dir['mgmt_ip'] = "10.105.241.134"
    dut6_dir['mgmt_mask']= "255.255.254.0"  
    dut6_dir['loop0_ip']= "6.6.6.6" 
    dut6_dir['loop0_ipv6'] = "2001:6:6:6::6/64" 
    dut6_dir['vlan1_ip']= "10.1.1.6"  
    dut6_dir['vlan1_ipv6']= "2001:10:1:1::6/64"
    dut6_dir['vlan1_2nd'] = "6.6.6.254"
    dut6_dir['internal'] = "6.6.6.100"
    dut6_dir['internal_v6'] = "2001:6:6::100/64"
    dut6_dir['vlan1_subnet'] = "10.1.1.0"
    dut6_dir['vlan1_mask']= "255.255.255.0"  
    dut6_dir['split_ports']= []
    dut6_dir['40g_ports']= []
    dut6_dir['static_route'] = "172.16.6"
    dut6_dir['static_route_mask'] = "255.255.255.0"
    dut6_dir['ebgp_as']  = 65006
    dut6_dir['vendor']  = "fortinet"
    dut6_dir['platform']  = "fortinet"
    dut_dir_list.append(dut6_dir) 
    dut_list.append(dut6)

    return dut_dir_list

def cisco_testbed_init():
    cisco_dir_list = []
    cisco1_dir = {}
    cisco1 = get_switch_telnet_connection_new("10.105.241.243",2045)
    cisco1_dir['comm'] = "10.105.241.243"
    cisco1_dir['comm_port'] = 2045
    cisco1_dir['name'] = "cisco_n9k"
    cisco1_dir['label'] = 10
    cisco1_dir['location'] = "Rack7-41"
    cisco1_dir['telnet'] = cisco1
    cisco1_dir['cfg'] = "cisco_n9k"
    cisco1_dir['mgmt_ip'] = "10.105.241.41"
    cisco1_dir['mgmt_mask']= "255.255.254.0"  
    cisco1_dir['loop0_ip']= "10.10.10.10" 
    cisco1_dir['loop0_ipv6'] = "2001:10:10:10::10/64" 
    cisco1_dir['vlan1_ip']= "10.1.1.10"  
    cisco1_dir['vlan1_ipv6']= "2001:10:1:1::10/64"
    cisco1_dir['vlan1_subnet'] = "10.1.1.0"
    cisco1_dir['vlan1_mask']= "255.255.255.0"  
    cisco1_dir['static_route'] = "172.16.10"
    cisco1_dir['static_route_mask'] = "255.255.255.0"
    cisco1_dir['ebgp_as']  = 65010
    cisco_dir_list.append(dut6_dir) 
    cisco_list.append(cisco)
    # dut7 = get_switch_telnet_connection_new("10.105.240.44",2002)
    # dut7_dir['comm'] = "10.105.240.44"
    # dut7_dir['comm_port'] = 2002
    # dut7_dir['name'] = "1048D-R4-39"
    # dut7_dir['label'] = 7
    # dut7_dir['location'] = "Rack4-39"
    # dut7_dir['telnet'] = dut7
    # dut7_dir['cfg'] = "1048D-R4-39"
    # dut7_dir['mgmt_ip'] = "10.105.240.39"
    # dut7_dir['mgmt_mask']= "255.255.254.0" 
    # dut7_dir['loop0_ip']= "7.7.7.7" 
    # dut7_dir['vlan1_ip']= "10.1.1.7"  
    # dut7_dir['vlan1_2nd'] = "7.7.7.254"
    # dut7_dir['internal'] = "7.7.7.100"
    # dut7_dir['vlan1_subnet'] = "10.1.1.0"
    # dut7_dir['vlan1_mask']= "255.255.255.0" 
    # dut7_dir['split_ports']= []  
    # dut7_dir['40g_ports']= [] 
    # dut7_dir['static_route'] = "172.16.7"
    # dut7_dir['static_route_mask'] = "255.255.255.0" 
    # dut7_dir['ebgp_as']  = 65007
    # dut_dir_list.append(dut7_dir) 
    # dut_list.append(dut7)

    



def fsw_upgrade(*args,**kwargs):
    build = int(kwargs['build'])
    dut_dict = kwargs['dut_dict']
    dut_name = dut_dict['name']
    dut = dut_dict['telnet']

    print(f'=============   Platform = dut_dict["platform"]')
    if dut_dict['platform'] != "fortinet":
        return
    
    tprint(f"=================== Upgrading FSW {dut_name} to build # {build} =================")
    model = find_dut_model(dut)
    model = model.strip()
    if model == "FSW_448D_FPOE":
        image_name = f"FSW_448D_FPOE-v6-build0{build}-FORTINET.out"
    elif model == "FSW_448D_POE":
        image_name =  f"FSW_448D_POE-v6-build0{build}-FORTINET.out" 
    elif model == "FSW_448D-v6":
        image_name = f"FSW_448D-v6-build0{build}-FORTINET.out"
    elif model == "FortiSwitch-3032E":
        if build == -1:
            image_name = "fs3e32.deb"
        else:
            image_name = f"FSW_3032E-v6-build0{build}-FORTINET.out"
    elif model == "FortiSwitch-3032D":
        if build == -1:
            image_name = "fs3d32.deb"
        else:
            image_name = f"FSW_3032D-v6-build0{build}-FORTINET.out"
    elif model == "FortiSwitch-1048E":
        if build == -1:
            image_name = "fs1e48.deb"
        else:
            image_name = f"FSW_1048E-v6-build0{build}-FORTINET.out"
    elif model == "FortiSwitch-1048D":
        if build == -1:
            image_name = "fs1d48.deb"
        else:
            image_name = f"FSW_1048D-v6-build0{build}-FORTINET.out"
    elif model == "FortiSwitch-1024D":
        if build == -1:
            image_name = "fs1d24.deb"
        else:
            image_name = f"FSW_1024D-v6-build0{build}-FORTINET.out"
    elif model == "FortiSwitch-548D-FPOE":
            image_name = f"FSW_548D_FPOE-v6-build0{build}-FORTINET.out"
    elif model == "FortiSwitch-548D":
            image_name = f"FSW_548D-v6-build0{build}-FORTINET.out"
    else:
        tprint("!!!!!!!!! Not able to identify switch platform, upgrade fails")
        return False

    dprint(f"image name = {image_name}")
    cmd = f"execute restore image tftp {image_name} 10.105.19.19"
    tprint(f"upgrade command = {cmd}")
    switch_interactive_exec(dut,cmd,"Do you want to continue? (y/n)")
    #console_timer(60,msg="wait for 60s to download image from tftp server")
    #switch_wait_enter_yes(dut,"Do you want to continue? (y/n)")
    prompt = "Do you want to continue? (y/n)"
    output = switch_read_console_output(dut,timeout = 40)
    dprint(output)
    result = False
    for line in output: 
        if "Command fail" in line:
            Info(f"upgrade with image {image_name} failed for {dut_name}")
            result = False

        elif "Check image OK" in line:
            Info(f"At {dut_name} image {image_name} is downloaded and checked OK,upgrade should be fine")
            result = True

        elif "Writing the disk" in line:
            Info(f"At {dut_name} image {image_name} is being written into disk, upgrade is Good!")
            result = True

        elif "Do you want to continue" in line:
            dprint(f"Being prompted to answer yes/no 2nd time.  Prompt = {prompt}")
            switch_enter_yes(dut)
            result = True
        else:
            pass
    return result

    

def sw_init_config_v6(*args, **kwargs):
    dut_dir = kwargs['device']
    dut_name = dut_dir['name']  
    dut_location = dut_dir['location'] 
    dut = dut_dir['telnet'] 
    dut_cfg_file = dut_dir['cfg']  
    mgmt_ip = dut_dir['mgmt_ip']  
    mgmt_mask = dut_dir['mgmt_mask']  
    loop0_ip = dut_dir['loop0_ip'] 
    loop0_ipv6 = dut_dir['loop0_ipv6']   
    vlan1_ip = dut_dir['vlan1_ip']
    vlan1_ipv6 = dut_dir['vlan1_ipv6']
    vlan1_subnet = dut_dir['vlan1_subnet']
    vlan1_mask = dut_dir['vlan1_mask']  
    split_ports = dut_dir['split_ports'] 
    ports_40g = dut_dir['40g_ports'] 
    vlan1_2nd = dut_dir['vlan1_2nd']
    internal = dut_dir['internal']
    internal_v6 = dut_dir['internal_v6']

    if "config_split" in kwargs:
        config_split = kwargs["config_split"]
    else:
        config_split = False

    config_global_hostname = f"""
    config system global
    set hostname {dut_name}
    end
    """

    config_cmds_lines(dut,config_global_hostname)
    config = f"""
        config system console 
        set output standard
        end
        """
    config_cmds_lines(dut,config)

    config_mgmt_mode = f"""
    config system interface
    config system interface
        edit mgmt
        set mode static
        end
    config system interface
        edit "mgmt"
        set mode static
        end
    """
    config_cmds_lines(dut,config_mgmt_mode)

    config_sys_interface = f"""
    config system interface
    edit mgmt
        set mode static
        set ip {mgmt_ip} {mgmt_mask}
        set allowaccess ping https http ssh snmp telnet radius-acct
        next
    edit vlan1
        set ip {vlan1_ip} {vlan1_mask}
        set allowaccess ping https ssh telnet
        set vlanid 1
        set interface internal
        set secondary-IP enable 
        config ipv6
                set ip6-address {vlan1_ipv6}
                set ip6-allowaccess ping https ssh telnet
            end
        next
        config secondaryip 
            edit 1
                set ip {vlan1_2nd} 255.255.255.255
                set allowaccess ping https ssh telnet
            next
            end
        next
    edit "loop0"
        set ip {loop0_ip} 255.255.255.255
        set allowaccess ping https http ssh telnet
        set type loopback
            config ipv6
                set ip6-address {loop0_ipv6}
                set ip6-allowaccess ping https ssh telnet
            end
        next
     edit "internal"
        set ip {internal} 255.255.255.255
        set allowaccess ping https http ssh telnet
        set type physical
        config ipv6
                set ip6-address {internal_v6}
                set ip6-allowaccess ping https ssh telnet
            end
        next
    next
    end
    """
    config_cmds_lines(dut,config_sys_interface)


    static_route = f"""
    config router static
    edit 1
        set device "mgmt"
        set dst 0.0.0.0 0.0.0.0
        set gateway 10.105.241.254
    next
    end
    """
    config_cmds_lines(dut,static_route)

    for port in ports_40g:
        sw_config_port_speed(dut,port,"40000cr4")

    # ospf_config = f"""
    # config router ospf
    # set router-id {loop0_ip}
    #     config area
    #         edit 0.0.0.0
    #         next
    #     end
    #     config ospf-interface
    #         edit "1"
    #             set interface "vlan1"
    #         next
    #     end
    #     config network
    #         edit 1
    #             set area 0.0.0.0
    #             set prefix {vlan1_subnet} 255.255.255.0
    #         next
    #     end
    #     config network
    #         edit 2
    #             set area 0.0.0.0
    #             set prefix {loop0_ip} 255.255.255.255
    #         next
    #     end
    #     config redistribute "connected"
    #         set status enable
    #     end
    # end
    # """
    # config_cmds_lines(dut,ospf_config)
    if config_split: 
        for port in split_ports:
            config_split_ports = f"""
            config switch phy-mode
            set {port}-phy-mode 4x10G
            end
            """
            config_cmds_lines(dut,config_split_ports)
            switch_enter_yes(dut)
            console_timer(200,msg="switch is being rebooted after configuring split port, wait for 200s")
            try:
                relogin_if_needed(dut)
            except Exception as e:
                debug("something is wrong with rlogin_if_needed at functionsw_init_config, try again")
                relogin_if_needed(dut)
        for port in split_ports:
            i = 0
            for i in range(4):
                i +=1 
                config = f"""
                config switch physical-port
                edit {port}.{i}
                    set speed 10000sr
                    end 
                """
                config_cmds_lines(dut,config)

    switch_show_cmd(dut,"show system interface")
    switch_show_cmd(dut,"get switch module summary")
    # switch_show_cmd(dut,"show router ospf")
    switch_show_cmd(dut,"show router static")

def sw_init_config(*args, **kwargs):
    dut_dir = kwargs['device']

    dut_name = dut_dir['name']  
    dut_location = dut_dir['location'] 
    dut = dut_dir['telnet'] 
    dut_cfg_file = dut_dir['cfg']  
    mgmt_ip = dut_dir['mgmt_ip']  
    mgmt_mask = dut_dir['mgmt_mask']  
    loop0_ip = dut_dir['loop0_ip']   
    vlan1_ip = dut_dir['vlan1_ip']
    vlan1_subnet = dut_dir['vlan1_subnet']
    vlan1_mask = dut_dir['vlan1_mask']  
    split_ports = dut_dir['split_ports'] 
    ports_40g = dut_dir['40g_ports'] 
    vlan1_2nd = dut_dir['vlan1_2nd']
    internal = dut_dir['internal']

    config_global_hostname = f"""
    config system global
    set hostname {dut_name}
    end
    """

    config_cmds_lines(dut,config_global_hostname)
    config = f"""
        config system console 
        set output standard
        end
        """
    config_cmds_lines(dut,config)

    config_mgmt_mode = f"""
    config system interface
    config system interface
    	edit mgmt
    	set mode static
    	end
    config system interface
    	edit "mgmt"
    	set mode static
    	end
    """
    config_cmds_lines(dut,config_mgmt_mode)

    config_sys_interface = f"""
    config system interface
    edit mgmt
    	set mode static
        set ip {mgmt_ip} {mgmt_mask}
        set allowaccess ping https http ssh snmp telnet radius-acct
        next
    edit vlan1
        set ip {vlan1_ip} {vlan1_mask}
        set allowaccess ping https ssh telnet
        set vlanid 1
        set interface internal
        set secondary-IP enable 
        config secondaryip 
            edit 1
                set ip {vlan1_2nd} 255.255.255.255
                set allowaccess ping https ssh telnet
            next
            end
        next
    edit "loop0"
        set ip {loop0_ip} 255.255.255.255
        set allowaccess ping https http ssh telnet
        set type loopback
        next

     edit "internal"
        set ip {internal} 255.255.255.255
        set allowaccess ping https http ssh telnet
        set type physical
    next
    end
    """
    config_cmds_lines(dut,config_sys_interface)


    static_route = f"""
    config router static
    edit 1
        set device "mgmt"
        set dst 0.0.0.0 0.0.0.0
        set gateway 10.105.241.254
    next
    end
    """
    config_cmds_lines(dut,static_route)

    for port in ports_40g:
        sw_config_port_speed(dut,port,"40000cr4")

    # ospf_config = f"""
    # config router ospf
    # set router-id {loop0_ip}
    #     config area
    #         edit 0.0.0.0
    #         next
    #     end
    #     config ospf-interface
    #         edit "1"
    #             set interface "vlan1"
    #         next
    #     end
    #     config network
    #         edit 1
    #             set area 0.0.0.0
    #             set prefix {vlan1_subnet} 255.255.255.0
    #         next
    #     end
    #     config network
    #         edit 2
    #             set area 0.0.0.0
    #             set prefix {loop0_ip} 255.255.255.255
    #         next
    #     end
    #     config redistribute "connected"
    #         set status enable
    #     end
    # end
    # """
    # config_cmds_lines(dut,ospf_config)

    for port in split_ports:
        config_split_ports = f"""
        config switch phy-mode
        set {port}-phy-mode 4x10G
        end
        """
        config_cmds_lines(dut,config_split_ports)
        switch_enter_yes(dut)
        console_timer(200,msg="switch is being rebooted after configuring split port, wait for 200s")
        try:
            relogin_if_needed(dut)
        except Exception as e:
            debug("something is wrong with rlogin_if_needed at functionsw_init_config, try again")
            relogin_if_needed(dut)
    for port in split_ports:
        i = 0
        for i in range(4):
            i +=1 
            config = f"""
            config switch physical-port
            edit {port}.{i}
                set speed 10000sr
                end 
            """
            config_cmds_lines(dut,config)

    switch_show_cmd(dut,"show system interface")
    switch_show_cmd(dut,"get switch module summary")
    # switch_show_cmd(dut,"show router ospf")
    switch_show_cmd(dut,"show router static")


if __name__ == "__main__":
    file = 'tbinfo_bgpv6.xml'
    _parse_xml(file)





