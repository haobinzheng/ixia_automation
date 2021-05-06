#from ixia_ngfp_lib import *
from utils import *
from settings import *
from test_process import * 
from common_lib import *

### This codes are hacking for the time being ####
### all the methods are self-sustained

def ixia_dhcp_codes(multiplier):
	chassis_ip = '10.105.241.234'
	tcl_server = '10.105.241.234'
	ixnetwork_tcl_server = "10.105.19.19:8004"
	portsList_v4 = ['1/1','1/2','1/7','1/8']
	debug("Setup IXIA with ports running as dhcp client mode")
	ports = ixia_connect_ports(chassis_ip,portsList_v4,ixnetwork_tcl_server,tcl_server)
	topo_list = []
	dhcp_handle_list = []
	counter = 1
	for port in ports:
		(topo_handle,device_group_handle) = ixia_port_topology(port,multiplier,topo_name="Topology "+str(counter))
		topo_list.append(topo_handle)
		dhcp_status = ixia_emulation_dhcp_group_config(handle=device_group_handle)	
		dhcp_client_handle = dhcp_status['dhcpv4client_handle']
		dhcp_handle_list.append(dhcp_client_handle)
		counter +=1 

	console_timer(400,msg="Wait for 400 sec after dhcp clients are created")
	topo_h1 = topo_list[0]
	topo_h2 = topo_list[1]
	topo_h3 = topo_list[2]
	topo_h4 = topo_list[3]
	ixia_start_protcols_verify(dhcp_handle_list)
	tprint("Creating traffic item I....")
	ixia_create_ipv4_traffic(topo_h1,topo_h2,rate=10)
	tprint("Creating traffic item II....")
	ixia_create_ipv4_traffic(topo_h2,topo_h1,rate=10)
	tprint("Creating traffic item III....")
	ixia_create_ipv4_traffic(topo_h3,topo_h4,rate=10)
	tprint("Creating traffic item IV....")
	ixia_create_ipv4_traffic(topo_h4,topo_h3,rate=10)

	console_timer(20,msg="Wait for 20 sec after traffics are created")
	ixia_start_traffic()
	console_timer(20,msg="Measure traffic for 20 sec and print out stats")
	tprint("Collect statistics after running traffic for 15 seconds, Please take a look at printed traffic stats to make sure no packet loss..")
 
	traffic_stats = ixiangpf.traffic_stats(
	    mode = 'flow'
	    )
	if traffic_stats['status'] != '1':
	    tprint('\nError: Failed to get traffic flow stats.\n')
	    tprint(traffic_stats)
	    sys.exit()

	flow_stat_list = parse_traffic_stats(traffic_stats)
	print_flow_stats_3rd(flow_stat_list)

def fgt_548d_setup():
	icl_ports = ['port47','port48']
	core_ports = ["port1","port2","port3","port4"]
	tprint('------------------------------ login Fortigate devices -----------------------')
	fgt1_dir = {}
	fgt2_dir = {}
	fgt_dir_list = []
	
	fgt1 = get_switch_telnet_connection(fgt1_com,fgt1_port,password='admin')
	fgt1_dir['name'] = fgt1_name
	fgt1_dir['location'] = fgt1_location
	fgt1_dir['telnet'] = fgt1
	fgt1_dir['cfg'] = fgt1_cfg
	fgt_dir_list.append(fgt1_dir)

	fgt2 = get_switch_telnet_connection(fgt2_com,fgt2_port,password='admin')
	fgt2_dir['name'] = fgt2_name
	fgt2_dir['location'] = fgt2_location
	fgt2_dir['telnet'] = fgt2
	fgt2_dir['cfg'] = fgt2_cfg
	fgt_dir_list.append(fgt1_dir)
	if upgrade_fgt and test_setup.lower() == "fg-548d" and not settings.FACTORY:
		#You need to change build number at settings
		# the following procudure is a hacking for the time bing
		fgt_upgrade_548d()
		# build = settings.build_548d
		# cmd = f"execute switch-controller switch-software upload tftp FSW_548D_FPOE-v6-build0{build}-FORTINET.out 10.105.19.19"
		# switch_exec_cmd(fgt1, cmd)
		# cmd = f"execute switch-controller switch-software upload tftp FSW_548D-v6-build0{build}-FORTINET.out 10.105.19.19"
		# switch_exec_cmd(fgt1, cmd)

		# cmd = "execute switch-controller switch-software list-available"
		# switch_show_cmd_name(fgt1_dir,cmd)

		# cmd = "execute switch-controller switch-software upgrade S548DN4K17000133 S548DN-IMG.swtp"
		# switch_exec_cmd(fgt1, cmd)
		# console_timer(300)
		# cmd = "execute switch-controller switch-software upgrade S548DF4K16000653 S548DF-IMG.swtp"
		# switch_exec_cmd(fgt1, cmd)
		# console_timer(300)
		# cmd = "execute switch-controller switch-software upgrade S548DF4K17000028 S548DF-IMG.swtp"
		# switch_exec_cmd(fgt1, cmd)
		# console_timer(300)
		# cmd = "execute switch-controller switch-software upgrade S548DF4K17000014 S548DF-IMG.swtp"
		# switch_exec_cmd(fgt1, cmd)
		# console_timer(300)
		# cmd = "execute switch-controller get-upgrade-status"
		# switch_show_cmd_name(fgt1_dir,cmd)

	if settings.FACTORY:
		tprint("=============== resetting all switches to factory ===========")
		for dut in dut_list:
			switch_interactive_exec(dut,"execute factoryresetfull","Do you want to continue? (y/n)")
		print("after reset sleep 5 min")
		console_timer(300)
		print("after sleep, relogin, should change password ")
	

		tprint('------------------------------ end of login Fortigate devices -----------------------')
		dut1 = get_switch_telnet_connection_new(dut1_com,dut1_port)
		dut2 = get_switch_telnet_connection_new(dut2_com,dut2_port)
		dut3 = get_switch_telnet_connection_new(dut3_com,dut3_port)
		dut4 = get_switch_telnet_connection_new(dut4_com,dut4_port)
		dut_list = [dut1,dut2,dut3,dut4]
		dut1_dir['telnet'] = dut1 
		dut2_dir['telnet'] = dut2
		dut3_dir['telnet'] = dut3
		dut4_dir['telnet'] = dut4


	tprint(" -------------- After factory reset, find out FSW images are reset as well -------------------")
	for dut_dir in dut_dir_list:
		dut = dut_dir['telnet']
		dut_name = dut_dir['name']
		image = find_dut_image(dut)
		tprint(f"============================ {dut_name} software image = {image}================")
	tprint("------------ configure port lldp profile to auto-isl --------------------")
	for dut_dir in dut_dir_list:
		switch_configure_cmd_name(dut_dir,"config switch physical-port")
		for port in core_ports:
			switch_configure_cmd_name(dut_dir,f"edit {port}")
			switch_configure_cmd_name(dut_dir,"set lldp-profile default-auto-isl")
			switch_configure_cmd_name(dut_dir,"next")
		switch_configure_cmd_name(dut_dir,"end")	
	tprint("------------  After configuring auto-isl, wait for 5 min  --------------------")
	console_timer(300)
	#relogin_dut_all(dut_list)
	for dut_dir in dut_dir_list:
		dut_name = dut_dir['name']
		switch_show_cmd_name(dut_dir,"get system status")
		dut = dut_dir['telnet']
		trunk_dict_list = dut_switch_trunk(dut)
		for trunk in trunk_dict_list:
			if set(trunk['mem'] ) == set(icl_ports):
				switch_configure_cmd_name(dut_dir,"config switch trunk")
				switch_configure_cmd_name(dut_dir,f"edit {trunk['name']}")
				switch_configure_cmd_name(dut_dir,'set mclag-icl enable')
				switch_configure_cmd_name(dut_dir,'end')

				if 'dut1' in dut_name or 'dut2' in dut_name:
					switch_configure_cmd_name(dut_dir,"config switch auto-isl-port-group")
					switch_configure_cmd_name(dut_dir,"edit core1")
					switch_configure_cmd_name(dut_dir,f"set members {core_ports[0]} {core_ports[1]} {core_ports[2]} {core_ports[3]}")
					switch_configure_cmd_name(dut_dir,'end')
				break
	print("after configure mclag wait for 300s")
	console_timer(300)
	
	for d in dut_dir_list:
		configure_switch_file(d['telnet'],d['cfg_b'])

	tprint("++++Wait for 120 seconds before configuring fortigate for FSW edge trunk")
	console_timer(120)
	tprint("------------  start configuring fortigate  --------------------")
	trunk_config = """
	config switch-controller managed-switch
			edit S548DF4K16000653
			config ports
				delete trunk1
					edit trunk1
			        set type trunk
			        set mode lacp-active
			        set mclag enable
			        set members port13
					next
			end
		next
		edit S548DN4K17000133
			config ports
				delete trunk1
				edit trunk1
					set type trunk
					set mode lacp-active
					set mclag enable
					set members port13
			next
		end
	end
	"""
	config_block_cmds(fgt1_dir, trunk_config)
	console_timer(200,msg="after configuring everything, wait for 200 sec")
	if upgrade_fgt and test_setup.lower() == "fg-548d":
		tprint("=================== Upgrade all managed FSW via FGT =================")
		fgt_upgrade_548d()
	relogin_dut_all(dut_list)
	# dut1 = get_switch_telnet_connection_new(dut1_com,dut1_port)
	# dut2 = get_switch_telnet_connection_new(dut2_com,dut2_port)
	# dut3 = get_switch_telnet_connection_new(dut3_com,dut3_port)
	# dut4 = get_switch_telnet_connection_new(dut4_com,dut4_port)
	tprint("------------  end of configuring fortigate  --------------------")
	tprint("After configuring all devices wait for 300s, then verify everything")
	console_timer(300)
	pre_test_verification(dut_list)