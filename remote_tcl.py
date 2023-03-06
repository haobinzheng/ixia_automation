import paramiko

# Set the IP address or hostname of the remote Windows 10 machine
remote_ip = '10.105.252.23'

# Set the username and password to use for the SSH connection
username = 'Administrator'
password = 'Fortinet123!'

# Create a SSH client object
ssh_client = paramiko.SSHClient()

# Automatically add the remote Windows 10 machine's SSH key to the local known_hosts file
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Connect to the remote Windows 10 machine using SSH
ssh_client.connect(hostname=remote_ip, username=username, password=password)

# Execute the TCL shell command on the remote Windows 10 machine
stdin, stdout, stderr = ssh_client.exec_command('winpty /c/Users/Administrator/testing/ixia_automation/powershell_tcl.exe')

# Print the output of the TCL shell command
print(stdout.read())

# Close the SSH connection
ssh_client.close()
