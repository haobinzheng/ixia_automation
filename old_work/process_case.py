import os
import multiprocessing
import subprocess
from switch_class import *

def snmp_run():
		subprocess.call("snmpwalk -Os -c public -v 2c 10.33.42.125 > /dev/null &",shell = True)
		#os.system("snmpwalk -Os -c public -v 2c 10.33.42.125 &")

def proc_snmp():
	subprocess.call("snmpwalk -Os -c public -v 2c 10.33.42.119 > /dev/null &",shell = True)
	#os.system("snmpwalk -Os -c public -v 2c 10.33.42.125 &")

def proc_show():
	subprocess.call('python process_show.py ',shell = True)

def proc_show_noshell():
	subprocess.call('python solution_test.py > /dev/null ',shell = True)

def proc_show_commands(sw_dut):
	dut =cienaswitch(sw_dut) 
	collect_dut_vc(dut)
	ingress_tu = ingress_tunnel(dut)
	egress_tu = egress_tunnel(dut)
	egress_tu.build_tunnel_all()
	ingress_tu.build_tunnel_all()
	while True:
		print "test subprocess"
		ingress_tu.show_tunnel_all()
		egress_tu.show_tunnel_all()
		dut.vc_db.flush_mac_all_vc()
		dut.vc_db.show_all_vc()

	
