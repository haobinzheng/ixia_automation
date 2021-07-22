import os
import time
# from console_util  import  *
from snmp_cmds import snmpwalk
import subprocess
import argparse
from utils import *


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

def shell_snmp_walk(ip):
	while True: 
		p = subprocess.Popen(f"snmpwalk -v1 -c public {ip}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		while True:
			line = p.stdout.readline()
			if not line:
				break
			print (f"snmpwalk: {line.rstrip()}")

		# p = subprocess.Popen("snmpwalk -v1 -c public 10.105.241.18", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		# while True:
		# 	line = p.stdout.readline()
		# 	if not line:
		# 		break
		# 	print (f"snmpwalk: {line.rstrip()}")
	 

	 

if __name__ == "__main__":
	#monitor_dut()
	#fsw_snmp_walk()
	parser = argparse.ArgumentParser()
	parser.add_argument("-c", "--config", help="Configure switches before starting testing", action="store_true")
	parser.add_argument("-test", "--testcase", type=str, help="Specific which test case you want to run. Example: 1/1-3/1,3,4,7 etc")
	parser.add_argument("-b", "--boot", help="Perform reboot test", action="store_true")
	parser.add_argument("-f", "--factory", help="Run the test after factory resetting all devices", action="store_true")
	parser.add_argument("-v", "--verbose", help="Run the test in verbose mode with amble debugs info", action="store_true")
	parser.add_argument("-s", "--setup_only", help="Setup testbed and IXIA only for manual testing", action="store_true")
	parser.add_argument("-i", "--interactive", help="Enter interactive mode for test parameters", action="store_true")
	parser.add_argument("-ug", "--sa_upgrade", type = str,help="FSW software upgrade in standlone mode. For debug image enter -1. Example: v6-193,v7-5,-1(debug image)")
	parser.add_argument("-p", "--ip", type=str,help="enter ip address")


	global DEBUG
	
	args = parser.parse_args()

	if args.sa_upgrade:
		upgrade_sa = True
		sw_build = args.sa_upgrade
		print_title(f"Upgrade FSW software in standalone: {sw_build}")
	else:
		upgrade_sa = False
	 
	if args.verbose:
		print_title("Running the test in verbose mode")
	else:
		print_title("Running the test in silent mode") 

	if args.config:
		setup = True
		print_title("Configure devices:Yes")
	else:
		setup = False   
		print_title("Configure devices:No")  
		 
	 
	if args.factory:
		factory = True
		print_title("Factory reset: Yes")
	else:
		factory = False
		print_title("Factory reset: No")

	if args.ip:
		ip_address = args.ip 
	else:
		print("Please provide ip address to the command")
		exit()
	


	shell_snmp_walk(ip_address)