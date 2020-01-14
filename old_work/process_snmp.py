import os
import multiprocessing
import subprocess
from switch_class import *
from utility import *



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
	sw_dut_J = switch_list[1]
	sw_dut_A  = switch_list[2]
	sw_8700_D = switch_list[3]
	sw_8700_E = switch_list[4]
	sw_8700_B = switch_list[5]
	sw_8700_F = switch_list[6]
	sw_8700_G = switch_list[7]

	dut = cienaswitch(sw_dut_A)
	sw_dut = sw_dut_J
	print "start to exercise snmp walk"
	p_snmp_1 = start_snmp(sw_dut)
	p_snmp_2 = start_snmp(sw_dut)
	while True:
		if p_snmp_1.poll() != None:
			p_snmp_1 = start_snmp(sw_dut)
		elif p_snmp_2.poll() != None:
			p_snmp_2 = start_snmp(sw_dut)
		else:
			sleep(5)
