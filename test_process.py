import os
import time
from console_util  import  *

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

if __name__ == "__main__":
	monitor_dut()