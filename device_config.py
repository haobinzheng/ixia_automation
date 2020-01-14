from utils import *
import settings 
from test_process import * 
from common_lib import *
from common_codes import *
from cli_functions import *

class Router_BGP():
    def __init__(self, *args, **kwargs):
        pass

class FSW():
    def __init__(self, *args,**kwargs):
        dut_dir = args[0]
        self.comm = dut_dir['comm']  
        self.comm_port = dut_dir['comm_port']  
        self.name = dut_dir['name']  
        self.location = dut_dir['location'] 
        self.console = dut_dir['telnet']  
        self.cfg_file = dut_dir['cfg'] 
        self.mgmt_ip = dut_dir['mgmt_ip'] 
        self.mgmt_mask = dut_dir['mgmt_mask']  
        self.loop0_ip = dut_dir['loop0_ip']  
        self.vlan1_ip = dut_dir['vlan1_ip'] 
        self.vlan1_subnet = dut_dir['vlan1_subnet']  
        self.vlan1_mask = dut_dir['vlan1_mask'] 
        self.split_ports = dut_dir['split_ports'] 
        self.ports_40g = dut_dir['40g_ports']


def update_data_loop(self):
      if len(self.receive_queue) > 0:
         updated_data = self.receive_queue.pop(0)
         if updated_data[0][0] == "Restart":
            print ("Displayer: scanner just restarted real-time scaning,I am now clearing display queue, but scroll display is still going on without any change.....")
            self.display_queue = []  # ininitiaze display queue only, but will not change the display object
            return
         elif updated_data[0][0] == "Done":
            print ("Displayer: scanner has done one round of scanning, I am now displaying all the scanned stocks...")
            try:  # This check is actually redundant
               if self.display_queue[-1][0] == "Done" or self.display_queue[-1][0] == "Restart":
                  self.display_queue.pop()
            except Exception as e:
               print ("Displayer: display queue is empty")
            print ("Displayer: scanner is done with scanning, now my display queue = {}".format(self.display_queue))
            #self.market_one = MultiProc_StockMarket(self.display_queue, self.order)
            self.market_one.load_market(self.display_queue)
         else:
            print("Displayer: popping one stock information from top of the receiving queue and dislay: {}".format(updated_data))
            #self.market_one = MultiProc_StockMarket(updated_data, self.order)
            self.market_one.load_market(updated_data)

def fsw_upgrade(*args,**kwargs):
    build = int(kwargs['build'])
    dut_dict = kwargs['dut_dict']
    dut_name = dut_dict['name']
    dut = dut_dict['telnet']
    
    tprint(f"=================== Upgrading FSW {dut_name} to build # {build} =================")
    model = find_dut_model(dut)
    model = model.strip()
    if model == "FSW_448D_FPOE":
        image_name = f"FSW_448D_FPOE-v6-build0{build}-FORTINET.out"
    elif model == "FSW_448D_POE":
        image_name =  f"FSW_448D_POE-v6-build0{build}-FORTINET.out" 
    elif model == "FSW_448D-v6":
        image_name = f"FSW_448D-v6-build0{build}-FORTINET.out"
    elif model == "FortiSwitch-3032E":
        image_name = f"FSW_3032E-v6-build0{build}-FORTINET.out"
    elif model == "FortiSwitch-3032D":
        image_name = f"FSW_3032D-v6-build0{build}-FORTINET.out"
    elif model == "FortiSwitch-1048E":
        image_name = f"FSW_1048E-v6-build0{build}-FORTINET.out"
    elif model == "FortiSwitch-1048D":
        image_name = f"FSW_1048D-v6-build0{build}-FORTINET.out"
    elif model == "FortiSwitch-1024D":
        image_name = f"FSW_1024D-v6-build0{build}-FORTINET.out"
    else:
        tprint("!!!!!!!!! Not able to identify switch platform, upgrade fails")
        return False

    dprint(f"image name = {image_name}")
    cmd = f"execute restore image tftp {image_name} 10.105.19.19"
    tprint(f"upgrade command = {cmd}")
    switch_interactive_exec(dut,cmd,"Do you want to continue? (y/n)")
    #console_timer(60,msg="wait for 60s to download image from tftp server")
    #switch_wait_enter_yes(dut,"Do you want to continue? (y/n)")
    prompt = "Do you want to continue? (y/n)"
    output = switch_read_console_output(dut,timeout = 40)
    dprint(output)
    result = False
    for line in output: 
        if "Command fail" in line:
            Info(f"upgrade with image {image_name} failed for {dut_name}")
            result = False

        elif "Check image OK" in line:
            Info(f"At {dut_name} image {image_name} is downloaded and checked OK,upgrade should be fine")
            result = True

        elif "Writing the disk" in line:
            Info(f"At {dut_name} image {image_name} is being written into disk, upgrade is Good!")
            result = True

        elif "Do you want to continue" in line:
            dprint(f"Being prompted to answer yes/no 2nd time.  Prompt = {prompt}")
            switch_enter_yes(dut)
            result = True
        else:
            pass
    return result

def sw_init_config(*args, **kwargs):
    dut_dir = kwargs['device']

    dut_name = dut_dir['name']  
    dut_location = dut_dir['location'] 
    dut = dut_dir['telnet'] 
    dut_cfg_file = dut_dir['cfg']  
    mgmt_ip = dut_dir['mgmt_ip']  
    mgmt_mask = dut_dir['mgmt_mask']  
    loop0_ip = dut_dir['loop0_ip']   
    vlan1_ip = dut_dir['vlan1_ip']
    vlan1_subnet = dut_dir['vlan1_subnet']
    vlan1_mask = dut_dir['vlan1_mask']  
    split_ports = dut_dir['split_ports'] 
    ports_40g = dut_dir['40g_ports'] 

    config_global_hostname = f"""
    config system global
    set hostname {dut_name}
    end
    """

    config_cmds_lines(dut,config_global_hostname)

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
        set ip {loop0_ip} 255.255.255.255
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

    for port in ports_40g:
        sw_config_port_speed(dut,port,"40000cr4")

    ospf_config = f"""
    config router ospf
    set router-id {loop0_ip}
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
                set prefix {vlan1_subnet} 255.255.255.0
            next
        end
        config redistribute "connected"
            set status enable
        end
    end
    """
    config_cmds_lines(dut,ospf_config)

    for port in split_ports:
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

    switch_show_cmd(dut,"show system interface")
    switch_show_cmd(dut,"get switch module summary")
    switch_show_cmd(dut,"show router ospf")
    switch_show_cmd(dut,"show router static")