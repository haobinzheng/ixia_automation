import os
import multiprocessing
import subprocess
from switch_class import *



if __name__ == "__main__":
	device_file = 'metro_switches_new'
	device = get_csv(device_file)
	routerFile = open(device_file, 'r')
	switch_dev = [a for a in routerFile]
	switch_list =  []
	for sw in switch_dev:
		sw_obj = switch(sw)
		switch_list.append(sw_obj)

	dw_dut_C  = switch_list[0]
	sw_dut = switch_list[1]
	sw_dut_A  = switch_list[2]
	sw_8700_D = switch_list[3]
	sw_8700_E = switch_list[4]
	sw_8700_B = switch_list[5]
	sw_8700_F = switch_list[6]
	sw_8700_G = switch_list[7]

	dut = cienaswitch(sw_dut)
	collect_dut_vc(dut)
	ingress_tu = ingress_tunnel(dut)
	egress_tu = egress_tunnel(dut)
	#ingress_tu.build_tunnel_all()
	#egress_tu.build_tunnel_all()
	print "start to excise show commands"
	
	while True:
		ingress_tu.show_tunnel_all()
		egress_tu.show_tunnel_all()
		dut.vc_db.flush_mac_all_vc()
		dut.vc_db.show_vc_all()
		show_macaddr(dut)
	
