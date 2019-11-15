 
import sys, os, time, traceback
from utils import *

# Import the RestPy module
from ixnetwork_restpy.testplatform.testplatform import TestPlatform
from ixnetwork_restpy.assistants.statistics.statviewassistant import StatViewAssistant

def ixia_rest_connect_chassis(apiServerIp,ixChassisIpList,portList):

    #apiServerIp = '10.105.19.19'

    # For Linux API server only
    username = 'admin'
    password = 'admin'

    # The IP address for your Ixia license server(s) in a list.
    licenseServerIp = [apiServerIp]

    # subscription, perpetual or mixed
    licenseMode = 'mixed'

    # tier1, tier2, tier3, tier3-10g
    licenseTier = 'tier3'

    # For linux and connection_manager only. Set to True to leave the session alive for debugging.
    debugMode = False

    # Forcefully take port ownership if the portList are owned by other users.
    forceTakePortOwnership = True

    # ixChassisIpList = ['10.105.241.216']
    
    #portList = [[ixChassisIpList[0], 1,8], [ixChassisIpList[0], 1, 7]]
    while True:
        try:
            testPlatform = TestPlatform(ip_address=apiServerIp, log_file_name='restpy.log')

            # Console output verbosity: 'none'|request|'request response'
            testPlatform.Trace = 'request_response'

            testPlatform.Authenticate(username, password)
            session = testPlatform.Sessions.add()
            ixNetwork = session.Ixnetwork
            testPlatform.info(ixNetwork)
            
            ixNetwork.NewConfig()

            ixNetwork.Globals.Licensing.LicensingServers = licenseServerIp
            ixNetwork.Globals.Licensing.Mode = licenseMode
            ixNetwork.Globals.Licensing.Tier = licenseTier

            # Create vports and name them so you could use .find() to filter vports by the name.
            #After this command is executed, ixnetwork will create two virtual ports with connection status "Unassigend"
            count = 0
            vport_holder_list = []
            for port in portList:
                count += 1
                vport = ixNetwork.Vport.add(Name=f'Port_{count}')
                #testPlatform.info(vport)
                vport_holder_list.append(vport)
            vportList = [vport.href for vport in ixNetwork.Vport.find()]
            vport1 = vport_holder_list[0]
            vport2 = vport_holder_list[1]
            # Assign ports.  
            testPorts = []
            for item in portList:
                testPorts.append(dict(Arg1=item[0], Arg2=item[1], Arg3=item[2]))
            dprint(testPorts)

            ixNetwork.AssignPorts(testPorts, [], vportList, forceTakePortOwnership)
            return testPlatform,session,ixNetwork,vport_holder_list

        except Exception as errMsg:
            print('\n%s' % traceback.format_exc(None, errMsg))
            if debugMode == False and 'session' in locals():
                session.remove()
          

def ixia_rest_create_topology(*args,**kwargs):
    debugMode = False
    try:
        session = kwargs['session']
        testPlatform = kwargs['platform']
        ixNetwork = kwargs['ixnet']
        vport = kwargs['vport']
        topo_name = kwargs['topo_name']
        dg_name = kwargs['dg_name']
        multi = kwargs['multiplier']
        mac_start = kwargs['mac_start']
        vlan_id = kwargs['vlan_id']       
        ixNetwork.info(f'Creating Topology Group {topo_name}')
        topology = ixNetwork.Topology.add(Name=topo_name, Ports=vport)
        deviceGroup = topology.DeviceGroup.add(Name=dg_name, Multiplier=multi)
        ethernet = deviceGroup.Ethernet.add(Name='Eth1')
        ethernet.Mac.Increment(start_value=mac_start, step_value='00:00:00:00:00:01')
        #vlan can not be used in FSW, dont know why. need to investigate
        # ethernet1.EnableVlans.Single(True)

        # ixNetwork.info('Configuring vlanID')
        # vlanObj = ethernet1.Vlan.find()[0].VlanId.Increment(start_value=vlan_id, step_value=0)
        return ethernet,topology
    except Exception as errMsg:
        print('\n%s' % traceback.format_exc(None, errMsg))
        if debugMode == False and 'session' in locals():
            session.remove()
        return False


def ixia_rest_create_ip(*args,**kwargs):
    debugMode = False
    try:
        session = kwargs['session']
        testPlatform = kwargs['platform']
        ixNetwork = kwargs['ixnet']
        start_ip = kwargs['start_ip']
        gw_start_ip = kwargs['gw_start_ip']
        ethernet = kwargs['ethernet']
        ip_prefix = kwargs['maskbits']

        ixNetwork.info('Configuring IPv4')
        ipv4 = ethernet.Ipv4.add(Name='IPV4')
        ipv4.Address.Increment(start_value=start_ip, step_value='0.0.0.1')
        # ipv4.address.RandomMask(fixed_value=16)
        print(dir(ipv4.Address))
        ipv4.GatewayIp.Increment(start_value=gw_start_ip, step_value='0.0.0.1')
        ipv4.Prefix.Single(ip_prefix)
        address = ipv4.Address
        # testPlatform.info(address.prefix)
        return ipv4
    except Exception as errMsg:
        print('\n%s' % traceback.format_exc(None, errMsg))
        if debugMode == False and 'session' in locals():
            session.remove()
        return False

def ixia_rest_create_dhcp_client(*args,**kwargs):
    debugMode = False
    try:
        session = kwargs['session']
        testPlatform = kwargs['platform']
        ixNetwork = kwargs['ixnet']
        ethernet = kwargs['ethernet']
         

        ixNetwork.info('Configuring IPv4 Dhcpv4client')

        #dhcpv4client = ethernet.Dhcpv4client.add(Multiplier=None, Name=None, StackedLayers=None)
        dhcpv4client = ethernet.Dhcpv4client.add(Name="DHCP_client")
        testPlatform.info(dhcpv4client)
        
        # testPlatform.info(address.prefix)
        return dhcpv4client
    except Exception as errMsg:
        print('\n%s' % traceback.format_exc(None, errMsg))
        if debugMode == False and 'session' in locals():
            session.remove()
        return False

    #     ixNetwork.info('Configuring IGMP Host')
    #     igmpHost = ipv4.IgmpHost.add(Name='igmpHost')
  
    #     ixNetwork.info('IGMP Querier')
    #     bgp2 = ipv4.IgmpQuerier.add(Name='igmpQuerier')

def ixia_rest_start_protocols(*args,**kwargs):
    debugMode = False
    session = kwargs['session']
    testPlatform = kwargs['platform']
    ixNetwork = kwargs['ixnet']
    ixNetwork.StartAllProtocols(Arg1='sync')
    wait_time = 90
    while True:
        try:
            ixNetwork.info('Verify protocol sessions\n')
            console_timer(wait_time,msg = f'wait for {wait_time} after protocol starts')
            protocolsSummary = StatViewAssistant(ixNetwork, 'Protocols Summary')
            protocolsSummary.CheckCondition('Sessions Not Started', StatViewAssistant.EQUAL, 0)
            protocolsSummary.CheckCondition('Sessions Down', StatViewAssistant.EQUAL, 0)
            ixNetwork.info(protocolsSummary)
            return 
        except Exception as errMsg:
            print('\n%s' % traceback.format_exc(None, errMsg))
            if debugMode == False and 'session' in locals():
                wait_time += 30

def ixia_rest_create_traffic(*args,**kwargs):
    debugMode = False
    try:
        session = kwargs['session']
        testPlatform = kwargs['platform']
        ixNetwork = kwargs['ixnet']
        src_topo = kwargs['src']
        dst_topo = kwargs['dst']
        traffic_name = kwargs['name']
        tracking_group = kwargs['tracking_group']

        ixNetwork.info('Create Traffic Item')
        trafficItem = ixNetwork.Traffic.TrafficItem.add(Name=traffic_name, BiDirectional=False, TrafficType='ipv4',TransmitMode='sequential')

        ixNetwork.info('Add endpoint flow group')
        trafficItem.EndpointSet.add(Sources=src_topo, Destinations=dst_topo)
        # trafficItem.Tracking.find()[0].TrackBy = [tracking_group]
        

        # # Note: A Traffic Item could have multiple EndpointSets (Flow groups).
        # #       Therefore, ConfigElement is a list.
        ixNetwork.info('Configuring config elements')
        configElement = trafficItem.ConfigElement.find()[0]
        configElement.FrameRate.update(Type='percentLineRate', Rate=50)
        #configElement.TransmissionControl.update(Type='fixedFrameCount', FrameCount=10000)
        configElement.TransmissionControl.update(Type='continuous')
        configElement.FrameRateDistribution.PortDistribution = 'splitRateEvenly'
        configElement.FrameSize.FixedSize = 1000
        
        trafficItem.Generate()
        
        # ixNetwork.Traffic.Apply()
        # ixNetwork.Traffic.Start()

        # StatViewAssistant could also filter by REGEX, LESS_THAN, GREATER_THAN, EQUAL. 
        # Examples:
        #    flowStatistics.AddRowFilter('Port Name', StatViewAssistant.REGEX, '^Port 1$')
        #    flowStatistics.AddRowFilter('Tx Frames', StatViewAssistant.LESS_THAN, 50000)

        # flowStatistics = StatViewAssistant(ixNetwork, 'Flow Statistics')
        # ixNetwork.info('{}\n'.format(flowStatistics))

        # for rowNumber,flowStat in enumerate(flowStatistics.Rows):
        #     ixNetwork.info('\n\nSTATS: {}\n\n'.format(flowStat))
        #     ixNetwork.info('\nRow:{}  TxPort:{}  RxPort:{}  TxFrames:{}  RxFrames:{}\n'.format(
        #         rowNumber, flowStat['Tx Port'], flowStat['Rx Port'],
        #         flowStat['Tx Frames'], flowStat['Rx Frames']))

        # flowStatistics = StatViewAssistant(ixNetwork, 'Traffic Item Statistics')
        # ixNetwork.info('{}\n'.format(flowStatistics))

    except Exception as errMsg:
        print('\n%s' % traceback.format_exc(None, errMsg))
        if debugMode == False and 'session' in locals():
            session.remove()

def ixia_rest_start_traffic(*args,**kwargs):
    session = kwargs['session'] 
    testPlatform = kwargs['platform']
    ixNetwork = kwargs['ixnet']
    trafficItem = ixNetwork.Traffic.TrafficItem
    for item in trafficItem.find():
        testPlatform.info(item)
        tracking = item.Tracking.find()
        testPlatform.info(tracking)
        tracking.TrackBy = [f"flowGroup0",f"trackingenabled0"]
    ixNetwork.Traffic.Apply()
    ixNetwork.Traffic.Start()

 
def ixia_rest_collect_stats(*args,**kwargs):
    debugMode = False
    try:
        session = kwargs['session']
        testPlatform = kwargs['platform']
        ixNetwork = kwargs['ixnet']

        #The following line print out all rows stats at once
        flowStatistics = StatViewAssistant(ixNetwork, 'Flow Statistics')
        print(flowStatistics)
        print(dir(flowStatistics))
        print(type(flowStatistics))
        print("--------------------------------------------------------")
        print(flowStatistics.Rows)
        print(dir(flowStatistics.Rows))
        print(type(flowStatistics))
        # ixNetwork.info('{}\n'.format(flowStatistics))
        flow_stats_list = []
        for rowNumber,flowStat in enumerate(flowStatistics.Rows):
            flowStat_dict = {}
            ixNetwork.info('\n\nSTATS: {}\n\n'.format(flowStat))
            ixNetwork.info('\nRow:{}  TxPort:{}  RxPort:{}  TxFrames:{}  RxFrames:{}  Delta:{} Tx Rate:{}\n'.format(
                rowNumber, flowStat['Tx Port'], flowStat['Rx Port'],
                flowStat['Tx Frames'], flowStat['Rx Frames'],flowStat["Frames Delta"],flowStat["Tx Rate (Bps)"]))
            flowStat_dict['Tx Port'] = flowStat['Tx Port'] 
            flowStat_dict['Tx Port'] = flowStat['Tx Port']
            flowStat_dict['Tx Frames'] = flowStat['Tx Frames']
            flowStat_dict['Rx Frames'] = flowStat['Rx Frames']
            flowStat_dict["Frames Delta"] = flowStat["Frames Delta"]
            flowStat_dict["Tx Rate (Bps)"] = flowStat["Tx Rate (Bps)"]
            flowStat_dict['Traffic Item'] =  flowStat['Traffic Item']
            flowStat_dict['Flow Group'] =    flowStat['Flow Group']
            flowStat_dict['Tx Frame Rate'] = flowStat['Tx Frame Rate']
            flowStat_dict['Tx Rate (bps)'] = flowStat['Tx Rate (bps)']
            flow_stats_list.append(flowStat_dict)

        print(flow_stats_list)
        return flow_stats_list

        # flowStatistics = StatViewAssistant(ixNetwork, 'Traffic Item Statistics')
        # ixNetwork.info('{}\n'.format(flowStatistics))
    except Exception as errMsg:
        print('\n%s' % traceback.format_exc(None, errMsg))
        if debugMode == False and 'session' in locals():
            session.remove()


if __name__ == "__main__":
    apiServerIp = '10.105.19.19'
    ixChassisIpList = ['10.105.241.234']
    
    portList = [[ixChassisIpList[0], 4,15], [ixChassisIpList[0], 4, 16]]
    testPlatform,Session,ixNetwork,vport_holder_list = ixia_rest_connect_chassis(apiServerIp,ixChassisIpList,portList)
    if ixNetwork == False:
        print(f"Error connected to IXIA chassis {ixChassisIpList}")
        exit()
    ethernet1,topology1 = ixia_rest_create_topology(
        platform = testPlatform, 
        session = Session,
        ixnet = ixNetwork,
        vport = vport_holder_list[0],
        topo_name = "Topology_1",   
        dg_name = "DG1",    
        multiplier = 10000,    
        mac_start = "00:11:01:01:01:01",
        vlan_id = 1
    )     

    if ethernet1 == False:
        print(f"Error creating topology on chassis {ixChassisIpList} port {vport_holder_list[0]}")
        exit()
    # ip_session = ixia_rest_create_ip(
    #     platform = testPlatform, 
    #     session = Session,
    #     ixnet = ixNetwork,
    #     start_ip = "10.1.1.1",
    #     gw_start_ip = "10.2.1.1",
    #     ethernet = ethernet1,
    #     maskbits = 16,
    # )
    ethernet2,topology2 = ixia_rest_create_topology(
        platform = testPlatform, 
        session = Session,
        ixnet = ixNetwork,
        vport = vport_holder_list[1],
        topo_name = "Topology_2",   
        dg_name = "DG2",    
        multiplier = 10000,    
        mac_start = "00:12:01:01:01:01",
        vlan_id = 1
    )     

    if ethernet2 == False:
        print(f"Error creating topology on chassis {ixChassisIpList} port {vport_holder_list[0]}")
        exit()

    dhcp_session1 = ixia_rest_create_dhcp_client(
        platform = testPlatform, 
        session = Session,
        ixnet = ixNetwork,
        ethernet = ethernet1,
    )
    dhcp_session2 = ixia_rest_create_dhcp_client(
        platform = testPlatform, 
        session = Session,
        ixnet = ixNetwork,
        ethernet = ethernet2,
    )
    # ip_session = ixia_rest_create_ip(
    #     platform = testPlatform, 
    #     session = Session,
    #     ixnet = ixNetwork,
    #     start_ip = "10.2.1.1",
    #     gw_start_ip = "10.1.1.1",
    #     ethernet = ethernet2,
    #     maskbits = 16,
    # )

    ixia_rest_start_protocols(
        platform = testPlatform, 
        session = Session,
        ixnet = ixNetwork,
    )

    ixia_rest_create_traffic(
        platform = testPlatform, 
        session = Session,
        ixnet = ixNetwork,
        src = topology1,
        dst = topology2,
        name= 'topo1_to_topo2',
        tracking_group = 'flowGroup0',
    )
    ixia_rest_create_traffic(
        platform = testPlatform, 
        session = Session,
        ixnet = ixNetwork,
        src = topology2,
        dst = topology1,
        name= 'topo2_to_topo1',
        tracking_group = 'flowGroup1',
    )
    ixia_rest_start_traffic(
        platform = testPlatform, 
        session = Session,
        ixnet = ixNetwork,
        )
    sleep(30)
    ixia_rest_collect_stats(
        platform = testPlatform, 
        session = Session,
        ixnet = ixNetwork, 
    )
