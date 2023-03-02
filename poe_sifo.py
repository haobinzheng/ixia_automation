import wexpect
from time import sleep


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

	pshell = power_shell_tcl()
	cmds = """
 	set port_list {"7,1"}
	foreach port $port_list {
		puts "psa_disconnect $port"
		psa_disconnect $port
		puts "psa_4pair $port single"
		psa_4pair $port single
		puts "psa_auto_port $port BT"
		psa_auto_port $port BT
		puts "power_bt $port c 4 p 30  "
		power_bt $port c 4 p 30
	}
	"""
	pshell.tcl_send_commands(cmds,"psa_bt")
	exit()

	# Send a command to the TCL shell
	tcl_shell.sendline('puts "Hello, world!"')
	output = tcl_shell.before
	print(output)
	tcl_shell.sendline('psa_test_load 1,1 fast c 4 -force t 20')
	tcl_shell.expect('>')
	print(tcl_shell.before)
	output = input("psa_test_load 1,1 fast c 4 -force t 20, enter any key to continue:")
	tcl_shell.sendline('psa_disconnect 1,1')
	tcl_shell.expect('>')
	print(tcl_shell.before)
	output = input("psa_disconnect 1,1,enter any key to continue:")
	exit()
	# Wait for the TCL prompt to appear again
	tcl_shell.expect('%')

	# Print the output from the TCL shell
	print(tcl_shell.before)

	# Exit the TCL shell
	tcl_shell.sendline('exit')
	 

	# Spawn a new process for the TCL shell
	tcl_shell = pexpect.spawn('tclsh')

	# Wait for the TCL prompt to appear
	tcl_shell.expect('tcl>')

	# Send a command to the TCL shell and expect a response
	tcl_shell.sendline('puts "Hello, world!"')
	tcl_shell.expect('Hello, world!')

	# Send another command and expect a different response
	tcl_shell.sendline('set greeting "Hello, Python!"')
	tcl_shell.expect('tcl>')

	# Send a third command and capture the output
	tcl_shell.sendline('puts $greeting')
	tcl_shell.expect('Hello, Python!')

	# Exit the TCL shell
	tcl_shell.sendline('exit')
	 