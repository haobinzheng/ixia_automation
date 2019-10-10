
from robot.api import logger
from pprint import pprint
import os
import sys
import time
import re

from datetime import datetime
from utils import *
from settings import *

from ixiatcl import IxiaTcl
from ixiahlt import IxiaHlt
from ixiangpf import IxiaNgpf
from ixiaerror import IxiaError

ixiatcl = IxiaTcl()
ixiahlt = IxiaHlt(ixiatcl)
ixiangpf = IxiaNgpf(ixiahlt)
ixNet = ixiangpf.ixnet 

try:
    ixnHLT_errorHandler('', {})
except (NameError,):
    def ixnHLT_errorHandler(cmd, retval):
        global ixiatcl
        err = ixiatcl.tcl_error_info()
        log = retval['log']
        additional_info = '> command: %s\n> tcl errorInfo: %s\n> log: %s' % (cmd, err, log)
        raise IxiaError(IxiaError.COMMAND_FAIL, additional_info)

try:
    ErrorHandler('', {})
except (NameError,):
    def ErrorHandler(cmd, retval):
        global ixiatcl
        err = ixiatcl.tcl_error_info()
        t = datetime.now()
        format_t = t.strftime("%Y%m%d-%H-%M-%S")
        additional_info = '%s:> command: %s\n> tcl errorInfo: %s\n> retval: %s' % (format_t, cmd, err, retval)
        logger.console('additional_info=%s' % additional_info)
        ixia_get_diag_file()
        raise IxiaError(IxiaError.COMMAND_FAIL, additional_info)

def ixia_diconnect():
    unset_status = ixiangpf.cleanup_session(reset='1')
    if unset_status['status'] != '1':
        ErrorHandler('cleanup_session', unset_status)
    else:
        ixia_print('ixia cleanup_session done')

    return(unset_status)

def ixia_print(obj, nested_level=0, output=sys.stdout):
    t = datetime.now()
    format_t = t.strftime("%Y%m%d-%H-%M-%S")
    spacing = '   '
    if type(obj) == dict:
        logger.console('%s' % ((nested_level) * spacing))
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                logger.console('%s%s:%s:' % ((nested_level + 1) * spacing, format_t, k))
                ixia_print(v, nested_level + 1, output)
            else:
                logger.console('%s%s:%s: %s' % ((nested_level + 1) * spacing, format_t, k, v))
        logger.console('%s:%s' % (nested_level * spacing))
    elif type(obj) == list:
        logger.console('%s[' % ((nested_level) * spacing))
        for v in obj:
            if hasattr(v, '__iter__'):
                ixia_print(v, nested_level + 1, output)
            else:
                logger.console('%s%s:%s' % ((nested_level + 1) * spacing, format_t, v))
        logger.console('%s]' % ((nested_level) * spacing))
    else:
        logger.console('%s%s:%s' % (nested_level * spacing, format_t, obj))

def collect_ixia_traffic_stats():
    traffic_stats = ixiangpf.traffic_stats(
        mode = 'flow'
        )

    if traffic_stats['status'] != '1':
        print ('\nError: Failed to get traffic flow stats.\n')
        print (traffic_stats)
        sys.exit()

    return(traffic_stats)

def ixia_get_diag_file():
    msg = 'Taking IXIA Diagfile ..'
    ixia_print(msg)
    status_dict = dict()
    status = ''

    ts = time.time()
    st = datetime.fromtimestamp(ts).strftime('%Y%m%d-%H-%M-%S')
    ixtechsupportFile = '/var/www/html/workspace/regression/ixNetDiag_' + st + '_Collect.Zip'
    msg = 'Ixia tech support file is -   ' + ixtechsupportFile
    ixia_print(msg)
    try:
        #status = ixiangpf.ixnet.execute('collectLogs', ixiangpf.ixnet.writeTo(ixtechsupportFile), 'currentInstance')
        ixia_print(str(status))
    except Exception as errMsg:
        status = 'Error' + str(errMsg)
    if 'Error' in status:
        status_dict['command'] = 'Get IxNet DiagFile'
        status_dict['Error or Exception'] = status
        msg = '** IXIA ERROR ** - Failed to take IXIA IxNetDiagFile, take it manually. ' + str(status)
        ixia_print(msg)
        return

    ### save config file
    ixncfgFile = '/var/www/html/workspace/regression/ixNetConfig_' + st + '.ixncfg'
    try:
        #status = ixiangpf.ixnet.execute('saveConfig', ixiangpf.ixnet.writeTo(ixncfgFile))
        ixia_print(str(status))
    except Exception as errMsg:
        status = 'Error' + str(errMsg)
    if 'Error' in status:
        status_dict['command'] = 'Save IxNet ConfigFile'
        status_dict['Error or Exception'] = status
        msg = '** IXIA ERROR ** - Failed to save IxNet ConfigFile ' + str(status)
        ixia_print(msg)

def ixia_protocal_status(info):
    #protocol_info {'status': '1', '/topology:1/deviceGroup:1/ethernet:1/ipv4:1': 
    #{'handles': {'sessions_total': '/topology:1/deviceGroup:1/ethernet:1/ipv4:1/item:1', 
    #'sessions_up': '/topology:1/deviceGroup:1/ethernet:1/ipv4:1/item:1'}}} 

    key = list(info.keys())[0]
    debug(key)
    handles = info[key]['handles']
    debug(info[key]['handles'])
    if 'sessions_up' in handles:
        return "UP"
    elif 'sessions_down' in handles:
        return "DOWN"

def ixia_protocal_info(ipv4_handle):
    # ipv4_prot_info_all = ixiangpf.protocol_info(
    #     mode = 'aggreate',
    # )

    # if ipv4_prot_info_all['status'] != IxiaHlt.SUCCESS:
    #     ErrorHandler('protocol_info', ipv4_prot_info_all)
    # else:
    #     tprint('protocol_info', ipv4_prot_info_all)

    ipv4_prot_info_1 = ixiangpf.protocol_info(
        handle = ipv4_handle,
        mode = 'handles',
    )

    if ipv4_prot_info_1['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('protocol_info', ipv4_prot_info_1)
        return False
    else:
        return ipv4_prot_info_1
        
def ixia_connect(**kwargs):
    '''
    Connects to IXIA chassis and make a use of the ports in the port_list 
    Arguments:
     -port_list: interface list
     -aggregation_mode: 
       ANY
     -aggregation_resource_mode:
       ANY
     -device:
       chaais IP address or chassis name
     -break_locks:
       CHOICES 0 1
     -close_server_on_disconnect:
       CHOICES 0 1
     -config_file:
       ANY
     -config_file_hlt:
       ANY
     -connect_timeout:
       NUMERIC
     -enable_win_tcl_server:
       CHOICES 0 1
     -guard_rail:
       CHOICES statistics none
     -interactive:
       CHOICES 0 1
     -ixnetwork_tcl_server
       ANY
     -ixnetwork_license_servers
       ANY
     -ixnetwork_license_type:
       ANY
     -'logging:
       CHOICES hltapi_calls
     -log_path
       ANY
     -ixnetwork_tcl_proxy:
       ANY
     -master_device:
       ANY
     -chain_sequence
       ANY
     -chain_cables_length
       ANY
     -chain_type:
       CHOICES none daisy star
     -reset:
       CHOICES 0 1
     -session_resume_keys:
       CHOICES 0 1
     -session_resume_include_filter
       ANY
     -sync
       CHOICES 0 1
     -tcl_proxy_username
       ANY
     -tcl_server
       ANY
     -username
       ANY
     -mode:
       CHOICES connect disconnect reconnect_ports save
     -vport_count:
       RANGE 1 - 600
     -vpor:t_list:
       REGEXP ^\[0-9\]+/\[0-9\]+/\[0-9\
     -execution_timeout:
       NUMERIC
     -return_detailed_handles
       CHOICES 0 1
     return:
       Connect result as a dictionary
    '''

    t = datetime.now()
    format_t = t.strftime("%Y%m%d-%H-%M-%S")
    ixia_print('ixia_connect start at %s' % format_t)

    ###########################################
    ##  CONNECT AND RETURN CONNECTION RESULT ##
    ###########################################
    tkwargs = {
        'connect_timeout':400,
    }
    for key, value in kwargs.items():
        tkwargs[key]=value
    connect_result = ixiangpf.connect(**tkwargs)
    
    if connect_result['status'] != '1':
        ErrorHandler('connect', connect_result)
    else:
        ixia_print('ixia_connect done')

    t = datetime.now()
    format_t = t.strftime("%Y%m%d-%H-%M-%S")
    ixia_print('ixia_connect done at %s' % format_t)
    return(connect_result)
     

def ixia_clear_traffic_stats():
    '''
    This command clear traffic
    Arguments:
     -max_wait_timer:
       NUMERIC
    '''

    kwargs={}
    kwargs['action']='clear_stats'

    #################################################
    ##  Create Create Traffic                       #
    #################################################
    traffic_control_status = ixiangpf.traffic_control(**kwargs)

    if traffic_control_status['status'] != '1':
        ErrorHandler('traffic_control', traffic_control_status)
    else:
        ixia_print('Traffic stats clear is done')
    time.sleep(15)
    return(traffic_control_status)

def ixia_destroy_topology(topology_handle,group_handle,multiplier):
    topology_status = ixiangpf.topology_config(
        mode                    =   'destroy'                             ,
        topology_name           =   "DHCPv4 Client"                     ,
        topology_handle          =   topology_handle                            ,
        device_group_multiplier  =   str(multiplier)                               ,
        device_group_enabled     =   '0'                                  ,
        device_group_handle      =   group_handle          ,
    )
    if topology_status['status'] != IxiaHlt.SUCCESS:
        ixnHLT_errorHandler('topology_config', topology_status)
    ixia_apply()

def ixia_connect_chassis(chassis_ip,portsList,ixnetwork_tcl_server,tcl_server):
    connect_status = ixia_connect(
        reset               =           1,
        device              =           chassis_ip,
        port_list           =           portsList,
        ixnetwork_tcl_server=           ixnetwork_tcl_server,
        tcl_server          =           tcl_server,
    )

    if connect_status['status'] != '1':
        ErrorHandler('connect', connect_status)

    port_handle = connect_status['vport_list']

    ports = connect_status['vport_list'].split()

    port_1 = port_handle.split(' ')[0]
    port_2 = port_handle.split(' ')[1]
    port_3 = port_handle.split(' ')[2]
    port_4 = port_handle.split(' ')[3]

    port_handle = ('port_1','port_2','port_3','port_4')
   
    

def ixia_static_ipv4_setup(chassis_ip,portsList,ixnetwork_tcl_server,tcl_server):
    
    connect_status = ixia_connect(
        reset               =           1,
        device              =           chassis_ip,
        port_list           =           portsList,
        ixnetwork_tcl_server=           ixnetwork_tcl_server,
        tcl_server          =           tcl_server,
    )

    if connect_status['status'] != '1':
        ErrorHandler('connect', connect_status)

    port_handle = connect_status['vport_list']

    ports = connect_status['vport_list'].split()

    port_1 = port_handle.split(' ')[0]
    port_2 = port_handle.split(' ')[1]
    port_3 = port_handle.split(' ')[2]
    port_4 = port_handle.split(' ')[3]
    

    port_handle = ('port_1','port_2','port_3','port_4')
    topology_handle_dict_list = []
    handle_dict = ixia_static_ipv4_topo(
            port=port_1,
            multiplier=1,
            topology_name="Topology 1",
            device_group_name = "Device Group 1",
            intf_ip="100.1.0.1", 
            gateway = "100.1.0.2",
            intf_mac="00.11.01.00.00.01",
            mask="255.255.255.0"
    )

    topology_handle_dict_list.append(handle_dict)
    handle_dict = ixia_static_ipv4_topo(
            port=port_2,
            multiplier=1,
            topology_name="Topology 2",
            device_group_name = "Device Group 2",
            intf_ip="100.1.0.2", 
            gateway = "100.1.0.1",
            intf_mac="00.12.01.00.00.01",
            mask="255.255.255.0"
    )
    topology_handle_dict_list.append(handle_dict)

    handle_dict = ixia_static_ipv4_topo(
            port=port_3,
            multiplier=1000,
            topology_name="Topology 3",
            device_group_name = "Device Group 3",
            intf_ip="100.2.0.1", 
            gateway = "100.2.10.1",
            intf_mac="00.13.01.00.00.01",
            mask="255.255.0.0"
    )
    topology_handle_dict_list.append(handle_dict)

    handle_dict= ixia_static_ipv4_topo(
            port=port_4,
            multiplier=1000,
            topology_name="Topology 4",
            device_group_name = "Device Group 4",
            intf_ip="100.2.10.1", 
            gateway = "100.2.0.1",
            intf_mac="00.14.01.00.00.01",
            mask="255.255.0.0"
    )

    topology_handle_dict_list.append(handle_dict)
    return topology_handle_dict_list

def ixia_apply():
    '''
    This command sends apply action
    Arguments:
     -action: regenerate
    '''

    kwargs={}
    kwargs['action']='apply'

    #################################################
    ##  Create Create Traffic                       #
    #################################################
    traffic_control_status = ixiangpf.traffic_control(**kwargs)

    if traffic_control_status['status'] != '1':
        ErrorHandler('traffic_control -action apply', traffic_control_status)
    else:
        ixia_print('Send apply done')

    return(traffic_control_status)


def ixia_static_ipv4_topo(**kwargs):
        ################################################################################
    # Configure Topology 2, Device Group 2                                         #
    ################################################################################

    port_2 = kwargs["port"]
    topology_2_status =ixiangpf.topology_config(
            topology_name      =kwargs["topology_name"]                           ,
            port_handle        = port_2                                  ,
        )

    if topology_2_status['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('multivalue_config', topology_2_status)
        
    topology_2_handle = topology_2_status['topology_handle']


    device_group_2_status = ixiangpf.topology_config(
            topology_handle              =topology_2_handle      ,
            device_group_name            =kwargs['device_group_name']       ,
            device_group_multiplier      =str(kwargs['multiplier'])                   ,
            device_group_enabled         ="1"                       ,
        )

    if device_group_2_status['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('multivalue_config', device_group_2_status)

    deviceGroup_2_handle = device_group_2_status['device_group_handle']

    ################################################################################
    # Configure protocol interfaces for second topology                             #
    ################################################################################

    multivalue_4_status =ixiangpf.multivalue_config(
            pattern               ="counter"                 ,
            counter_start         =kwargs['intf_mac']       ,
            counter_step          ="00.00.00.00.00.01"       ,
            counter_direction     ="increment"               ,
            nest_step             ="00.00.01.00.00.00"       ,
            nest_owner            =topology_2_handle      ,
            nest_enabled          ="1"                       ,
        )
        
    if multivalue_4_status['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('multivalue_config', multivalue_4_status)

    multivalue_4_handle = multivalue_4_status['multivalue_handle']


    ethernet_2_status = ixiangpf.interface_config(
            protocol_name                ="Ethernet 2"               ,
            protocol_handle              =deviceGroup_2_handle      ,
            mtu                          ="1500"                      ,
            src_mac_addr                 =multivalue_4_handle       ,
            vlan                         ="0"                          ,
            vlan_id                      ="1"                          ,
            vlan_id_step                 ="0"                          ,
            vlan_id_count                ="1"                          ,
            vlan_tpid                    ="0x8100"                     ,
            vlan_user_priority           ="0"                          ,
            vlan_user_priority_step      ="0"                          ,
            use_vpn_parameters           ="0"                          ,
            site_id                      ="0"                          ,
        )
    if ethernet_2_status['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('interface_config', ethernet_2_status)
        
    ethernet_2_handle=ethernet_2_status['ethernet_handle']


    multivalue_5_status = ixiangpf.multivalue_config(
            pattern                ="counter"                 ,
            counter_start          =kwargs['intf_ip']               ,
            counter_step           ="0.0.0.1"                 ,
            counter_direction      ="increment"               ,
            nest_step              ="0.1.0.0"                 ,
            nest_owner             =topology_2_handle      ,
            nest_enabled           ="1"                       ,
        )
        
    if multivalue_5_status['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('multivalue_config', multivalue_5_status)
        
    multivalue_5_handle = multivalue_5_status['multivalue_handle']


    multivalue_6_status = ixiangpf.multivalue_config(
            pattern                ="counter"                 ,
            counter_start          = kwargs['gateway']              ,
            counter_step           ="255.255.255.255"         ,
            counter_direction      ="decrement"               ,
            nest_step              ="0.0.0.1"                 ,
            nest_owner             =topology_2_handle      ,
            nest_enabled           ="0"                       ,
        )   
    if multivalue_6_status['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('multivalue_config', multivalue_6_status)
        
    multivalue_6_handle = multivalue_6_status['multivalue_handle']


    ipv4_2_status = ixiangpf.interface_config(
            protocol_name                ="IPv4 2"                  ,
            protocol_handle              =ethernet_2_handle        ,
            ipv4_resolve_gateway         ="1"                         ,
            ipv4_manual_gateway_mac      ="00.00.00.00.00.01"         ,
            gateway                      =multivalue_6_handle      ,
            intf_ip_addr                 =multivalue_5_handle      ,
            netmask                      =kwargs['mask']             ,
        )
        
    if ipv4_2_status['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('interface_config', ipv4_2_status)
        return (None,None,None,None,) 

    ipv4_2_handle = ipv4_2_status['ipv4_handle']
    handle_dict = {}
    handle_dict['port_handle'] = port_2
    handle_dict['topology_handle'] = topology_2_handle
    handle_dict['ipv4_handle'] = ipv4_2_handle
    handle_dict['deviceGroup_handle'] = deviceGroup_2_handle
    handle_dict['ethernet_handle'] = ethernet_2_handle

    ixia_apply_changes_protocol(topology_2_handle)
    return handle_dict

def ixia_static_ipv6_pair_setup(chassis_ip,portsList,ixnetwork_tcl_server,tcl_server):
    debug("Start to configure IPv6 port pairs")
    connect_status = ixia_connect(
        reset               =           1,
        device              =           chassis_ip,
        port_list           =           portsList,
        ixnetwork_tcl_server=           ixnetwork_tcl_server,
        tcl_server          =           tcl_server,
    )

    if connect_status['status'] != '1':
        ErrorHandler('connect', connect_status)

    port_handle = connect_status['vport_list']

    ports = connect_status['vport_list'].split()

    #This should be changed in the future, port3--> port1, port4-->port2 etc
    port_3 = port_handle.split(' ')[0]
    port_4 = port_handle.split(' ')[1]
    # port_3 = port_handle.split(' ')[2]
    # port_4 = port_handle.split(' ')[3]

    port_handle = ('port_3','port_4')

    ################################################################################
    # Configure Topology 3, Device Group 3                                         #
    ################################################################################

    topology_3_status = ixiangpf.topology_config(
            topology_name      ="Topology 3"                          ,
            port_handle        =port_3                                ,
        )   
        
    if topology_3_status['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('multivalue_config', topology_3_status)

    topology_3_handle = topology_3_status['topology_handle']


    device_group_3_status = ixiangpf.topology_config(
            topology_handle              =topology_3_handle      ,
            device_group_name            ="Device Group3"         ,
            device_group_multiplier      ="1"                      ,
            device_group_enabled         ="1"                       ,
        )
        
    if device_group_3_status['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('multivalue_config', device_group_3_status)
        
    deviceGroup_3_handle = device_group_3_status['device_group_handle']

    ################################################################################
    # Configure protocol interfaces for the third topology                         #
    ################################################################################

    multivalue_7_status = ixiangpf.multivalue_config(
            pattern                ="counter"                 ,
            counter_start          ="00.13.01.00.00.01"       ,
            counter_step           ="00.00.00.00.00.01"       ,
            counter_direction      ="increment"               ,
            nest_step              ="00.00.01.00.00.00"       ,
            nest_owner             =topology_3_handle      ,
            nest_enabled           ="1"                       ,
        )
        
        
    if multivalue_7_status['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('multivalue_config', multivalue_7_status)

    multivalue_7_handle = multivalue_7_status['multivalue_handle']


    ethernet_3_status = ixiangpf.interface_config(
            protocol_name                ="Ethernet 3"               ,
            protocol_handle              =deviceGroup_3_handle      ,
            mtu                          ="1500"                       ,
            src_mac_addr                 =multivalue_7_handle       ,
            src_mac_addr_step            ="00.00.00.00.00.00"          ,
            vlan                         ="0"                          ,
            vlan_id                      ="1"                          ,
            vlan_id_step                 ="0"                          ,
            vlan_id_count                ="1"                          ,
            vlan_tpid                    ="0x8100"                     ,
            vlan_user_priority           ="0"                          ,
            vlan_user_priority_step      ="0"                          ,
            use_vpn_parameters           ="0"                          ,
            site_id                      ="0"                          ,
        )
        
    if ethernet_3_status['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('interface_config', ethernet_3_status)
        
    ethernet_3_handle = ethernet_3_status ['ethernet_handle']


    multivalue_8_status = ixiangpf.multivalue_config (
            pattern                ="counter"                 ,
            counter_start          ="3000:0:0:1:0:0:0:2"      ,
            counter_step           ="0:0:0:1:0:0:0:0"         ,
            counter_direction      ="increment"               ,
            nest_step              ="0:0:0:1:0:0:0:0"         ,
            nest_owner             ="topology_3_handle"      ,
            nest_enabled           ="1"                       ,
        )
        
    if multivalue_8_status['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('multivalue_config', multivalue_8_status)

    multivalue_8_handle = multivalue_8_status['multivalue_handle']

    multivalue_9_status = ixiangpf.multivalue_config(
            pattern                ="counter"                 ,
            counter_start          ="3000:0:1:1:0:0:0:2"      ,
            counter_step           ="0:0:0:1:0:0:0:0"         ,
            counter_direction      ="increment"               ,
            nest_step              ="0:0:0:1:0:0:0:0"         ,
            nest_owner             =topology_3_handle      ,
            nest_enabled           ="1"                       ,
        )
        
    if multivalue_9_status['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('multivalue_config', multivalue_9_status)
        
    multivalue_9_handle = multivalue_9_status["multivalue_handle"]


    ipv6_3_status =ixiangpf.interface_config(
            protocol_name                     ="IPv6 3"                  ,
            protocol_handle                   =ethernet_3_handle        ,
            ipv6_multiplier                   ="1"                         ,
            ipv6_resolve_gateway              ="1"                         ,
            ipv6_manual_gateway_mac           ="00.00.00.00.00.01"         ,
            ipv6_manual_gateway_mac_step      ="00.00.00.00.00.00"         ,
            ipv6_gateway                      =multivalue_9_handle      ,
            ipv6_gateway_step                 ="::0"                       ,
            ipv6_intf_addr                    =multivalue_8_handle      ,
            ipv6_intf_addr_step               ="::0"                       ,
            ipv6_prefix_length                ="64"                        ,
        )   
    if ipv6_3_status['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('interface_config', ipv6_3_status)
        
    ipv6_3_handle = ipv6_3_status["ipv6_handle"]

    ################################################################################
    # Configure Topology 4, Device Group 4                                         #
    ################################################################################

    topology_4_status = ixiangpf.topology_config(
            topology_name      ="Topology 4"                          ,
            port_handle        =port_4                                ,
        )
        
    if topology_4_status['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('multivalue_config', topology_4_status)
        
    topology_4_handle = topology_4_status["topology_handle"]


    device_group_4_status=ixiangpf.topology_config(
            topology_handle              =topology_4_handle      ,
            device_group_name            ="Device Group4"         ,
            device_group_multiplier      ="1"                      ,
            device_group_enabled         ="1"                       ,
        )
    if device_group_4_status['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('multivalue_config', device_group_4_status)
        
    deviceGroup_4_handle = device_group_4_status["device_group_handle"]

    ################################################################################
    # Configure protocol interfaces for the fourth topology                        #
    ################################################################################

    multivalue_10_status = ixiangpf.multivalue_config (
            pattern                ="counter"                 ,
            counter_start          ="00.14.01.00.00.01"       ,
            counter_step           ="00.00.00.00.00.01"       ,
            counter_direction      ="increment"               ,
            nest_step              ="00.00.01.00.00.00"       ,
            nest_owner             =topology_4_handle      ,
            nest_enabled           ="1"                       ,
        )

    if multivalue_10_status['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('multivalue_config', multivalue_10_status)

    multivalue_10_handle = multivalue_10_status ["multivalue_handle"]

    ethernet_4_status = ixiangpf.interface_config (
            protocol_name                ="Ethernet 4"               ,
            protocol_handle              =deviceGroup_4_handle      ,
            mtu                          ="1500"                       ,
            src_mac_addr                 =multivalue_10_handle      ,
            src_mac_addr_step            ="00.00.00.00.00.00"          ,
            vlan                         ="0"                          ,
            vlan_id                      ="1"                          ,
            vlan_id_step                 ="0"                          ,
            vlan_id_count                ="1"                          ,
            vlan_tpid                    ="0x8100"                     ,
            vlan_user_priority           ="0"                          ,
            vlan_user_priority_step      ="0"                         ,
            use_vpn_parameters           ="0"                          ,
            site_id                      ="0"                          ,
        )

        
    if ethernet_4_status['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('interface_config', ethernet_4_status)

    ethernet_4_handle = ethernet_4_status["ethernet_handle"]


    multivalue_11_status = ixiangpf.multivalue_config(
            pattern                ="counter"                 ,
            counter_start          ="3000:0:1:1:0:0:0:2"      ,
            counter_step           ="0:0:0:1:0:0:0:0"         ,
            counter_direction      ="increment"               ,
            nest_step              ="0:0:0:1:0:0:0:0"         ,
            nest_owner             =topology_4_handle      ,
            nest_enabled           ="1"                       ,
        )

    if multivalue_11_status['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('multivalue_config', multivalue_11_status)

    multivalue_11_handle = multivalue_11_status ["multivalue_handle"]


    multivalue_12_status=ixiangpf.multivalue_config(
            pattern                ="counter"                 ,
            counter_start          ="3000:0:0:1:0:0:0:2"      ,
            counter_step           ="0:0:0:1:0:0:0:0"         ,
            counter_direction      ="increment"               ,
            nest_step              ="0:0:0:1:0:0:0:0"         ,
            nest_owner             =topology_4_handle      ,
            nest_enabled           ="1"                       ,
        )

    if multivalue_12_status['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('multivalue_config', multivalue_12_status)
        
    multivalue_12_handle = multivalue_12_status["multivalue_handle"]


    ipv6_4_status = ixiangpf.interface_config(
            protocol_name                     ="IPv6 4"                  ,
            protocol_handle                   =ethernet_4_handle        ,
            ipv6_multiplier                   ="1"                         ,
            ipv6_resolve_gateway              ="1"                         ,
            ipv6_manual_gateway_mac           ="00.00.00.00.00.01"         ,
            ipv6_manual_gateway_mac_step      ="00.00.00.00.00.00"         ,
            ipv6_gateway                      =multivalue_12_handle      ,
            ipv6_gateway_step                 ="::0"                       ,
            ipv6_intf_addr                    =multivalue_11_handle      ,
            ipv6_intf_addr_step               ="::0"                       ,
            ipv6_prefix_length                ="64"                        ,
        )
        
    if ipv6_4_status['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('interface_config', ipv6_4_status)
        
    ipv6_4_handle = ipv6_4_status ["ipv6_handle"]
    return (ipv6_3_handle,ipv6_4_handle)

def ixia_stop_one_protcol(ipv4_handle):
    ####################################################
    # Start protocols
    ####################################################
    debug ("Start running ixia_stop_one_protcol")
    tprint("Stopping individual protocol....")

    start = ixiangpf.test_control(
        handle = ipv4_handle,
        action='stop_protocol',
    )
    if start['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('test_control', start)

    #tprint("After stop protocol, wait for 5 seconds for things to settle")
    #time.sleep(5)
    return start

def ixia_abort_one_protcol(ipv4_handle):
    ####################################################
    # Start protocols
    ####################################################
    debug ("Start running ixia_stop_one_protcol")
    tprint("Startting individual protocol....")

    start = ixiangpf.test_control(
        handle = ipv4_handle,
        action='abort_protocol',
    )
    if start['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('test_control', start)

    tprint("After stop protocol, wait for 15 seconds for things to settle")
    time.sleep(15)
    return start['status']

def ixia_apply_changes_protocol(myhandle):
    tprint ("Applying changes on the fly")
    applyChanges = ixiangpf.test_control(
        handle = myhandle,
        action = 'apply_on_the_fly_changes',)
    if applyChanges['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('test_control', applyChanges)
    time.sleep(10)
    return applyChanges

def ixia_start_one_protcol(ipv4_handle):
    ####################################################
    # Start protocols
    ####################################################
    debug ("Start running ixia_start_one_protcol")
    tprint("Startting individual protocol....")

    start = ixiangpf.test_control(
        handle = ipv4_handle,
        action='start_protocol',
    )
    if start['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('test_control', start)

    # tprint("After starting protocol, wait for 5 seconds for things to settle")
    time.sleep(5)
    return start

def ixia_start_protcols(ipv4_1_handle,ipv4_2_handle):
    ####################################################
    # Start protocols
    ####################################################
    debug ("Start to running ixia_start_protocols")
    tprint("Startting protocols....")

    start = ixiangpf.test_control(action='start_all_protocols')
    if start['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('test_control', start)

    tprint("After starting protocols, wait for 15 seconds for things to settle before creating traffic items")
    time.sleep(15)
    tprint("Verify sessions status after protocol is started")
    ipv4_proto_info_1 = ixia_protocal_info(ipv4_1_handle)
    #tprint('protocol_info', ipv4_proto_info_1)
    ipv4_proto_info_1.pop('status') 
    if ixia_protocal_status(ipv4_proto_info_1) == "UP":
        tprint("IPv4 protocol session is UP: {}".format(ipv4_proto_info_1.keys()))
    elif ixia_protocal_status(ipv4_proto_info_1) == "DOWN":
        tprint("IPv4 protocol session is DOWN: {}, check your test setup!!".format(list(ipv4_proto_info_1.keys())[0]))
        return False
    ipv4_proto_info_2 = ixia_protocal_info(ipv4_2_handle)
    #tprint('protocol_info', ipv4_proto_info_1)
    ipv4_proto_info_2.pop('status') 
    if ixia_protocal_status(ipv4_proto_info_2) == "UP":
        tprint("IPv4 protocol session is UP: {}".format(ipv4_proto_info_2.keys()))
    elif ixia_protocal_status(ipv4_proto_info_2) == "DOWN":
        tprint("IPv4 protocol session is DOWN: {}, check your test setup!!".format(list(ipv4_proto_info_2.keys())[0]))
        return False

def ixia_start_protcols_verify(handle_list, **kwargs):
    ####################################################
    # Start protocols
    ####################################################
    if 'timeout' in kwargs:
        timeout = int(kwargs['timeout'])
    else:
        timeout = 60
    debug ("Start to running ixia_start_protocols")
    tprint("Startting protocols....")

    status = ixiangpf.test_control(action='start_all_protocols')
    if status['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('test_control', status)

    tprint(f"After starting protocols, wait for {timeout} seconds for protocols to come up")
    console_timer(timeout)
    tprint("Verify sessions status after protocol is started")
    for handle in handle_list:
        proto_info = ixia_protocal_info(handle)
        #tprint('protocol_info', ipv4_proto_info_1)
        proto_info.pop('status') 
        if ixia_protocal_status(proto_info) == "UP":
            tprint("Protocol session is UP: {}".format(proto_info.keys()))
        elif ixia_protocal_status(proto_info) == "DOWN":
            tprint("protocol session is DOWN: {}, check your test setup!!".format(list(proto_info.keys())[0]))
            return False

    return 

def ixia_create_ipv4_traffic(src,dst,**kwargs):
    ####################################################
    ##Configure traffic for all configuration elements##
    ##########################################################
    tprint("IXIA creating traffic item ....")
    if 'rate' in kwargs:
        rate = kwargs['rate']
    else:
        rate = 100
    if 'name' in kwargs:
        stream_name = kwargs['name']
    else:
        stream_name ='Traffic_Item_1'
    twargs = {}
    tkwargs = {
            'mode':'create',
            'endpointset_count':1,
            'src_dest_mesh':'one_to_one',
            'emulation_src_handle': src,
            'emulation_dst_handle': dst,
            'route_mesh':'one_to_one',
            'src_dest_mesh':'one_to_one',
            'bidirectional':0,
            'name':stream_name,
            'circuit_endpoint_type':'ipv4',
            'frame_size':1000,
            'rate_mode':'percent',
            'rate_percent':rate,
            'burst_loop_count':1000,
            'inter_burst_gap':100,
            'pkts_per_burst':10000,
            'track_by':'endpoint_pair',
            'l3_protocol':'ipv4'
        }
    for key, value in tkwargs.items():
        if re.search('port_handle', key):
            tkwargs[key]='%s/%s' % (1, value)
        else:
            tkwargs[key]=value
    ixia_apply()
     
    traffic_config_status = ixiangpf.traffic_config(**tkwargs)
    stream_id = traffic_config_status['stream_id'] 
    if traffic_config_status['status'] != '1':
        ErrorHandler('traffic_config', traffic_config_status)
        return False
    else:
        tprint('Create Burst Traffic stream: Done')
        return traffic_config_status

def ixia_remove_traffic_config(**kwargs):
    '''
    This command remove Traffic stream
    Arguments:
     -stream_id:
       ANY
    Default:
     'mode':'remove',
    '''
    tkwargs = {
        'mode':'remove',
    }
    for key, value in kwargs.items():
        tkwargs[key]=value

    #################################################
    ##  Create Create Traffic                       #
    #################################################
    traffic_config_status = ixiangpf.traffic_config(**tkwargs)

    if traffic_config_status['status'] != '1':
       
        ErrorHandler('traffic_config', traffic_config_status)
    else:
        ixia_print('Remove Traffic Stream done')

    return(traffic_config_status)

def ixia_start_traffic():
    ################################################################################
    # Apply And Start traffic                                                                #
    ################################################################################
    tprint("Starting Traffic.....")
    kwargs={}
    tkwargs = {}
    kwargs = {
            'action':'apply',
            'max_wait_timer':120,
        }
    for key, value in kwargs.items():
        tkwargs[key]=value
    traffic_control_status = ixiangpf.traffic_control(**tkwargs)

    if traffic_control_status['status'] != '1':
        ErrorHandler('traffic_control -action apply', traffic_control_status)
    else:
        tprint('\nApply traffic to hardward: Done')


    tprint("!!!!!!Running traffic for 15 seconds, please inspect any traffic loss before test starts")
    kwargs={}
    tkwargs = {}
    kwargs = {
            'action':'run',
            'max_wait_timer':120,
        }
    for key, value in kwargs.items():
        tkwargs[key]=value
    run_traffic = ixiangpf.traffic_control(**tkwargs)

    if run_traffic['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('test_control', run_traffic)

def ixia_connect_ports(chassis_ip,portsList,ixnetwork_tcl_server,tcl_server):
    connect_status = ixia_connect(
        reset               =           1,
        device              =           chassis_ip,
        port_list           =           portsList,
        ixnetwork_tcl_server=           ixnetwork_tcl_server,
        tcl_server          =           tcl_server,
    )

    if connect_status['status'] != '1':
        ErrorHandler('connect', connect_status)
        return False
    else:
        port_handle = connect_status['vport_list']
        ports = connect_status['vport_list'].split(' ')
        return ports
        

def ixia_port_topology(port,multiplier,**kwargs):
    topo_name = kwargs['topo_name']
    topology_status = ixiangpf.topology_config(
        topology_name           =   topo_name,
        port_handle             =   port,
        device_group_multiplier =    str(multiplier),
    )
    if topology_status['status'] != IxiaHlt.SUCCESS:
        ixnHLT_errorHandler('topology_config', topology_status)
        return False
    else:
        tprint ("Configuring of topology is done")

        deviceGroup_handle = topology_status ['device_group_handle']
        top_1 = topology_status['topology_handle']
        return (top_1,deviceGroup_handle)

def ixia_stop_traffic():
    '''
    This command stop sending traffic
    Arguments:
     -max_wait_timer:
       NUMERIC
    '''

    kwargs={}
    kwargs['action']='stop'
    kwargs['max_wait_timer']=60

    #################################################
    ##  Create Create Traffic                       #
    #################################################
    traffic_control_status = ixiangpf.traffic_control(**kwargs)
    time.sleep(2)

    if traffic_control_status['status'] != '1':
        ErrorHandler('traffic_control', traffic_control_status)
    else:
        if traffic_control_status['stopped'] == '0':
            ixia_print("traffic is not stop yet... Give poll for the traffic status for another 60 seconds\n")
            count = 30
            waitTime = 0
            while True:
                traffic_poll_status = ixiangpf.traffic_control(
                    action = 'poll',
                )
                if traffic_poll_status['stopped'] == '0':
                    if count == 0:
                        break
                    else:
                        time.sleep(2)
                        count -= 1
                        waitTime += 2
                else:
                    break

            if traffic_poll_status['stopped'] == '0':
                ErrorHandler('traffic_control', traffic_control_status)
            else:
                ixia_print('traffic is stopped (wait time=%s seconds)' % waitTime)
        else:
            ixia_print('traffic is stopped')
            time.sleep(2)

    return(traffic_control_status)


def ixia_emulation_dhcp_group_config(**kwargs):
    '''
    This command configure emulate dhcp group
    Arguments:
     -dhcp_range_server_address:
       ANY
     -handle:
       ANY
    return:
     -ping_status
    '''
    tkwargs = {
        'dhcp_range_ip_type':"ipv4",
        'dhcp_range_renew_timer':"0",
        'dhcp_range_use_first_server':"1",
        'use_rapid_commit':"0",
        'protocol_name':"""DHCPv4 Client""",
        'dhcp4_broadcast':"0",
        'dhcp4_gateway_address':"0.0.0.0",
        'dhcp4_gateway_mac':"00.00.00.00.00.00",
    }
    for key, value in kwargs.items():
        tkwargs[key]=value

    #####################################################
    ##  ping host                                       #
    #####################################################
    dhcp_group_status = ixiangpf.emulation_dhcp_group_config(**tkwargs)

    if dhcp_group_status['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('emulation_dhcp_group_config', dhcp_group_status)
    else:
        ixia_print('Configure Emulation dhcp group done')

    return(dhcp_group_status)