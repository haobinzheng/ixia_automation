import os
import time
# from console_util  import  *
from snmp_cmds import snmpwalk
import subprocess


def monitor_dut():
	host1 = "10.105.50.63"
	user = "admin"
	password = "admin"
	cmd = "diagnose sys top 1"
	sucess_count = 0
	fail_count = 0
	total = 10
	for i in range(total):
		result = ssh(host1,user,password,cmd) 
		print (result)
		if result[0] == "Success":
			sucess_count += 1
		else:
			fail_count += 1
	print("Success rate = {:.2%}".format(sucess_count/total))
	print("Failure rate = {:.2%}".format(fail_count/total))

def fsw_snmp_walk():
	host1 = "10.105.241.18"
	host2 = "10.105.241.116"
	res = snmpwalk(
 	ipaddress=host1,
 	oid='.1.3.6.1.2.1.1.4.0',
	community='public')
	print(res)

	res = snmpwalk(
 	ipaddress=host2,
 	oid="all",
	community='public')
	print(res)

def shell_snmp_walk():
	while True: 
		p = subprocess.Popen("snmpwalk -v1 -c public 10.105.241.116", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		while True:
			line = p.stdout.readline()
			if not line:
				break
			print (f"snmpwalk: {line.rstrip()}")

		p = subprocess.Popen("snmpwalk -v1 -c public 10.105.241.18", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		while True:
			line = p.stdout.readline()
			if not line:
				break
			print (f"snmpwalk: {line.rstrip()}")
	 

	 

if __name__ == "__main__":
	#monitor_dut()
	#fsw_snmp_walk()
	shell_snmp_walk()