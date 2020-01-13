from utils import *
from settings import *
from test_process import * 
from common_lib import *
from common_codes import *
from cli_functions import *


def sw_init_config(*args, **kwargs):
    dut_dir = kwargs['device']

    dut_name = dut_dir['name']  
    dut_location = dut_dir['location'] 
    dut = dut_dir['telnet'] 
    dut_cfg_file = dut_dir['cfg']  
    mgmt_ip = dut_dir['mgmt_ip']  
    mgmt_mask = dut_dir['mgmt_mask']  
    loop0_ip = dut_dir['loop0_ip']   
    vlan_ip = dut_dir['vlan1_ip'] 
    vlan1_mask = dut_dir['vlan1_mask']  
    split_ports = dut_dir['split_ports'] 
    port_40g = [dut_dir['40g_ports'] 


	config_mgmt_mode = f"""
	config system interface
    edit mgmt
	set mode static
	end
	config system interface
    	edit "mgmt"
		set mode static
    	end
	config system interface
    	edit "mgmt"
    	set mode static
    	end
	"""

	config_sys_interface = f"""
	config system interface
    edit mgmt
    	set mode static
        set ip {mgmt_ip} {mgmt_mask}
        set allowaccess ping https http ssh snmp telnet radius-acct
    next
    edit vlan1
        set ip {vlan1_ip} {vlan1_mask}
        set allowaccess ping https ssh telnet
        set vlanid 1
        set interface internal
    next
    edit "loop0"
        set ip {loop0_ip} {loop0_mask}
        set allowaccess ping https http ssh telnet
        set type loopback
    next
	end
	"""
    for port in split_ports:
        config_split_ports = f"""
        config switch phy-mode
        set {port}-phy-mode 4x10G
        end
        """
        switch_interactive_yes(dut,"Do you want to continue? (y/n)")
