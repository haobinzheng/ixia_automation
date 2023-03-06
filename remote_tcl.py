import paramiko
from time import sleep
import pexpect
import sys


# Set the IP address or hostname of the remote Windows 10 machine
remote_ip = '10.105.252.23'

# Set the username and password to use for the SSH connection
username = 'Administrator'
password = 'Fortinet123!'

login = "ssh Administrator@10.105.252.23"
# # Create a SSH client object
# ssh_client = paramiko.SSHClient()

# # Automatically add the remote Windows 10 machine's SSH key to the local known_hosts file
# ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# # Connect to the remote Windows 10 machine using SSH
# ssh_client.connect(hostname=remote_ip, username=username, password=password)

# # Execute the TCL shell command on the remote Windows 10 machine
# stdin, stdout, stderr = ssh_client.exec_command('/Users/Administrator/testing/ixia_automation/powershell_tcl.exe\n')
# sleep(20)
# # Print the output of the TCL shell command
# print(stdout.read())

# # Close the SSH connection
# ssh_client.close()




ssh_cmd = f"ssh {username}@{remote_ip}"
ssh = pexpect.spawn(ssh_cmd)
ssh.logfile_read = sys.stdout.buffer
# wait for the SSH password prompt and enter the password
ssh.expect("password:")
ssh.sendline(password)

ssh.expect('>')
print(ssh.before)
ssh.send('/Users/Administrator/testing/ixia_automation/powershell_tcl.exe\r\n')
sleep(5)
ssh.send('\r\n')
sleep(10)
# wait for the tclsh prompt to appear
ssh.expect('>')
#print(ssh.before)
# ssh.send('dir\r\n')
# #ssh.expect("\r\n")
# ssh.expect('>')
# sleep(2)
# print(ssh.before)
# # create an SSH session to the remote Windows 10 machin
# # send the command to start a tclsh shell
# ssh.send('/Users/Administrator/testing/ixia_automation/powershell_tcl.exe\r\n')
# sleep(5)
# ssh.send('\r\n')
# sleep(10)
# # wait for the tclsh prompt to appear
# ssh.expect('>')
# print(ssh.before)

# interact with the tclsh shell
ssh.send('puts "hello world"')
ssh.expect('>')
print(ssh.before)

# exit the tclsh shell
ssh.send('exit\r\n')
#ssh.expect('>')

# close the SSH session
ssh.close()
