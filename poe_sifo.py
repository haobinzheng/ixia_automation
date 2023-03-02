import wexpect
from time import sleep
from protocols_class import *
from device_config import *


if __name__ == "__main__":
	# Spawn a new process for the TCL shell
	#tcl_shell = wexpect.spawn('/c/Program\\ Files\\ (x86)/Sifos/PSA3000/PowerShell\\ TCL.exe')
	# tcl_shell = wexpect.spawn('winpty ./powershell_tcl.exe')
	# tcl_shell.sendline('\n')
	# sleep(1)
	# tcl_shell.sendline('\n')
	# sleep(1)
	# tcl_shell.sendline('\n')
	# sleep(1)
	# tcl_shell.sendline('\n')
	# tcl_shell.sendline('puts "Hello, world!"')
	# # Wait for the TCL prompt to appear
	# tcl_shell.expect('>')
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

	pshell = power_shell_tcl()
	cmds = """
 	set port_list {"5,1" "6,1" "7,1" "8,1" "9,1" "10,1" "11,1" "12,1"}
	foreach port $port_list {
		puts "psa_disconnect $port"
		psa_disconnect $port
		puts "psa_4pair $port single"
		psa_4pair $port single
		puts "psa_auto_port $port BT"
		psa_auto_port $port BT
		puts "power_bt $port c 6 p 60  "
		power_bt $port c 6 p 60
	}
	"""
	pshell.tcl_send_commands(cmds,"psa_bt")
	sw = switches[0]
	while True:
		sw.print_show_command("get switch poe inline")
		output = input("Please check poe inline output. Do you want to finish showing this command?(Y/N): ")
		if output.upper() == "Y":
			break
	pshell.tcl_exit_shell()