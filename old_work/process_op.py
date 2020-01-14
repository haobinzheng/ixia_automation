import os
import multiprocessing
import subprocess
from switch_class import *
from class_dut import *



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
	sw_5160_J = switch_list[1]
	sw_5142_A  = switch_list[2]
	sw_8700_D = switch_list[3]
	sw_8700_E = switch_list[4]
	sw_8700_B = switch_list[5]
	sw_5142_F = switch_list[6]
	sw_3190_G = switch_list[7]

	dut_J = CN_5160_J(sw_5160_J)
	dut_F = CN_5142_F(sw_5142_F)
	dut_G = CN_3190_G(sw_3190_G)
	print "start the process to excise mtu"
	
	while True:
		dut_J.sweep_active_port_mtu()
		dut_J.disable_ports()
		dut_J.enable_ports()
		dut_F.sweep_active_port_mtu()
		dut_F.disable_ports()
		dut_F.enable_ports()
		dut_G.sweep_active_port_mtu()
		dut_G.disable_ports()
		dut_G.enable_ports()
