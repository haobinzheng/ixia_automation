 
import sys, os, time, traceback
from utils import *

# Import the RestPy module
from ixnetwork_restpy.testplatform.testplatform import TestPlatform
from ixnetwork_restpy.assistants.statistics.statviewassistant import StatViewAssistant

"""
bgpiprouteproperty = ipv4prefixpools.BgpIPRouteProperty.add(AdvertiseAsBgp3107=None, AdvertiseAsBgp3107Sr=None, AdvertiseAsRfc8277=None, Name=None, NoOfASPathSegmentsPerRouteRange=None, NoOfClusters=None, NoOfCommunities=None, NoOfExternalCommunities=None, NoOfLabels=None, NoOfLargeCommunities=None, NoOfTlvs=None)
enableaspathsegments = bgpiprouteproperty.EnableAsPathSegments
testplatform.info(enableaspathsegments)


bgpiprouteproperty = ipv4prefixpools.BgpIPRouteProperty.add(AdvertiseAsBgp3107=None, AdvertiseAsBgp3107Sr=None, AdvertiseAsRfc8277=None, Name=None, NoOfASPathSegmentsPerRouteRange=None, NoOfClusters=None, NoOfCommunities=None, NoOfExternalCommunities=None, NoOfLabels=None, NoOfLargeCommunities=None, NoOfTlvs=None)
maxnoofaspathsegmentsperrouterange = bgpiprouteproperty.MaxNoOfASPathSegmentsPerRouteRange
testplatform.info(maxnoofaspathsegmentsperrouterange)


"""

class IXIA_TOPOLOGY:
    def __init__(self,*args,**kwargs):
        self.ixia = args[0]
        self.port = args[1]
        self.name=kwargs['name']
        self.dg_name = kwargs['dg_name']
        self.mac_start = kwargs['mac_start']
        self.network = kwargs['network']
        self.bgp_as = kwargs['local_as']
        self.bgp_name = f"BGP_{self.name}"
        self.ip,self.mask = seperate_ip_mask(kwargs['ip'])
        self.gw= kwargs['gw']
        self.ethernet,self.device_group,self.topology = ixia_rest_create_topology(
        platform = self.ixia.testPlatform, 
        session = self.ixia.Session,
        ixnet = self.ixia.ixNetwork,
        vport = self.port,
        topo_name = self.name,   
        dg_name = self.dg_name,    
        multiplier = 1,    
        mac_start = self.mac_start,
        )     

    def add_ipv4(self,*args,**kwargs):
        # ip = kwargs['ip']
        # gw = kwargs['gw']
        # mask = kwargs['mask']
        self.ip_session = ixia_rest_create_ip(
        platform = self.ixia.testPlatform, 
        session = self.ixia.Session,
        ixnet = self.ixia.ixNetwork,
        start_ip = self.ip,
        gw_start_ip = self.gw,
        ethernet = self.ethernet,
        maskbits = self.mask,
    )

    def add_bgp(self,*args,**kwargs):
        dut_ip = kwargs['dut_ip']
        bgp_type = kwargs['bgp_type']
        num = kwargs['num']
        self.bgp = ixia_rest_create_bgp(
            platform = self.ixia.testPlatform,
            ixnet = self.ixia.ixNetwork,
            name = self.bgp_name,
            peer_ip = dut_ip,
            type = bgp_type,
            local_as = self.bgp_as,
            networks_number = num,
            networks_start_ip =self.network ,
            device_group = self.device_group,
            ip = self.ip_session,
        )

class IXIA:
    def __init__(self,*args,**kargs):
        self.apiServerIp = args[0]
        self.ixChassisIpList = args[1]
        self.portList = args[2]
        self.testPlatform,self.Session,self.ixNetwork,self.vport_holder_list = ixia_rest_connect_chassis(self.apiServerIp,self.ixChassisIpList,self.portList)
        #self.create_topologies()
        self.topologies = self.create_topologies()
         
    def create_topologies(self):
        i = 0
        bgp_as = 101
        topo_list = []
        for port in self.vport_holder_list:
            print(self.portList[i][3])
            topo = IXIA_TOPOLOGY(self,port,name=f"Topology_{i+1}",dg_name=f"DG{i}",
                mac_start=self.portList[i][3],local_as = self.portList[i][5],network=self.portList[i][4],ip=self.portList[i][6],gw=self.portList[i][7])
            topo_list.append(topo)
            i += 1
            bgp_as += 1 
        return topo_list

    def create_traffic(self,*args,**kwargs):
        src_topo = kwargs['src_topo']
        dst_topo = kwargs['dst_topo']
        traffic_name = kwargs['traffic_name']
        tracking_name = kwargs['tracking_name']
        ixia_rest_create_traffic(
        platform = self.testPlatform, 
        session = self.Session,
        ixnet = self.ixNetwork,
        src = src_topo,
        dst = dst_topo,
        name= traffic_name,
        tracking_group = tracking_name,
    )

    def start_traffic(self):

        ixia_rest_start_traffic(
        platform = self.testPlatform, 
        session = self.Session,
        ixnet = self.ixNetwork,
        )

    def collect_stats(self):
        self.flow_stats_list = ixia_rest_collect_stats(
        platform = self.testPlatform, 
        session = self.Session,
        ixnet = self.ixNetwork, 
    )

    def check_traffic(self):
        if check_traffic(self.flow_stats_list) == False:
            tprint("========================= Failed: significant traffic loss ============")
        else:
            tprint("========================= Passed: traffic is passed without loss ============")


    def start_protocol(self,*args, **kwargs):
        wait_time = kwargs['wait']
        ixia_rest_start_protocols(
            platform = self.testPlatform, 
            session = self.Session,
            ixnet = self.ixNetwork,
            wait = 40,
        )


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
        #vlan_id = kwargs['vlan_id']       
        ixNetwork.info(f'Creating Topology Group {topo_name}')
        topology = ixNetwork.Topology.add(Name=topo_name, Ports=vport)
        deviceGroup = topology.DeviceGroup.add(Name=dg_name, Multiplier=multi)
        ethernet = deviceGroup.Ethernet.add(Name=topo_name)
        ethernet.Mac.Increment(start_value=mac_start, step_value='00:00:00:00:00:01')
        #vlan can not be used in FSW, dont know why. need to investigate
        # ethernet1.EnableVlans.Single(True)

        # ixNetwork.info('Configuring vlanID')
        # vlanObj = ethernet1.Vlan.find()[0].VlanId.Increment(start_value=vlan_id, step_value=0)
        return ethernet,deviceGroup,topology
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
    if "wait" in kwargs:
        wait_time = int(kwargs['wait'])
    else:
        wait_time = 60
    try_counter = 0
    while try_counter < 2:
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
            try_counter += 1
            if debugMode == False and 'session' in locals():
                wait_time += 10

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
        configElement.FrameRate.update(Type='percentLineRate', Rate=15)
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
            flowStat_dict['Tx Frames'] = int(flowStat['Tx Frames'])
            flowStat_dict['Rx Frames'] = int(flowStat['Rx Frames'])
            flowStat_dict["Frames Delta"] = int(flowStat["Frames Delta"])
            flowStat_dict["Tx Rate (Bps)"] = (flowStat["Tx Rate (Bps)"])
            flowStat_dict['Traffic Item'] =  flowStat['Traffic Item']
            flowStat_dict['Flow Group'] =    flowStat['Flow Group']
            flowStat_dict['Tx Frame Rate'] = (flowStat['Tx Frame Rate'])
            flowStat_dict['Tx Rate (bps)'] = (flowStat['Tx Rate (bps)'])
            flow_stats_list.append(flowStat_dict)

        print(flow_stats_list)
        return flow_stats_list

        # flowStatistics = StatViewAssistant(ixNetwork, 'Traffic Item Statistics')
        # ixNetwork.info('{}\n'.format(flowStatistics))
    except Exception as errMsg:
        print('\n%s' % traceback.format_exc(None, errMsg))
        if debugMode == False and 'session' in locals():
            session.remove()

def check_traffic(flow_stats_list):
    for flow in flow_stats_list:
        if flow["Frames Delta"] > 20:
            return False
    return True


def ixia_rest_create_bgp(*args,**kwargs):
    testplatform = kwargs['platform']
    bgp_name = kwargs['name']
    bgp_peer_ip = kwargs['peer_ip']
    bgp_type = kwargs['type']  #Either internal or external
    local_as = kwargs['local_as'] 
    network_group_number = kwargs['networks_number']
    network_start_address = kwargs['networks_start_ip']
    device_group = kwargs['device_group']
    ipv4 = kwargs['ip']
    ixNetwork = kwargs['ixnet']

    network_group_name = f"{bgp_name}-routes"
    ixNetwork.info(f'Configuring BgpIpv4Peer {bgp_name}')
    bgp2 = ipv4.BgpIpv4Peer.add(Name=bgp_name)
    bgp2.DutIp.Increment(start_value=bgp_peer_ip, step_value='0.0.0.0')
    bgp2.Type.Single(bgp_type)
    #bgp2.Type.Single('external')
    bgp2.LocalAs2Bytes.Increment(start_value=local_as, step_value=0)
    # bgp2.RemoteAs2Bytes.Increment(start_value=65000, step_value=0)

    ixNetwork.info(f'Configuring Network Group {bgp_name}')
    networkGroup = device_group.NetworkGroup.add(Name=network_group_name, Multiplier=network_group_number)
    ipv4PrefixPool = networkGroup.Ipv4PrefixPools.add(NumberOfAddresses='1')
    ipv4PrefixPool.NetworkAddress.Increment(start_value=network_start_address, step_value='0.0.0.1')
    ipv4PrefixPool.PrefixLength.Single(32)

    ixia_rest_add_as_path(pool=ipv4PrefixPool,num_path=6, as_base=65000)
    

def ixia_rest_add_as_path(*args,**kwargs):
    ipv4PrefixPool = kwargs['pool']
    num_path = kwargs['num_path']
    as_start_num = kwargs['as_base']

    bgpiprouteproperty = ipv4PrefixPool.BgpIPRouteProperty.add(NoOfASPathSegmentsPerRouteRange=num_path)
    bgpiprouteproperty.EnableAsPathSegments.Single("True")
     

    bgpaspathsegmentlist = bgpiprouteproperty.BgpAsPathSegmentList.find()
    bgpaspathsegmentlist.EnableASPathSegment.Single("True")
    
    #print(f"type of bgpaspathsegmentlist = {type(bgpaspathsegmentlist)}")
    i = 0
    for seg in bgpaspathsegmentlist:
        bgpasnumberlist = seg.BgpAsNumberList.find()
        bgpasnumberlist.AsNumber.Single(as_start_num+i)
        i += 1 

 
if __name__ == "__main__":
    apiServerIp = '10.105.19.19'
    ixChassisIpList = ['10.105.241.234']
    
    #chassis_ip, module,port,mac,bgp_network,bgp_as,ip_address/mask, gateway
    portList = [[ixChassisIpList[0], 1,1,"00:11:01:01:01:01","10.10.1.1",101,"10.1.1.101/24","10.1.1.1"], 
    [ixChassisIpList[0], 1, 2,"00:12:01:01:01:01","10.20.1.1",102,"10.1.1.102/24","10.1.1.1"],
    [ixChassisIpList[0], 1, 3,"00:13:01:01:01:01","10.30.1.1",103,"10.1.1.103/24","10.1.1.1"],
    [ixChassisIpList[0], 1, 4,"00:14:01:01:01:01","10.40.1.1",104,"10.1.1.104/24","10.1.1.1"], 
    [ixChassisIpList[0], 1, 5,"00:15:01:01:01:01","10.50.1.1",105,"10.1.1.105/24","10.1.1.1"],
    [ixChassisIpList[0], 1, 6,"00:16:01:01:01:01","10.60.1.1",106,"10.1.1.106/24","10.1.1.1"]]
    myixia = IXIA(apiServerIp,ixChassisIpList,portList)
    

    # myixia.topologies[0].add_ipv4(ip='10.1.1.101',gw='10.1.1.1',mask=24)
    # myixia.topologies[1].add_ipv4(ip='10.1.1.102',gw='10.1.1.1',mask=24)
    # myixia.topologies[2].add_ipv4(ip='10.1.1.103',gw='10.1.1.1',mask=24)
    # myixia.topologies[3].add_ipv4(ip='10.1.1.104',gw='10.1.1.1',mask=24)
    # myixia.topologies[4].add_ipv4(ip='10.1.1.105',gw='10.1.1.1',mask=24)
    # myixia.topologies[5].add_ipv4(ip='10.1.1.106',gw='10.1.1.1',mask=24)

    myixia.topologies[0].add_ipv4()
    myixia.topologies[1].add_ipv4()
    myixia.topologies[2].add_ipv4()
    myixia.topologies[3].add_ipv4()
    myixia.topologies[4].add_ipv4()
    myixia.topologies[5].add_ipv4()


    myixia.topologies[0].add_bgp(dut_ip='10.1.1.1',bgp_type='external',num=100)
    myixia.topologies[1].add_bgp(dut_ip='10.1.1.2',bgp_type='external',num=100)
    myixia.topologies[2].add_bgp(dut_ip='10.1.1.3',bgp_type='external',num=100)
    myixia.topologies[3].add_bgp(dut_ip='10.1.1.4',bgp_type='external',num=100)
    myixia.topologies[4].add_bgp(dut_ip='10.1.1.5',bgp_type='external',num=100)
    myixia.topologies[5].add_bgp(dut_ip='10.1.1.6',bgp_type='external',num=100)


    myixia.start_protocol(wait=40)

    myixia.create_traffic(src_topo=myixia.topologies[0].topology, dst_topo=myixia.topologies[1].topology,traffic_name="t1_to_t2",tracking_name="Tracking_1")
    myixia.create_traffic(src_topo=myixia.topologies[1].topology, dst_topo=myixia.topologies[0].topology,traffic_name="t2_to_t1",tracking_name="Tracking_2")

    myixia.create_traffic(src_topo=myixia.topologies[2].topology, dst_topo=myixia.topologies[3].topology,traffic_name="t2_to_t3",tracking_name="Tracking_3")
    myixia.create_traffic(src_topo=myixia.topologies[3].topology, dst_topo=myixia.topologies[2].topology,traffic_name="t3_to_t2",tracking_name="Tracking_4")

    myixia.create_traffic(src_topo=myixia.topologies[4].topology, dst_topo=myixia.topologies[5].topology,traffic_name="t4_to_t5",tracking_name="Tracking_5")
    myixia.create_traffic(src_topo=myixia.topologies[5].topology, dst_topo=myixia.topologies[4].topology,traffic_name="t5_to_t4",tracking_name="Tracking_6")


    myixia.start_traffic()
    myixia.collect_stats()
    myixia.check_traffic()
    
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
