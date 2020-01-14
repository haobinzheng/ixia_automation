import os
import multiprocessing
import subprocess

def snmp_run():
	subprocess.call("snmpwalk -Os -c public -v 2c 10.33.42.125 > /dev/null &",shell = True)
	#os.system("snmpwalk -Os -c public -v 2c 10.33.42.125 &")
