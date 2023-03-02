import wexpect
from time import sleep
from protocols_class import *
from device_config import *


if __name__ == "__main__":

	setup = test_setup("yaml_testcase/poe_bt_testing.yaml")
	#print(setup)
	setup.pretty_print()
	for test in setup.testcase_obj_list:
		print(test.case_name)
		print(test.dut_port_list)
		print(test.class_list)
		print(test.poe_port_list)
		for tcl in test.tcl_procedure_list:
			print(tcl)
			if type(tcl) == dict:
				tcl = dict2obj(tcl)
				print(tcl.proc_name)
				print(tcl.commands)
	exit()
	file = 'tbinfo_poe_testing_npi.xml'
	tb = parse_tbinfo_untangle(file)
	testtopo_file = 'topo_poe_npi_6xx.xml'
	parse_testtopo_untangle(testtopo_file,tb)
	tb.show_tbinfo()


	switches = []
	devices=[]
	for d in tb.devices:
		if d.type == "FSW" and d.active == True:
			switch = FortiSwitch_XML(d,topo_db=tb)
			switches.append(switch)
			devices.append(switch)

	for c in tb.connections:
		c.update_devices_obj(devices)

	# pshell = power_shell_tcl()
	new_power_shell = True
	for test in setup.testcase_obj_list:
		print(test.case_name)
		for tcl in test.tcl_procedure_list:
			print(tcl)
			if type(tcl) == dict:
				tcl = dict2obj(tcl)
			print(tcl.proc_name)
			print(tcl.commands)
			if new_power_shell:
				tprint(f"Launching Power Shell TCL with PSA IP = {tcl.sifo_ip}")
				pshell = power_shell_tcl(tcl.sifo_ip)
				new_power_shell = False
			pshell.tcl_send_commands(tcl.commands,tcl.proc_name)
			sw = switches[0]
			while True:
				sw.print_show_command("get switch poe inline")
				output = input("Please check poe inline output. Do you want to finish showing this command?(Y/N): ")
				if output.upper() == "Y":
					break
			if tcl.tcl_close == True:
				pshell.tcl_close_shell()
				new_power_shell = True
	pshell.tcl_close_shell()