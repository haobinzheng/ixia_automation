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
import yaml
from jinja2 import Environment, PackageLoader
from jinja2 import Template

from utils import *
from apc import *
import settings 
from test_process import * 
from common_lib import *
from common_codes import *
from cli_functions import *

class Router_BFD:   
    def __init__(self,*args,**kwargs):
        self.switch = args[0]
        self.dut = args[0]
        self.peer_list_v6 = None
        self.peer_list_v4 = None
        self.peers_v6 = self.discover_bfd6_neighbors()
        self.peers_v4 = self.discover_bfd4_neighbors()

    
    def discover_bfd6_neighbors(self):
        if self.switch.is_fortinet() == False:
            return None
        dut = self.switch
        neighbor_dict_list = self.get_bfd_neighbors(version="v6")
        neighbor_list = []
        for n in neighbor_dict_list:
            try: 
                neighbor = BFD_Peer(n)
                neighbor_list.append(neighbor)
            except:
                pass
        self.peer_list_v6 = neighbor_list
        return neighbor_list

    def discover_bfd4_neighbors(self):
        if self.switch.is_fortinet() == False:
            return None
        dut = self.switch
        neighbor_dict_list = self.get_bfd_neighbors(verson="v4")
        neighbor_list = []
        for n in neighbor_dict_list:
            neighbor = BFD_Peer(n)
            neighbor_list.append(neighbor)
        self.peer_list_v4 = neighbor_list
        return neighbor_list

    def counte_peers_v6(self):
        if self.switch.is_fortinet() == False:
            return
        total_count = 0
        up_count = 0
        down_count = 0
        down_peer_list = []
        for p in self.peer_list_v6:
            total_count += 1
            if p.status == "up":
                up_count += 1
            else:
                down_count += 1
                down_peer_list.append(p.peer)

        self.up_count = up_count
        self.down_count = down_count
        self.down_peer_list = down_peer_list
        self.total_count = total_count
        print(f" =============== BFD Checking IPv6 Peer Status for {self.switch.name} =======")
        print(f"    Total Number of Peer Found: {self.total_count}")
        print(f"    Total Number of Peer Up: {self.up_count}")
        print(f"    Total Number of Peer Down: {self.down_count}")
        print(f"    Peers Down: {self.down_peer_list}")

    def counte_peers_v4(self): #dont do v4 for now. the get router info bfd nei output is empty
        up_count = 0
        down_count = 0
        down_peer_list = []
        for p in self.peer_list_v4:
            if p.status == "up":
                up_count += 1
            else:
                down_count += 1
                down_peer_list.append(p.peer)

        self.up_count = up_count
        self.down_count = down_count
        self.down_peer_list = down_peer_list
        print(f" =============== BFD Checking IPv4 Peer Status for {self.switch.name} =======")
        print(f"    Total Number of Peer Up: self.up_count")
        print(f"    Total Number of Peer Down: self.down_count")
        print(f"    Peers Down: self.down_peer_list")

    def get_bfd_neighbors(self,*args,**kwargs):
        if self.switch.is_fortinet() == False:
            return

        if "version" in kwargs:
            ver = kwargs['version']
        else:
            ver = "v4"
        Info(f"==== {self.switch.name}: Discovering BFD Neighbors for {ver}")
        dut = self.switch.console
        if ver == "v6":
            result = collect_show_cmd(dut,"get router info6 bfd neighbor")
        else:
            result = collect_show_cmd(dut,"get router info bfd neighbor")
        new_peer = False
        peer_dict_list = []
        if result: 
            Info("=============== Collect bfd neighbor information again ================")
            if ver == "v6":
                result = collect_show_cmd(dut,"get router info6 bfd neighbor")
            else:
              result = collect_show_cmd(dut,"get router info bfd neighbor")
        for line in result:
            if "peer" in line and "multihop" in line and "local-address" in line:
                neighbor_dict = {}
                items = line.split()
                neighbor_dict["peer"] = items[1]
                neighbor_dict["local_address"] = items[4]
                new_peer = True
            elif new_peer and "ID" in line and "Remote" not in line:
                neighbor_dict["id"] = [i.strip() for i in line.split(":")][1]
            elif new_peer and "Remote ID" in line:
                neighbor_dict["remote_id"] = [i.strip() for i in line.split(":")][1]
            elif new_peer and "Ifp" in line:
                neighbor_dict["interface"] = [i.strip() for i in line.split(":")][1]
            elif new_peer and "Status" in line:
                neighbor_dict["status"] = [i.strip() for i in line.split(":")][1]
            elif new_peer and "Transmission interval" in line:  #this is the end of peer info
                print(f"{self.switch.name}: get_bfd_neighbors(): neighbor_dict={neighbor_dict}")
                peer_dict_list.append(neighbor_dict)
                new_peer = False # mark the end of the peer
        return peer_dict_list

class BFD_Peer:
    def __init__(self,*args,**kwargs):
        neighbor_dict = args[0]
        self.id = neighbor_dict["id"]
        self.peer = neighbor_dict["peer"]
        self.local_address = neighbor_dict["local_address"]
        self.remote_id = neighbor_dict["remote_id"]
        self.interface = neighbor_dict["interface"]
        self.status = neighbor_dict["status"]
     # 020-09-11 16:58:17 ::  peer 2001:2:2:2::2 multihop local-address 2001:6:6:6::6
     # 020-09-11 16:58:17 ::      ID: 251844542
     # 020-09-11 16:58:17 ::      Remote ID: 1561134723
     # 020-09-11 16:58:17 ::      Ifp : vlan1
     # 020-09-11 16:58:17 ::      Status: up
     # 020-09-11 16:58:17 ::      Uptime: 47 second(s)
     # 020-09-11 16:58:17 ::      Diagnostics: ok
     # 020-09-11 16:58:17 ::      Remote diagnostics: ok
     # 020-09-11 16:58:17 ::      Local timers:
     # 020-09-11 16:58:17 ::          Detection Multiplier: 3
     # 020-09-11 16:58:17 ::          Receive interval: 250ms
     # 020-09-11 16:58:17 ::          Transmission interval: 250ms
     # 020-09-11 16:58:17 ::      Remote timers:
     # 020-09-11 16:58:17 ::          Detection Multiplier: 3
     # 020-09-11 16:58:17 ::          Receive interval: 250ms
     # 020-09-11 16:58:17 ::          Transmission interval: 250ms

class BGP_networks:
    def __init__(self,*args,**kwargs):
        self.switches = args[0]
        self.routers = []
        for switch in self.switches:
            self.routers.append(switch.router_bgp)

    def switch_is_fortinet(self,router):
        if router.switch.platform == "fortinet":
            return True
        else:
            return False
    
    def ping_sweep_v6(self):
        num = len(self.switches)
        for i in range(num-1):
            for j in range(i+1,num):
                ping_ipv6(self.switches[i].console,ip=self.switches[j].loop0_ipv6.split("/")[0])

    def ping_sweep_v6_extensive(self,*args,**kwargs):
        if "skip" in kwargs:
            skip = kwargs['skip']
        else:
            skip = False

        if skip ==True:
            return 
        num = len(self.switches)
        for i in range(num-1):
            console = self.switches[i].console
            for j in range(i+1,num):
                for interface1,interface2 in zip(self.switches[i].sys_interfaces,self.switches[j].sys_interfaces):
                    ip_src = interface1.ipv6_2nd
                    ip_dst = interface2.ipv6_2nd
                    sw_src = self.switches[i].name
                    sw_dst = self.switches[j].name
                    interface_name = interface1.name
                    switch_name = self.switches[j].name
                    if interface_name == "mgmt":
                        continue
                    ping_ipv6(console,ip=ip_dst)
                    ping_ipv6_extensive(console=console, ip_src=ip_src,ip_dst = ip_dst,name=interface_name,sw_src=sw_src, sw_dst=sw_dst)
 
    def show_address_mappings(self):
        arp_list = []
        lloc_list = []
        for switch in self.switches:
            arp_list.append(switch.discover_sys_arp())
            lloc_list.append(switch.discover_ipv6_neighbors())
        print(arp_list)
        print(lloc_list)

        arp_mapping = {}
        lloc_mapping = {}
        for a in arp_list:
            arp_mapping.update(a)
        for a in lloc_list:
            lloc_mapping.update(a)

        print("==================== network wide ipv4 and link local address mapping =================")
        for k,v in arp_mapping.items():
            print(f"MAC Address: {k}")
            print(f"    IPv4 address: {v}")
            lloc = lloc_mapping[k]
            print(f"    Link Local Address: {lloc}")


    def show_summary(self):
        for router in self.routers:
            Info(f"----------------------{router.switch.name} -----------------------")
            router.show_bgp_summary()
            #router.check_neighbor_status()

    def show_summary_v6(self):
        for router in self.routers:
            router.show_bgp_summary_v6()
            Info(f"----------------------{router.switch.name} -----------------------")
            #router.check_bgp_neighbor_status_v6()

    def clear_bgp_config(self):
        for router in self.routers:
            router.clear_config()

   
    def build_ibgp_mesh_topo(self):
        for switch in self.switches:
            switch.router_ospf.neighbor_discovery()
            switch.router_bgp.update_ospf_neighbors()
            switch.router_bgp.config_ibgp_mesh_loopback()


    def build_bgp_peer_multi_hops(self,bgp1,as1,bgp2,as2):
        tprint(f"============== Configurating BGP peer between {bgp1.switch.name} AS = {as1} and {bgp2.switch.name} AS={as2} ")
        if bgp1.switch.is_fortinet():
            bgp_config = f"""
            config router bgp
                set as {as1}
                set router-id {bgp1.router_id }
            end
            config redistribute6 "connected"
             set status enable
            end
            """
            config_cmds_lines(bgp1.switch.console,bgp_config)
            bgp_config = f"""
            config router bgp
                config neighbor
                    edit {bgp2.switch.loop0_ipv6.split("/")[0]}
                        set remote-as {as2}
                        set ebgp-enforce-multihop enable
                        set ebgp-multihop-ttl 3
                        set update-source loop0
                    next
                end
            end
            """
            config_cmds_lines(bgp1.switch.console,bgp_config)

        if bgp2.switch.is_fortinet():
            bgp_config = f"""
            config router bgp
                set as {as2}
                set router-id {bgp2.router_id }
            end
            """
            config_cmds_lines(bgp2.switch.console,bgp_config)
            bgp_config = f"""
            config router bgp
                config neighbor
                    edit {bgp1.switch.loop0_ipv6.split("/")[0]}
                        set remote-as {as1}
                        set ebgp-enforce-multihop enable
                        set ebgp-multihop-ttl 3
                        set update-source loop0
                    next
                end
            end
            """
            config_cmds_lines(bgp2.switch.console,bgp_config)

    def build_bgp_peer(self,bgp1,as1,bgp2,as2):
        tprint(f"============== Configurating BGP peer between {bgp1.switch.name} AS = {as1} and {bgp2.switch.name} AS={as2} ")
        if bgp1.switch.is_fortinet():
            bgp_config = f"""
            config router bgp
                set as {as1}
                set router-id {bgp1.router_id }
            end
            config redistribute6 "connected"
             set status enable
            end
            """
            config_cmds_lines(bgp1.switch.console,bgp_config)
            bgp_config = f"""
            config router bgp
                config neighbor
                    edit {bgp2.switch.vlan1_ipv6.split("/")[0]}
                        set remote-as {as2}
                    next
                end
            end
            """
            config_cmds_lines(bgp1.switch.console,bgp_config)

        elif bgp1.switch.platform == "n9k":
            bgp_config = f"""
            config t
            router bgp 65000
            neighbor {bgp2.switch.vlan1_ipv6.split("/")[0]}
                remote-as {as2}
                address-family ipv6 unicast
            """
            config_cmds_lines(bgp1.switch.console,bgp_config)

        if bgp2.switch.is_fortinet():
            bgp_config = f"""
            config router bgp
                set as {as2}
                set router-id {bgp2.router_id }
            end
            """
            config_cmds_lines(bgp2.switch.console,bgp_config)
            bgp_config = f"""
            config router bgp
                config neighbor
                    edit {bgp1.switch.vlan1_ipv6.split("/")[0]}
                        set remote-as {as1}
                    next
                end
            end
            """
            config_cmds_lines(bgp2.switch.console,bgp_config)

        elif bgp2.switch.platform == "n9k":
            bgp_config = f"""
            config t
            router bgp 65000
            neighbor {bgp1.switch.vlan1_ipv6.split("/")[0]}
                remote-as {as1}
                address-family ipv6 unicast
            """
            config_cmds_lines(bgp2.switch.console,bgp_config)

    def build_bgp_peer_address(self,bgp1,as1,addr1,bgp2,as2,addr2):
        tprint(f"============== Configurating BGP peer between {bgp1.switch.name} AS = {as1} and {bgp2.switch.name} AS={as2} ")
        if bgp1.switch.is_fortinet():
            bgp_config = f"""
            config router bgp
                set as {as1}
                set router-id {bgp1.router_id }
            end
            config redistribute6 "connected"
             set status disable
            end
            """
            config_cmds_lines(bgp1.switch.console,bgp_config)

            bgp_config = f"""
            config router bgp
                config neighbor
                    edit {addr2}
                        set remote-as {as2}
                    next
                end
            end
            """
            config_cmds_lines(bgp1.switch.console,bgp_config)

        if bgp2.switch.is_fortinet():
            bgp_config = f"""
            config router bgp
                set as {as2}
                set router-id {bgp2.router_id }
            end
            config redistribute6 "connected"
             set status disable
            end
            """
            config_cmds_lines(bgp2.switch.console,bgp_config)

            bgp_config = f"""
            config router bgp
                config neighbor
                    edit {addr1}
                        set remote-as {as1}
                    next
                end
            end
            """
            config_cmds_lines(bgp2.switch.console,bgp_config)
        

    def biuld_ibgp_mesh_topo_sys_intf(self):
        for router1 in self.routers:
            for router2 in self.routers:
                if router1 is router2: 
                    continue 
                else:
                    self.config_ibgp_session_all_interface(router1,router2) 

    def biuld_ibgp_mesh_topo_sys_intf_one(self):
        for router1 in self.routers:
            for router2 in self.routers:
                if router1 is router2: 
                    continue 
                else:
                    self.config_ibgp_session_one_interface(router1,router2) 

    # def biuld_ibgp_mesh_topo_sys_intf_v6_2nd_single(self,*args,**kwargs):
    #     interface_name = kwargs['interface']
    #     for router1 in self.routers: 
    #         for router2 in self.routers:   
    #             if router1 is router2: 
    #                 continue 
    #             else:
    #                 self.config_ibgp_session_all_interface_v6_2nd(router1,router2) 

    def biuld_ibgp_mesh_topo_sys_intf_v6_2nd(self,*args,**kwargs):
        if "interface" in kwargs:
            interface_name = kwargs["interface"]
        else:
            interface_name = "All"
        if interface_name == "All":
            for router1 in self.routers: 
                for router2 in self.routers:   
                    if router1 is router2: 
                        continue 
                    else:
                        self.config_ibgp_session_all_interface_v6_2nd(router1,router2) 
        else:
            for router1 in self.routers: 
                for router2 in self.routers:   
                    if router1 is router2: 
                        continue 
                    else:
                        self.config_ibgp_session_all_interface_v6_2nd(router1,router2,interface=interface_name) 

    def biuld_ibgp_mesh_topo_sys_intf_v6(self):
        for router1 in self.routers: 
            for router2 in self.routers:   
                if router1 is router2: 
                    continue 
                else:
                    self.config_ibgp_session_all_interface_v6(router1,router2) 

    def biuld_ibgp_mesh_topo_sys_intf_v6_one(self):
        for router1 in self.routers: 
            for router2 in self.routers:   
                if router1 is router2: 
                    continue 
                else:
                    self.config_ibgp_session_one_interface_v6(router1,router2) 


    def config_ospf_networks(self):
        for switch in self.switches:
            switch.show_switch_info()
            switch.router_ospf.basic_config()
        console_timer(20,msg="Class BGP Network: After configuring ospf, wait for 20 sec")

    def config_ibgp_session_one_interface(self,bgp1,bgp2):
        tprint(f"============== Configurating iBGP peer between {bgp1.switch.name} and {bgp2.switch.name} ")
        if bgp1.switch.is_fortinet():
            bgp_config = f"""
            config router bgp
                set as {bgp1.ibgp_as}
                set router-id {bgp1.router_id }
            end
            end
            """
            config_cmds_lines(bgp1.switch.console,bgp_config)
            bgp_config = f"""
            config router bgp
                config neighbor
                    edit {bgp2.router_id}
                        set remote-as {bgp2.ibgp_as}
                        set update-source loop0
                    next
                end
            end
            """
            config_cmds_lines(bgp1.switch.console,bgp_config)

        if bgp2.switch.is_fortinet():
            bgp_config = f"""
            config router bgp
                set as {bgp2.ibgp_as}
                set router-id {bgp2.router_id }
            end
            end
            """
            config_cmds_lines(bgp2.switch.console,bgp_config)

            bgp_config = f"""
            config router bgp
                config neighbor
                    edit {bgp1.router_id}
                        set remote-as {bgp1.ibgp_as}
                        set update-source loop0
                    next
                end
            end
            """
            config_cmds_lines(bgp2.switch.console,bgp_config)


    def config_ibgp_session_all_interface(self,bgp1,bgp2):
        tprint(f"============== Configurating iBGP peer between {bgp1.switch.name} and {bgp2.switch.name} ")
        if bgp1.switch.is_fortinet():
            bgp_config = f"""
            config router bgp
                set as {bgp1.ibgp_as}
                set router-id {bgp1.router_id }
            end
            end
            """
            config_cmds_lines(bgp1.switch.console,bgp_config)
            bgp_config = f"""
            config router bgp
                config neighbor
                    edit {bgp2.router_id}
                        set remote-as {bgp2.ibgp_as}
                        set update-source loop0
                    next
                end
            end
            """
            config_cmds_lines(bgp1.switch.console,bgp_config)

            bgp_config = f"""
            config router bgp
                config neighbor
                    edit {bgp2.switch.internal}
                        set remote-as {bgp2.ibgp_as}
                        set update-source loop0
                    next
                end
            end
            """
            config_cmds_lines(bgp1.switch.console,bgp_config)

            bgp_config = f"""
            config router bgp
                config neighbor
                    edit {bgp2.switch.vlan1_2nd}
                        set remote-as {bgp2.ibgp_as}
                        set update-source loop0
                    next
                end
            end
            """
            config_cmds_lines(bgp1.switch.console,bgp_config)

        if bgp2.switch.is_fortinet():
            bgp_config = f"""
            config router bgp
                set as {bgp2.ibgp_as}
                set router-id {bgp2.router_id }
            end
            end
            """
            config_cmds_lines(bgp2.switch.console,bgp_config)

            bgp_config = f"""
            config router bgp
                config neighbor
                    edit {bgp1.router_id}
                        set remote-as {bgp1.ibgp_as}
                        set update-source loop0
                    next
                end
            end
            """
            config_cmds_lines(bgp2.switch.console,bgp_config)


            bgp_config = f"""
            config router bgp
                config neighbor
                    edit {bgp1.switch.internal}
                        set remote-as {bgp1.ibgp_as}
                        set update-source loop0
                    next
                end
            end
            """
            config_cmds_lines(bgp2.switch.console,bgp_config)

            bgp_config = f"""
            config router bgp
                config neighbor
                    edit {bgp1.switch.vlan1_2nd}
                        set remote-as {bgp1.ibgp_as}
                        set update-source loop0
                    next
                end
            end
            """
            config_cmds_lines(bgp2.switch.console,bgp_config)

    def config_ibgp_session_one_interface_v6(self,bgp1,bgp2):
        tprint(f"============== Configurating One-Session IPv6 iBGP peer between {bgp1.switch.name} and {bgp2.switch.name} ")
        if bgp1.switch.is_fortinet():
            bgp_config = f"""
            config router bgp
                set as {bgp1.ibgp_as}
                set router-id {bgp1.router_id }
            end
            end
            """
            config_cmds_lines(bgp1.switch.console,bgp_config)
            bgp_config = f"""
            config router bgp
                config neighbor
                    edit {bgp2.switch.loop0_ipv6.split("/")[0]}
                        set remote-as {bgp2.ibgp_as}
                        set update-source loop0
                    next
                end
            end
            """
            config_cmds_lines(bgp1.switch.console,bgp_config)


        #Cofiguring router #2 
        if bgp2.switch.is_fortinet():
            bgp_config = f"""
            config router bgp
                set as {bgp2.ibgp_as}
                set router-id {bgp2.router_id }
            end
            end
            """
            config_cmds_lines(bgp2.switch.console,bgp_config)

            bgp_config = f"""
            config router bgp
                config neighbor
                    edit {bgp2.switch.loop0_ipv6.split("/")[0]}
                        set remote-as {bgp1.ibgp_as}
                        set update-source loop0
                    next
                end
            end
            """
            config_cmds_lines(bgp2.switch.console,bgp_config)


    def config_ibgp_session_all_interface_v6_2nd(self,bgp1,bgp2,*args,**kwargs):
        tprint(f"============== Configurating iBGP peer between {bgp1.switch.name} and {bgp2.switch.name} ")
        if "interface" in kwargs:
            my_intf = kwargs['interface']
        else:
            my_intf = None 

        if bgp1.switch.is_fortinet():
            bgp_config = f"""
            config router bgp
                set as {bgp1.ibgp_as}
                set router-id {bgp1.router_id }
            end
            end
            """
            config_cmds_lines(bgp1.switch.console,bgp_config)
            for interface1,interface2 in zip(bgp1.switch.sys_interfaces,bgp2.switch.sys_interfaces):
                if interface1.name == "mgmt" or interface2.name == "mgmt":
                    continue
                if my_intf == None or (interface1.name == my_intf and interface2.name == my_intf):
                    bgp_config = f"""
                    config router bgp
                        config neighbor
                            edit {interface2.ipv6_2nd.split("/")[0]}
                                set remote-as {bgp2.ibgp_as}
                                set update-source {interface1.name}
                            next
                        end
                    end
                    """
                    config_cmds_lines(bgp1.switch.console,bgp_config)


        #Cofiguring router #2 
        if bgp2.switch.is_fortinet():
            bgp_config = f"""
            config router bgp
                set as {bgp2.ibgp_as}
                set router-id {bgp2.router_id }
            end
            end
            """
            config_cmds_lines(bgp2.switch.console,bgp_config)

            for interface1,interface2 in zip(bgp1.switch.sys_interfaces,bgp2.switch.sys_interfaces):
                if interface1.name == "mgmt" or interface2.name == "mgmt":
                    continue
                if my_intf == None or (interface1.name == my_intf and interface2.name == my_intf):
                    bgp_config = f"""
                    config router bgp
                        config neighbor
                            edit {interface1.ipv6_2nd.split("/")[0]}
                                set remote-as {bgp2.ibgp_as}
                                set update-source {interface2.name}
                            next
                        end
                    end
                    """
                    config_cmds_lines(bgp2.switch.console,bgp_config)
           
    def config_ibgp_session_all_interface_v6(self,bgp1,bgp2):
        tprint(f"============== Configurating iBGP peer between {bgp1.switch.name} and {bgp2.switch.name} ")
        if bgp1.switch.is_fortinet():
            bgp_config = f"""
            config router bgp
                set as {bgp1.ibgp_as}
                set router-id {bgp1.router_id }
            end
            end
            """
            config_cmds_lines(bgp1.switch.console,bgp_config)
            bgp_config = f"""
            config router bgp
                config neighbor
                    edit {bgp2.switch.loop0_ipv6.split("/")[0]}
                        set remote-as {bgp2.ibgp_as}
                        set update-source loop0
                    next
                end
            end
            """
            config_cmds_lines(bgp1.switch.console,bgp_config)

            bgp_config = f"""
            config router bgp
                config neighbor
                    edit {bgp2.switch.internal_v6.split("/")[0]}
                        set remote-as {bgp2.ibgp_as}
                        set update-source internal
                    next
                end
            end
            """
            config_cmds_lines(bgp1.switch.console,bgp_config)

            bgp_config = f"""
            config router bgp
                config neighbor
                    edit {bgp2.switch.vlan1_ipv6.split("/")[0]}
                        set remote-as {bgp2.ibgp_as}
                    next
                end
            end
            """
            config_cmds_lines(bgp1.switch.console,bgp_config)

        #Cofiguring router #2 
        if bgp2.switch.is_fortinet():
            bgp_config = f"""
            config router bgp
                set as {bgp2.ibgp_as}
                set router-id {bgp2.router_id }
            end
            end
            """
            config_cmds_lines(bgp2.switch.console,bgp_config)

            bgp_config = f"""
            config router bgp
                config neighbor
                    edit {bgp2.switch.loop0_ipv6.split("/")[0]}
                        set remote-as {bgp1.ibgp_as}
                        set update-source loop0
                    next
                end
            end
            """
            config_cmds_lines(bgp2.switch.console,bgp_config)


            bgp_config = f"""
            config router bgp
                config neighbor
                    edit {bgp1.switch.internal_v6.split("/")[0]}
                        set remote-as {bgp1.ibgp_as}
                        set update-source internal
                    next
                end
            end
            """
            config_cmds_lines(bgp2.switch.console,bgp_config)

            bgp_config = f"""
            config router bgp
                config neighbor
                    edit {bgp1.switch.vlan1_ipv6.split("/")[0]}
                        set remote-as {bgp1.ibgp_as}
                    next
                end
            end
            """
            config_cmds_lines(bgp2.switch.console,bgp_config)



    def config_ibgp_session(self,bgp1,bgp2):
        tprint(f"============== Configurating iBGP peer between {bgp1.switch.name} and {bgp2.switch.name} ")
        bgp_config = f"""
        config router bgp
            set as {bgp1.ibgp_as}
            set router-id {bgp1.router_id }
        end
        end
        """
        config_cmds_lines(bgp1.switch.console,bgp_config)
        bgp_config = f"""
        config router bgp
            config neighbor
                edit {bgp2.router_id}
                    set remote-as {bgp2.ibgp_as}
                    set update-source loop0
                next
            end
        end
        """
        config_cmds_lines(bgp1.switch.console,bgp_config)


        bgp_config = f"""
        config router bgp
            set as {bgp2.ibgp_as}
            set router-id {bgp2.router_id }
        end
        end
        """
        config_cmds_lines(bgp2.switch.console,bgp_config)

        bgp_config = f"""
        config router bgp
            config neighbor
                edit {bgp1.router_id}
                    set remote-as {bgp1.ibgp_as}
                    set update-source loop0
                next
            end
        end
        """
        config_cmds_lines(bgp2.switch.console,bgp_config)

    def config_ibgp_session_loopback_v6(self,bgp1,bgp2):
        tprint(f"============== Configurating iBGP peer between {bgp1.switch.name} and {bgp2.switch.name} ")
        bgp_config = f"""
        config router bgp
            set as {bgp1.ibgp_as}
            set router-id {bgp1.router_id }
        end
        end
        """
        config_cmds_lines(bgp1.switch.console,bgp_config)
        bgp_config = f"""
        config router bgp
            config neighbor
                edit {bgp2.switch.loop0_ipv6.split("/")[0]}
                    set remote-as {bgp2.ibgp_as}
                    set update-source loop0
                next
            end
        end
        """
        config_cmds_lines(bgp1.switch.console,bgp_config)


        bgp_config = f"""
        config router bgp
            set as {bgp2.ibgp_as}
            set router-id {bgp2.router_id }
        end
        end
        """
        config_cmds_lines(bgp2.switch.console,bgp_config)

        bgp_config = f"""
        config router bgp
            config neighbor
                edit {bgp1.switch.loop0_ipv6.split("/")[0]}
                    set remote-as {bgp1.ibgp_as}
                    set update-source loop0
                next
            end
        end
        """
        config_cmds_lines(bgp2.switch.console,bgp_config)

    def config_ebgp_session_v6(self,bgp1,bgp2):
        tprint(f"============== Configurating eBGP peer between {bgp1.switch.name} and {bgp2.switch.name} ")
        bgp_config = f"""
        config router bgp
            set as {bgp1.ebgp_as}
            set router-id {bgp1.router_id }
        end
        end
        """
        config_cmds_lines(bgp1.switch.console,bgp_config)

        bgp_config = f"""
        config router bgp
            config neighbor
                edit {bgp2.switch.vlan1_ipv6.split("/")[0]}
                    set remote-as {bgp2.ebgp_as}
                next
            end
        end
        """
        config_cmds_lines(bgp1.switch.console,bgp_config)


        bgp_config = f"""
        config router bgp
            set as {bgp2.ebgp_as}
            set router-id {bgp2.router_id }
        end
        end
        """
        config_cmds_lines(bgp2.switch.console,bgp_config)

        bgp_config = f"""
        config router bgp
            config neighbor
                edit {bgp1.switch.vlan1_ipv6.split("/")[0]}
                    set remote-as {bgp1.ebgp_as}
                next
            end
        end
        """
        config_cmds_lines(bgp2.switch.console,bgp_config)

    

    def config_ebgp_session(self,bgp1,bgp2):
        tprint(f"============== Configurating eBGP peer between {bgp1.switch.name} and {bgp2.switch.name} ")
        bgp_config = f"""
        config router bgp
            set as {bgp1.ebgp_as}
            set router-id {bgp1.router_id }
        end
        end
        """
        config_cmds_lines(bgp1.switch.console,bgp_config)

        bgp_config = f"""
        config router bgp
            config neighbor
                edit {bgp2.switch.vlan1_ip}
                    set remote-as {bgp2.ebgp_as}
                next
            end
        end
        """
        config_cmds_lines(bgp1.switch.console,bgp_config)


        bgp_config = f"""
        config router bgp
            set as {bgp2.ebgp_as}
            set router-id {bgp2.router_id }
        end
        end
        """
        config_cmds_lines(bgp2.switch.console,bgp_config)

        bgp_config = f"""
        config router bgp
            config neighbor
                edit {bgp1.switch.vlan1_ip}
                    set remote-as {bgp1.ebgp_as}
                next
            end
        end
        """
        config_cmds_lines(bgp2.switch.console,bgp_config)

    def config_rs_ebgp_session_v6(self,bgp1,bgp2):
        tprint(f"============== Configurating IPv6 eBGP Route Server peer between {bgp1.switch.name} and {bgp2.switch.name} ")
        bgp_config = f"""
        config router bgp
            set as {bgp1.ebgp_as}
            set router-id {bgp1.router_id }
        end
        end
        """
        config_cmds_lines(bgp1.switch.console,bgp_config)

        bgp_config = f"""
        config router bgp
            config neighbor
                edit {bgp2.switch.vlan1_ipv6.split("/")[0]}
                    set remote-as {bgp2.ebgp_as}
                    set route-server-client6 enable
                next
            end
        end
        """
        config_cmds_lines(bgp1.switch.console,bgp_config)


        bgp_config = f"""
        config router bgp
            set as {bgp2.ebgp_as}
            set router-id {bgp2.router_id }
        end
        end
        """
        config_cmds_lines(bgp2.switch.console,bgp_config)

        bgp_config = f"""
        config router bgp
            config neighbor
                edit {bgp1.switch.vlan1_ipv6.split("/")[0]}
                    set remote-as {bgp1.ebgp_as}
                next
            end
        end
        """
        config_cmds_lines(bgp2.switch.console,bgp_config)

    def config_rs_ebgp_session(self,bgp1,bgp2):
        tprint(f"============== Configurating route server eBGP peer between {bgp1.switch.name} and {bgp2.switch.name} ")
        bgp_config = f"""
        config router bgp
            set as {bgp1.ebgp_as}
            set router-id {bgp1.router_id }
        end
        end
        """
        config_cmds_lines(bgp1.switch.console,bgp_config)

        bgp_config = f"""
        config router bgp
            config neighbor
                edit {bgp2.switch.vlan1_ip}
                    set remote-as {bgp2.ebgp_as}
                    set route-server-client enable
                next
            end
        end
        """
        config_cmds_lines(bgp1.switch.console,bgp_config)


        bgp_config = f"""
        config router bgp
            set as {bgp2.ebgp_as}
            set router-id {bgp2.router_id }
        end
        end
        """
        config_cmds_lines(bgp2.switch.console,bgp_config)

        bgp_config = f"""
        config router bgp
            config neighbor
                edit {bgp1.switch.vlan1_ip}
                    set remote-as {bgp1.ebgp_as}
                next
            end
        end
        """
        config_cmds_lines(bgp2.switch.console,bgp_config)

    def config_ibgp_rr_session(self,rr,client):
        tprint(f"============== Configurating iBGP Router Reflector and Client session between {rr.switch.name} and {client.switch.name} ")
        bgp_config = f"""
        config router bgp
            set as {rr.ibgp_as}
            set router-id {rr.router_id }
        end
        end
        """
        config_cmds_lines(rr.switch.console,bgp_config)
        bgp_config = f"""
        config router bgp
            config neighbor
                edit {client.router_id}
                    set remote-as {client.ibgp_as}
                    set update-source loop0
                    set route-reflector-client enable
                next
            end
        end
        """
        config_cmds_lines(rr.switch.console,bgp_config)


        bgp_config = f"""
        config router bgp
            set as {client.ibgp_as}
            set router-id {client.router_id }
        end
        end
        """
        config_cmds_lines(client.switch.console,bgp_config)

        bgp_config = f"""
        config router bgp
            config neighbor
                edit {rr.router_id}
                    set remote-as {rr.ibgp_as}
                    set update-source loop0
                next
            end
        end
        """
        config_cmds_lines(client.switch.console,bgp_config)

    def config_ibgp_rr_session_v6(self,rr,client):
        tprint(f"============== Configurating iBGP v6 Router Reflector and Client session between {rr.switch.name} and {client.switch.name} ")
        if rr.switch.is_fortinet():
            bgp_config = f"""
            config router bgp
                set as {rr.ibgp_as}
                set router-id {rr.router_id }
            end
            end
            """
            config_cmds_lines(rr.switch.console,bgp_config)         

            bgp_config = f"""
            config router bgp
                config neighbor
                    edit {client.switch.loop0_ipv6.split("/")[0]}
                        set remote-as {client.ibgp_as}
                        set update-source loop0
                        set route-reflector-client enable
                    next
                end
            end
            """
            config_cmds_lines(rr.switch.console,bgp_config)

        if client.switch.is_fortinet():
            bgp_config = f"""
            config router bgp
                set as {client.ibgp_as}
                set router-id {client.router_id }
            end
            end
            """
            config_cmds_lines(client.switch.console,bgp_config)

            bgp_config = f"""
            config router bgp
                config neighbor
                    edit {rr.switch.loop0_ipv6.split("/")[0]}
                        set remote-as {rr.ibgp_as}
                        set update-source loop0
                    next
                end
            end
            """
            config_cmds_lines(client.switch.console,bgp_config)

    def config_cluster_id(self,rr1,rr2):
        bgp_config = f"""
        config router bgp
            set cluster-id  1.1.1.2
        end
        """
        config_cmds_lines(rr1.switch.console,bgp_config)

        bgp_config = f"""
        config router bgp
            set cluster-id 2.2.2.3
        end
        """
        config_cmds_lines(rr2.switch.console,bgp_config)

    def build_route_server_topo_v6(self):
        rs = self.routers[0]
        for i in range(1,6):
            self.config_rs_ebgp_session_v6(rs,self.routers[i])


    def build_route_server_topo(self):
        rs = self.routers[0]
        for i in range(1,6):
            self.config_rs_ebgp_session(rs,self.routers[i])
         

    def build_router_reflector_topo(self):
        rr1 = self.routers[0]
        rr2 = self.routers[1]

        for i in range(2,7):
            self.config_ibgp_rr_session(rr1,self.routers[i])
        for i in range(2,7):
            self.config_ibgp_rr_session(rr2,self.routers[i])

        self.config_ibgp_session(rr1,rr2)

    def build_router_reflector_topo_v6(self):
        rr1 = self.routers[0]
        rr2 = self.routers[1]

        for i in range(2,6):
            self.config_ibgp_rr_session_v6(rr1,self.routers[i])
        for i in range(2,6):
            self.config_ibgp_rr_session_v6(rr2,self.routers[i])

        self.config_ibgp_session_loopback_v6(rr1,rr2)

        self.config_cluster_id(rr1,rr2)


    def config_all_confed_id(self):
        for router in self.routers:
            bgp_config = f"""
            config router bgp
                 set confederation-identifier {router.confed_id}   
            end
            """
            config_cmds_lines(router.switch.console,bgp_config)

    def config_confed_peers(self,router,peer_list):
        id_list = " ".join(str(r.ebgp_as) for r in peer_list)
        print(id_list)
        
        bgp_config = f"""
        config router bgp
             set confederation-peers {id_list}   
        end
        """
        config_cmds_lines(router.switch.console,bgp_config)


    def build_confed_topo_1(self):
        fed_50_1 = self.routers[0]
        fed_50_2 = self.routers[1]

        fed_60_1 = self.routers[2]
        fed_60_2 = self.routers[3]
        fed_60_3 = self.routers[4]

        fed_70_1 = self.routers[5]
        fed_70_2 = self.routers[6]


        fed_50_1.ibgp_as = 50
        fed_50_2.ibgp_as = 50
        fed_50_1.ebgp_as = 50
        fed_50_2.ebgp_as = 50

        fed_60_1.ibgp_as =60
        fed_60_2.ibgp_as =60
        fed_60_3.ibgp_as =60
        fed_60_1.ebgp_as =60
        fed_60_2.ebgp_as =60
        fed_60_3.ebgp_as =60

        fed_70_1.ibgp_as =70
        fed_70_2.ibgp_as =70
        fed_70_1.ebgp_as =70
        fed_70_2.ebgp_as =70

        self.config_ibgp_session(fed_50_1,fed_50_2)


        self.config_ibgp_session(fed_60_1,fed_60_2)
        self.config_ibgp_session(fed_60_1,fed_60_3)
        self.config_ibgp_session(fed_60_2,fed_60_3)
        
        
        self.config_ibgp_session(fed_70_1,fed_70_2)

        self.config_ebgp_session(fed_50_2,fed_60_1)
        self.config_ebgp_session(fed_50_2,fed_70_1)
        self.config_ebgp_session(fed_60_1,fed_70_2)

        self.config_all_confed_id()

        self.config_confed_peers(fed_50_2,[fed_60_1,fed_70_1])
        self.config_confed_peers(fed_60_1,[fed_70_2,fed_50_2])
        self.config_confed_peers(fed_70_1,[fed_50_2])
        self.config_confed_peers(fed_70_2,[fed_60_1])

    def build_confed_topo_1_v6(self):
        fed_50_1 = self.routers[0]
        fed_50_2 = self.routers[1]

        fed_60_1 = self.routers[2]
        fed_60_2 = self.routers[3]

        fed_70_1 = self.routers[4]
        fed_70_2 = self.routers[5]


        fed_50_1.ibgp_as = 50
        fed_50_2.ibgp_as = 50
        fed_50_1.ebgp_as = 50
        fed_50_2.ebgp_as = 50

        fed_60_1.ibgp_as = 60
        fed_60_2.ibgp_as = 60
        fed_60_1.ebgp_as = 60
        fed_60_2.ebgp_as = 60
        
        fed_70_1.ibgp_as = 70
        fed_70_2.ibgp_as = 70
        fed_70_1.ebgp_as = 70
        fed_70_2.ebgp_as = 70

        self.config_ibgp_session_loopback_v6(fed_50_1,fed_50_2)

        self.config_ibgp_session_loopback_v6(fed_60_1,fed_60_2)
         
        self.config_ibgp_session_loopback_v6(fed_70_1,fed_70_2)

        self.config_ebgp_session_v6(fed_50_2,fed_60_1)
        self.config_ebgp_session_v6(fed_50_2,fed_70_1)
        self.config_ebgp_session_v6(fed_60_1,fed_70_2)

        self.config_all_confed_id()

        self.config_confed_peers(fed_50_2,[fed_60_1,fed_70_1])
        self.config_confed_peers(fed_60_1,[fed_70_2,fed_50_2])
        self.config_confed_peers(fed_70_1,[fed_50_2])
        self.config_confed_peers(fed_70_2,[fed_60_1])

class Router_community_list:
    def __init__(self, *args, **kwargs):
        self.switch = args[0]

    def basic_config(self):
        basic_config_community_list(self.switch.console)

    def clean_up(self):
        pass

class Router_prefix_list:
    def __init__(self,*args, **kwargs):
        self.switch = args[0]

    def prefix_large_config_v4(self):
        large_config_prefix_list_v4(self.switch.console)

    def prefix_orf_v4(self):
        config = """
        config router prefix-list
        edit "orf-list"
            config rule
                edit 1
                    set prefix 10.0.0.0 255.0.0.0
                    unset ge
                    unset le
                next
                edit 2
                    set action deny
                    set prefix 169.254.0.0 255.255.0.0
                    unset ge
                    unset le
                next
                edit 3
                    set prefix 100.0.0.0 255.0.0.0
                    set ge 9
                    set le 24
                next
                edit 4
                    set prefix 200.0.0.0 255.0.0.0
                    set ge 9
                    set le 24
                next
                edit 5
                    set action deny
                    set prefix 255.0.0.0 255.0.0.0
                    set ge 9
                    set le 32
                next
            end
            next
        end
        """
        config_cmds_lines(self.switch.console,config)

    def prefix_unsuppress_v4(self):
        config = """
        config router prefix-list
        edit "unsuppress-list"
            config rule
                edit 1
                    set prefix 10.10.4.27/32   
                next
                edit 2
                     set prefix 10.10.4.28/32  
                next
                edit 3
                    set prefix 10.10.4.29/32
                next
                edit 4
                    set prefix 10.10.4.30/32
                next
            end
            next
        end
        """
        config_cmds_lines(self.switch.console,config)



    def prefix_orf_v6(self):
        config = """
        config router prefix-list6
        edit "orf-list-v6"
            config rule
                edit 1
                    set prefix6 "2001:10::0/32"
                    set ge 33
                    set le 128
                next
                edit 2
                    set prefix6 "2001:20::0/32"
                    set ge 33
                    set le 128
                next
                edit 3
                    set prefix6 "2001:30::0/32"
                    set ge 33
                    set le 128
                next
                edit 4
                    set action deny
                    set prefix6 "fe80::0/16"
                    set ge 17
                    set le 128
                next
                edit 5
                    set prefix6 "2001:40::0/32"
                    set ge 33
                    set le 128
                next
                edit 6
                    set prefix6 "2001:50::0/32"
                    set ge 33
                    set le 128
                next
            end
            next
        end

        """
        config_cmds_lines(self.switch.console,config)

    def prefix_unsuppress_v6(self):
        config = """
        config router prefix-list6
        edit "unsuppress-list-v6"
            config rule
                edit 1
                    set prefix6 2001:104:1:1::1b/128  
                next
                edit 2
                    set prefix6 2001:104:1:1::1c/128
                next
                edit 3
                    set prefix6 2001:104:1:1::1d/128
                next
                edit 4
                    set prefix6 2001:104:1:1::1e/128  
                next
            end
            next
        end
        """
        config_cmds_lines(self.switch.console,config)

    def prefix_clean_up(self):
        pass

class Router_aspath_list:
    def __init__(self,*args,**kargs):
        self.switch = args[0]

    def basic_config(self):
        basic_config_aspath_list(self.switch.console)

    def clean_up(self):
        pass

class Router_access_list6:

    def __init__(self,*args,**kargs):
        self.switch = args[0]

    def config_acl6(self,*args,**kwargs):
        sample = """
        config router access-list6
        edit "admin-routes"
            config rule
                edit 1
                    set prefix6 "2001:103:1:1::1/128"
                    set exact-match disable
                next
            end
        next
        end
        """
        acl_name = kwargs['acl_name']
        prefix = kwargs['prefix']
        if "/" in prefix:
            prefix = prefix.split("/")[0]

        config = f"""
        config router access-list6
        edit {acl_name}
            config rule
                edit 1
                    set prefix6 {prefix}/128
                next
            end
        next
        end
        """
        config_cmds_lines(self.switch.console,config)

class Acl_usage_entry():
    def __init__(self,*args,**kwargs):
        self.group_id = None 
        self.stage = None 
        self.policer_total = None 
        self.policer_free = None 
        self.counter_total = None 
        self.counter_free = None 
        self.rule_total = None 
        self.rule_free = None 

    def show_usage_entry(self):
        print(f"group_id={self.group_id}")
        print(f"stage={self.stage}")
        print(f"policer_total={self.policer_total}")
        print(f"policer_free={self.policer_free}")
        print(f"counter_total={self.counter_total}")
        print(f"counter_free={self.counter_free}")
        print(f"rule_total={self.rule_total}")
        print(f"rule_free={self.rule_free}")


class Switch_ACL:
    def __init__(self,*args,**kwargs):
        self.switch = args[0]
        self.clauses = None
        self.acl_usage_list = []
        self.update_acl_usage()

    def update_acl_usage(self):
        sample = """
        S424EPTF21001277 # get switch acl usage

        Device    RULES         COUNTERS       POLICERS       STAGE     GROUP
                 (total/free)   (total/free)  (total/free)
        ______________________________________________________________________



        0        128   /89     256   /217    2048  /2048   ingress       1
        0        128   /126    512   /510    2048  /2048   ingress       3
        0        128   /127    512   /512    2048  /2048   ingress       4
        0        128   /128    512   /512    2048  /2048   ingress       5
        0        128   /128    256   /256    2048  /2048   ingress       6
        0        256   /256    512   /512    384   /384    egress        1
        0        256   /256    0     /0      0     /0      prelookup      1
        """
        cmd_output = collect_show_cmd(self.switch.console,"get switch acl usage")

        #regex = r"\d+   /\d+     \d+   /\d+    \d+  /\d+"
        regex = r"\d+\s+/\d+\s+\d+\s+/\d+\s+\d+\s+/\d+"
        self.acl_usage_list = []
        for line in cmd_output:
            matched = re.search(regex,line)
            if matched:
                print(matched.group())
                usage_entry = Acl_usage_entry()
                items = line.split()
                usage_entry.group_id = int(items[-1]) 
                usage_entry.stage = items[-2] 
                usage_entry.policer_free = int(items[-3].strip("/"))
                usage_entry.policer_total = int(items[-4])
                usage_entry.counter_free = int(items[-5].strip("/"))
                usage_entry.counter_total = int(items[-6]) 
                usage_entry.rule_free = int(items[-7].strip("/"))
                usage_entry.rule_total = int(items[-8])
                self.acl_usage_list.append(usage_entry)
        #print(self.acl_usage_list)
        return self.acl_usage_list

    def print_acl_usage(self):
        for entry in self.acl_usage_list:
            entry.show_usage_entry()

class DotOnex():
    def __init__(self,*args,**kwargs):
        self.switch = args[0]
        self.user = kwargs['user']
        self.user_group = kwargs["user_group"]
        self.secrete = kwargs["secrete"]
        self.server = kwargs["server"]
        self.port_list = []
 
        if "port_list" in kwargs:
            self.port_list = kwargs["port_list"]

    def dot1x_global_config(self):
        initial_config = f"""
        config user radius
            edit {self.user}
                set secret {self.secrete}
                set server  {self.server}
            next
        end
        config user group
            edit {self.user_group}
                set member {self.user}
            next
        end

        config switch global
            config port-security
                set link-down-auth no-action
                set max-reauth-attempt 3
            end
        end
        """
        self.switch.config_cmds_fast(initial_config)
        # if "port_list" in kwargs:
        #     self.port_list = kwargs["port_list"]
        #     self.dot1x_interface_config(self.port_list)

    def dot1x_interface_config(self,*args,**kwargs):
        port_list = kwargs["port_list"]
        self.port_list = port_list
        for port in port_list:
            cmds = f"""
            config switch interface
                edit {port}
                    config port-security
                        set port-security-mode 802.1X-mac-based
                        set dacl enable
                    end
                    set security-groups {self.user_group}
                 end
            """
            self.switch.config_cmds_fast(cmds)
 
    def dot1x_remove_config(self):
        for port in self.port_list:
            cmds = f"""
            config switch interface
                edit {port}
                    config port-security
                        unset port-security-mode  
                    end
                    unset security-groups
                 end
            """
            self.switch.config_cmds_fast(cmds)
        self.port_list = []

        remove_config = f"""
        config user group
            delete {self.user_group}
        end
        config switch global
            config port-security
                unset link-down-auth  
                unset max-reauth-attempt 
            end
        end
         config user radius
            delete {self.user}
        end
        """
        self.switch.config_cmds_fast(remove_config)

class switch_acl_dotonex(Switch_ACL):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.clauses = None

    def config_acl_dotonex_jinja(self,yaml_string):
        jinja_string = """
         config switch acl service custom
            edit {{filter_name}}
            set protocol IP
            next
        end
        config switch acl 802-1X   
        edit {{ acl_index }}
                {% for key, value in globals_config.items() %}
                set {{ key }} {{ value }}
                {% endfor -%}
                config access-list-entry
                  {% for entry in entries %}
                  edit {{ entry.index }}
                  set group {{entry.group_id}}
                  config classifier
                    {% for key, value in entry.classifiers.items() %}
                    set {{ key }} {{ value }}
                    {% endfor -%}
                  end
                  config action
                  {% for key, value in entry.actions.items() %}
                    set {{ key }} {{ value }}
                  {% endfor -%}
                  end
                 next 
                 {% endfor -%}
              end
            next
        end
        """
        config = yaml.safe_load(yaml_string)
        template = Template(jinja_string)
        result = template.render(config)
        self.switch.config_cmds_fast(result)

    def remove_acl_dot1x_jinja(self,yaml_string):
        jinja_string = """
        config switch acl 802-1X  
        {% for acl_index in range(1,acl_length + 1) %}
        delete {{ acl_index }}
        {% endfor -%}
        end
        config switch acl service custom
            delete {{filter_name}}
            next
        end
        """
        config = yaml.safe_load(yaml_string)
        template = Template(jinja_string)
        result = template.render(config)
        self.switch.config_cmds_fast(result)

    def acl_dot1x_find_clauses(self):
        result = collect_edit_items_general(self.switch.console,"conf switch acl 802-1X",keyword="802-1X")
        print(result)
        clauses = []
        for item in result:
            two_parts = re.split('\\s+',item)
            clauses.append(two_parts[0])
        print(f"acl_dot1x_find_clauses: the list of acl 8021x entries = {clauses}")
        self.clauses = clauses
        return clauses


    def acl_dot1x_clean_up(self,filter_name):
        self.acl_dot1x_find_clauses()
        switch_exec_cmd(self.switch.console,"conf switch acl 802-1X")
        for c in self.clauses:
            switch_exec_cmd(self.switch.console, f"delete {c} " )
        switch_exec_cmd(self.switch.console,"end")

        cmds = f"""
        config switch acl service custom
            delete {filter_name}
            next
        end
        """
        self.switch.config_cmds_fast(cmds)

    def config_acl_dotonex_simple(self,*args,**kwargs):
        sample = f"""
        config switch acl service custom
            edit {filter_name}
            set protocol IP
            next
        end
        config switch acl 802-1X
            edit 1
            set description "Test Filter-Id"
            set filter-id “Testing”
            config access-list-entry
            edit 1
            set description "Test ACL entry”
            config action
            set count enable
            set drop enable
            end
            config classifier
            set dst-ip-prefix 192.168.0.0 255.255.255.0
            set ether-type 0x0800
            set service "filter-id-service1"
            set src-ip-prefix 192.168.0.0 255.255.255.0
            set src-mac 00:00:00:00:00:00
            end
            next
            end
            next
            end
        """
        filter_name = kwargs["filter_name"]
        entry_index = kwargs["entry_index"]
        mac_address = kwargs["mac_address"]
        acl_index = kwargs["acl_index"]
        cmds = f"""
            config switch acl service custom
                edit {filter_name}
                set protocol IP
                next
            end
            config switch acl 802-1X
            edit {acl_index}
                config access-list-entry
                    edit {entry_index}
                        config action
                            set count enable
                        end
                        config classifier
                            set ether-type 0x0800
                            set src-mac {mac_address}
                        end
                    next
                end
                set filter-id {filter_name}
            next
        end
        """
        self.switch.config_cmds_fast(cmds)

    def remove_acl_dotonex_simple(self,*args,**kwargs):
        
        filter_name = kwargs["filter_name"]
        acl_index = kwargs["acl_index"]
        cmds = f"""
        config switch acl 802-1X
            delete {acl_index}
            next
        end
        config switch acl service custom
                delete {filter_name}
        end
        """
        self.switch.config_cmds_fast(cmds)

class switch_acl_ingress(Switch_ACL):
    def __init__(self,*args,**kwargs):
        # self.switch = args[0]
        # self.clauses = None
        super().__init__(*args,**kwargs)
        #self.config_explicit_drop()

    def config_explicit_drop(self,index,group,intf):
        cmds = f"""
        config switch acl ingress
        edit {index}
                set group {group}
                set ingress-interface {intf}
                config action
                    set count enable
                    set drop enable
                end
            next
        end
        """
        self.switch.config_cmds_fast(cmds)

    def config_explicit_allow(self,index,group,intf):
        cmds = f"""
        config switch acl ingress
        edit {index}
                set group {group}
                set ingress-interface {intf}
                config action
                    set count enable
                    set drop disable
                end
            next
        end
        """
        self.switch.config_cmds_fast(cmds)


    def config_acl_ingress_jinja(self,acl_yaml):
        sample = """
        hostname {{ name }}

        interface Loopback1
        ip address 10.1.1.{{ id }} 255.255.255.255

        {% for vlan, name in vlans.items() %}
        vlan {{ vlan }}
         name {{ name }}
        {% endfor -%}

        router bgp {{ id }}
        {% for neighbor in bgp %}
         neighbor {{ neighbor.neighbor }} remote-as {{ neighbor.remote_as }}
        {% endfor %}
        """

        jinja_string = """
        config switch acl ingress   
        edit {{ index }}
                {% for key, value in globals_config.items() %}
                set {{ key }} {{ value }}
                {% endfor -%}
                config classifier
                    {% for key, value in classifiers.items() %}
                    set {{ key }} {{ value }}
                    {% endfor -%}
                end
                config action
                {% for key, value in actions.items() %}
                    set {{ key }} {{ value }}
                {% endfor -%}
                 end
            next 
        end
        """
        config = yaml.safe_load(acl_yaml)
        template = Template(jinja_string)
        result = template.render(config)
        self.switch.config_cmds_fast(result)


    def config_acl6_generic(self,index,globals,classifiers,actions):
        example = """
        config switch acl ingress
        edit 1
                set group 3
                set ingress-interface port2
                config classifier
                    set dst-ip6-prefix 2001:10:1:1::1/64
                    set src-ip6-prefix 2001:10:1:1::2/64
                end
                config action
                    set count enable
                end
            next
        end
        """
         
        cmds = f"""
        config switch acl ingress
        """
        cmds += f"""
        edit {index}
        """
        if globals != {}:
            for k,v in globals.items():
                cmds += f"""
                set {k} {v}
                """
        if  classifiers != {}:
            cmds += f"""
            config classifier
            """

            for k,v in classifiers.items():
                cmds += f"""
                set {k} {v}
                """
            cmds += f"""
            end
            """
        if  actions != {}:
            cmds += f"""
            config action
            """
            for k,v in actions.items():
                cmds += f"""
                set {k} {v}
                """
            cmds += f"""
            end
            """
        cmds += f"""
            next
        end
        """
        self.switch.config_cmds_fast(cmds)

    def config_acl6_basic(self,*args,**kwargs):
        example = """
        config switch acl ingress
        edit 1
                set group 3
                set ingress-interface port2
                config classifier
                    set dst-ip6-prefix 2001:10:1:1::1/64
                    set src-ip6-prefix 2001:10:1:1::2/64
                end
                config action
                    set count enable
                end
            next
        end
        """
        
        src=kwargs["src"]
        dst=kwargs["dst"]
        intf=kwargs["intf"]
        index=kwargs["index"]
        group_id=kwargs["group_id"]
        cmds = f"""
        config switch acl ingress
        edit {index}
                set group {group_id}
                set ingress-interface {intf}
                config classifier
                    set dst-ip6-prefix {dst}
                    set src-ip6-prefix {src}
                end
                config action
                    set count enable
                end
            next
        end
        """
        self.switch.config_cmds_fast(cmds)


    def acl_basic_config(self):
        basic_config_access_list(self.switch.console)

    def acl_ingress_find_clauses(self):
        result = collect_edit_items_general(self.switch.console,"config switch acl ingress",keyword="acl")
        print(result)
        clauses = []
        for item in result:
            two_parts = re.split('\\s+',item)
            clauses.append(two_parts[0])
        print(clauses)
        self.clauses = clauses
        return clauses


    def acl_ingress_clean_up(self):
        self.acl_ingress_find_clauses()
        switch_exec_cmd(self.switch.console,"config switch acl ingress")
        for c in self.clauses:
            switch_exec_cmd(self.switch.console, f"delete {c} " )
        switch_exec_cmd(self.switch.console,"end")


class Router_access_list:
    def __init__(self,*args,**kargs):
        self.switch = args[0]

    def config_acl(self,*args,**kwargs):
        pass


    def acl_basic_config(self):
        basic_config_access_list(self.switch.console)

    def router_acl_find_clauses(self):
        result = collect_edit_items(self.switch.console,"config router access-list")
        print(result)
        clauses = []
        for item in result:
            two_parts = re.split('\\s+',item)
            clauses.append(two_parts[0])
        print(clauses)
        self.clauses = clauses
        return clauses

    def clean_up(self):
        self.router_acl_find_clauses()
        switch_exec_cmd(self.switch.console,"config router route-map")
        for c in self.clauses:
            switch_exec_cmd(self.switch.console, f"delete {c} " )
        switch_exec_cmd(self.switch.console,"end")


class Router_route_map:
    def __init__(self,*args,**kwargs):
        self.switch = args[0]

    def community_config(self):
        route_map_community(self.switch.console)

    def routemap_basic_config(self):
        basic_config_route_map(self.switch.console)

    def aspath_map(self,*args,**kwargs):
        name = kwargs['name']
        as_num = kwargs['as_num']
        config = f"""
        config router route-map
         edit {name}
            set protocol bgp
                config rule
                  edit 1
                    set set-aspath {as_num}                         
                next
            end
        next
        end
        """
        config_cmds_lines(self.switch.console,config)

    def config_atomic_aggregate(self,*args,**kwargs):
        name = kwargs['name']
        agg_as = kwargs['agg_as']
        ip = kwargs['ip']


        config = f"""
        config router route-map
        edit {name}
            set protocol bgp
                config rule
                    edit 1
                        set set-aggregator-as {agg_as}
                        set set-aggregator-ip {ip}
                        set set-atomic-aggregate enable
                    next
                end
        next
        end
        """
        config_cmds_lines(self.switch.console,config)


    def find_clauses(self):
        result = collect_edit_items(self.switch.console,"config router route-map")
        print(result)
        clauses = []
        for item in result:
            two_parts = re.split('\\s+',item)
            clauses.append(two_parts[0])
        print(clauses)
        self.clauses = clauses
        return clauses


    def routemap_clean_up(self):
        self.find_clauses()
        switch_exec_cmd(self.switch.console,"config router route-map")
        for c in self.clauses:
            switch_exec_cmd(self.switch.console, f"delete {c} " )
        switch_exec_cmd(self.switch.console,"end")

    def unsuppress_map(self):

        config = """
        config router route-map
            edit "suppress-map-4"
                set protocol bgp
                    config rule
                        edit 1
                            set match-ip-address "unsuppress-list"
                        next
                    end
            next
            edit "unsuppress-map-6"
                set protocol bgp
                    config rule
                        edit 1
                            set match-ip6-address "unsuppress-list-v6"
                        next
                    end
            next
        end
        """
        config_cmds_lines(self.switch.console,config)

class Ospf_Neighbor:
    def __init__(self,*args,**kargs):
        neighbor_dict = args[0]
        self.id = neighbor_dict["id"]
        self.pri = neighbor_dict["pri"]
        self.state = neighbor_dict["state"]
        self.address = neighbor_dict['address']
        self.dead = neighbor_dict['dead']
        self.interface = neighbor_dict["interface"]

    def show_details(self):
        tprint("====================================================")
        tprint(f"Neighbor router id: {self.id}")
        tprint(f"Neighbor OSPF Priority: {self.pri}")
        tprint(f"Neighbor OSPF state: {self.state}")
        tprint(f"Neighbor Dead Time: {self.dead}")
        tprint(f"Neighbor Address: {self.address}")
        tprint(f"Neighbor Interface: {self.interface}")

class Ospf_Neighbor_v6:
    def __init__(self,*args,**kargs):
        neighbor_dict = args[0]
        self.id = neighbor_dict["id"]
        self.pri = neighbor_dict["pri"]
        self.state = neighbor_dict["state"]
        self.duration = neighbor_dict['duration']
        self.dead = neighbor_dict['dead']
        self.interface = neighbor_dict["interface"]

    def show_details(self):
        tprint("====================================================")
        tprint(f"Neighbor OSPFv3 router id: {self.id}")
        tprint(f"Neighbor OSPFv3 Priority: {self.pri}")
        tprint(f"Neighbor OSPFv3 state: {self.state}")
        tprint(f"Neighbor OSPFv3 Dead Time: {self.dead}")
        tprint(f"Neighbor OSPPv3 Duration: {self.duration}")
        tprint(f"Neighbor OSPFv3 Interface: {self.interface}")


class Router_ISIS:
    def __init__(self,*args,**kargs):
        self.switch = args[0]
        self.dut = self.switch.console
        self.neighbor_list = []
        self.neighbor_list_v6 = []
        #self.change_router_id(self.switch.loop0_ip)

    def show_isis_neighbor_v4(self):
        switch_show_cmd(self.dut, "get router info isis neighbor")

    def config_interface_isis(self,*args,**kwargs):
        interface = kwargs["interface"]
        isis_level = kwargs["circuit_type"]

        config = f"""
        config router isis
        config interface
            edit {interface}
                set circuit-type {isis_level}
            next
        end
        end
        """
        config_cmds_lines(self.dut,config,device=self.switch)

    def config_net(self,*args,**kwargs):
        isis_net = kwargs['net']
        config = f"""
        config router isis
            config net
                edit 1
                    set net {isis_net}
                next
            end
        """
        config_cmds_lines(self.dut,config,device=self.switch)

class Router_OSPF:
    def __init__(self,*args,**kargs):
        self.switch = args[0]
        self.dut = self.switch.console
        self.neighbor_list = []
        self.neighbor_list_v6 = []
        #self.change_router_id(self.switch.loop0_ip)

    def config_general(self,*args,**kwargs):

        router_id = kwargs["router_id"]
        area_ip = kwargs["area"]

        #area_ip should mostly be 0.0.0.0
        config = f"""
        config router ospf
        set router-id {router_id}
        config area
            edit {area_ip}
            next
        end
        end
        """

        config_cmds_lines(self.dut,config,device=self.switch)

    def config_network(self,*args,**kwargs):
        index = kwargs["index"]
        ip = kwargs["ip"]
        mask = kwargs["mask"]

        config = f"""
        config router ospf
        config network
            edit {index}
            set area 0.0.0.0
            set prefix {ip} {mask}
            next
        end
        end
        """
        config_cmds_lines(self.dut,config,device=self.switch)

    def config_interface_ospf(self,*args,**kwargs):
        interface = kwargs["interface"]

        config = f"""
        config router ospf
        config interface
            edit {interface}
            next
        end
        end
        """
        config_cmds_lines(self.dut,config,device=self.switch)


    def remove_ospf_all(self):
        self.remove_ospf_v4()
        self.remove_ospf_v6()

    def remove_ospf_v4(self):
        vlans = self.switch.find_vlan_interfaces()
        for v in vlans:
            ospf_config = f"""
            config router ospf 
                config interface
                    delete {v}
                end
            end
            """
            config_cmds_lines(self.dut,ospf_config)

        for n in range(5):
            ospf_config = f"""
                config router ospf 
                config network
                    delete {n}
                end 
            end
            """
            config_cmds_lines(self.dut,ospf_config)

        redistributed_list = ["connected","static","bgp","rip","isis"]
        for d in redistributed_list:
            ospf_config = f"""
                config router ospf 
                    config redistribute {d}
                        set status disable
                    end
                end
                """
            config_cmds_lines(self.dut,ospf_config)

    def remove_ospf_v6(self):
        vlans = self.switch.find_vlan_interfaces()
        for v in vlans:
            ospf_config = f"""
            config router ospf6 
                config interface
                    delete {v}
                end 
            end
            """
            config_cmds_lines(self.dut,ospf_config)

        redistributed_list = ["connected","static","bgp","ripng","isis"]
        for d in redistributed_list:
            ospf_config = f"""
                config router ospf6 
                    config redistribute {d}
                        set status disable
                    end
                end
                """
            config_cmds_lines(self.dut,ospf_config)

    def update_switch(self,switch):
        self.switch = switch
        self.dut = switch.console

    def basic_config_fabric(self):
        if self.switch.is_fortinet() == False:
            return 
        if self.switch.software_version == "6.2.0":
            ospf_config = f"""
            config router ospf
            set router-id {self.switch.loop0_ip}
                config area
                    edit 0.0.0.0
                    next
                end
                config ospf-interface
                    edit "1"
                        set interface "vlan1000"
                    next
                end
                config network
                    edit 1
                        set area 0.0.0.0
                        set prefix {self.switch.vlan1000_subnet} 255.255.255.0
                    next
                end
                config network
                    edit 2
                        set area 0.0.0.0
                        set prefix {self.switch.loop0_ip} 255.255.255.255
                    next
                end
                config redistribute "connected"
                    set status enable
                end
                config redistribute "static"
                    set status enable
                end
            end
            end
            """
        else:
            ospf_config = f"""
            config router ospf
            set router-id {self.switch.loop0_ip}
                config area
                    edit 0.0.0.0
                    next
                end
                config interface
                    edit vlan1000
                    next
                end
                 
                config network
                    edit 1
                        set area 0.0.0.0
                        set prefix {self.switch.vlan1000_subnet} 255.255.255.0
                    next
                end
                config network
                    edit 2
                        set area 0.0.0.0
                        set prefix {self.switch.loop0_ip} 255.255.255.255
                    next
                end
                config redistribute "connected"
                    set status enable
                end
                 config redistribute "static"
                    set status enable
                end
            end
            end
            """
        config_cmds_lines(self.dut,ospf_config)

    def basic_config(self):
        if self.switch.is_fortinet() == False:
            return 
        if self.switch.software_version == "6.2.0":
            ospf_config = f"""
            config router ospf
            set router-id {self.switch.loop0_ip}
                config area
                    edit 0.0.0.0
                    next
                end
                config ospf-interface
                    edit "1"
                        set interface "vlan1"
                    next
                end
                config network
                    edit 1
                        set area 0.0.0.0
                        set prefix {self.switch.vlan1_subnet} 255.255.255.0
                    next
                end
                config network
                    edit 2
                        set area 0.0.0.0
                        set prefix {self.switch.loop0_ip} 255.255.255.255
                    next
                end
                config redistribute "connected"
                    set status enable
                end
            end
            """
        else:
            ospf_config = f"""
            config router ospf
            set router-id {self.switch.loop0_ip}
                config area
                    edit 0.0.0.0
                    next
                end
                config interface
                    edit vlan1
                    next
                end
                 
                config network
                    edit 1
                        set area 0.0.0.0
                        set prefix {self.switch.vlan1_subnet} 255.255.255.0
                    next
                end
                config network
                    edit 2
                        set area 0.0.0.0
                        set prefix {self.switch.loop0_ip} 255.255.255.255
                    next
                end
                config redistribute "connected"
                    set status enable
                end
            end
            """
        config_cmds_lines(self.dut,ospf_config)

    def basic_config_v6_fabric(self):
        if self.switch.is_fortinet() == False:
            return 
        ospf_config = f"""
            config router ospf6
            set router-id {self.switch.loop0_ip}
                config area
                    edit 0.0.0.0
                    next
                end
                config interface
                    edit vlan1000
                    next
                end
                config redistribute "connected"
                    set status enable
                end
                config redistribute "static"
                    set status enable
                end
            end
            """
        config_cmds_lines(self.dut,ospf_config)

    def basic_config_v6(self):
        if self.switch.is_fortinet() == False:
            return 
        ospf_config = f"""
            config router ospf6
            set router-id {self.switch.loop0_ip}
                config area
                    edit 0.0.0.0
                    next
                end
                config interface
                    edit vlan1
                    next
                end
                config redistribute "connected"
                    set status enable
                end
            end
            """
        config_cmds_lines(self.dut,ospf_config)

    def show_protocol_states(self):
        self.show_config()
        self.show_ospf_neighbors()
        self.show_hardware_l3()

    def show_protocol_states_v6(self):
        self.show_ospf_config_v6()
        self.show_ospf_neighbor_v6()
        self.show_hardware_l3()

    def show_config(self):
        switch_show_cmd(self.switch.console,"show router ospf")

    def show_ospf_config_v6(self):
        switch_show_cmd(self.switch.console,"show router ospf6")

    def show_ospf_neighbor_v6(self):
        switch_show_cmd(self.dut, "get router info6 ospf neighbor")

    def show_ospf_neighbor_v4(self):
        switch_show_cmd(self.dut, "get router info ospf neighbor")

    def show_ospf_neighbor_v64(self):
        switch_show_cmd(self.dut, "get router info6 ospf neighbor")
        switch_show_cmd(self.dut, "get router info ospf neighbor")

    def show_hardware_l3(self):
        switch_show_cmd(self.dut,"diagnose hardware switchinfo l3-summary")

    def change_router_id(self,id):
        ospf_config = f"""
        config router ospf
            set router-id {id}
        end
        """
        config_cmds_lines(self.dut,ospf_config)

    def announce_loopbacks(self,num):
        dut = self.switch.console
        net,host = ip_break_up(self.switch.loop0_ip)
        if net == None or host == None:
            tprint("Something is wrong with loopback address breakup" )
            return False

        self.change_router_id(self.switch.loop0_ip)
        for i in range(2,num+2):
            ospf_config = f"""
            config router ospf
                config network
                    edit {i}
                        set area 0.0.0.0
                        set prefix {net}.{int(host)+i} 255.255.255.255
                    next
                end
            end
            """
        config_cmds_lines(self.dut,ospf_config)

    def update_neighbors(self):
        self.neighbor_list = self.neighbor_discovery()

    def neighbor_discovery(self):
        if self.switch.is_fortinet() == False:
            return
        dut = self.dut
        neighbor_dict_list = get_router_info_ospf_neighbor(dut)
        neighbor_list = []
        for n in neighbor_dict_list:
            neighbor = Ospf_Neighbor(n)
            neighbor_list.append(neighbor)
        self.neighbor_list = neighbor_list
        return neighbor_list

    def neighbor_discovery_v6(self):
        if self.switch.is_fortinet() == False:
            return 
        dut = self.dut
        neighbor_dict_list = get_router_info_ospf_neighbor_v6(dut)
        neighbor_list = []
        for n in neighbor_dict_list:
            neighbor = Ospf_Neighbor_v6(n)
            neighbor_list.append(neighbor)
        self.neighbor_list_v6 = neighbor_list
        return neighbor_list

    def neighbor_discovery_all(self):
        if self.switch.is_fortinet() == False:
            return 
        dut = self.dut

        #discover IPv4 ospf neighbors
        neighbor_dict_list = get_router_info_ospf_neighbor(dut)
        neighbor_list = []
        for n in neighbor_dict_list:
            neighbor = Ospf_Neighbor(n)
            neighbor_list.append(neighbor)
        self.neighbor_list = neighbor_list

        #discover IPv6 ospf neighbors
        neighbor_dict_list = get_router_info_ospf_neighbor_v6(dut)
        neighbor_list = []
        for n in neighbor_dict_list:
            neighbor = Ospf_Neighbor_v6(n)
            neighbor_list.append(neighbor)
        self.neighbor_list_v6 = neighbor_list

    def show_ospf_neighbors(self):
        if self.switch.is_fortinet() == False:
            return 
        for neighbor in self.neighbor_list:
            neighbor.show_details()

    def show_ospf_neighbors_v6(self):
        if self.switch.is_fortinet() == False:
            return 
        for neighbor in self.neighbor_list_v6:
            neighbor.show_details()

    def show_ospf_neighbors_all(self):
        if self.switch.is_fortinet() == False:
            return 
        for neighbor in self.neighbor_list:
            neighbor.show_details()
        for neighbor in self.neighbor_list_v6:
            neighbor.show_details()

    def add_network_entries(self,prefixes,masks):
        i=0
        for prefix,mask in zip(prefixes,masks):
            i+=1 
            ospf_config = f"""
            config router ospf
                config network
                    edit {i}
                    set area 0.0.0.0
                    set prefix {prefix} {mask}
                end
            end
            """
            config_cmds_lines(self.dut,ospf_config)


    def delete_network_entries(self):
        ospf_config = f"""
        config router ospf
            config network
                delete 1
                delete 2
            end
        end
        """
        config_cmds_lines(self.dut,ospf_config)

    def disable_redistributed_connected(self):
        ospf_config = f"""
        config router ospf
         
        config redistribute "connected"
            set status disable
        end
        end
        """
        config_cmds_lines(self.dut,ospf_config)

    def enable_redistributed_connected(self):
        ospf_config = f"""
        config router ospf
         
        config redistribute "connected"
            set status enable
        end
        end
        """
        config_cmds_lines(self.dut,ospf_config)

    def ospf_neighbor_all_up_v4(self,*args,**kwargs):
        if self.switch.is_fortinet() == False:
            return 
        neighbor_num = 0
        if "num" in kwargs:
            expected_neighbor_nums = kwargs['num']
        else:
            expected_neighbor_nums = 0
        for neighbor in self.neighbor_list:
            if re.match(r'[0-9]+\.[0-9]+s',neighbor.dead):
                neighbor_num += 1
                print(f"ospf_neighbor_all_up_v4(): neighbor {neighbor.id} up")
        
        print(f"ospf_neighbor_all_up_v4: Total number of ospf neighbors found = {neighbor_num}")

        if neighbor_num == expected_neighbor_nums:
            return True
        else:
            return False

     #    4 :: 3032D-R7-40 # get router info6 ospf neighbor
     # 020-08-31 22:07:44 :: Neighbor ID     Pri    DeadTime    State/IfState         Duration I/F[State]
     # 020-08-31 22:07:44 :: 1.1.1.1           1    00:00:38   Twoway/DROther       4d08:49:16 vlan1[DROther]
     # 020-08-31 22:07:44 :: 3.3.3.3           1    00:00:39   Twoway/DROther       4d08:49:19 vlan1[DROther]
     # 020-08-31 22:07:44 :: 4.4.4.4           1    00:00:38     Full/DR            4d08:49:22 vlan1[DROther]
     # 020-08-31 22:07:44 :: 5.5.5.5           1    00:00:38     Full/BDR           3d09:34:01 vlan1[DROther]
     # 020-08-31 22:07:44 :: 6.6.6.6           1    00:00:38   Twoway/DROther       3d09:33:35 vlan1[DROther]

    def ospf_neighbor_all_up_v6(self,*args,**kwargs):
        if self.switch.is_fortinet() == False:
            return
        neighbor_num = 0
        if "num" in kwargs:
            expected_neighbor_nums = kwargs['num']
        else:
            expected_neighbor_nums = 0
        for neighbor in self.neighbor_list_v6:
            if re.match(r'[0-9a-z]+\:[0-9]+\:[0-9]',neighbor.duration):
                neighbor_num += 1
                print(f"ospf_neighbor_all_up_v6(): neighbor {neighbor.id} up")
        
        print(f"ospf_neighbor_all_up_v6: Total number of ospf neighbors found = {neighbor_num}")

        if neighbor_num == expected_neighbor_nums:
            return True
        else:
            return False

     #    4 :: 3032D-R7-40 # get router info6 ospf neighbor
     # 020-08-31 22:07:44 :: Neighbor ID     Pri    DeadTime    State/IfState         Duration I/F[State]
     # 020-08-31 22:07:44 :: 1.1.1.1           1    00:00:38   Twoway/DROther       4d08:49:16 vlan1[DROther]
     # 020-08-31 22:07:44 :: 3.3.3.3           1    00:00:39   Twoway/DROther       4d08:49:19 vlan1[DROther]
     # 020-08-31 22:07:44 :: 4.4.4.4           1    00:00:38     Full/DR            4d08:49:22 vlan1[DROther]
     # 020-08-31 22:07:44 :: 5.5.5.5           1    00:00:38     Full/BDR           3d09:34:01 vlan1[DROther]
     # 020-08-31 22:07:44 :: 6.6.6.6           1    00:00:38   Twoway/DROther       3d09:33:35 vlan1[DROther]

class BGP_Neighbor:
    def __init__(self,*args,**kargs):
        # Neighbor        V         AS MsgRcvd MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd
        try:
            neighbor_dict = args[0]
            self.switch= args[1]
            self.id = neighbor_dict["Neighbor"]
            self.version = neighbor_dict["V"]
            self.AS = neighbor_dict["AS"]
            self.received_msg = neighbor_dict['MsgRcvd']
            self.sent_msg = neighbor_dict['MsgSent']
            self.table_version = neighbor_dict["TblVer"]
            self.inq = neighbor_dict["InQ"]
            self.outq = neighbor_dict["OutQ"]
            self.up_timer = neighbor_dict["Up/Down"]
        except:
            print("BGP neighbor discovery did not work, BGP Neighbor Initialization failed")
        try:
            self.prefix_recieved = int(neighbor_dict["State/PfxRcd"])
        except Exception as e:
            self.prefix_recieved = neighbor_dict["State/PfxRcd"]


    def nei_config_unsuppress(self,map_name):
        config = f"""
        config router bgp
                config neighbor
                   edit {self.id}
                set remote-as 65000
                set unsuppress-map {map_name}
                set update-source "loop0"
            next
            end
        end
        """
        config_cmds_lines(self.switch.console,config)

    def show_details(self):
        tprint("====================================================")
        tprint(f"Neighbor router id: {self.id}")
        tprint(f"Neighbor BGP Version: {self.version}")
        tprint(f"Neighbor BGP AS #: {self.AS}")
        tprint(f"Neighbor MSG received: {self.received_msg}")
        tprint(f"Neighbor Table Version: {self.table_version}")
        tprint(f"Neighbor Ingress Q: {self.inq}")
        tprint(f"Neighbor Egress Q: {self.outq}")
        tprint(f"Neighbor Up Timer: {self.up_timer}")
        tprint(f"Neighbor Prefix Received: {self.prefix_recieved}")


    def set_weight_routes_neighbor(self,value):
        self.remove_all_filters()
        config = f"""
        config router bgp
     
        config neighbor
            edit {self.id}
                set weight {value}
            next
        end
        end
        """
        config_cmds_lines(self.switch.console,config)

    def config_md5_password(self):
        self.remove_all_filters()
        config = f"""
        config router bgp
     
        config neighbor
            edit {self.id}
                set password lab
            next
        end
        end
        """
        config_cmds_lines(self.switch.console,config)

    def default_route_originated(self):
        self.remove_all_filters()
        config = f"""
        config router bgp
     
        config neighbor
            edit {self.id}
                set capability-default-originate enable
            next
        end
        end
        """
        config_cmds_lines(self.switch.console,config)


    def add_prefix_list_in(self,*args,**kwargs):
        prefix = kwargs['prefix']

        config = f"""
        config router bgp
     
        config neighbor
            edit {self.id}
                set prefix-list-in  {prefix}
            next
        end
        end
        """
        config_cmds_lines(self.switch.console,config)

    def configure_orf_prefix(self,*args,**kwargs):
        prefix = kwargs['prefix']
        config = f"""
        config router bgp
            config neighbor
             edit {self.id}
             set capability-orf both
             next
        end
        """
        config_cmds_lines(self.switch.console,config)
        self.add_prefix_list_in(prefix)

    def add_prefix_list_out(self,*args,**kwargs):
        prefix = kwargs['prefix']

        config = f"""
        config router bgp
     
        config neighbor
            edit {self.id}
                set prefix-list-out {prefix}
            next
        end
        end
        """
        config_cmds_lines(self.switch.console,config)

    def remove_prefix_list(self,*args,**kwargs):
         
        config = f"""
        config router bgp
     
        config neighbor
            edit {self.id}
                unset prefix-list-in   
                unset prefix-list-out
            next
        end
        end
        """
        config_cmds_lines(self.switch.console,config)

    def add_distribute_list_in(self,*args,**kwargs):
        distribute = kwargs['distribute']

        config = f"""
        config router bgp
     
        config neighbor
            edit {self.id}
                set distribute-list-in {distribute}
            next
        end
        end
        """
        config_cmds_lines(self.switch.console,config)

    def add_distribute_list_out(self,*args,**kwargs):
        distribute = kwargs['distribute']

        config = f"""
        config router bgp
     
        config neighbor
            edit {self.id}
                set distribute-list-out {distribute}
            next
        end
        end
        """
        config_cmds_lines(self.switch.console, config)

    def remove_distribute_list(self,*args,**kwargs):

        config = f"""
        config router bgp
     
        config neighbor
            edit {self.id}
                unset distribute-list-out
                unset distribute-list-in
            next
        end
        end
        """
        config_cmds_lines(self.switch.console,config)

    def add_aspath_in(self,*args,**kwargs):
        aspath = kwargs['aspath']

        config = f"""
        config router bgp
     
        config neighbor
            edit {self.id}
                set aspath-filter-list-in {aspath}
            next
        end
        end
        """
        config_cmds_lines(self.switch.console,config)

    def add_aspath_out(self,*args,**kwargs):
        aspath = kwargs['aspath']

        config = f"""
        config router bgp
     
        config neighbor
            edit {self.id}
                set aspath-filter-list-out {aspath}
            next
        end
        end
        """
        config_cmds_lines(self.switch.console,config)

    def remove_aspath_list(self):
        config = f"""
        config router bgp
     
        config neighbor
            edit {self.id}
                unset aspath-filter-list-out  
                unset aspath-filter-list-in
            next
        end
        end
        """
        config_cmds_lines(self.switch.console,config)

    def add_route_map_in(self,*args,**kwargs):
        route_map = kwargs['route_map']

        config = f"""
        config router bgp
     
        config neighbor
            edit {self.id}
                set route-map-in {route_map}
            next
        end
        end
        """
        config_cmds_lines(self.switch.console,config)

    def add_route_map_out(self,*args,**kwargs):
        route_map = kwargs['route_map']

        config = f"""
        config router bgp
     
        config neighbor
            edit {self.id}
                set route-map-out {route_map}
            next
        end
        end
        """
        config_cmds_lines(self.switch.console,config)

    def remove_route_map_in(self,*args,**kwargs):
        if "route_map" in kwargs:
            route_map = kwargs['route_map']

        config = f"""
        config router bgp
     
        config neighbor
            edit {self.id}
                unset route-map-in 
            next
        end
        end
        """
        config_cmds_lines(self.switch.console,config)

    def remove_route_map_out(self,*args,**kwargs):
        if "route_map" in kwargs:
            route_map = kwargs['route_map']

        config = f"""
        config router bgp
     
        config neighbor
            edit {self.id}
                unset route-map-out 
            next
        end
        end
        """
        config_cmds_lines(self.switch.console,config)

    def remove_route_maps(self,*args,**kwargs):
        
        config = f"""
        config router bgp
     
        config neighbor
            edit {self.id}
                unset route-map-out 
                unset route-map-in
            next
        end
        end
        """

    def remove_all_filters(self,*args,**kwargs):
        
        config = f"""
        config router bgp
     
        config neighbor
            edit {self.id}
                unset route-map-out 
                unset route-map-in
                unset aspath-filter-list-out  
                unset aspath-filter-list-in
                unset prefix-list-in   
                unset prefix-list-out
                unset distribute-list-out
                unset distribute-list-in
            next
        end
        end
        """
        config_cmds_lines(self.switch.console,config)



class BGP_Network:

    # 548D-R8-33 # get router info6 bgp network
    # router_daemon_sync_timezone:43 not implemented
    # BGP table version is 1130, local router ID is 6.6.6.6, vrf id 0
    # Default local pref 100, local AS 65000
    # Status codes:  s suppressed, d damped, h history, * valid, > best, = multipath,
    #                i internal, r RIB-failure, S Stale, R Removed
    # Nexthop codes: @NNN nexthop's vrf id, < announce-nh-self
    # Origin codes:  i - IGP, e - EGP, ? - incomplete

    #    Network          Next Hop            Metric LocPrf Weight Path
    # *>i2001:101:1:1::1/128
    #                     2001:10:1:1::213
    #                                                   100      0 103 i
    # *>i2001:101:1:1::2/128
    #                     2001:10:1:1::213
    #                                                   100      0 103 i
    # *>i2001:101:1:1::3/128
    #                     2001:10:1:1::213
    #                                                   100      0 103 i
    # *>i2001:101:1:1::4/128
    #                     2001:10:1:1::213
    #                                                   100      0 103 i
    # *>i2001:101:1:1::5/128
    #                     2001:10:1:1::213
    #                                                   100      0 103 i
    def __init__(self,*args,**kwargs):
        self.router_bgp = kwargs["router_bgp"]
        self.af = kwargs["af"]
        self.network = None
        self.next_hop = None
        self.metric = None
        self.local_preference = None
        self.weight = None
        self.path = None


class Router_BGP:
    def __init__(self,*args,**kwargs):
        self.switch = args[0]
        self.ospf_neighbors = [n.id for n in self.switch.router_ospf.neighbor_list]
        self.ospf_neighbors_address = [n.address for n in self.switch.router_ospf.neighbor_list]
        self.router_id = self.switch.loop0_ip
        self.ibgp_as = 65000
        self.ebgp_as = self.switch.ebgp_as
        self.confed_id = 5000
        self.bgp_neighbors_objs = None
        self.ixia_port_info = None
         
        self.ospf_neighbors = None
        self.ospf_neighbors_address = None # this is the same as self.ospf_neighbors_address_vlan1_v4. Just keep it for backward compatibility
        self.ospf_neighbors_address_vlan1_v4 = None
        self.ospf_neighbors_address_loop0_v4 =  None
        self.ospf_neighbors_swlist_v4 = None
        #v6 neighbors
        self.ospf_neighbors_v6 = None
        self.ospf_neighbors_address_vlan1_v6 =  None
        self.ospf_neighbors_address_loop0_v6 =  None
        self.ospf_neighbors_swlist_v6 =  None
        self.bgp_config_neighbors = None #Need to be found by using find_bgp_config_neighbors(dut)
        self.local_as = 65000
        #self.route_map = Router_route_map()

    def config_bgp_basic(self):
        bgp_config = f"""
        config router bgp
            set as {self.local_as}
            set router-id {self.router_id}
        end
        """
        config_cmds_lines(self.switch.console,bgp_config)

    def clear_bgp_all(self):
        config = "execute router clear bgp all"
        config_cmds_lines(self.switch.console,config)

    def config_all_neighbor_commands(self,cmds):
        self.update_bgp_config_neighbors()
        commands = split_f_string_lines(cmds)
        for n in self.bgp_config_neighbors:
            #for command in commands:
                config = f"""
                  config router bgp
                    config neighbor
                        edit {n}
                        {cmds}
                    end
                 end
                """
                config_cmds_lines(self.switch.console,config)

    def config_neighbor_command(self,*args,**kwargs):
        neighbor = kwargs['neighbor']
        command = kwargs['command']

        config = f"""
        config router bgp
            config neighbor
                edit {neighbor}
                {command}
            end
        end
        """
        config_cmds_lines(self.switch.console,config)


    def cisco_n9k_bgp(self):
        config = """
        router bgp 65000
        router bgp 65000
          router-id 10.10.10.10
          address-family ipv4 unicast
          neighbor 2001:1:1:1::1
            remote-as 65000
            update-source loopback0
            address-family ipv6 unicast
          neighbor 2001:2:2:2::2
            remote-as 65000
            update-source loopback0
            address-family ipv6 unicast
          neighbor 2001:3:3:3::3
            remote-as 65000
            update-source loopback0
            address-family ipv6 unicast
          neighbor 2001:4:4:4::4
            remote-as 65000
            update-source loopback0
            address-family ipv6 unicast
          neighbor 2001:5:5:5::5
            remote-as 65000
            update-source loopback0
            address-family ipv6 unicast
          neighbor 2001:6:6:6::6
            remote-as 65000
            update-source loopback0
            address-family ipv6 unicast
          neighbor 2001:10:1:1::1
            remote-as 65000
            update-source Vlan1
            address-family ipv6 unicast
          neighbor 2001:10:1:1::2
            remote-as 65000
            update-source Vlan1
            address-family ipv6 unicast
          neighbor 2001:10:1:1::3
            remote-as 65000
            update-source Vlan1
            address-family ipv6 unicast
          neighbor 2001:10:1:1::4
            remote-as 65000
            update-source Vlan1
            address-family ipv6 unicast
          neighbor 2001:10:1:1::5
            remote-as 65000
            update-source Vlan1
            address-family ipv6 unicast
          neighbor 2001:10:1:1::6
            remote-as 65000
            update-source Vlan1
            address-family ipv6 unicast
          neighbor 2001:10:1:1::213
            remote-as 103
            address-family ipv6 unicast
          neighbor 2001:10:1:1::214
            remote-as 104
            address-family ipv6 unicast
          neighbor fe80::6d5:90ff:fe2e:22a7
            remote-as 65000
            address-family ipv6 unicast
          neighbor fe80::724c:a5ff:fea5:a219
            remote-as 65000
            address-family ipv6 unicast
          neighbor fe80::926c:acff:fe0c:bceb
            remote-as 65000
            address-family ipv6 unicast
          neighbor fe80::926c:acff:fe13:9575
            remote-as 65000
            address-family ipv6 unicast
          neighbor fe80::926c:acff:fe6d:c951
            remote-as 65000
            address-family ipv6 unicast
          neighbor fe80::ea1c:baff:fe88:d15f
            remote-as 65000
            address-family ipv6 unicast
          neighbor 1.1.1.1
            remote-as 65000
            update-source loopback0
            address-family ipv4 unicast
          neighbor 2.2.2.2
            remote-as 65000
            update-source loopback0
            address-family ipv4 unicast
          neighbor 3.3.3.3
            remote-as 65000
            update-source loopback0
            address-family ipv4 unicast
          neighbor 4.4.4.4
            remote-as 65000
            update-source loopback0
            address-family ipv4 unicast
          neighbor 5.5.5.5
            remote-as 65000
            update-source loopback0
            address-family ipv4 unicast
          neighbor 6.6.6.6
            remote-as 65000
            update-source loopback0
            address-family ipv4 unicast
          neighbor 10.1.1.1
            remote-as 65000
            address-family ipv4 unicast
          neighbor 10.1.1.2
            remote-as 65000
            address-family ipv4 unicast
          neighbor 10.1.1.3
            remote-as 65000
            address-family ipv4 unicast
          neighbor 10.1.1.4
            remote-as 65000
            address-family ipv4 unicast
          neighbor 10.1.1.5
            remote-as 65000
            address-family ipv4 unicast
          neighbor 10.1.1.6
            remote-as 65000
            address-family ipv4 unicast
          neighbor 10.1.1.213
            remote-as 103
            address-family ipv4 unicast
          neighbor 10.1.1.214
            remote-as 104
            address-family ipv4 unicast
            end
        """
        config_cmds_lines(self.switch.console,config)

    def bgp_discover_networks(self,*args,**kwargs):  # Now it is just for V4
        if "af" in kwargs:
            af = kwargs['af']
        else:
            af = "v4"
        dut = self.swwitch.console
        if af == "v4":
            result = collect_show_cmd(dut,"get router info bgp network")
        elif af == "v6":
            result = collect_show_cmd(dut,"get router info6 bgp network")
        network_list = []
        #    Network          Next Hop            Metric LocPrf Weight Path

        network_regex = r"(^\*[\s=>i]+)(.+)"
        line1_regex = r"BGP table version is ([0-9]+), local router ID is ([0-9\.]+[0-9]+), vrf id ([0-9]+)"
        for line in result:
            matched = re.match(line1_regex,line)
            if matched:
                table_version = matched.group(1)
                router_id = matched.group(2)
                vrf_id = matched.group(3)
                continue
            matched_network = re.matche(network_regex,line)
            if matched_network:
                net_or_nhop = matched.group(2)
                net_or_nhop_list = net_or_nhop.split()
                if len(net_of_nhop_list) == 6:
                    if not network_dict == False:
                        network_list.append(network_dict)
                    network_dict = {}
                    network_dict["path_list"] = []
                    net_path_dict = {}
                    network_dict["network"] = net_or_nhop_list[0]

                    net_path_dict["nhop"] = net_or_nhop_list[1]
                    net_path_dict["metric"] = net_or_nhop_list[2]
                    net_path_dict["locprf"] = net_or_nhop_list[3]
                    net_path_dict['weight']= net_or_nhop_list[4]
                    net_path_dict["path"]= net_or_nhop_list[5]

                    network_dict["path_list"].append(net_path_dict)

                elif len(net_of_nhop_list) == 5:
                    net_path_dict = {}

                    net_path_dict["nhop"] = net_or_nhop_list[0]
                    net_path_dict["metric"] = net_or_nhop_list[1]
                    net_path_dict["locprf"] = net_or_nhop_list[2]
                    net_path_dict['weight']= net_or_nhop_list[3]
                    net_path_dict["path"]= net_or_nhop_list[4]

                    network_dict["path_list"].append(net_path_dict)
                else:
                    return network_list
        return network_list


    def bgp_config_unsuppress_map(self,map_name):
        for neighbor in self.bgp_neighbors_objs:
            neighbor.nei_config_unsuppress(map_name)

    def config_aggregate_summary_only(self, agge_net,mask_length):
        #example find_subnet("10.1.1.1",24)
        agg_net = find_subnet(self.ixia_network,mask_length)
        config = f"""
        config router bgp
            config aggregate-address
             edit 1
                set prefix {agg_net}/{mask_length}
                set summary-only enable
            next
            end
        end
        """
        config_cmds_lines(self.switch.console,config)

    def attach_ixia(self,ixia_port):
        self.ixia_port_info = ixia_port
        print(f"self.ixia_port_info = {self.ixia_port_info}")

    @property
    def ixia_network(self):
        return (self.ixia_port_info)[4]

    @ixia_network.setter 
    def ixia_network(self,ip_net):
        (self.ixia_port_info)[4] = ip_net

    @property
    def ixia_bgp_as(self):
        return (self.ixia_port_info)[5]

    @ixia_bgp_as.setter 
    def ixia_bgp_as(self,bgp_as):
        (self.ixia_port_info)[5] = bgp_as


    def update_switch(self,switch):
        self.switch = switch

    def check_network_exist(self,nets):
        return check_route_exist(dut=self.switch.console,networks=nets,cmd="get router info bgp network")


    def check_neighbor_status(self):
        if self.switch.is_fortinet() == False:
            return 
        Info(f"=================== Checking BGP neighbor status on switch {self.switch.name} =======================")
        self.get_neighbors_summary()
        result = True
        for neighbor in self.bgp_neighbors_objs:
            if type(neighbor.prefix_recieved) != int:
                tprint(f"!!!!!! {self.switch.name} has BGP neighbor {neighbor.id} Down")
                result = False
        if result == True:
            Info(f"==================== {self.switch.name} has all BGP neighbors up =================== ")
            # for neighbor in self.bgp_neighbors_objs:
            #     neighbor.show_details()
        return result

    def check_bgp_neighbor_status_v6(self):
        self.get_bgp_neighbors_summary_v6()
        result = True
        if self.bgp_neighbors_objs is None:
            Info(f"==================== {self.switch.name} has NO BGPv6 neighbors  =================== ")
            return False
        if len(self.bgp_neighbors_objs) == 0:
            Info(f"==================== {self.switch.name} has NO BGPv6 neighbors  =================== ")
            return False
        for neighbor in self.bgp_neighbors_objs:
            if type(neighbor.prefix_recieved) != int:
                tprint(f"!!!!!! {self.switch.name} has BGPv6 neighbor {neighbor.id} Down")
                result = False

        if result == False:
            Info(f"==================== {self.switch.name} has BGPv6 neighbors DOWN =================== ")
            for neighbor in self.bgp_neighbors_objs:
                neighbor.show_details()
        else:
            Info(f"==================== {self.switch.name} has all BGPv6 neighbors up =================== ")
        return result


    def add_ebgp_peer(self,*args,**kwargs):
        ip = kwargs['ip']
        remote_as = kwargs['remote_as']

        if '/' in ip:
            ip_addr,mask= seperate_ip_mask(ip)

        bgp_config = f"""
        config router bgp
            config neighbor
            edit {ip_addr}
                set remote-as {remote_as}
            next
            end
        end
        """
        config_cmds_lines(self.switch.console,bgp_config)

    def show_protocol_states(self):
        if self.switch.is_fortinet() == False:
            return 
        self.show_bgp_config()
        self.show_bgp_summary()
        self.show_bgp_network()
        self.show_bgp_routes()

    def show_bgp_protocol_states_v4(self):
        if self.switch.is_fortinet() == False:
            return 
        self.show_bgp_config()
        self.show_bgp_summary()
        self.show_bgp_network()
        self.show_bgp_routes()

    def show_bgp_protocol_states_v6(self):
        if self.switch.is_fortinet() == False:
            return 
        self.show_bgp_config_v6()
        self.show_bgp_summary_v6()
        self.show_bgp_network_v6()
        self.show_bgp_routes_v6()

    def show_bgp_network(self):
        if self.switch.is_fortinet() == False:
            return 
        dut = self.switch.dut
        switch_show_cmd(self.switch.console,"get router info bgp network")

    def show_bgp_network_v6(self):
        if self.switch.is_fortinet() == False:
            return 
        dut = self.switch.dut
        switch_show_cmd(self.switch.console,"get router info6 bgp network")

    def show_bgp_network_v64(self):
        if self.switch.is_fortinet() == False:
            return 
        dut = self.switch.dut
        switch_show_cmd(self.switch.console,"get router info6 bgp network")
        switch_show_cmd(self.switch.console,"get router info bgp network")

    def get_neighbors_summary(self):
        if self.switch.is_fortinet() == False:
            return 
        bgp_neighor_list = get_router_bgp_summary(self.switch.console)
        items_list = []
        for n_dict in bgp_neighor_list:
            n_obj = BGP_Neighbor(n_dict,self.switch)
            items_list.append(n_obj)
        self.bgp_neighbors_objs = items_list
        return items_list   

    def get_bgp_neighbors_summary_v6(self):
        if self.switch.is_fortinet() == False:
            return 
        items_list = []
        bgp_neighor_list = get_router_bgp_summary_v6(self.switch.console)
        if not bgp_neighor_list:
            self.bgp_neighbors_objs = items_list
            return items_list
        
        for n_dict in bgp_neighor_list:
            n_obj = BGP_Neighbor(n_dict,self.switch)
            n_obj.show_details()
            items_list.append(n_obj)
        self.bgp_neighbors_objs = items_list
        return items_list   

    def update_ospf_neighbors(self,*args,**kwargs):
        if self.switch.is_fortinet() == False:
            return
        if "sw_list" in kwargs:
            switch_list = kwargs['sw_list']
        else:
            switch_list = []
        self.ospf_neighbors = [n.id for n in self.switch.router_ospf.neighbor_list]
        self.ospf_neighbors_address = [n.address for n in self.switch.router_ospf.neighbor_list]

    def update_ospf_neighbors_v6(self,*args,**kwargs):
        if self.switch.is_fortinet() == False:
            return 
        if "sw_list" in kwargs:
            switch_list = kwargs['sw_list']
        else:
            switch_list = []
        self.ospf_neighbors_v6 = [n.id for n in self.switch.router_ospf.neighbor_list_v6]
        #Need to re-write!!!!
        self.ospf_neighbors_address_vlan1_v6 = [s.vlan1_ipv6.split('/')[0] for n in self.switch.router_ospf.neighbor_list_v6 for s in switch_list if n.id == s.loop0_ip ]
        self.ospf_neighbors_address_loop0_v6 = [s.loop0_ipv6.split('/')[0] for n in self.switch.router_ospf.neighbor_list_v6 for s in switch_list if n.id == s.loop0_ip ]
        self.ospf_neighbors_address_loop0_v4 = [s.loop0_ip for n in self.switch.router_ospf.neighbor_list_v6 for s in switch_list if n.id == s.loop0_ip ]
        print(f"ospf neighbors vlan1 ipv6 address = {self.ospf_neighbors_address_vlan1_v6}")
        print(f"ospf neighbors loop0 ipv6 address = {self.ospf_neighbors_address_loop0_v6}")

    def update_ospf_neighbors_all(self,*args,**kwargs):
        if self.switch.is_fortinet() == False:
            return 
        if "sw_list" in kwargs:
            switch_list = kwargs['sw_list']
        else:
            switch_list = []

        #v4 neighbors     
        self.ospf_neighbors = [n.id for n in self.switch.router_ospf.neighbor_list]
        self.ospf_neighbors_address = [n.address for n in self.switch.router_ospf.neighbor_list]
        self.ospf_neighbors_address_vlan1_v4 = self.ospf_neighbors_address
        self.ospf_neighbors_swlist_v4 = [s for n in self.switch.router_ospf.neighbor_list for s in switch_list if n.id == s.loop0_ip ]
        #v6 neighbors
        self.ospf_neighbors_v6 = [n.id for n in self.switch.router_ospf.neighbor_list_v6]
        self.ospf_neighbors_address_vlan1_v6 = [s.vlan1_ipv6.split('/')[0] for n in self.switch.router_ospf.neighbor_list_v6 for s in switch_list if n.id == s.loop0_ip ]
        self.ospf_neighbors_address_loop0_v6 = [s.loop0_ipv6.split('/')[0] for n in self.switch.router_ospf.neighbor_list_v6 for s in switch_list if n.id == s.loop0_ip ]
        self.ospf_neighbors_address_loop0_v4 = [s.loop0_ip for n in self.switch.router_ospf.neighbor_list_v6 for s in switch_list if n.id == s.loop0_ip ]
        self.ospf_neighbors_swlist_v6 = [s for n in self.switch.router_ospf.neighbor_list_v6 for s in switch_list if n.id == s.loop0_ip ]
        print(f"ospf neighbors vlan1 ipv6 address = {self.ospf_neighbors_address_vlan1_v6}")
        print(f"ospf neighbors loop0 ipv6 address = {self.ospf_neighbors_address_loop0_v6}")


    def config_ibgp_mesh_direct(self):
        if self.switch.is_fortinet() == False:
            return 
        tprint(f"============== Configurating iBGP at {self.switch.name} ")
        dut=self.switch.console
        bgp_config = f"""
        config router bgp
            set as 65000
            set router-id {self.router_id }
        end
        """
        config_cmds_lines(dut,bgp_config)
        for n in self.ospf_neighbors_address: 
            bgp_config = f"""
            config router bgp
                config neighbor
                edit {n}
                    set remote-as 65000
                    set update-source vlan1
                next
                end
            end
            """
            config_cmds_lines(dut,bgp_config)

    def config_ibgp_mesh_svi_v6_fabric(self):
        if self.switch.is_fortinet() == False:
            return 
        tprint(f"============== Configurating iBGP at {self.switch.name} ")
        dut=self.switch.console
        bgp_config = f"""
        config router bgp
            set as 65000
            set router-id {self.router_id }
        end
        end
        """
        config_cmds_lines(dut,bgp_config)
        for n in self.ospf_neighbors_address_vlan1_v6:
            bgp_config = f"""
            config router bgp
                config neighbor
                edit {n}
                    set remote-as 65000
                    set update-source vlan1
                next
                end
            end
            """
            config_cmds_lines(dut,bgp_config)

    def config_ibgp_mesh_svi_v6(self):
        if self.switch.is_fortinet() == False:
            return 
        tprint(f"============== Configurating iBGP at {self.switch.name} ")
        dut=self.switch.console
        bgp_config = f"""
        config router bgp
            set as 65000
            set router-id {self.router_id }
        end
        end
        """
        config_cmds_lines(dut,bgp_config)
        for n in self.ospf_neighbors_address_vlan1_v6:
            bgp_config = f"""
            config router bgp
                config neighbor
                edit {n}
                    set remote-as 65000
                    set update-source vlan1
                next
                end
            end
            """
            config_cmds_lines(dut,bgp_config)

    def update_ipv6_neighbor_cache(self):
        if self.switch.is_fortinet() == False:
            return 
        self.ipv6_neighbors = self.switch.ipv6_neighbors


    def config_ibgp_mesh_link_local(self,*args,**kwargs):
        if self.switch.is_fortinet() == False:
            return 
        tprint(f"============== Configurating iBGP via link local address at {self.switch.name} ")
        if "interface" in kwargs:
            interface = kwargs['interface']
        else:
            interface = "vlan1"
        dut=self.switch.console
        bgp_config = f"""
        config router bgp
            set as 65000
            set router-id {self.router_id }
        end
        end
        """
        config_cmds_lines(dut,bgp_config)
        for n in self.ipv6_neighbors:
            bgp_config = f"""
            config router bgp
                config neighbor
                edit {n}
                    set remote-as 65000
                    set interface {interface}
                next
                end
            end
            """
            config_cmds_lines(dut,bgp_config)

    #gradually remove this procedue
    def show_config(self):
        switch_show_cmd(self.switch.console,"show router bgp")

    #gradually use this procedure to replace show_config defined above this line
    def show_bgp_config(self):
        switch_show_cmd(self.switch.console,"show router bgp")

    def show_bgp_config_v6(self):
        switch_show_cmd(self.switch.console,"show router bgp")

    def config_ibgp_loopback_bfd(self,action):
        if self.switch.is_fortinet() == False:
            return 
        for n in self.ospf_neighbors: 
            bgp_config = f"""
            config router bgp
                config neighbor
                edit {n}
                    set bfd {action}
                next
                end
            end
            """
            config_cmds_lines(self.switch.console,bgp_config)
        switch_show_cmd(dut,"show router bgp")


    def update_bgp_config_neighbors(self):
        self.bgp_config_neighbors = find_bgp_config_neighbors(self.switch.console)


    def config_bgp_bfd_all_neighbors(self,action):
        if self.switch.is_fortinet() == False:
            return 

        self.bgp_config_neighbors = find_bgp_config_neighbors(self.switch.console)
        for n in self.bgp_config_neighbors: 
            bgp_config = f"""
            config router bgp
                config neighbor
                edit {n}
                    set bfd {action}
                next
                end
            end
            """
            config_cmds_lines(self.switch.console,bgp_config)

        switch_show_cmd(self.switch.console,"show router bgp")

    def config_ibgp_loopback_bfd_v6(self,action):
        if self.switch.is_fortinet() == False:
            return 
        for n in self.ospf_neighbors_address_loop0_v6: 
            bgp_config = f"""
            config router bgp
                config neighbor
                edit {n}
                    set bfd {action}
                next
                end
            end
            """
            config_cmds_lines(self.switch.console,bgp_config)

        switch_show_cmd(self.switch.console,"show router bgp")

    def show_bfd_neighbor(self):
        if self.switch.is_fortinet() == False:
            return 
        dut=self.switch.console
        switch_show_cmd(dut,"get router info bfd neighbor")

    def show_bfd_neighbor_v6(self):
        if self.switch.is_fortinet() == False:
            return 
        dut=self.switch.console
        switch_show_cmd(dut,"get router info6 bfd neighbor")
            

    def config_ibgp_mesh_loopback(self):
        if self.switch.is_fortinet() == False:
            return 
        tprint(f"============== Configurating iBGP at {self.switch.name} ")
        dut=self.switch.console
        bgp_config = f"""
        config router bgp
            set as 65000
            set router-id {self.router_id }
        end
        end
        """
        config_cmds_lines(dut,bgp_config)
        for n in self.ospf_neighbors: 
            bgp_config = f"""
            config router bgp
                config neighbor
                edit {n}
                    set remote-as 65000
                    set update-source loop0
                    set activate enable
                    set activate6 enable
                next
                end
            end
            """
            config_cmds_lines(dut,bgp_config)

    def config_ibgp_mesh_loopback_v6(self):
        if self.switch.is_fortinet() == False:
            return 
        tprint(f"============== Configurating iBGP at {self.switch.name} ")
        dut=self.switch.console
        bgp_config = f"""
        config router bgp
            set as 65000
            set router-id {self.router_id }
        end
        end
        """
        config_cmds_lines(dut,bgp_config)
        for n in self.ospf_neighbors_address_loop0_v6: 
            bgp_config = f"""
            config router bgp
                config neighbor
                edit {n}
                    set remote-as 65000
                    set update-source loop0
                    set activate enable
                    set activate6 enable
                next
                end
            end
            """
            config_cmds_lines(dut,bgp_config)

    def activate_ibgp_mesh_loopback_v6(self,*args,**kwargs):
        if self.switch.is_fortinet() == False:
            return 
        address_family = kwargs["address_family"]

        tprint(f"============== Activating address family for iBGPv6 neighbor at {self.switch.name} ")
        dut=self.switch.console
        if address_family == "v4":
            for n in self.ospf_neighbors_address_loop0_v6: 
                bgp_config = f"""
                config router bgp
                    config neighbor
                    edit {n}
                        set activate enable
                        set activate6 disable
                    next
                    end
                end
                """
                config_cmds_lines(dut,bgp_config)
        elif address_family == "v6":
            for n in self.ospf_neighbors_address_loop0_v6: 
                bgp_config = f"""
                config router bgp
                    config neighbor
                    edit {n}
                        set activate disable
                        set activate6 enable
                    next
                    end
                end
                """
                config_cmds_lines(dut,bgp_config)

    def activate_bgp_address_family(self,*args,**kwargs):
        address_family = kwargs["address_family"]
        interface = kwargs["interface"]
        version = kwargs["version"]

        if self.switch.is_fortinet() == False:
            return 

        tprint(f"============== Activating address family for iBGPv6 neighbor at {self.switch.name} ")
        dut=self.switch.console
        if address_family == "v4" and interface == "svi" and version == "v4" :
            for n in self.ospf_neighbors_address_vlan1_v4: 
                bgp_config = f"""
                config router bgp
                    config neighbor
                    edit {n}
                        set activate enable
                        set activate6 disable
                    next
                    end
                end
                """
                config_cmds_lines(dut,bgp_config)

        elif address_family == "v4" and interface == "svi" and version == "v6" :
            for n in self.ospf_neighbors_address_vlan1_v4: 
                bgp_config = f"""
                config router bgp
                    config neighbor
                    edit {n}
                        set activate disable
                        set activate6 enable
                    next
                    end
                end
                """
                config_cmds_lines(dut,bgp_config)

        elif address_family == "v4" and interface == "svi" and version == "both" :
            for n in self.ospf_neighbors_address_vlan1_v4: 
                bgp_config = f"""
                config router bgp
                    config neighbor
                    edit {n}
                        set activate enable
                        set activate6 enable
                    next
                    end
                end
                """
                config_cmds_lines(dut,bgp_config)

        elif address_family == "v6" and interface == "svi" and version == "v4":
            for n in self.ospf_neighbors_address_vlan1_v6: 
                bgp_config = f"""
                config router bgp
                    config neighbor
                    edit {n}
                        set activate enable
                        set activate6 disable
                    next
                    end
                end
                """
                config_cmds_lines(dut,bgp_config)

        elif address_family == "v6" and interface == "svi" and version == "v6":
            for n in self.ospf_neighbors_address_vlan1_v6: 
                bgp_config = f"""
                config router bgp
                    config neighbor
                    edit {n}
                        set activate disable
                        set activate6 enable
                    next
                    end
                end
                """
                config_cmds_lines(dut,bgp_config)

        elif address_family == "v6" and interface == "svi" and version =="both":
            for n in self.ospf_neighbors_address_vlan1_v6: 
                bgp_config = f"""
                config router bgp
                    config neighbor
                    edit {n}
                        set activate enable
                        set activate6 enable
                    next
                    end
                end
                """
                config_cmds_lines(dut,bgp_config)


        elif address_family == "v6" and interface == "loopback" and version =="v6":
            for n in self.ospf_neighbors_address_loop0_v6: 
                bgp_config = f"""
                config router bgp
                    config neighbor
                    edit {n}
                        set activate disable
                        set activate6 enable
                    next
                    end
                end
                """
                config_cmds_lines(dut,bgp_config)

        elif address_family == "v6" and interface == "loopback" and version =="v4":
            for n in self.ospf_neighbors_address_loop0_v6: 
                bgp_config = f"""
                config router bgp
                    config neighbor
                    edit {n}
                        set activate enable
                        set activate6 disable
                    next
                    end
                end
                """
                config_cmds_lines(dut,bgp_config)

        elif address_family == "v6" and interface == "loopback" and version == "both":
            for n in self.ospf_neighbors_address_loop0_v6: 
                bgp_config = f"""
                config router bgp
                    config neighbor
                    edit {n}
                        set activate enable
                        set activate6 enable
                    next
                    end
                end
                """
                config_cmds_lines(dut,bgp_config)

        elif address_family == "v4" and interface == "loopback" and version == "v4":
            for n in self.ospf_neighbors_address_loop0_v4: 
                bgp_config = f"""
                config router bgp
                    config neighbor
                    edit {n}
                        set activate enable
                        set activate6 disable
                    next
                    end
                end
                """
                config_cmds_lines(dut,bgp_config)

        elif address_family == "v4" and interface == "loopback" and version == "v6":
            for n in self.ospf_neighbors_address_loop0_v4: 
                bgp_config = f"""
                config router bgp
                    config neighbor
                    edit {n}
                        set activate disable
                        set activate6 enable
                    next
                    end
                end
                """
                config_cmds_lines(dut,bgp_config)

        elif address_family == "v4" and interface == "loopback" and version == "both":
            for n in self.ospf_neighbors_address_loop0_v4: 
                bgp_config = f"""
                config router bgp
                    config neighbor
                    edit {n}
                        set activate enable
                        set activate6 enable
                    next
                    end
                end
                """
                config_cmds_lines(dut,bgp_config)
        else:
            Info("Error: Did provide correct parameters for BGP address family activation")
            Info("Parameters: address_family = 'v4/v6', interface = 'svi/loopback', version = 'v4/v6/both")
            Info("Please try again")


    def activate_ibgp_mesh_svi_v6(self,*args,**kwargs):
        address_family = kwargs["address_family"]

        tprint(f"============== Activating address family for iBGPv6 neighbor at {self.switch.name} ")
        dut=self.switch.console
        if address_family == "v4":
            for n in self.ospf_neighbors_address_vlan1_v6: 
                bgp_config = f"""
                config router bgp
                    config neighbor
                    edit {n}
                        set activate enable
                        set activate6 disable
                    next
                    end
                end
                """
                config_cmds_lines(dut,bgp_config)
        elif address_family == "v6":
            for n in self.ospf_neighbors_address_vlan1_v6: 
                bgp_config = f"""
                config router bgp
                    config neighbor
                    edit {n}
                        set activate disable
                        set activate6 enable
                    next
                    end
                end
                """
                config_cmds_lines(dut,bgp_config)

     

    def config_ibgp_mesh_loopback_v4(self):
        if self.switch.is_fortinet() == False:
            return
        tprint(f"============== Configurating iBGP at {self.switch.name} ")
        dut=self.switch.console
        bgp_config = f"""
        config router bgp
            set as 65000
            set router-id {self.router_id }
        end
        end
        """
        config_cmds_lines(dut,bgp_config)
        for n in self.ospf_neighbors_address_loop0_v4: 
            bgp_config = f"""
            config router bgp
                config neighbor
                edit {n}
                    set remote-as 65000
                    set update-source loop0
                    set activate enable
                    set activate6 enable
                next
                end
            end
            """
            config_cmds_lines(dut,bgp_config)

    def config_ebgp_mesh_direct(self):
        if not switch.router_bgp.check_bgp_neighbor_status_v6():
            result = False
        tprint(f"============== Configurating eBGP mesh at {self.switch.name} ")
        dut=self.switch.console
        bgp_config = f"""
        config router bgp
            set as {self.switch.ebgp_as}
            set router-id {self.router_id }
        end
        """
        config_cmds_lines(dut,bgp_config)
        for switch in self.switch.neighbor_switch_list:
            bgp_config = f"""
            config router bgp
                config neighbor
                edit {switch.vlan1_ip}
                    set remote-as {switch.ebgp_as}
                    set activate enable
                    set activate6 enable
                next
                end
            end
            """
            config_cmds_lines(dut,bgp_config)

    def config_ebgp_mesh_svi_v6(self):
        if self.switch.is_fortinet() == False:
            return 
        tprint(f"============== Configurating eBGP v6 mesh over SVI at {self.switch.name} ")
        dut=self.switch.console
        bgp_config = f"""
        config router bgp
            set as {self.switch.ebgp_as}
            set router-id {self.router_id }
        end
        """
        config_cmds_lines(dut,bgp_config)
        for sw in self.ospf_neighbors_swlist_v6:
            bgp_config = f"""
            config router bgp
                config neighbor
                edit {sw.vlan1_ipv6.split('/')[0]}
                    set remote-as {sw.ebgp_as}
                    set activate enable
                    set activate6 enable
                next
                end
            end
            """
            config_cmds_lines(dut,bgp_config)



    def config_ebgp_mesh_svi_v4(self):
        tprint(f"============== Configurating eBGP v4 mesh over SVI at {self.switch.name} ")
        dut=self.switch.console
        bgp_config = f"""
        config router bgp
            set as {self.switch.ebgp_as}
            set router-id {self.router_id }
        end
        """
        config_cmds_lines(dut,bgp_config)
        for sw in self.ospf_neighbors_swlist_v4:
            bgp_config = f"""
            config router bgp
                config neighbor
                edit {sw.vlan1_ip}
                    set remote-as {sw.ebgp_as}
                    set activate enable
                    set activate6 enable
                next
                end
            end
            """
            config_cmds_lines(dut,bgp_config)

    def config_ebgp_mesh_multihop(self):
        if self.switch.is_fortinet() == False:
            return 
        tprint(f"================ Configurating eBGP multihop at {self.switch.name} =================")
        dut=self.switch.console
        bgp_config = f"""
        config router bgp
            set as {self.switch.ebgp_as}
            set router-id {self.router_id }
        end
        """
        config_cmds_lines(dut,bgp_config)
        for switch in self.switch.neighbor_switch_list:
            bgp_config = f"""
            config router bgp
                config neighbor
                edit {switch.loop0_ip}
                    set remote-as {switch.ebgp_as}
                    set ebgp-enforce-multihop enable
                    set ebgp-multihop-ttl 3
                    set update-source loop0
                    set activate enable
                    set activate6 enable
                next
                end
            end
            """
            config_cmds_lines(dut,bgp_config)

    def config_ebgp_mesh_multihop_v6(self):
        if self.switch.is_fortinet() == False:
            return 
        tprint(f"============== Configurating eBGP multihop v6 mesh over loopback at {self.switch.name} ")
        dut=self.switch.console
        bgp_config = f"""
        config router bgp
            set as {self.switch.ebgp_as}
            set router-id {self.router_id }
        end
        """
        config_cmds_lines(dut,bgp_config)
        for sw in self.ospf_neighbors_swlist_v6:
            bgp_config = f"""
            config router bgp
                config neighbor
                edit {sw.loop0_ipv6.split('/')[0]}
                    set remote-as {sw.ebgp_as}
                    set ebgp-enforce-multihop enable
                    set ebgp-multihop-ttl 3
                    set update-source loop0
                    set activate enable
                    set activate6 enable
                next
                end
            end
            """
            config_cmds_lines(dut,bgp_config)

    def config_ebgp_mesh_multihop_v4(self):
        tprint(f"============== Configurating eBGP multihop v6 mesh over loopback at {self.switch.name} ")
        dut=self.switch.console
        bgp_config = f"""
        config router bgp
            set as {self.switch.ebgp_as}
            set router-id {self.router_id }
        end
        """
        config_cmds_lines(dut,bgp_config)
        for sw in self.ospf_neighbors_swlist_v6:
            bgp_config = f"""
            config router bgp
                config neighbor
                edit {sw.loop0_ipv4}
                    set remote-as {sw.ebgp_as}
                    set ebgp-enforce-multihop enable
                    set ebgp-multihop-ttl 3
                    set update-source loop0
                    set activate enable
                    set activate6 enable
                    set 
                next
                end
            end
            """
            config_cmds_lines(dut,bgp_config)

    def config_ebgp_ixia(self,ixia_port):
        if self.switch.is_fortinet() == False:
            return 
        tprint(f"=============={self.switch.name}: Configurating eBGP peer relationship to IXIA Peer")
        ixia_ip,ixia_mask = seperate_ip_mask(ixia_port[6])
        ixia_as = ixia_port[5]
        if ixia_ip == None:
            return False

        bgp_config = f"""
        config router bgp
            set as 65000
            set router-id {self.router_id }
        end
        """
        config_cmds_lines(self.switch.console,bgp_config)

        bgp_config = f"""
        config router bgp
            config neighbor
            edit {ixia_ip}
                set remote-as {ixia_as}
            next
            end
        end
        """
        config_cmds_lines(self.switch.console,bgp_config)
        return True
  

    def config_ebgp_ixia_v4(self,*args,**kwargs):
        tprint(f"============== Configurating eBGP peer relationship to ixia {self.switch.name} ")
        ixia_port = kwargs["ixia_port"]
        ixia_as = kwargs["ixia_as"]
        ixia_ip,ixia_mask = seperate_ip_mask(ixia_port[4])
        if ixia_ip == None:
            return False

        if "sw_as" in kwargs:
            sw_as = kwargs["sw_as"]
            if sw_as != None:
                sw_as = int(sw_as)
        else:
            sw_as = 65000
        if sw_as != None:
            bgp_config = f"""
            config router bgp
                set as {sw_as}
                set router-id {self.router_id }
            end
            """
            config_cmds_lines(self.switch.console,bgp_config)
        bgp_config = f"""
        config router bgp
            config neighbor
            edit {ixia_ip}
                set remote-as {ixia_as}
            next
            end
        end
        """
        config_cmds_lines(self.switch.console,bgp_config)
        return True

    def cisco_bgp_ixia_v6(self,*args,**kwargs):
        tprint(f"============== Configurating BGP peer relationship to ixia {self.switch.name} ")
        ixia_port = kwargs["ixia_port"]
        ixia_as = kwargs["ixia_as"]
        ixia_ip,ixia_mask = seperate_ip_mask(ixia_port[6])
        if ixia_ip == None:
            return False

        if "sw_as" in kwargs:
            sw_as = int(kwargs["sw_as"])
        else:
            sw_as = 65000

        # if sw_as != None:
        #     bgp_config = f"""
        #     config router bgp
        #         set as {sw_as}
        #         set router-id {self.router_id }
        #     end
        #     """
        #     config_cmds_lines(self.switch.console,bgp_config)
        bgp_config = f"""
        config t
            router bgp 65000
            neighbor {ixia_ip}
                remote-as {ixia_as}
                address-family ipv6 unicast
        end
        """
        config_cmds_lines(self.switch.console,bgp_config)
        return True

    def cisco_bgp_ixia_v4(self,*args,**kwargs):
        tprint(f"============== Configurating BGP peer relationship to ixia {self.switch.name} ")
        ixia_port = kwargs["ixia_port"]
        ixia_as = kwargs["ixia_as"]
        ixia_ip,ixia_mask = seperate_ip_mask(ixia_port[6])
        if ixia_ip == None:
            return False

        if "sw_as" in kwargs:
            sw_as = int(kwargs["sw_as"])
        else:
            sw_as = 65000

        if self.switch.is_fortinet():
            if sw_as != None:
                bgp_config = f"""
                config router bgp
                    set as {sw_as}
                    set router-id {self.router_id }
                end
                """
                config_cmds_lines(self.switch.console,bgp_config)
            bgp_config = f"""
             config router bgp
                config neighbor
                edit {ixia_ip}
                    set remote-as {ixia_as}
                next
                end
            end
            """
            config_cmds_lines(self.switch.console,bgp_config)

        elif self.switch.platform == "n9k":
            bgp_config = f"""
            config t
            router bgp 65000
            neighbor {ixia_ip}
                remote-as {ixia_as}
                address-family ipv4 unicast
            """
            config_cmds_lines(self.switch.console,bgp_config)
        return True

    def config_ebgp_ixia_v6(self,*args,**kwargs):
        # if self.switch.is_fortinet() == False:
        #     return 
        tprint(f"============== Configurating eBGP peer relationship to ixia {self.switch.name} ")
        ixia_port = kwargs["ixia_port"]
        ixia_as = kwargs["ixia_as"]
        ixia_ip,ixia_mask = seperate_ip_mask(ixia_port[6])
        if ixia_ip == None:
            return False

        if "sw_as" in kwargs:
            sw_as = kwargs["sw_as"]
            if sw_as != None:
                sw_as = int(sw_as)
        else:
            sw_as = 65000

        if self.switch.is_fortinet():
            if sw_as != None:
                bgp_config = f"""
                config router bgp
                    set as {sw_as}
                    set router-id {self.router_id }
                end
                """
                config_cmds_lines(self.switch.console,bgp_config)

            bgp_config = f"""
            config router bgp
                config neighbor
                edit {ixia_ip}
                    set remote-as {ixia_as}
                next
                end
            end
            """
            config_cmds_lines(self.switch.console,bgp_config)

        elif self.switch.platform == "n9k":
            bgp_config = f"""
                config t
                router bgp 65000
                neighbor {ixia_ip}
                    remote-as {ixia_as}
                    address-family ipv6 unicast
                """
            config_cmds_lines(self.switch.console,bgp_config)
        return True

    def config_ibgp_ixia_v6(self,*args,**kwargs):
        tprint(f"============== Configurating eBGP peer relationship to ixia {self.switch.name} ")
        ixia_port = kwargs["ixia_port"]
        ixia_as = kwargs["ixia_as"] # ignore this one
        ixia_ip,ixia_mask = seperate_ip_mask(ixia_port[6])
        if ixia_ip == None:
            return False

        bgp_config = f"""
        config router bgp
            set as 65000
            set router-id {self.router_id }
        end
        """
        config_cmds_lines(self.switch.console,bgp_config)
        bgp_config = f"""
        config router bgp
            config neighbor
            edit {ixia_ip}
                set remote-as 65000
            next
            end
        end
        """
        config_cmds_lines(self.switch.console,bgp_config)
        return True


    def config_ibgp_ixia_v4(self,*args,**kwargs):
        tprint(f"============== Configurating eBGP peer relationship to ixia {self.switch.name} ")
        ixia_port = kwargs["ixia_port"]
        ixia_as = kwargs["ixia_as"] #ignore as number as it is iBGP
        ixia_ip,ixia_mask = seperate_ip_mask(ixia_port[4])
        if ixia_ip == None:
            return False
        bgp_config = f"""
        config router bgp
            set as 65000
            set router-id {self.router_id }
        end
        """
        config_cmds_lines(self.switch.console,bgp_config)
        bgp_config = f"""
        config router bgp
            config neighbor
            edit {ixia_ip}
                set remote-as 65000
            next
            end
        end
        """
        config_cmds_lines(self.switch.console,bgp_config)
        return True

    def config_redistribute_connected(self):
        tprint(f"============== Redistrubte connected to BGP at {self.switch.name} ")
        switch = self.switch
        dut = switch.console
        #switch.config_sys_interface(10)
    
        sleep(10)
        bgp_config = f"""
        config router bgp
            config redistribute connected 
            set status enable
            end
        end
        """
        config_cmds_lines(dut,bgp_config)
        switch_show_cmd(dut,"show router bgp")

    def config_redistribute_connected_v6(self):
        if self.switch.is_fortinet() == False:
            return 
        tprint(f"============== Redistrubte connected to BGP at {self.switch.name} ")
        switch = self.switch
        dut = switch.console
        #switch.config_sys_interface(10)
    
        sleep(10)
        bgp_config = f"""
        config router bgp
            config redistribute6 connected 
            set status enable
            end
        end
        """
        config_cmds_lines(dut,bgp_config)
        switch_show_cmd(dut,"show router bgp")


    def config_redistribute_static(self):
        tprint(f"============== Redistrubte static routes to BGP at {self.switch.name} ")
        switch = self.switch
        dut = switch.console
        #switch.config_sys_interface(10)
    
        sleep(10)
        bgp_config = f"""
        config router bgp
            config redistribute static
            set status enable
            end
        end
        """
        config_cmds_lines(dut,bgp_config)

 
    def clear_bgp_all(self):
        switch_exec_cmd(self.switch.console,"execute router clear bgp all")

    def config_redistribute_ospf(self,action):
        tprint(f"============== Redistrubte ospf routes to BGP at {self.switch.name} ")
        switch = self.switch
        dut = switch.console
        #switch.config_sys_interface(10)
    
        sleep(10)
        bgp_config = f"""
        config router bgp
            config redistribute ospf
            set status {action}
            end
        end
        """
        config_cmds_lines(dut,bgp_config)

    def config_redistribute_isis(self):
        tprint(f"============== Redistrubte ospf routes to BGP at {self.switch.name} ")
        switch = self.switch
        dut = switch.console
        #switch.config_sys_interface(10)
    
        sleep(10)
        bgp_config = f"""
        config router bgp
            config redistribute isis
            set status enable
            end
        end
        """
        config_cmds_lines(dut,bgp_config)


    def show_bgp_summary(self):
        if self.switch.is_fortinet() == False:
            return 
        dut=self.switch.console
        switch_show_cmd(dut,"get router info bgp summary")

    def show_bgp_summary_v6(self):
        if self.switch.is_fortinet() == False:
            return 
        dut=self.switch.console
        switch_show_cmd(dut,"get router info6 bgp summary")

    def show_bgp_routes_v6(self):
        dut=self.switch.console
        switch_show_cmd(dut,"get router info6 routing-table bgp")

    def show_bgp_routes(self):
        dut=self.switch.console
        switch_show_cmd(dut,"get router info routing-table bgp")

    def bgp_network_cmd(self,*args,**kwargs):
        network = kwargs["network"]
        cmd = kwargs["cmd"]
        index = kwargs["index"]
        config = f"""
            config router bgp
                config network
                    edit {index}
                    set prefix {network}/32
                    {cmd}
                end
            next
            end
            """
        config_cmds_lines(self.switch.console,config)


    def bgp_network6_cmd(self,*args,**kwargs):
        network = kwargs["network"]
        cmd = kwargs["cmd"]
        index = kwargs["index"]
        config = f"""
            config router bgp
                config network6
                    edit {index}
                    set prefix {network}
                    {cmd}
                end
            next
            end
            """
        config_cmds_lines(self.switch.console,config)


    def clear_config(self):
        if self.switch.is_fortinet() == False:
            return
        neighbor_list = get_switch_show_bgp(self.switch.console)
        print(neighbor_list)
        network_list = get_bgp_network_config(self.switch.console)
        agg_list = get_bgp_aggregate_address_config(self.switch.console)
        for n in neighbor_list:
            config = f"""
            config router bgp
                config neighbor
                delete {n}
                end
                end
            """
            config_cmds_lines(self.switch.console,config)

        for n in network_list:
            config = f"""
            config router bgp
                config network
                delete {n}
                end
                end
            """
            config_cmds_lines(self.switch.console,config)

        for n in agg_list:
            config = f"""
            config router bgp
                config aggregate-address
                delete {n}
                end
                end
            """
            config_cmds_lines(self.switch.console,config)

        bgp_config = f"""
        config router bgp
            unset as 
            unset keepalive-timer
            unset holdtime-timer
            unset always-compare-med
            unset bestpath-as-path-ignore 
            unset bestpath-cmp-confed-aspath
            unset bestpath-cmp-routerid
            unset bestpath-med-confed
            unset bestpath-med-missing-as-worst
            unset client-to-client-reflection
            unset dampening
            unset deterministic-med
            unset enforce-first-as
            unset fast-external-failover
            unset log-neighbor-changes
            unset cluster-id
            unset confederation-identifier
            unset default-local-preference
            unset scan-time
            unset maximum-paths-ebgp
            unset bestpath-aspath-multipath-relax
            unset maximum-paths-ibgp
            unset distance-external
            unset distance-internal
            unset distance-local
            unset graceful-stalepath-time 
            end
        """
        config_cmds_lines(self.switch.console,bgp_config)

    def clear_config_all(self):
        self.clear_config_v6()

    def delete_all_neighbors_v6(self):
        if self.switch.is_fortinet() == False:
            return 
        neighbor_list = get_switch_show_bgp_v6(self.switch.console)
        print(neighbor_list)
        for n in neighbor_list:
            config = f"""
            config router bgp
                config neighbor
                delete {n}
                end
                end
            """
            config_cmds_lines(self.switch.console,config)


    def clear_config_v6(self):
        if self.switch.is_fortinet() == False:
            return 
        neighbor_list = get_switch_show_bgp_v6(self.switch.console)
        print(neighbor_list)
        network_list = get_bgp_network_config_v6(self.switch.console)
        agg_list = get_bgp_aggregate_address_config_v6(self.switch.console)
        for n in neighbor_list:
            config = f"""
            config router bgp
                config neighbor
                delete {n}
                end
                end
            """
            config_cmds_lines(self.switch.console,config)

        for n in network_list:
            config = f"""
            config router bgp
                config network
                delete {n}
                end
                end
            """
            config_cmds_lines(self.switch.console,config)

        for n in agg_list:
            config = f"""
            config router bgp
                config aggregate-address
                delete {n}
                end
                end
            """
            config_cmds_lines(self.switch.console,config)

        bgp_config = f"""
        config router bgp
            unset as 
            unset keepalive-timer
            unset holdtime-timer
            unset always-compare-med
            unset bestpath-as-path-ignore 
            unset bestpath-cmp-confed-aspath
            unset bestpath-cmp-routerid
            unset bestpath-med-confed
            unset bestpath-med-missing-as-worst
            unset client-to-client-reflection
            unset dampening
            unset deterministic-med
            unset enforce-first-as
            unset fast-external-failover
            unset log-neighbor-changes
            unset cluster-id
            unset confederation-identifier
            unset default-local-preference
            unset scan-time
            unset maximum-paths-ebgp
            unset bestpath-aspath-multipath-relax
            unset maximum-paths-ibgp
            unset distance-external
            unset distance-internal
            unset distance-local
            unset graceful-stalepath-time 
            end
        """
        config_cmds_lines(self.switch.console,bgp_config)



class acl_counter_entry():
    def __init__(self):
        self.type = None
        self.id = None
        self.group = None
        self.all_pkts = None
        self.red_pkts = None 
        self.yellow_pkts = None 
        self.green_pkts = None 
        self.all_bytes = None
        self.red_bytes = None 
        self.yellow_bytes = None 
        self.green_bytes = None 
        self.description = None 

class acl_counter_class():
    def __init__(self,cmd_output):
        self.cmd_output = cmd_output
        self.acl_counter_list = []
        self.parse_cmd_output()

    def parse_cmd_output(self):
        example = """
        ingress: 

         ID     Group    Color     Packets                Bytes           description
        _____________________________________________________________________________

        1         1          all   212656               212656000                                                                             
        1         1        green   769                  769000                                                                                
        1         1       yellow   68                   68000                                                                                 
        1         1          red   211819               211819000                                                                             
         ID     Group    Color     Packets                Bytes           description
        _____________________________________________________________________________

        2         1          all   0                    0                                                                                     
        2         1        green   0                    0                                                                                     
        2         1       yellow   0                    0                                                                                     
        2         1          red   0                    0                                                                                     

        egress: 

         ID     Group    Color     Packets                Bytes           description
        _____________________________________________________________________________

        1         1        green   0                    0                                                                                     
        1         1       yellow   0                    0                                                                                     
         ID     Group    Color     Packets                Bytes           description
        _____________________________________________________________________________

        2         1        green   0                    0                                                                                     
        2         1       yellow   0                    0    
        """
        ingress_found = False
        egress_found = False
        acl_counter = None

        for line in self.cmd_output:
            if "ingress:" in line:
                ingress_found = True
                egress_found = False
                continue
            if "egress:" in line:
                egress_found = True
                ingress_found = False
                continue
            if "ID     Group    Color     Packets" in line:
                if acl_counter != None:
                    self.acl_counter_list.append(acl_counter)
                acl_counter = acl_counter_entry()
                acl_counter.type = "ingress" if ingress_found else "egress"
                continue
            # if "ID     Group    Color     Packets" in line:
            #     acl_counter = acl_counter_entry()
            #     self.acl_counter_list.append(acl_counter)
            #     acl_counter.type = "egress" if egress_found else "ingress"
            #     continue
            if "get switch acl counters all" in line:
                continue
            if "all" in line:
                line_list = line.split()
                #print(f"All: {line_list}")
                acl_counter.id = int(line_list[0])
                acl_counter.group = int(line_list[1])
                acl_counter.all_pkts = int(line_list[3])
                acl_counter.all_bytes = int(line_list[4])
                continue
            if "green" in line:
                line_list = line.split()
                #print(f"green: {line_list}")
                acl_counter.id = int(line_list[0])
                acl_counter.group = int(line_list[1])
                acl_counter.green_pkts = int(line_list[3])
                acl_counter.green_bytes = int(line_list[4])
                continue
            if "yellow" in line:
                line_list = line.split()
                #print(f"yellow: {line_list}")
                acl_counter.id = int(line_list[0])
                acl_counter.group = int(line_list[1])
                acl_counter.yellow_pkts = int(line_list[3])
                acl_counter.yellow_bytes = int(line_list[4])
            if "red" in line:
                line_list = line.split()
                #print(f"yellow: {line_list}")
                acl_counter.id = int(line_list[0])
                acl_counter.group = int(line_list[1])
                acl_counter.red_pkts = int(line_list[3])
                acl_counter.red_bytes = int(line_list[4])
        self.acl_counter_list.append(acl_counter)
         

    def print_acl_counters(self):
        for acl in self.acl_counter_list:
            print(f"ID:{acl.id} | Type:{acl.type} | All:{acl.all_pkts} | Green:{acl.green_pkts} | Yellow:{acl.yellow_pkts} | Red:{acl.red_pkts}")



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
        self.remote_system = None
        self.remote_system_role = None
        self.remote_system_console = None
        self.remote_image = None
        self.role = None

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
        print(f"---------------------------- LLDP Neihgbor Info --------------------")
        print("type = {}".format(self.type))
        print("local_port = {}".format(self.local_port))
        print("med_type = {}".format(self.med_type))
        print("capability = {}".format(self.capability))
        print("remote_port = {}".format(self.remote_port))
        print("status = {}".format(self.status))
        print("remote_system = {}".format(self.remote_system))
        print("remote_system_role = {}".format(self.remote_system_role))
        print("remote image = {}".format(self.remote_image))

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

class switch_trunk_class():
    def __init__(self,*args,**kwargs):
        self.sample = """
        edit "8EF3X17000533-0"
        set mode lacp-active
        set auto-isl 1
        set mclag-icl enable
        set static-isl enable
            set members "port15" "port16"
        next
        """
        self.switch = args[0]
        self.name = None
        self.mode = None
        self.auto_isl = 1
        self.mclag_icl = "disable"
        self.static_isl = "disable"
        self.static_isl_auto_vlan = "enable"
        self.type = "dynamic"
        self.create = "system"
        self.members = []


class interface:
    def __init__(self,*args, **kwargs):
        
        self.switch = args[0]
        self.vid = None
        self.second = None
        self.second_ip = None
        self.port_list = None
        self.ip = kwargs['ip']
        self.type = "vlan"

        if "vid" in kwargs['vid']:
            self.vid = kwargs['vid']
       
        if "second" in kwargs:
            self.second = kwargs['second']
        if "second_ip" in kwargs:
            self.second_ip = kwargs['second_ip']
        if "ports" in kwargs:
            self.port_list = kwargs["ports"]
        if "type" in kwargs:
            self.type = kwargs['type']


class System_interface:
    def __init__(self,*args,**kwargs):
        self.switch = None
        self.name = None
        self.ipv4 = None
        self.ipv4_mask = None
        self.allowaccess = None
        self.type = None
        self.vlan = None
        self.isvlan = False 
        self.vlan_id = None
        self.ipv6 = None
        self.ipv6_mask = None
        self.ipv6_2nd = None


    def derive_ipv6_extra(self,*args,**kwargs):
        if self.ipv6 != None and self.name != "mgmt":
            ipv6 = self.ipv6
            ipv6_list = ipv6.split(":")
            ipv6_list[2] = str(int(ipv6_list[2])+1)
            ipv6_list = [s for s in ipv6_list if s]
            ipv6_2nd = f"{ipv6_list[0]}:{ipv6_list[1]}:{ipv6_list[2]}:{ipv6_list[3]}::{ipv6_list[4]}"
            self.ipv6_2nd = ipv6_2nd


class FortiSwitch:
    def __init__(self, *args,**kwargs):
        dut_dir = args[0]
        self.dut_dir = dut_dir
        self.comm = dut_dir['comm']  
        self.comm_port = dut_dir['comm_port']  
        self.name = dut_dir['name'] 
        self.show_basic_info()
        self.label = dut_dir['label'] 
        self.location = dut_dir['location'] 
        self.console = dut_dir['telnet'] 
        self.dut = dut_dir['telnet']  
        self.cfg_file = dut_dir['cfg'] 
        self.mgmt_ip = dut_dir['mgmt_ip'] 
        self.mgmt_mask = dut_dir['mgmt_mask']  
        self.loop0_ip = dut_dir['loop0_ip'] 
        self.loop0_ipv4 = dut_dir['loop0_ip']  #have a duplicate member just for convenience
        self.loop0_ipv6 = dut_dir['loop0_ipv6']
        self.rid = self.loop0_ip
        self.vlan1_ip = dut_dir['vlan1_ip']
        self.vlan1000_ip = dut_dir['vlan1000_ip'] 
        self.vlan1_ipv6= dut_dir['vlan1_ipv6']
        self.vlan1000_ipv6= dut_dir['vlan1000_ipv6']
        self.vlan1_2nd = dut_dir['vlan1_2nd']
        self.vlan1000_2nd = dut_dir['vlan1000_2nd']
        self.internal = dut_dir['internal']
        self.internal_v6 = dut_dir['internal_v6']
        self.vlan1_subnet = dut_dir['vlan1_subnet']
        self.vlan1000_subnet = dut_dir['vlan1000_subnet']  
        self.vlan1_mask = dut_dir['vlan1_mask'] 
        self.vlan1000_mask = dut_dir['vlan1000_mask'] 
        self.split_ports = dut_dir['split_ports'] 
        self.ports_40g = dut_dir['40g_ports']
        self.static_route = dut_dir['static_route']
        self.static_route_mask = dut_dir['static_route_mask']
        self.ebgp_as = dut_dir['ebgp_as']
        self.vendor = dut_dir['vendor']
        self.platform = dut_dir['platform']
        self.software_version = find_dut_build(self.console,platform=self.platform)[0]
        self.software_build = find_dut_build(self.console,platform=self.platform)[1]
        self.model = find_dut_model(self.console)
        self.router_ospf = Router_OSPF(self)
        self.router_bgp = Router_BGP(self)
        self.router_isis = Router_ISIS(self)
        self.access_list= Router_access_list(self)
        self.route_map = Router_route_map(self)
        self.aspath_list = Router_aspath_list(self)
        self.prefix_list = Router_prefix_list(self)
        self.community_list = Router_community_list(self)
        self.lldp_neighbor_list = get_switch_lldp_summary(self.console)
        self.neighbor_ip_list = []
        self.neighbor_switch_list = []
        self.ipv6_neighbors = []  # this is IPv6 neighbor list for vlan1.  Must have in this setup
        self.ipv4_neighbors = []  # this is IPv4 neighbor list for vlan1.  
        self.mac_neighbors = [] # this is neighbor's MAC address for vlan1. 
        self.lldp_obj_list = None
        self.discover_lldp_neighbors()
        self.config_lldp_neighbor_ports()
        self.vlan_interfaces = []
        self.cisco_config_full_2()
        self.sys_interfaces = self.find_sys_interfaces()
        self.disable_diag_debugs()
        self.trunk_list = []
        #self.add_extra_ipv6()


    def config_sw_after_factory(self):
        

        config_mgmt_mode = f"""
        config system interface
            edit mgmt
            set mode static
            end
        config system interface
            edit "mgmt"
            set mode static
            end
        """
        config_cmds_lines(self.console,config_mgmt_mode)
        config = f"""
        conf system interface 
            edit mgmt
            set ip {self.mgmt_ip} {self.mgmt_netmask}
            set allowaccess ping https ssh snmp http telnet fgfm
            set type physical
            set role lan
            next
        end
        """
        config_cmds_lines(self.console,config)
        sleep(10)

        config = f"""
        config router static
            edit 1
                set gateway {self.mgmt_gateway}
                set device "mgmt"
            next
        end
        """
        config_cmds_lines(self.console,config)
        sleep(10)

    def discover_switch_trunk(self,*args,**kwargs):
        self.sample = """
        config switch trunk
            edit "8EF3X17000533-0"
                set mode lacp-active
                set auto-isl 1
                set mclag-icl enable
                set static-isl enable
                    set members "port15" "port16"
            next
            edit "core1"
                set mode lacp-active
                set auto-isl 1
                set mclag enable
                    set members "port3" "port4"
            next
            edit "core2"
                set mode lacp-active
                set auto-isl 1
                set mclag enable
                    set members "port5" "port6"
            next
            edit "GT3KD3Z15800103"
                set auto-isl 1
                set fortilink 1
                set mclag enable
                set static-isl enable
                set mclag-icl enable
                set static-isl-auto-vlan disable
                    set members "port49"
            next
            end
        """
        if self.is_fortinet() == False:
            return 
        Info(f"Discovering switch trunk and updating switch trunk database at {self.name}......")
        switch_trunk_obj_list = []
        switch_trunk_dict_list = []

        output = collect_show_cmd(self.console,"show switch trunk")
        print(output)
        trunk_block_list = []
        if output == None:
            ErrorNotify(f"show switch trunk has returned NoneType at switch {self.name}")
            exit(-1)
        for line in output:
            if "edit" in line:
                trunk_block = []
                trunk_block.append(line)
                continue
            elif "edit" in line:
                trunk_block.append(line)
            elif "next" in line:
                trunk_block_list.append(trunk_block)
        if len(trunk_block_list) == 0:
            return
        for trunk_block in trunk_block_list:
            trunk_obj = switch_trunk_class(self.console)
            for line in trunk_block:
                if "edit" in line:
                    trunk_obj.name = line.split()[1].replace('"',"")
                elif "set" in line and "auto-isl" in line:
                    trunk_obj.auto_isl = int(line.split()[2])
                elif "set" in line and "fortilink" in line:
                    trunk_obj.fortilink = int(line.split()[2])
                elif "set" in line and "mclag" in line:
                    trunk_obj.mclag = line.split()[2]
                elif "set" in line and "static-isl" in line and "static-isl-auto-vlan" not in line:
                    trunk_obj.static_isl = line.split()[2]
                elif "set" in line and "static-isl-auto-vlan" in line:
                    trunk_obj.static_isl_auto_vlan = line.split()[2]
                elif "set" in line and "members" in line:
                    trunk_obj.members = line.split()[2:]
                elif "set" in line and "mclag-icl" in line:
                    trunk_obj.mclag_icl = line.split()[2]
            if len(trunk_obj.name) > 10:
                trunk_obj.create = "system"
            else:
                trunk_obj.create = "manual"
            if trunk_obj.static_isl == "enable":
                trunk_obj.type = "static"
            else:
                trunk_obj.type = "dynamic"
            self.trunk_list.append(trunk_obj)

        print(self.trunk_list)
        return self.trunk_list
 


    def config_switch_interface_cmd(self,*args,**kwargs):
        cmd = kwargs["cmd"]
        port = kwargs["port"]
        config = f"""
            config switch interface
                edit {port}
                    {cmd}
                next
            end
            """
        config_cmds_lines(self.console,config)




    def fsw_upgrade(self,*args,**kwargs):
        if "build" in kwargs:
            build = int(kwargs['build'])
            build = f"{build:04}"
        else:
            ErrorNotify("Software build number is missing. Exmaple: build=xxx.  Exiting program")
            exit(-1)
        if "version" in kwargs:
            version = kwargs['version']
        else:
            version = "v6"
        dut = self.console
        dut_name = self.name
        
        tprint(f"=================== Upgrading FSW {dut_name} to build # {build} =================")
        model = find_dut_model(dut)
        model = model.strip()
        if model == "FSW_448D_FPOE":
            image_name = f"FSW_448D_FPOE-{version}-build{build}-FORTINET.out"
        elif model == "FSW_448D_POE":
            image_name =  f"FSW_448D_POE-{version}-build{build}-FORTINET.out" 
        elif model == "FSW_448D-v6":
            image_name = f"FSW_448D-{version}-build{build}-FORTINET.out"
        elif model == "FortiSwitch-3032E":
            if build == -1:
                image_name = "fs3e32.deb"
            else:
                image_name = f"FSW_3032E-{version}-build{build}-FORTINET.out"
        elif model == "FortiSwitch-3032D":
            if build == -1:
                image_name = "fs3d32.deb"
            else:
                image_name = f"FSW_3032D-{version}-build{build}-FORTINET.out"
        elif model == "FortiSwitch-1048E":
            if build == -1:
                image_name = "fs1e48.deb"
            else:
                image_name = f"FSW_1048E-{version}-build{build}-FORTINET.out"
        elif model == "FortiSwitch-1048D":
            if build == -1:
                image_name = "fs1d48.deb"
            else:
                image_name = f"FSW_1048D-{version}-build{build}-FORTINET.out"
        elif model == "FortiSwitch-1024D":
            if build == -1:
                image_name = "fs1d24.deb"
            else:
                image_name = f"FSW_1024D-{version}-build{build}-FORTINET.out"
        elif model == "FortiSwitch-548D-FPOE":
                image_name = f"FSW_548D_FPOE-{version}-build{build}-FORTINET.out"
        elif model == "FortiSwitch-548D":
                image_name = f"FSW_548D-{version}-build{build}-FORTINET.out"
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


    def collect_linux_cmd(self,*args,**kwargs):
        if "cmd" in kwargs:
            linux_cmd = kwargs['cmd']
        else:
            linux_cmd = None
        if "sw_name" in kwargs:
            sw_name = kwargs['sw_name']
        else:
            sw_name = "dut"
        Info(f"============================ {sw_name}: {linux_cmd} ========================")
        cmd = f"""
            fnsysctl sh 
        """
        self.show_command(cmd)

        cmd = f"""
            {linux_cmd}
            
        """
        self.show_command(cmd)

        cmd = f"""
            exit 
        """
        self.show_command(cmd)
    
    def collect_linux_cmd_batch(self,*args,**kwargs):
        if "cmd" in kwargs:
            linux_cmds = kwargs['cmd']
        else:
            linux_cmds = None
        if "sw_name" in kwargs:
            sw_name = kwargs['sw_name']
        else:
            sw_name = "dut"
        cmd = f"""
            fnsysctl sh 
        """
        self.show_command_linux(cmd)

        for linux_cmd in linux_cmds:
            cmd = f"""
                {linux_cmd}
                
            """
            self.show_command_linux(cmd)

        cmd = f"""
            exit 
        """
        self.show_command_linux(cmd)

    def get_crash_debug(self):
        # commands = [
        # "fnsysctl cat /proc/slabinfo","fnsysctl cat /proc/zoneinfo","fnsysctl cat /proc/meminfo", 
        # "fnsysctl ps wlT", "fnsysctl cat /sys/kernel/slab/fib6_nodes/total_objects",
        # "fnsysctl cat /sys/kernel/slab/ip6_dst_cache/total_objects"
        #  ]

        command_list = [
        "cat /proc/slabinfo","cat /proc/zoneinfo","cat /proc/meminfo", 
        "ps wlT", "cat /sys/kernel/slab/fib6_nodes/total_objects",
        "cat /sys/kernel/slab/ip6_dst_cache/total_objects"
         ]
         
        self.collect_linux_cmd_batch(cmd=command_list,sw_name=self.name)

    def show_command(self,cmd):
        return switch_show_cmd(self.dut,cmd)

    def show_command_linux(self,cmd):
        switch_show_cmd_linux(self.dut,cmd)

    def disable_diag_debugs(self):
        config = """
        diag debug application bfd 0
        """
        config_cmds_lines(self.console,config)


    def clear_crash_log(self):
        config = "diagnose debug crash clear"
        config_cmds_lines(self.console,config)

    def find_crash(self):
        cmd = "diag debug crashlog read" 
        result = collect_show_cmd(self.console,cmd)

    def reboot_and_relogin(self):
        if self.is_fortinet() == False:
            return 
        else:
            switch_exec_reboot(self.console,device=self.name)

        console_timer(300,msg=f"===== rebooting the switch {self.name}, wait for 300s =====")
        dut = self.console
        Info(f"================= Re-login device: {self.name} =============")
        try:
            relogin_if_needed(dut)
        except Exception as e:
            debug("something is wrong with rlogin_if_needed at bgp, try again")
            relogin_if_needed(dut)
        image = find_dut_image(dut)
        tprint(f"============================ {dut_name} software image = {image} ============")


    def reboot(self):
        if self.is_fortinet() == False:
            return 
        else:
            switch_exec_reboot(self.console,device=self.name)

    def switch_relogin(self,*args,**kwargs):
        if "password" in kwargs:
            pwd = kwargs['password']
        else:
            pwd = self.password
        print(f"============== Relogin switch {self.name}, password = {pwd} ==============")
        tn = self.console
        if switch_find_login_prompt(self.console) == True:
            print("Re-login switch.....")
            tn.read_until(("login: ").encode('ascii'),timeout=10)
            tn.write(('admin' + '\n').encode('ascii'))
            tn.read_until(("Password: ").encode('ascii'),timeout=10)
            tn.write((pwd + '\n').encode('ascii'))
            sleep(1)
            tn.read_until(("# ").encode('ascii'),timeout=10)
            switch_configure_cmd(tn,'config system global',mode="silent")
            switch_configure_cmd(tn,'set admintimeout 480',mode="silent")
            switch_configure_cmd(tn,'end',mode="silent")
            return True
        else:
            switch_configure_cmd(self.console,'config system global',mode='silent')
            switch_configure_cmd(self.console,'set admintimeout 480',mode='silent')
            switch_configure_cmd(self.console,'end',mode='silent')
            return True

    def relogin(self):
        dut = self.console
        Info(f"================= Re-login device: {self.name} =============")
        try:
            relogin_if_needed(dut)
        except Exception as e:
            debug("something is wrong with rlogin_if_needed at bgp, try again")
            relogin_if_needed(dut)
        image = find_dut_image(dut)
        tprint(f"============================ {dut_name} software image = {image} ============")
 
    def config_stp(self,*args,**kwargs):
        if "root" in kwargs:
            root = kwargs['root']
        else:
            root = False

        if root:
            config = """
            config switch stp instance
                edit 0
                set priority 8192
            end
            """
        config_cmds_lines(self.console,config)



    def add_vlan_interface(self,*args,**kwargs):
        vlan_name = kwargs['vlan_name']
        ipv4_addr = kwargs['ipv4_addr']
        ipv6_addr = kwargs['ipv6_addr']
        vlan = kwargs['vlan']

        config = f"""
        config system interface
        edit {vlan_name}
            set ip {ipv4_addr} 255.255.255.0
            set allowaccess ping https ssh telnet
            set secondary-IP enable
                 config ipv6
                    set ip6-address {ipv6_addr}
                    set ip6-allowaccess ping https ssh telnet
                end
            set vlanid {vlan}
            set interface "internal"
            next
        end
        """
        config_cmds_lines(self.console,config)

    def delete_all_vlan_interfaces(self):
        vlans = self.find_vlan_interfaces()
        for v in vlans:
            config = f"""
                config system interface
                delete {v}
            end
        """
        config_cmds_lines(self.console,config)

    def find_sys_interfaces(self,*args,**kwargs):

        # edit "internal"
        #     set ip 1.1.1.100 255.255.255.255
        #     set allowaccess ping https http ssh telnet
        #     set type physical
        #     set snmp-index 34
        #         config ipv6
        #             set ip6-address 2001:1:1:1::100/128
        #             set ip6-allowaccess ping https ssh telnet
        #         end
        # next
        # edit "vlan1000"
        #     set ip 100.1.1.1 255.255.255.0
        #     set allowaccess ping https ssh telnet
        #     set secondary-IP enable
        #     set snmp-index 37
        #         config ipv6
        #             set ip6-address 2001:100:1:1::1/64
        #             set ip6-allowaccess ping https ssh telnet
        #         end
        #     set vlanid 1000
        #     set interface "internal"
        # next
        # edit "loop0"
        #     set ip 1.1.1.1 255.255.255.255
        #     set allowaccess ping https http ssh telnet
        #     set type loopback
        #     set snmp-index 38
        #         config ipv6
        #             set ip6-address 2001:1:1:1::1/128
        #             set ip6-allowaccess ping https ssh telnet
        #         end
        # next
        # self.switch = args[0]
        # self.name = None
        # self.ipv4 = None
        # self.ipv4_mask = None
        # self.allowaccess = None
        # self.type = None
        # self.vlan = None
        # self.ipv6 = None
        if self.is_fortinet() == False:
            return 
        cmd_output = collect_show_cmd(self.console,"show system interface")
        debug(cmd_output)
        sys_int_list = []
        regex_name = r'\s*edit "([a-z0-9]+)"'
        ipv4_regex = r'\s*set ip ([0-9.]+\.[0-9]+) ([0-9.]+\.[0-9]+)'
        ipv6_regex = r'\s*set ip6-address (([a-f0-9:]+:+)+[a-f0-9]+)/([0-9]+)'
        regex_type = r'set type ([a-zA-Z]+)'
        regex_ipv6_extra = r'edit (([a-f0-9:]+:+)+[a-f0-9]+)'
        regex_vlan = r'set vlanid ([0-9]+)'

        new_interface = False
        for line in cmd_output:
            debug (f"system interface ouput:: {line}")
            matched = re.match(regex_name,line)
            if matched:
                name = matched.group(1)
                debug(name)
                sys_interface = System_interface()
                sys_interface.switch = self.console
                sys_interface.name = name
                new_interface = True
                continue
            m = re.match(ipv4_regex,line)
            if m:
                sys_interface.ipv4 = m.group(1)
                sys_interface.ipv4_mask = m.group(2)
                continue
            m = re.match(ipv6_regex,line)
            if m:
                sys_interface.ipv6 = m.group(1)
                sys_interface.ipv6_mask = m.group(3)
                continue
            m = re.match(regex_type,line)
            if m:
                sys_interface.type = m.group(1)
                continue
            m = re.match(regex_ipv6_extra,line)
            if m:
                sys_interface.ipv6_2nd = m.group(1)
                continue
            if "next" in line and new_interface:
                debug (f"problemetic line:: {line}")
                sys_int_list.append(sys_interface)
                new_interface = False
            m = re.match(regex_vlan,line)
            if m:
                sys_interface.vlan_id = m.group(1)
                sys_interface.isvlan = True

        debug(sys_int_list)
        return sys_int_list

    
    def add_extra_ipv6_no_fw(self):
        if self.is_fortinet() == False:
            return 
        for interface in self.sys_interfaces:
            if interface.name == "mgmt":
                continue
            interface.derive_ipv6_extra()
            ipv6_2nd = interface.ipv6_2nd
            mask = interface.ipv6_mask

            dut = self.console
            config = f"""
             config system interface
                edit {interface.name}
                    config ipv6
                        config ip6-extra-addr
                            edit {ipv6_2nd}/{mask}
                        next
                    end
                 end
              next
            end
            """
            config_cmds_lines(self.console,config)

        self.sys_interfaces = self.find_sys_interfaces()


    def turn_on_ipv6_fw(self):
        if self.is_fortinet() == False:
            return 
        for interface in self.sys_interfaces:
            if interface.name == "mgmt":
                continue

            config = f"""
            config system interface
                edit {interface.name}
                    config ipv6
                    set ip6-allowaccess any
            """
            config_cmds_lines(self.console,config)
            switch_interactive_exec(self.console,"end","Do you want to continue? (y/n)")
            config = f"""
            end
            """
            config_cmds_lines(self.console,config)

    def add_extra_ipv6_with_fw(self):
        if self.is_fortinet() == False:
            return 
        for interface in self.sys_interfaces:
            if interface.name == "mgmt":
                continue
            interface.derive_ipv6_extra()
            ipv6_2nd = interface.ipv6_2nd
            mask = interface.ipv6_mask

            dut = self.console
            config = f"""
             config system interface
                edit {interface.name}
                    config ipv6
                        config ip6-extra-addr
                            edit {ipv6_2nd}/{mask}
                        next
                    end
                 end
              next
            end
            """
            config_cmds_lines(self.console,config)

            config = f"""
            config system interface
                edit {interface.name}
                    config ipv6
                    set ip6-allowaccess any
            """
            config_cmds_lines(self.console,config)
            switch_interactive_exec(dut,"end","Do you want to continue? (y/n)")
            config = f"""
            end
            """
            config_cmds_lines(self.console,config)

    def remove_firewall_sys_interface(self):
        if self.is_fortinet() == False:
            return 
        for interface in self.sys_interfaces:
            if interface.name == "mgmt":
                continue

            dut = self.console
             
            config = f"""
            config system interface
                edit {interface.name}
                    config ipv6
                    set ip6-allowaccess ping
                end
            end
            """
            config_cmds_lines(self.console,config)
             

    def find_vlan_interfaces(self):
        result = collect_show_cmd(self.console,"show system interface")
        regex = r'\s+edit "(vlan[0-9]+)"'
        self.vlan_interfaces = []
        for line in result:
             # print(line)
             matched = re.match(regex,line)
             if matched:
                print(matched.group(1))
                self.vlan_interfaces.append(matched.group(1))
        return self.vlan_interfaces
           

    def config_lldp_neighbor_ports(self,*args,**kwargs):
        if self.is_fortinet() == False:
            return 
        Info(f"Configuring ISL ports at {self.name}......")
        if "vlan" in kwargs:
            vlan = kwargs["vlan"]
        else:
            vlan = 2000
        for n in self.lldp_obj_list:
            port = n.local_port

            config = f"""
            config switch interface
                edit {port}
                    set allowed-vlans 1-{vlan}
                next
            end
            """
            config_cmds_lines(self.console,config)

    # def discovery_lldp(self):

    #     output = collect_show_cmd(self.console,"get switch lldp neighbors-summary")
    #     ###################### debug ############################
    #     result = """
    #     S424DP3X16000238 #

    #     2020-07-12 17:36:29:S424DP3X16000238=get switch lldp neighbors-summary


    #     Capability codes:
    #         R:Router, B:Bridge, T:Telephone, C:DOCSIS Cable Device
    #         W:WLAN Access Point, P:Repeater, S:Station, O:Other
    #     MED type codes:
    #         Generic:Generic Endpoint (Class 1), Media:Media Endpoint (Class 2)
    #         Comms:Communications Endpoint (Class 3), Network:Network Connectivity Device

    #       Portname    Status   Device-name                 TTL   Capability  MED-type  Port-ID
    #       __________  _______  __________________________  ____  __________  ________  _______
    #       port1       Up       -                           -     -           -         -
    #       port2       Down     -                           -     -           -         -
    #       port3       Down     -                           -     -           -         -
    #       port4       Down     -                           -     -           -         -
    #       port5       Down     -                           -     -           -         -
    #       port6       Down     -                           -     -           -         -
    #       port7       Down     -                           -     -           -         -
    #       port8       Down     -                           -     -           -         -
    #       port9       Down     -                           -     -           -         -
    #       port10      Down     -                           -     -           -         -
    #       port11      Down     -                           -     -           -         -
    #       port12      Down     -                           -     -           -         -
    #       port13      Down     -                           -     -           -         -
    #       port14      Down     -                           -     -           -         -
    #       port15      Down     -                           -     -           -         -
    #       port16      Down     -                           -     -           -         -
    #       port17      Down     -                           -     -           -         -
    #       port18      Down     -                           -     -           -         -
    #       port19      Down     -                           -     -           -         -
    #       port20      Down     -                           -     -           -         -
    #       port21      Down     -                           -     -           -         -
    #       port22      Down     -                           -     -           -         -
    #       port23      Up       S224EPTF19000002            120   BR          -         port23
    #       port24      Down     -                           -     -           -         -
    #       port25      Down     -                           -     -           -         -
    #       port26      Down     -                           -     -           -         -

    #     S424DP3X16000238 #

    #     """
    #     b= output.split("\n")
    #     result = [x.encode('utf-8').strip() for x in b if x.strip()]
    #     printr("========== DiscoveryLLDP starts here ===========")
    #     # result = self.ShowCmd("get switch lldp neighbors-summary")
    #     printr(result)
    #     ###################### debug ############################
    #     self.parse_lldp(result)

       
    def discover_lldp_neighbors(self):
        if self.is_fortinet() == False:
            return 
        Info(f"Discovering LLDP neighbors and updating LLDP database at {self.name}......")
        lldp_obj_list = []
        lldp_dict_list = []

        output = collect_show_cmd(self.console,"get switch lldp neighbors-summary")
        #print(output)
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
        print(self.lldp_dict_list)



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



    def cisco_config_full(self):
        dut = self.dut
        if self.platform == "n9k":
            config = """
            config t
            router bgp 65000
              router-id 10.10.10.10
              address-family ipv4 unicast
                maximum-paths 4
              address-family ipv6 unicast
                maximum-paths 4
              neighbor 2001:1:1:1::1
                remote-as 65000
                update-source loopback0
                address-family ipv6 unicast
              neighbor 2001:2:2:2::2
                remote-as 65000
                update-source loopback0
                address-family ipv6 unicast
              neighbor 2001:3:3:3::3
                remote-as 65000
                update-source loopback0
                address-family ipv6 unicast
              neighbor 2001:4:4:4::4
                remote-as 65000
                update-source loopback0
                address-family ipv6 unicast
              neighbor 2001:5:5:5::5
                remote-as 65000
                update-source loopback0
                address-family ipv6 unicast
              neighbor 2001:6:6:6::6
                remote-as 65000
                update-source loopback0
                address-family ipv6 unicast
              neighbor 2001:10:1:1::1
                remote-as 65000
                update-source Vlan1
                address-family ipv6 unicast
              neighbor 2001:10:1:1::2
                remote-as 65000
                update-source Vlan1
                address-family ipv6 unicast
              neighbor 2001:10:1:1::3
                remote-as 65000
                update-source Vlan1
                address-family ipv6 unicast
              neighbor 2001:10:1:1::4
                remote-as 65000
                update-source Vlan1
                address-family ipv6 unicast
              neighbor 2001:10:1:1::5
                remote-as 65000
                update-source Vlan1
                address-family ipv6 unicast
              neighbor 2001:10:1:1::6
                remote-as 65000
                update-source Vlan1
                address-family ipv6 unicast
              neighbor 2001:10:1:1::213
                remote-as 103
                address-family ipv6 unicast
              neighbor 2001:10:1:1::214
                remote-as 104
                address-family ipv6 unicast
              neighbor fe80::6d5:90ff:fe2e:22a7
                remote-as 65000
                address-family ipv6 unicast
              neighbor fe80::724c:a5ff:fea5:a219
                remote-as 65000
                address-family ipv6 unicast
              neighbor fe80::926c:acff:fe0c:bceb
                remote-as 65000
                address-family ipv6 unicast
              neighbor fe80::926c:acff:fe13:9575
                remote-as 65000
                address-family ipv6 unicast
              neighbor fe80::926c:acff:fe6d:c951
                remote-as 65000
                address-family ipv6 unicast
              neighbor fe80::ea1c:baff:fe88:d15f
                remote-as 65000
                address-family ipv6 unicast
              neighbor 1.1.1.1
                remote-as 65000
                update-source loopback0
                address-family ipv4 unicast
              neighbor 2.2.2.2
                remote-as 65000
                update-source loopback0
                address-family ipv4 unicast
              neighbor 3.3.3.3
                remote-as 65000
                update-source loopback0
                address-family ipv4 unicast
              neighbor 4.4.4.4
                remote-as 65000
                update-source loopback0
                address-family ipv4 unicast
              neighbor 5.5.5.5
                remote-as 65000
                update-source loopback0
                address-family ipv4 unicast
              neighbor 6.6.6.6
                remote-as 65000
                update-source loopback0
                address-family ipv4 unicast
              neighbor 10.1.1.1
                remote-as 65000
                address-family ipv4 unicast
              neighbor 10.1.1.2
                remote-as 65000
                address-family ipv4 unicast
              neighbor 10.1.1.3
                remote-as 65000
                address-family ipv4 unicast
              neighbor 10.1.1.4
                remote-as 65000
                address-family ipv4 unicast
              neighbor 10.1.1.5
                remote-as 65000
                address-family ipv4 unicast
              neighbor 10.1.1.6
                remote-as 65000
                address-family ipv4 unicast
              neighbor 10.1.1.213
                remote-as 103
                address-family ipv4 unicast
              neighbor 10.1.1.214
                remote-as 104
                address-family ipv4 unicast
                end
            """
            config_cmds_lines(dut,config)


    def cisco_config_full_2(self):
        dut = self.dut
        if self.platform == "n9k":
            debug("======Enter into cisco_config_full_2")
            config = """
            config t
            router bgp 65000
              router-id 10.10.10.10
              address-family ipv4 unicast
                maximum-paths 4
              address-family ipv6 unicast
                redistribute direct route-map known-community
                aggregate-address 2001:105:1:1::/64 as-set summary-only
                maximum-paths 4
              neighbor 2001:1:1:1::1
                remote-as 65000
                update-source loopback0
                address-family ipv6 unicast
              neighbor 2001:2:2:2::2
                remote-as 65000
                update-source loopback0
                address-family ipv6 unicast
              neighbor 2001:3:3:3::3
                remote-as 65000
                update-source loopback0
                address-family ipv6 unicast
              neighbor 2001:4:4:4::4
                remote-as 65000
                update-source loopback0
                address-family ipv6 unicast
              neighbor 2001:5:5:5::5
                remote-as 65000
                update-source loopback0
                address-family ipv6 unicast
              neighbor 2001:6:6:6::6
                remote-as 65000
                update-source loopback0
                address-family ipv6 unicast
              neighbor 2001:10:1:1::1
                remote-as 65000
                update-source Vlan1
                address-family ipv6 unicast
              neighbor 2001:10:1:1::2
                remote-as 65000
                update-source Vlan1
                address-family ipv6 unicast
              neighbor 2001:10:1:1::3
                remote-as 65000
                update-source Vlan1
                address-family ipv6 unicast
              neighbor 2001:10:1:1::4
                remote-as 65000
                update-source Vlan1
                address-family ipv6 unicast
              neighbor 2001:10:1:1::5
                remote-as 65000
                update-source Vlan1
                address-family ipv6 unicast
              neighbor 2001:10:1:1::6
                remote-as 65000
                update-source Vlan1
                address-family ipv6 unicast
              neighbor 2001:10:1:1::213
                remote-as 103
                address-family ipv6 unicast
              neighbor 2001:10:1:1::214
                remote-as 104
                address-family ipv6 unicast
              neighbor fe80::6d5:90ff:fe2e:22a7
                remote-as 65000
                address-family ipv6 unicast
              neighbor fe80::724c:a5ff:fea5:a219
                remote-as 65000
                address-family ipv6 unicast
              neighbor fe80::926c:acff:fe0c:bceb
                remote-as 65000
                address-family ipv6 unicast
              neighbor fe80::926c:acff:fe13:9575
                remote-as 65000
                address-family ipv6 unicast
              neighbor fe80::926c:acff:fe6d:c951
                remote-as 65000
                address-family ipv6 unicast
              neighbor fe80::ea1c:baff:fe88:d15f
                remote-as 65000
                address-family ipv6 unicast
              neighbor 1.1.1.1
                remote-as 65000
                update-source loopback0
                address-family ipv4 unicast
              neighbor 2.2.2.2
                remote-as 65000
                update-source loopback0
                address-family ipv4 unicast
              neighbor 3.3.3.3
                remote-as 65000
                update-source loopback0
                address-family ipv4 unicast
              neighbor 4.4.4.4
                remote-as 65000
                update-source loopback0
                address-family ipv4 unicast
              neighbor 5.5.5.5
                remote-as 65000
                update-source loopback0
                address-family ipv4 unicast
              neighbor 6.6.6.6
                remote-as 65000
                update-source loopback0
                address-family ipv4 unicast
              neighbor 10.1.1.1
                remote-as 65000
                address-family ipv4 unicast
              neighbor 10.1.1.2
                remote-as 65000
                address-family ipv4 unicast
              neighbor 10.1.1.3
                remote-as 65000
                address-family ipv4 unicast
              neighbor 10.1.1.4
                remote-as 65000
                address-family ipv4 unicast
              neighbor 10.1.1.5
                remote-as 65000
                address-family ipv4 unicast
              neighbor 10.1.1.6
                remote-as 65000
                address-family ipv4 unicast
              neighbor 10.1.1.213
                remote-as 103
                address-family ipv4 unicast
              neighbor 10.1.1.214
                remote-as 104
                address-family ipv4 unicast
                end
            """
            config_cmds_lines(dut,config)

    def config_commands(self,config):
        dut = self.dut
        config_cmds_lines(dut,config)

    def cisco_config_ibgp_ixia(self):
        dut = self.dut

        config = """
        config t
        router bgp 65000
          neighbor 2001:10:1:1::213
            remote-as 65000
            address-family ipv6 unicast
          neighbor 2001:10:1:1::214
            remote-as 65000
            address-family ipv6 unicast
          neighbor 10.1.1.213
            remote-as 65000
            address-family ipv4 unicast
          neighbor 10.1.1.214
            remote-as 65000
            address-family ipv4 unicast
            end
        """
        config_cmds_lines_cisco(dut,config)


    def cisco_config_ebgp_ixia(self):
        Info(f"Configuring IPv4 and IPv6 eBGP on Cisco Nexus 9k")

        dut = self.dut

        config = """
        conf t
        router bgp 65000
          neighbor 2001:10:1:1::213
            remote-as 103
            address-family ipv6 unicast
          neighbor 2001:10:1:1::214
            remote-as 104
            address-family ipv6 unicast
          neighbor 10.1.1.213
            remote-as 103
            address-family ipv4 unicast
          neighbor 10.1.1.214
            remote-as 104
            address-family ipv4 unicast
            end
        """
        config_cmds_lines_cisco(dut,config)


    def show_basic_info(self):
        Info(f"FortiSwitch _init_:Switch Name = {self.name}")

    def discover_ipv6_neighbors(self,*args,**kwargs):
        # 3032D-R7-40 # diagnose ipv6 neighbor-cache list | grep fe80
        # ifindex=46 ifname=vlan1 fe80::6d5:90ff:fe2e:22a7 04:d5:90:2e:22:a7 state=00000002 use=1408794 confirm=1725 update=1408794 ref=1
        # ifindex=46 ifname=vlan1 fe80::ea1c:baff:fe88:d15f e8:1c:ba:88:d1:5f state=00000002 use=1414615 confirm=2592 update=1414615 ref=1
        # ifindex=5 ifname=mgmt fe80::8058:7190:cd95:e51a state=00000000 use=1294278 confirm=1330278 update=1294278 ref=0
        # ifindex=46 ifname=vlan1 fe80::926c:acff:fe6d:c951 90:6c:ac:6d:c9:51 state=00000002 use=627073 confirm=799 update=627073 ref=1
        # ifindex=5 ifname=mgmt fe80::926c:acff:fe15:2f98 90:6c:ac:15:2f:98 state=00000004 use=2622815 confirm=2658815 update=2622815 ref=0
        # ifindex=46 ifname=vlan1 fe80::926c:acff:fe0c:bceb 90:6c:ac:0c:bc:eb state=00000002 use=1406945 confirm=5921 update=1406945 ref=1
        # ifindex=46 ifname=vlan1 fe80::7e21:eff:fe39:a3e7 7c:21:0e:39:a3:e7 state=00000002 use=2637329 confirm=2097 update=2637329 ref=1
        # ifindex=46 ifname=vlan1 fe80::724c:a5ff:fea5:a219 70:4c:a5:a5:a2:19 state=00000002 use=1406820 confirm=5275 update=1406819 ref=1

        if "interface" in kwargs:
            interface = kwargs['interface']
        else:
            interface = "vlan1"
        dut = self.console
        result = collect_show_cmd(dut,"diagnose ipv6 neighbor-cache list | grep fe80")
        neighbor_list = []
        for line in result:
            if  interface in line:
                items = re.split('\\s+',line)
                neighbor_dict = {}
                neighbor_dict[items[3]] = items[2]
                neighbor_list.append(neighbor_dict) 
                self.ipv6_neighbors.append(items[2])
        return neighbor_list


    
    def discover_sys_arp(self,*args,**kwargs):
        # 3032E-R7-19 # get system arp
        # Address           Age(min)   Hardware Addr      Interface
        # 10.1.1.10         0          7c:21:0e:39:a3:e7  vlan1
        # 10.1.1.5          0          90:6c:ac:0c:bc:eb  vlan1
        # 10.1.1.4          0          90:6c:ac:6d:c9:51  vlan1
        # 10.1.1.6          0          70:4c:a5:a5:a2:19  vlan1
        # 10.1.1.3          0          04:d5:90:2e:22:a7  vlan1
        # 10.1.1.2          0          90:6c:ac:13:95:75  vlan1
        # 10.105.241.254    1          90:6c:ac:15:2f:98  mgmt

        if "interface" in kwargs:
            interface = kwargs['interface']
        else:
            interface = "vlan1"
        dut = self.console
        result = collect_show_cmd(dut,"get system arp")
        arp_dict = {}
        for line in result:
            if  interface in line:
                items = re.split('\\s+',line)
                arp_dict[items[2]] = items[0]
                self.ipv4_neighbors.append(items[0].strip())
                self.mac_neighbors.append(items[2].strip())
        return arp_dict


    def is_fortinet(self):
        if self.platform == "fortinet":
            return True
        else:
            return False

    def backup_config(self,file_name):
        cmd = f"execute backup config tftp {file_name} 10.105.19.19"
        switch_exec_cmd(self.console,cmd)
        console_timer(2)
        
    def restore_config(self,file_name):
        #restore a file will cause switch to reboot
        cmd = f"execute restore config tftp {file_name} 10.105.19.19"
        switch_exec_cmd(self.console,cmd)
        switch_enter_yes(self.console)


    def check_route_exist(self,nets):
        return check_route_exist(dut=self.console,networks=nets,cmd="get router info routing-table all")

    def show_vlan_neighbors(self):
        tprint(self.neighbor_ip_list)

    def vlan_neighors(self,other_switches):
        lldp_neighbors = self.lldp_neighbor_list
        neighbor_ip_list = []
        neighbor_switch_list = []
        for neighbor in lldp_neighbors:
            if neighbor["Status"]  == 'Up':
                # print( neighbor["Device-name"])
                # debug(f"lldp neighbor dict = {self.lldp_neighbor_list}")
                for switch in other_switches:
                    #print(f"switch.name = {switch.name}")
                    if neighbor["Device-name"].strip() == switch.name:
                        neighbor_ip_list.append(switch.vlan1_ip)
                        neighbor_switch_list.append(switch)
                        break
        #print(neighbor_ip_list)
        self.neighbor_ip_list= neighbor_ip_list
        self.neighbor_switch_list = neighbor_switch_list

    def show_routing(self):
        if self.is_fortinet() == False:
            return 
        self.show_routing_table()
        self.router_ospf.show_protocol_states()
        self.router_bgp.show_protocol_states()

    def show_routing_v6(self):
        if self.is_fortinet() == False:
            return 
        self.show_routing_table_v6()
        self.router_ospf.show_protocol_states_v6()
        self.router_bgp.show_bgp_protocol_states_v6()

    def show_routing_table(self):
        switch_show_cmd(self.console,"get router info routing-table all")
        switch_show_cmd(self.console,"get router info routing-table ospf")
        switch_show_cmd(self.console,"get router info routing-table bgp ")

    def show_routing_table_v6(self):
        switch_show_cmd(self.console,"get router info6 routing-table")
        switch_show_cmd(self.console,"get router info6 routing-table ospf")
        switch_show_cmd(self.console,"get router info6 routing-table bgp")

    def show_routing_table_v64(self):
        self.show_routing_table()
        self.show_routing_table_v6()


    def factory_reset_nologin(self):
        switch_factory_reset_nologin(self.dut_dir)

    # def relogin(self):
    #     dut = self.console
    #     tprint(f"============ relogin {self.name} ====== ")
    #     try:
    #         relogin_if_needed(dut)
    #     except Exception as e:
    #         debug("something is wrong with rlogin_if_needed at bgp test cases, try again")
    #         relogin_if_needed(dut)
    #     image = find_dut_image(dut)
    #     tprint(f"============================ {self.name} software image = {image} ============")
    #     switch_show_cmd(self.console,"get system status")
    
    def show_log(self):
        sw_display_log(self.console,lines=200)

    def relogin_after_factory(self):
        tprint('-------------------- re-login switch after factory rest-----------------------')
        dut_com = self.dut_dir['comm'] 
        dut_port = self.dut_dir['comm_port']
        dut = get_switch_telnet_connection_new(dut_com,dut_port)
        self.dut_dir['telnet'] = dut
        self.console = dut
        self.dut = dut
        self.router_ospf = Router_OSPF(self)
        self.router_bgp = Router_BGP(self)
        # self.router_ospf.update_switch(self)
        # self.router_bgp.update_switch(self)

    def show_switch_info(self):
        if self.is_fortinet() == False:
            return
        tprint("=====================================================================")
        tprint(f"   Comm Server = {self.comm}")
        tprint(f"   Comm Server Port = {self.comm_port}")
        tprint(f"   Rack Location = {self.location}")
        tprint(f"   Management IP address = {self.mgmt_ip}")
        tprint(f"   Management IP address Mask = {self.mgmt_mask}")
        tprint(f"   Loopback0 IP address  = {self.loop0_ip}")
        tprint(f"   VLAN 1 IP address  = {self.vlan1_ip}")
        tprint(f"   VLAN 1 IP Mask  = {self.vlan1_mask}")
        tprint(f"   Split Ports  = {self.split_ports}")
        tprint(f"   40G Ports  = {self.ports_40g}")
        tprint("\n")

    def config_static_routes(self,num):
        for i in range(2,num+2):
            config = f"""
                config router static
                edit {i}
                    set dst {self.static_route}.{i} 255.255.255.255
                    set gateway {self.router_ospf.neighbor_list[0].address}
                    next
                end
            """
            config_cmds_lines(self.console,config)

    def config_static_route_host(self,*args,**kwargs):
        index = kwargs['index']
        dst = kwargs['dst']
        gw = kwargs['gw']
        config = f"""
            config router static
            edit {index}
                set dst {dst} 255.255.255.255
                set gateway {gw}
                next
            end
        """
        config_cmds_lines(self.console,config)

    def config_static6_route_host(self,*args,**kwargs):
        index = kwargs['index']
        dst = kwargs['dst']
        gw = kwargs['gw']
        config = f"""
            config router static6
            edit {index}
                set dst {dst}/128 
                set gateway {gw}
                next
            end
        """
        config_cmds_lines(self.console,config)


    def pre_restore_config(self):
        dut = self.dut
        config_global_hostname = f"""
        config system global
        set hostname {self.name}
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
            set ip {self.mgmt_ip} {self.mgmt_mask}
            set allowaccess ping https http ssh snmp telnet radius-acct
            next
        edit vlan1
            set ip {self.vlan1_ip} {self.vlan1_mask}
            set allowaccess ping https ssh telnet
            set vlanid 1
            set interface internal
            set secondary-IP enable 
            config secondaryip 
                edit 1
                    set ip {self.vlan1_2nd} 255.255.255.255
                    set allowaccess ping https ssh telnet
                next
                end
            next
        edit "loop0"
            set ip {self.loop0_ip} 255.255.255.255
            set allowaccess ping https http ssh telnet
            set type loopback
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


    def init_config(self):
        dut = self.dut
        config_global_hostname = f"""
        config system global
        set hostname {self.name}
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
            set ip {self.mgmt_ip} {self.mgmt_mask}
            set allowaccess ping https http ssh snmp telnet radius-acct
            next
        edit vlan1
            set ip {self.vlan1_ip} {self.vlan1_mask}
            set allowaccess ping https ssh telnet
            set vlanid 1
            set interface internal
            set secondary-IP enable 
            config secondaryip 
                edit 1
                    set ip {self.vlan1_2nd} 255.255.255.255
                    set allowaccess ping https ssh telnet
                next
                end
            next
        edit "loop0"
            set ip {self.loop0_ip} 255.255.255.255
            set allowaccess ping https http ssh telnet
            set type loopback
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

        for port in self.ports_40g:
            sw_config_port_speed(dut,port,"40000cr4")

        for port in self.split_ports:
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

        for port in self.split_ports:
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

    def config_sys_interface(self,num):
        dut = self.console
        label = self.label
        net,host = ip_break_up(self.loop0_ip)
        if net == None or host == None:
            tprint("Something is wrong with loopback address breakup" )
            return False

        for i in range(2,num+2):
            config  = f"""
            config system interface
            edit vlan{i}
                set vlanid {i}
                set interface internal
                set ip 10.1.{i}.{label} {self.vlan1_mask}
                set allowaccess ping https ssh telnet
            next
            edit loop{i}
                set type loopback
                set ip {net}.{int(host)+i} 255.255.255.255
                set allowaccess ping https http ssh telnet
                
            next
            end
            """
            config_cmds_lines(dut,config)

    def config_sys_vlan_v6(self,*args,**kwargs):
        dut = self.console
        ipv6 = kwargs["ipv6"]
        ipv4 = kwargs["ipv4"]
        vlan_id = kwargs["vlan"]
         
        config  = f"""
        config system interface
        edit vlan{vlan_id}
            set ip {ipv4} 255.255.255.255
            set allowaccess ping https ssh telnet
            set vlanid {vlan_id}
            set interface internal
            config ipv6
                set ip6-address {ipv6}/128
                set ip6-allowaccess ping https ssh telnet
            end
        next
        end
        """
        config_cmds_lines(dut,config)

    def fsw_show_cmd(self,cmd):
        dut = self.console
        result = collect_show_cmd(dut,cmd,t=3)
        return result
        #print_collect_show(result)

    def sw_fnsysctl_process(self,lw_list):
        lw_dict = {}
        for item in lw_list:
            print(item)
            if "PID" in item or "VSZ" in item:
                continue 
            item_list = item.split()
            if len(item_list) < 10:
                continue
            #print(item_list)
            lw_dict[item_list[9]] = int(item_list[5])

        # print(lw_dict)
        return lw_dict

class FortiSwitch_XML(FortiSwitch):
    def __init__(self,*args,**kwargs):
        device_xml = args[0]
        self.tb=kwargs['topo_db']
        if "password" in kwargs:
            self.password = kwargs['password']
        else:
            self.password = device_xml.password
        self.last_cmd_time = None
        self.ixia_ports = device_xml.ixia_ports
        self.version = None
        self.image_prefix = None
        self.name = device_xml.name
        self.hostname = device_xml.hostname
        self.console_ip = device_xml.console_ip
        self.console_line = device_xml.console_line
        self.tftp_ip = device_xml.tftp_ip
        self.pdu_model = device_xml.pdu_model
        self.pdu_ip = device_xml.pdu_ip
        self.pdu_port = device_xml.pdu_port
        self.pdu_ip_2 = device_xml.pdu_ip_2
        self.pdu_port_2 = device_xml.pdu_port_2
        self.dual_pdu = device_xml.dual_pdu
        self.username = device_xml.username
        self.mgmt_ip = device_xml.mgmt_ip
        self.loop0_ip = None
        self.ebgp_as = None
        self.mgmt_netmask = device_xml.mgmt_netmask
        self.mgmt_gateway = device_xml.mgmt_gateway
        self.license = device_xml.license
        self.role = device_xml.role
        try:
            self.cluter = int(re.match(r'tier([0-9]+)-([0-9]+)-([0-9]+)',device_xml.role).group(3)) 
            self.tier = int(re.match(r'tier([0-9]+)-([0-9]+)-([0-9]+)',device_xml.role).group(1)) 
            self.pod = int(re.match(r'tier([0-9]+)-([0-9]+)-([0-9]+)',device_xml.role).group(2)) 
        except Exception as e:
            self.cluter = None
            self.tier = None
            self.pod = None
        self.type = device_xml.type
        self.active = device_xml.active
        self.uplink_ports = device_xml.uplink_ports
        self.fortigate_ports_db = device_xml.fortigate_ports
        self.platform = "fortinet"
        self.trunk_list = []
        self.icl_links = []
        self.up_links = []
        self.down_links = []
        self.up_links_pod = {}
        self.down_links_pod = {}
        self.fortigate_links = []
        self.lldp_neighbors_list = []
        self.managed = False
        self.ftg_console = None # To be provided when the switch is managed.  see foritgate_xml discover_managed_switches()
        self.console = telnet_switch(self.console_ip,self.console_line,password=self.password)
        self.dut = self.console # For compatibility with old Fortiswitch codes
        self.switch_system_status()
        self.system_interfaces = self.find_sys_interfaces()
        self.split_ports = []
        self.split_port_exist = False
        self.find_split_ports()
        self.router_ospf = Router_OSPF(self)
        self.router_isis = Router_ISIS(self)
        self.router_bgp = Router_BGP(self)
        self.system_interfaces_list = None
        
    def find_split_ports(self):
        self.split_ports = []
        for port in self.ixia_ports: 
            if "." in port:
                dprint(f"find split port: {port}")
                port_name = port.split(".")[0]
                self.split_ports.append(port_name)
                self.split_port_exist = True
        Info(f"At switch {self.hostname}, split ports are {self.split_ports}")
        Info(f"At switch {self.hostname}, split ports exist = {self.split_port_exist}")

    def fnsysctl_bcm_output(self):
        bcm_cmds = f"""
        fnsysctl shell
        bcm.user.proxy

        fp show

        exit
        exit
        """
        print_show_cmd_list_generic(self.console,bcm_cmds)

    def delete_vlan_interfaces(self):
        for interface in self.system_interfaces:
            if interface.isvlan or "vlan" in interface.name:
                cmds = f"""
                config system interface
                delete {interface.name}
                end
                """
                self.config_cmds_fast(cmds)

    def sw_add_ebgp_peer(self,*args,**kwargs):
        ip = kwargs['ip']
        remote_as = kwargs['remote_as']
        local_as = kwargs['local_as']
        router_id = kwargs['router_id']

        if '/' in ip:
            ip_addr,mask= seperate_ip_mask(ip)

        bgp_config = f"""
        config router bgp
            set as {local_as}
            set router-id {router_id}
            config neighbor
            edit {ip_addr}
                set remote-as {remote_as}
            next
            end
        end
        """
        config_cmds_lines(self.console,bgp_config)

    def exec_command(self,cmd):
         switch_exec_cmd(self.console, cmd)

    def power_cycle(self,*args,**kwargs):
        sample = """
        (base) 21:48:55:~/Python/python/ixia_automation % telnet 10.105.50.114

        Trying 10.105.50.114...
        Connected to 10.105.50.114.
        Escape character is '^]'.

        User Name :
        User Name : apc
        Password  : ***


        American Power Conversion               Network Management Card AOS      v3.7.4
        (c) Copyright 2009 All Rights Reserved  Rack PDU APP                     v3.7.4
        -------------------------------------------------------------------------------
        Name      : rack8-b                                   Date : 11/23/2007
        Contact   : Unknown                                   Time : 09:28:08
        Location  : QA324-RACK-20:A:P1                        User : Administrator
        Up Time   : 219 Days 10 Hours 40 Minutes              Stat : P+ N+ A+

        Switched Rack PDU: Communication Established

        ------- Control Console -------------------------------------------------------

             1- Device Manager
             2- Network
             3- System
             4- Logout

             <ESC>- Main Menu, <ENTER>- Refresh, <CTRL-L>- Event Log
        > 1

        ------- Device Manager --------------------------------------------------------

             1- Bank Management
             2- Outlet Management
             3- Power Supply Status
             4- PDU Configuration

             <ESC>- Back, <ENTER>- Refresh, <CTRL-L>- Event Log
        > 2

        ------- Outlet Management -----------------------------------------------------

             1- Outlet Control/Configuration
             2- Outlet Restriction

             <ESC>- Back, <ENTER>- Refresh, <CTRL-L>- Event Log
        > 1

        ------- Outlet Control/Configuration ------------------------------------------

             1- Outlet 1                 ON
             2- Outlet 2                 ON
             3- Outlet 3                 ON
             4- Outlet 4                 ON
             5- Outlet 5                 ON
             6- Outlet 6                 ON
             7- Outlet 7                 ON
             8- Outlet 8                 ON
             9- Outlet 9                 ON
            10- Outlet 10                ON
            11- Outlet 11                ON
            12- Outlet 12                ON
            13- Outlet 13                ON
            14- Outlet 14                ON
            15- Outlet 15                ON
            16- Outlet 16                ON
            17- Master Control/Configuration

             <ESC>- Back, <ENTER>- Refresh, <CTRL-L>- Event Log
        > 9

        ------- Outlet 9 --------------------------------------------------------------

                Name         : Outlet 9
                Outlet       : 9
                State        : ON
                Bank         : 2

             1- Control Outlet
             2- Configure Outlet

             ?- Help, <ESC>- Back, <ENTER>- Refresh, <CTRL-L>- Event Log
        > 1

        ------- Control Outlet --------------------------------------------------------

                Name         : Outlet 9
                Outlet       : 9
                State        : ON
                Bank         : 2

             1- Immediate On
             2- Immediate Off
             3- Immediate Reboot
             4- Delayed On
             5- Delayed Off
             6- Delayed Reboot
             7- Cancel

             ?- Help, <ESC>- Back, <ENTER>- Refresh, <CTRL-L>- Event Log
        > 3
                -----------------------------------------------------------------------
                Immediate Reboot

                This command will immediately shutdown
                outlet 9 named 'Outlet 9', delay for 5 seconds,
                and then restart.

                Enter 'YES' to continue or <ENTER> to cancel : YES
                Command successfully issued.

                Press <ENTER> to continue...


        ------- Control Outlet --------------------------------------------------------

                Name         : Outlet 9
                Outlet       : 9
                State        : ON
                Bank         : 2

             1- Immediate On
             2- Immediate Off
             3- Immediate Reboot
             4- Delayed On
             5- Delayed Off
             6- Delayed Reboot
             7- Cancel

             ?- Help, <ESC>- Back, <ENTER>- Refresh, <CTRL-L>- Event Log
        >
        """
        pdu = telnet_apc(self.pdu_ip)
        print( self.pdu_model)
        if self.pdu_model == "RARITAN_C":
            telnet_send_cmd(pdu,f"oloff {self.pdu_port} ")
            sleep(2)
            telnet_send_cmd(pdu,f"olon {self.pdu_port} ")
            sleep(2)
            telnet_send_cmd(pdu,"exit")
        elif self.pdu_model == "RARITAN_M":
            sequences = [1,2,1,self.pdu_port,1,3,"YES","\n"]
            for s in sequences:
                telnet_send_cmd(pdu,f"{s}")
                sleep(2)
            send_ctrl_c_cmd(pdu)
            sleep(2)
            telnet_send_cmd(pdu,"4")

    def config_split_port(self):
        jinja_sample = """
        config switch acl 802-1X  
        {% for acl_index in range(1,acl_length + 1) %}
        delete {{ acl_index }}
        {% endfor -%}
        end
        config switch acl service custom
            delete {{filter_name}}
            next
        end
        """
        yaml_string = f"""
        split_port_list: {self.split_ports}
        """

        jinja_string = """
        config switch phy-mode
        {% for port in split_port_list %}
        set {{port}}-phy-mode 4x10G
        {% endfor -%}
        end
        """
        Info(f"config_split_port: Configuring split ports {self.split_ports} ")
        config = yaml.safe_load(yaml_string)
        template = Template(jinja_string)
        result = template.render(config)
        self.config_cmds_fast(result)
        # cmds = f"""
        #     config switch phy-mode
        #     set {port}-phy-mode 4x10G
        #     end
        # """
        # sw.config_cmds_fast(cmds)
        switch_enter_yes(self.console)
        console_timer(200,msg="switch is being rebooted after configuring split port, wait for 200s")
        try:
            self.switch_relogin()
        except Exception as e:
            debug("something is wrong with rlogin_if_needed at functionsw_init_config, try again")
            self.switch_relogin()

    def pdu_status(self):
        a = apc()
        Status = {}
        Status = a.get_status(self.pdu_ip, self.pdu_port)
        print(Status)
    
    def pdu_on(self):
        a = apc()
        Status = {}
        Status = a.set_off(self.pdu_ip, self.pdu_port)
        print(Status)

    def pdu_off(self):
        a = apc()
        Status = {}
        Status = a.set_on(self.pdu_ip, self.pdu_port)
        print(Status)

    def recover_password(self,image_name):
        sample = """
        [G]:  Get firmware image from TFTP server.
        [F]:  Format boot device.
        [C]:  Copy boot device to another one.
        [I]:  Configuration and Information.
        [U]:  Upgrade BIOS image.
        [R]:  Reboot FortiSwitch.
        [Q]:  Quit menu and continue to boot.
        [H]:  Display this list of options.

        Enter G,F,C,I,U,R,Q,or H:

        Enter G,F,C,I,U,R,Q,or H:

        Enter G,F,C,I,U,R,Q,or H: f

        Format partition Default/Backup/Data2:[D/B/S]? d

        Formating Default partition ... 100%

        Enter G,F,C,I,U,R,Q,or H: f

        Format partition Default/Backup/Data2:[D/B/S]? b

        Formating Backup partition ... 100%

        Enter G,F,C,I,U,R,Q,or H: f

        Format partition Default/Backup/Data2:[D/B/S]? s

        Formating Data2 partition ... 100%

        Enter G,F,C,I,U,R,Q,or H: f

        Format partition Default/Backup/Data2:[D/B/S]?
        Format partition Default/Backup/Data2:[D/B/S]? d

        Formating Default partition ... 100%

        Enter G,F,C,I,U,R,Q,or H: g

        Enter TFTP server address [10.105.3.38]: 10.105.19.19
        Enter local address [10.1.1.111]: 10.105.50.25
        Enter local netmask [255.255.255.0]:
        Enter default gateway [10.1.1.1]: 10.105.50.254
        Enter firmware image file name [248ef.out]: FSW_248E_FPOE-v6-build0478-FORTINET.out
        Save as Default/Backup/Run without saving:[D/B/R]? d

        Loading [ 28826982, 28826982 ]   Success


        """
        a = apc()
        Status = {}
        
        Status = a.set_reboot(self.pdu_ip, self.pdu_port)
        print(Status)
        if self.dual_pdu == True:
            Status = a.set_reboot(self.pdu_ip_2, self.pdu_port_2)
            print(Status)

        for i in range(20):
            self.console.write(convert_cmd_ascii_n("X"))
            sleep(0.5)
        
        self.console.write(convert_cmd_ascii_n("f"))
        sleep(2)
        self.console.write(convert_cmd_ascii_n("d"))
        sleep(5)
        self.console.write(convert_cmd_ascii_n("f"))
        sleep(2)
        self.console.write(convert_cmd_ascii_n("b"))
        sleep(5)
        self.console.write(convert_cmd_ascii_n("f"))
        sleep(2)
        self.console.write(convert_cmd_ascii_n("s"))
        sleep(5)
        self.console.write(convert_cmd_ascii_n("g"))
        sleep(2)
        self.console.write(convert_cmd_ascii_n(f"{self.tftp_ip}"))
        sleep(2)
        self.console.write(convert_cmd_ascii_n(f"{self.mgmt_ip}"))
        sleep(2)
        self.console.write(convert_cmd_ascii_n(f"{self.mgmt_netmask}"))
        sleep(2)
        self.console.write(convert_cmd_ascii_n(f"{self.mgmt_gateway}"))
        sleep(2)
        self.console.write(convert_cmd_ascii_n(image_name))
        sleep(2)



    def pdu_cycle_bios(self):
        a = apc()
        Status = {}
        Status = a.set_reboot(self.pdu_ip, self.pdu_port)
        print(Status)
        cmd = convert_cmd_ascii_n("R")
        self.console.write(cmd)
        sleep(0.5)
        self.console.write(cmd)
        sleep(0.5)
        self.console.write(cmd)
        sleep(0.5)
        self.console.write(cmd)
        sleep(0.5)
        self.console.write(cmd)
        sleep(0.5)
        self.console.write(cmd)
        sleep(0.5)
        self.console.write(cmd)
        sleep(0.5)
        self.console.write(cmd)
        sleep(0.5)

    def get_poe_env(self):
        sample = """
        poe_port_legacy=
        poe_guard_band=19
        poe_power_bank=15
        poe_power_policy=0
        poe_priority_medium=
        poe_priority_high=
        poe_priority_critical=
        poe_priority_low=1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24
        poe_perpetual_fast=1,3
        poe_port_enable=1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24
        poe_power_budget=220
        poe_perpetual=2,4
        """
        output = collect_show_cmd(self.console,"diagnose hardware sysinfo bootenv")
        dprint(output)
        poe_env_dict = {}
        for line in output:
            if "poe" in line:
                try:
                    k,v = line.split("=")
                    if "," in v:
                        v = v.split(",")
                        v = [int(i) for i in v]
                        poe_env_dict[k] = v
                    else:
                        poe_env_dict[k] = [v]
                except Exception as e: 
                    pass
        return poe_env_dict


    def get_poe_inline(self):
        sample = """
        S108FFTV21000007 # get switch poe  inline

        Unit Power Budget: 70.00W
        Unit Guard Band: 10.00W
        Unit Power Consumption: 56.00W
        Unit Temperature: 46.00 Centigrade
        Unit Poe Power Mode : Priority Based.


        Interface   Status    State             Max-Power(W)   Power-consumption(W)   Priority   Class   Error
        ------------------------------------------------------------------------------------------------------------
        port1       Enabled   Fault:4           N/A            N/A                    N/A        N/A     Power Fault: Error Type 32 (Port is off: Powerbudget exceeded)
        port2       Enabled   Delivering Power  33.00          19.00                  Critical   4
        port3       Enabled   Fault:4           N/A            N/A                    N/A        N/A     Power Fault: Error Type 32 (Port is off: Powerbudget exceeded)
        port4       Enabled   Delivering Power  33.00          18.80                  Critical   4
        port5       Enabled   Delivering Power  33.00          18.80                  Critical   4
        port6       Enabled   Fault:4           N/A            N/A                    N/A        N/A     Power Fault: Error Type 32 (Port is off: Powerbudget exceeded)
        port7       Enabled   Fault:4           N/A            N/A                    N/A        N/A     Power Fault: Error Type 32 (Port is off: Powerbudget exceeded)
        port8       Enabled   Fault:4           N/A            N/A                    N/A        N/A     Power Fault: Error Type 32 (Port is off: Powerbudget exceeded)
        """
        output = collect_show_cmd(self.console,"get switch poe inline")
        dprint(output)
        poe_inline_dict = {}
        poe_inline_dict["ports"] = []
        start = False
        for line in output:
            if "Unit Power Budget" in line:
                k,v = line.split(":")
                poe_inline_dict[k.strip()] = v.strip()
            elif "Unit Poe Power Mode" in line:
                k,v = line.split(":")
                poe_inline_dict[k.strip()] = v.strip()
            elif "Interface   Status    State" in line:
                poe_items = line.split()
                start = True
            elif "port" in line and start:
                port_items = line.split()
                if "Delivering Power" in line:
                    port_items.remove("Power")
                poe_port_dict = {i:j for i,j in zip(poe_items,port_items)}
                poe_inline_dict["ports"].append(poe_port_dict)
        #print(poe_inline_dict)
        return poe_inline_dict

    def reboot_bios(self):
        #rebooot from BIOS mode
        print("Trying to get BIOS prompt by hitting Enter Key....")
        for i in range(5):
            self.console.write(('' + '\n').encode('ascii'))
            sleep(1)
        
        cmd = "R"
        switch_interactive_exec_bios(self.console,cmd,"Really reboot FortiSwitch? (Y/N): ")

    def exect_boot_bios(self):
        self.switch_reboot()
        cmd = convert_cmd_ascii_n("b")
        for i in range(100):
            self.console.write(cmd)
            sleep(0.2)
         

    def pdu_cycle(self):
        a = apc()
        Status = {}
        Status = a.set_reboot(self.pdu_ip, self.pdu_port)
        print(Status)

    def config_vlan_interface(self,*args,**kwargs):
        vlan = kwargs["vlan"]
        ip = kwargs["ip"]
        mask = kwargs['mask']

        vlan_id = re.match(r"vlan([0-9]+)",vlan).group(1)
        config = f"""
        config system interface
            edit {vlan}
            set ip {ip} {mask}
            set vlanid {vlan_id}
            set interface "internal"
            next
            end
            """
        config_cmds_lines(self.console,config,device=self)

    def clear_crash_log(self):
        config = f"""
        diagnose debug crashlog clear
        """
        config_cmds_lines(self.console,config)

    def get_crash_log(self):
        found = False
        output = self.show_command("diagnose debug crashlog get")
        for line in output:
            if "diagnose debug crashlog get" in line or self.hostname in line:
                continue
            matched = re.match(r"[0-9a-zA-Z]+",line)
            if matched:
                found = True
        if found:
            Info(f"!!!!!!!!!! Crash Log was found at {self.hostname} !!!!!!!!!!")
            output = self.show_command("diagnose debug crashlog read")

        return found


    def config_sw_after_factory_xml(self):
        config_mgmt_mode = f"""
        config system interface
            edit mgmt
            set mode static
            end
        config system interface
            edit "mgmt"
            set mode static
            end
        """
        config_cmds_lines(self.console,config_mgmt_mode)
        config = f"""
        conf system interface 
            edit mgmt
            set ip {self.mgmt_ip} {self.mgmt_netmask}
            set allowaccess ping https ssh snmp http telnet fgfm
            set type physical
            set role lan
            next
        end
        """
        config_cmds_lines(self.console,config)
        sleep(10)

        config = f"""
        config router static
            edit 1
                set gateway {self.mgmt_gateway}
                set device "mgmt"
            next
        end
        """
        config_cmds_lines(self.console,config)
        sleep(10)

    def switch_reboot(self):
        switch_exec_reboot(self.console,device=self.hostname)

        print(f"===== rebooting the switch {self.name}  =====")
        # dut = self.console
        # Info(f"================= Re-login device: {self.name} =============")
        # try:
        #     relogin_if_needed(dut)
        # except Exception as e:
        #     debug("something is wrong with rlogin_if_needed at bgp, try again")
        #     relogin_if_needed(dut)
        # image = find_dut_image(dut)
        # tprint(f"============================ {dut_name} software image = {image} ============")

    def switch_reboot_login(self):
        switch_exec_reboot(self.console,device=self.hostname)
        Info(f"Fortiswitch_XML/switch_reboot_login: After rebooting switch, sleep 300 seconds")
        sleep(300)
        self.sw_relogin()

    def ftg_sw_upgrade(self,*args,**kwargs):
         
        build = settings.build_548d
        tprint(f"================ Upgrading FSWs {self.serial_number} via Fortigate =============")
        samples = """
        S248EFTF18002594 # get system status
        
        S248EFTF18002594 # get system status
        Version: FortiSwitch-248E-FPOE v6.4.0,build0470,210205 (Interim)
        Serial-Number: S248EFTF18002594
        BIOS version: 04000004
        System Part-Number: P21940-02
        Burn in MAC: 70:4c:a5:d4:43:d2
        Hostname: S248EFTF18002594
        Distribution: International
        Branch point: 470
        System time: Wed Dec 31 17:21:44 1969

        image_name = FSW_248E_POE-v7-build0022-FORTINET.out
        """

        ftp_sample = """
        FG2K5E3917900021-Active (global) # execute switch-controller switch-software upload tftp FSW_548D_FPOE-v7-build0055-FORTINET.out 10.105.252.120

        Downloading file FSW_548D_FPOE-v7-build0055-FORTINET.out from tftp server 10.105.252.120...
        ############################
        Image checking ...
        Image MD5 calculating ...
        Image Saving S548DF-v7.0-build055-IMG.swtp ...
        Successful!

        File Syncing...

        FG2K5E3917900021-Active (global) # execute switch-controller switch-software list-available 

        ImageName                              ImageSize(B)   ImageInfo               Uploaded Time  
        S248EF-v7.0-build048-IMG.swtp          29377410       S248EF-v7.0-build048    Mon Aug 16 14:59:27 2021
        S548DF-v7.0-build048-IMG.swtp          30113665       S548DF-v7.0-build048    Mon Aug 16 14:56:46 2021
        S148FF-v7.0-build043-IMG.swtp          22917068       S148FF-v7.0-build043    Wed Jul 28 12:01:42 2021
        S548DF-v7.0-build055-IMG.swtp          30157077       S548DF-v7.0-build055    Thu Nov  4 20:07:33 2021

        FG2K5E3917900021-Active (global) # execute switch-controller switch-software upload tftp FSW_548D-v7-build0055-FORTINET.out 10.105.252.120

        Downloading file FSW_548D-v7-build0055-FORTINET.out from tftp server 10.105.252.120...
        ############################
        Image checking ...
        Image MD5 calculating ...
        Image Saving S548DN-v7.0-build055-IMG.swtp ...
        Successful!

        File Syncing...

        FG2K5E3917900021-Active (global) # execute switch-controller switch-software list-available 

        ImageName                              ImageSize(B)   ImageInfo               Uploaded Time  
        S248EF-v7.0-build048-IMG.swtp          29377410       S248EF-v7.0-build048    Mon Aug 16 14:59:27 2021
        S548DN-v7.0-build055-IMG.swtp          30151901       S548DN-v7.0-build055    Thu Nov  4 20:13:34 2021
        S548DF-v7.0-build048-IMG.swtp          30113665       S548DF-v7.0-build048    Mon Aug 16 14:56:46 2021
        S148FF-v7.0-build043-IMG.swtp          22917068       S148FF-v7.0-build043    Wed Jul 28 12:01:42 2021
        S548DF-v7.0-build055-IMG.swtp          30157077       S548DF-v7.0-build055    Thu Nov  4 20:07:33 2021
        """
        if "build" in kwargs:
            build = int(kwargs['build'])
            build = f"{build:04}"
        else:
            ErrorNotify("Software build number is missing. Exmaple: build=xxx.  Exiting program")
            exit(-1)
        if "version" in kwargs:
            version = kwargs['version']
        else:
            version = "v7"  # version should be provided when callign this API, but if lazy just assume v7

        if "tftp_server" in kwargs:
            tftp_server = kwargs['tftp_server']
        else:
            tftp_server = "10.105.252.120"
        dut = self.console
        dut_name = self.name

        fgt1 = self.ftg_console


        cmds = """
        end
        conf vdom
        edit root
        conf switch-controller global
        set https-image-push enable
        end
        end
        """
        config_cmds_lines(fgt1,cmds)

        image_name = f"{self.image_prefix}-{version}-build{build}-FORTINET.out"
        #upgrade_name = f"{self.image_prefix}-{version}-build{build}-IMG.swtp"

        dprint(f"image name = {image_name}")

        switch_exec_cmd(fgt1,'config global')

        cmd = f"execute switch-controller switch-software delete all"
        switch_interactive_exec(fgt1,cmd,"Do you want to continue? (y/n)")
        cmd = f"execute switch-controller switch-software upload tftp {image_name} {tftp_server}"

        output = ftg_collect_execute_cmd(fgt1,cmd,timeout=20)
        tprint(f"output of upload tftp command = {output}")

        # for line in output:
        #     if "Image Saving" in line:
        #         upgrade_name = line.split()[2]
        #switch_exec_cmd(fgt1, cmd)
        console_timer(20,msg=f"Sleep for 20s after uploading image from tftp server")

        cmd = "execute switch-controller switch-software list-available"
        #switch_show_cmd(fgt1,cmd)
        output = ftg_collect_execute_cmd(fgt1,cmd)
        tprint(f"output of  switch-software list-available = {output}")
        switch_exec_cmd(fgt1, "end")
        regex = r"S[0-9a-z.\-A-Z]+swtp"
        for line in output:
            if "IMG.swtp" in line:
                upgrade_name = line.split()[0]

        switch_exec_cmd(fgt1, "config vdom")
        switch_exec_cmd(fgt1, "edit root")
        ###########################
        cmd = f"execute switch-controller switch-software upgrade {self.serial_number} {upgrade_name}"
        switch_exec_cmd(fgt1, cmd,wait=60)
        console_timer(200,msg=f"upgrading {self.serial_number} to {upgrade_name}, wait for 200s to upgrade")
        cmd = "execute switch-controller get-upgrade-status"
        switch_show_cmd(fgt1,cmd)
        ##################################
        sample = f"""
        FG2K5E3917900021-Active (root) # execute switch-controller get-upgrade-status 
                Device    Running-version                                Status      Next-boot
        ===================================================================================================================
        VDOM : root
        S548DN4K17000133  S548DN-v7.0.0-build037,210610 (Interim)        (0/0/0)   N/A  (Idle) 
        S548DF4K16000653  S548DF-v7.0.0-build037,210610 (Interim)        (0/0/0)   N/A  (Idle) 
        S248EFTF18003119  S248EF-v7.0.0-build037,210610 (Interim)        (0/0/0)   N/A  (Idle) 
        S248EFTF18002509  S248EF-v7.0.0-build037,210610 (Interim)        (0/0/0)   N/A  (Idle) 
        S248EFTF18003105  S248EF-v7.0.0-build037,210610 (Interim)        (0/0/0)   N/A  (Idle) 
        S248EFTF18003278  S248EF-v7.0.0-build037,210610 (Interim)        (0/0/0)   N/A  (Idle) 
        S248EFTF18002594  S248EF-v7.0.0-build037,210610 (Interim)        (0/0/0)   N/A  (Idle) 
        S248EFTF18002618  S248EF-v7.0.0-build037,210610 (Interim)        (0/0/0)   N/A  (Idle) 
        """

        return True

    def ftg_sw_upgrade_no_wait(self,*args,**kwargs):
         
        build = settings.build_548d
        tprint(f"================ Upgrading FSWs {self.serial_number} via Fortigate =============")
        samples = """
        S248EFTF18002594 # get system status
        
        S248EFTF18002594 # get system status
        Version: FortiSwitch-248E-FPOE v6.4.0,build0470,210205 (Interim)
        Serial-Number: S248EFTF18002594
        BIOS version: 04000004
        System Part-Number: P21940-02
        Burn in MAC: 70:4c:a5:d4:43:d2
        Hostname: S248EFTF18002594
        Distribution: International
        Branch point: 470
        System time: Wed Dec 31 17:21:44 1969

        image_name = FSW_248E_POE-v7-build0022-FORTINET.out
        """

        ftp_sample = """
        FG2K5E3917900021-Active (global) # execute switch-controller switch-software upload tftp FSW_548D_FPOE-v7-build0055-FORTINET.out 10.105.252.120

        Downloading file FSW_548D_FPOE-v7-build0055-FORTINET.out from tftp server 10.105.252.120...
        ############################
        Image checking ...
        Image MD5 calculating ...
        Image Saving S548DF-v7.0-build055-IMG.swtp ...
        Successful!

        File Syncing...

        FG2K5E3917900021-Active (global) # execute switch-controller switch-software list-available 

        ImageName                              ImageSize(B)   ImageInfo               Uploaded Time  
        S248EF-v7.0-build048-IMG.swtp          29377410       S248EF-v7.0-build048    Mon Aug 16 14:59:27 2021
        S548DF-v7.0-build048-IMG.swtp          30113665       S548DF-v7.0-build048    Mon Aug 16 14:56:46 2021
        S148FF-v7.0-build043-IMG.swtp          22917068       S148FF-v7.0-build043    Wed Jul 28 12:01:42 2021
        S548DF-v7.0-build055-IMG.swtp          30157077       S548DF-v7.0-build055    Thu Nov  4 20:07:33 2021

        FG2K5E3917900021-Active (global) # execute switch-controller switch-software upload tftp FSW_548D-v7-build0055-FORTINET.out 10.105.252.120

        Downloading file FSW_548D-v7-build0055-FORTINET.out from tftp server 10.105.252.120...
        ############################
        Image checking ...
        Image MD5 calculating ...
        Image Saving S548DN-v7.0-build055-IMG.swtp ...
        Successful!

        File Syncing...

        FG2K5E3917900021-Active (global) # execute switch-controller switch-software list-available 

        ImageName                              ImageSize(B)   ImageInfo               Uploaded Time  
        S248EF-v7.0-build048-IMG.swtp          29377410       S248EF-v7.0-build048    Mon Aug 16 14:59:27 2021
        S548DN-v7.0-build055-IMG.swtp          30151901       S548DN-v7.0-build055    Thu Nov  4 20:13:34 2021
        S548DF-v7.0-build048-IMG.swtp          30113665       S548DF-v7.0-build048    Mon Aug 16 14:56:46 2021
        S148FF-v7.0-build043-IMG.swtp          22917068       S148FF-v7.0-build043    Wed Jul 28 12:01:42 2021
        S548DF-v7.0-build055-IMG.swtp          30157077       S548DF-v7.0-build055    Thu Nov  4 20:07:33 2021
        """
        if "build" in kwargs:
            build = int(kwargs['build'])
            build = f"{build:04}"
        else:
            ErrorNotify("Software build number is missing. Exmaple: build=xxx.  Exiting program")
            exit(-1)
        if "version" in kwargs:
            version = kwargs['version']
        else:
            version = "v7"  # version should be provided when callign this API, but if lazy just assume v7

        if "tftp_server" in kwargs:
            tftp_server = kwargs['tftp_server']
        else:
            tftp_server = "10.105.252.120"
        dut = self.console
        dut_name = self.name

        fgt1 = self.ftg_console

        cmds = """
        end
        conf vdom
        edit root
        conf switch-controller global
        set https-image-push enable
        end
        end
        """
        config_cmds_lines(fgt1,cmds)

        image_name = f"{self.image_prefix}-{version}-build{build}-FORTINET.out"
        #upgrade_name = f"{self.image_prefix}-{version}-build{build}-IMG.swtp"

        dprint(f"image name = {image_name}")

        switch_exec_cmd(fgt1,'config global')

        cmd = f"execute switch-controller switch-software delete all"
        switch_interactive_exec(fgt1,cmd,"Do you want to continue? (y/n)")
        cmd = f"execute switch-controller switch-software upload tftp {image_name} {tftp_server}"

        output = ftg_collect_execute_cmd(fgt1,cmd,timeout=20)
        tprint(f"output of upload tftp command = {output}")

        # for line in output:
        #     if "Image Saving" in line:
        #         upgrade_name = line.split()[2]
        #switch_exec_cmd(fgt1, cmd)
        console_timer(20,msg=f"Sleep for 20s after uploading image from tftp server")

        cmd = "execute switch-controller switch-software list-available"
        #switch_show_cmd(fgt1,cmd)
        output = ftg_collect_execute_cmd(fgt1,cmd)
        tprint(f"output of  switch-software list-available = {output}")
        switch_exec_cmd(fgt1, "end")
        regex = r"S[0-9a-z.\-A-Z]+swtp"
        for line in output:
            if "IMG.swtp" in line:
                upgrade_name = line.split()[0]

        switch_exec_cmd(fgt1, "config vdom")
        switch_exec_cmd(fgt1, "edit root")
        ###########################
        cmd = f"execute switch-controller switch-software upgrade {self.serial_number} {upgrade_name}"
        switch_exec_cmd(fgt1,cmd)
        switch_exec_cmd(fgt1, "end")
        return True

    def fsw_upgrade_v2(self,*args,**kwargs):
        samples = """
        S248EFTF18002594 # get system status
        
        S248EFTF18002594 # get system status
        Version: FortiSwitch-248E-FPOE v6.4.0,build0470,210205 (Interim)
        Serial-Number: S248EFTF18002594
        BIOS version: 04000004
        System Part-Number: P21940-02
        Burn in MAC: 70:4c:a5:d4:43:d2
        Hostname: S248EFTF18002594
        Distribution: International
        Branch point: 470
        System time: Wed Dec 31 17:21:44 1969

        image_name = FSW_248E_POE-v7-build0022-FORTINET.out
        """

        if "build" in kwargs:
            build = int(kwargs['build'])
            build = f"{build:04}"
        else:
            ErrorNotify("Software build number is missing. Exmaple: build=xxx.  Exiting program")
            exit(-1)
        if "version" in kwargs:
            version = kwargs['version']
        else:
            version = "v6"
        dut = self.console
        dut_name = self.name

        config = f"""
        config system admin
            edit "admin"
            set accprofile "super_admin"
            set password ENC AK1uHvbOfsDLnA6ya8BxpLwXCNcKNZ9+7K7YC1pLpb4Qvs=
        next
        end
        """
        config_cmds_lines(self.console,config)

        image_name = f"{self.image_prefix}-{version}-build{build}-FORTINET.out"

        dprint(f"image name = {image_name}")
        cmd = f"execute restore image tftp {image_name} {self.tftp_ip}"
        tprint(f"upgrade command = {cmd}")
        switch_interactive_exec(dut,cmd,"Do you want to continue? (y/n)")
        #console_timer(60,msg="wait for 60s to download image from tftp server")
        #switch_wait_enter_yes(dut,"Do you want to continue? (y/n)")
        prompt = "Do you want to continue? (y/n)"
        output = switch_read_console_output(dut,timeout = 100)
        dprint(output)
        result = False
        for line in output: 
            if "Command fail" in line:
                Info(f"upgrade with image {image_name} failed for {dut_name}: {line}")
                result = False

            elif "Check image OK" in line:
                Info(f"At {dut_name} image {image_name} is downloaded and checked OK,upgrade should be fine: {line}")
                result = True

            elif "Writing the disk" in line:
                Info(f"At {dut_name} image {image_name} is being written into disk, upgrade is Good!: {line}")
                result = True

            elif "Do you want to continue" in line:
                dprint(f"Being prompted to answer yes/no 2nd time.  Prompt = {prompt}")
                switch_enter_yes(dut)
                result = True
            else:
                result = True
        return result

    def factory_and_restore_config(self):
        self.switch_factory_reset()
        console_timer(300,msg="class fortiswitch_xml | factory_reset_restore_config: factory reset wating 300 sec....")
        self.sw_relogin()
        self.config_network_standalone()

    def config_network_standalone(self):
        config = f"""
        conf system interface 
            edit mgmt
            set mode static
            end
        """
        config_cmds_lines_fast(self.console,config)
        sleep(2)
        config = f"""
        conf system interface 
            edit mgmt
            set mode static
            end
        """
        config_cmds_lines_fast(self.console,config)

        sleep(5)
        config = f"""
        conf system interface 
            edit mgmt
            set ip {self.mgmt_ip} {self.mgmt_netmask}
            set allowaccess ping telnet https http ssh
        end
        """
        config_cmds_lines_fast(self.console,config)
        sleep(5)

        config = f"""
        config router static
            edit 1
                set gateway {self.mgmt_gateway}
                set device "mgmt"
            next
        end
        """
        config_cmds_lines_fast(self.console,config)
        sleep(5)
        if self.split_port_exist:
            self.config_split_port()

    def sw_relogin(self):
        Info(f"================= {self.hostname}: Re-Login console after rebooting or power_cycle =================")
        self.console = telnet_switch(self.console_ip,self.console_line,password=self.password,relogin=True,console=self.console)
        self.dut = self.console # For compatibility with old Fortiswitch codes

    def switch_system_status(self,*args,**kwargs):
        sample = """
        S548DN4K17000133 # get system status
        Version: FortiSwitch-548D v6.4.4,build0454,201106 (GA)
        Serial-Number: S548DN4K17000133
        BIOS version: 04000013
        System Part-Number: P18057-06
        Burn in MAC: 70:4c:a5:79:22:5a
        Hostname: S548DN4K17000133
        Distribution: International
        Branch point: 454
        System time: Tue Oct  2 06:03:37 2001
        path=system, objname=status, tablename=(null), size=0
        """
        print(f"========================== {self.hostname}: Get System Status =======================")
        if self.console != None:
            output = collect_show_cmd(self.console,"get system status")
        else:
            Info(f"!!!!!!! the device {self.hostname} has no console connection, please check your console connection")
            return

        for line in output:
            if "Version:" in line:
                k,v = line.split(":")
                self.version = v.split()[0].strip()
                self.image_prefix = re.sub("FortiSwitch","FSW",self.version)
                self.image_prefix = self.image_prefix.replace("-","_")
                print(f"Platform version = {self.version}")
                continue
            if "Hostname" in line:
                self.discovered_hostname = line.split(":")[1].strip()
                print(f"Discovered hostname = {self.discovered_hostname}")
                continue
            if "Serial-Number" in line:
                self.serial_number = line.split(":")[1].strip()
                print(f"Serial Number = {self.serial_number}")

        for device in self.tb.devices:
            #print(device.hostname)
            if self.serial_number == device.hostname:
                device.serial_number = self.serial_number
                device.discovered_hostname = self.discovered_hostname
                device.version = self.version
                print(f"----------------------------- Updated topo_db device infor  ------------------------")
                device.print_info()

    def sw_network_discovery(self,*args,**kwargs):
        self.discover_fortiswitch_lldp()
        print(f"!!!!!!!!!!================= Important: Network Discovery Result ================= !!!!!!!")
        print(f"switch hostname = {self.hostname}")
        print(f"switch role = {self.role}")
        print(f"Fortilink ports = {self.fortigate_links}")
        print(f"ICL ports = {self.icl_links}")
        print(f"Uplinke ports = {self.up_links}")
        print(f"Uplinke ports pod = {self.up_links_pod}")
        print(f"Downlink ports = {self.down_links}")
        print(f"Downlink ports pod = {self.down_links_pod}")


    def config_lldp_profile_auto_isl(self):

        ports = self.icl_links + self.up_links + self.down_links
        for port in ports:
            config = f"""
            conf switch physical-port
                edit {port}
                set lldp-profile default-auto-isl
                end
            """
            config_cmds_lines(self.console,config)

    def discover_fortiswitch_lldp(self):
        if self.is_fortinet() == False:
            return 
        Info(f"Discovering LLDP neighbors and updating LLDP database at {self.name}......")
        lldp_obj_list = []
        lldp_dict_list = []

        self.icl_links = []
        self.up_links = []
        self.down_links = []
        self.fortigate_links = []
        self.lldp_neighbors_list

        print(f"========================== {self.serial_number}: Discovering LLDP Neighbors =======================")
        output = collect_show_cmd(self.console,"get switch lldp neighbors-summary")
        #print(output)
        for line in output:
            if "Portname" in line and  "Status" in line and "Device-name" in line:
                items = line.split()
                continue
            if " Up " in line:
                lldp_dict = {k:v for k, v in zip(items,line.split())}
                #printr(lldp_dict)
                if lldp_dict["Device-name"] == "-" or lldp_dict["Capability"] == "-":
                    continue
                else:
                    lldp = lldp_class()
                    lldp.local_port = lldp_dict["Portname"]
                    lldp.status = lldp_dict["Status"]
                    lldp.ttl = lldp_dict["TTL"]
                    lldp.remote_system = lldp_dict["Device-name"]
                    lldp.capability = lldp_dict["Capability"]
                    lldp.remote_port = lldp_dict["Port-ID"]
                    lldp_obj_list.append(lldp)
                    lldp_dict_list.append(lldp_dict)
                    dprint("############################### Debug ########################")
                    dprint(f"Debug: Looking for this neighbor: {lldp.remote_system}")
                    for device in self.tb.devices:
                        if device.serial_number == None:
                            continue
                        if (lldp.remote_system == device.hostname or lldp.remote_system == device.discovered_hostname \
                            or device.serial_number in lldp.remote_system) \
                            and self.serial_number != device.serial_number:
                            dprint(f"===== Debug:device hostname: {device.hostname}")
                            dprint(f"===== Debug: device discovered hostname: {device.discovered_hostname}")
                            lldp.remote_system_role = device.role
                            if "FGT" in device.role and 'tier' in self.role:
                                self.fortigate_links.append(lldp.local_port)
                                self.fortigate_links = list(set(self.fortigate_links))
                            elif 'tier' in self.role and 'tier' in device.role:
                                neighbor_tier = int(re.match(r'tier([0-9]+)-([0-9]+)',device.role).group(1)) 
                                neighbor_pod = int(re.match(r'tier([0-9]+)-([0-9]+)',device.role).group(2)) 
                                self_tier = int(re.match(r'tier([0-9]+)-([0-9]+)',self.role).group(1))
                                self_pod = int(re.match(r'tier([0-9]+)-([0-9]+)',self.role).group(2))  
                                if neighbor_tier < self_tier:
                                    self.up_links.append(lldp.local_port)
                                    if neighbor_pod not in self.up_links_pod:
                                        self.up_links_pod.setdefault(neighbor_pod,[]).append(lldp.local_port)
                                    else:
                                        self.up_links_pod[neighbor_pod].append(lldp.local_port)
                                elif neighbor_tier > self_tier:
                                    self.down_links.append(lldp.local_port)
                                    if neighbor_pod not in self.down_links_pod:
                                        self.down_links_pod.setdefault(neighbor_pod,[]).append(lldp.local_port)
                                    else:
                                        self.down_links_pod[neighbor_pod].append(lldp.local_port)
                                else:
                                    self.icl_links.append(lldp.local_port)

                    lldp.print_lldp()
                    self.lldp_neighbors_list.append(lldp)
        for item in self.up_links_pod:
            self.up_links_pod[item] = list(set(self.up_links_pod[item]))

        for item in self.down_links_pod:
            self.down_links_pod[item] = list(set(self.down_links_pod[item]))

        self.lldp_dict_list = lldp_dict_list
        self.lldp_obj_list = lldp_obj_list
        dprint(self.lldp_dict_list)


    def shut_port(self,port):
        switch_shut_port(self.console,port)

    def unshut_port(self,port):
        switch_unshut_port(self.console,port)

    def switch_factory_reset(self):
        tprint(f":::::::::: Factory resetting {self.hostname} :::::::::::")
        switch_interactive_exec(self.console,"execute factoryreset","Do you want to continue? (y/n)") 

    def login_factory_reset(self,*args,**kwargs):
        tn = self.console
        hostname = self.hostname
        if 'password' in kwargs:
            password = kwargs['password']
        else:
            password = "Fortinet123!"
         
        tn.write(('' + '\n').encode('ascii'))
        tn.write(('' + '\n').encode('ascii'))
        time.sleep(0.2)

        tn.read_until(("login: ").encode('ascii'),timeout=5)

        tn.write(('admin' + '\n').encode('ascii'))

        tn.read_until(("Password: ").encode('ascii'),timeout=5)

        ###################### Has to be 3 enters: Dont change ################
        tn.write(('' + '\n').encode('ascii'))
        tn.write(('' + '\n').encode('ascii'))
        tn.write(('' + '\n').encode('ascii'))
        ############################ Dont change ##############################

        prompt = switch_find_login_prompt_new(tn)
        p = prompt[0]
        debug(prompt)
        if p == "change":
            Info(f"Login {hostname} after factory reset , changing password..... ") #This needs to rewrite to take care factory reset situation
            ############################################# Dont change these lines ##################################
            tn.write(('' + '\n').encode('ascii'))
            tn.write(('' + '\n').encode('ascii'))
            tn.write(('' + '\n').encode('ascii'))
            tn.write(('' + '\n').encode('ascii'))
            tn.write(('' + '\n').encode('ascii'))
            tn.write(('' + '\n').encode('ascii'))
            tn.write(('' + '\n').encode('ascii'))
            tn.write(('' + '\n').encode('ascii'))
            tn.write(('' + '\n').encode('ascii')) 
            sleep(3)       # For some console, it took long time for promopt to show up.  Keep this wait 3 sec
            ############################################# Dont change these lines ###################################
            tn.read_until(("login: ").encode('ascii'),timeout=5)
            tn.write(('admin' + '\n').encode('ascii'))           # this would not work for factory reset scenario
            tn.write(('' + '\n').encode('ascii'))
            tn.read_until(("Password: ").encode('ascii'),timeout=5) #read_util() can not work with prompt with prompt with space, such as New Password
            tn.write((password + '\n').encode('ascii'))   #this is for factory reset scenario
            tn.read_until(("Password: ").encode('ascii'),timeout=10)
            tn.write((password + '\n').encode('ascii'))
            tn.write(('' + '\n').encode('ascii'))
            tn.write(('' + '\n').encode('ascii'))
            tn.read_until(("# ").encode('ascii'),timeout=10)
            # tn.read_until(("login: ").encode('ascii'),timeout=5)
            # tn.write(('admin' + '\n').encode('ascii'))           # this would not work for factory reset scenario
            # sleep(0.6)
            # tn.write(('' + '\n').encode('ascii')) #This line is needed. Don't deleted!!!!!! After enter is hit, user can enter password
            # tn.read_until(("Password: ").encode('ascii'),timeout=5) #read_util() can not work with prompt with prompt with space, such as New Password
            # tn.write(('fortinet123' + '\n').encode('ascii'))   #this is for factory reset scenario
            # #sleep(0.5) Must not have sleep in between write and read_until
            # tn.read_until(("Password: ").encode('ascii'),timeout=10)
            # tn.write(('fortinet123' + '\n').encode('ascii'))
            # sleep(0.5)
            # tn.write(('' + '\n').encode('ascii'))
            # tn.write(('' + '\n').encode('ascii'))
            # tn.read_until(("# ").encode('ascii'),timeout=10)

            switch_configure_cmd(tn,'config system global')
            switch_configure_cmd(tn,'set admintimeout 480')
            switch_configure_cmd(tn,'end')
            tprint("get_switch_telnet_connection_new: Login sucessful!\n")
            try:
                print(f"=========== Software Image = {find_dut_build(tn)[0]} ==================")
                print(f"=========== Software Build = {find_dut_build(tn)[1]} ==================")
            except Exception as e:
                pass
        else:
            ErrorNotify(f"Not able to login {hostname} after factory reset the device")
            exit()

    def config_auto_isl_port_group(self):
        Info("Start configuring MCLAG auto isl port group")
        Info(f"switch role = {self.role}")
        Info(f"switch down_links = {self.down_links}")
        Info(f"switch down_links_pod = {self.down_links_pod}")
        #For 2 tiers MC-LAG, you need the following two lines:
        # if len(self.down_links) == 0 or "tier1" not in self.role:
        #     return
        #For 3 tiers MC-LAG, you need the following two lines:
        # if len(self.down_links) == 0 or "tier1" not in self.role or "tier2" not in self.role:
        #     return

        if len(self.down_links) == 0:
            return

        for pod in self.down_links_pod:
            ports = " ".join(self.down_links_pod[pod])
            config = f"""
            config switch auto-isl-port-group
                edit Tier{self.tier}-Trunk-{pod}
                    set members {ports}
                end
            """
            config_cmds_lines(self.console,config)

    def print_show_interesting(self,cmd,*args,**kwargs):
        tn = self.console
        if 't' in kwargs:
            timeout = kwargs['t']
        else:
            timeout = 5
        #relogin_if_needed(tn)
        if "logger" in kwargs:
            mylogger = kwargs["logger"]
        else:
            mylogger = None
        handle_prompt_before_commands(tn)
        original_cmd = cmd
        cmd_bytes = convert_cmd_ascii_n(cmd)
        tn.write(('' + '\n').encode('ascii')) # uncomment this line if doesn't work
        tn.write(('' + '\n').encode('ascii')) # uncomment this line if doesn't work
        tn.write(cmd_bytes)
        tn.write(('' + '\n').encode('ascii')) # uncomment this line if doesn't work
        tn.write(('' + '\n').encode('ascii')) # uncomment this line if doesn't work
        sleep(timeout)
        output = tn.read_very_eager()
        out_list = output.split(b'\r\n')
        encoding = 'utf-8'
        out_str_list = []
        for o in out_list:
            o_str = o.decode(encoding).strip(' \r')
            out_str_list.append(o_str)
        for out_str in out_str_list:
            for key in args:
                if key in out_str:
                    tprint(f"{str(out_str)}\n")
                    if mylogger != None:
                        mylogger.write(f"{str(out_str)}\n")
                    return True
        return False
        
    def print_show_command(self,cmd,*args,**kwargs):
        if "logger" in kwargs:
            print_show_cmd(self.console,cmd,logger=kwargs["logger"])
        else:
            print_show_cmd(self.console,cmd)

    #config_lines are defined with """ """
    def config_cmds(self,config_lines):
        config_cmds_lines(self.console,config_lines)

    def config_cmds_fast(self,config_lines):
        config_cmds_lines_fast(self.console,config_lines)

    def config_cmds_json(self,json_cmds):
        cmds ="""
         {
        "config switch acl ingress": {
            f"edit {index}:{
                "group": group_id
                "ingress_interface":f"{port_name}"

        }
        }
        """
        pass

class Managed_Switch():
    def __init__(self,*args,**kwargs):
        self.ftg_console = args[0]
        self.switch_id = None
        self.major_version = None
        self.minor_version = None
        self.authorized = None
        self.up = None
        self.flag = None
        self.address = None
        self.join_time = None
        self.switch_obj = None

    def print_managed_sw_info(self):
        print_dash_line()
        print(f"Switch ID = {self.switch_id}")
        print(f"Software Version = {self.major_version}, {self.minor_version}")
        print(f"Authorized = {self.authorized}")
        print(f"Switch is Up = {self.up}")
        print(f"Switch address = {self.address}")


class FortiGate_XML(FortiSwitch):
    def __init__(self,*args,**kwargs):
        device_xml = args[0]
        if "password" in kwargs:
            self.pwd = kwargs['password']
        else:
            self.pwd = device_xml.password
        self.ixia_ports = device_xml.ixia_ports
        self.tb=kwargs['topo_db']
        self.physical_ports = []
        self.port_mac_pair = {}
        self.mac_port_pair = {}
        self.lldp_neighbors_list = []
        self.fortilink_ports = []
        self.fortilink_ports_pod = {}
        self.fortilink_interfaces = []
        self.fortilink_just_configued = []
        self.fgt_ha_ports = []
        self.version = None
        self.image_prefix = None
        self.discovered_hostname = None
        self.serial_number = None
        self.platform = "fortigate"
        self.name = device_xml.name
        self.hostname = device_xml.hostname
        self.console_ip = device_xml.console_ip
        self.console_line = device_xml.console_line
        self.username = device_xml.username
        self.password = device_xml.password
        self.mgmt_ip = device_xml.mgmt_ip
        self.mgmt_netmask = device_xml.mgmt_netmask
        self.mgmt_gateway = device_xml.mgmt_gateway
        self.license = device_xml.license
        self.role = re.match(r'([A-Za-z]+)_([A-Za-z]+)-([1-9])',device_xml.role).group(1)
        self.mode = re.match(r'([A-Z]+)_([A-Za-z]+)-([1-9])',device_xml.role).group(2)
        self.cluter = re.match(r'([A-Z]+)_([A-Za-z]+)-([1-9])',device_xml.role).group(3)
        self.type = device_xml.type
        self.active = device_xml.active
        self.fortilink_ports_db = device_xml.fortilink_ports
        self.ha_ports_db = device_xml.ha_ports
        self.ixia_ports_db = device_xml.ixia_ports
        self.managed_switches_list = []
        self.switch_custom_cmds_list = []
        self.console = telnet_switch(self.console_ip,self.console_line,password=self.pwd,platform="fortigate")
        self.local_discovery()
        self.change_hostname()

    def change_hostname(self):
        if self.mode == "Active":
            name = f"{self.hostname}-Active"
        else:
            name = f"{self.hostname}-Passive"
        config = f"""
        config global
        config system global
        set hostname {name}
        end
        end
        """
        config_cmds_lines(self.console,config)


    def ha_sync(self,*args,**kwargs):
        action = kwargs['action']
        Info("synchronize configuration at both Firewalls")
        config = f"""
        conf global
        execute ha synchronize {action}
        """
        config_cmds_lines(self.console,config)

    def ha_failover(self,*args,**kwargs):
        config = f"""
        config global
        """
        config_cmds_lines(self.console,config)
        switch_interactive_exec(self.console,"execute ha failover set","Do you want to continue? (y/n)")

    def fgt_upgrade_v2(self,*args,**kwargs):
        samples = """
        S248EFTF18002594 # get system status
        
        S248EFTF18002594 # get system status
        Version: FortiSwitch-248E-FPOE v6.4.0,build0470,210205 (Interim)
        Serial-Number: S248EFTF18002594
        BIOS version: 04000004
        System Part-Number: P21940-02
        Burn in MAC: 70:4c:a5:d4:43:d2
        Hostname: S248EFTF18002594
        Distribution: International
        Branch point: 470
        System time: Wed Dec 31 17:21:44 1969

        image_name = FSW_248E_POE-v7-build0022-FORTINET.out
        """

        if "build" in kwargs:
            build = int(kwargs['build'])
            build = f"{build:04}"
        else:
            ErrorNotify("Software build number is missing. Exmaple: build=xxx.  Exiting program")
            exit(-1)
        if "version" in kwargs:
            version = kwargs['version']
        else:
            version = "v6"
        dut = self.console
        dut_name = self.name

        # if version == "v7":
        #     version = "v7.0.0"
        image_name = f"{self.image_prefix}-{version}-build{build}-FORTINET.out"

        dprint(f"image name = {image_name}")
        cmd = f"execute restore image tftp {image_name} 10.105.19.19"
        tprint(f"upgrade command = {cmd}")

        tprint(f":::::::::: Image Upgrade {self.hostname} :::::::::::")
        config = """
        config global
        """
        config_cmds_lines(self.console,config)
        switch_interactive_exec(dut,cmd,"Do you want to continue? (y/n)")
        #console_timer(60,msg="wait for 60s to download image from tftp server")
        #switch_wait_enter_yes(dut,"Do you want to continue? (y/n)")
        sleep(30)
        switch_enter_yes(dut)
        output = switch_read_console_output(dut,timeout = 30)
        dprint(output)
        result = False
        for line in output: 
            if "Command fail" in line:
                Info(f"upgrade with image {image_name} failed for {dut_name}: {line}")
                result = False

            elif "Check image OK" in line:
                Info(f"At {dut_name} image {image_name} is downloaded and checked OK,upgrade should be fine: {line}")
                result = True

            elif "Writing the disk" in line:
                Info(f"At {dut_name} image {image_name} is being written into disk, upgrade is Good!: {line}")
                result = True

            elif "Do you want to continue" in line:
                dprint(f"Being prompted to answer yes/no 2nd time.  Prompt = {prompt}")
                switch_enter_yes(dut)
                result = True
            elif "Error" in line or "Invalid" in line or "Can not get image" in line:
                Info(f"upgrade with image {image_name} failed for {dut_name}: {line}")
                result = False
            else:
                result = True
        return result



    def config_default_policy(self,*args,**kwargs):
        config = """
        conf vdom
        edit root
        config firewall policy
        edit 1
            set name allowed-all
            set srcintf any
            set dstintf any
            set srcaddr all
            set dstaddr all
            set action accept
            set schedule always
            set service ALL
            set inspection-mode proxy
            set logtraffic disable
            set nat enable
        next
        end
        end
        """
        config_cmds_lines(self.console,config)

    def fgt_relogin(self):
        Info(f"================= {self.discovered_hostname}: Re-Login console =================")
        self.console = telnet_switch(self.console_ip,self.console_line,password=self.pwd,platform="fortigate",relogin=True,console=self.console)

    def fgt_factory_reset(self):
        tprint(f":::::::::: Factory resetting {self.hostname} :::::::::::")
        config = """
        config global
        """
        config_cmds_lines(self.console,config)
        switch_interactive_exec(self.console,"execute factoryreset","Do you want to continue? (y/n)") 

    def fgt_reboot(self):
        tprint(f":::::::::: Rebooting Fortigate {self.hostname} :::::::::::")
        config = """
        config global
        """
        config_cmds_lines(self.console,config)
        switch_interactive_exec(self.console,"execute reboot","Do you want to continue? (y/n)") 

    def fortigate_system_status(self,*args,**kwargs):
        sample = """
        FortiGate-2500E # get system status
        Version: FortiGate-2500E v6.4.4,build1802,201208 (Interim)
        Virus-DB: 1.00123(2015-12-11 13:18)
        Extended DB: 1.00000(2018-04-09 18:07)
        Extreme DB: 1.00000(2018-04-09 18:07)
        IPS-DB: 6.00741(2015-12-01 02:30)
        IPS-ETDB: 6.00741(2015-12-01 02:30)
        APP-DB: 6.00741(2015-12-01 02:30)
        INDUSTRIAL-DB: 6.00741(2015-12-01 02:30)
        Serial-Number: FG2K5E3917900021
        IPS Malicious URL Database: 1.00001(2015-01-01 01:01)
        BIOS version: 05000004
        System Part-Number: P18723-05
        Log hard disk: Available
        Hostname: FortiGate-2500E
        Private Encryption: Disable
        Operation Mode: NAT
        Current virtual domain: root
        Max number of virtual domains: 500
        Virtual domains status: 2 in NAT mode, 0 in TP mode
        Virtual domain configuration: multiple
        FIPS-CC mode: disable
        Current HA mode: a-p, primary
        Cluster uptime: 174 days, 5 hours, 55 minutes, 20 seconds
        Branch point: 1802
        Release Version Information: Interim
        FortiOS x86-64: Yes
        System time: Thu May  6 22:59:50 2021
        Cluster state change time: 2021-04-27 14:16:02
        """

        print(f"========================== {self.hostname}: Get System Status =======================")
        cmds = """
        get system status
        """
        output = self.fgt_show_commands(cmds,timeout=2) #timeout has to be > 1
        #print(output)

        for line in output:
            if "Version:" in line:
                k,v = line.split(":")
                self.version = v.split()[0].strip()
                self.image_prefix = re.sub("FortiGate","FGT",self.version)
                self.image_prefix = self.image_prefix.replace("-","_")
                print(f"Platform version = {self.version}")
                continue
            if "Hostname" in line:
                self.discovered_hostname = line.split(":")[1].strip()
                print(f"Discovered hostname = {self.discovered_hostname}")
                continue
            if "Serial-Number" in line:
                self.serial_number = line.split(":")[1].strip()
                print(f"Serial Number = {self.serial_number}")

        for device in self.tb.devices:
            #print(device.hostname)
            if self.serial_number == device.hostname:
                device.serial_number = self.serial_number
                device.discovered_hostname = self.discovered_hostname
                device.version = self.version
                print(f"----------------------------- Updated topo_db device infor  ------------------------")
                device.print_info()

    def collect_physical_ports(self,*args,**kwargs):
        sample = """
        config global
        get system interface physical
        ==[port31]
        mode: static
        ip: 0.0.0.0 0.0.0.0
        ipv6: ::/0
        status: down
        speed: n/a
        ==[port32]
        mode: static
        ip: 0.0.0.0 0.0.0.0
        ipv6: ::/0
        status: down
        speed: n/a
        """
        cmds = """
        config global
        get system interface physical
        """
        print(f"========================== {self.serial_number}: discovering physical ports =======================")
        ports = self.fgt_show_commands(cmds,timeout=10)

        self.physical_ports = []
        port_regex = r"==\[(port[0-9]+)\]"
        for line in ports:
            #print(line)
            if "==" in line:
                #print(line)
                matched = re.search(port_regex,line)
                if matched:
                    p = matched.group(1)
                    #print(p)
                    self.physical_ports.append(p)

        print(f"Physical ports on {self.serial_number}: {self.physical_ports}")   

    def change_fortilink_ports(self,*args,**kwargs):
        state = kwargs['state']
        for port in self.fortilink_ports:
            config = f"""
            conf vdom
                edit root
                config system interface
                edit {port}
                    set status {state}
                    next
                    end
                end
            """
            config_cmds_lines(self.console,config) 

    def config_switch_custom_cmds(self,*args,**kwargs):
        self.config_custom_console_output()
        self.config_custom_timeout()

    def config_custom_console_output(self,*args,**kwargs):
        if "vdom" in kwargs:
            vdom_name = kwargs['vdom']
        else:
            vdom_name = "root"
        name = "console_output"
        config = f"""
        config vdom
        edit {vdom_name}
        config switch-controller custom-command
            edit {name}
                set command "config system console %0a set output standard %0a end %0a"
            next
            end
            end
        end
        """
        config_cmds_lines(self.console,config)
        self.switch_custom_cmds_list.append(name)
        return name

    def config_custom_timeout(self,*args,**kwargs):
        if "vdom" in kwargs:
            vdom_name = kwargs['vdom']
        else:
            vdom_name = "root"
        name = "timeout"
        config = f"""
        config vdom
        edit {vdom_name}
        config switch-controller custom-command
            edit {name}
                set command "config system global %0a set admintimeout 480 %0a end %0a"
            next
            end
            end
        end
        """
        config_cmds_lines(self.console,config)
        self.switch_custom_cmds_list.append(name)
        return name

    def unconfig_fortilink(self,*args,**kwargs):

        for flk in self.fortilink_just_configued:
            config = f"""
                config vdom
                edit root
                config system interface
                    delete {flk}
                end
                end
                """
            config_cmds_lines(self.console,config)
            sleep(2)
            show_cmds = f"""
            config vdom
            edit root
                config system interface
                    edit {flk}
                        show 
            """
            self.fgt_show_commands(show_cmds)

    def config_fortilink(self,*args,**kwargs):
        sample = """
        config vdom
        edit root
        config system interface
            edit "fortilink1"
            set vdom "root"
            set fortilink enable
            set ip 192.168.255.1 255.255.255.0
            set allowaccess ping fabric
            set type aggregate
            set member "port15" "port16"
            set device-identification enable
            set lldp-reception enable
            set lldp-transmission enable
            set snmp-index 50
            set auto-auth-extension-device enable
            set fortilink-split-interface disable
            set switch-controller-nac "fortilink1"
            set swc-first-create 127
            set lacp-mode active
            next
        end
        """
        if "domain" in kwargs:
            domain = kwargs['domain']
        else:
            domain = "root"

        if "name" in kwargs:
            fortilink_name = kwargs['name']
        else:
            fortilink_name = "Myfortilink"

        if "ip_addr" in kwargs:
            ip_addr = kwargs['ip_addr']
        else:
            ip_addr = f"192.168.1.1 255.255.255.0"

        fortilink_ports = " ".join(self.fortilink_ports)

        config = f"""
            config vdom
            edit root
            config system interface
                edit {fortilink_name}
                set vdom {domain}
                set fortilink enable
                set allowaccess ping fabric
                set type aggregate
                set member {fortilink_ports}
                set device-identification enable
                set lldp-reception enable
                set lldp-transmission enable
                set auto-auth-extension-device enable
                set fortilink-split-interface disable
                set switch-controller-nac {fortilink_name}
                set lacp-mode active
                next
            end
            end
            """
        config_cmds_lines(self.console,config)
        self.fortilink_interfaces.append(fortilink_name)
        self.fortilink_just_configued.append(fortilink_name)
        sleep(2)
        show_cmds = f"""
        config vdom
            edit root
                config system interface
                    edit {fortilink_name}
                        show 
        """
        self.fgt_show_commands(show_cmds)

    def config_fortilink_switch(self,*args,**kwargs):
        sample = """
        config vdom
        edit root
        config system interface
            edit "fortilink1"
            set vdom "root"
            set fortilink enable
            set ip 192.168.255.1 255.255.255.0
            set allowaccess ping fabric
            set type aggregate
            set member "port15" "port16"
            set device-identification enable
            set lldp-reception enable
            set lldp-transmission enable
            set snmp-index 50
            set auto-auth-extension-device enable
            set fortilink-split-interface disable
            set switch-controller-nac "fortilink1"
            set swc-first-create 127
            set lacp-mode active
            next
        end
        """
        if "domain" in kwargs:
            domain = kwargs['domain']
        else:
            domain = "root"

        if "name" in kwargs:
            fortilink_name = kwargs['name']
        else:
            fortilink_name = "Myfortilink"

        if "ip_addr" in kwargs:
            ip_addr = kwargs['ip_addr']
        else:
            ip_addr = f"192.168.1.1 255.255.255.0"

        fortilink_ports = " ".join(self.fortilink_ports)

        config = f"""
        config system switch-interface
            edit {fortilink_name}
            set vdom "root"
            set member {fortilink_ports}
            set type switch
            next
        end
        """
        config_cmds_lines(self.console,config)


        config = f"""
            config vdom
            edit root
            config system interface
                edit {fortilink_name}
                set vdom {domain}
                set fortilink enable
                set allowaccess ping fabric
                set type switch
                set device-identification enable
                set lldp-reception enable
                set lldp-transmission enable
                set auto-auth-extension-device enable
                set switch-controller-nac {fortilink_name}
                next
            end
            end
            """
        config_cmds_lines(self.console,config)
        self.fortilink_interfaces.append(fortilink_name)
        self.fortilink_just_configued.append(fortilink_name)
        sleep(2)
        show_cmds = f"""
        config vdom
            edit root
                config system interface
                    edit {fortilink_name}
                        show 
        """
        self.fgt_show_commands(show_cmds)

    def local_discovery(self,*args,**kwargs):
        self.fortigate_system_status()
        self.collect_physical_ports()
        #self.port2mac()

    def fgt_network_discovery(self,*args,**kwargs):
        self.discover_fgt_lldp()
        print(f"Fotilink ports = {self.fortilink_ports}")
        print(f"Fotigate HA ports = {self.fgt_ha_ports}")

    def discover_fgt_lldp(self):

        sample = """
        FortiGate-2500E # conf vdom

        FortiGate-2500E (vdom) # edit root
        current vf=root:0

        FortiGate-2500E (root) # diagnose lldprx neighbor summary
        1 port 15 mac 70:4C:A5:52:38:D4  chassis 70:4C:A5:52:38:FC port 'port1' system 'FortiGate-2500E'
        2 port 18 mac 90:6C:AC:62:14:40  chassis 90:6C:AC:62:14:40 port 'port1' system 'S548DF4K16000653'
        3 port 16 mac 70:4C:A5:52:38:D5  chassis 70:4C:A5:52:38:FC port 'port2' system 'FortiGate-2500E'
        4 port 17 mac 70:4C:A5:79:22:5C  chassis 70:4C:A5:79:22:5C port 'port1' system 'S548DN4K17000133'

        """
        print(f"========================== {self.serial_number}: Discovering LLDP Neighbors =======================")
        cmds = f"""
            config vdom
            edit root
            diagnose lldprx neighbor summary
        """
        output = self.fgt_show_commands(cmds,timeout=4)
        #print(output)
        neighbor_count = 0
        for line in output:
            if "chassis" in line and "system" in line:
                neighbor_count += 1

        print(f"total number of lldp neighbors are: {neighbor_count}")

        cmds = f"""
            config vdom
            edit root
            diagnose lldprx neighbor details
        """
        output = self.fgt_show_commands(cmds,timeout=10)
        #print(output)
        lldp_neighbor_dict = {}
        regix_mac = r'[0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){5}'
        for line in output:
            if ":" in line and "lldprx" in line:
                if re.search(regix_mac, line):
                    continue
                #print(line)
                k,v = line.split(':')
                lldp_neighbor_dict[k] = v

        #print(lldp_neighbor_dict)

        self.fortilink_ports = []
        self.fgt_ha_ports = []
        for i in range(neighbor_count):
            nei = lldp_class()
            nei.local_port = lldp_neighbor_dict[f'lldprx.neighbor.{i+1}.port.txt'].strip()
            nei.remote_port = lldp_neighbor_dict[f'lldprx.neighbor.{i+1}.port.id.data'].strip()
            nei.remote_system = lldp_neighbor_dict[f'lldprx.neighbor.{i+1}.system.name.data'].strip()
            nei.remote_image = lldp_neighbor_dict[f'lldprx.neighbor.{i+1}.system.desc.data'].strip()
            #print(f"Debug associating remote system: remote_system name = {nei.remote_system}")
            for device in self.tb.devices:
                #print(device.hostname)
                if nei.remote_system == device.hostname or nei.remote_system == device.discovered_hostname or device.serial_number in nei.remote_system:
                    print(f"Debug-lldp neighbor found: device hostname: {nei.remote_system}")
                    print(f"Debug-lldp neighbor found: device discovered hostname: {device.discovered_hostname}")
                    if 'tier1' in device.role:
                        self.fortilink_ports.append(nei.local_port)
                        nei.remote_system_role = device.role

                        neighbor_tier = int(re.match(r'tier([0-9]+)-([0-9]+)',device.role).group(1)) 
                        neighbor_pod = int(re.match(r'tier([0-9]+)-([0-9]+)',device.role).group(2)) 
                               
                        if neighbor_pod not in self.fortilink_ports_pod:
                            self.fortilink_ports_pod.setdefault(neighbor_pod,[]).append(nei.local_port)
                        else:
                            self.fortilink_ports_pod[neighbor_pod].append(nei.local_port)
                    elif "FGT" in device.role and self.serial_number != device.serial_number:
                        nei.remote_system_role = device.role
                        self.fgt_ha_ports.append(nei.local_port)
                    else:
                        pass
            nei.print_lldp()
            self.lldp_neighbors_list.append(nei)




    def port2mac(self,*args,**kwargs):
        sample = """
        commands: 
            FortiGate-2500E # config global

            FortiGate-2500E (global) # get hardware nic port1 | grep HWaddr
        output:
            Current_HWaddr   70:4c:a5:52:38:d4
            Permanent_HWaddr 70:4c:a5:52:38:d4
        """
        print(f"{self.name}: Discovering mac address for physical ports.......")
        port_mac_pair = {}
        mac_port_pair = {}
        for port in self.physical_ports:
            cmds = f"""
                config global
                get hardware nic {port} | grep HWaddr
            """
            hw_addresses = self.fgt_show_commands(cmds,timeout=1)
            debug(hw_addresses)

            mac_regex = r'([0-9a-f]{2}(?::[0-9a-f]{2}){5})'
            for addr in hw_addresses:
                #print(addr)
                if "Current_HWaddr" in addr:
                    #print(addr)
                    matched = re.search(mac_regex,addr)
                    if matched:
                        mac = matched.group(1)
                        #print(mac)
                        port_mac_pair[port] = mac
                        mac_port_pair[mac] = port

        self.port_mac_pair = port_mac_pair
        self.mac_port_pair = mac_port_pair
        #print(self.port_mac_pair)
        #print(self.mac_port_pair)

    def set_port_alias(self,*args,**kwargs):
        for port in self.physical_ports:
            config = f"""
            conf vdom
                edit root
                config system interface
                edit {port}
                    set lldp-reception enable
                    set lldp-transmission enable
                    set alias {port}
                    next
                    end
                end
            """
            config_cmds_lines(self.console,config)

    def execute_custom_command(self,*args,**kwargs):
        switch_name = kwargs["switch_name"]
        cmd = kwargs["cmd"]
        if 'vdom' in kwargs:
            vdom = kwargs["vdom"]
        else:
            vdom = "root"

        config = f"""
        config vdom
            edit {vdom}
            execute switch-controller custom-command {cmd} {switch_name}
        end
        end
        """
        config_cmds_lines(self.console,config)

    def fgt_show_commands(self,cmds,**kwargs):
        if 'timeout' in kwargs:
            timeout = kwargs['timeout']
        else:
            timeout = 3
        #relogin_if_needed(tn)
        #make sure to start from the gloal prompt
        tn = self.console
        handle_prompt_before_commands(tn)
        cmds = split_f_string_lines(cmds)
        for i in range(len(cmds)):
            original_cmd = cmds[i]
            cmd = cmds[i]
            cmd_bytes = convert_cmd_ascii_n(cmd)
            if i != len(cmds)-1:
                tn.write(cmd_bytes)
                tn.write(('' + '\n').encode('ascii')) # uncomment this line if doesn't work
            else:
                tn.write(cmd_bytes)
                tn.write(('' + '\n').encode('ascii')) # uncomment this line if doesn't work
                sleep(timeout)
                output = tn.read_very_eager()
                #print(output)
                out_list = output.split(b'\r\n')
                encoding = 'utf-8'
                out_str_list = []
                for o in out_list:
                    o_str = o.decode(encoding).strip(' \r')
                    out_str_list.append(o_str)
                good_out_list = clean_show_output_recursive(out_str_list,original_cmd)
                debug(good_out_list)
                tprint(f"-------------------------------------------")
                for i in good_out_list:
                    tprint(i)
        tn.write(('end' + '\n').encode('ascii'))
        sleep(0.5)
        tn.write(('end' + '\n').encode('ascii'))
        sleep(0.5)
        return good_out_list


    def discover_managed_switches(self,*args,**kwargs):

        sample_v7 = """
        FortiGate-2500E (root) # execute switch-controller get-conn-status 
        Managed-devices in current vdom root:

        FortiLink interface : Myfortilink
        SWITCH-ID         VERSION           STATUS         FLAG   ADDRESS              JOIN-TIME            NAME            
        S548DF4K16000653  v6.4.7 (478)      Authorized/Up   -   10.255.2.2      Wed May 12 20:58:44 2021    -               
        S548DN4K17000133  v6.4.7 (478)      Authorized/Up   -   10.255.2.3      Wed May 12 20:44:40 2021    -               
        S248EFTF18003278  v6.4.7 (478)      Authorized/Up   -   10.255.2.4      Wed May 12 20:46:10 2021    -               
        S248EFTF18002594  v6.4.7 (478)      Authorized/Up   -   10.255.2.5      Wed May 12 20:46:14 2021    -               

         Flags: C=config sync, U=upgrading, S=staged, D=delayed reboot pending, E=config sync error, 3=L3
         Managed-Switches: 4 (UP: 4 DOWN: 0)
        """
        sample_output = """
        FortiGate-3000D (root) # execute switch-controller get-conn-status
        Managed-devices in current vdom root:

        STACK-NAME: FortiSwitch-Stack-fortilink
        SWITCH-ID         VERSION           STATUS         FLAG   ADDRESS              JOIN-TIME            NAME
        S224EPTF18000630  v7.0.0 (007)      Authorized/Up   -   169.254.1.4     Fri Feb 19 21:53:49 2021    -
        S224EPTF18000820  v7.0.0 (007)      Authorized/Up   -   169.254.1.5     Fri Feb 26 10:20:43 2021    -
        S248EF3X17000518  v7.0.0 (007)      Authorized/Up   -   169.254.1.3     Fri Feb 19 21:53:21 2021    -
        S248EF3X17000533  v7.0.0 (007)      Authorized/Up   -   169.254.1.2     Fri Feb 26 10:17:29 2021    -
        S424DF3X14000015  v7.0.0 (008)      Authorized/Up   -   169.254.1.8     Fri Feb 26 11:00:28 2021    -
        S424DN3X16000332  v7.0.0 (008)      Authorized/Up   -   169.254.1.9     Fri Feb 26 11:04:00 2021    -
        S448DN3X15000028  v7.0.0 (007)      Authorized/Up   -   169.254.1.6     Fri Feb 26 11:26:46 2021    -
        S448DP3X15000029  v7.0.0 (008)      Authorized/Up   -   169.254.1.7     Fri Feb 26 11:53:20 2021    -

        Flags: C=config sync, U=upgrading, S=staged, D=delayed reboot pending, E=config sync error, 3=L3
        Managed-Switches: 8 (UP: 8 DOWN: 0)
        """

        tb = kwargs['topology']
        if 'vdom' in kwargs:
            vdom = kwargs['vdom']
        else:
            vdom = "root"

        config = f"""
            config vdom
            edit {vdom}
        """
        config_cmds_lines(self.console,config)

        output = collect_show_cmd(self.console,"execute switch-controller get-conn-status")
        dprint(output)

        Found = False
        End = False
        managed_switches = []
        try:
            for line in output:
                if "SWITCH-ID" in line and "VERSION" in line and "STATUS" in line:
                    Found = True
                    continue
                if "Flags: C=config sync" in line:
                    End = True
                    break

                if Found and not End and len(line) > 1: 
                    dprint(line)
                    msw = Managed_Switch(self.console)
                    msw.switch_id = line.split()[0]
                    msw.major_version = line.split()[1]
                    msw.minor_version = re.sub('[()]',"",line.split()[2])
                    status = line.split()[3].split('/')
                    if status[0] == "Authorized":
                        msw.authorized = True
                    else:
                        msw.authorized = False
                    if "Up" in status[1]:
                        msw.up = True
                    else:
                        msw.up = False
                    msw.flag = line.split()[4]
                    msw.address = line.split()[5]
                    managed_switches.append(msw)

                    for sw in tb.switches:
                        if msw.switch_id == sw.serial_number:
                            sw.managed = True
                            msw.switch_obj = sw
                            msw.switch_obj.ftg_console = self.console
                            msw.ftg_console = self.console
        except Exception as e:
            print("Some managed switches are not recognized by the fortigate")
        self.managed_switches_list = managed_switches
        return self.managed_switches_list

    def enable_multiple_vdom(self):
        config = """
        conf system global
        set vdom-mode multi-vdom
        end
        """
        config_cmds_lines(self.console,config,mode="slow")
        switch_wait_enter_yes(self.console,"Do you want to continue? (y/n)")
        sleep(2)
        self.fgt_relogin()

    def config_after_factory(self):
        self.change_hostname()
        self.local_discovery()
        self.enable_multiple_vdom()
        sleep(10)
        ports = self.fortilink_ports_db + self.ha_ports_db 

        for port in ports:
            config = f"""
            config vdom
                edit root
                config system interface
                edit {port}
                    set lldp-reception enable
                    set lldp-transmission enable
                    set alias {port}
                    next
                    end
                end
            """
            sleep(2)
            config_cmds_lines(self.console,config)

        #self.set_port_alias()
        config = f"""
        config vdom
        edit root
        conf system interface 
            edit mgmt1 
            set vdom root
            set ip {self.mgmt_ip} {self.mgmt_netmask}
            set allowaccess ping https ssh snmp http telnet fgfm
            set type physical
            set role lan
            next
        end
        """
        config_cmds_lines(self.console,config)
        sleep(10)

        config = f"""
        conf vdom
        edit root
        config router static
            edit 1
                set gateway {self.mgmt_gateway}
                set device "mgmt1"
            next
        end
        """
        config_cmds_lines(self.console,config)
        sleep(10)

    def config_ha(self):
        if self.mode == "Active":
            pri = 200
        else:
            pri = 100

        config = f"""
        config global
        config system ha
            set group-id 25
            set group-name "2500E"
            set mode a-p
            set hbdev {self.fgt_ha_ports[0]} 50 {self.fgt_ha_ports[1]} 25
            set session-pickup enable
            set override enable
            set priority {pri}
            end
            end
        """
        config_cmds_lines(self.console,config)

    def config_msw_mclag_icl(self):
        for msw in self.managed_switches_list:
            icl_ports = msw.switch_obj.icl_links
            if len(icl_ports) == 0:
                continue

            config = f"""
                config vdom
                edit root
                config switch-controller managed-switch
                edit {msw.switch_id}
                config ports
                """
            config_cmds_lines(self.console,config)

            
            for port in icl_ports:
                config = f"""
                edit {port}
                set lldp-profile default-auto-mclag-icl
                next 
                """
                config_cmds_lines(self.console,config)

            config = f"""
                end
                end
                """
            config_cmds_lines(self.console,config)

    def config_ftg_ixia_port(self,*args,**kwargs):
        port = kwargs['port']
        ip = kwargs['ip']
        mask = kwargs['mask']
        dhcp_start = kwargs["dhcp_start"]
        dhcp_end = kwargs["dhcp_end"]

        config = f"""
        config vdom
            edit root
            config system interface
            edit {port}
                set vdom "root"
                set ip {ip} {mask}
                set allowaccess ping https ssh snmp http fgfm speed-test
                set type physical
        end
        end
        config vdom
            edit root
            conf system dhcp server
            edit 7
                    set dns-service default
                    set default-gateway {ip}
                    set netmask {mask}
                    set interface {port}
                    config ip-range
                        edit 1
                            set start-ip {dhcp_start}
                            set end-ip {dhcp_end}
                        next
                    end
                next
            end
        end
        end
        """
        config_cmds_lines(self.console,config)

class tbinfo():
    def __init__(self,*args, **kwargs):
        self.devices = None
        self.ixia = None
        self.connections = None
        self.switches = None
        self.fortigates = None


    def show_tbinfo(self):
        for d in self.devices:
            print_dash_line()
            d.print_info()

        print_double_line()
        if self.ixia != None:
            self.ixia.print_ixia_info()

        print_double_line()
        if self.connections != None:
            for c in self.connections:
                print_dash_line()
                c.print_connection_info()


class Connection_XML():
    def __init__(self,*args,**kwargs):
        self.name = None
        self.connection_string = None
        self.type = None
        self.mode = None
        self.left_string = None
        self.right_string = None
        self.left_device = None
        self.left_device_obj = None
        self.left_switch = None
        self.left_port = None
        self.right_device = None
        self.right_device_obj = None
        self.right_switch = None
        self.right_port = None
        self.active = False
        self.testtopo_name = None

    def print_connection_info(self):
        print(f"Connection name = {self.name}")
        print(f"Connection String In XML File = {self.connection_string}")
        print(f"Connection Type = {self.type}")
        print(f"Connection Mode = {self.mode}")
        print(f"Connection Left String = {self.left_string}")
        print(f"Connection Right String = {self.right_string}")
        print(f"Connection Left Device Name = {self.left_device}")
        print(f"Connection Left Device Object = {self.left_device_obj}")
        print(f"Connection Left Port = {self.left_port}")
        print(f"Connection Right Device Name = {self.right_device}")
        print(f"Connection Right Device Object = {self.right_device_obj}")
        print(f"Connection Right Port = {self.right_port}")
        print(f"Connection Active In this testing = {self.active}")
        print(f"Connection link name in test topology = {self.testtopo_name}")

    def associate_ports_device(self):
        if self.type == "tier1_link" and self.left_device_obj.type == "FGT":
            self.left_device_obj.fortilink_ports.append(self.left_port)
        elif self.type == "tier1_link" and self.right_device_obj.type == "FGT":
            self.right_device_obj.fortilink_ports.append(self.right_port)
        elif self.type == "tier1_link" and self.right_device_obj.type == "FSW":
            self.right_device_obj.fortigate_ports.append(self.right_port)
        elif self.type == "tier1_link" and self.left_device_obj.type == "FSW":
            self.left_device_obj.fortigate_ports.append(self.left_port)
        elif self.type == "ha_link":
            self.left_device_obj.ha_ports.append(self.left_port)
            self.right_device_obj.ha_ports.append(self.right_port)
        elif self.type == "ixia_link":
            self.left_device_obj.ixia_ports.append(self.left_port)
        else:
            pass

    def update_obj(self,devices,ixia):
        left_found = False
        right_found = False
        for d in devices:
            if d.name == self.left_device:
                self.left_device_obj = d
                left_found = True
                break
        if left_found == False and ixia != None:
            if ixia.name == self.left_device:
                self.left_device_obj = ixia
        for d in devices:
            if d.name == self.right_device:
                self.right_device_obj = d
                break
        if right_found == False and ixia != None:
            if ixia.name == self.right_device:
                self.right_device_obj = ixia

    def update_devices_obj(self,switches):
        for s in switches:
            if s.name == self.left_device: 
                self.left_switch = s
            elif s.name == self.right_device: 
                self.right_switch = s

    def shut_unused_ports(self):
        if self.active == False:
            if self.left_switch:
                switch_shut_port(self.left_switch.console,self.left_port)
            if self.right_switch:
                switch_shut_port(self.right_switch.console,self.right_port)
        else:
            if self.left_switch:
                switch_unshut_port(self.left_switch.console,self.left_port)
                self.left_switch.config_switch_interface_cmd(cmd="set allowed-vlan 1-4000",port=self.left_port)
            if self.right_switch:
                switch_unshut_port(self.right_switch.console,self.right_port)
                self.right_switch.config_switch_interface_cmd(cmd="set allowed-vlan 1-4000",port=self.right_port)

    def unshut_all_ports(self):
        if self.left_switch:
            switch_unshut_port(self.left_switch.console,self.left_port)
        if self.right_switch:
            switch_unshut_port(self.right_switch.console,self.right_port)


    def parse_string(self):
            self.left_string,self.right_string = self.connection_string.split(',')
            self.left_device,self.left_port = self.left_string.split(":")
            self.right_device,self.right_port = self.right_string.split(":")

class IXIA_XML():
    def __init__(self, *args, **kwargs):
        #<trafgen1 type="IXIA" model="IXIA" chassis_ip="10.160.12.5" tcl_server_ip="10.160.12.5" ixnetwork_server_ip="10.160.37.24:8030">
        self.name = None
        self.type = None
        self.model = None
        self.chassis_ip = None
        self.tcl_server_ip = None
        self.ixnetwork_server_ip = None
        self.ixnetwork_server_port = None
        self.active = False
        self.port_list = []
        self.port_active_list = []
        self.device_list = []
        self.device_list_obj = []
        self.device_port_list = []
        self.device_list_active = []
        self.device_port_list_active = []
        self.port_dev_pair_list = []


    def print_ixia_info(self):
        print(f"IXIA Name in XML  = {self.name}")
        print(f"IXIA Type = {self.type}")
        print(f"IXIA Mode = {self.model}")
        print(f"IXIA Chassis IP = {self.chassis_ip}")
        print(f"IXIA TCL Server IP = {self.tcl_server_ip}")
        print(f"IXIA Ixnetwork Server IP = {self.ixnetwork_server_ip}")
        print(f"IXIA Ixnetwork Server Port = {self.ixnetwork_server_port}")

    def update_ixia_portList(self,connections):
        for c in connections:
            if "trafgen" in c.right_device:
                
                self.device_list.append(c.left_device_obj.hostname)
                self.device_list_obj.append(c.left_device_obj)
                self.device_port_list.append(c.left_port)
                self.port_list.append(c.right_port)
                if c.active:
                    port_dev_pair = {}
                    self.port_active_list.append(c.right_port)
                    self.device_list_active.append(c.left_device_obj.hostname)
                    self.device_port_list_active.append(c.left_port)
                    port_dev_pair[c.right_port] = c.left_device_obj.hostname
                    self.port_dev_pair_list.append(port_dev_pair)

            
class Device_XML():
    def __init__(self,*args,**kwargs):
        self.name = None
        self.hostname = None
        self.console_ip = None
        self.console_line = None
        self.username = None
        self.tftp_ip = None
        self.password = None
        self.mgmt_ip = None
        self.mgmt_netmask = None
        self.mgmt_gateway = None
        self.license = None
        self.role = None
        self.type = None
        self.active = False
        self.uplink_ports = None
        self.serial_number = None
        self.discovered_hostname = None
        self.version = None
        self.pdu_model = None
        self.pdu_ip = None
        self.pdu_port = None
        self.pdu_ip_2 = None
        self.pdu_port_2 = None
        self.dual_pdu = False
        self.fortilink_ports = []
        self.fortigate_ports = []
        self.ha_ports = []
        self.ixia_ports = []


    def print_info(self):
        print(f"Device Name in XML File = {self.name}")
        print(f"Device Host Name = {self.hostname}")
        print(f"Serial Number = {self.serial_number}")
        print(f"Discovered Hostname = {self.discovered_hostname}")
        print(f"Platform version = {self.version}")
        print(f"Device type = {self.type}")
        print(f"Device Active = {self.active}")
        print(f"Device Role = {self.role}")
        print(f"Console IP = {self.console_ip}")
        print(f"Console Line = {self.console_line}")
        print(f"Mamangement IP = {self.mgmt_ip}")
        print(f"Management Mask = {self.mgmt_netmask}")
        print(f"Management Gateway = {self.mgmt_gateway}")
        print(f"TFTP Server IP in XML File = {self.tftp_ip}")
        print(f"Login username= {self.username}")
        print(f"Login password= {self.password}")
        print(f"License = {self.license}")
        print(f"Device actively used this the test topo = {self.active}")
        print(f"Device role in this the test topo = {self.role}")

class POE_TESTER():
    def __init__(self,*args,**kwargs):
        device_xml = args[0]
        self.tb=kwargs['topo_db']
        self.console_ip = device_xml.console_ip
        self.console_line = device_xml.console_line
        self.console = telnet_poe(self.console_ip, self.console_line)

    def poe_just_reset(self,*args,**kwargs):
        if "current" in kwargs:
            current = kwargs["current"]
        else:
            current = 20

        if "poe_class" in kwargs:
            poe_class = kwargs["poe_class"]
        else:
            poe_class = 0

        self.enter_poe_command(cmd ='reset')
        sleep(2)

    def poe_reset(self,*args,**kwargs):
        if "current" in kwargs:
            current = kwargs["current"]
        else:
            current = 20

        if "poe_class" in kwargs:
            poe_class = kwargs["poe_class"]
        else:
            poe_class = 0

        self.enter_poe_command(cmd ='reset')
        sleep(2)
        self.enter_poe_command(cmd ='connect on')
        sleep(2)
        self.enter_poe_command(cmd ='detect ok ')
        sleep(2)
        self.enter_poe_command(cmd =f'class {poe_class}')
        sleep(2)
        self.enter_poe_command(cmd =f'set {current}')
        sleep(2)
        self.enter_poe_command(cmd ='auto on')
        sleep(2)

    def group_poe_reset(self,*args,**kwargs):
        if "current" in kwargs:
            current = kwargs["current"]
        else:
            current = 20

        if "poe_class" in kwargs:
            poe_class = kwargs["poe_class"]
        else:
            poe_class = 0

        if "group_name" in kwargs:
            grp = kwargs["group_name"]
        else:
            grp = "g1"

        self.enter_poe_command(cmd =f'{grp} reset')
        sleep(2)
        self.enter_poe_command(cmd =f'{grp} connect on')
        sleep(2)
        self.enter_poe_command(cmd =f'{grp} detect ok ')
        sleep(2)
        self.enter_poe_command(cmd =f'{grp} class {poe_class}')
        sleep(2)
        self.enter_poe_command(cmd =f'{grp} set {current}')
        sleep(2)
        self.enter_poe_command(cmd =f'{grp} auto on')
        sleep(2)

    def port_poe_reset(self,*args,**kwargs):
        if "current" in kwargs:
            current = kwargs["current"]
        else:
            current = 20

        if "poe_class" in kwargs:
            poe_class = kwargs["poe_class"]
        else:
            poe_class = 0

        if "port_name" in kwargs:
            port = kwargs["port_name"]
        else:
            port = "p1"

        if "reset" in kwargs:
            config_reset = kwargs["reset"]
        else:
            config_reset = "yes"
        sleep_time = 0.5
        if config_reset == "yes" or config_reset == "Yes" or config_reset == "YES":
            self.enter_poe_command(cmd =f'{port} reset')
            sleep(sleep_time)
        self.enter_poe_command(cmd =f'{port} connect on')
        sleep(sleep_time)
        self.enter_poe_command(cmd =f'{port} detect ok ')
        sleep(sleep_time)
        self.enter_poe_command(cmd =f'{port} class {poe_class}')
        sleep(sleep_time)
        self.enter_poe_command(cmd =f'{port} set {current}')
        sleep(sleep_time)
        self.enter_poe_command(cmd =f'{port} auto on')
        sleep(sleep_time)

    def get_poe_command(self,*args,**kwargs):
        tn = self.console
        cmd = kwargs["cmd"]
        tn.write(('' + '\r').encode('utf-8'))
        sleep(2)
        tn.read_until((">").encode('utf-8'),timeout=5)
        print(f"start enter command......{cmd}")
        #tn.write(('measure').encode('ascii'))
        tn.write((cmd + "\r").encode("utf-8"))
        sleep(2)
        #output = tn.read_until((">").encode('ascii'),timeout=5)
        output = tn.read_very_eager()
        print(output)
        out_list = self.parse_poe_output(output,cmd)
        return out_list

    def parse_poe_output(self,output,original_cmd):
        out_list = output.split(b'\r\n')
        encoding = 'utf-8'
        out_str_list = []
        for o in out_list:
            o_str = o.decode(encoding).strip(' \r')
            out_str_list.append(o_str)
        good_out_list = clean_show_output_recursive(out_str_list,original_cmd)
        new_list = []
        for item in good_out_list:
            if original_cmd in item or ">" in item:
                good_out_list.remove(item)

        debug(good_out_list)
        print_output_list(good_out_list)
        return good_out_list

    def enter_poe_command(self,*args,**kwargs):
        tn = self.console
        cmd = kwargs["cmd"]
        tn.write(('' + '\r').encode('utf-8'))
        sleep(1)
        tn.read_until((">").encode('utf-8'),timeout=5)
        print(f"start enter command......{cmd}")
        #tn.write(('measure').encode('ascii'))
        tn.write((cmd + "\r").encode("utf-8"))

    def parse_measure_output(self,out_list):
        power_dict = {}
        for item in out_list:
            p,v = item.split()
            power_dict[p.strip(":")] = v 

        return power_dict
    
    def parse_status_output(self,out_list):
        power_dict = {}
        for item in out_list:
            p,d,v = item.split()
            power_dict[p.strip(":")] = v 

        return power_dict

