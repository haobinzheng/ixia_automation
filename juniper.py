import re
import os
import sys
from collections import OrderedDict

def debug(msg):
	return
	print(f"Debug: {msg}")

def create_vni_from_vlans(vlan_file):
	with open("vlans.txt","r") as f:
		lines = f.readlines()
		for line in lines:
			if "vxlan" in line:
				continue
			vlan = line.split()[4]
			vlan_str = format(int(vlan),"04d")
			#print(vlan)	
			vni_str = "185" + vlan_str
			vlan_config = f"set vlans VNI-185-{vlan_str} vlan-id {vlan}"
			vni_config = f"set vlans VNI-185-{vlan_str} vxlan vni {vni_str}"
			# print(vlan_config)
			# print(vni_config)

			evpn_vlan_config = f"set routing-instances EVPN vlans VNI-185-{vlan_str} vlan-id {vlan}"
			evpn_vni_config = f"set routing-instances EVPN vlans VNI-185-{vlan_str} vxlan vni {vni_str}"
			evpn_vni_config_node = f"set routing-instances EVPN vlans VNI-185-{vlan_str} vxlan ingress-node-replication"
			print(evpn_vlan_config)
			print(evpn_vni_config)
			print(evpn_vni_config_node)

def create_vlans_config(vlans_list):
	for vlan in vlans_list:
		vlan_str = format(int(vlan),"04d")
		#print(vlan)	
		vlan_config = f"set vlans VNI-185-{vlan_str} vlan-id {vlan}"
		print(vlan_config)

def create_interface_config(port_vlan_dict_str):
	for p,v in port_vlan_dict_str.items():
		fpc,mod,port_num = p.split('/')
		if int(port_num) -1  < 24:
			interface_config = f'set interface ge-{int(fpc)-1}/0/{int(port_num)-1} unit 0 ethernet-switching vlan members {v}'
		else:
			interface_config = f'set interface mge-{int(fpc)-1}/0/{int(port_num)-1} unit 0 ethernet-switching vlan members {v}'

		print(interface_config)

def create_interface_description(port_description_dict):
	for p,v in port_description_dict.items():
		fpc,mod,port_num = p.split('/')
		if int(port_num) -1  < 24:
			interface_config = f'set interface ge-{int(fpc)-1}/0/{int(port_num)-1} description "{v}"'
		else:
			interface_config = f'set interface mge-{int(fpc)-1}/0/{int(port_num)-1} description "{v}"'

		print(interface_config)

def generate_config_from_cisco(idf_file):
	vlans_list = []
	with open(idf_file,'r') as f:
		lines = f.readlines()
		regex_vlan = r'^vlan ([0-9\,]+)'
		#regex_interface = r'interface GigabitEthernet([0-9\/]+)'
		regex_interface = r'interface ([a-zA-Z]+)([0-9\/]+)'
		regex_port_vlan = r' switchport access vlan ([0-9]+)'
		regex_description = r' description (.*)'
		regex_dict = OrderedDict()
		port_vlan_dict = {}
		port_vlan_dict_str = {}
		port_description_dict = {}
		regex_dict["vlan"] = regex_vlan
		regex_dict["interface"] = regex_interface
		regex_dict["description"] = regex_description
		regex_dict["port_vlan"] = regex_port_vlan

		for line in lines:
			found = None
			for name,regex in regex_dict.items():
				found = re.match(regex,line)
				if found != None:
					found_name = name
					break
			if found != None:
				debug("Found Something!")
				if found_name == "vlan":
					debug("Found Vlan!")
					vlans = found.group(1)
					vlans_line = vlans.split(",")
					for v in vlans_line:
						vlans_list.append(v)
				elif found_name == "interface":
					debug("Found Interface!")
					interface_type = found.group(1)
					port_name = found.group(2)
					debug(port_name)
				elif found_name == "port_vlan":
					debug("Port Vlan!")
					port_vlan = found.group(1)
					port_vlan_dict[port_name] = port_vlan
					port_vlan_str = format(int(port_vlan),"04d")
					port_vlan_str = f"VNI-185-{port_vlan_str}"
					port_vlan_dict_str[port_name] = port_vlan_str
				elif found_name == "description":
					debug(f"For matching description port name = {port_name}")
					port_description = found.group(1)
					if interface_type == "GigabitEthernet":
						port_description_dict[port_name] = port_description
						debug(f"Found Description! {port_name} -- {port_description_dict[port_name]} ")

		debug(vlans_list)
		create_vlans_config(vlans_list)
		debug(port_vlan_dict)
		create_interface_config(port_vlan_dict_str)
		debug(port_description_dict)
		create_interface_description(port_description_dict)

if __name__ == "__main__":
	generate_config_from_cisco("idf_2.txt")





