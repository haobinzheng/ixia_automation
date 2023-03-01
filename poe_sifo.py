import wexpect

# Spawn a new process for the TCL shell
#tcl_shell = wexpect.spawn('/c/Program\\ Files\\ (x86)/Sifos/PSA3000/PowerShell\\ TCL.exe')
tcl_shell = wexpect.spawn('winpty ./powershell_tcl.exe')
tcl_shell.sendline('\n\n\n\n')
tcl_shell.sendline('puts "Hello, world!"')
# Wait for the TCL prompt to appear
tcl_shell.expect('>')

# Send a command to the TCL shell
tcl_shell.sendline('puts "Hello, world!"')
output = tcl_shell.before.decode()
print(output)
exit()
# Wait for the TCL prompt to appear again
tcl_shell.expect('%')

# Print the output from the TCL shell
print(tcl_shell.before.decode())

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
 