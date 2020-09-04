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

class BGP_networks:
    def __init__(self,*args,**kwargs):
        self.switches = args[0]
        self.routers = []
        for switch in self.switches:
            self.routers.append(switch.router_bgp)

    def show_summary(self):
        for router in self.routers:
            router.show_bgp_summary()
            router.check_neighbor_status()

    def clear_bgp_config(self):
        for router in self.routers:
            router.clear_config()

   
    def build_ibgp_mesh_topo(self):
        for switch in self.switches:
            switch.router_ospf.neighbor_discovery()
            switch.router_bgp.update_ospf_neighbors()
            switch.router_bgp.config_ibgp_mesh_loopback()

    def biuld_ibgp_mesh_topo_sys_intf(self):
        for router1 in self.routers: 
            for router2 in self.routers:
                if router1 is router2: 
                    continue 
                else:
                    self.config_ibgp_session_all_interface(router1,router2) 

    def config_ospf_networks(self):
        for switch in self.switches:
            switch.show_switch_info()
            switch.router_ospf.basic_config()
        console_timer(20,msg="Class BGP Network: After configuring ospf, wait for 20 sec")

    def config_ibgp_session_all_interface(self,bgp1,bgp2):
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

   
    def build_router_reflector_topo(self):
        rr1 = self.routers[0]
        rr2 = self.routers[1]

        for i in range(2,7):
            self.config_ibgp_rr_session(rr1,self.routers[i])
        for i in range(2,7):
            self.config_ibgp_rr_session(rr2,self.routers[i])

        self.config_ibgp_session(rr1,rr2)

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

class Router_OSPF:
    def __init__(self,*args,**kargs):
        self.switch = args[0]
        self.dut = self.switch.console
        self.neighbor_list = []
        self.neighbor_list_v6 = []
        #self.change_router_id(self.switch.loop0_ip)

    def update_switch(self,switch):
        self.switch = switch
        self.dut = switch.console

    def basic_config(self):
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

    def basic_config_v6(self):
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

    def neighbor_discovery_v6(self):
        dut = self.dut
        neighbor_dict_list = get_router_info_ospf_neighbor_v6(dut)
        neighbor_list = []
        for n in neighbor_dict_list:
            neighbor = Ospf_Neighbor_v6(n)
            neighbor_list.append(neighbor)
        self.neighbor_list_v6 = neighbor_list
        return neighbor_list

    def neighbor_discovery_all(self):
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
        for neighbor in self.neighbor_list:
            neighbor.show_details()

    def show_ospf_neighbors_v6(self):
        for neighbor in self.neighbor_list_v6:
            neighbor.show_details()

    def show_ospf_neighbors_all(self):
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
        #self.route_map = Router_route_map()

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
        self.show_bgp_config()
        self.show_bgp_summary()
        self.show_bgp_network()

    def show_bgp_protocol_states_v6(self):
        self.show_bgp_config_v6()
        self.show_bgp_summary_v6()
        self.show_bgp_network_v6()

    def show_bgp_network(self):
        dut = self.switch.dut
        switch_show_cmd(self.switch.console,"get router info bgp network")

    def show_bgp_network_v6(self):
        dut = self.switch.dut
        switch_show_cmd(self.switch.console,"get router info bgp6 network")

    def get_neighbors_summary(self):
        bgp_neighor_list = get_router_bgp_summary(self.switch.console)
        items_list = []
        for n_dict in bgp_neighor_list:
            n_obj = BGP_Neighbor(n_dict,self.switch)
            items_list.append(n_obj)
        self.bgp_neighbors_objs = items_list
        return items_list   

    def get_bgp_neighbors_summary_v6(self):
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
        if "sw_list" in kwargs:
            switch_list = kwargs['sw_list']
        else:
            switch_list = []
        self.ospf_neighbors = [n.id for n in self.switch.router_ospf.neighbor_list]
        self.ospf_neighbors_address = [n.address for n in self.switch.router_ospf.neighbor_list]

    def update_ospf_neighbors_v6(self,*args,**kwargs):
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


    def config_ibgp_mesh_svi_v6(self):
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

    #gradually remove this procedue
    def show_config(self):
        switch_show_cmd(self.switch.console,"show router bgp")

    #gradually use this procedure to replace show_config defined above this line
    def show_bgp_config(self):
        switch_show_cmd(self.switch.console,"show router bgp")

    def show_bgp_config_v6(self):
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

    def config_ibgp_loopback_bfd_v6(self,action):
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

    def config_ibgp_mesh_loopback_v6(self):
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
                next
                end
            end
            """
            config_cmds_lines(dut,bgp_config)

    def activate_ibgp_mesh_loopback_v6(self,*args,**kwargs):
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

        tprint(f"============== Activating address family for iBGPv6 neighbor at {self.switch.name} ")
        dut=self.switch.console
        if address_family == "v4" and interface == "svi":
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
        elif address_family == "v6" and interface == "svi":
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

        elif address_family == "v6" and interface == "loopback":
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

        elif address_family == "v4" and interface == "loopback":
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
        else:
            Info("Error: Did provide correct parameters for BGP address family activation")
            Info("Parameters: address_family = 'v4' or 'v6, interface = 'svi' or 'loopback'")
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

    def config_ebgp_mesh_svi_v6(self):
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

    def config_ebgp_mesh_multihop_v6(self):
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
                    set 
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
                    set 
                next
                end
            end
            """
            config_cmds_lines(dut,bgp_config)

    def config_ebgp_ixia(self,ixia_port):
        tprint(f"============== Configurating eBGP peer relationship to ixia {self.switch.name} ")

        ixia_ip,ixia_mask = seperate_ip_mask(ixia_port[6])
        ixia_as = ixia_port[5]
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

    def config_ebgp_ixia_v6(self,*args,**kwargs):
        tprint(f"============== Configurating eBGP peer relationship to ixia {self.switch.name} ")
        ixia_port = kwargs["ixia_port"]
        ixia_as = kwargs["ixia_as"]
        ixia_ip,ixia_mask = seperate_ip_mask(ixia_port[6])
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

    def show_bgp_summary_v6(self):
        dut=self.switch.console
        switch_show_cmd(dut,"get router info6 bgp summary")

    def clear_config(self):
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

    def clear_config_v6(self):
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


class system_interfaces:
    def __init__(self,*args,**kwargs):
        self.switch = args[0]

    def create_interface(self,*args,**kwargs):
        pass


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
        self.loop0_ipv4 = dut_dir['loop0_ip']  #have a duplicate member just for convenience
        self.loop0_ipv6 = dut_dir['loop0_ipv6']
        self.rid = self.loop0_ip
        self.vlan1_ip = dut_dir['vlan1_ip'] 
        self.vlan1_ipv6= dut_dir['vlan1_ipv6']
        self.vlan1_2nd = dut_dir['vlan1_2nd']
        self.internal = dut_dir['internal']
        self.internal_v6 = dut_dir['internal_v6']
        self.vlan1_subnet = dut_dir['vlan1_subnet']  
        self.vlan1_mask = dut_dir['vlan1_mask'] 
        self.split_ports = dut_dir['split_ports'] 
        self.ports_40g = dut_dir['40g_ports']
        self.static_route = dut_dir['static_route']
        self.static_route_mask = dut_dir['static_route_mask']
        self.ebgp_as = dut_dir['ebgp_as']
        self.software_version = find_dut_build(self.console)[0]
        self.software_build = find_dut_build(self.console)[1]
        self.model = find_dut_model(self.console)
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

    def show_routing_v6(self):
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