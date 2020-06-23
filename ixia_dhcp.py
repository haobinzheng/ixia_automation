
from ixia_restpy_lib import *
 
if __name__ == "__main__":
    apiServerIp = '10.105.19.19'
    ixChassisIpList = ['10.105.241.234']

    # apiServerIp = '10.105.0.119'
    # ixChassisIpList = ['10.105.0.102']
    
    #chassis_ip, module,port,mac,bgp_network,bgp_as,ip_address/mask, gateway
    # portList = [[ixChassisIpList[0], 1,1,"00:11:01:01:01:01","10.10.1.1",101,"10.1.1.101/24","10.1.1.1"], 
    # [ixChassisIpList[0], 1, 2,"00:12:01:01:01:01","10.20.1.1",102,"10.1.1.102/24","10.1.1.1"],
    # [ixChassisIpList[0], 1, 3,"00:13:01:01:01:01","10.30.1.1",103,"10.1.1.103/24","10.1.1.1"],
    # [ixChassisIpList[0], 1, 4,"00:14:01:01:01:01","10.40.1.1",104,"10.1.1.104/24","10.1.1.1"], 
    # [ixChassisIpList[0], 1, 5,"00:15:01:01:01:01","10.50.1.1",105,"10.1.1.105/24","10.1.1.1"],
    # [ixChassisIpList[0], 1, 6,"00:16:01:01:01:01","10.60.1.1",106,"10.1.1.106/24","10.1.1.1"]]

    bgp_portList = [[ixChassisIpList[0], 8,13,"00:11:01:01:01:01","10.1.1.0",101,"10.10.1.100/24","10.10.1.254"], 
    [ixChassisIpList[0], 8, 14,"00:12:01:01:01:01","10.20.1.1",102,"10.1.1.254/24","10.10.1.254"],
    [ixChassisIpList[0], 8, 15,"00:13:01:01:01:01","10.30.1.1.",102,"10.1.1.254/24","10.10.1.254"],
    [ixChassisIpList[0], 8, 16,"00:14:01:01:01:01","10.40.1.1",102,"10.10.1.1/24","10.10.1.253"]]

    myixia = IXIA(apiServerIp,ixChassisIpList,bgp_portList)

    myixia.topologies[0].add_ipv4()
    myixia.topologies[0].add_dhcp_server()
    myixia.topologies[0].dhcp_server_gw()
    myixia.topologies[0].dhcp_server_pool_size(pool_size = 20000)
    myixia.topologies[0].dhcp_server_address(start_ip = "10.10.1.2",prefix=16)

    myixia.topologies[1].add_dhcp_client()
    myixia.topologies[2].add_dhcp_client()

    myixia.topologies[3].add_ipv4()
    myixia.topologies[3].add_dhcp_server()
    myixia.topologies[3].dhcp_server_gw()
    myixia.topologies[3].dhcp_server_pool_size(pool_size = 20000)
    myixia.topologies[3].dhcp_server_address(start_ip = "10.20.1.2",prefix=16)

    myixia.start_protocol(wait=40)


    myixia.create_traffic(src_topo=myixia.topologies[1].topology, dst_topo=myixia.topologies[2].topology,traffic_name="t1_to_t2",tracking_name="Tracking_1")
    myixia.create_traffic(src_topo=myixia.topologies[2].topology, dst_topo=myixia.topologies[1].topology,traffic_name="t2_to_t1",tracking_name="Tracking_2")


    myixia.start_traffic()
    myixia.collect_stats()
    myixia.check_traffic()

    #myixia.topologies[0].add_ipv4()
    # myixia.topologies[1].add_ipv4()
    # myixia.topologies[2].add_ipv4()
    # myixia.topologies[3].add_ipv4()

    # myixia.topologies[0].add_ptp()
    # myixia.topologies[1].add_ptp()

    exit()


    # myixia.topologies[0].add_ipv4()
    # myixia.topologies[1].add_ipv4()
    # myixia.topologies[2].add_ipv4()
    # myixia.topologies[3].add_ipv4()
    # myixia.topologies[4].add_ipv4()
    # myixia.topologies[5].add_ipv4()


    myixia.topologies[0].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=1000)
    # myixia.topologies[1].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=1000)
    # myixia.topologies[2].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=1000)
    # myixia.topologies[3].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=1000)
    # myixia.topologies[4].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=1000)
    # myixia.topologies[5].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=1000)

    # # myixia.topologies[0].add_aspath_med(1,65010,6000)
    # # myixia.topologies[1].add_aspath_med(2,65020,5000)
    # # myixia.topologies[2].add_aspath_med(3,65030,4000)
    # # myixia.topologies[3].add_aspath_med(4,65040,3000)
    # # myixia.topologies[4].add_aspath_med(5,65050,2000)
    # # myixia.topologies[5].add_aspath_med(6,65060,1000)
    # # myixia.topologies[0].add_aspath_med(1,65010,6000)

    # myixia.topologies[0].change_bgp_routes_attributes(num_path=1,as_base=65010,med=6000,flapping="random",community=3,comm_base=101,weight=111)
    # myixia.topologies[1].change_bgp_routes_attributes(num_path=2,as_base=65020,med=5000,flapping="random",community=3,comm_base=102,weight=222)
    # myixia.topologies[2].change_bgp_routes_attributes(num_path=3,as_base=65030,med=4000,flapping="random",community=3,comm_base=103,weight=333)
    # myixia.topologies[3].change_bgp_routes_attributes(num_path=4,as_base=65040,med=3000,flapping="random",community=3,comm_base=104,weight=444)
    # myixia.topologies[4].change_bgp_routes_attributes(num_path=5,as_base=65050,med=2000,flapping="random",community=3,comm_base=105,weight=555)
    # myixia.topologies[5].change_bgp_routes_attributes(num_path=6,as_base=65060,med=1000,flapping="random",community=3,comm_base=106,weight=666)
    
    # myixia.start_protocol(wait=40)

    # exit()

    # myixia.create_traffic(src_topo=myixia.topologies[0].topology, dst_topo=myixia.topologies[1].topology,traffic_name="t1_to_t2",tracking_name="Tracking_1")
    # myixia.create_traffic(src_topo=myixia.topologies[1].topology, dst_topo=myixia.topologies[0].topology,traffic_name="t2_to_t1",tracking_name="Tracking_2")

    # myixia.create_traffic(src_topo=myixia.topologies[2].topology, dst_topo=myixia.topologies[3].topology,traffic_name="t2_to_t3",tracking_name="Tracking_3")
    # myixia.create_traffic(src_topo=myixia.topologies[3].topology, dst_topo=myixia.topologies[2].topology,traffic_name="t3_to_t2",tracking_name="Tracking_4")

    # myixia.create_traffic(src_topo=myixia.topologies[4].topology, dst_topo=myixia.topologies[5].topology,traffic_name="t4_to_t5",tracking_name="Tracking_5")
    # myixia.create_traffic(src_topo=myixia.topologies[5].topology, dst_topo=myixia.topologies[4].topology,traffic_name="t5_to_t4",tracking_name="Tracking_6")


    # myixia.start_traffic()
    # myixia.collect_stats()
    # myixia.check_traffic()
    
    # testPlatform,Session,ixNetwork,vport_holder_list = ixia_rest_connect_chassis(apiServerIp,ixChassisIpList,portList)
    # if ixNetwork == False:
    #     print(f"Error connected to IXIA chassis {ixChassisIpList}")
    #     exit()
    # ethernet1,device_group1,topology1 = ixia_rest_create_topology(
    #     platform = testPlatform, 
    #     session = Session,
    #     ixnet = ixNetwork,
    #     vport = vport_holder_list[0],
    #     topo_name = "Topology_1",   
    #     dg_name = "DG1",    
    #     multiplier = 1,    
    #     mac_start = "00:11:01:01:01:01",
    #     vlan_id = 1
    # )     

    # if ethernet1 == False:
    #     print(f"Error creating topology on chassis {ixChassisIpList} port {vport_holder_list[0]}")
    #     exit()
    # ip_session_1 = ixia_rest_create_ip(
    #     platform = testPlatform, 
    #     session = Session,
    #     ixnet = ixNetwork,
    #     start_ip = '10.1.1.101',
    #     gw_start_ip = '10.1.1.1',
    #     ethernet = ethernet1,
    #     maskbits = 24,
    # )
    # ethernet2,device_group2,topology2 = ixia_rest_create_topology(
    #     platform = testPlatform, 
    #     session = Session,
    #     ixnet = ixNetwork,
    #     vport = vport_holder_list[1],
    #     topo_name = "Topology_2",   
    #     dg_name = "DG2",    
    #     multiplier = 1,    
    #     mac_start = "00:12:01:01:01:01",
    #     vlan_id = 1
    # )     

    # if ethernet2 == False:
    #     print(f"Error creating topology on chassis {ixChassisIpList} port {vport_holder_list[0]}")
    #     exit()

    # # dhcp_session1 = ixia_rest_create_dhcp_client(
    # #     platform = testPlatform, 
    # #     session = Session,
    # #     ixnet = ixNetwork,
    # #     ethernet = ethernet1,
    # # )
    # # dhcp_session2 = ixia_rest_create_dhcp_client(
    # #     platform = testPlatform, 
    # #     session = Session,
    # #     ixnet = ixNetwork,
    # #     ethernet = ethernet2,
    # # )
    # ip_session_2 = ixia_rest_create_ip(
    #     platform = testPlatform, 
    #     session = Session,
    #     ixnet = ixNetwork,
    #     start_ip = '10.1.1.102',
    #     gw_start_ip = "10.1.1.1",
    #     ethernet = ethernet2,
    #     maskbits = 24,
    # )

    # ixia_rest_create_bgp(
    #     name = "BGP_1",
    #     peer_ip ='10.1.1.1',
    #     type = "external",
    #     local_as = 101,
    #     networks_number = 100,
    #     networks_start_ip = '10.10.0.1',
    #     device_group = device_group1,
    #     ip = ip_session_1,
    # )
    # ixia_rest_create_bgp(
    #     name = "BGP_2",
    #     peer_ip ='10.1.1.2',
    #     type = "external",
    #     local_as = 102,
    #     networks_number = 100,
    #     networks_start_ip = '20.20.0.1',
    #     device_group = device_group2,
    #     ip = ip_session_2,
    # )
     
    

    # ixia_rest_start_protocols(
    #     platform = testPlatform, 
    #     session = Session,
    #     ixnet = ixNetwork,
    #     wait = 40,
    # )

    # ixia_rest_create_traffic(
    #     platform = testPlatform, 
    #     session = Session,
    #     ixnet = ixNetwork,
    #     src = topology1,
    #     dst = topology2,
    #     name= 'topo1_to_topo2',
    #     tracking_group = 'flowGroup0',
    # )
    # ixia_rest_create_traffic(
    #     platform = testPlatform, 
    #     session = Session,
    #     ixnet = ixNetwork,
    #     src = topology2,
    #     dst = topology1,
    #     name= 'topo2_to_topo1',
    #     tracking_group = 'flowGroup1',
    # )
    # ixia_rest_start_traffic(
    #     platform = testPlatform, 
    #     session = Session,
    #     ixnet = ixNetwork,
    #     )
    # sleep(30)
    # flow_stats_list = ixia_rest_collect_stats(
    #     platform = testPlatform, 
    #     session = Session,
    #     ixnet = ixNetwork, 
    # )

    # if check_traffic(flow_stats_list) == False:
    #     tprint("========================= Failed: significant traffic loss ============")
    # else:
    #      tprint("========================= Passed: traffic is passed without loss ============")
