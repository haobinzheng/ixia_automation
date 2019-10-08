from robot.api import logger
from pprint import pprint
import os, sys, re
import time
import ast
import pdb

from datetime import datetime

from ixiatcl import IxiaTcl
from ixiahlt import IxiaHlt
from ixiangpf import IxiaNgpf
from ixiaerror import IxiaError

ixiatcl = IxiaTcl()
ixiahlt = IxiaHlt(ixiatcl)
ixiangpf = IxiaNgpf(ixiahlt)

# Remove these 2 lines after debug done 6/5/2018
#pid = os.getpid()
#log_file_name = '/var/www/html/workspace/regression/ixia_debug_log_for_wrong_port_issue_%s.txt' % pid
#ixiahlt.ixiatcl._eval("set ::ixia::debug 3")
#ixiahlt.ixiatcl._eval("set ::ixia::debug_file_name %s" % log_file_name)

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
1G
    return(connect_result)

def ixia_disconnect(**kwargs):
    '''
    Disconnect from IXIA chassis and reset the ports to factory defaults before releasing them
    Arguments:
     -maintain_lock: 
       CHOICES 0 1
     -skip_wait_pending_operations:
       CHOICES 0 1
     -reset:
       CHOICES 0 1
       1 - Reset the ports to factory defaults before releasing them
     return:
       Disconnect result as a dictionary
    '''
    for k in kwargs:
        exec('{KEY} = {VALUE}'.format(KEY = k, VALUE = repr(kwargs[k])))

    #################################################
    ##  DISCONNECT AND RETURN DISCONNECTION RESULT ##
    #################################################
    disconnect_result = ixiangpf.cleanup_session(**kwargs)

    if disconnect_result['status'] != '1':
        ErrorHandler('cleanup_session', disconnect_result)
    else:
        ixia_print('ixia_disconnect done')

    return(disconnect_result)

def ixia_topology_config(**kwargs):
    '''
    create a topology 
    Arguments:
     -port_handle:
       REGEXP ^[0-9]+/[0-9]+/[0-9]+$
    Default:
     -topology_name:'topology 1'
    return:
     -topology_handle:
    '''
    tkwargs = {
        'topology_name':'topology 1',
    }
    for key, value in kwargs.iteritems():
        if key == 'port_handle':
            tkwargs[key]='%s/%s' % (1, value)
        else:
            tkwargs[key]=value

    #################################################
    ##  Configure Topology                          #
    #################################################
    topology_status = ixiangpf.topology_config(**tkwargs)

    if topology_status['status'] != '1':
        ErrorHandler('topology_config', topology_status)
    else:
        ixia_print('Configure Topology done')

    return topology_status

def ixia_devicegrp_config(**kwargs):
    '''
    create one or multiple device groups
    Arguments:
     -topology_handle:
       ALPHA
     -device_group_multiplier:
       NUMERIC
    Default:
     -device_group_name:'group 1'
     -device_group_multiplier:1
     -device_group_enabled:1
    return:
     -device_group_handle
    '''
    tkwargs = {
        'device_group_multiplier':1,
        'device_group_enabled':1,
    }
    for key, value in kwargs.iteritems():
        tkwargs[key]=value

    #################################################
    ##  Configure Group(s)                          #
    #################################################
    device_group_status = ixiangpf.topology_config(**tkwargs)

    if device_group_status['status'] != '1':
        ErrorHandler('topology_config', device_group_status)
    else:
        ixia_print('Configure Group(s) done')

    return(device_group_status)

def ixia_multivalue_config(**kwargs):
    '''
    create multivalue config
    Arguments:
     -topology_handle:
       ALPHA
     -nest_step:
       ANY
     -nest_owner:
       ANY
     -counter_start:
       NUMERIC
    Default:
     -pattern:'counter'
     -counter_step:00:00:00:00:00:01
     -counter_direction:'increment'
     -nest_enabled:1
    return:
     -multivalue_handle
    '''
    tkwargs = {
        'pattern':'counter',
        'counter_step':'00:00:00:00:00:01',
        'counter_direction':'increment',
        'nest_enabled':1
    }
    for key, value in kwargs.iteritems():
        tkwargs[key]=value

    #################################################
    ##  Configure Group(s)                          #
    #################################################
    multivalue_config_status = ixiangpf.multivalue_config(**tkwargs)

    if multivalue_config_status['status'] != '1':
        ErrorHandler('multivalue_config', multivalue_config_status)
    else:
        ixia_print('multivalue_config done')

    return(multivalue_config_status)

def ixia_multivalue_config_custom(**kwargs):
    '''
    create multivalue config
    Arguments:
     -topology_handle:
       ALPHA
     -nest_step:
       ANY
     -nest_owner:
       ANY
     -counter_start:
       NUMERIC
    return:
     -multivalue_handle
    '''
    tkwargs = {
    }
    for key, value in kwargs.iteritems():
        tkwargs[key]=value

    #################################################
    ##  Configure Group(s)                          #
    #################################################
    multivalue_config_status = ixiangpf.multivalue_config(**tkwargs)

    if multivalue_config_status['status'] != '1':
        ErrorHandler('multivalue_config', multivalue_config_status)
    else:
        ixia_print('multivalue_config done')

    return(multivalue_config_status)


def ixia_l2_interface_config(**kwargs):
    '''
    This command create Ethernet Stack for the Device Group
    Arguments:
     -protocol_name:
       ALPHA
     -protocol_handle:
       ANY
     -mtu:
       NUMERIC
     -src_mac_addr:
       ANY
     -src_mac_addr_step:
       NUMERIC
     -vlan:
       CHOICES 0 1
     -vlan_id_count:
       NUMERIC
     -vlan_id:
       NUMERIC
    return:
     -ethernet_handle
    '''
    tkwargs = {
        'mtu':1500,
    }
    for key, value in kwargs.iteritems():
        tkwargs[key]=value

    #####################################################
    ##  Create Src Ethernet Stack for the Device Group  #
    #####################################################
    ethernet_status = ixiangpf.interface_config(**tkwargs)

    if ethernet_status['status'] != '1':
        ErrorHandler('inerface_config', ethernet_status)
    else:
        ixia_print('Create Ethernet Stack for the Device Group done')

    return(ethernet_status)

def ixia_l2_multi_vlan_tag_interface_config(topology_handle):
    '''
    This command create Ethernet Stack for the Device Group
    Arguments:
     -nest_owner:
       topology_handle
    return:
     -multivalue_handle
    '''
    tkwargs = {
        'pattern':"single_value",
        'single_value':"2",
        'nest_step':"1",
        'nest_owner':topology_handle,
        'nest_enabled':"0",
        'overlay_value':"3",
        'overlay_value_step':"3",
        'overlay_index':"2",
        'overlay_index_step':"0",
        'overlay_count':"1",
    }
    #####################################################
    ##  Create Src Ethernet Stack for the Device Group  #
    #####################################################
    multivalue_status = ixiangpf.multivalue_config(**tkwargs)
    if multivalue_status['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('multivalue_config', multivalue_status)
    else:
        ixia_print('Create multivalue configuration done')

    return(multivalue_status)

def ixia_ping(protocol_handle, ping_dst, send_ping=1):
    '''
    This command ping a destination host
    Arguments:
     -protocol_handle:
       ANY
     -ping_dst
       ANY
     -send_ping:
       HOICES 0 1
    return:
     -ping_status
    '''
    kwargs = {}
    kwargs['protocol_handle']=protocol_handle
    kwargs['ping_dst']=ping_dst
    kwargs['send_ping']=send_ping

    #####################################################
    ##  ping host                                       #
    #####################################################
    ping_status = ixiangpf.interface_config(**kwargs)

    ping_status_ret = {'status': 0}
    if ping_status['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('inerface_config', ping_status)

    keys = ping_status.keys()
    port_handle = keys[1]
    if ping_status[port_handle]['ping_success'] != IxiaHlt.SUCCESS:
        try:
            ixia_print('%s ping %s failed: %s' % (port_handle, ping_dst, ping_status[port_handle]['ping_details']))
        except:
            ixia_print('$s ping %s failed. cannot find ping failure details' % (port_handle, ping_dst))
    else:
        ping_status_ret = {'status': 1}
        ixia_print('%s ping %s successful' % (port_handle, ping_dst))

    return(ping_status_ret)

def ixia_l3_interface_config(**kwargs):
    '''
    This command create L3 Stack on top of Ethernet Stack
    Arguments:
     -protocol_name:
       ALPHA
     -protocol_handle:
       ANY
     -gateway:
       ANY
     -gateway_step:
       ANY
     -intf_ip_addr:
       ANY
     -intf_ip_addr_step:
       NUMERIC
     -netmask:
       ANY
    return:
     l3_status as a dictionary
    '''

    #################################################
    ##  Create L3 Stack on top of Ethernet Stack    #
    #################################################
    l3_status = ixiangpf.interface_config(**kwargs)

    if l3_status['status'] != '1':
        ErrorHandler('inerface_config', l3_status)
    else:
        ixia_print('Create L3 Stack on top of Ethernet Stack done')

    return(l3_status)

def ixia_ospf_config(**kwargs):
    '''
    Creating OSPFv2 on top of IPv4 1 stack
    Arguments:
     -handle:
       ANY -- ipv4_handle
    -mode:
       ANY -- create
    -network_type:
       ANY -- ptop
    -protocol_name:
       ANY
    -lsa_discard_mode:
       NUMERIC
    -router_interface_active
       NUMERIC
    -router_active:
       NUMERIC
    -router_id:
       ANY 
    return:
     -ospfv2_handle:
    '''
    tkwargs = {
        'mode':'create',
        'network_type':'broadcast',
        'lsa_discard_mode':'0',
        'router_interface_active':'1',
        'router_active':'1',
    }
    for key, value in kwargs.iteritems():
        tkwargs[key]=value

    #################################################
    ##  Configure OSPFv2                            #
    #################################################
    ospf_config_status = ixiangpf.emulation_ospf_config(**tkwargs)

    if ospf_config_status['status'] != '1':
        ErrorHandler('emulation_ospf_config', ospf_config_status)
    else:
        ixia_print('Configure OSPFv2 done')

    return ospf_config_status

def ixia_ospf_network_group_config(**kwargs):
    '''
    This command Configure OSPFv2 group range
    Arguments:
     -mode:
       ANY
     -protocol_handle:
       ALPHA -- deviceGroup_handle
     -protocol_name:
       ALPHA
     -connected_to_handle:
       ALPHA -- ethernet_handle
     -type:
       ALPHA -- ipv4-prefix
     -ipv4_prefix_network_address:
       ANY
     -ipv4_prefix_length:
       NUMERIC
     -ipv4_prefix_number_of_addresses:
       NUMERIC
     -ipv4_prefix_active:
       NUMERIC
     -ipv4_prefix_route_origin:
       ALPHA
    return:
       network_group_config_status
    '''

    tkwargs = {
        'type':'ipv4-prefix',
        'ipv4_prefix_length':'32',
        'ipv4_prefix_number_of_addresses':'1',
    }
    for key, value in kwargs.iteritems():
        if key == 'protocol_handle' or key == 'protocol_name' or key == 'connected_to_handle' or key == 'ipv4_prefix_network_address' or key == 'multiplier' or key == 'ipv4_prefix_network_address_step':
            tkwargs[key]=value
        else:
            tkwargs[key]=value


    #################################################
    ##  Configure OSPFv2 group range                #
    #################################################
    network_group_config_status = ixiangpf.network_group_config(**tkwargs)

    if network_group_config_status['status'] != '1':
        ErrorHandler('network_group_config', network_group_config_status)
    else:
        networkGroup_1_handle = network_group_config_status['network_group_handle']
        tkwargs = {
            'handle':networkGroup_1_handle,
            'mode':'modify',
            'ipv4_prefix_active':'1',
            'ipv4_prefix_route_origin':'another_area',
        }

        #################################################
        ##  Configure OSPFv2 group range                #
        #################################################
        ospf_network_group_config_status = ixiangpf.emulation_ospf_network_group_config(**tkwargs)

        if ospf_network_group_config_status['status'] != '1':
            ErrorHandler('emulation_ospf_network_group_config', ospf_network_group_config_status)
        else:
            ixia_print('Configure OSPFv2 group range done')

    return(network_group_config_status)



def ixia_emulation_ospf_network_group_config(**kwargs):
    '''
    This command Configure Emulation OSPF Network Group Config
    '''
#    tkwargs = {
#            'handle':networkGroup_1_handle,
#            'mode':'modify',
#            'ipv4_prefix_active':'1',
#            'ipv4_prefix_route_origin':'another_area',
#       }

    tkwargs = {
        'mode':'modify'
    }

    for key, value in kwargs.iteritems():
        tkwargs[key]=value


    #################################################
    ##  Configure OSPFv2 group range                #
    #################################################
    ospf_network_group_config_status = ixiangpf.emulation_ospf_network_group_config(**tkwargs)
    
    if ospf_network_group_config_status['status'] != '1':
        ErrorHandler('emulation_ospf_network_group_config', ospf_network_group_config_status)
    else:
        ixia_print('Configure OSPFv2 group range done')

    return(ospf_network_group_config_status)


def ixia_bgp_config(**kwargs):
    '''
    Creating bgp on top of IPv4 1 stack
    Arguments:
     -handle:
       ANY -- ipv4_handle
    -mode:
       ANY -- enable
    -network_type:
       ANY -- broadcast
    -protocol_name:
       ANY
    -router_id:
       ANY 
    return:
     -bgp handle
    '''
    tkwargs = {
        'mode':'enable'
    }
    for key, value in kwargs.iteritems():
        tkwargs[key]=value

    #################################################
    ##  Configure BGP                          #
    #################################################
    bgp_config_status = ixiangpf.emulation_bgp_config(**tkwargs)

    if bgp_config_status['status'] != '1':
        ErrorHandler('emulation_bgp_config', bgp_config_status)
    else:
        ixia_print('Configure BGP done')

    return bgp_config_status

def ixia_network_group_config(**kwargs):
    '''
    it is general network group config function
    Arguments:
     -handle:
       ANY -- ipv4_handle
    return:
     -network group handle
    '''
    tkwargs = {
    }
    for key, value in kwargs.iteritems():
        tkwargs[key]=value

    #################################################
    ##  Configure Network Group Config              #
    #################################################
    network_group_config_status = ixiangpf.network_group_config(**tkwargs)

    if network_group_config_status['status'] != '1':
        ErrorHandler('network_group_config_status', network_group_config_status)
    else:
        ixia_print('Configure Network Group Config Done')

    return network_group_config_status


def ixia_bgp_route_config(**kwargs):
    '''
    Creating bgp on top of IPv4 1 stack
    Arguments:
     -handle:
       ANY -- ipv4_handle
    -mode:
       ANY -- enable
    return:
     -bgp route handle
    '''
    tkwargs = {
        'mode':'create'
    }
    for key, value in kwargs.iteritems():
        tkwargs[key]=value

    #################################################
    ##  Configure BGP Route                         #
    #################################################
    bgp_route_config_status = ixiangpf.emulation_bgp_route_config(**tkwargs)

    if bgp_route_config_status['status'] != '1':
        ErrorHandler('emulation_bgp_config_route', bgp_route_config_status)
    else:
        ixia_print('Configure BGP Route done')

    return bgp_route_config_status

def ixia_isis_config(**kwargs):
    '''
    Creating ISIS Config
    Arguments:
     -handle:
       ANY -- ipv4_handle
    -mode:
       ANY -- enable
    -network_type:
       ANY -- broadcast
    -protocol_name:
       ANY
    -router_id:
       ANY 
    return:
     -isis handle
    '''
    tkwargs = {
        'mode':'create'
    }
    for key, value in kwargs.iteritems():
        tkwargs[key]=value

    #################################################
    ##  Configure ISIS                          #
    #################################################
    isis_config_status = ixiangpf.emulation_isis_config(**tkwargs)

    if isis_config_status['status'] != '1':
        ErrorHandler('isis_config_status', isis_config_status)
    else:
        ixia_print('Configure ISIS done')

    return isis_config_status


def ixia_isis_network_group_config(**kwargs):
    '''
    Creating Or Modifying Routes for ISIS
    Arguments:
     -handle:
       ANY -- ISIS Handle
    return:
     -IsIs Handle
    '''
    tkwargs = {
        'mode':'create'
    }
    for key, value in kwargs.iteritems():
        tkwargs[key]=value

    #################################################
    ##  Configure ISIS Network Group Config                        
    #################################################
    isis_network_group_config_status = ixiangpf.emulation_isis_network_group_config(**tkwargs)

    if isis_network_group_config_status['status'] != '1':
        ErrorHandler('isis_network_group_config_status', isis_network_group_config_status)
    else:
        ixia_print('Configure ISIS Network Group Done')

    return isis_network_group_config_status

def ixia_emulation_isis_info(**kwargs):
    '''
    Retrieving Ixia learned IS-IS Info
    Arguments:
     -handle:
       ANY -- ISIS Handle
    return:
     -Dictionary Of All Learned Info 
    '''
    tkwargs = {
        'mode':'stats'
    }
    for key, value in kwargs.iteritems():
        tkwargs[key]=value

    #################################################
    ##  Configure ISIS Info                        
    #################################################
    isis_info = ixiangpf.emulation_isis_info(**tkwargs)

    if isis_info ['status'] != '1':
        ErrorHandler('isis_info fails', isis_info)
    else:
        ixia_print('Retrieved ISIS Info')

    return isis_info



def ixia_multivalue_config_with_double_values_for_single_arg(**kwargs):
    '''
   	ixia_multivalue_config_with_double_values_for_single_arg
    '''
    tkwargs = {
    }
    for key, value in kwargs.iteritems():
    	if key == 'nest_step_1' or key == 'nest_step_2':
            temp_key = 'nest_step'
            nest_step_1_value = kwargs['nest_step_1']
            nest_step_2_value = kwargs['nest_step_2']
            tkwargs[temp_key] = '%s,%s' % (nest_step_1_value,nest_step_2_value)
    	elif key == 'nest_owner_1' or key == 'nest_owner_2':
    	    temp_key = 'nest_owner'
    	    nest_owner_value_1 = kwargs['nest_owner_1']
    	    nest_owner_value_2 = kwargs['nest_owner_2']
    	    tkwargs[temp_key] = '%s,%s' % (nest_owner_value_1,nest_owner_value_2)
    	elif key == 'nest_enabled_1' or key == 'nest_enabled_2':
    	    temp_key = 'nest_enabled'
    	    nest_enabled_value_1 = kwargs['nest_enabled_1']
    	    nest_enabled_value_2 = kwargs['nest_enabled_2']
    	    tkwargs[temp_key] = '%s,%s' % (nest_enabled_value_1,nest_enabled_value_2)
    	else:
    	    tkwargs[key] = value
    #################################################
    ##  Configure Multivalue With Custom Nest Values #
    #################################################
    multivalue_config_status = ixiangpf.multivalue_config(**tkwargs)

    if multivalue_config_status['status'] != '1':
        ErrorHandler('ixia_multivalue_config_bgp', multivalue_config_status)
    else:
        ixia_print('ixia_multivalue_config_bgp done')

    return(multivalue_config_status)




def ixia_control_protocol(**kwargs):
    '''
    This command control LDP protocol
    Arguments:
     -handle:
       ALPHA -- topology_handle
     -action:
       ALPHA -- start_protocol
    return:
       none
    '''
    tkwargs = {
        'action':'start_protocol',
    }
    for key, value in kwargs.iteritems():
        tkwargs[key]=value

    #################################################
    ##  Control protocol                            #
    #################################################
    test_control_status = ixiangpf.test_control(**tkwargs)

    if test_control_status['status'] != '1':
        ErrorHandler('test_control', test_control_status)

def ixia_show_ospf_info(**kwargs):
    '''
    This command display osfp protocol learned info
    Arguments:
     -handle:
       ALPHA -- ospfv2_handle
     -mode:
       ALPHA -- learned_info
    return:
       none
    '''
    tkwargs = {
        'mode':'learned_info',
    }
    for key, value in kwargs.iteritems():
        tkwargs[key]=value

    #################################################
    ##  Display OSPF protocol learned info          #
    #################################################
    ospf_info_status = ixiangpf.emulation_ospf_info(**tkwargs)

    if ospf_info_status['status'] != '1':
        ErrorHandler('emulation_ospf_info', ospf_info_status)
    else:
        ixia_print(ospf_info_status)

def ixia_emulation_dhcp_server_config(**kwargs):
    '''
    This command configure emulate dhcp server
    Arguments:
     -dhcp_offer_router_address:
       ANY
     -handle:
       ANY
     -ipaddress_pool:
       ANY
    return:
     -ping_status
    '''
    tkwargs = {
        'ip_dns1':"0.0.0.0",
        'ip_dns2':"0.0.0.0",
        'ip_version':"4",
        'ipaddress_count':"10",
        'ipaddress_pool_prefix_length':"24",
        'ipaddress_pool_prefix_inside_step':"0",
        'lease_time':"86400",
        'mode':"create",
        'protocol_name':"""DHCPv4 Server 1""",
        'use_rapid_commit':"0",
        'echo_relay_info':"1",
        'pool_address_increment':"0.0.0.1",
        'subnet_addr_assign':"0",
        'subnet':"relay",
    }
    for key, value in kwargs.iteritems():
        tkwargs[key]=value

    #####################################################
    ##  ping host                                       #
    #####################################################
    dhcp_server_status = ixiangpf.emulation_dhcp_server_config(**tkwargs)

    if dhcp_server_status['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('emulation_dhcp_server_config', dhcp_server_status)
    else:
        ixia_print('Configure emulation dhcp server done')

    return(dhcp_server_status)

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
        'protocol_name':"""DHCPv4 Client 1""",
        'dhcp4_broadcast':"0",
        'dhcp4_gateway_address':"0.0.0.0",
        'dhcp4_gateway_mac':"00.00.00.00.00.00",
    }
    for key, value in kwargs.iteritems():
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

def ixia_emulation_dhcp_config(**kwargs):
    '''
    This command configure emulate dhcp
    Arguments:
    '''
    tkwargs = {
                'handle':"/globals",
		'mode':"create",
		'msg_timeout':"4",
		'outstanding_releases_count':"400",
		'outstanding_session_count':"400",
		'release_rate':"200",
		'request_rate':"200",
		'retry_count':"3",
		'client_port':"68",
		'start_scale_mode':"port",
		'stop_scale_mode':"port",
		'interval_stop':"1000",
		'interval_start':"1000",
		'enable_restart':"0",
		'enable_lifetime':"0",
		'unlimited_restarts':"0",
		'server_port':"67",
		'msg_timeout_factor':"2",
		'msg_max_timeout':"64",
		'override_global_setup_rate':"1",
		'override_global_teardown_rate':"1",
		'skip_release_on_stop':"0",
		'renew_on_link_up':"0",
		'ip_version':"4",
		'dhcp4_arp_gw':"0",
    }
    for key, value in kwargs.iteritems():
        tkwargs[key]=value

    #####################################################
    ##  ping host                                       #
    #####################################################
    dhcp_status = ixiangpf.emulation_dhcp_config(**tkwargs)

    if dhcp_status['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('emulation_dhcp_config', dhcp_status)
    else:
        ixia_print('Configure Emulation dhcp done')

    return(dhcp_status)

def ixia_emulation_dhcp_stats(**kwargs):
    '''
    This command configure emulate dhcp
    Arguments:
    '''
    tkwargs = {
                'handle':"/globals",
                'mode':"session",
    		'dhcp_version':"dhcp4"
    }
    for key, value in kwargs.iteritems():
        tkwargs[key]=value

    #####################################################
    ##  ping host                                       #
    #####################################################
    dhcp_status = ixiangpf.emulation_dhcp_stats(**tkwargs)

    if dhcp_status['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('emulation_dhcp_stats', dhcp_status)
    else:
        ixia_print('Stats DHCP is Success')

    return(dhcp_status)

def ixia_ipv4_arp_config():
    '''
    This command configure global options for ipv4 arp
    Arguments:
       None
    return:
     config info in a dictionary
    '''

    kwargs = {}
    kwargs['protocol_handle']='/globals'
    kwargs['arp_on_linkup']=1
    kwargs['single_arp_per_gateway']=1
    kwargs['ipv4_send_arp_rate']=200
    kwargs['ipv4_send_arp_interval']=1000
    kwargs['ipv4_send_arp_max_outstanding']=400
    kwargs['ipv4_send_arp_scale_mode']='port'
    kwargs['ipv4_attempt_enabled']=0
    kwargs['ipv4_attempt_rate']=200
    kwargs['ipv4_attempt_interval']=1000
    kwargs['ipv4_attempt_scale_mode']='port'
    kwargs['ipv4_diconnect_enabled']=0
    kwargs['ipv4_disconnect_rate']=200
    kwargs['ipv4_disconnect_interval']=1000
    kwargs['ipv4_disconnect_scale_mode']='port'

    #################################################
    ##  Create global Arp  service                  #
    #################################################
    global_arp_config_status = ixiangpf.interface_config(**kwargs)

    if global_arp_config_status['status'] != '1':
        ErrorHandler('interface_config', global_arp_config_status)
    else:
        ixia_print('Configure a global Arp service for Ipv4 done')

    return(global_arp_config_status)

def ixia_ipv6_arp_config():
    '''
    This command configure global options for ipv6 arp
    Arguments:
       None
    return:
     config info in a dictionary
    '''

    kwargs = {}
    kwargs['protocol_handle']='/globals'
    kwargs['arp_on_linkup']=1
    kwargs['single_ns_per_gateway']=1
    kwargs['ipv6_send_ns_rate']=200
    kwargs['ipv6_send_ns_interval']=1000
    kwargs['ipv6_send_ns_max_outstanding']=400
    kwargs['ipv6_send_ns_scale_mode']='port'
    kwargs['ipv6_attempt_enabled']=0
    kwargs['ipv6_attempt_rate']=200
    kwargs['ipv6_attempt_interval']=1000
    kwargs['ipv6_attempt_scale_mode']='port'
    kwargs['ipv6_diconnect_enabled']=0
    kwargs['ipv6_disconnect_rate']=200
    kwargs['ipv6_disconnect_interval']=1000
    kwargs['ipv6_disconnect_scale_mode']='port'

    #################################################
    ##  Create global Arp  service                  #
    #################################################
    global_arp_config_status = ixiangpf.interface_config(**kwargs)

    if global_arp_config_status['status'] != '1':
        ErrorHandler('interface_config', global_arp_config_status)
    else:
        ixia_print('Configure a global Arp service for Ipv6 done')

    return(global_arp_config_status)

def ixia_ethernet_config(**kwargs):
    '''
    This command configure global options for ethernet
    Arguments:
       phy_mode: copper/fiber
    return:
     config info in a dictionary
    '''
    tkwargs = {
        'protocol_handle':'/globals',
        'ethernet_attempt_enabled':0,
        'ethernet_attempt_rate':100,
        'ethernet_attempt_interval':999,
        'ethernet_attempt_scale_mode':'port',
        'ethernet_diconnect_enabled':0,
        'ethernet_disconnect_rate':100,
        'ethernet_disconnect_interval':999,
        'ethernet_disconnect_scale_mode':'port',
        'phy_mode':'copper',
    }
    for key, value in kwargs.iteritems():
        tkwargs[key]=value

    #################################################
    ##  Create global Arp  service                  #
    #################################################
    ethernet_global_status = ixiangpf.interface_config(**tkwargs)

    if ethernet_global_status['status'] != '1':
        ErrorHandler('interface_config', ethernet_global_status)
    else:
        ixia_print('Configure ethernet done')

    return(ethernet_global_status)



def return_ixia_protocol_info():

    protocol_info = ixiangpf.protocol_info(
	mode = 'aggregate',
    )

    if protocol_info['status'] != IxiaHlt.SUCCESS:
    	ErrorHandler('protocol_info', protocol_info)

    return(protocol_info)


def ixia_stop_protocols_with_params(**kwargs):
    '''
    This command configure starts all protocol(s)
    Arguments:
       handle
    return:
     config info in a dictionary
    '''

    tkwargs = {}
    for key, value in kwargs.iteritems():
        tkwargs[key]=value
        temp_string = str(key)+":"+str(value)
        ixia_print(temp_string)
        tkwargs['action']='stop_protocol'

    #################################################
    ##  Stop Protocol                 #
    #################################################
    test_control_status = ixiangpf.test_control(**tkwargs)

    if test_control_status['status'] != '1':
        ErrorHandler('test_control', test_control_status)
    else:
        ixia_print('ixia_stop_protocols_with_params Done')
   
    return(test_control_status)

def ixia_start_protocols_with_params(**kwargs):
    '''
    This command configure starts all protocol(s)
    Arguments:
       None
    return:
     config info in a dictionary
    '''

    tkwargs = {}
    for key, value in kwargs.iteritems():
        tkwargs[key]=value
        temp_string = str(key)+":"+str(value)
        ixia_print(temp_string)
        tkwargs['action']='start_protocol'

    #################################################
    ##  Create global Arp  service                  #
    #################################################
    test_control_status = ixiangpf.test_control(**tkwargs)

    if test_control_status['status'] != '1':
        ErrorHandler('test_control', test_control_status)
    else:
        ixia_print('ixia_start_protocols_with_params Done')

    return(test_control_status)

def ixia_start_protocols(loop_count=20):
    '''
    This command configure starts all protocol(s)
    Arguments:
       None
    return:
     config info in a dictionary
    '''

    kwargs = {}
    kwargs['action']='start_all_protocols'

    #################################################
    ##  Create global Arp  service                  #
    #################################################
    test_control_status = ixiangpf.test_control(**kwargs)

    if test_control_status['status'] != '1':
        ErrorHandler('test_control', test_control_status)
    else:
        ixia_print('ixia_start_protocols Waiting for sessions to come up')

    iter_count = int(loop_count)
    not_all_sessions_up = 1
    while (iter_count and not_all_sessions_up):
        ixia_print("Waiting for sessions to come up %s" % iter_count)
        protocol_info = ixiangpf.protocol_info(
            mode = 'aggregate',
        )
        if protocol_info['status'] != IxiaHlt.SUCCESS:
            ErrorHandler('protocol_info', protocol_info)

        protocol_info.pop('status')
        keys = protocol_info.viewkeys()
        protocols_notup_list = []
        protocols_except_list = []
        not_all_sessions_up = 0
        for key in keys:
            try:
                up_count = protocol_info[key]['aggregate']['sessions_up']
                total_count = protocol_info[key]['aggregate']['sessions_total']
                if up_count < total_count:
                        ixia_print("key: %s, Not all sessions are up. (Session Up: %s, Session Total: %s) wait 5 seconds...." % (key, up_count, total_count))
                        not_all_sessions_up = 1
                        protocols_notup_list.append(key)
                else:
                    ixia_print("key: %s All sessions are up" % key)
            except:
                protocols_except_list.append(key)
        time.sleep(5)
        iter_count = iter_count - 1

    if protocols_except_list != []:
        ixia_print("Protocols with no sessions_up or sessions_total: %s" % protocols_except_list)

    if iter_count == 0 and protocols_notup_list != []:
        ixia_print("Protocols did not come up fully: %s Giving up..." % protocols_notup_list)
        test_control_status['log'] = 'Not all protocol sessions are up'
        test_control_status['status'] = '0'
    else:
        ixia_print("All sessions on all protocols are up")
        test_control_status['status'] = '1'

    return(test_control_status)

def ixia_start_protocols_without_check_status():
    '''
    This command configure starts all protocol(s)
    Arguments:
       None
    return:
     config info in a dictionary
    '''

    kwargs = {}
    kwargs['action']='start_all_protocols'

    ixia_print("ixia_start_protocols_without_check_status - Start Protocols started")

    test_control_status = ixiangpf.test_control(**kwargs)

    ixia_print("ixia_start_protocols_without_check_status - Start Protocols Done ")

    return(test_control_status)

def ixia_wait_all_sessions_up(protocol_handles, totalTime=5):
    '''
    This command configure starts all protocol(s)
    Arguments:
       protocol_handles
       totalTime
    return:
       1: success, 0 fail
    '''
    bad_protocol_handles = []
    protocol_handles_list = protocol_handles.split()
    for protocol_handle in protocol_handles_list:
        for timer in range(0, totalTime):
            sessionStatus = ixiangpf.protocol_info(
                handle=protocol_handle,
                mode = 'aggregate',
            )
            currentSessionUp = sessionStatus[protocol_handle]['aggregate']['sessions_up']
            totalSessions = sessionStatus[protocol_handle]['aggregate']['sessions_total']
            ixia_print('Verifying protocol sessions', protocol_handle)
            ixia_print('%s/%s: CurrentSessionUp:%s TotalSessions:%s\n' % (timer, totalTime, currentSessionUp, totalSessions))
            if timer < totalTime and currentSessionUp != totalSessions:
                time.sleep(5)
                continue
            if timer < totalTime and currentSessionUp == totalSessions:
                ixia_print('All sessions in protocol_handle %s are UP. ' % protocol_handle)
                break
            if timer == totalTime and currentSessionUp != totalSessions:
                wait_timer = timer * 5
                ixia_print('Error: %s: It has been %s seconds and total sessions are not all UP. ' % (protocol_handle, wait_timer))
                bad_protocol_handles.append(protocol_handle)
    if len(bad_protocol_handles) == 0:
        return(1)
    else:
        return(0)

def ixia_stop_protocols():
    '''
    This command configure stop all protocol(s)
    Arguments:
       None
    return:
     config info in a dictionary
    '''

    kwargs = {}
    kwargs['action']='stop_all_protocols'

    #################################################
    ##  Create global Arp  service                  #
    #################################################
    test_control_status = ixiangpf.test_control(**kwargs)

    if test_control_status['status'] != '1':
        ErrorHandler('test_control', test_control_status)
    else:
        ixia_print('Stop all protocols done')

    return(test_control_status)

def ixia_send_arp_req(protocol_handle):
    '''
    This command configure sends arp request
    Arguments:
       -protocol_handle:
        interface handler
    return:
     config info in a dictionary
    '''

    kwargs = {}
    kwargs['protocol_handle']=protocol_handle
    kwargs['arp_send_req']=1

    #################################################
    ##  Create global Arp  service                  #
    #################################################
    api_status = {'status':0}
    for i in range(20):
        arp_status = ixiangpf.interface_config(**kwargs)

        if arp_status['status'] != '1':
            ErrorHandler('interface_config', arp_status)
        else:
            ixia_print('sends out arp request done')
            
        if arp_status[protocol_handle]['arp_request_success'] != IxiaHlt.SUCCESS:
            try:
                 interfaces_not_started = arp_status[protocol_handle]['arp_interfaces_not_started']
                 ixia_print("Interfaces not started: %s, please wait...." % interfaces_not_started)
            except:
                 try:
                     arp_failed_item_handles = arp_status[protocol_handle]['arp_failed_item_handles']
                     ixia_print("Arp failed on: %s" %  arp_failed_item_handles)
                 except:
                     ixia_print("arp_request_success is 0, but neither arp_interfaces_not_started nor arp_failed_item_handles key is returned")
            time.sleep(5)
        else:
            ixia_print("ARP succeeded on %s" % protocol_handle)
            api_status = {'status':1}
            break

    if arp_status[protocol_handle]['arp_request_success'] != IxiaHlt.SUCCESS:
        ixia_get_diag_file()

    return(api_status)

def ixia_traffic_config(**kwargs):
    '''
    This command configures Traffic stream
    Arguments:
     -src_handle:
       ALPHA
     -dst_handle:
       ALPHA
     others
       ANY (check IXIA HLAPI traffic_config API manual for detail)
    Default:
     'mode':'create',
     'endpointset_count':1,
     'src_dest_mesh':'one_to_one',
     'route_mesh':'one_to_one',
     'bidirectional':1,
     'name':'Traffic_Item_1',
     'circuit_endpoint_type':'ipv4',
     'frame_size':64,
     'rate_mode':'percent',
     'rate_percent':2,
     'track_by':'endpoint_pair'
    '''

    tkwargs = {
        'mode':'create',
        'endpointset_count':1,
        'src_dest_mesh':'one_to_one',
        'route_mesh':'one_to_one',
        'bidirectional':1,
        'name':'Traffic_Item_1',
        'circuit_endpoint_type':'ipv4',
        'frame_size':64,
        'rate_mode':'percent',
        'rate_percent':2,
        'track_by':'endpoint_pair'
    }
    for key, value in kwargs.iteritems():
        temp_string = str(key)+":"+str(value)
        logger.console('\t%s' % temp_string)
        if re.search('port_handle', key):
            tkwargs[key]='%s/%s' % (1, value)
        elif re.search('frame_rate', key):
            mode,rate=value.split(':')
            if mode == 'percent':
                tkwargs['rate_mode']='percent'
                tkwargs['rate_percent']=rate
            elif mode == 'pps':
                tkwargs['rate_mode']='pps'
                tkwargs['rate_pps']=rate
            elif mode == 'bps':
                tkwargs['rate_mode']='bps'
                tkwargs['rate_bps']=rate		
            else:
                tkwargs[key]=value

    #################################################
    ##  Create Create Traffic                       #
    #################################################
    traffic_config_status = ixiangpf.traffic_config(**tkwargs)

    if traffic_config_status['status'] != '1':
        ErrorHandler('traffic_config', traffic_config_status)
    else:
        ixia_print('Create Traffic stream done')

    return(traffic_config_status)

def ixia_burst_traffic_config(**kwargs):
    '''
    This command configures Burts Traffic stream
    Arguments:
     -src_handle:
       ALPHA
     -dst_handle:
       ALPHA
     others
       ANY (check IXIA HLAPI traffic_config API manual for detail)
    Default:
     'mode':'create',
     'endpointset_count':1,
     'src_dest_mesh':'one_to_one',
     'route_mesh':'one_to_one',
     'bidirectional':1,
     'name':'Traffic_Item_1',
     'circuit_endpoint_type':'ipv4',
     'frame_size':64,
     'rate_mode':'percent',
     'rate_percent':2,
     'burst_loop_count':1,
     'inter_burst_gap':100,
    '''

    tkwargs = {
        'mode':'create',
        'endpointset_count':1,
        'src_dest_mesh':'one_to_one',
        'route_mesh':'one_to_one',
        'bidirectional':1,
        'name':'Traffic_Item_1',
        'circuit_endpoint_type':'ipv4',
        'frame_size':64,
        'rate_mode':'percent',
        'rate_percent':2,
        'burst_loop_count':1,
        'inter_burst_gap':100,
        'pkts_per_burst':10000,
        'track_by':'endpoint_pair',
    }
    for key, value in kwargs.iteritems():
        if re.search('port_handle', key):
            tkwargs[key]='%s/%s' % (1, value)
        else:
            tkwargs[key]=value

    #################################################
    ##  Create Create Traffic                       #
    #################################################
    traffic_config_status = ixiangpf.traffic_config(**tkwargs)

    if traffic_config_status['status'] != '1':
        ErrorHandler('traffic_config', traffic_config_status)
    else:
        ixia_print('Create Burst Traffic stream done')

    return(traffic_config_status)

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
    for key, value in kwargs.iteritems():
        tkwargs[key]=value

    #################################################
    ##  Create Create Traffic                       #
    #################################################
    traffic_config_status = ixiangpf.traffic_config(**tkwargs)

    if traffic_config_status['status'] != '1':
        tprint(f"ixia_remove_traffic_config: status = {traffic_config_status}")
        #ErrorHandler('traffic_config', traffic_config_status)
    else:
        ixia_print('Remove Traffic Stream done')

    return(traffic_config_status)

def ixia_regenerate():
    '''
    This command sends regenerate action
    Arguments:
     -action: regenerate
    '''

    kwargs={}
    kwargs['action']='regenerate'

    #################################################
    ##  Create Create Traffic                       #
    #################################################
    traffic_control_status = ixiangpf.traffic_control(**kwargs)

    if traffic_control_status['status'] != '1':
        ErrorHandler('traffic_control -action regenerate', traffic_control_status)
    else:
        ixia_print('Send regenerate done')

    return(traffic_control_status)

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

def ixia_start_traffic(**kwargs):
    '''
    This command apply & Start the traffic
    Arguments:
     -max_wait_timer:
       NUMERIC
     -handle:
       ANY
    '''

    tkwargs = {
        'action':'run',
        'max_wait_timer':120,
    }
    for key, value in kwargs.iteritems():
        tkwargs[key]=value

    #################################################
    ##  Create Create Traffic                       #
    #################################################
    traffic_control_status = ixiangpf.traffic_control(**tkwargs)
    time.sleep(2)

    if traffic_control_status['status'] != '1':
        ErrorHandler('traffic_control -action run', traffic_control_status)

    if tkwargs['max_wait_timer'] != 0:
        if traffic_control_status['stopped'] == '1':
            ixia_print("traffic is not started yet... Give poll for the traffic status for another 60 seconds\n")
            count = 60
            waitTime = 0
            while True:
                traffic_poll_status = ixiangpf.traffic_control(
                    action = 'poll',
                )
                if traffic_poll_status['stopped'] == '1':
                    if count == 0:
                        break
                    else:
                        time.sleep(2)
                        count -= 1
                        waitTime += 2
                else:
                    break

            if traffic_poll_status['stopped'] == '1':
                ErrorHandler('traffic_control', traffic_control_status)
            else:
                ixia_print('traffic is started (wait time=%s seconds)' % waitTime)
        else:
            ixia_print('traffic is started')

    return(traffic_control_status)

def ixia_apply_traffic(**kwargs):
    '''
    This command apply traffic
    Arguments:
     -max_wait_timer:
       NUMERIC
     -handle:
       ANY
    '''

    tkwargs = {
        'action':'apply',
        'max_wait_timer':120,
    }
    for key, value in kwargs.iteritems():
        tkwargs[key]=value

    #################################################
    ##  Create Create Traffic                       #
    #################################################
    traffic_control_status = ixiangpf.traffic_control(**tkwargs)

    if traffic_control_status['status'] != '1':
        ErrorHandler('traffic_control -action apply', traffic_control_status)
    else:
        ixia_print('traffic apply complete')

    return(traffic_control_status)

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

def ixia_clear_traffic():
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
        ixia_print('traffic clear is done')

    return(traffic_control_status)

def ixia_traffic_stats(port):
    '''
    This command Collecting traffic Stats for a port
    Arguments:
     -mode:
       ALPHA
    '''

    kwargs={}
    kwargs['mode']='aggregate'

    #################################################
    ##  Create Create Traffic                       #
    #################################################
    traffic_stats = ixiangpf.traffic_stats(**kwargs)

    port = '%s/%s' % (1, port)

    if traffic_stats['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('traffic_stats', traffic_stats)
    else:
        tx_count = traffic_stats[port]['aggregate']['tx']['pkt_count']
        if tx_count == 'N/A':
            tx_count = 0
        rx_count = traffic_stats[port]['aggregate']['rx']['pkt_count']
        if rx_count == 'N/A':
            rx_count = 0
        tx_total_count = traffic_stats[port]['aggregate']['tx']['total_pkts']
        if tx_total_count == 'N/A':
            tx_total_count = 0
        rx_total_count = traffic_stats[port]['aggregate']['rx']['total_pkts']
        if rx_total_count == 'N/A':
            rx_total_count = 0
        tx_byte_rate = traffic_stats[port]['aggregate']['tx']['pkt_byte_rate']
        rx_byte_rate = traffic_stats[port]['aggregate']['rx']['pkt_byte_rate']
        tx_pkt_rate = traffic_stats[port]['aggregate']['tx']['total_pkt_rate']
        rx_pkt_rate = traffic_stats[port]['aggregate']['rx']['raw_pkt_rate']
        raw_pkt_count = traffic_stats[port]['aggregate']['rx']['raw_pkt_count']

    traffic_stats = {
        'status':1,
        'tx_count':tx_count,
        'rx_count':rx_count,
        'tx_total_count':tx_total_count,
        'rx_total_count':rx_total_count,
        'tx_byte_rate':tx_byte_rate,
        'rx_byte_rate':rx_byte_rate,
        'tx_pkt_rate':tx_pkt_rate,
        'rx_pkt_rate':rx_pkt_rate,
        'raw_pkt_count':raw_pkt_count,
    }
    return(traffic_stats)

def ixia_flow_stats(flow, port):
    '''
    This command Collecting Flow Stats for a port
     -flowe:
       NUMERIC
     -flowe:
       port
    '''

    kwargs={}
    kwargs['mode']='flow'

    #################################################
    ##  Create Create Traffic                       #
    #################################################
    flow_stats = ixiangpf.traffic_stats(**kwargs)

    flow = '%s/%s' % (1, flow)

    if flow_stats['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('flow_stats', flow_stats)
    else:
        find_flow_count = 0
        for fn in flow_stats['flow']:
            if flow_stats['flow'][fn]['flow_name'] == flow:
                flow_count = flow_stats['flow'][fn][port]
                find_flow_count = 1
                break
        if find_flow_count == 0:
            ErrorHandler('flow_stats', flow_stats)

    flow_stats = {
        'status':1,
        'flow_count':flow_count,
    }
    return(flow_stats)

def ixia_tracking_stats():
    '''
    This command Collecting tracking Stats for a port
    '''
    kwargs = {
        'mode':'user_defined_stats',
        'uds_type':'l23_traffic_flow',
        'uds_action':'get_available_traffic_item_filters',
    }
    #################################################
    ##  Create flow stats
    #################################################
    flow_stats = ixiangpf.traffic_stats(**kwargs)

    if flow_stats['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('flow_stats', flow_stats)
    else:
        ti_filters_list = flow_stats['filters']
        kwargs = {
            'mode':'user_defined_stats',
            'uds_type':'l23_traffic_flow',
            'uds_action':'get_available_tracking_filters',
        }
        #################################################
        ##  Create flow stats
        #################################################
        tracking_stats = ixiangpf.traffic_stats(**kwargs)
        if tracking_stats['status'] != IxiaHlt.SUCCESS:
            ErrorHandler('tracking_stats', tracking_stats)
        else:
            tracking_filters_list = tracking_stats['filters']
            kwargs = {
                'mode':'user_defined_stats',
                'uds_type':'l23_traffic_flow',
                'uds_action':'get_stats',
                'uds_traffic_item_filter':ti_filters_list,
                'uds_tracking_filter':tracking_filters_list,
                'uds_tracking_filter_count':len(tracking_filters_list),
                'uds_l23tf_egress_latency_bin_display':'show_egress_rows',
                'uds_l23tf_filter_type':'enumeration',
                'uds_l23tf_enumeration_sorting_type':'ascending',
                'uds_l23tf_aggregated_across_ports':0,
            }
            traffic_stats = ixiangpf.traffic_stats(**kwargs)
            if traffic_stats['status'] != IxiaHlt.SUCCESS:
                ErrorHandler('traffic_stats', traffic_stats)
            else:
                rowCount = traffic_stats['row_count']
                stat_name_list = ['Tx Port', 'Egress Tracking', 'Rx Frames', 'Rx Frame Rate']
                values_dict = dict()
                cnt = 0
                for i in range(1, int(rowCount)+1):
                    index = str(i)
                    stats = traffic_stats[index]
                    cnt_str = str(cnt)
                    values_dict[cnt_str]= []
                    for stat_name in stat_name_list:
                        values_dict[cnt_str].append(stats[stat_name])
                    cnt += 1
    return(values_dict)

def ixia_traffic_packets(port, ptype, count_title):
    '''
    This command Collecting packets counts
    Arguments:
     -mode:
       ALPHA
    '''

    kwargs={}
    kwargs['mode']='aggregate'

    #################################################
    ##  Create Create Traffic                       #
    #################################################
    traffic_stats = ixiangpf.traffic_stats(**kwargs)

    port = '%s/%s' % (1, port)

    if traffic_stats['status'] != IxiaHlt.SUCCESS:
        ErrorHandler('traffic_stats', traffic_stats)
    else:
        packet_count = traffic_stats[port]['aggregate'][ptype][count_title]
        if packet_count == 'N/A':
            packet_count = 0

    traffic_stats = {
        'status':1,
        'packet_count':packet_count,
    }
    return(traffic_stats)

def ixia_traffic_pkts(**kwargs):
    '''
    This command returns packages
    Arguments:
     -traffic_stats data (dictionalry)
     -port:
      tx
      rt
     return:
      package count
    '''

    #################################################
    ##  Create Create Traffic                       #
    #################################################
    port = str(kwargs['port'])

    port = '%s/%s' % (1, port)

    traffic_item_name = str(kwargs['traffic_item_name'])
    traffic_stats = kwargs['traffic_stats']
    return(traffic_stats['traffic_item'][traffic_item_name][port]['total_pkts'])

def PacketDiff(traffic1, traffic2, perc):
    '''
    This API compares the difference of first packets with seconds. Returns 1 if
    the difference is within perc. Otherwise, returns 0
    '''
    func_name = PacketDiff.__name__
    try:
        status_data = {'status':0}
        if type(traffic1) != float:
            traffic1 = float(traffic1)
        if type(traffic2) != float:
            traffic2 = float(traffic2)
        if type(perc) != float:
            perc = float(perc)
        if perc > 1.0 or perc <= 0.0:
            raise Exception('Invalid perc %s, it has to be in the range of 1.0 < perc > 0.0' % perc)
        if traffic1 == 0.0:
            raise Exception('Invalid traffic1. It cannot be 0')
        if traffic2 == 0.0:
            raise Exception('Invalid traffic2. It cannot be 0')
        if traffic1 >= traffic2:
            pc = traffic2/traffic1
        else:
            pc = traffic1/traffic2
        if pc >= perc:
            result = 1
        else:
            result = 0
        status_data = {'status':1, 'result':result}
    except Exception as msg:
        e = '%s Exception: %s' % (func_name, msg)
        status_data = {'status':0, 'result':e}
    except:
        e = '%s, Unexpected error: %s' % (func_name, sys.exc_info()[0])
        status_data = {'status':0, 'result':e}
    finally:
        return(status_data)

def ixia_get_resolved_mac(handle):
    '''
    This API returns resolved Gateway Mac
    '''
    func_name = ixia_get_resolved_mac.__name__
    try:
        status_data = {'status':0}
        resolved_mac_list = ixiangpf.ixnet.getAttribute(handle, 'resolvedGatewayMac')
        status_data = {'status':1, 'resolvedGatewayMac':resolved_mac_list}
    except:
        e = '%s, Unexpected error: %s' % (func_name, sys.exc_info()[0])
        status_data = {'status':0, 'resolvedGatewayMac':e}
    finally:
        return(status_data)

def ixia_enable_capture(**kwargs):
    '''
    Enable capture
    Arguments:
     -port_handle:
       ANY
     -data_plane_capture_enable:
       CHOICES 0 1
     -control_plane_capture_enable:
       CHOICES 0 1
     -slice_size:
       NUMERIC
     -capture_mode:
       trigger
     -trigger_position:
       NUMERIC
     -after_trigger_filter:
       ANY
     -before_trigger_filter:
       ANY
     -continuous_filter:
       ANY
    '''
    tkwargs = {
	'data_plane_capture_enable':0,
	'control_plane_capture_enable':0,
	'slice_size':0,
	'capture_mode':'trigger',
	'trigger_position':1,
	'after_trigger_filter':'all',
	'before_trigger_filter':'all',
	'continuous_filter':'filter',
	'trigger_position':1,

	
    }
    for key, value in kwargs.iteritems():
        if key == 'port_handle':
            tkwargs[key]='%s/%s' % (1, value)
        else:
            tkwargs[key]=value

    #################################################
    ##  Enable capture
    #################################################
    enable_capture_status = ixiangpf.packet_config_buffers(**tkwargs)

    if enable_capture_status['status'] != '1':
        ErrorHandler('enable_capture', enable_capture_status)
    else:
        ixia_print('enable_capture done')

    return(enable_capture_status)

def ixia_start_capture(**kwargs):
    '''
    Enable capture
    Arguments:
     -port_handle:
       ANY
    '''
    tkwargs = {
        'action':'start',
    }
    for key, value in kwargs.iteritems():
        if key == 'port_handle':
            tkwargs[key]='%s/%s' % (1, value)
        else:
            tkwargs[key]=value

    #################################################
    ##  Enable capture
    #################################################
    start_capture_status = ixiangpf.packet_control(**tkwargs)

    if start_capture_status['status'] != '1':
        ErrorHandler('start_capture', start_capture_status)
    else:
        ixia_print('start_capture done')

    return(start_capture_status)

def _ixia_captureState(vport, capture_type):
    '''
        Check the status of capturing returns: ready - if all packets have been uploaded on client, notReady - if packet uploading is in progress
        Parameters:
           -vport object.  Ex: '/vport:1', '::ixNet::OBJ-/vport:1'
           capture_type - data or control
        Return:
           ready - if all packets have been uploaded on client
           notReady - if packet uploading is in progress
    '''
    # vport - vport object.  Ex: '/vport:1', '::ixNet::OBJ-/vport:1'
    attribute_name = '-'+capture_type.lower()+'CaptureState'
    capture_state = ixiangpf.ixnet.getAttribute(vport+'/capture', attribute_name)
    return(capture_state)

def _ixia_get_capture_raw_data(vport, capture_type, max_packets):
    '''
        capture raw data packets
        Parameters:
            vport - vport object.  Ex: '/vport:1', '::ixNet::OBJ-/vport:1'
            capture_type - data or control
            max_packets - maximum number of raw packet to decode
        Return:
            hexdump of captured data in a list
    '''
    captured_attribute_name = '-'+capture_type.lower()+'CapturedPacketCounter'
    getPacket_exec = 'getPacketFrom'+capture_type.capitalize()+'Capture'
    numCaptured = ixiangpf.ixnet.getAttribute(vport+'/capture', captured_attribute_name)
    data_dump_list = []

    ### numCaptured count may be very huge, limit it to max
    if int(numCaptured) > max_packets:
        count = max_packets
    else:
        count = numCaptured
    count = int(count)
    for packetIndex in range(count):
        currentPacket = ixiangpf.ixnet.getList(vport+'/capture', 'currentPacket')[0]
        ixiangpf.ixnet.execute(getPacket_exec, currentPacket, packetIndex)
        packetHex = ixiangpf.ixnet.getAttribute(currentPacket, '-packetHex')
        data_dump_list.append(packetHex)
    return data_dump_list

def ixia_capture_raw_data(port_handle, capture_type='data', max_packets=10):
    '''
        capture raw data packetes
        Arguments:
          -port_handle: ixia port
          -capture_type: either 'data' for data plane capture or 'control' for control plane capture
          -max_packets - maximum number of raw packet to decode
    '''
    vport = ixiangpf.convert_porthandle_to_vport(port_handle='%s/%s' % (1, port_handle))['handle']
    count=0
    max_packets = int(max_packets)
    while (_ixia_captureState(vport, capture_type) != 'ready'):
        ixia_print('captureState is not ready, waiting 10 seconds....')
        if count > 360:
            ErrorHandler('ixia_wait_capture_data_ready', _ixia_captureState(vport, capture_type))
        else:
            time.sleep(10)

    ixia_print('capture is processed....')

    captured_data_list = _ixia_get_capture_raw_data(vport, capture_type, max_packets)

    return captured_data_list

def ixia_stop_capture(**kwargs):
    '''
    Enable capture
    Arguments:
     -port_handle:
       ANY
    '''
    tkwargs = {
        'action':'stop',
    }
    for key, value in kwargs.iteritems():
        if key == 'port_handle':
            tkwargs[key]='%s/%s' % (1, value)
        else:
            tkwargs[key]=value

    #################################################
    ##  Enable capture
    #################################################
    stop_capture_status = ixiangpf.packet_control(**tkwargs)

    if stop_capture_status['status'] != '1':
        ErrorHandler('stop_capture', stop_capture_status)
    else:
        ixia_print('stop_capture done')

    return(stop_capture_status)

def ixia_get_captured_data(**kwargs):
    '''
    Enable capture
    Arguments:
     -port_handle:
       ANY
    '''
    tkwargs = {
        'format':'none',
        'stop':1
    }
    for key, value in kwargs.iteritems():
        if key == 'port_handle':
            tkwargs[key]='%s/%s' % (1, value)
        else:
            tkwargs[key]=value

    #################################################
    ##  Enable capture
    #################################################
    get_captured_data_status = ixiangpf.packet_stats(**tkwargs)

    if get_captured_data_status['status'] != '1':
        ErrorHandler('get_captured_data', get_captured_data_status)
    else:
        ixia_print('get_captured_data done')

    return(get_captured_data_status)

def ixia_packet_config_filter(**kwargs):
    '''
    Configure filters for capturing
    Arguments:
     -port_handle:
       ANY
    '''
    tkwargs = {
    }
    for key, value in kwargs.iteritems():
        if key == 'port_handle':
            tkwargs[key]='%s/%s' % (1, value)
        else:
            tkwargs[key]=value

    #################################################
    ##  Enable capture
    #################################################
    config_capture_filter_status = ixiangpf.packet_config_filter(**tkwargs)

    if config_capture_filter_status['status'] != '1':
        ErrorHandler('packet_config_filter', config_capture_filter_status)
    else:
        ixia_print('packet_config_filter done')

    return(config_capture_filter_status)

def ixia_packet_config_trigger2(**kwargs):
    '''
    Configure trigger for capturing
    Arguments:
     -port_handle:
       ANY
    '''
    tkwargs = {
	'capture_filter':1,
	'capture_filter_pattern':'pattern1',
    }
    for key, value in kwargs.iteritems():
        if key == 'port_handle':
            tkwargs[key]='%s/%s' % (1, value)
        else:
            tkwargs[key]=value

    #################################################
    ##  Enable capture
    #################################################
    config_capture_trigger_status = ixiangpf.packet_config_triggers(**tkwargs)

    if config_capture_trigger_status['status'] != '1':
        ErrorHandler('packet_config_triggers', config_capture_trigger_status)
    else:
        ixia_print('packet_config_triggers done')

    return(config_capture_trigger_status)

def ixia_packet_config_trigger(**kwargs):
    '''
    Configure trigger for capturing
    Arguments:
     -port_handle:
       ANY
    '''
    tkwargs = {
        'mode':'create',
        'capture_filter':1,
        'capture_trigger':1,
        'capture_filter_SA':'any',
        'capture_filter_DA':'any',
        'capture_filter_error':'errAnyFrame',
        'capture_filter_framesize':0,
        'capture_filter_framesize_from':64,
        'capture_filter_framesize_to':1518,
        'capture_filter_pattern':'any',
    }
    for key, value in kwargs.iteritems():
        if key == 'port_handle':
            tkwargs[key]='%s/%s' % (1, value)
        else:
            tkwargs[key]=value

    #################################################
    ##  Enable capture
    #################################################
    config_capture_trigger_status = ixiangpf.packet_config_triggers(**tkwargs)

    if config_capture_trigger_status['status'] != '1':
        ErrorHandler('packet_config_triggers', config_capture_trigger_status)
    else:
        ixia_print('packet_config_triggers done')

    return(config_capture_trigger_status)

def ixia_igmp_config(**kwargs):
    '''
    Configure IGMP Emulation
    Arguments:
     -handle:
       ANY
     -protocol_name:
       ANY
     -mode:
       ANY
     -igmp_version:
       vi,v2,v3
    '''
    tkwargs = {
        'protocol_name':'IGMP Host',
        'mode':'create',
        'filter_mode':'include',
        'igmp_version':'v2',
    }
    for key, value in kwargs.iteritems():
        tkwargs[key]=value

    #################################################
    ##  emulation_igmp_config
    #################################################
    emulation_igmp_status = ixiangpf.emulation_igmp_config(**tkwargs)

    if emulation_igmp_status['status'] != '1':
        ErrorHandler('emulation_igmp_config', emulation_igmp_status)
    else:
        ixia_print('emulation_igmp_config done')

    return(emulation_igmp_status)

def ixia_multicast_group_config(**kwargs):
    '''
    Configure Multicast Group
    Arguments:
     -mode:
       ANY
     -ip_addr_start:
       ANY
     -ip_addr_step:
       ANY
     -num_groups:
       NUMERIC
     -active:
       CHOISE 0 1
    '''
    #################################################
    ##  emulation_igmp_config
    #################################################
    mkwargs = {
        'pattern':'counter',
        'counter_start':'230.1.1.1',
        'counter_step':'0.0.0.0',
        'counter_direction':'increment',
        'nest_step':'0.0.0.0',
        'nest_enabled':'1',
    }
    for key, value in kwargs.iteritems():
        if key == 'group_start_ip':
            mkwargs['counter_start']=value
        if key == 'group_members':
            mkwargs['nest_owner']=value

    multivalue_config_status = ixiangpf.multivalue_config(**mkwargs)
    if multivalue_config_status['status'] != '1':
        ErrorHandler('multivalue_config', multivalue_config_status)
    else:
        multivalue_handle = multivalue_config_status['multivalue_handle']

    tkwargs = {
        'mode':'create',
        'ip_addr_start':multivalue_handle,
        'ip_addr_step':'0.0.0.0',
        'num_groups':'1',
        'active':'1',
    }
    for key, value in kwargs.iteritems():
        if key == 'group_start_ip':
            continue
        elif key == 'group_members':
            continue
        else:
            tkwargs[key]=value

    emulation_multicast_group_config_status = ixiangpf.emulation_multicast_group_config(**tkwargs)
    if emulation_multicast_group_config_status['status'] != '1':
        ErrorHandler('emulation_multicast_group_config', emulation_multicast_group_config_status)
    else:
        ixia_print('emulation_multicast_group_config done')

    return(emulation_multicast_group_config_status)

def ixia_igmp_group_config(**kwargs):
    '''
    Configure IGMP Group Configure
    Arguments:
     -mode:
       ANY
     -g_filter_mode:
       ANY
     -group_pool_handle:
       ANY
     -no_of_grp_ranges:
       NUMERIC
     -no_of_src_ranges:
       NUMERIC
     -session_handle:
       ANY
     -source_pool_handle:
       ANY
    '''
    tkwargs = {
        'mode':'create',
        'g_filter_mode':'include',
        'no_of_grp_ranges':'1',
        'no_of_src_ranges':'1',
    }
    for key, value in kwargs.iteritems():
        if key == 'igmp_hosts':
            tkwargs['session_handle']=value
        else:
            tkwargs[key]=value

    #################################################
    ##  emulation_igmp_config
    #################################################
    emulation_igmp_group_config_status = ixiangpf.emulation_igmp_group_config(**tkwargs)
    if emulation_igmp_group_config_status['status'] != '1':
        ErrorHandler('emulation_igmp_group_config', emulation_igmp_group_config_status)
    else:
        ixia_print('emulation_igmp_group_config done')

    return(emulation_igmp_group_config_status)

def ixia_multicast_source_config(**kwargs):
    '''
    Configure Multicast Source Configure
    Arguments:
     -mode:
       ANY
     -ip_addr_start:
       ANY
     -ip_addr_step:
       ANY
     -num_sources:
       NUMERIC
     -active:
       CHOISE 0 1
    '''
    tkwargs = {
        'mode':'create',
        'ip_addr_step':'0.0.0.1',
        'num_sources':'1',
        'active':'1',
    }
    for key, value in kwargs.iteritems():
        tkwargs[key]=value

    #################################################
    ##  emulation_igmp_config
    #################################################
    emulation_multicast_source_config_status = ixiangpf.emulation_multicast_source_config(**tkwargs)

    if emulation_multicast_source_config_status['status'] != '1':
        ErrorHandler('emulation_multicast_source_config', emulation_multicast_source_config_status)
    else:
        ixia_print('emulation_multicast_source_config done')

    return(emulation_multicast_source_config_status)

def ixia_igmp_querier_config(**kwargs):
    '''
    Configure IMGP Querier Configure
    Arguments:
     -mode:
       ANY
     -discard_learned_info:
       CHOISE 0 1
     -general_query_response_interval:
       NUMERIC
     -num_sources:
       NUMERIC
     -active:
       CHOISE 0 1
     -handle:
       ANY
     -igmp_version:
       v1,v2,v3
     -query_interval:
       NUMERIC
     -name:
       ANY
    '''
    tkwargs = {
        'mode':'create',
        'discard_learned_info':'0',
        'general_query_response_interval':11000,
        'igmp_version':'v2',
        'query_interval':120,
        'active':'1',
    }
    for key, value in kwargs.iteritems():
        tkwargs[key]=value

    #################################################
    ##  emulation_igmp_config
    #################################################
    emulation_igmp_querier_config_status = ixiangpf.emulation_igmp_querier_config(**tkwargs)

    if emulation_igmp_querier_config_status['status'] != '1':
        ErrorHandler('emulation_igmp_querier', emulation_igmp_querier_config_status)
    else:
        ixia_print('emulation_igmp_querier_config done')

    return(emulation_igmp_querier_config_status)

def ixia_igmp_control(**kwargs):
    '''
    Trigger IGMP
    Arguments:
     -mode:
       ANY
     -handle:
       ANY
    '''
    tkwargs = {
        'mode':'start',
    }
    for key, value in kwargs.iteritems():
        tkwargs[key]=value

    #################################################
    ##  emulation_igmp_config
    #################################################
    emulation_igmp_control_status = ixiangpf.emulation_igmp_control(**tkwargs)

    if emulation_igmp_control_status['status'] != '1':
        ErrorHandler('emulation_igmp_control', emulation_igmp_control_status)
    else:
        ixia_print('emulation_igmp_control done')

    return(emulation_igmp_control_status)

def ixia_igmp_info(**kwargs):
    '''
    Trigger IGMP
    Arguments:
     -mode:
       ANY
     -handle:
       ANY
     -type:
       ANY
    '''
    tkwargs = {
        'mode':'aggregate',
    }
    for key, value in kwargs.iteritems():
        tkwargs[key]=value

    #################################################
    ##  emulation_igmp_config
    #################################################
    emulation_igmp_info_status = ixiangpf.emulation_igmp_info(**tkwargs)

    if emulation_igmp_info_status['status'] != '1':
        ErrorHandler('emulation_igmp_info', emulation_igmp_info_status)
    else:
        ixia_print('emulation_igmp_info done')

        for i in range(5):
            if emulation_igmp_info_status[tkwargs['handle']]['sessions_down'] != 0:
                ixia_print("Not all igmp sessions are up, wait 5 more seconds....")
                time.sleep(5)
            else:
                ixia_print("All igmp sessions are up")
                break

        if emulation_igmp_info_status[tkwargs['handle']]['sessions_down'] == 0:
            ixia_get_diag_file()

    return(emulation_igmp_info_status)

def ixia_multicast_traffic_config(**kwargs):
    '''
    Configure multicast traffic
    Arguments:
     -mode:
       ANY
    '''
    tkwargs = {
        'mode':'create',
        'endpointset_count':1,
        'emulation_dst_handle':'',
        'emulation_multicast_dst_handle_type':['none'],
        'name':'TI0-Traffic_Item_1',
        'circuit_endpoint_type':'ipv4',
        'frame_size':128,
        'rate_mode':'percent',
        'rate_percent':10,
        'track_by':'endpoint_pair',
    }
    for key, value in kwargs.iteritems():
        tkwargs[key]=value

    #################################################
    ##  emulation_igmp_config
    #################################################
    traffic_config_status = ixiangpf.traffic_config(**tkwargs)

    if traffic_config_status['status'] != '1':
        ErrorHandler('traffic_config', traffic_config_status)
    else:
        ixia_print('traffic_config done')

    return(traffic_config_status)

def ixia_config_phy_mode(**kwargs):
    '''
    Configure phy mode
    Arguments:
     -port_handle:
       REGEXP ^[0-9]+/[0-9]+/[0-9]+$
     -phy_mode:
       copper
       fiber
    '''
    tkwargs = {
        'mode':'config',
        'auto_detect_instrumentation_type':'floating',
    }
    for key, value in kwargs.iteritems():
        if key == 'port_handle':
            tkwargs[key]='%s/%s' % (1, value)
        else:
            tkwargs[key]=value

    #################################################
    ##  emulation_igmp_config
    #################################################
    phy_mode_config_status = ixiahlt.interface_config(**tkwargs)
    if phy_mode_config_status['status'] != '1':
        ErrorHandler('ixia_config_phy_mode', phy_mode_config_status)
    else:
        ixia_print('config phy_mode done')

    return(phy_mode_config_status)

def ixia_unset_with_protocols_down():
    '''
    Unset ixia configurations including removes all the client side variable and handles. reboots the ports cpu to initial state
    Arguments:
     none
    '''
    # Stop sending traffic
    kwargs={}
    kwargs['action']='stop'
    unset_status = ixiangpf.traffic_control(**kwargs)
    if unset_status['status'] != '1':
        ErrorHandler('traffic_control', unset_status)
    else:
        ixia_print('traffic stop is done')

    # removes all the client side variable and handles  and remove the config on the IxNetwork API Server GUI
    unset_status = ixiangpf.cleanup_session(reset='1')
    if unset_status['status'] != '1':
        ErrorHandler('cleanup_session', unset_status)
    else:
        ixia_print('ixia cleanup_session done')

    return(unset_status)

def ixia_unset():
    '''
    Unset ixia configurations including removes all the client side variable and handles. reboots the ports cpu to initial state
    Arguments:
     none
    '''
    # Stop sending traffic
    #kwargs={}
    #kwargs['action']='stop'
    #kwargs['max_wait_timer']=60
    #unset_status = ixiangpf.traffic_control(**kwargs)
    #if unset_status['status'] != '1':
    #    ErrorHandler('traffic_control', unset_status)
    #else:
    #    ixia_print('traffic stop is done')
    #
    # stop protocols
    # kwargs = {}
    # kwargs['action']='stop_all_protocols'
    # unset_status = ixiangpf.test_control(**kwargs)
    # if unset_status['status'] != '1':
    #    ErrorHandler('test_control', unset_status)
    # else:
    #    ixia_print('Stop all protocols done')
   
    # removes all the client side variable and handles  and remove the config on the IxNetwork API Server GUI
    unset_status = ixiangpf.cleanup_session(reset='1')
    if unset_status['status'] != '1':
        ErrorHandler('cleanup_session', unset_status)
    else:
        ixia_print('ixia cleanup_session done')

    return(unset_status)

    # **** This part needs ports argument
    #      This code works before calling ixiangpf.cleanup_session(reset='1'), otherwise, ixiangpf.reboot_port_cpu would fail
    #full_ports = []
    #for port in ports:
    #    full_ports.append('%s/%s' % (1, port))
    #ixia_print('full_ports=%s' % full_ports)
    #tkwargs = {'port_list':full_ports}
    #reboot_port_cpu_status = ixiangpf.reboot_port_cpu(**tkwargs)
    #ixia_print('reboot_port_cpu_status=%s' % reboot_port_cpu_status)
    #if reboot_port_cpu_status['status'] != '1':
    #    ErrorHandler('reboot_port_cpu', reboot_port_cpu_status)
    #else:
    #    ixia_print('ixia reboot_port_cpu on %s done' % full_ports)

def ixia_simulate_link(ports, port, action):
    '''
    this api simulate link up/down
    Arguments:
     port
     action: down/up
    '''
    # Stop sending traffic
    if action == 'up':
        action_state = 'connectedLinkUp'
    elif action == 'down':
        action_state = 'connectedLinkDown'
    else:
        ixia_print('ixia_simulate_link, unknown action=%s' % action) 
        return(0)
    vportList = ixiangpf.ixnet.getList("/", 'vport')
    index = ports.index(port)
    ixiangpf.ixnet.execute('linkUpDn', vportList[index], action)
    attempt  = 10
    while attempt > 0:
        state = ixiangpf.ixnet.getAttribute(vportList[index], '-connectionState')
        if state == action_state:
            break
        ixia_print('Link is not %s yet, Please wait 5 more seconds....' % action)
        attempt -= 1
        time.sleep(5)
    if attempt == 0:
        ErrorHandler('ixia_simulate_link %s timeout' % action, state)
    else:
        ixia_print('ixia_simulate_link %s complete' % action)
    
def ixia_test_control(ipv4_handle, action):
    '''
    this api simulate link up/down
    Arguments:
     ipv4_handle
     action: start_protocol/stop_protocol
    '''
    # Stop sending traffic
    tkwargs = {
        'handle':ipv4_handle,
        'action':action,
    }
    test_control_status = ixiangpf.test_control(**tkwargs)
    if test_control_status['status'] != '1':
        ErrorHandler('test_control', test_control_status)
    else:
        ixia_print('ixia_test_control %s done' % action)

    return(test_control_status)

def ixia_config_pauseframe(**kwargs):
    '''
    Config pause frame
    Arguments:
     -mode:
       ANY
    '''
    tkwargs = {
        'traffic_generator':'ixnetwork_540',
        'mode':'create',
        'name':'PFC_Pause_Packet',
        'circuit_type':'raw',
        'frame_size':84,
        'length_mode':'fixed',
        'tx_mode':'advanced',
        'transmit_mode':'continuous',
    }
    for key, value in kwargs.iteritems():
        if key == 'src_port':
            tkwargs['emulation_src_handle'] = '%s/%s' % (1, value)
        elif key == 'dst_port':
            tkwargs['emulation_dst_handle'] = '%s/%s' % (1, value)
        else:
            tkwargs[key]=value

    #################################################
    ##  Configure a raw traffic PFC_Pause_packet
    #################################################
    traffic_config_status = ixiangpf.traffic_config(**tkwargs)

    if traffic_config_status['status'] != '1':
        ErrorHandler('traffic_config_status', traffic_config_status)
    else:
        config_elements = ixiatcl.convert_tcl_list(traffic_config_status['traffic_item'])
        current_config_element = config_elements[0]
        stack_handle_pointer = {ce: ixiatcl.convert_tcl_list(traffic_config_status[ce]['headers'])[0] for ce in config_elements}
        tkwargs = {
            'traffic_generator':'ixnetwork_540',
            'mode':'replace_header',
            'stream_id':stack_handle_pointer[current_config_element],
            'stack_index':'1',
            'pt_handle':'pfcPause',
        }
        traffic_config_status = ixiangpf.traffic_config(**tkwargs)
        if traffic_config_status['status'] != '1':
            ErrorHandler('config_puaseframe', traffic_config_status)
        else:
            print('\nConfigure Pause Frame done')

    return(traffic_config_status)

def ixia_set_pauseframe_singlevalue(traffic_config, value):
    '''
    Config pause frame single value
    Arguments:
     -traffic_config:
       return info of ixia_config_pauseframe
     -value
       pasue frame single value
    '''
    #################################################
    ##  Configure a raw traffic PFC_Pause_packet
    #################################################
    last_stack = traffic_config['last_stack']
    tkwargs = {
        'traffic_generator':'ixnetwork_540',
        'mode':'set_field_values',
        'header_handle':last_stack,
        'pt_handle':'pfcPause',
        'field_handle':"pfcPause.header.macControl.pauseQuanta.pfcQueue0-6",
        'field_activeFieldChoice':0,
        'field_auto':0,
        'field_optionalEnabled':1,
        'field_fullMesh':0,
        'field_trackingEnabled':0,
        'field_valueType':'singleValue',
        'field_singleValue':value,
    }
    traffic_config_status = ixiangpf.traffic_config(**tkwargs)
    if traffic_config_status['status'] != '1':
        ErrorHandler('config_puaseframe', traffic_config_status)
    else:
        print('\nSet Pause Frame singleValue value done')

    return(traffic_config_status)

def ixia_config_custom_pauseframe(**kwargs):
    '''
    Config pause frame
    Arguments:
     -src_port:
       ANY
     -src_mac
       ANY
     -dst_port:
       ANY
     -dst_mac:
       ANY
     -etherType:
       ANY
     -pkt_length:
       ANY
     -data:
       ANY    
     -frame_size:
       ANY
    '''
    tkwargs = {
        'traffic_generator':'ixnetwork_540',
        'mode':'create',
        'name':'Custom_Pause_Packet',
        'circuit_type':'raw',
        'frame_size':86,
        'length_mode':'fixed',
        'tx_mode':'advanced',
        'transmit_mode':'continuous',
    }
    for key, value in kwargs.iteritems():
        if key == 'src_port':
            tkwargs['emulation_src_handle'] = '%s/%s' % (1, value)
        elif key == 'dst_port':
            tkwargs['emulation_dst_handle'] = '%s/%s' % (1, value)
        elif key == 'src_mac':
            src_mac = value
        elif key == 'dst_mac':
            dst_mac = value
        elif key == 'pkt_length':
            pkt_length = value
        elif key == 'etherType':
            etherType = value
        elif key == 'data':
            data = value
        else:
            tkwargs[key] = value

    #################################################
    ##  Configure a raw traffic PFC_Pause_packet
    #################################################
    traffic_config_status = ixiangpf.traffic_config(**tkwargs)

    if traffic_config_status['status'] != '1':
        ErrorHandler('traffic_config_status', traffic_config_status)
    else:
        config_elements = ixiatcl.convert_tcl_list(traffic_config_status['traffic_item'])
        current_config_element = config_elements[0]
        #################################################
        ##  Configure ethernet field
        #################################################
        tkwargs = {
            'traffic_generator':'ixnetwork_540',
            'mode':'modify_or_insert',
            'stream_id':current_config_element,
            'stack_index':'1',
            'pt_handle':'ethernet',
        }
        traffic_config_status = ixiangpf.traffic_config(**tkwargs)
        if traffic_config_status['status'] != '1':
            ErrorHandler('config_puaseframe', traffic_config_status)
        else:
            last_stack = traffic_config_status['last_stack']
            # Configure ethernet.header destinationAddress
            tkwargs = {
                'traffic_generator':'ixnetwork_540',
                'mode':'set_field_values',
                'header_handle':last_stack,
                'pt_handle':'ethernet',
                'field_handle':'ethernet.header.destinationAddress-1',
                'field_activeFieldChoice':0,
                'field_auto':0,
                'field_optionalEnabled':1,
                'field_fullMesh':0,
                'field_trackingEnabled':0,
                'field_valueType':'singleValue',
                'field_singleValue':dst_mac,
            }
            traffic_config_status = ixiangpf.traffic_config(**tkwargs)
            if traffic_config_status['status'] != '1':
                ErrorHandler('Configure ethernet header destinationAddress', traffic_config_status)
            else:
                # Configure ethernet.header sourceAddress
                tkwargs = {
                    'traffic_generator':'ixnetwork_540',
                    'mode':'set_field_values',
                    'header_handle':last_stack,
                    'pt_handle':'ethernet',
                    'field_handle':'ethernet.header.sourceAddress-2',
                    'field_activeFieldChoice':0,
                    'field_auto':0,
                    'field_optionalEnabled':1,
                    'field_fullMesh':0,
                    'field_trackingEnabled':0,
                    'field_valueType':'singleValue',
                    'field_singleValue':src_mac,
                }
                traffic_config_status = ixiangpf.traffic_config(**tkwargs)
                if traffic_config_status['status'] != '1':
                    ErrorHandler('Configure ethernet header sourceAddress', traffic_config_status)
                else:
                    tkwargs = {
                        'traffic_generator':'ixnetwork_540',
                        'mode':'set_field_values',
                        'header_handle':last_stack,
                        'pt_handle':'ethernet',
                        'field_handle':'ethernet.header.etherType-3',
                        'field_activeFieldChoice':0,
                        'field_auto':0,
                        'field_optionalEnabled':1,
                        'field_fullMesh':0,
                        'field_trackingEnabled':0,
                        'field_valueType':'singleValue',
                        'field_singleValue':etherType,
                    }
                    traffic_config_status = ixiangpf.traffic_config(**tkwargs)
                    if traffic_config_status['status'] != '1':
                        ErrorHandler('Configure ethernet header etherType', traffic_config_status)
                    else:
                        ixia_print('Configure ethernet header done')

        #################################################
        ##  Configure custom field
        #################################################
        tkwargs = {
            'traffic_generator':'ixnetwork_540',
            'mode':'modify_or_insert',
            'stream_id':current_config_element,
            'stack_index':'2',
            'pt_handle':'custom',
        }
        traffic_config_status = ixiangpf.traffic_config(**tkwargs)
        if traffic_config_status['status'] != '1':
            ErrorHandler('config custom header', traffic_config_status)
        else:
            last_stack = traffic_config_status['last_stack']
            # Configure coustom header length
            tkwargs = {
                'traffic_generator':'ixnetwork_540',
                'mode':'set_field_values',
                'header_handle':last_stack,
                'pt_handle':'custom',
                'field_handle':'custom.header.length-1',
                'field_activeFieldChoice':0,
                'field_auto':0,
                'field_optionalEnabled':1,
                'field_fullMesh':0,
                'field_trackingEnabled':0,
                'field_valueType':'singleValue',
                'field_singleValue':pkt_length,
            }
            traffic_config_status = ixiangpf.traffic_config(**tkwargs)
            if traffic_config_status['status'] != '1':
                ErrorHandler('Configure coustom header length', traffic_config_status)
            else:
                # Configure coustom header data
                tkwargs = {
                    'traffic_generator':'ixnetwork_540',
                    'mode':'set_field_values',
                    'header_handle':last_stack,
                    'pt_handle':'custom',
                    'field_handle':'custom.header.data-2',
                    'field_activeFieldChoice':0,
                    'field_auto':0,
                    'field_optionalEnabled':1,
                    'field_fullMesh':0,
                    'field_trackingEnabled':0,
                    'field_valueType':'singleValue',
                    'field_singleValue':data,
                }
                traffic_config_status = ixiangpf.traffic_config(**tkwargs)
                if traffic_config_status['status'] != '1':
                    ErrorHandler('Configure coustom data', traffic_config_status)
                else:
                    print('\nConfigure custom pause frame done')

    return(traffic_config_status)

def ixia_config_dhcp_client_tlv_creation(**kwargs):

    '''
     Config dhcp client tlv creation
     Arguments:
     -tlv name:
       ANY
     -tlv description:
       ANY
    '''
    tkwargs = {
	'mode':"create_tlv",
	'tlv_is_enabled':"1",
	'tlv_include_in_messages':"""kDiscover kRequest""",
	'tlv_enable_per_session':"1",
	'type_name':"Type",
	'type_is_editable':"0",
	'type_is_required':"1",
	'length_name':"Length",
	'length_description':"""Dhcp client TLV length field.""",
	'length_encoding':"decimal",
	'length_size':"1",
	'length_value':"0",
	'length_is_editable':"0",
	'length_is_enabled':"1",
	'disable_name_matching':"1",
    }	

        
    for key, value in kwargs.iteritems():
    	if key == 'tlv_name':
    	    tkwargs['tlv_name'] = value
    	elif key == 'tlv_description':
                tkwargs['tlv_description'] = value
    	else:
    	    tkwargs[key] = value

    #################################################
    ##  Create Create Traffic                       #
    #################################################
    traffic_tlv_config = ixiangpf.tlv_config(**tkwargs)

    if traffic_tlv_config['status'] != '1':
        ErrorHandler('traffic_tlv_config', traffic_tlv_config)
    else:
        print('\n DHCP TLV Value Config Creation of TLV Done \n')

    return(traffic_tlv_config)


def ixia_config_dhcp_client_tlv_element_creation(**kwargs):
    '''
     Config dhcp client tlv element creation
     Arguments:
     -field_name:
       ANY
     -field_description:
       ANY
  
    '''
    tkwargs = {
	'mode':"create_field",
    }

    for key, value in kwargs.iteritems():
    	if key == 'handle':
    	    tkwargs['handle'] = value
    	elif key == 'field_name':
                tkwargs['field_name'] = value
    	elif key == 'field_description':
    	    tkwargs['field_description'] = value
    	elif key == 'field_value':
    	    tkwargs['field_value'] = value
    	else:
    	    tkwargs[key] = value

    #################################################
    ##  Create Create Traffic                       #
    #################################################	
    traffic_tlv_config = ixiangpf.tlv_config(**tkwargs)

    if traffic_tlv_config['status'] != '1':
        ErrorHandler('traffic_tlv_config', traffic_tlv_config)
    else:
        print('\n DHCP TLV Value Config Creation of TLV ELEMENT Done \n')

    return(traffic_tlv_config)

def ixia_emulation_dhcp_control(**kwargs):
    '''
	This Keyword Will Call the Ixia emulation_dhcp_control
	function for rebind, renew, abort
    '''
    tkwargs = {
    }
    for key, value in kwargs.iteritems():
    	if key == 'handle':
    	    tkwargs['handle'] = value
    	else:
    	    tkwargs[key] = value

    #################################################
    ##  Create Create Traffic                       #
    #################################################	
    dhcp_emulation_control = ixiangpf.emulation_dhcp_control(**tkwargs)

    if dhcp_emulation_control['status'] != '1':
        ErrorHandler('dhcp_emulation_control', dhcp_emulation_control)
    else:
        print('\n DHCP Control Emulation Operation is Done \n')

    return(dhcp_emulation_control)


def ixia_emulation_dot1x_config(**kwargs):
    '''
    create emulation dot1x config
    Arguments:
     -topology_handle:
       ALPHA
     -nest_step:
       ANY
     -nest_owner:
       ANY
     -counter_start:
       NUMERIC
    return:
     -dot1x handle
    '''
    tkwargs = {
    }
    for key, value in kwargs.iteritems():
        temp_string = str(key)+":"+str(value)
        logger.console('\t%s' % temp_string)
        tkwargs[key]=value

    #################################################
    ##  Configure Group(s)                          #
    #################################################
    dot1x_config_status = ixiangpf.emulation_dotonex_config(**tkwargs)

    if dot1x_config_status['status'] != '1':
        ErrorHandler('dot1x config status', dot1x_config_status)
    else:
        ixia_print('dot1x config done')


    return(dot1x_config_status)


def ixia_emulation_dot1x_control(**kwargs):
    '''
    create emulation dot1x control
    Arguments:
     -topology_handle:
       ALPHA
     -nest_step:
       ANY
     -nest_owner:
       ANY
     -counter_start:
       NUMERIC
    return:
     -dot1x handle
    '''
    tkwargs = {
    }
    for key, value in kwargs.iteritems():
        temp_string = str(key)+":"+str(value)
        logger.console('\t%s' % temp_string)
        tkwargs[key]=value

    #################################################
    ##  Configure Group(s)                          #
    #################################################
    dot1x_control_status = ixiangpf.emulation_dotonex_control(**tkwargs)

    if dot1x_control_status['status'] != '1':
        ErrorHandler('dot1x_control_status', dot1x_control_status)
    else:
        ixia_print('dot1x control done')

    return(dot1x_control_status)


def ixia_config_dhcp_packet_with_dhcp_message_type(**kwargs):
    '''
    This command configures Traffic stream
    Arguments:
     -src_handle:
       ALPHA
     -dst_handle:
       ALPHA
     others
       ANY (check IXIA HLAPI traffic_config API manual for detail)
    '''

    tkwargs = {
        'mode':'create',
        'endpointset_count':1,
        'src_dest_mesh':'one_to_one',
        'route_mesh':'one_to_one',
        'bidirectional':1,
        'name':'Traffic_Item_1',
        'circuit_endpoint_type':'ipv4',
        'frame_size':64,
        'rate_mode':'percent',
        'rate_percent':2,
        'track_by':'endpoint_pair'
    }
    for key, value in kwargs.iteritems():
        if re.search('port_handle', key):
            tkwargs[key]='%s/%s' % (1, value)
        elif re.search('frame_rate', key):
            mode,rate=value.split(':')
            if mode == 'percent':
                tkwargs['rate_mode']='percent'
                tkwargs['rate_percent']=rate
            elif mode == 'pps':
                tkwargs['rate_mode']='pps'
                tkwargs['rate_pps']=rate
        elif key == 'dhcp_message_type':
            dhcp_message_type = value
        elif key == 'client_hardware_address':
	        client_hardware_address = value
        else:
            tkwargs[key]=value
    #################################################
    ##  Configure a IPv4 Packet
    #################################################
    traffic_config_status = ixiangpf.traffic_config(**tkwargs)

    if traffic_config_status['status'] != '1':
        ErrorHandler('traffic_config_status', traffic_config_status)
    else:
        config_elements = ixiatcl.convert_tcl_list(traffic_config_status['traffic_item'])
        current_config_element = config_elements[0]
        #################################################
        ##  Configure UDP header
        #################################################
        tkwargs = {
            'traffic_generator':'ixnetwork_540',
            'mode':'modify_or_insert',
            'stream_id':current_config_element,
            'stack_index':'3',
            'pt_handle':'udp',
        }
        traffic_config_status = ixiangpf.traffic_config(**tkwargs)
        if traffic_config_status['status'] != '1':
            ErrorHandler('config_puaseframe', traffic_config_status)
        else:
            last_stack = traffic_config_status['last_stack']
            # Configure UDP Source Port
            tkwargs = {
                'traffic_generator':'ixnetwork_540',
                'mode':'set_field_values',
                'header_handle':last_stack,
                'pt_handle':'udp',
                'field_handle':'udp.header.srcPort-1',
                'field_activeFieldChoice':0,
                'field_auto':1,
                'field_optionalEnabled':1,
                'field_fullMesh':0,
                'field_trackingEnabled':0,
                'field_valueType':'singleValue',
                'field_singleValue':68,
            }
            traffic_config_status = ixiangpf.traffic_config(**tkwargs)
            if traffic_config_status['status'] != '1':
                ErrorHandler('Configure udp src port', traffic_config_status)
            else:
                # Configure udp.header.dstport
                tkwargs = {
                    'traffic_generator':'ixnetwork_540',
                    'mode':'set_field_values',
                    'header_handle':last_stack,
                    'pt_handle':'udp',
                    'field_handle':'udp.header.dstPort-2',
                    'field_activeFieldChoice':0,
                    'field_auto':1,
                    'field_optionalEnabled':1,
                    'field_fullMesh':0,
                    'field_trackingEnabled':0,
                    'field_valueType':'singleValue',
                    'field_singleValue':67,
                }
                traffic_config_status = ixiangpf.traffic_config(**tkwargs)
                if traffic_config_status['status'] != '1':
                    ErrorHandler('Configure udp dst port', traffic_config_status)
                else:
		    #udp header length
                    tkwargs = {
                        'traffic_generator':'ixnetwork_540',
                        'mode':'set_field_values',
                        'header_handle':last_stack,
                        'pt_handle':'udp',
                        'field_handle':'udp.header.length-3',
                        'field_activeFieldChoice':0,
                        'field_auto':1,
                        'field_optionalEnabled':1,
                        'field_fullMesh':0,
                        'field_trackingEnabled':0,
                        'field_valueType':'singleValue',
                        'field_singleValue':362,
                    }
                    traffic_config_status = ixiangpf.traffic_config(**tkwargs)
                    if traffic_config_status['status'] != '1':
                        ErrorHandler('Configure udp header length', traffic_config_status)
                    else:
			#udp header checksum
                    	tkwargs = {
                            'traffic_generator':'ixnetwork_540',
	                    'mode':'set_field_values',
        	            'header_handle':last_stack,
                	    'pt_handle':'udp',
                            'field_handle':'udp.header.checksum-4',
	                    'field_activeFieldChoice':0,
        	            'field_auto':1,
	                    'field_optionalEnabled':1,
	                    'field_fullMesh':0,
	                    'field_trackingEnabled':0,
        	            'field_valueType':'singleValue',
                	    'field_singleValue':0,
	                }
                    traffic_config_status = ixiangpf.traffic_config(**tkwargs)
                    if traffic_config_status['status'] != '1':
                        ErrorHandler('Configure udp checksum', traffic_config_status)
                    else:
                        ixia_print('Configure UDP Header done')

        #################################################
        ##  Configure DHCP Header 
        #################################################
        tkwargs = {
            'traffic_generator':'ixnetwork_540',
            'mode':'modify_or_insert',
            'stream_id':current_config_element,
            'stack_index':'4',
            'pt_handle':'dhcp',
        }
        traffic_config_status = ixiangpf.traffic_config(**tkwargs)
        if traffic_config_status['status'] != '1':
            ErrorHandler('config dhcp header', traffic_config_status)
        else:
            last_stack = traffic_config_status['last_stack']
            # Configure dhcp header opcode
            tkwargs = {
                'traffic_generator':'ixnetwork_540',
                'mode':'set_field_values',
                'header_handle':last_stack,
                'pt_handle':'dhcp',
                'field_handle':'dhcp.header.opCode-1',
                'field_activeFieldChoice':0,
                'field_auto':0,
                'field_optionalEnabled':1,
                'field_fullMesh':0,
                'field_trackingEnabled':0,
                'field_valueType':'singleValue',
                'field_singleValue':1,
            }
            traffic_config_status = ixiangpf.traffic_config(**tkwargs)
            if traffic_config_status['status'] != '1':
                ErrorHandler('config dhcp header opcode', traffic_config_status)
            else:
                # Configure client hardware
                tkwargs = {
                    'traffic_generator':'ixnetwork_540',
                    'mode':'set_field_values',
                    'header_handle':last_stack,
                    'pt_handle':'dhcp',
                    'field_handle':'dhcp.header.clientHwAddress-12',
                    'field_activeFieldChoice':0,
                    'field_auto':0,
                    'field_optionalEnabled':1,
                    'field_fullMesh':0,
                    'field_trackingEnabled':0,
                    'field_valueType':'singleValue',
                    'field_singleValue':client_hardware_address,
                }
                traffic_config_status = ixiangpf.traffic_config(**tkwargs)
                if traffic_config_status['status'] != '1':
                    ErrorHandler('Configure client hardware', traffic_config_status)
                else:
		    #insert the dhcp message type 
                    tkwargs = {
                        'traffic_generator':'ixnetwork_540',
                        'mode':'set_field_values',
                        'header_handle':last_stack,
                        'pt_handle':'dhcp',
                        'field_handle':'dhcp.header.options.fields.nextOption.field.dhcpMessageType.code-182',
                        'field_activeFieldChoice':1,
                        'field_auto':0,
                        'field_optionalEnabled':1,
                        'field_fullMesh':0,
                        'field_trackingEnabled':0,
                        'field_valueType':'singleValue',
                        'field_singleValue':53,
                    }
                    traffic_config_status = ixiangpf.traffic_config(**tkwargs)
                    if traffic_config_status['status'] != '1':
                        ErrorHandler('Configure dhcp message type', traffic_config_status)
                    else:
			#insert the dhcp message type length
                        tkwargs = {
                            'traffic_generator':'ixnetwork_540',
                            'mode':'set_field_values',
                            'header_handle':last_stack,
                            'pt_handle':'dhcp',
                            'field_handle':'dhcp.header.options.fields.nextOption.field.dhcpMessageType.length-183',
                            'field_activeFieldChoice':1,
                            'field_auto':0,
                            'field_optionalEnabled':1,
                            'field_fullMesh':0,
                            'field_trackingEnabled':0,
                            'field_valueType':'singleValue',
                            'field_singleValue':1,
                        }
                        traffic_config_status = ixiangpf.traffic_config(**tkwargs)
                        if traffic_config_status['status'] != '1':
                            ErrorHandler('Configure dhcp message type length', traffic_config_status)
                        else:
			    #insert the dhcp message type -message type
                            tkwargs = {
                                'traffic_generator':'ixnetwork_540',
                                'mode':'set_field_values',
                                'header_handle':last_stack,
                                'pt_handle':'dhcp',
                                'field_handle':'dhcp.header.options.fields.nextOption.field.dhcpMessageType.messageType-184',
                                'field_activeFieldChoice':1,
                                'field_auto':0,
                                'field_optionalEnabled':1,
                                'field_fullMesh':0,
                                'field_trackingEnabled':0,
                                'field_valueType':'singleValue',
                                'field_singleValue':dhcp_message_type,
                            }
                            traffic_config_status = ixiangpf.traffic_config(**tkwargs)
                            if traffic_config_status['status'] != '1':
                                ErrorHandler('Configure dhcp message type - value', traffic_config_status)
                            else:
                                print('\nConfigure DHCP Header With DHCP Message Type Option done')

    return(traffic_config_status)

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

def ixia_test_control_with_keyword_args(**kwargs):
    '''
    This command applies the action which is passed to the function in test control
    Arguments:
     -action: apply
    '''

    tkwargs = {}
        
    for key, value in kwargs.iteritems():
        tkwargs[key]=value


    #################################################
    ##  apply test control action                   #
    #################################################
    test_control_status = ixiangpf.test_control(**kwargs)

    if test_control_status['status'] != '1':
        ErrorHandler('test_control ', test_control_status)
    else:
        ixia_print('test control is done')

    return(test_control_status)


def get_ixia_port_speed(ports, port):
    '''
	this api will return the speed of ixia port
    '''
    temp_str = "retrieving speed of ixia port:"+str(port)
    ixia_print(temp_str)
    print(ports)
    vport_list = ixiangpf.ixnet.getList('/', 'vport')
    index = ports.index(port)
    vport = vport_list[index]
    speed = ixiangpf.ixnet.getAttribute(vport, '-actualSpeed')
    temp_str = 'Ixia Port Speed:'+str(speed)
    ixia_print(temp_str)
    return speed
 
def ixia_close_alltabs():
    '''
        this api closes all open tabs
    '''
    ixia_print('Close All existing analyser tabs')
    ixiangpf.ixnet.execute('closeAllTabs')

def ixia_traffic_config_with_printing_details(**kwargs):
    '''
    This command configures Traffic stream
    Arguments:
     -src_handle:
       ALPHA
     -dst_handle:
       ALPHA
     others
       ANY (check IXIA HLAPI traffic_config API manual for detail)
    Default:
     'mode':'create',
     'endpointset_count':1,
     'src_dest_mesh':'one_to_one',
     'route_mesh':'one_to_one',
     'bidirectional':1,
     'name':'Traffic_Item_1',
     'circuit_endpoint_type':'ipv4',
     'frame_size':64,
     'rate_mode':'percent',
     'rate_percent':2,
     'track_by':'endpoint_pair'
    '''

    tkwargs = {
        'mode':'create',
        'endpointset_count':1,
        'src_dest_mesh':'one_to_one',
        'route_mesh':'one_to_one',
        'bidirectional':1,
        'name':'Traffic_Item_1',
        'circuit_endpoint_type':'ipv4',
        'frame_size':64,
        'rate_mode':'percent',
        'rate_percent':2,
        'track_by':'endpoint_pair'
    }
    for key, value in kwargs.iteritems():
        temp_string = str(key)+":"+str(value)
        ixia_print(str(temp_string))        
        if re.search('port_handle', key):
            tkwargs[key]='%s/%s' % (1, value)
        elif re.search('frame_rate', key):
            mode,rate=value.split(':')
            if mode == 'percent':
                tkwargs['rate_mode']='percent'
                tkwargs['rate_percent']=rate
            elif mode == 'pps':
                tkwargs['rate_mode']='pps'
                tkwargs['rate_pps']=rate
        else:
                tkwargs[key]=value

    #################################################
    ##  Create Create Traffic                       #
    #################################################

	
    traffic_config_status = ixiangpf.traffic_config(**tkwargs)

    if traffic_config_status['status'] != '1':
        ErrorHandler('traffic_config', traffic_config_status)
    else:
        ixia_print('Create Traffic stream done')

    return(traffic_config_status)




def ixia_traffic_config_with_random_field_values(**kwargs):
    '''
    This command configures Traffic stream
    Arguments:
     -src_handle:
       ALPHA
     -dst_handle:
       ALPHA
     others
       ANY (check IXIA HLAPI traffic_config API manual for detail)
    '''

    tkwargs = {
        'mode':'create',
        'endpointset_count':1,
        'src_dest_mesh':'one_to_one',
        'route_mesh':'one_to_one',
        'bidirectional':1,
        'name':'Traffic_Item_1',
        'circuit_endpoint_type':'ipv4',
        'frame_size':64,
        'rate_mode':'percent',
        'rate_percent':2,
        'track_by':'endpoint_pair'
    }
    for key, value in kwargs.iteritems():
        temp_string = str(key)+":"+str(value)
        logger.console('\t%s' % temp_string)
        if re.search('port_handle', key):
            tkwargs[key]='%s/%s' % (1, value)
        elif re.search('frame_rate', key):
            mode,rate=value.split(':')
            if mode == 'percent':
                tkwargs['rate_mode']='percent'
                tkwargs['rate_percent']=rate
            elif mode == 'pps':
                tkwargs['rate_mode']='pps'
                tkwargs['rate_pps']=rate
            elif re.search('stack_index',key):
        	    continue
            elif re.search('field_handle',key):
        	    continue
            elif re.search('pt_handle',key):
        	    continue
            else:
                    tkwargs[key]=value
    #################################################
    ##  Configure 
    #################################################
    traffic_config_status = ixiangpf.traffic_config(**tkwargs)

    if traffic_config_status['status'] != '1':
        ErrorHandler('traffic_config_status', traffic_config_status)
    else:
        config_elements = ixiatcl.convert_tcl_list(traffic_config_status['traffic_item'])
        current_config_element = config_elements[0]
        #################################################
        ##  Adding TCP Header
        #################################################
        stack_index_var = kwargs['stack_index']
        pt_handle_var = kwargs['pt_handle']
        tkwargs = {
            'traffic_generator':'ixnetwork_540',
            'mode':'modify_or_insert',
            'stream_id':current_config_element,
            'stack_index':stack_index_var,
            'pt_handle':pt_handle_var,
        }
        traffic_config_status = ixiangpf.traffic_config(**tkwargs)
        if traffic_config_status['status'] != '1':
            ErrorHandler('Ipv4 header', traffic_config_status)
        else:
            field_handle_temp = kwargs['field_handle']
            logger.console(field_handle_temp)
            last_stack = traffic_config_status['last_stack']
            tkwargs = {
                'traffic_generator':'ixnetwork_540',
                'mode':'set_field_values',
                'header_handle':last_stack,
                'pt_handle':pt_handle_var,
                'field_handle':field_handle_temp,
                'field_activeFieldChoice':0,
                'field_auto':0,
                'field_optionalEnabled':1,
                'field_fullMesh':0,
                'field_trackingEnabled':0,
                'field_valueType':'nonRepeatableRandom',
            }
            traffic_config_status = ixiangpf.traffic_config(**tkwargs)
            if traffic_config_status['status'] != '1':
                ErrorHandler('Configure IPv4 Destination IP Address', traffic_config_status)
	
    logger.console('configuring Ipv4 random option is done')        
    return(traffic_config_status)

def ixia_traffic_config_with_random_two_fields(**kwargs):
    '''
    This command configures Traffic stream
    Arguments:
     -src_handle:
       ALPHA
     -dst_handle:
       ALPHA
     others
       ANY (check IXIA HLAPI traffic_config API manual for detail)
    '''

    tkwargs = {
        'mode':'create',
        'endpointset_count':1,
        'src_dest_mesh':'one_to_one',
        'route_mesh':'one_to_one',
        'bidirectional':1,
        'name':'Traffic_Item_1',
        'circuit_endpoint_type':'ipv4',
        'frame_size':64,
        'rate_mode':'percent',
        'rate_percent':2,
        'track_by':'endpoint_pair'
    }
    for key, value in kwargs.iteritems():
        temp_string = str(key)+":"+str(value)
        logger.console('\t%s' % temp_string)
        if re.search('port_handle', key):
            tkwargs[key]='%s/%s' % (1, value)
        elif re.search('frame_rate', key):
            mode,rate=value.split(':')
            if mode == 'percent':
                tkwargs['rate_mode']='percent'
                tkwargs['rate_percent']=rate
            elif mode == 'pps':
                tkwargs['rate_mode']='pps'
                tkwargs['rate_pps']=rate
        elif re.search('stack_index',key):
    	    continue
        elif re.search('pt_handle',key):
    	    continue
        elif re.search('field_handle_1',key):
    	    continue
        elif re.search('field_handle_2',key):
    	    continue
        else:
            tkwargs[key]=value
    #################################################
    ##  Configure a Packet
    #################################################
    traffic_config_status = ixiangpf.traffic_config(**tkwargs)

    if traffic_config_status['status'] != '1':
        ErrorHandler('traffic_config_status', traffic_config_status)
    else:
        config_elements = ixiatcl.convert_tcl_list(traffic_config_status['traffic_item'])
        current_config_element = config_elements[0]
        #################################################
        ##  Adding Headers
        #################################################
        stack_index_var = kwargs['stack_index']
        pt_handle_var = kwargs['pt_handle']
        tkwargs = {
            'traffic_generator':'ixnetwork_540',
            'mode':'modify_or_insert',
            'stream_id':current_config_element,
            'stack_index':stack_index_var,
            'pt_handle':pt_handle_var,
        }
    traffic_config_status = ixiangpf.traffic_config(**tkwargs)
    if traffic_config_status['status'] != '1':
        ErrorHandler('Ipv4 header', traffic_config_status)
    else:
        last_stack = traffic_config_status['last_stack']
        field_handle_1_var = kwargs['field_handle_1']
        tkwargs = {
            'traffic_generator':'ixnetwork_540',
            'mode':'set_field_values',
            'header_handle':last_stack,
            'pt_handle':pt_handle_var,
            'field_handle':field_handle_1_var,
            'field_activeFieldChoice':0,
            'field_auto':0,
            'field_optionalEnabled':1,
            'field_fullMesh':0,
            'field_trackingEnabled':0,
            'field_valueType':'nonRepeatableRandom',
        }
    traffic_config_status = ixiangpf.traffic_config(**tkwargs)
    if traffic_config_status['status'] != '1':
        ErrorHandler('Configure random traffic done', traffic_config_status)
    else:
        field_handle_2_var = kwargs['field_handle_2']
        tkwargs = {
            'traffic_generator':'ixnetwork_540',
            'mode':'set_field_values',
            'header_handle':last_stack,
            'pt_handle':pt_handle_var,
            'field_handle':field_handle_2_var,
            'field_activeFieldChoice':0,
            'field_auto':0,
            'field_optionalEnabled':1,
            'field_fullMesh':0,
            'field_trackingEnabled':0,
            'field_valueType':'nonRepeatableRandom',
        }
    traffic_config_status = ixiangpf.traffic_config(**tkwargs)
    if traffic_config_status['status'] != '1':
        ErrorHandler('Configure Random Traffic is done ', traffic_config_status)	
	
    logger.console('configuring Random Traffic option are done')
    return(traffic_config_status)


def ixia_traffic_config_with_random_l4_and_l3_header(**kwargs):
    '''
    This command configures Traffic stream
    Arguments:
     -src_handle:
       ALPHA
     -dst_handle:
       ALPHA
     others
       ANY (check IXIA HLAPI traffic_config API manual for detail)
    '''

    tkwargs = {
        'mode':'create',
        'endpointset_count':1,
        'src_dest_mesh':'one_to_one',
        'route_mesh':'one_to_one',
        'bidirectional':1,
        'name':'Traffic_Item_1',
        'circuit_endpoint_type':'ipv4',
        'frame_size':64,
        'rate_mode':'percent',
        'rate_percent':2,
        'track_by':'endpoint_pair'
    }
    for key, value in kwargs.iteritems():
        temp_string = str(key)+":"+str(value)
        logger.console('\t%s' % temp_string)
        if re.search('port_handle', key):
            tkwargs[key]='%s/%s' % (1, value)
        elif re.search('frame_rate', key):
            mode,rate=value.split(':')
            if mode == 'percent':
                tkwargs['rate_mode']='percent'
                tkwargs['rate_percent']=rate
            elif mode == 'pps':
                tkwargs['rate_mode']='pps'
                tkwargs['rate_pps']=rate
        elif re.search('stack_index',key):
    	    continue
        elif re.search('pt_handle',key):
    	    continue
        elif re.search('field_handle_1',key):
    	    continue
        elif re.search('field_handle_2',key):
    	    continue
        elif re.search('header_length',key):
    	    continue
        else:
            tkwargs[key]=value
    #################################################
    ##  Configure a Packet
    #################################################
    traffic_config_status = ixiangpf.traffic_config(**tkwargs)

    if traffic_config_status['status'] != '1':
        ErrorHandler('traffic_config_status', traffic_config_status)
    else:
        config_elements = ixiatcl.convert_tcl_list(traffic_config_status['traffic_item'])
        current_config_element = config_elements[0]
        #################################################
        ##  Adding IPv4 Headers
        #################################################
        stack_index_ipv4 = kwargs['stack_index_ipv4']
        pt_handle_ipv4 = kwargs['pt_handle_ipv4']
        tkwargs = {
            'traffic_generator':'ixnetwork_540',
            'mode':'modify_or_insert',
            'stream_id':current_config_element,
            'stack_index':stack_index_ipv4,
            'pt_handle':pt_handle_ipv4,
        }
            
    traffic_config_status = ixiangpf.traffic_config(**tkwargs)
    if traffic_config_status['status'] != '1':
        ErrorHandler('Ipv4 header', traffic_config_status)
        last_stack = traffic_config_status['last_stack']
        ipv4_header_length = kwargs['ipv4_header_length']
        ipv4_header_length_int = int(ipv4_header_length)
    for x in range(0,ipv4_header_length_int):
        temp_index = x+1 
        str1 = "ipv4_field_handle_"+str(temp_index)
        field_handle_1_var = kwargs[str1]
        tkwargs = {
            'traffic_generator':'ixnetwork_540',
            'mode':'set_field_values',
            'header_handle':last_stack,
            'pt_handle':pt_handle_ipv4,
            'field_handle':field_handle_1_var,
            'field_activeFieldChoice':0,
            'field_auto':0,
            'field_optionalEnabled':1,
            'field_fullMesh':0,
            'field_trackingEnabled':0,
            'field_valueType':'nonRepeatableRandom',
        }
    traffic_config_status = ixiangpf.traffic_config(**tkwargs)
    if traffic_config_status['status'] != '1':
        ErrorHandler('Configure random traffic done IPv4', traffic_config_status)
        logger.console('Configuring TCP/UDP Header')
        stack_index_tcp = kwargs['stack_index_tcp']
        pt_handle_tcp = kwargs['pt_handle_tcp']
        tkwargs = {
            'traffic_generator':'ixnetwork_540',
            'mode':'modify_or_insert',
            'stream_id':current_config_element,
            'stack_index':stack_index_tcp,
            'pt_handle':pt_handle_tcp,
        }
    traffic_config_status = ixiangpf.traffic_config(**tkwargs)
    if traffic_config_status['status'] != '1':
        ErrorHandler('TCP header', traffic_config_status)
        last_stack = traffic_config_status['last_stack']
        tcp_header_length = kwargs['tcp_header_length']
        tcp_header_length_int = int(tcp_header_length)
    for x in range(0,tcp_header_length_int):
        temp_index = x+1 
        str1 = "tcp_field_handle_"+str(temp_index)
        field_handle_1_var = kwargs[str1]
        tkwargs = {
            'traffic_generator':'ixnetwork_540',
            'mode':'set_field_values',
            'header_handle':last_stack,
            'pt_handle':pt_handle_tcp,
            'field_handle':field_handle_1_var,
            'field_activeFieldChoice':0,
            'field_auto':0,
            'field_optionalEnabled':1,
            'field_fullMesh':0,
            'field_trackingEnabled':0,
            'field_valueType':'nonRepeatableRandom',
        }
    traffic_config_status = ixiangpf.traffic_config(**tkwargs)
    if traffic_config_status['status'] != '1':
        ErrorHandler('Configure random traffic done ', traffic_config_status)
	
    logger.console('configuring Random Traffic option are done')
    return(traffic_config_status)




if __name__ == "__main__":
    pdb.set_trace()
    t = PacketDiff(1072, 5, 0.001)
