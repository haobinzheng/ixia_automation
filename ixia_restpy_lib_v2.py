
import sys, os, time, traceback
from utils import *

# Import the RestPy module
from ixnetwork_restpy.testplatform.testplatform import TestPlatform
from ixnetwork_restpy.assistants.statistics.statviewassistant import StatViewAssistant


class IXIA_TOPOLOGY:
    def __init__(self,*args,**kwargs):
        self.ixia = args[0]
        self.port = args[1]
        self.name=kwargs['name']
        self.dg_name = kwargs['dg_name']
        self.mac_start = kwargs['mac_start']
        # self.network = kwargs['network']
        # self.bgp_as = kwargs['local_as']
        # self.bgp_name = f"BGP_{self.name}"
        self.ipv4,self.ipv4_mask = seperate_ip_mask(kwargs['ipv4'])
        self.ipv6,self.ipv6_mask = seperate_ip_mask(kwargs['ipv6'])
        self.ipv4_gw= kwargs['ipv4_gw']
        self.ipv6_gw= kwargs['ipv6_gw']
        self.ip_session = None #will be created at add_ipv4 method
        self.ptp_name = self.name + "_ptp"
        self.ether_name = kwargs['ether_name']
        self.ipv4_name = kwargs['ipv4_name']
        self.ipv6_name = kwargs['ipv6_name']
        self.dhcp_client_name = kwargs['dhcp_client_name']
        self.dhcp_server_name = kwargs['dhcp_server_name']
        self.ipv4_session = None
        self.ipv6_session = None
        self.multiplier = kwargs['multiplier']
        self.ethernet,self.device_group,self.topology = ixia_rest_create_topology(
        platform = self.ixia.testPlatform, 
        session = self.ixia.Session,
        ixnet = self.ixia.ixNetwork,
        vport = self.port,
        topo_name = self.name,   
        dg_name = self.dg_name,
        ether_name = self.ether_name,
        multiplier = self.multiplier,    
        mac_start = self.mac_start
        )     


    def add_ipv6(self,*args,**kwargs):
        # ip = kwargs['ip']
        # gw = kwargs['gw']
        # mask = kwargs['mask']
        self.ipv6_session = ixia_rest_create_ipv6(
        platform = self.ixia.testPlatform, 
        session = self.ixia.Session,
        ixnet = self.ixia.ixNetwork,
        start_ip = self.ipv6,
        gw_start_ip = self.ipv6_gw,
        ethernet = self.ethernet,
        maskbits = self.ipv6_mask,
        ip_name = self.ipv6_name
    )

    def add_ipv4(self,*args,**kwargs):
        # ip = kwargs['ip']
        # gw = kwargs['gw']
        # mask = kwargs['mask']
        self.ipv4_session = ixia_rest_create_ip(
        platform = self.ixia.testPlatform, 
        session = self.ixia.Session,
        ixnet = self.ixia.ixNetwork,
        start_ip = self.ipv4,
        gw_start_ip = self.ipv4_gw,
        ethernet = self.ethernet,
        maskbits = self.ipv4_mask,
        ip_name = self.ipv4_name
    )

    def add_ptp(self,*args,**kwargs):
        self.ptp = ixia_rest_create_ptp(
            platform = self.ixia.testPlatform,
            ixnet = self.ixia.ixNetwork,
            name = self.ptp_name,
            ip = self.ipv4_session,
        )

    def add_dhcp_client(self,*args,**kwargs):
        self.dhcp_client = ixia_rest_create_dhcp_client(
            session = self.ixia.Session,
            platform = self.ixia.testPlatform,
            ixnet = self.ixia.ixNetwork,
            ethernet = self.ethernet,
            name = self.dhcp_client_name
            )

    def add_dhcp_server(self,*args,**kwargs):
        self.dhcp_server = ixia_rest_create_dhcp_server(
            ip_session = self.ipv4_session,
            session = self.ixia.Session,
            platform = self.ixia.testPlatform,
            ixnet = self.ixia.ixNetwork,
            ethernet = self.ethernet,
            name = self.dhcp_server_name
            )
    def dhcp_server_gw(self,*args,**kwargs):
        if "gateway" in kwargs:
            gateway = kwargs['gateway']
        else:
            gateway = self.ipv4
        ixia_rest_dhcp_server_gw(
            dhcp_server = self.dhcp_server,
            session = self.ixia.Session,
            platform = self.ixia.testPlatform,
            ixnet = self.ixia.ixNetwork,     
            ip_gw = gateway
        )

    def dhcp_server_pool_size(self,*args,**kwargs):
        pool_size = kwargs['pool_size']
        ixia_rest_dhcp_server_pool_size(
            dhcp_server = self.dhcp_server,
            session = self.ixia.Session,
            platform = self.ixia.testPlatform,
            ixnet = self.ixia.ixNetwork,     
            pool_size= pool_size
        )

    def dhcp_server_address(self,*args,**kwargs):
        if "prefix" in kwargs:
            prefix = kwargs['prefix']
        else:
            prefix = "24"
        ixia_rest_dhcp_server_address(
            dhcp_server = self.dhcp_server,
            session = self.ixia.Session,
            platform = self.ixia.testPlatform,
            ixnet = self.ixia.ixNetwork,     
            start_ip = kwargs['start_ip'],
            prefix = prefix
        )


    def dhcp_server_pool_size_v6(self,*args,**kwargs):
        pool_size = kwargs['pool_size']
        ixia_rest_dhcp_server_pool_size_v6(
            dhcp_server = self.dhcp_server,
            session = self.ixia.Session,
            platform = self.ixia.testPlatform,
            ixnet = self.ixia.ixNetwork,     
            pool_size= pool_size
        )

    def add_dhcp_client_v6(self,*args,**kwargs):
        self.dhcp_client = ixia_rest_create_dhcp_client_v6(
            session = self.ixia.Session,
            platform = self.ixia.testPlatform,
            ixnet = self.ixia.ixNetwork,
            ethernet = self.ethernet,
            name = self.dhcp_client_name
            )
    def add_dhcp_server_v6(self,*args,**kwargs):
        self.dhcp_server = ixia_rest_create_dhcp_server_v6(
            ip_session = self.ipv6_session,
            session = self.ixia.Session,
            platform = self.ixia.testPlatform,
            ixnet = self.ixia.ixNetwork,
            ethernet = self.ethernet,
            name = self.dhcp_server_name
            )

    def dhcp_server_gw_v6(self,*args,**kwargs):
        if "gateway" in kwargs:
            gateway = kwargs['gateway']
        else:
            gateway = self.ipv6
        ixia_rest_dhcp_server_gw_v6(
            dhcp_server = self.dhcp_server,
            session = self.ixia.Session,
            platform = self.ixia.testPlatform,
            ixnet = self.ixia.ixNetwork,     
            ip_gw = gateway
        )


    def dhcp_server_address_v6(self,*args,**kwargs):
        if "prefix" in kwargs:
            prefix = kwargs['prefix']
        else:
            prefix = "24"
        ixia_rest_dhcp_server_address_v6(
            dhcp_server = self.dhcp_server,
            session = self.ixia.Session,
            platform = self.ixia.testPlatform,
            ixnet = self.ixia.ixNetwork,     
            start_ip = kwargs['start_ip'],
            prefix = prefix
        )

    def add_bgp(self,*args,**kwargs):
        dut_ip = kwargs['dut_ip']
        bgp_type = kwargs['bgp_type']
        num = kwargs['num']
        self.bgp,self.network_group, self.ipv4_pool = ixia_rest_create_bgp(
            platform = self.ixia.testPlatform,
            ixnet = self.ixia.ixNetwork,
            name = self.bgp_name,
            peer_ip = dut_ip,
            type = bgp_type,
            local_as = self.bgp_as,
            networks_number = num,
            networks_start_ip =self.network ,
            device_group = self.device_group,
            ip = self.ipv4_session,
        )

    def change_origin(self,code):
        ixia_rest_set_origin(pool=self.ipv4_pool, origin=code,platform=self.ixia.testPlatform)

    def change_med(self,med_value):
        ixia_rest_set_med(pool=self.ipv4_pool,med=med_value, platform=self.ixia.testPlatform)

    def change_local_pref(self,value):
        ixia_rest_set_local_pref(pool=self.ipv4_pool,local=value, platform=self.ixia.testPlatform)

    def add_aspath(self,num,base):
        ixia_rest_add_as_path(pool=self.ipv4_pool,num_path=num,as_base=base)

    def add_aspath_med(self,num,base,med_value):
        ixia_rest_change_route_properties(pool=self.ipv4_pool,num_path=num,as_base=base,med=med_value)

    def change_bgp_routes_attributes(self,*args, **kwargs):
        ipv4PrefixPool = self.ipv4_pool
        testplatform = self.ixia.testPlatform

    # bgpiprouteproperty = ipv4PrefixPool.BgpIPRouteProperty
    # bgpiprouteproperty.update(NoOfASPathSegmentsPerRouteRange=num_path)
        bgpiprouteproperty = ipv4PrefixPool.BgpIPRouteProperty.add()
        if "num_path" in kwargs:
            num_path = kwargs['num_path']
            as_start_num = kwargs['as_base']
            bgpiprouteproperty.update(NoOfASPathSegmentsPerRouteRange=num_path)
            bgpiprouteproperty.EnableAsPathSegments.Single("True")
             
            bgpaspathsegmentlist = bgpiprouteproperty.BgpAsPathSegmentList.find()
            bgpaspathsegmentlist.EnableASPathSegment.Single("True")
            
            #print(f"type of bgpaspathsegmentlist = {type(bgpaspathsegmentlist)}")
            i = 0
            for seg in bgpaspathsegmentlist:
                bgpasnumberlist = seg.BgpAsNumberList.find()
                bgpasnumberlist.AsNumber.Single(as_start_num+i)
                i += 1 
        if "community" in kwargs:
            typecode = "ixnetwork_restpy.errors.BadRequestError: Valid enum values are 0=noexport 1=noadvertised 2=noexport_subconfed 3=manual 4=llgr_stale 5=no_llgr"
            num_comm = kwargs['community']
            comm_start_num = kwargs['comm_base']
            bgpiprouteproperty.update(NoOfCommunities=num_comm)
            bgpiprouteproperty.EnableCommunity.Single("True")
             
            bgpcommunitieslist = bgpiprouteproperty.BgpCommunitiesList.find()
            #bgpcommunitieslist.EnableCommunity.Single("True")
            
            #print(f"type of bgpaspathsegmentlist = {type(bgpaspathsegmentlist)}")
            i = 0
            for comm in bgpcommunitieslist:
                i+=1
                comm.AsNumber.Single(comm_start_num)
                comm.LastTwoOctets.Single(i)
                comm.Type.Single("manual")
        if "med" in kwargs:
            med = kwargs['med']
            bgpiprouteproperty.EnableMultiExitDiscriminator.Single("True")
            bgpiprouteproperty.MultiExitDiscriminator.Single(med)
        if "local" in kwargs:
            local = kwargs['local']
            bgpiprouteproperty.EnableLocalPreference.Single("True")
            bgpiprouteproperty.LocalPreference.Single(local)

        if "origin" in kwargs:
            origin = kwargs['origin']
            bgpiprouteproperty.Origin.Single(origin)
        if "flapping" in kwargs:
            start_ip = kwargs["flapping"]
            if start_ip.upper() == "RANDOM":
                bgpiprouteproperty.EnableFlapping.Random()
            else:
                bgpiprouteproperty.EnableFlapping.Increment(start_value=start_ip, step_value='0.0.0.1')
        if "weight" in kwargs:
            value = kwargs['weight']
            bgpiprouteproperty.Weight.Single(value)
         
        

# portList = [[ixChassisIpList[0], 8,13,"00:11:01:01:01:01","10.10.1.100/24","10.10.1.254"], 

class IXIA:
    def __init__(self,*args,**kwargs):
        self.apiServerIp = args[0]
        self.ixChassisIpList = args[1]
        self.portList = args[2]
        # self.protocol = kwargs["protocol"]
        self.testPlatform,self.Session,self.ixNetwork,self.vport_holder_list = ixia_rest_connect_chassis(self.apiServerIp,self.ixChassisIpList,self.portList)
        #self.create_topologies()
        self.topologies = self.create_topologies()
         
    def create_topologies(self):
        i = 0
        bgp_as = 101
        topo_list = []
        for port in self.vport_holder_list:
            print(self.portList[i][3])
            topo = IXIA_TOPOLOGY(self,port,
                name=f"Topology_{i+1}",
                dg_name=f"DG{i+1}",
                ether_name=f"Ethernet_{i+1}",
                ipv4_name=f"IPv4_{i+1}",
                ipv6_name=f"IPv6_{i+1}",
                dhcp_client_name=f"DHCP_Client_{i+1}",
                dhcp_server_name=f"DHCP_Server_{i+1}",
                mac_start=self.portList[i][3],
                ipv4= self.portList[i][4],
                ipv4_gw= self.portList[i][5],
                ipv6=self.portList[i][6],
                ipv6_gw=self.portList[i][7],
                multiplier=self.portList[i][8],
            )
            topo_list.append(topo)
            i += 1
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

    def stop_traffic(self):

        ixia_rest_stop_traffic(
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

    def clear_stats(self):
        self.flow_stats_list = ixia_rest_clear_stats(
        platform = self.testPlatform, 
        session = self.Session,
        ixnet = self.ixNetwork, 
    )
    def check_traffic(self):
        if check_traffic(self.flow_stats_list) == False:
            tprint("========================= Failed: significant traffic loss ============")
            return False
        else:
            tprint("========================= Passed: traffic is passed without packet loss ============")
            return True


    def start_protocol(self,*args, **kwargs):
        wait_time = kwargs['wait']
        ixia_rest_start_protocols(
            platform = self.testPlatform, 
            session = self.Session,
            ixnet = self.ixNetwork,
            wait = 40,
        )

    def stop_protocol(self,*args, **kwargs):
        wait_time = kwargs['wait']
        ixia_rest_stop_protocols(
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
            print(f"server ip = {apiServerIp}")
            testPlatform = TestPlatform(ip_address=apiServerIp,log_file_name='restpy.log')
            # testPlatform = TestPlatform(ip_address=apiServerIp,rest_port=62428,log_file_name='restpy.log')

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
        ether_name = kwargs['ether_name']
        #vlan_id = kwargs['vlan_id']       
        ixNetwork.info(f'Creating Topology Group {topo_name}')
        topology = ixNetwork.Topology.add(Name=topo_name, Ports=vport)
        deviceGroup = topology.DeviceGroup.add(Name=dg_name, Multiplier=multi)
        ethernet = deviceGroup.Ethernet.add(Name=ether_name)
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
        ip_name = kwargs['ip_name']

        ixNetwork.info('Configuring IPv4')
        ipv4 = ethernet.Ipv4.add(Name=ip_name)
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

def ixia_rest_create_ipv6(*args,**kwargs):
    debugMode = False
    try:
        session = kwargs['session']
        testPlatform = kwargs['platform']
        ixNetwork = kwargs['ixnet']
        start_ip = kwargs['start_ip']
        gw_start_ip = kwargs['gw_start_ip']
        ethernet = kwargs['ethernet']
        ip_prefix = kwargs['maskbits']
        ip_name = kwargs['ip_name']

        ixNetwork.info('Configuring IPv6')
        ipv6 = ethernet.Ipv6.add(Name=ip_name)
        ipv6.Address.Increment(start_value=start_ip, step_value='::1')
        # ipv4.address.RandomMask(fixed_value=16)
        print(dir(ipv6.Address))
        ipv6.GatewayIp.Increment(start_value=gw_start_ip, step_value='::1')
        ipv6.Prefix.Single(ip_prefix)
        address = ipv6.Address
        # testPlatform.info(address.prefix)
        return ipv6
    except Exception as errMsg:
        print('\n%s' % traceback.format_exc(None, errMsg))
        if debugMode == False and 'session' in locals():
            session.remove()
        return False

def ixia_rest_create_dhcp_client_v6(*args,**kwargs):
    debugMode = False
    try:
        session = kwargs['session']
        testPlatform = kwargs['platform']
        ixNetwork = kwargs['ixnet']
        ethernet = kwargs['ethernet']
        name = kwargs['name']
         

        ixNetwork.info('Configuring IPv6 Dhcpv6client')

        #dhcpv4client = ethernet.Dhcpv4client.add(Multiplier=None, Name=None, StackedLayers=None)
        dhcpv6client = ethernet.Dhcpv6client.add(Name=name)
        testPlatform.info(dhcpv6client)
        
        # testPlatform.info(address.prefix)
        return dhcpv6client
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
        name = kwargs['name']
         

        ixNetwork.info('Configuring IPv4 Dhcpv4client')

        #dhcpv4client = ethernet.Dhcpv4client.add(Multiplier=None, Name=None, StackedLayers=None)
        dhcpv4client = ethernet.Dhcpv4client.add(Name=name)
        testPlatform.info(dhcpv4client)
        
        # testPlatform.info(address.prefix)
        return dhcpv4client
    except Exception as errMsg:
        print('\n%s' % traceback.format_exc(None, errMsg))
        if debugMode == False and 'session' in locals():
            session.remove()
        return False

def ixia_rest_create_dhcp_server_v6(*args,**kwargs):
    debugMode = False
    try:
        ip_session = kwargs['ip_session']
        session = kwargs['session']
        testPlatform = kwargs['platform']
        ixNetwork = kwargs['ixnet']
        ethernet = kwargs['ethernet']
        name = kwargs['name']
         

        ixNetwork.info('Configuring IPv6 Dhcpv6server')

        dhcpv4server = ip_session.Dhcpv6server.add(Name=name)
        testPlatform.info(dhcpv4server)
        
        return dhcpv4server
    except Exception as errMsg:
        print('\n%s' % traceback.format_exc(None, errMsg))
        if debugMode == False and 'session' in locals():
            session.remove()
        return False

def ixia_rest_dhcp_server_gw_v6(*args,**kwargs):
    debugMode = False
    try:
        dhcp_server = kwargs['dhcp_server']
        testPlatform = kwargs['platform']
        ixNetwork = kwargs['ixnet']
        ip_gw = kwargs['ip_gw']

        ixNetwork.info('Configuring IPv4 Dhcpv4sver IP Gateway')
        dhcp_server.Dhcp6ServerSessions.IpGateway.Single(ip_gw)
        testPlatform.info(dhcp_server.Dhcp6ServerSessions.IpGateway)
    except Exception as errMsg:
        print('\n%s' % traceback.format_exc(None, errMsg))
        if debugMode == False and 'session' in locals():
            session.remove()
        return False


def ixia_rest_dhcp_server_address_v6(*args,**kwargs):
    debugMode = False
    try:
        dhcp_server = kwargs['dhcp_server']
        testPlatform = kwargs['platform']
        ixNetwork = kwargs['ixnet']
        start_ip = kwargs['start_ip']
        prefix = kwargs['prefix']

        ixNetwork.info('Configuring IPv6 Dhcpv6sver IP Gateway')
        dhcp_server.Dhcp6ServerSessions.IpAddress.Increment(start_value=start_ip, step_value="::1")
        testPlatform.info(dhcp_server.Dhcp6ServerSessions.IpAddress)
        dhcp_server.Dhcp6ServerSessions.IpPrefix.Single(prefix)
        testPlatform.info(dhcp_server.Dhcp6ServerSessions.IpPrefix)
    except Exception as errMsg:
        print('\n%s' % traceback.format_exc(None, errMsg))
        if debugMode == False and 'session' in locals():
            session.remove()
        return False


def ixia_rest_dhcp_server_pool_size_v6(*args,**kwargs):
    debugMode = False
    try:
        dhcp_server = kwargs['dhcp_server']
        testPlatform = kwargs['platform']
        ixNetwork = kwargs['ixnet']
        size = kwargs['pool_size']

        ixNetwork.info('Configuring IPv6 Dhcpv6sver IP Pool Size')
        dhcp_server.Dhcp6ServerSessions.PoolSize.Single(size)
        testPlatform.info(dhcp_server.Dhcp6ServerSessions.PoolSize)
    except Exception as errMsg:
        print('\n%s' % traceback.format_exc(None, errMsg))
        if debugMode == False and 'session' in locals():
            session.remove()
        return False


def ixia_rest_create_dhcp_server(*args,**kwargs):
    debugMode = False
    try:
        ip_session = kwargs['ip_session']
        session = kwargs['session']
        testPlatform = kwargs['platform']
        ixNetwork = kwargs['ixnet']
        ethernet = kwargs['ethernet']
        name = kwargs['name']
         

        ixNetwork.info('Configuring IPv4 Dhcpv4server')

        dhcpv4server = ip_session.Dhcpv4server.add(Name=name)
        testPlatform.info(dhcpv4server)
        
        return dhcpv4server
    except Exception as errMsg:
        print('\n%s' % traceback.format_exc(None, errMsg))
        if debugMode == False and 'session' in locals():
            session.remove()
        return False

def ixia_rest_dhcp_server_gw(*args,**kwargs):
    debugMode = False
    try:
        dhcp_server = kwargs['dhcp_server']
        testPlatform = kwargs['platform']
        ixNetwork = kwargs['ixnet']
        ip_gw = kwargs['ip_gw']

        ixNetwork.info('Configuring IPv4 Dhcpv4sver IP Gateway')
        dhcp_server.Dhcp4ServerSessions.IpGateway.Single(ip_gw)
        testPlatform.info(dhcp_server.Dhcp4ServerSessions.IpGateway)
    except Exception as errMsg:
        print('\n%s' % traceback.format_exc(None, errMsg))
        if debugMode == False and 'session' in locals():
            session.remove()
        return False


def ixia_rest_dhcp_server_address(*args,**kwargs):
    debugMode = False
    try:
        dhcp_server = kwargs['dhcp_server']
        testPlatform = kwargs['platform']
        ixNetwork = kwargs['ixnet']
        start_ip = kwargs['start_ip']
        prefix = kwargs['prefix']

        ixNetwork.info('Configuring IPv4 Dhcpv4sver IP Gateway')
        dhcp_server.Dhcp4ServerSessions.IpAddress.Increment(start_value=start_ip, step_value="0.0.0.1")
        testPlatform.info(dhcp_server.Dhcp4ServerSessions.IpAddress)
        dhcp_server.Dhcp4ServerSessions.IpPrefix.Single(prefix)
        testPlatform.info(dhcp_server.Dhcp4ServerSessions.IpPrefix)
    except Exception as errMsg:
        print('\n%s' % traceback.format_exc(None, errMsg))
        if debugMode == False and 'session' in locals():
            session.remove()
        return False

def ixia_rest_dhcp_server_pool_size(*args,**kwargs):
    debugMode = False
    try:
        dhcp_server = kwargs['dhcp_server']
        testPlatform = kwargs['platform']
        ixNetwork = kwargs['ixnet']
        size = kwargs['pool_size']

        ixNetwork.info('Configuring IPv4 Dhcpv4sver IP Pool Size')
        dhcp_server.Dhcp4ServerSessions.PoolSize.Single(size)
        testPlatform.info(dhcp_server.Dhcp4ServerSessions.PoolSize)
    except Exception as errMsg:
        print('\n%s' % traceback.format_exc(None, errMsg))
        if debugMode == False and 'session' in locals():
            session.remove()
        return False


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

def ixia_rest_stop_protocols(*args,**kwargs):
    debugMode = False
    session = kwargs['session']
    testPlatform = kwargs['platform']
    ixNetwork = kwargs['ixnet']
    # ixNetwork.StopAllProtocols(Arg1='sync')
    ixNetwork.StopAllProtocols()
    if "wait" in kwargs:
        wait_time = int(kwargs['wait'])
    else:
        wait_time = 60
    try_counter = 0
    while try_counter < 2:
        try:
            ixNetwork.info('Verify protocol sessions\n')
            console_timer(wait_time,msg = f'wait for {wait_time} after protocol stopps')
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
    console_timer(10,msg="Let traffic forward for 10s after start ixia traffic")

def ixia_rest_stop_traffic(*args,**kwargs):
    session = kwargs['session'] 
    testPlatform = kwargs['platform']
    ixNetwork = kwargs['ixnet']
    # trafficItem = ixNetwork.Traffic.TrafficItem
    # for item in trafficItem.find():
    #     testPlatform.info(item)
    #     tracking = item.Tracking.find()
    #     testPlatform.info(tracking)
    #     tracking.TrackBy = [f"flowGroup0",f"trackingenabled0"]
    # ixNetwork.Traffic.Apply()
    ixNetwork.Traffic.Stop()


def ixia_rest_clear_stats(*args,**kwargs):
    debugMode = False
    try:
        session = kwargs['session']
        testPlatform = kwargs['platform']
        ixNetwork = kwargs['ixnet']

        ixNetwork.ClearPortsAndTrafficStats()
        console_timer(20,msg="wait 20s for traffic stats to cleared")
        #The following line print out all rows stats at once
        #Assistant(ixNetwork, 'Traffic Item Statistics')
        # ixNetwork.info('{}\n'.format(flowStatistics))
    except Exception as errMsg:
        print('ixia_rest_clear_stats failed! \n%s' % traceback.format_exc(None, errMsg))
        if debugMode == False and 'session' in locals():
            session.remove()


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


def ixia_rest_create_ptp(*args,**kwargs):

# def add_ptp(self,*args,**kwargs):
#         self.ptp,self,network_group = ixia_rest_create_ptp(
#             platform = self.ixia.testPlatform,
#             ixnet = self.ixia.ixNetwork,
#             name = self.ptp_name,
#             ip = self.ip_session,
#         )
    testplatform = kwargs['platform']
    ptp_name = kwargs['name']
    # device_group = kwargs['device_group']
    ipv4 = kwargs['ip']
    ixNetwork = kwargs['ixnet']

    # network_group_name = f"{ptp_name}"
    ixNetwork.info(f'Configuring PTP {ptp_name}')
    ptp = ipv4.Ptp.add(Name=ptp_name)
    #ixia_rest_add_as_path(pool=ipv4PrefixPool,num_path=6, as_base=65000)
    #ixia_rest_set_origin(pool=ipv4PrefixPool,origin="egp",platform=testplatform)
    #ixia_rest_set_med(pool=ipv4PrefixPool,med=1234,platform=testplatform)
    return ptp
 

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

    #ixia_rest_add_as_path(pool=ipv4PrefixPool,num_path=6, as_base=65000)
    #ixia_rest_set_origin(pool=ipv4PrefixPool,origin="egp",platform=testplatform)
    #ixia_rest_set_med(pool=ipv4PrefixPool,med=1234,platform=testplatform)
    return bgp2,networkGroup,ipv4PrefixPool

    ixia_rest_add_as_path(pool=ipv4PrefixPool,num_path=6, as_base=65000)
    
def ixia_rest_set_origin(*args,**kwargs):
    ipv4PrefixPool = kwargs['pool']
    origin = kwargs['origin']
    testplatform = kwargs['platform']

    bgpiprouteproperty = ipv4PrefixPool.BgpIPRouteProperty.add()
    testplatform.info(bgpiprouteproperty.Origin.Values)
    bgpiprouteproperty.Origin.Single(origin)
    testplatform.info(bgpiprouteproperty.Origin.Values)

def ixia_rest_set_local_pref(*args,**kwargs):
    ipv4PrefixPool = kwargs['pool']
    local = kwargs['local']
    testplatform = kwargs['platform']

    bgpiprouteproperty = ipv4PrefixPool.BgpIPRouteProperty.add()
    testplatform.info(bgpiprouteproperty.LocalPreference.Values)
    bgpiprouteproperty.EnableLocalPreference.Single("True")
    bgpiprouteproperty.LocalPreference.Single(local)
    testplatform.info(bgpiprouteproperty.LocalPreference.Values)

def ixia_rest_set_med(*args,**kwargs):
    ipv4PrefixPool = kwargs['pool']
    med = kwargs['med']
    testplatform = kwargs['platform']

    bgpiprouteproperty = ipv4PrefixPool.BgpIPRouteProperty.add()
    #bgpiprouteproperty = ipv4PrefixPool.BgpIPRouteProperty
    testplatform.info(bgpiprouteproperty.MultiExitDiscriminator.Values)
    bgpiprouteproperty.EnableMultiExitDiscriminator.Single("True")
    bgpiprouteproperty.MultiExitDiscriminator.Single(med)
    testplatform.info(bgpiprouteproperty.MultiExitDiscriminator.Values)

def ixia_rest_add_as_path(*args,**kwargs):
    ipv4PrefixPool = kwargs['pool']
    num_path = kwargs['num_path']
    as_start_num = kwargs['as_base']

    # bgpiprouteproperty = ipv4PrefixPool.BgpIPRouteProperty
    # bgpiprouteproperty.update(NoOfASPathSegmentsPerRouteRange=num_path)
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

def ixia_rest_change_route_properties(*args, **kwargs):
    ipv4PrefixPool = kwargs['pool']

    # bgpiprouteproperty = ipv4PrefixPool.BgpIPRouteProperty
    # bgpiprouteproperty.update(NoOfASPathSegmentsPerRouteRange=num_path)
    bgpiprouteproperty = ipv4PrefixPool.BgpIPRouteProperty.add()
    if "num_path" in kwargs:
        num_path = kwargs['num_path']
        as_start_num = kwargs['as_base']
        bgpiprouteproperty.update(NoOfASPathSegmentsPerRouteRange=num_path)
        bgpiprouteproperty.EnableAsPathSegments.Single("True")
         
        bgpaspathsegmentlist = bgpiprouteproperty.BgpAsPathSegmentList.find()
        bgpaspathsegmentlist.EnableASPathSegment.Single("True")
        
        #print(f"type of bgpaspathsegmentlist = {type(bgpaspathsegmentlist)}")
        i = 0
        for seg in bgpaspathsegmentlist:
            bgpasnumberlist = seg.BgpAsNumberList.find()
            bgpasnumberlist.AsNumber.Single(as_start_num+i)
            i += 1 
    if "med" in kwargs:
        med = kwargs['med']
        bgpiprouteproperty.EnableMultiExitDiscriminator.Single("True")
        bgpiprouteproperty.MultiExitDiscriminator.Single(med)
    if "local" in kwargs:
        local = kwargs['local']
        bgpiprouteproperty.EnableLocalPreference.Single("True")
        bgpiprouteproperty.LocalPreference.Single(local)

    if "origin" in kwargs:
        origin = kwargs['origin']
        bgpiprouteproperty.Origin.Single(origin)
    if "flapping" in kwargs:
        start_ip = kwargs["flapping"]
        if start_ip.upper() == "RANDOM":
            bgpiprouteproperty.EnableFlapping.Random()
        else:
            bgpiprouteproperty.EnableFlapping.Increment(start_value=start_ip, step_value='0.0.0.1')
        
    #testplatform.info(bgpiprouteproperty2.MultiExitDiscriminator.Values)
 
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

    ipv6_portList = [[ixChassisIpList[0], 8,13,"00:11:01:01:01:01","2001:0010:0001:0001::",101,"2001:0010:0010:0001::100/64","2001:0010:0010.0001::254"], 
    [ixChassisIpList[0], 8, 14,"00:12:01:01:01:01","2001:0010.0020.0001.0001::",102,"2001:0010:0001:0001::254/64","2001:0010:0010:0001::254"],
    [ixChassisIpList[0], 8, 15,"00:13:01:01:01:01","2001:0010.0030.0001.0001.",102,"2001:0010:0001:0001::254/64","2001:0010:0010:0001::254"],
    [ixChassisIpList[0], 8, 16,"00:14:01:01:01:01","2001:0010:0040.0001.0001::",102,"2001:0010:0010:0001::0001/64","2001:0010:0010:0001::253"]]

    myixia = IXIA(apiServerIp,ixChassisIpList,ipv6_portList)

    myixia.topologies[0].add_ipv6()
    myixia.topologies[0].add_dhcp_server()
    myixia.topologies[0].dhcp_server_gw()
    myixia.topologies[0].dhcp_server_pool_size(pool_size = 50)
    myixia.topologies[0].dhcp_server_address(start_ip = "10.10.1.105")

    myixia.topologies[1].add_dhcp_client()
    myixia.topologies[2].add_dhcp_client()

    myixia.topologies[3].add_ipv4()
    myixia.topologies[3].add_dhcp_server()
    myixia.topologies[3].dhcp_server_gw()
    myixia.topologies[3].dhcp_server_pool_size(pool_size = 50)
    myixia.topologies[3].dhcp_server_address(start_ip = "10.10.1.5")

    myixia.start_protocol(wait=40)
    exit()

    bgp_portList = [[ixChassisIpList[0], 8,13,"00:11:01:01:01:01","10.1.1.0",101,"10.10.1.100/24","10.10.1.254"], 
    [ixChassisIpList[0], 8, 14,"00:12:01:01:01:01","10.20.1.1",102,"10.1.1.254/24","10.10.1.254"],
    [ixChassisIpList[0], 8, 15,"00:13:01:01:01:01","10.30.1.1.",102,"10.1.1.254/24","10.10.1.254"],
    [ixChassisIpList[0], 8, 16,"00:14:01:01:01:01","10.40.1.1",102,"10.10.1.1/24","10.10.1.253"]]

    myixia = IXIA(apiServerIp,ixChassisIpList,bgp_portList)

    myixia.topologies[0].add_ipv4()
    myixia.topologies[0].add_dhcp_server()
    myixia.topologies[0].dhcp_server_gw()
    myixia.topologies[0].dhcp_server_pool_size(pool_size = 50)
    myixia.topologies[0].dhcp_server_address(start_ip = "10.10.1.105")

    myixia.topologies[1].add_dhcp_client()
    myixia.topologies[2].add_dhcp_client()

    myixia.topologies[3].add_ipv4()
    myixia.topologies[3].add_dhcp_server()
    myixia.topologies[3].dhcp_server_gw()
    myixia.topologies[3].dhcp_server_pool_size(pool_size = 50)
    myixia.topologies[3].dhcp_server_address(start_ip = "10.10.1.5")

    myixia.start_protocol(wait=40)

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
