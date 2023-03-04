import wexpect
from time import sleep
from protocols_class import *
from device_config import *
from jinja2 import Template
from jinja2 import Environment, FileSystemLoader
import jinja2.ext

def jinja2_zip(*args):
    return zip(*args)

if __name__ == "__main__":
	sys.stdout = Logger("Log/poe_bt_testing.log")
	
	# for test in setup.testcase_obj_list:
	# 	print(test.case_name)
	# 	print(test.dut_port_list)
	# 	print(test.class_list)
	# 	print(test.poe_port_list)
	# 	for tcl in test.tcl_procedure_list:
	# 		print(tcl)
	# 		if type(tcl) == dict:
	# 			tcl = dict2obj(tcl)
	# 			print(tcl.proc_name)
	# 			print(tcl.commands)
	# exit()

	def jinja_zip(*args):
		return zip(*args)
	env = Environment(loader=FileSystemLoader('yaml_testcase'),extensions=[jinja2.ext.do])
	print(env.loader.list_templates())

	# env = Environment()
	# env.filters['zip'] = jinja2_zip
	env.filters['jinja_zip'] = jinja_zip
	template = env.get_template('poe_testing.yml.j2')
	yaml_str = template.render()
	print(yaml_str)
	yaml_dict = yaml.safe_load(yaml_str)
	 
	# Write the dictionary to a YAML file
	with open('yaml_testcase/poe_npi_testing.yaml', 'w') as f:
			yaml.dump(yaml_dict, f)
	#Use this newly generated yaml file to set up testing
	setup = test_setup("yaml_testcase/poe_npi_testing.yaml")
	#setup.pretty_print()

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
	sw = switches[0]
	timer = 60*15 #10 minutes
	for test in setup.testcase_obj_list:
		if test.execute == False:
			continue
		print(test.case_name)
		print(test.dut_port_list)
		print(test.class_list)
		print(test.poe_port_list)
		
		# Start the timer
		for tcl in test.tcl_procedure_list:
			if type(tcl) == dict:
				tcl = dict2obj(tcl)
			print(tcl)
			print(tcl.proc_name)
			print(tcl.commands)
			print(tcl.poe_class)
			if tcl.execute == False:
				continue
			if new_power_shell:
				tprint(f"Launching Power Shell TCL with PSA IP = {tcl.sifo_ip}")
				pshell = power_shell_tcl(tcl.sifo_ip)
				new_power_shell = False
			pshell.tcl_send_commands_direct(tcl.disconnect_commands,"disconnect")
			sleep(60)
			pshell.tcl_send_commands_direct(tcl.commands,tcl.proc_name)
			poe_inline_dict = {}
			start_time = time.time()
			while True:
				if time.time() - start_time >  timer:
					ErrorNotify(f"Failed After {timer} seconds:  test case {test.case_name} |  TCL procedure {tcl.proc_name} | POE Class {tcl.poe_class}: Not to deliever power to all switch ports {test.dut_port_list}")
					break
				sleep(10)
				#sw.print_show_command("get switch poe inline")
				output = collect_show_cmd(sw.console,"get switch poe inline")
				for line in output:
					for p in test.dut_port_list:
						if p in line and "Delivering Power" in line and str(tcl.poe_class) in line :
							items = line.split()
							dprint(items)
							portname = items[0]
							status = items[1]
							state = f"{items[2]} {items[3]}"
							max_power = items[4]
							power_comsumption = items[5]
							priority = items[6]
							poe_class = items[7]
							poe_inline_dict.setdefault(portname,{}) 
							poe_inline_dict[portname]["status"] =status
							poe_inline_dict[portname]["state"] = state
							poe_inline_dict[portname]["max_power"] = max_power
							poe_inline_dict[portname]["power_comsumption"] = power_comsumption
							poe_inline_dict[portname]["priority"] = priority
							poe_inline_dict[portname]["poe_class"] = poe_class
							dprint(float(poe_inline_dict[portname]["max_power"]),float(tcl.max_power))
							if float(poe_inline_dict[portname]["max_power"]) != float(tcl.max_power):
								poe_inline_dict[portname]["powered"] = False
							else:
								poe_inline_dict[portname]["powered"] = True
 									 
				print_dict(poe_inline_dict)
				ports = poe_inline_dict.keys()
				result = True
				if set(ports) != set(test.dut_port_list):
					result = False
					continue
				for p,p_status in poe_inline_dict.items():
					if p_status["powered"] == False:
						print(f'{p} poe checking result = {p_status["powered"]}')
						result = False
						break
				if result == True:
					tprint(f"PASSED: test case {test.case_name} | TCL procedure {tcl.proc_name} | POE Class {tcl.poe_class}")
					break
					 
				# keyin = input("Please check poe inline output. Do you want to finish showing this command?(Y/N): ")
				# if keyin.upper() == "Y":
				# 	break
				
			if tcl.tcl_close == True:
				pshell.tcl_close_shell()
				new_power_shell = True
	pshell.tcl_close_shell()