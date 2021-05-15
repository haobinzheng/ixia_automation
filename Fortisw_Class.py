from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

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
import pdb
# import xlsxwriter
# from excel import *
# #from ixia_ngfp_lib import *
# import settings
# from console_util  import  *
# import pexpect
# from threading import Thread
# import subprocess
# import spur

from robot.api import logger

from local_util import *

DEBUG = True

# S524DF5018000010 # show switch interface  port13
# config switch interface
#     edit "port13"
#         set allowed-vlans 4093
#         set untagged-vlans 4093
#         set snmp-index 13
#     next
# end

# S524DF5018000010 # show switch interface  port13
# config switch interface
#     edit "port13"
#         set allowed-vlans 10,4089-4093
#         set untagged-vlans 4093
#         set snmp-index 13
#     next
# end
# def parse_allow_vlans(output):

class port_class():
    def __init__(self,name):
        self.name = name
        self.allow_vlans = []
        self.lldp_neighbor = None

    def parse_port_config(self,output):
        # printr("Enter parse_port_config")
        for line in output:
            if "allowed-vlans" in line:
                regex = r'set allowed-vlans ([0-9|\-\,]+)'
                matched = re.search(regex,line)
                if matched:
                    vlans = matched.group(1)
                    vlan_list = vlans.split(',')
                    self.allow_vlans = vlan_list
                    # printr(vlan_list)

    def update_allowed_vlan(self,allow_vlans):
        pass

class switch_vlan():
    def __init__(self,output):
        self.sample_output = """
        id                  : 10
        private-vlan        : disable
        description         : (null)
        learning            : enable
        rspan-mode          : disable
        igmp-snooping       : disable
        mld-snooping        : enable
        mld-snooping-fast-leave: enable
        mld-snooping-querier: enable
        mld-snooping-querier-addr: ::
        mld-snooping-proxy  : enable
        mld-snooping-static-group:
        == [ static-group-1 ]
        name: static-group-1            mcast-addr: ff3e::10           members:
            == [ port1 ]
            member-name: port1

        dhcp-snooping       : disable
        dhcp6-snooping      : disable
        member-by-mac:
        member-by-ipv4:
        member-by-ipv6:
        member-by-proto:
        """
        self.id = None
        self.private_vlan = None
        self.learning = None
        self.rspan_mode = None
        self.igmp_snooping = None
        self.mld_snooping = None 
        self.mld_snooping_fast_leave = None 
        self.mld_snooping_querier = None 
        self.mld_snooping_querier_addr = None 
        self.mld_snooping_proxy = None 
        self.mld_snooping_static_group = None 
        self.dhcp_snooping = None 
        self.dhcp6_snooping = None 
        self.member_by_mac = None
        self.member_by_ipv4 = None
        self.member_by_proto = None
        self.config_dict = None 
        self.parse_vlan_get(output)
        self.print_sw_vlan()

    def parse_vlan_get(self,output):
        if type(output) == dict:
            vlan_dict = output
        else:
            vlan_dict = {}
            for line in output:
                if "::" in line:
                    k,v = line.split()
                    k = k.strip(":")
                    vlan_dict[k.strip()] = v.strip()
                else:
                    words = line.split(":")
                    if len(words) == 2:
                        k = words[0]
                        v = words[1]
                        vlan_dict[k.strip()] = v.strip()
                    elif len(words) == 1:
                        k = words[0]
                        vlan_dict[k.strip()] = "Null"
            
            printr("vlan_dict = {}".format(vlan_dict))

        if 'id' in vlan_dict:
            self.id = vlan_dict.get('id',None)
        else:
            self.id = None
            vlan_dict['id'] = None

        if 'private-vlan' in vlan_dict:
            self.private_vlan = vlan_dict.get('private-vlan',None)
        else:
            self.private_vlan = None
            vlan_dict['private-vlan'] = None

        if 'learning' in vlan_dict:
            self.learning = vlan_dict.get('learning',None)
        else:
            self.learning = None
            vlan_dict['learning'] = None

        if 'rspan-mode' in vlan_dict:
            self.rspan_mode = vlan_dict.get('rspan-mode',None)
        else:
            self.rspan_mode = None
            vlan_dict['rspan-mode'] = None

        if 'igmp-snooping' in vlan_dict:
            self.igmp_snooping = vlan_dict.get('igmp-snooping',None)
        else:
            self.igmp_snooping = None
            vlan_dict['igmp-snooping'] = None

        if 'mld-snooping' in vlan_dict:
            self.igmp_snooping = vlan_dict.get('mld-snooping',None)
        else:
            self.mld_snooping = None
            vlan_dict['mld-snooping'] = None

        if 'mld-snooping-fast-leave' in vlan_dict:
            self.mld_snooping_fast_leave = vlan_dict.get('mld-snooping-fast-leave',None) 
        else:
            self.mld_snooping_fast_leave = None
            vlan_dict['mld-snooping-fast-leave'] = None

        if 'mld-snooping-querier' in vlan_dict:
            self.mld_snooping_querier = vlan_dict.get('mld-snooping-querier',None)
        else:
            self.mld_snooping_querier = None
            vlan_dict['mld-snooping-querier'] = None

        if 'mld-snooping-querier-addr' in vlan_dict:
            self.mld_snooping_querier_addr = vlan_dict.get('mld-snooping-querier-addr',None)
        else:
            self.mld_snooping_querier_addr = None
            vlan_dict['mld-snooping-querier-addr'] = None

        if 'mld-snooping-proxy' in vlan_dict:
            self.mld_snooping_proxy = vlan_dict.get('mld-snooping-proxy',None)
        else:
            self.mld_snooping_proxy = None
            vlan_dict['mld-snooping-proxy'] = None

        if 'mld-snooping-static-group' in vlan_dict:
            self.mld_snooping_static_group = vlan_dict.get('mld-snooping-static-group',None) 
        else:
            self.mld_snooping_static_group = None
            vlan_dict['mld-snooping-static-group'] = None

        if 'dhcp-snooping' in vlan_dict:
            self.dhcp_snooping = vlan_dict.get('dhcp-snooping',None) 
        else:
            self.dhcp_snooping = None
            vlan_dict['dhcp-snooping'] = None

        if 'dhcp6-snooping' in vlan_dict:
            self.dhcp6_snooping = vlan_dict.get('dhcp6-snooping',None) 
        else:
            self.dhcp6_snooping = None
            vlan_dict['dhcp6-snooping'] = None

        if 'member-by-mac' in vlan_dict:
            self.member_by_mac = vlan_dict.get('member-by-mac',None)
        else:
            self.member_by_mac = None
            vlan_dict['member-by-mac'] = None

        if 'member-by-ipv4' in vlan_dict:
            self.member_by_ipv4 = vlan_dict.get('member-by-ipv4',None)
        else:
            self.member_by_ipv4 = None
            vlan_dict['member-by-ipv4'] = None

        if 'member-by-proto' in vlan_dict:
            self.member_by_proto = vlan_dict.get('member-by-proto',None)
        else:
            self.member_by_proto = None
            vlan_dict['member-by-proto'] = None

        self.config_dict = vlan_dict

    def print_sw_vlan(self):
        printr("self.id = {}".format(self.id))
        printr("self.private_vlan = {}".format(self.private_vlan))
        printr("self.learning = {}".format(self.learning))
        printr("self.rspan_mode = {}".format(self.rspan_mode))
        printr("self.igmp_snooping ={}".format(self.igmp_snooping))
        printr("self.mld_snooping = {}".format(self.mld_snooping))
        printr("self.mld_snooping_fast_leave = {}".format(self.mld_snooping_fast_leave))
        printr("self.mld_snooping_querier = {}".format(self.mld_snooping_querier)) 
        printr("self.mld_snooping_querier_addr = {}".format(self.mld_snooping_querier_addr))
        printr("self.mld_snooping_proxy = {}".format(self.mld_snooping_proxy)) 
        printr("self.mld_snooping_static_group = {}".format(self.mld_snooping_static_group)) 
        printr("self.dhcp_snooping = {}".format(self.dhcp_snooping)) 
        printr("self.dhcp6_snooping = {}".format(self.dhcp6_snooping))
        printr("self.member_by_mac = {}".format(self.member_by_mac))
        printr("self.member_by_ipv4 = {}".format(self.member_by_ipv4))
        printr("self.member_by_proto = {}".format(self.member_by_proto))

         
class lldp_class():
    def __init__(self):
        self.type = None
        self.local_port = None
        self.status = None
        self.ttl =  None
        self.neighbor = None
        self.capability = None
        self.med_type = None
        self.remote_port = None
         
    def __repr__(self):
        return '{self.__class__.__name__}(fsw obj)'.format(self=self)


    def __str__(self):
        return '{self.__class__.__name__}:{self.local_port}, {self.neighbor}, {self.med_type},{self.remote_port'.format(self=self)

    def parse_stats(self,items):
        self.local_port = items[0]
        self.tx = items[1]
        self.rx = items[2]
        self.discard = items[3]
        self.added = items[4]
        self.neighbor_deleted = items[5]
        self.aged_out = items[6]
        self.unknow_tlvs = items[7]

    def print_lldp(self):
        printr("type = {}".format(self.type))
        printr("local_port = {}".format(self.local_port))
        printr("med_type = {}".format(self.med_type))
        printr("capability = {}".format(self.capability))
        printr("remote_port = {}".format(self.remote_port))
        printr("status = {}".format(self.status))


class fortisw():
    def __init__(self,instance):
        self.instance = instance 
        self.name = None
        self.user = None
        self.password = None
        self.console = None
        self.port = None
        self.telnet = None
        self.lldp_obj_list = None
        self.lldp_dict_list = None
        self.switch_ports = []
        self.tpid = None
        self.sw_vlans = []

    def __repr__(self):
        return '{self.__class__.__name__}({self.instance}):{self.name}'.format(self=self)

    def __str__(self):
        return '{self.__class__.__name__}:{self.name}, {self.console}, {self.port}'.format(self=self)

    #Portname    Status   Device-name                 TTL   Capability  MED-type  Port-ID 
    # port17      Up       S448DP3X17000253            120   BR          -         port17
    # port17      Up       S448DN3X15000026            120   BR          Network   port18


    def find_vlan_config(self,*args,**kwargs):
        k = kwargs['key']
        v = kwargs['value']
        vlan_id = kwargs['vlan']

        for vlan_obj in self.sw_vlans:
            if vlan_obj.id == vlan_id or vlan_id in vlan_obj.id:
                if vlan_obj.config_dict[k] == None:
                    return False
                elif vlan_obj.config_dict[k] == v or v in vlan_obj.config_dict[k]:
                    return True
                else:
                    return False
        return False


    def update_switch_vlan(self,get_output):
        if type(get_output) == dict:
            output = get_output
        else:
            output = self.CollectShowCmdRobot(get_output)
            printr(output)
        sw_vlan = switch_vlan(output)
        self.sw_vlans = []
        self.sw_vlans.append(sw_vlan)

    def update_lldp_stats(self,stats):
        # printr(stats)
        port_found = False
        lldp_found = False
        for line in stats:
            if "port" in line:
                items = line.split()
        if len(items) == 0:
            return False
        port_name = items[0]
        for port in self.switch_ports:
            if port_name == port.name:
                port_found = True
                for lldp_obj in self.lldp_obj_list:
                    if port.name == lldp_obj.local_port:
                        port.lldp_neighbor = lldp_obj
                        lldp_found = True
                        break
        if port_found and lldp_found:
            port.lldp_neighbor.parse_stats(items)
        else:
            port = port_class(port_name)
            lldp = lldp_class()
            port.lldp_neighbor = lldp
            port.lldp_neighbor.parse_stats(items)
        return port.lldp_neighbor

    def update_port_config(self,port_name,output):
        # printr("Enter update_port_config")
        port= port_class(port_name)
        port.parse_port_config(output)
        return port.allow_vlans

    def update_switch_config(self,output):
        if output == None or len(output) == 0:
            return None
        try:
            for line in output:
                if "fortilink-p2p-tpid" in line:
                    regex = r"0[xX][0-9a-fA-F]+"
                    matched = re.search(regex,line)
                    if matched: 
                        self.tpid = matched.group()
                        return self.tpid
        except Exception as e:
            return None
        return None

    def switch_commands(self,cmd):
        #printr("========== DiscoveryLLDP starts here ===========")
        result = self.ShowCmd(cmd)
        printr(result)
        return result

    def parse_lldp(self,output):
        lldp_obj_list = []
        lldp_dict_list = []
        printr(output)
        for line in output:
            if "Portname" in line and  "Status" in line and "Device-name" in line:
                items = line.split()
                continue
            if " Up " in line:
                lldp_dict = {k:v for k, v in zip(items,line.split())}
                # printr(lldp_dict)
                if lldp_dict["Device-name"] == "-" or lldp_dict["Capability"] == "-":
                    pass
                else:
                    lldp = lldp_class()
                    lldp.local_port = lldp_dict["Portname"]
                    lldp.status = lldp_dict["Status"]
                    lldp.ttl = lldp_dict["TTL"]
                    lldp.neighbor = lldp_dict["Device-name"]
                    lldp.capability = lldp_dict["Capability"]
                    if lldp_dict["MED-type"] == "-":
                        lldp.med_type = "p2p".encode('utf-8')
                        lldp_dict["MED-type"] = "p2p".encode('utf-8')
                    else:
                        lldp.med_type = lldp_dict["MED-type"]
                    lldp.remote_port = lldp_dict["Port-ID"]
                    lldp_obj_list.append(lldp)
                    lldp_dict_list.append(lldp_dict)
        self.lldp_dict_list = lldp_dict_list
        self.lldp_obj_list = lldp_obj_list
        printr(self.lldp_dict_list)
         

    # def parse_lldp_robot(self,output):
    #     lldp_neighbor_list = []
    #     for line in output:
    #         if "Portname" in line and  "Status" in line and "Device-name" in line:
    #             items = line.split()
    #             continue
    #         if " Up " in line:
    #             lldp_dict = {k:v for k, v in zip(items,line.split())}
    #             if lldp_dict["Device-name"] == '-':
    #                 continue
    #             if lldp_dict["MED-type"] == "-":
    #                 lldp_dict["MED-type"] = "p2p".encode('utf-8')
    #             printr(lldp_dict)
    #             lldp_neighbor_list.append(lldp_dict)
    #     self.lldp_neighbors_dict = lldp_neighbor_list
    #     printr(self.lldp_neighbors_dict)
    #     return lldp_neighbor_list

    def discovery_lldp(self):
        ###################### debug ############################
        result = """
        S424DP3X16000238 # 

        2020-07-12 17:36:29:S424DP3X16000238=get switch lldp neighbors-summary
            

        Capability codes:
            R:Router, B:Bridge, T:Telephone, C:DOCSIS Cable Device
            W:WLAN Access Point, P:Repeater, S:Station, O:Other
        MED type codes:
            Generic:Generic Endpoint (Class 1), Media:Media Endpoint (Class 2)
            Comms:Communications Endpoint (Class 3), Network:Network Connectivity Device

          Portname    Status   Device-name                 TTL   Capability  MED-type  Port-ID
          __________  _______  __________________________  ____  __________  ________  _______
          port1       Up       -                           -     -           -         -
          port2       Down     -                           -     -           -         -
          port3       Down     -                           -     -           -         -
          port4       Down     -                           -     -           -         -
          port5       Down     -                           -     -           -         -
          port6       Down     -                           -     -           -         -
          port7       Down     -                           -     -           -         -
          port8       Down     -                           -     -           -         -
          port9       Down     -                           -     -           -         -
          port10      Down     -                           -     -           -         -
          port11      Down     -                           -     -           -         -
          port12      Down     -                           -     -           -         -
          port13      Down     -                           -     -           -         -
          port14      Down     -                           -     -           -         -
          port15      Down     -                           -     -           -         -
          port16      Down     -                           -     -           -         -
          port17      Down     -                           -     -           -         -
          port18      Down     -                           -     -           -         -
          port19      Down     -                           -     -           -         -
          port20      Down     -                           -     -           -         -
          port21      Down     -                           -     -           -         -
          port22      Down     -                           -     -           -         -
          port23      Up       S224EPTF19000002            120   BR          -         port23
          port24      Down     -                           -     -           -         -
          port25      Down     -                           -     -           -         -
          port26      Down     -                           -     -           -         -

        S424DP3X16000238 # 


        """
        b= result.split("\n")
        result = [x.encode('utf-8').strip() for x in b if x.strip()]        
        printr("========== DiscoveryLLDP starts here ===========")
        # result = self.ShowCmd("get switch lldp neighbors-summary")
        printr(result)
        ###################### debug ############################
        self.parse_lldp(result)

    def DiscoveryLLDPRobot(self,output):
        # printr("========== Debug: DiscoveryLLDPRobot starts here ===========")
        # printr(output)
        self.parse_lldp(output)
        # printr("========== Debug: DiscoveryLLDPRobot after parse_lldp method")
        #printr(self.lldp_neighbors)
         
     

    def CollectShowCmdRobot(self,output,**kwargs):
        # printr("Entering collect_show_cmd")
        # printr(output)
        #string coming from Robot is unicode. So split should NOT use b'. To make things worse in this
        #3to2 transformation, need to be more careful.  
        #out_list = output.split(b'\r\n')
        out_str_list = []
        
        out_list = output.split('\r\n')
        encoding = 'utf-8'
        for o in out_list:
            o_str = o.strip()
            #o_str = o.decode(encoding).strip(' ')
            o_str = o_str.encode(encoding).strip()
            if o_str:
                out_str_list.append(o_str)
        #printr(out_str_list)
        return out_str_list

    def ClearLine(self):
        status = clear_console_line(self.console,str(self.port),login_pwd='Fortinet123!', exec_pwd='Fortinet123!', prompt='#')
        printr(status['status'])
        if status['status'] != 0:
            printr('unable clear console port {}:{}'.format(self.console,self.port))
            return False
        else:
            printr('Cleared console port {}:{}'.format(self.console,self.port))
            return True
         
    def find_p2p_port(self):
        #printr("========= Enter find_p2p_port () =============")
        for n in self.lldp_obj_list:
            #printr("n.med_type = {}".format(n.med_type))
            if n.med_type == "p2p":
                return (True, n.local_port)
        return (False, None)

    def FindP2pPort(self):
        Network = False
        P2P = False
        p2p_num = 0
        net_port = None
        p2p_port = None
        port_set = set()
        #printr("========= Enter FindP2pPort () =============")
        for n in self.lldp_obj_list:
            n.print_lldp()
            if n.capability == "-" or n.neighbor == "-":
                continue
            if n.med_type == "Network" :
                Network = True
                # printr("------------Found network port")
                # printr(n.local_port)
                net_port = n.local_port
                port_set.add(n.local_port)
            if n.med_type == "p2p":
                P2P = True
                p2p_num += 1
                p2p_port = n.local_port
                port_set.add(n.local_port)
                # printr("------------Found p2p port")
                # printr(n.local_port)
        ########## DEBUG ######################
        printr("p2p_num = {}".format(p2p_num))
        printr("Network = {}".format(Network))
        printr("P2P = {}".format(P2P))
        ######### DEBUG #######################
        if Network and P2P and net_port == p2p_port: 
            return (True,p2p_port)
        elif P2P and p2p_num == 2 and len(port_set) == 1:
            return (True,p2p_port)
        else:
            return (False, None)
   
    # def FindP2pPort(self):
    #     #printr("========= Enter FindP2pPort () =============")
    #     for n in self.lldp_obj_list:
    #         if n.med_type == "p2p" and len(self.lldp_obj_list) > 2:
    #             printr("------------Found p2p port")
    #             printr(n.local_port)
    #             return (True, n.local_port)
    #     return (False,None)

    def FindNetworkPort(self):
        Network = False
        P2P = False
        p2p_num = 0
        net_num = 0
        net_port = None
        p2p_port = None
        #printr("========= Enter FindP2pPort () =============")
        for n in self.lldp_obj_list:
            if n.capability == "-":
                continue
            if n.med_type == "Network" :
                Network = True
                # printr("------------Found network port")
                # printr(n.local_port) 
                net_port = n.local_port
                net_num += 1  
            if n.med_type == "p2p":
                P2P = True
                p2p_num += 1
                p2p_port = n.local_port
                # printr("------------Found p2p port")
                # printr(n.local_port)
        ########## DEBUG ######################
        printr("p2p_num = {}".format(p2p_num))
        printr("Network Port ? = {}".format(Network))
        printr("P2P Port ? = {}".format(P2P))
        ######### DEBUG #######################
        if Network and P2P and net_port == p2p_port: 
            return (True,net_port)
        elif P2P and p2p_num == 1:
            return (True,p2p_port)
        elif P2P and p2p_num == 2:
            return (True,p2p_port)
        elif Network and net_num == 1:
            return (True,net_port)

        else:
            return (False, None)

    # def FindP2pPortDict(self):
    #     # printr("========= Enter find_ptp_rebot () =============")
    #     for n in self.lldp_dict_list:
    #         printr("loop through.......")
    #         if n["MED-type"] == "p2p":
    #             # printr("------------Found p2p port")
    #             # printr(n["Portname"])
    #             return (True,n["Portname"])
    #             #return True
    #     return (False,None)

    def UpdateSwInfo(self,name,user,password,console,port):
        self.name = name
        self.user = user
        self.password = password
        self.console = console
        self.port = port
        printr("Switch name = {}, user name = {}, password={},console ip= {}, console port = {}".format(self.name,self.user,self.password,self.console,self.port))

    def RunTest(self):
        printr("This is a test of Fortiswitch class")

    def ShowDeviceInfo(self):
        printr("Switch name = {}, user name = {}, password={},console ip= {}, console port = {}".format(self.name,self.user,self.password,self.console,self.port))

    def Telnet(self):
        # ip = "10.105.50.3"
        # line = "2057"
        # ip="10.105.152.2"
        # line="2083"
        self.ClearLine()
        self.telnet = TelnetConsole(self.console,self.port)

    def VerifyLldpNeighbor(self):
        pass

    def ShowCmd(self,cmd):
        output = switch_show_cmd(self.telnet,cmd)
        return output

class fortigate():
    def __init__(self,instance):
        self.instance = instance 
        self.name = None
        self.user = None
        self.password = None
        self.console = None
        self.port = None
        self.telnet = None

    def __repr__(self):
        return '{self.__class__.__name__}({self.instance}):{self.name}'.format(self=self)

    def __str__(self):
        return '{self.__class__.__name__}:{self.name}, {self.console}, {self.port}'.format(self=self)


    def GetLldp(self):
        self.collect_show_cmd("get switch lldp summary")

    def CollectShowCmdRobot(self,output,**kwargs):
        # printr("Entering collect_show_cmd")
        # printr(output)
        #string coming from Robot is unicode. So split should not use b'. To make things worse in this
        #3to2 transformation, need to be more careful.  
        #out_list = output.split(b'\r\n')
        out_list = output.split('\r\n')
        encoding = 'utf-8'
        out_str_list = []
        for o in out_list:
            o_str = o.strip()
            #o_str = o.decode(encoding).strip(' ')
            o_str = o_str.encode(encoding).strip()
            if o_str:
                out_str_list.append(o_str)
             
        #printr(out_str_list)
        return out_str_list

    def ClearLine(self):
        status = clear_console_line(self.console,str(self.port),login_pwd='Fortinet123!', exec_pwd='Fortinet123!', prompt='#')
        printr(status['status'])
        if status['status'] != 0:
            printr('unable clear console port {}:{}'.format(self.console,self.port))
            return False
        else:
            printr('Cleared console port {}:{}'.format(self.console,self.port))
            return True

    def UpdateSwInfo(self,name,user,password,console,port):
        self.name = name
        self.user = user
        self.password = password
        self.console = console
        self.port = port
        printr("Switch name = {}, user name = {}, password={},console ip= {}, console port = {}".format(self.name,self.user,self.password,self.console,self.port))

    def Telnet(self):
        ip = "10.105.50.3"
        line = "2057"
        # ip="10.105.152.2"
        # line="2083"
        self.ClearLine()
        self.telnet = TelnetConsole(self.console,self.port)

    def ShowCmd(self,cmd):
        output = switch_show_cmd(self.telnet,cmd)
        return output

    def RunTest(self):
        printr("This is a test of Fortigate class")

    def ShowDeviceInfo(self):
        printr("Switch name = {}, user name = {}, password={},console ip= {}, console port = {}".format(self.name,self.user,self.password,self.console,self.port))


def verify_ptp_robot(fsw):
    # printr("========= Enter find_ptp_rebot () =============")
    for n in fsw.lldp_neighbors_dict:
        printr("loop through.......")
        if n["MED-type"] == "p2p":
            printr("------------Found p2p port")
            return True 
    return False

def find_p2p_port(fsw):
    # printr("========= Enter find_p2p_port () =============")
    for n in fsw.lldp_neighbors:
        if n.med_type == "p2p":
            return (True, n.local_port)
    return (False,None)

def testing(*args,**kwargs):
   name = kwargs["name"]
   age = kwargs["age"]
   printr("testing")
   printr("testing name = {},age={}".format(name,age))

   b = {"name":"mike","age":14,"location":"china"}
   a = "mike"
   printr("{} is a good man".format(a))

   for k,v in b.items():
       printr(k,v)
   return a

def transform_robot_output(output,**kwargs):
    # printr("Entering collect_show_cmd")
    # printr(output)
    #string coming from Robot is unicode. So split should not use b'. To make things worse in this
    #3to2 transformation, need to be more careful.  
    #out_list = output.split(b'\r\n')
    out_list = output.split('\r\n')
    encoding = 'utf-8'
    out_str_list = []
    for o in out_list:
        o_str = o.strip()
        print("o_str = ".format(o_str))
        #o_str = o.decode(encoding).strip(' ')
        o_str = o_str.encode(encoding).strip()
        if o_str:
            out_str_list.append(o_str)
         
    #printr(out_str_list)
    return out_str_list

def robot_2_python(word):
    if type(word) is list:
        return word
    if type(word) is int:
        return str(word).encode('utf-8')
    return str(word.strip().encode('utf-8').replace('"',''))
      
def verify_tpid_config(*args, **kwargs):
    output = kwargs['output']
    state = kwargs["state"]
    try:
        output_list = transform_robot_output(output)
    except Exception as e:
        return False

    state = robot_2_python(state)

    if state == "disable":
        for line in output_list:
            if "fortilink-p2p-tpid" in line:
                return False
        return True
    if state == "enable":
        for line in output_list:
            if "fortilink-p2p-tpid" in line:
                return True
        return False

def verify_p2p_config(*args,**kwargs):
    output = kwargs['output']
    state = kwargs["state"]
    output_list = transform_robot_output(output)

    printr("debug: state = {}".format(repr(state)))
    state = robot_2_python(state)
    printr("debug: state = {}".format(repr(state)))
    if  state == "disable":
        for line in output_list:
            if "portlink-p2p" in line:
                return False
        return True
    if state == "enable":
        for line in output_list:
            if state in line:
                return True
        return False

def verify_config_key_value(*args, **kwargs):
    sampple_config = """
    1048D-R4-40 # show switch interface port2
    config switch interface
    edit "port2"
        set allowed-vlans 1-2000
        set auto-discovery-fortilink enable
        set snmp-index 2
    next
    end

    """
    output = kwargs['output']
    check_item = kwargs['key']
    output_list = transform_robot_output(output)
    for line in output_list:
        if check_item in line:
            return True 

    return False

def verify_commands_output_keys(*args,**kwargs):
    sample = """
    FS1D483Z16000018 # get switch mld-snooping globals 
    aging-time          : 30
    leave-response-timeout: 10
    query-interval      : 125

    FS1D483Z16000018 #
    """
    output = kwargs['output']
    output_list = transform_robot_output(output)

    total = len(args)
    printr("args = {},total number of args = {}".format(args,total))
    counter = 0
    for item in args:
        printr("args item = {}".format(item))
        for line in output_list:
            if item in line:
                counter += 1
                break

    if total == counter:
        return True
    else:
        return False


def verify_get_key_value(*args, **kwargs):
    sampple_config = """
    1048D-R4-40 (global) # get
    auto-fortilink-discovery: enable
    auto-isl            : enable
    auto-isl-port-group : 0
    dhcp-snooping-database-export: disable
    dmi-global-all      : enable
    flapguard-retain-trigger: disable
    flood-unknown-multicast: disable
    forti-trunk-dmac    : 02:80:c2:00:00:02
    ip-mac-binding      : disable
    loop-guard-tx-interval: 3
    mac-aging-interval  : 300
    max-path-in-ecmp-group: 8
    mclag-igmpsnooping-aware: disable
    mclag-peer-info-timeout: 60
    mclag-port-base     : 0
    mclag-split-brain-detect: disable
    mclag-stp-aware     : enable
    name                : (null)
    packet-buffer-mode  : store-forward
    port-security:
        link-down-auth      : set-unauth
        mab-reauth          : disable
        max-reauth-attempt  : 0
        quarantine-vlan     : enable
        reauth-period       : 60
        tx-period           : 30
    trunk-hash-mode     : default
    trunk-hash-unicast-src-port: disable
    trunk-hash-unkunicast-src-dst: enable
    virtual-wire-tpid   : 0xdee5
    """

    output = kwargs['output']
    key = kwargs['key']
    value = kwargs['value']
    if type(output) == dict:
        printr("output = {},key={},value={}".format(output,key,value))
        if output[key] == value or value in output[key]:
            return True
        else:
            return False
    else:
        output_list = transform_robot_output(output)
        for line in output_list:
            if key in line:
                k,v = line.split(":")
                if value == v.strip() or int(value) == int(v.strip()):
                    return True
        return False

def verify_config_lines(*args, **kwargs):
    output = kwargs['output']
    configs = args
    output_list = transform_robot_output(output)

    results = []
    for config in configs:
        for line in output_list:
            if config in line:
                results.append(True)
                break

    if len(results) == len(configs):
        return True
    else:
        return False
        

def verify_switch_interface_config(*args, **kwargs):
    sampple_config = """
    1048D-R4-40 # show switch interface port2
    config switch interface
    edit "port2"
        set allowed-vlans 1-2000
        set auto-discovery-fortilink enable
        set snmp-index 2
    next
    end

    """
    output = kwargs['output']
    if "vlan" in kwargs:
        allowed_vlan = kwargs["vlan"]
    else:
        allowed_vlan = None

    output_list = transform_robot_output(output)
    for line in output_list:
        if allowed_vlan in line:
            return True 

    return False


def verify_vlan_mld_config(*args,**kwargs):
    sample_config = """
    3032E-R7-19 # show switch vlan 10
    config switch vlan
        edit 10
            set mld-snooping enable
            set mld-snooping-proxy enable
                config mld-snooping-static-group
                edit "static-group-1"
                    set mcast-addr ff3e::10
                        set members "port1"
        next
    end
    """
    if 'output' in kwargs:
        output = kwargs['output']
    else:
        output = "Null"

    if 'state' in kwargs:
        state = kwargs["state"]
    else:
        state = "Null"

    if 'vlan' in kwargs:
        vlan = kwargs["vlan"]
    else:
        vlan = "Null"

    if "proxy" in kwargs:
        proxy = kwargs['proxy']
    else:
        proxy = "Null"

    if "querier" in kwargs:
        querier = kwargs['querier']
    else:
        querier = "Null"

    if "querier_addr" in kwargs:
        querier_addr = kwargs["querier_addr"]
    else:
        querier_addr = "Null"

    if "static_group" in kwargs:
        static_group = kwargs["static_group"]
    else:
        static_group = "Null"

    if "member" in kwargs:
        member = kwargs["member"]
    else:
        member = "Null"

    if "members" in kwargs:
        members = kwargs["members"]
    else:
        members = "Null"

    if "group_list" in kwargs:
        group_list = kwargs["group_list"]
    else:
        group_list = "Null"

    if "config_groups_list" in kwargs:
        config_groups_list = kwargs["config_groups_list"]
    else:
        config_groups_list = "Null"


    output_list = transform_robot_output(output)

    state = robot_2_python(state)
    vlan = robot_2_python(vlan)
    proxy = robot_2_python(proxy)
    querier = robot_2_python(querier)
    querier_addr = robot_2_python(querier_addr)
    static_group = robot_2_python(static_group)
    members= robot_2_python(members)
    member= robot_2_python(member)
    group_list= robot_2_python(group_list)
    config_groups_list= robot_2_python(config_groups_list)

    printr("debug: state = {}".format(repr(state)))
    printr("debug: vlan = {}".format(repr(vlan)))
    printr("debug: porxy = {}".format(repr(proxy)))
    printr("debug: querier = {}".format(repr(querier)))
    printr("debug: querier_addr = {}".format(repr(querier_addr)))
    printr("debug: static_group = {}".format(repr(static_group)))
    printr("debug: member = {}".format(repr(member)))
    printr("debug: members = {}".format(repr(members)))
    printr("debug: group_list = {}".format(repr(group_list)))
    printr("debug: config_groups_list = {}".format(repr(config_groups_list)))


    try:
        if state == "enable": 
            for line in output_list:
                if "set mld-snooping enable" in line:
                    return True
            return False
        elif state == "enable" and querier  == "disable":
            for line in output_list:
                if "set mld-snooping-querier enable" in line:
                    return False
            return True
        elif state == "enable" and querier == "enable":
            for line in output_list:
                if "set mld-snooping-querier enable" in line:
                    return True
            return False
        elif state == "disable" and querier == "enable":
            for line in output_list:
                if "set mld-snooping-querier enable" in line:
                    return False
            return True
        elif querier == "enable" and querier_addr != "Null":
            printr("I am here where querier = enable && querier_addr != Null")
            for line in output_list:
                printr(line)
                if querier_addr in line:
                    return True
            return False
        elif querier == "disable" and querier_addr != "Null":
            for line in output_list:
                if querier_addr in line:
                    return False
            return True
        elif static_group != "Null" and  member == "Null" :
            for line in output_list:
                if static_group in line:
                    return True
            return False
        elif static_group != "Null" and  member != "Null" :
            group_found = False
            for line in output_list:
                if static_group in line:
                   group_found = True
            member_found = False
            for line in output_list:
                if member in line:
                    member_found = True
            if group_found == True and member_found == True: 
                return True
            else:
                return False
        elif static_group != "Null" and  members != "Null" :
            group_found = False
            for line in output_list:
                if static_group in line:
                   group_found = True
            members_found = []
            for line in output_list:
                for m in line:
                    if m in line:
                        members_found.append(True)
            if group_found == True and len(members_found) == len(members): 
                return True
            else:
                return False

        elif group_list != "Null":
            group_match = []
            for group in group_list:
                for line in output_list:
                    if group in line:
                        group_match.append(True)
            if len(group_match) == len(group_list):
                return True
            else:
                return False
        elif config_groups_list != "Null":
            group_match = []
            for group in config_groups_list:
                for line in output_list:
                    if group in line:
                        group_match.append(True)
            if len(group_match) == len(config_groups_list):
                return True
            else:
                return False

    except Exception as e:
        pass

    return False

def verify_two_output_list(*args,**kwargs):
    list1 = args[0]
    list2 = args[1]

    for i,j in zip(list1,list2):
        if i != j:
            return False

    return True

def verify_static_group(*args, **kwargs):
    sample = """
    FS1D483Z16000018 # get switch mld-snooping static-group


    VLAN ID   Group-Name       Multicast-addr               Member-interface
     _______   ______________   ______________               ________________
    20        static-group-1   ff3e:0:0:0:0:0:0:10                          port7
    """
    key = kwargs['key']
    value = kwargs['value']
    output = kwargs['output']

    key = robot_2_python(key)
    value = robot_2_python(value)
    output_list = transform_robot_output(output)

    printr("key = {}".format(repr(key)))
    printr("value = {}".format(repr(value)))

    if "number" in key:
        count = 0
        for line in output_list:
            if "static-group" in line:
                count += 1

        if int(value) == count:
            return True
        else:
            return False




def verify_mld_config(*args,**kwargs):
    sample_output_enable = """
    3032E-R7-19 # get switch mld-snooping status
    MLD-SNOOPING enabled vlans:

    VLAN     PROXY        QUERIER VERSION
    ----     -----        ---------------
    10       DISABLED     MLDv1


    Max multicast snooping groups 1022

    Total MLD groups 0 (Learned 0, Static 0)
    Total IGMP groups 0 (Learned 0, Static 0)

    Remaining allowed mcast snooping groups: 1022
    """

    sample_output_disable =  """
    3032E-R7-19 # get switch mld-snooping status
    MLD-SNOOPING enabled vlans:

    VLAN     PROXY        QUERIER VERSION
    ----     -----        ---------------


    Max multicast snooping groups 1022

    Total MLD groups 0 (Learned 0, Static 0)
    Total IGMP groups 0 (Learned 0, Static 0)

    Remaining allowed mcast snooping groups: 1022
        """

    sampe_output_proxy = """

    3032E-R7-19 # get switch mld-snooping status
    MLD-SNOOPING enabled vlans:

    VLAN     PROXY        QUERIER VERSION
    ----     -----        ---------------
    10       ENABLED      MLDv1


    Max multicast snooping groups 1022

    Total MLD groups 0 (Learned 0, Static 0)
    Total IGMP groups 0 (Learned 0, Static 0)

    Remaining allowed mcast snooping groups: 1022
    """
    output = kwargs['output']
    state = kwargs["state"]
    vlan = kwargs["vlan"]
    proxy = kwargs['proxy']
    output_list = transform_robot_output(output)

    state = robot_2_python(state)
    vlan = robot_2_python(vlan)
    proxy = robot_2_python(proxy)
    printr("debug: state = {}".format(repr(state)))
    printr("debug: vlan = {}".format(repr(vlan)))
    printr("debug: porxy = {}".format(repr(proxy)))
    for i in range(len(output_list)):
        if "---------------" in output_list[i]:
            target = output_list[i+1]
            break
    if state.upper() == "ENABLE" and vlan in target:
        if proxy.upper() == "DISABLE" and "DISABLED" in target:
            return True
        elif proxy.upper() == "ENABLE" and "ENABLED" in target:
            return True
        else: 
            return False

    if state.upper() == "DISABLE" and vlan in target:
        return False
    else:
        return True


def find_access_vlan(access_vlans,vlan):
    if vlan in access_vlans:
        return True
    return False

def verify_tpid_id(found,target):
    if found == None:
        return False
    if target in found:
        return True
    else:
        return False

def verify_storm_control(output):
    check_point_1 = False
    check_point_2 = False
    check_point_3 = False
    for line in output:
        if "storm-control-mode override" in line:
            check_point_1 = True
        elif "broadcast enable" in line:
            check_point_2 = True
        elif "rate 111" in line:
            check_point_3 = True

    if check_point_1 and check_point_2 and check_point_3:
        return True
    else:
        return False


def compare_lldp_stats(lldp1,lldp2): 
    # printr(int(lldp2.rx))
    # printr(int(lldp1.rx))
    # printr(int(lldp2.tx))
    # printr(int(lldp1.tx))
    if int(lldp2.rx) > int(lldp1.rx) and int(lldp2.tx) > int(lldp1.tx):
        return True
    else:
        return False

def stp_port_status(*args, **kwargs):
    stp_data = kwargs["data"]
    port_dut = kwargs["port"]
    role = kwargs["role"]
    for line in stp_data:
        if "FORWARDING" in line:
            items = line.split()
            port_name = items[0]
            if port_dut == port_name:
                role_line = items[4]
                if role_line.upper() == role.upper():
                    return True
    return False


def verify_pdu_counters(*args,**kwargs):
    sample_output = """
    FS1D483Z16000018 # diagnose switch pdu-counters list 
    primary CPU counters:
      packet receive error :        0
      Non-zero port counters:
      port1:
        LLDP packet                   :      128
        DHCP6 Packet                  :        6
        IGMP Query packet             :        6
        MLD Query packet              :       38
        MLDv1 Report packet           :       78
        MLD Done packet               :        6
      port2:
        STP packet                    :        3
        LLDP packet                   :      128
      port14:
        MLD Query packet              :       12

    """
    key = kwargs['key']
    value = kwargs['value']
    output = kwargs['output']

    key = robot_2_python(key)
    value = robot_2_python(value)
    output_list = transform_robot_output(output)

    printr("key = {}".format(repr(key)))
    printr("value = {}".format(repr(value)))

    k = None
    v = None
    for item in output_list:
        if key in item:
            k,v = [x.strip() for x in item.split(":")]
            printr("k,v = {},{}".format(repr(k),repr(v)))
            break 
    if v != None :
        if "MLDv1 Report packet" in key:
            if int(v) == int(value) or int(v) == int(value)/2 :
                return True
            else:
                return False
        elif "MLD Done packet" in key:
            if value != "any":
                if int(v) == int(value) or int(v) == int(value)*2 :
                    return True
            elif value == "any":
                if int(v) > 0:
                    return True
                else:
                    return False
    else:
        return None

def get_pdu_counters(*args,**kwargs):
    sample_output = """
    FS1D483Z16000018 # diagnose switch pdu-counters list 
    primary CPU counters:
      packet receive error :        0
      Non-zero port counters:
      port1:
        LLDP packet                   :      128
        DHCP6 Packet                  :        6
        IGMP Query packet             :        6
        MLD Query packet              :       38
        MLDv1 Report packet           :       78
        MLD Done packet               :        6
      port2:
        STP packet                    :        3
        LLDP packet                   :      128
      port14:
        MLD Query packet              :       12

    """
    key = kwargs['key']
    value = kwargs['value']
    output = kwargs['output']

    key = robot_2_python(key)
    value = robot_2_python(value)
    output_list = transform_robot_output(output)

    printr("key = {}".format(repr(key)))
    printr("value = {}".format(repr(value)))

    k = None
    v = None
    for item in output_list:
        if key in item:
            k,v = [x.strip() for x in item.split(":")]
            printr("k,v = {},{}".format(repr(k),repr(v)))
            return int(v)
    
    return None


def verify_mld_snooping_mrouter_port(*args,**kwargs):
    sample_output = """
    MLD-SNOOPING learned mcast-groups:
    port         VLAN    GROUP                    Age-timeout     MLD-Version
    port1            20      querier                  163         MLDv1
    port3            20      ff3e:0:0:0:0:1:1:6                       186         MLDv1
    port3            20      ff3e:0:0:0:0:1:1:5                       186         MLDv1
    port3            20      ff3e:0:0:0:0:1:1:4                       186         MLDv1
    port3            20      ff3e:0:0:0:0:1:1:3                       186         MLDv1
    port3            20      ff3e:0:0:0:0:1:1:2                       186         MLDv1
    port3            20      ff3e:0:0:0:0:1:1:1                       186         MLDv1
    port13           20      ff3e:0:0:0:0:1:1:6                       185         MLDv1
    port13           20      ff3e:0:0:0:0:1:1:5                       185         MLDv1
    port13           20      ff3e:0:0:0:0:1:1:4                       185         MLDv1
    port13           20      ff3e:0:0:0:0:1:1:3                       185         MLDv1
    port13           20      ff3e:0:0:0:0:1:1:2                       185         MLDv1
    port13           20      ff3e:0:0:0:0:1:1:1                       185         MLDv1
    port14           20      ff3e:0:0:0:0:1:1:6                       183         MLDv1
    port14           20      ff3e:0:0:0:0:1:1:5                       183         MLDv1
    port14           20      ff3e:0:0:0:0:1:1:4                       183         MLDv1
    port14           20      ff3e:0:0:0:0:1:1:3                       183         MLDv1
    port14           20      ff3e:0:0:0:0:1:1:2                       183         MLDv1
    port14           20      ff3e:0:0:0:0:1:1:1                       183         MLDv1

    Total MLD Hosts: 18
    """
    key = kwargs['key']
    value = kwargs['value']
    output = kwargs['output']

    key = robot_2_python(key)
    value = robot_2_python(value)
    output_list = transform_robot_output(output)

    printr("key = {}".format(repr(key)))
    printr("value = {}".format(repr(value)))

    if value == "any":
        for item in output_list:
            if key in item:
                return True
        return False
    else:
        count = 0
        for item in output_list:
            if key in item:
                count += 1
        printr("count = {}".format(repr(count)))
        if count == int(value):
            return True
        else:
            return False


def verify_mld_snooping_group(*args,**kwargs):
    sample_output = """
    MLD-SNOOPING learned mcast-groups:
    port         VLAN    GROUP                    Age-timeout     MLD-Version
    port1            20      querier                  163         MLDv1
    port3            20      ff3e:0:0:0:0:1:1:6                       186         MLDv1
    port3            20      ff3e:0:0:0:0:1:1:5                       186         MLDv1
    port3            20      ff3e:0:0:0:0:1:1:4                       186         MLDv1
    port3            20      ff3e:0:0:0:0:1:1:3                       186         MLDv1
    port3            20      ff3e:0:0:0:0:1:1:2                       186         MLDv1
    port3            20      ff3e:0:0:0:0:1:1:1                       186         MLDv1
    port13           20      ff3e:0:0:0:0:1:1:6                       185         MLDv1
    port13           20      ff3e:0:0:0:0:1:1:5                       185         MLDv1
    port13           20      ff3e:0:0:0:0:1:1:4                       185         MLDv1
    port13           20      ff3e:0:0:0:0:1:1:3                       185         MLDv1
    port13           20      ff3e:0:0:0:0:1:1:2                       185         MLDv1
    port13           20      ff3e:0:0:0:0:1:1:1                       185         MLDv1
    port14           20      ff3e:0:0:0:0:1:1:6                       183         MLDv1
    port14           20      ff3e:0:0:0:0:1:1:5                       183         MLDv1
    port14           20      ff3e:0:0:0:0:1:1:4                       183         MLDv1
    port14           20      ff3e:0:0:0:0:1:1:3                       183         MLDv1
    port14           20      ff3e:0:0:0:0:1:1:2                       183         MLDv1
    port14           20      ff3e:0:0:0:0:1:1:1                       183         MLDv1

    Total MLD Hosts: 18
    """
    key = kwargs['key']
    value = kwargs['value']
    output = kwargs['output']

    key = robot_2_python(key)
    value = robot_2_python(value)
    output_list = transform_robot_output(output)

    printr("key = {}".format(repr(key)))
    printr("value = {}".format(repr(value)))

    k = None
    v = None 
    for item in output_list:
        if key in item:
            #printr("debug: within loop item = {}".format(repr(item)))
            k,v = [x for x in item.split(":")]
            # k,v = [x.strip() for x in item.split(":")]
            #printr("k,v = {},{}".format(repr(k),repr(v)))
            break 
    if v != None:
        if int(v) == int(value):
            return True
        else:
            return False
    else:
        return False

def clear_lines(console_ip,port):
    status = clear_console_line(console_ip,str(port),login_pwd='fortinet123', exec_pwd='fortinet123', prompt='#')
    printr(status['status'])
    if status['status'] != 0:
        printr('unable clear console port {}:{}'.format(console_ip,port))
        return False
    else:
        printr('Cleared console port {}:{}'.format(console_ip,port))
        return True

def verify_system_performance(*args,**kwargs):
    sample = """
    CPU states: 0% user 10% system 14% nice 76% idle
    Memory states: 12% used
    Average network usage: 0 kbps in 1 minute, 0 kbps in 10 minutes, 0 kbps in 30 minutes
    Uptime: 1 days,  16 hours,  39 minutes
    """
    output = kwargs['output']

    output_list = transform_robot_output(output)

    cpu_regex = r'CPU states: ([0-9%]+) user ([0-9%]+) system ([0-9%]+) nice ([0-9%]+) idle'
    mem_regex = r'Memory states: ([0-9%]+) used'

    printr("key = {}".format(repr(output_list)))
    # printr("value = {}".format(repr(value)))

    for line in output_list:
        matched = re.match(cpu_regex,line)
        if matched:
            cpu_user = int(matched.group(1).strip("%"))/100
            printr("cpu_user = {}".format(repr(cpu_user)))
            cpu_sys =  int(matched.group(2).strip("%"))/100
            printr("cpu_sys = {}".format(repr(cpu_sys)))
            continue
        matched = re.match(mem_regex,line)
        if matched:
            mem_used = int(matched.group(1).strip("%"))/100
            printr("mem_used = {}".format(repr(mem_used)))

        for i in [cpu_user,cpu_sys,mem_used]:
            if i > 0.9:
                printr("cpu_user={},cpu_sys={},mem_used={}".format(cpu_user,cpu_sys,mem_used))
                return False

        return True


def find_packet_with_pattern(*args,**kwargs):
    packet = kwargs['packet']
    key = kwargs['key']
    pattern = kwargs['pattern']
    if "all" in kwargs:
        Count_all = True
    else:
        Count_all = False


    key = robot_2_python(key)
    pattern = robot_2_python(pattern)

    printr("key = {}".format(repr(key)))
    printr("pattern = {}".format(repr(pattern)))

    if key == "mcast_dst" and not Count_all:
        pattern_regex = pattern + "[0-9a-fA-F]+"
        mcast_regex = r"'display_name': 'Destination', 'value': '{}'".format(pattern_regex)
        printr("mcast_regex = {}".format(mcast_regex))
        matched = re.search(mcast_regex,str(packet))
        if matched:
            printr(matched.group())
            return True
        else:
            printr("Nothing matched")
            return False
    if key == "mcast_dst" and Count_all:
        pattern_regex = pattern + "[0-9a-fA-F]+"
        mcast_regex = r"'display_name': 'Destination', 'value': '{}'".format(pattern_regex)
        printr("mcast_regex = {}".format(mcast_regex))
        counter = 0
        matches = re.findall(mcast_regex,str(packet))
        if matches:
            for m in matches:
                printr(m)
                counter += 1
        return counter
    if key == "mcast_src" and pattern == "allzero" and Count_all:
        mcast_regex = r"'display_name': 'Source Host', 'value': '::'"
        counter = 0
        matches = re.findall(mcast_regex,str(packet))
        if matches:
            for m in matches:
                printr(m)
                counter += 1
        return counter

    if key == "mcast_src" and pattern == "link_local" and Count_all:
        pattern_regex = pattern + "[0-9a-fA-F]+"
        mcast_regex = r"'display_name': 'Source Host', 'value': 'fe80[:0-9a-fA-F]+'"
        printr("mcast_regex = {}".format(mcast_regex))
        counter = 0
        matches = re.findall(mcast_regex,str(packet))
        if matches:
            for m in matches:
                printr(m)
                counter += 1
        return counter

if __name__ == "__main__":
    testing(name="steve",age=30)
    # sw = fortisw()
    # sw.collect_show_cmd("this is a test")
    # ip="10.105.152.2"
    # line="2083"

    # ip="10.105.152.52"
    # line="23"
    #wait_with_timer(10)
    ip = "10.105.50.1"
    line = "2075"
    fsw = fortisw(1)
    fsw.console = ip
    fsw.port= line
    fsw.Telnet()

    fsw.discovery_lldp()
    result,port = fsw.FindP2pPort()
    printr("Find P2P Port result = {}".format(result))
    if result:
        printr("=============== P2P port  = {}".format(port))
    result,port = fsw.FindNetworkPort()
    printr("Find Network Port result = {}".format(result))
    if result:
        printr("=============== Network port  = {}".format(port))

    exit()
    output = fsw.switch_commands("show switch global")
    output = fsw.CollectShowCmdRobot(output)
    fsw.update_switch_config(output)
    exit()
    output = fsw.switch_commands("diagnose stp vlan list 10")
    result = stp_port_status(role="root",port="port17",data=output)
    print(result)
    exit()
    output = fsw.switch_commands("get switch lldp stat port17")
    lldp1 = fsw.update_lldp_stats(output)
    sleep(10)
    output = fsw.switch_commands("get switch lldp stats port17")
    lldp2 = fsw.update_lldp_stats(output)
    print(compare_lldp_stats(lldp1,lldp2))
    exit()
    output = fsw.switch_commands("show switch global")
    value = fsw.update_switch_config(output)
    print(verify_tpid_id(value,"0x8818"))
    exit(1)
    fsw.discovery_lldp()
    result,port = fsw.FindP2pPort()
    if result:
        printr("=============== P2P port  = {}".format(port))
    #pdb.set_trace()
     
    #ftg = fortigate(1)
    # ftg.Telnet()
    # ftg.ShowCmd("get switch lldp neighbors-summary")
    # log_with_time(ftg)
    # ftg.console = ip
    # ftg.port = line
    # ftg.ClearLine()

    # TelnetConsole(ip,line)

