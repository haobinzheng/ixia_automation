import os
import sys
import time
import re
import argparse
import threading
from threading import Thread
from time import sleep
import multiprocessing

from utils import *
import settings 
from test_process import * 
from common_lib import *
from common_codes import *
from cli_functions import *

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

    def basic_config(self):
        basic_config_prefix_list(self.switch.console)

    def clean_up(self):
        pass

class Router_aspath_list:
    def __init__(self,*args,**kargs):
        self.switch = args[0]

    def basic_config(self):
        basic_config_aspath_list(self.switch.console)

    def clean_up(self):
        pass

class Router_access_list:
    def __init__(self,*args,**kargs):
        self.switch = args[0]

    def basic_config(self):
        basic_config_access_list(self.switch.console)

    def acl_find_clauses(self):
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
        self.find_clauses()
        switch_exec_cmd(self.switch.console,"config router route-map")
        for c in self.clauses:
            switch_exec_cmd(self.switch.console, f"delete {c} " )
        switch_exec_cmd(self.switch.console,"end")


class Router_route_map:
    def __init__(self,*args,**kwargs):
         self.switch = args[0]

    def community_config(self):
        route_map_community(self.switch.console)

    def basic_config(self):
        basic_config_route_map(self.switch.console)

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


    def clean_up(self):
        self.find_clauses()
        switch_exec_cmd(self.switch.console,"config router route-map")
        for c in self.clauses:
            switch_exec_cmd(self.switch.console, f"delete {c} " )
        switch_exec_cmd(self.switch.console,"end")


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

class Router_OSPF:
    def __init__(self,*args,**kargs):
        self.switch = args[0]
        self.dut = self.switch.console
        self.neighbor_list = []
        #self.change_router_id(self.switch.loop0_ip)

    def update_switch(self,switch):
        self.switch = switch
        self.dut = switch.console

    def basic_config(self):
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
        config_cmds_lines(self.dut,ospf_config)

    def show_protocol_states(self):
        self.show_config()
        self.show_neighbor()
        self.show_hardware_l3()

    def show_config(self):
        switch_show_cmd(self.switch.console,"show router ospf")

    def show_neighbor(self):
        switch_show_cmd(self.dut, "get router info ospf neighbor all")

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
        dut = self.dut
        neighbor_dict_list = get_router_info_ospf_neighbor(dut)
        neighbor_list = []
        for n in neighbor_dict_list:
            neighbor = Ospf_Neighbor(n)
            neighbor_list.append(neighbor)
        self.neighbor_list = neighbor_list
        return neighbor_list

    def show_ospf_neighbors(self):
        for neighbor in self.neighbor_list:
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

class BGP_Neighbor:
    def __init__(self,*args,**kargs):
        # Neighbor        V         AS MsgRcvd MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd
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
        try:
            self.prefix_recieved = int(neighbor_dict["State/PfxRcd"])
        except Exception as e:
            self.prefix_recieved = neighbor_dict["State/PfxRcd"]

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

class Router_BGP:
    def __init__(self,*args,**kwargs):
        self.switch = args[0]
        self.ospf_neighbors = [n.id for n in self.switch.router_ospf.neighbor_list]
        self.ospf_neighbors_address = [n.address for n in self.switch.router_ospf.neighbor_list]
        self.router_id = self.switch.loop0_ip
        self.bgp_neighbors_objs = None

    def update_switch(self,switch):
        self.switch = switch

    def check_network_exist(self,nets):
        return check_route_exist(dut=self.switch.console,networks=nets,cmd="get router info bgp network")


    def check_neighbor_status(self):
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
        self.show_config()
        self.show_bgp_summary()
        self.show_bgp_network()

    def show_bgp_network(self):
        dut = self.switch.dut
        switch_show_cmd(self.switch.console,"get router info bgp network")

    def get_neighbors_summary(self):
        bgp_neighor_list = get_router_bgp_summary(self.switch.console)
        items_list = []
        for n_dict in bgp_neighor_list:
            n_obj = BGP_Neighbor(n_dict,self.switch)
            items_list.append(n_obj)
        self.bgp_neighbors_objs = items_list
        return items_list   

    def update_ospf_neighbors(self):
        self.ospf_neighbors = [n.id for n in self.switch.router_ospf.neighbor_list]
        self.ospf_neighbors_address = [n.address for n in self.switch.router_ospf.neighbor_list]

    def config_ibgp_mesh_direct(self):
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

    def show_config(self):
        switch_show_cmd(self.switch.console,"show router bgp")

    def config_ibgp_loopback_bfd(self,action):
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

    def config_ibgp_mesh_loopback(self):
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
                next
                end
            end
            """
            config_cmds_lines(dut,bgp_config)

    def config_ebgp_mesh_direct(self):
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
                next
                end
            end
            """
            config_cmds_lines(dut,bgp_config)

    def config_ebgp_mesh_multihop(self):
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
                next
                end
            end
            """
            config_cmds_lines(dut,bgp_config)

    def config_ebgp_ixia(self,ixia_port_info):
        tprint(f"============== Configurating eBGP peer relationship to ixia {self.switch.name} ")

        ixia_ip,ixia_mask = seperate_ip_mask(ixia_port_info[6])
        ixia_as = ixia_port_info[5]
        if ixia_ip == None:
            return False
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
        dut=self.switch.console
        switch_show_cmd(dut,"get router info bgp summary")


    def clear_config(self):
        neighbor_list = get_switch_show_bgp(self.switch.console)
        print(neighbor_list)
        network_list = get_bgp_network_config(self.switch.console)
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

        bgp_config = f"""
        config router bgp
            unset router-id
            unset as 
            unset keepalive-timer
            unset holdtime-timer
            unset always-compare-med
            unset bestpath-as-path-ignore  
            end
        """
        config_cmds_lines(self.switch.console,bgp_config)

class FortiSwitch:
    def __init__(self, *args,**kwargs):
        dut_dir = args[0]
        self.dut_dir = dut_dir
        self.comm = dut_dir['comm']  
        self.comm_port = dut_dir['comm_port']  
        self.name = dut_dir['name'] 
        self.label = dut_dir['label'] 
        self.location = dut_dir['location'] 
        self.console = dut_dir['telnet'] 
        self.dut = dut_dir['telnet']  
        self.cfg_file = dut_dir['cfg'] 
        self.mgmt_ip = dut_dir['mgmt_ip'] 
        self.mgmt_mask = dut_dir['mgmt_mask']  
        self.loop0_ip = dut_dir['loop0_ip']  
        self.rid = self.loop0_ip
        self.vlan1_ip = dut_dir['vlan1_ip'] 
        self.vlan1_2nd = dut_dir['vlan1_2nd']
        self.vlan1_subnet = dut_dir['vlan1_subnet']  
        self.vlan1_mask = dut_dir['vlan1_mask'] 
        self.split_ports = dut_dir['split_ports'] 
        self.ports_40g = dut_dir['40g_ports']
        self.static_route = dut_dir['static_route']
        self.static_route_mask = dut_dir['static_route_mask']
        self.ebgp_as = dut_dir['ebgp_as']
        self.router_ospf = Router_OSPF(self)
        self.router_bgp = Router_BGP(self)
        self.access_list= Router_access_list(self)
        self.route_map = Router_route_map(self)
        self.aspath_list = Router_aspath_list(self)
        self.prefix_list = Router_prefix_list(self)
        self.community_list = Router_community_list(self)
        self.lldp_neighbor_list = get_switch_lldp_summary(self.console)
        self.neighbor_ip_list = []
        self.neighbor_switch_list = []


        

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
        self.show_routing_table()
        self.router_ospf.show_protocol_states()
        self.router_bgp.show_protocol_states()

    def show_routing_table(self):
        switch_show_cmd(self.console,"get router info routing-table all ")

    def factory_reset_nologin(self):
        switch_factory_reset_nologin(self.dut_dir)

    def relogin(self):
        dut = self.console
        tprint(f"============ relogin {self.name} ====== ")
        try:
            relogin_if_needed(dut)
        except Exception as e:
            debug("something is wrong with rlogin_if_needed at bgp, try again")
            relogin_if_needed(dut)
        image = find_dut_image(dut)
        tprint(f"============================ {self.name} software image = {image} ============")
        switch_show_cmd(self.console,"get system status")

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