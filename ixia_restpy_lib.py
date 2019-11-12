 
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
        return ixNetwork,vport_holder_list

    except Exception as errMsg:
        print('\n%s' % traceback.format_exc(None, errMsg))
        if debugMode == False and 'session' in locals():
            session.remove()
        return False,False

def ixia_rest_create_topology(*args,**kwargs):
    debugMode = False
    try:
        ixNetwork = kwargs['session']
        vport1 = kwargs['vport']
        topo_name = kwargs['topo_name']
        dg_name = kwargs['dg_name']
        multi = kwargs['multiplier']
        mac_start = kwargs['mac_start']
        vlan_id = kwargs['vlan_id']       
        ixNetwork.info(f'Creating Topology Group {topo_name}')
        topology1 = ixNetwork.Topology.add(Name=topo_name, Ports=vport1)
        deviceGroup1 = topology1.DeviceGroup.add(Name=dg_name, Multiplier=multi)
        ethernet1 = deviceGroup1.Ethernet.add(Name='Eth1')
        ethernet1.Mac.Increment(start_value=mac_start, step_value='00:00:00:00:00:01')
        #vlan can not be used in FSW, dont know why. need to investigate
        # ethernet1.EnableVlans.Single(True)

        # ixNetwork.info('Configuring vlanID')
        # vlanObj = ethernet1.Vlan.find()[0].VlanId.Increment(start_value=vlan_id, step_value=0)
        return ethernet1
    except Exception as errMsg:
        print('\n%s' % traceback.format_exc(None, errMsg))
        if debugMode == False and 'session' in locals():
            session.remove()
        return False

def ixia_rest_create_ip(*args,**kwargs):
    debugMode = False
    try:
        ixNetwork = kwargs['session']
        start_ip = kwargs['start_ip']
        gw_start_ip = kwargs['gw_start_ip']
        ethernet = kwargs['ethernet']

        ixNetwork.info('Configuring IPv4')
        ipv4 = ethernet.Ipv4.add(Name='Ipv4')
        ipv4.Address.Increment(start_value=start_ip, step_value='0.0.0.1')
        #ipv4.address.RandomMask(mask_value=16)
        print(dir(ipv4.Address))
        ipv4.GatewayIp.Increment(start_value=gw_start_ip, step_value='0.0.0.1')
        return ipv4
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
    ixNetwork = kwargs['session']
    ixNetwork.StartAllProtocols(Arg1='sync')

    ixNetwork.info('Verify protocol sessions\n')
    protocolsSummary = StatViewAssistant(ixNetwork, 'Protocols Summary')
    protocolsSummary.CheckCondition('Sessions Not Started', StatViewAssistant.EQUAL, 0)
    protocolsSummary.CheckCondition('Sessions Down', StatViewAssistant.EQUAL, 0)
    ixNetwork.info(protocolsSummary)

    #     ixNetwork.info('Create Traffic Item')
    #     trafficItem = ixNetwork.Traffic.TrafficItem.add(Name='BGP Traffic', BiDirectional=False, TrafficType='ipv4')

    #     ixNetwork.info('Add endpoint flow group')
    #     trafficItem.EndpointSet.add(Sources=topology1, Destinations=topology2)

    #     # Note: A Traffic Item could have multiple EndpointSets (Flow groups).
    #     #       Therefore, ConfigElement is a list.
    #     ixNetwork.info('Configuring config elements')
    #     configElement = trafficItem.ConfigElement.find()[0]
    #     configElement.FrameRate.update(Type='percentLineRate', Rate=50)
    #     configElement.TransmissionControl.update(Type='fixedFrameCount', FrameCount=10000)
    #     configElement.FrameRateDistribution.PortDistribution = 'splitRateEvenly'
    #     configElement.FrameSize.FixedSize = 128
    #     trafficItem.Tracking.find()[0].TrackBy = ['flowGroup0']

    #     trafficItem.Generate()
    #     ixNetwork.Traffic.Apply()
    #     ixNetwork.Traffic.Start()

    #     # StatViewAssistant could also filter by REGEX, LESS_THAN, GREATER_THAN, EQUAL. 
    #     # Examples:
    #     #    flowStatistics.AddRowFilter('Port Name', StatViewAssistant.REGEX, '^Port 1$')
    #     #    flowStatistics.AddRowFilter('Tx Frames', StatViewAssistant.LESS_THAN, 50000)

    #     flowStatistics = StatViewAssistant(ixNetwork, 'Flow Statistics')
    #     ixNetwork.info('{}\n'.format(flowStatistics))

    #     for rowNumber,flowStat in enumerate(flowStatistics.Rows):
    #         ixNetwork.info('\n\nSTATS: {}\n\n'.format(flowStat))
    #         ixNetwork.info('\nRow:{}  TxPort:{}  RxPort:{}  TxFrames:{}  RxFrames:{}\n'.format(
    #             rowNumber, flowStat['Tx Port'], flowStat['Rx Port'],
    #             flowStat['Tx Frames'], flowStat['Rx Frames']))

    #     flowStatistics = StatViewAssistant(ixNetwork, 'Traffic Item Statistics')
    #     ixNetwork.info('{}\n'.format(flowStatistics))

    #     if debugMode == False:
    #         # For linux and connection_manager only
    #         session.remove()

    # except Exception as errMsg:
    #     print('\n%s' % traceback.format_exc(None, errMsg))
    #     if debugMode == False and 'session' in locals():
    #         session.remove()



if __name__ == "__main__":
    apiServerIp = '10.105.19.19'
    ixChassisIpList = ['10.105.241.234']
    
    portList = [[ixChassisIpList[0], 4,15], [ixChassisIpList[0], 4, 16]]
    ixNetwork,vport_holder_list = ixia_rest_connect_chassis(apiServerIp,ixChassisIpList,portList)
    if ixNetwork == False:
        print(f"Error connected to IXIA chassis {ixChassisIpList}")
        exit()
    ethernet_session = ixia_rest_create_topology(
        session = ixNetwork,
        vport = vport_holder_list[0],
        topo_name = "Topology_1",   
        dg_name = "DG1",    
        multiplier = 1000,    
        mac_start = "00:11:01:01:01:01",
        vlan_id = 1
    )     

    if ethernet_session == False:
        print(f"Error creating topology on chassis {ixChassisIpList} port {vport_holder_list[0]}")
        exit()
    ip_session = ixia_rest_create_ip(
        session = ixNetwork,
        start_ip = "10.1.1.1",
        gw_start_ip = "10.2.1.1",
        ethernet = ethernet_session,
    )

    ethernet_session = ixia_rest_create_topology(
        session = ixNetwork,
        vport = vport_holder_list[1],
        topo_name = "Topology_2",   
        dg_name = "DG2",    
        multiplier = 1000,    
        mac_start = "00:12:01:01:01:01",
        vlan_id = 1
    )     

    if ethernet_session == False:
        print(f"Error creating topology on chassis {ixChassisIpList} port {vport_holder_list[0]}")
        exit()
    ip_session = ixia_rest_create_ip(
        session = ixNetwork,
        start_ip = "10.2.1.1",
        gw_start_ip = "10.1.1.1",
        ethernet = ethernet_session,
    )

    ixia_rest_start_protocols(session = ixNetwork)
    
