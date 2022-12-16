import telnetlib
import sys
import time
import logging
import traceback
#import paramiko
import time
from time import sleep
import re
import os
from datetime import datetime
import xlsxwriter
from excel import *
#from ixia_ngfp_lib import *
import settings
from console_util  import  *
import pexpect
from threading import Thread
import subprocess
#import spur

DEBUG = False

def send_Message(stock_msg):
  #stock_msg = remove_bracket(stock_msg)
  cmd = """osascript send_imessage.applescript 4088967681 '{}' """.format(stock_msg)
  #print(new_cmd)
  os.system(cmd)
  return None
 
def ip_break_up(ip):
	matched = re.search(r'([0-9]+\.[0-9]+\.[0-9]+)\.([0-9]+)',ip)
	if matched:
	  net = matched.group(1)
	  host = matched.group(2)
	  return net,host
	return None, None


def list_add(proc_list_all,proc_list):
	for i in proc_list:
		proc_list_all.append(i)

def init_tracking_loop(loop_count):
	loop_count = 0

def tracking_loop(loop_count,mac_list):
	loop_count +=1
	if loop_count == len(mac_list):
		Tracking = "End"
	elif loop_count == len(mac_list) - 1:
		Tracking = "Penultimate"
	elif loop_count == 1:
		Tracking = "Start"
	else:
		Tracking = "Middle"
	return Tracking

def touch(fname):
    if os.path.exists(fname):
        os.utime(fname, None)
    else:
        open(fname, 'a').close()

def print_bytes(bytes):
	message = bytes.strip()
	lines = message.splitlines()
	for line in lines:
		print (line.decode('ascii'))

def scp_file(**kwargs):
	if "file" in kwargs:
		FILE = kwargs['file']
	else:
		FILE="MCLAG_Perf_448D_1.xlsx"
	if "server" in kwargs:
		HOST=kwargs['server']
	else:
		HOST="10.105.19.19"
	if "password" in kwargs:
		PASS=kwargs['password']
	else:
		PASS="Shenghuo2014+"
	if "user" in kwargs:
		USER=kwargs['user']
	else:
		USER="zhengh"
	REMOTE_FILE=""
	
	
	COMMAND="scp -oPubKeyAuthentication=no %s %s@%s:%s" % (FILE, USER, HOST, REMOTE_FILE)

	child = pexpect.spawn(COMMAND)
	child.expect('password:')
	child.sendline(PASS)
	child.expect(pexpect.EOF)
	print_bytes(child.before)

class Logger(object):
    def __init__(self, file):
        self.terminal = sys.stdout
        print(file)
        self.log = open(file, "w")

    def write(self, message):
        try:
            self.terminal.write(message)
            self.terminal.flush()
            self.log.write(message)
            self.log.flush()
        except UnicodeEncodeError as e:
            print("Error: UnicodeEncodeError")

    def flush(self):
        self.terminal.flush()

    def close(self):
        # self.terminal.close()
        self.log.close()

# def tprint(var):
#     print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+" :: "+str(var))



def parse_sys_top(result):
	high_lines = []
	high = False
	cpu_dict={}
	whole = ''
	busy_dict = {}
	for line in result:
		if "U" in line and "S" in line and "I" in line:
			debug("parse_sys_top:found cpu utils headline")
			items = re.split(';\\s+|,\\s+|\n',line)
			debug(f"(parse_sys_top: headline parsing: {items}")
			user = items[0]
			user = int((re.match('([0-9]+)(U)',user)).group(1))
			system = items[1]
			system = int((re.match('([0-9]+)(S)',system)).group(1))
			idle = items[2]
			idle = int(re.match('([0-9]+)(I)',idle).group(1))
			busy_dict['user'] = user
			busy_dict['system'] = system
			busy_dict['idle'] = idle
			whole = line
			debug(f'parse_sys_top: headline = {whole}')
			continue
			# print(user,system,idle)
		if line == '':
			continue
		line = line.strip()
		items = re.split('\\s+|,\\s+|\n',line)
		debug(items)
		if len(items) != 5 and len(items) !=6 :
			continue
		try:
			debug("parse_sys_top: items length = {}".format(len(items)))
			if len(items) == 5:
				obj = float(items[3])
				debug("parse_sys_top: items[3] = {}".format(obj))
			if len(items) == 6:
				obj = float(items[4])
				debug("parse_sys_top: items[4] = {}".format(obj))
			cpu_dict[items[0]] = {}
			cpu_dict[items[0]]['cpu'] = obj
			cpu_dict[items[0]]['line'] = line
			cpu_dict[items[0]]['headline'] = whole
			cpu_dict[items[0]]['headline_dict'] = busy_dict

			if obj > 30.0:
				high_lines.append(line)
				debug("parse_sys_top: cpu is high")
				high = True
		except Exception as e:
			tprint("parse_sys_top: line not parsable")
	debug (high_lines)
	debug (cpu_dict)
	return (high,high_lines,cpu_dict)

def print_cmd_output(msg,dut_name,cmd):
	# global DEBUG
	# print(DEBUG)
	tprint("========== Commnd output at {}: {}".format(dut_name,cmd))
	if type(msg) == list:
		for m in msg:
			tprint("{}: {}".format(dut_name,m))
	else:
		tprint("{}: {}".format(dut_name,msg))

def print_cmd_output_from_list(msgs):
	# global DEBUG
	# print(DEBUG)
	if type(msgs) == list:
		for m in msgs:
			tprint(f"{m}")
	else:
		tprint(f"{msgs}")

def print_file(msg, file,**kwargs):
	if "dut_name" in kwargs:
		dut_name = kwargs['dut_name']
	else:
		dut_name = "DUT"
	with open(file,'a+') as f:
		if type(msg) == list:
			for m in msg:
				f.write(time_str("{}:{}\n".format(dut_name,m)))
		else:
			f.write(time_str("{}:{}\n".format(dut_name,msg)))

def dprint(msg):
	# global DEBUG
	# print(DEBUG)
	if settings.DEBUG or DEBUG:
		if type(msg) == list:
			for m in msg:
				tprint("Debug: {}".format(m))
		else:
			tprint("Debug: {}".format(msg))

def print_output_list(msg):
	if type(msg) == list:
		for m in msg:
			tprint(f"{m}")
	else:
		tprint(f"Debug: {msg}")

def debug(msg):
	# global DEBUG
	#print(f"DEBUG Mode = {settings.DEBUG}")
	if settings.DEBUG:
		if type(msg) == list:
			for m in msg:
				tprint("Debug: {}".format(m))
		else:
			tprint("Debug: {}".format(msg))

def kwargs_args_example(*args, **kwargs):

	for num in args:
		z+= num 

	tkwargs = {}
	for k,v in kwargs.items():
		tkwargs[k] = v
		if k == "final":
			final = tkwargs[k]
			break
	z += final 
	return z

def time_str(mesg):
	return str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + " :: " + mesg

def tprint(*args, **kwargs):
    tempa = ' '.join(str(a) for a in args)
    tempk = ' '.join([str(kwargs[k]) for k in kwargs])
    temp = tempa + ' ' + tempk # puts a space between the two for clean output
    print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + " :: " + temp)

def Info(*args, **kwargs):
    if DEBUG != True:
	    return
    tempa = ' '.join(str(a) for a in args)
    tempk = ' '.join([str(kwargs[k]) for k in kwargs])
    temp = tempa + ' ' + tempk # puts a space between the two for clean output
    print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + " :: " + "Info: " + temp)
    print('\n')

def ErrorNotify(*args, **kwargs):
    tempa = ' '.join(str(a) for a in args)
    tempk = ' '.join([str(kwargs[k]) for k in kwargs])
    temp = tempa + ' ' + tempk # puts a space between the two for clean output
    print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + " :: " + "Error: " + temp)

def print_flow_stats_3rd_log(flow_list,file):
	with open(file,'a+') as f:
		f.write("-----------------------------------------------------------------\n")
		for flow in flow_list:
			f.write(time_str("Flow ID:{}\n".format(flow['id'])))
			f.write(time_str("TX_Port:{}\n".format(flow['tx_port'])))
			f.write(time_str("RX_Port:{}\n".format(flow['rx_port'])))
			f.write(time_str("TX packet rate:{}\n".format(flow['total_pkt_rate'])))
			f.write(time_str("Total_TX_pkts:{}\n".format(flow['total_tx_pkts'])))
			f.write(time_str("Total_RX_pkts:{}\n".format(flow['total_rx_pkts'])))
			f.write(time_str("Pkt Loss:{}\n".format(flow['loss_pkts'])))
			f.write(time_str("Pkt Loss Time:{}\n".format(flow["loss_time"])))
			f.write("-----------------------------------------------------------------\n")

def print_flow_stats_3rd(flow_list):
	print("----------------------------------------------")
	for flow in flow_list:
		tprint("Flow ID:{}".format(flow['id']))
		tprint("TX_Port:{}".format(flow['tx_port']))
		tprint("RX_Port:{}".format(flow['rx_port']))
		tprint("TX packet rate:{}".format(flow['total_pkt_rate']))
		tprint("Total_TX_pkts:{}".format(flow['total_tx_pkts']))
		tprint("Total_RX_pkts:{}".format(flow['total_rx_pkts']))
		tprint("Pkt Loss:{}".format(flow['loss_pkts']))
		tprint("Pkt Loss Time:{}".format(flow["loss_time"]))
		#tprint("Test Case: {}".format(flow['reason']))
		print("----------------------------------------------")

def print_flow_stats_new(flow_list):
	for flow in flow_list:
		tprint("Flow ID:{}, TX_Port:{}, RX_Port:{}, TX packet rate:{}, Total_TX_pkts:{},Total_RX_pkts:{},Pkt Loss:{}, \
			Pkt Loss time:{}, Test case: {}". \
			format(flow['id'],flow['tx_port'],flow['rx_port'],flow['total_pkt_rate'], \
				flow['total_tx_pkts'],flow['total_rx_pkts'],flow['loss_pkts'],flow["loss_time"],flow['reason']))
		tprint("--------------------------------")

def print_flow_stats(flow_list):
	for flow in flow_list:
		tprint("Flow ID:{}, TX_Port:{}, RX_Port:{}, TX packet rate:{}, Total_TX_pkts:{},Total_RX_pkts:{},Pkt Loss:{}, Pkt Loss time:{}". \
			format(flow['id'],flow['tx_port'],flow['rx_port'],flow['total_pkt_rate'], \
				flow['total_tx_pkts'],flow['total_rx_pkts'],flow['loss_pkts'],flow["loss_time"]))
		tprint("--------------------------------")

def test_flow_stats():
	traffic_stats = {'status': '1', 'measure_mode': 'mixed', 'waiting_for_stats': '0', 'flow': \
	{'2': {'rx': {'pkt_loss_duration': 'N/A', 'total_pkt_rate': '0.000', 'total_pkt_kbit_rate': '0.000', \
	'total_pkt_mbit_rate': '0.000', 'port': '1/1/1', 'total_pkt_byte_rate': '0.000', 'expected_pkts': 'N/A', \
	'last_tstamp': '00:00:32.459', 'misdirected_ports': 'N/A', 'reverse_error': 'N/A', 'total_pkt_bytes': \
	'3732279000', 'loss_percent': '4.191', 'min_delay': '40300', 'loss_pkts': '163250', 'total_pkts_bytes': \
	'3732279000', 'avg_delay': '41623', 'first_tstamp': '00:00:00.671', 'total_pkt_bit_rate': '0.000', \
	'l1_bit_rate': '0.000', 'total_pkts': '3732279', 'misdirected_rate': 'N/A', 'small_error': 'N/A', \
	'misdirected_pkts': 'N/A', 'big_error': 'N/A', 'max_delay': '45320'}, 'tx': {'total_pkt_rate': '0.000', \
	'total_pkt_kbit_rate': '0.000', 'total_pkt_mbit_rate': '0.000', 'total_pkt_byte_rate': '0.000', \
	'total_pkt_bit_rate': '0.000', 'total_pkts': '3895529', 'port': '1/1/2', 'l1_bit_rate': '0.000'}, \
	'pgid_value': 'N/A', 'tracking': {'2': {'tracking_value': '100.1.0.2-100.1.0.1', 'tracking_name': \
	'Source/Dest Endpoint Pair'}, '1': {'tracking_value': 'TI1-Traffic_Item_2', 'tracking_name': 'Traffic Item'}, \
	'count': '2'}, 'flow_name': '1/1/1 TI1-Traffic_Item_2 100.1.0.2-100.1.0.1'}, '1': {'tracking': \
	{'1': {'tracking_value': 'TI0-Traffic_Item_1', 'tracking_name': 'Traffic Item'}, '2': {'tracking_name': \
	'Source/Dest Endpoint Pair', 'tracking_value': '100.1.0.1-100.1.0.2'}, 'count': '2'}, \
	'flow_name': '1/1/2 TI0-Traffic_Item_1 100.1.0.1-100.1.0.2', 'rx': {'expected_pkts': 'N/A', 'port': '1/1/2', \
	'reverse_error': 'N/A', 'total_pkt_kbit_rate': '0.000', 'total_pkt_mbit_rate': '0.000', 'misdirected_rate': 'N/A', \
	'big_error': 'N/A', 'max_delay': '44060', 'misdirected_pkts': 'N/A', 'total_pkt_byte_rate': '0.000', 'loss_percent': \
	 '0.050', 'last_tstamp': '00:00:32.459', 'pkt_loss_duration': 'N/A', 'first_tstamp': '00:00:00.671', \
	 'misdirected_ports': 'N/A', 'l1_bit_rate': '0.000', 'loss_pkts': '1942', 'min_delay': '39840', \
	 'total_pkt_bit_rate': '0.000', 'avg_delay': '41276', 'total_pkt_rate': '0.000', 'small_error': 'N/A', \
	 'total_pkts_bytes': '3893587000', 'total_pkts': '3893587', 'total_pkt_bytes': '3893587000'}, 'tx':\
	 {'total_pkt_kbit_rate': '0.000', 'total_pkt_mbit_rate': '0.000', 'total_pkt_byte_rate': '0.000', 'port': '1/1/1', \
	 'total_pkt_bit_rate': '0.000', 'total_pkt_rate': '0.000', 'total_pkts': '3895529', 'l1_bit_rate': '0.000'}, \
	 'pgid_value': 'N/A'}}}
	for k, v in traffic_stats.items():
		if k == "flow":
			flow_stats = v
			break
	flow_num = list(flow_stats.keys())[0]

	 
	flow_stats_items = flow_stats[flow_num]
	#tprint(flow_stats_items)
	flow_list = []
	for k, v in flow_stats.items():
		flow_info = {}
		flow_info['id'] = k
		flow_info['rx'] = rx_stats = v['rx']
		flow_info['tx'] = tx_stats = v['tx']
		tprint(rx_stats)
		tprint(tx_stats)
		flow_info['rx_port'] = rx_stats['port']
		flow_info['total_pkts'] = int(rx_stats['total_pkts'])
		flow_info['total_pkts_bytes'] = int(rx_stats['total_pkts_bytes'])

		flow_info['loss_pkts'] = int(rx_stats['loss_pkts'])
		flow_info['max_delay'] = int(rx_stats['max_delay'])
		flow_info['total_pkt_rate'] =float(tx_stats['total_pkt_rate'])
		if flow_info['total_pkt_rate'] != 0:
			flow_info["loss_time"] = str(flow_info['loss_pkts']/flow_info['total_pkt_rate']) 
		else:
			flow_info["loss_time"] = "0"
		flow_info['tx_port'] = tx_stats['port']
		flow_list.append(flow_info)

	print_flow_stats(flow_list)
	 

def create_console_connection(ip_address, console_port, username, password,timeout):
        logging.debug('Function Start - create_console_connection')
        str1 = "IP Address="+str(ip_address)+" Username="+str(username)+" Password="+str(password)+" "
        str1 = str1 + " Console Port Number="+str(console_port)+" "
        logging.debug(str1)
        timeout = 10
        try:
                tn1 = telnetlib.Telnet(ip_address,console_port,timeout)
                sleep_time_function(2)
                tn1.write('\x03')
                sleep_time_function(2)
                #tn1.write('\x03')
                #sleep_time_function(2)
                #tn1.write('\x03')
                #sleep_time_function(5)
                tn1.read_until("login: ",timeout)
                tn1.write(username + "\r\n")
                tn1.read_until("Password: ",timeout)
                tn1.write("\r\n")
                tn1.read_until("# ",timeout)
                tn1.write("get system status\r\n")
                output = tn1.read_until("# ",timeout)
                tprint(output)
                return tn1
        except Exception as e:
                logging.debug(e)

def threads_exit(stop_threads,threads_list):
	# stop_threads = True
	for t in threads_list:
		t.join()

def convert_cmd_ascii(cmd):
	return cmd.encode('ascii')

def convert_cmd_ascii_n(cmd):
	cmd = cmd + '\n'
	return cmd.encode('ascii')

def relogin_dut_all(dut_list):
	for dut in dut_list:
		relogin_if_needed(dut)

	config_admin_timeout(dut_list)

def relogin_after_reboot(dut):
	time.sleep(200)
	relogin_if_needed(dut)

def switch_exec_reboot(dut,**kwargs):
	if "device" in kwargs:
		dev_name = kwargs['device']
	else:
		dev_name = "DUT"

	tprint("-------- Rebooting device : {}".format(dev_name))
	switch_interactive_exec(dut,"exec reboot","Do you want to continue? (y/n)")
	# thread = Thread(target = relogin_after_reboot,args = (dut,))
	# thread.start()
	return

def switch_flap_port(tn, port):
	switch_shut_port(tn,port)
	sleep(3)
	switch_unshut_port(tn,port)

def switch_shut_port(tn,port):

	config = f"""
		config switch physical
		edit {port}
		set status down
		end
		"""
	config_cmds_lines(tn,config)

	# switch_configure_cmd(tn,"config switch physical")
	# switch_configure_cmd(tn,"edit {}".format(port))
	# switch_configure_cmd(tn,"set status down")
	# switch_configure_cmd(tn,"end")

def switch_unshut_port(tn,port):
	config = f"""
		config switch physical
		edit {port}
		set status up
		end
		"""
	config_cmds_lines(tn,config)
	# switch_configure_cmd(tn,"config switch physical")
	# switch_configure_cmd(tn,"edit {}".format(port))
	# switch_configure_cmd(tn,"set status up")
	# switch_configure_cmd(tn,"end")

def switch_system_interface_shut(tn,port):
	fgt_shut_port(tn,port)

def switch_system_interface_unshut(tn,port):
	fgt_unshut_port(tn,port)

def fgt_shut_port(tn,port):
	switch_configure_cmd(tn,"config vdom")
	switch_configure_cmd(tn,"edit root")
	switch_configure_cmd(tn,"config system interface")
	switch_configure_cmd(tn,"edit {}".format(port))
	switch_configure_cmd(tn,"set status down")
	switch_configure_cmd(tn,"end")

def fgt_unshut_port(tn,port):
	switch_configure_cmd(tn,"config vdom")
	switch_configure_cmd(tn,"edit root")
	switch_configure_cmd(tn,"config system interface")
	switch_configure_cmd(tn,"edit {}".format(port))
	switch_configure_cmd(tn,"set status up")
	switch_configure_cmd(tn,"end")

def send_ctrl_c_cmd(tn):
	tn.write(('\x03').encode('ascii'))

def collect_edit_question_cmd(tn,cmd,**kwargs):
	if 't' in kwargs:
		timeout = kwargs['t']
	else:
		timeout = 3
	#relogin_if_needed(tn)
	cmd = convert_cmd_ascii(cmd)
	tn.write(cmd)
	tn.write(('' + '\n').encode('ascii'))
	tn.write(('' + '\n').encode('ascii'))
	sleep(timeout)
	output = tn.read_very_eager()
	#output = tn.read_until(("# ").encode('ascii'))
	out_list = output.split(b'\r\n')
	encoding = 'utf-8'
	out_str_list = []
	for o in out_list:
		o_str = o.decode(encoding).rstrip(' ')
		out_str_list.append(o_str)
	# tprint(dir(output))
	# tprint(type(output))
	#tprint(out_list)
	# for i in out_str_list:
	# 	tprint(i)
	return out_str_list

def clean_show_output(out_str_list,cmd):
	i = 0
	i_list = []
	for o in out_str_list:
		if str(cmd) in str(o):
			i_list.append(i)
		i += 1
	index = i_list[-1]
	good_out_list = out_str_list[index:]
	debug(good_out_list)
	return good_out_list

def clean_show_output_recursive_general(out_str_list,cmd_list):
	for cmd in cmd_list:
		for o in out_str_list:
			if str(cmd) in str(o):
				return out_str_list
			else:
				out_str_list.pop(0)
				return clean_show_output_recursive(out_str_list,cmd)

def clean_show_output_recursive(out_str_list,cmd):
	for o in out_str_list:
		if str(cmd) in str(o):
			return out_str_list
		else:
			out_str_list.pop(0)
			return clean_show_output_recursive(out_str_list,cmd)

def read_console(tn):
	sleep(5)
	output = tn.read_very_eager()
	print(output)
	out_list = output.split(b'\r\n')
	encoding = 'utf-8'
	out_str_list = []
	for o in out_list:
		o_str = o.decode(encoding).strip(' \r')
		out_str_list.append(o_str)
		 
	print(out_str_list)
	return out_str_list

def print_show_cmd_list_generic(tn,cmd_f_string,*args,**kwargs):
	if 't' in kwargs:
		timeout = kwargs['t']
	else:
		timeout = 5
	#relogin_if_needed(tn)
	if "logger" in kwargs:
		mylogger = kwargs["logger"]
	else:
		mylogger = None
	handle_prompt_before_commands(tn)
	original_cmds = cmd_f_string
	cmd_list = split_fstring_lines_generic(cmd_f_string)	
	for cmd in cmd_list:
		cmd_bytes = convert_cmd_ascii_n(cmd)
		tn.write(cmd_bytes)
	sleep(timeout)
	output = tn.read_very_eager()
	out_list = output.split(b'\r\n')
	encoding = 'utf-8'
	out_str_list = []
	for o in out_list:
		o_str = o.decode(encoding).strip(' \r')
		out_str_list.append(o_str)
	for out_str in out_str_list:
		tprint(f"{str(out_str)}\n")
		if mylogger != None:
			mylogger.write(f"{str(out_str)}\n")

def print_show_cmd(tn,cmd,*args,**kwargs):
	if 't' in kwargs:
		timeout = kwargs['t']
	else:
		timeout = 5
	#relogin_if_needed(tn)
	if "logger" in kwargs:
		mylogger = kwargs["logger"]
	else:
		mylogger = None
	if "mode" in kwargs:
		mode = kwargs["mode"]
	else:
		mode = "slow"
	Info(f"print_show_cmd: mode = {mode}")
	if mode == "slow":
		handle_prompt_before_commands(tn)
	original_cmd = cmd
	cmd_bytes = convert_cmd_ascii_n(cmd)
	tn.write(('' + '\n').encode('ascii')) # uncomment this line if doesn't work
	tn.write(('' + '\n').encode('ascii')) # uncomment this line if doesn't work
	tn.write(cmd_bytes)
	tn.write(('' + '\n').encode('ascii')) # uncomment this line if doesn't work
	tn.write(('' + '\n').encode('ascii')) # uncomment this line if doesn't work
	sleep(timeout)
	output = tn.read_very_eager()
	out_list = output.split(b'\r\n')
	encoding = 'utf-8'
	out_str_list = []
	for o in out_list:
		o_str = o.decode(encoding).strip(' \r')
		out_str_list.append(o_str)
	for out_str in out_str_list:
		tprint(f"{str(out_str)}\n")
		if mylogger != None:
			mylogger.write(f"{str(out_str)}\n")

def collect_show_cmd_general(tn,*args,**kwargs):
	if 't' in kwargs:
		timeout = kwargs['t']
	else:
		timeout = 5
	#relogin_if_needed(tn)
	origal_cmd_list = args
	handle_prompt_before_commands(tn)
	for cmd in args:
		original_cmd = cmd
		cmd_bytes = convert_cmd_ascii_n(cmd)
		tn.write(('' + '\n').encode('ascii')) # uncomment this line if doesn't work
		tn.write(('' + '\n').encode('ascii')) # uncomment this line if doesn't work
		tn.write(cmd_bytes)
		tn.write(('' + '\n').encode('ascii')) # uncomment this line if doesn't work
		tn.write(('' + '\n').encode('ascii')) # uncomment this line if doesn't work
		sleep(timeout)
	output = tn.read_very_eager()
	#print(output)
	#output = tn.read_until(("# ").encode('ascii'))
	out_list = output.split(b'\r\n')
	encoding = 'utf-8'
	out_str_list = []
	for o in out_list:
		o_str = o.decode(encoding).strip(' \r')
		out_str_list.append(o_str)
	good_out_list = clean_show_output_recursive_general(out_str_list,origal_cmd_list)
	debug(good_out_list)
	print_output_list(good_out_list)
	return good_out_list

def collect_show_cmd(tn,cmd,**kwargs):
	if 't' in kwargs:
		timeout = kwargs['t']
	else:
		timeout = 5
	if 'mode' in kwargs:
		mode = kwargs['mode']
	else:
		mode = "slow"
	if "ssh" in kwargs:
		ssh = kwargs['ssh']
		return ssh.cmd_proc(cmd)

	Info(f"At collect_show_cmd: mode = {mode}")
	#relogin_if_needed(tn)
	if mode == "slow":
		handle_prompt_before_commands(tn)
	original_cmd = cmd
	cmd_bytes = convert_cmd_ascii_n(cmd)
	tn.write(('' + '\n').encode('ascii')) # uncomment this line if doesn't work
	tn.write(('' + '\n').encode('ascii')) # uncomment this line if doesn't work
	tn.write(cmd_bytes)
	tn.write(('' + '\n').encode('ascii')) # uncomment this line if doesn't work
	tn.write(('' + '\n').encode('ascii')) # uncomment this line if doesn't work
	sleep(timeout)
	output = tn.read_very_eager()
	#print(output)
	#output = tn.read_until(("# ").encode('ascii'))
	out_list = output.split(b'\r\n')
	encoding = 'utf-8'
	out_str_list = []
	for o in out_list:
		o_str = o.decode(encoding).strip(' \r')
		out_str_list.append(o_str)
	# tprint(dir(output))
	# tprint(type(output))
	#tprint(out_list)
	# for i in out_str_list:
	# 	tprint(i)
	#Will revove these lines after bgp is done
	if cmd == "get router info6 bgp summary":
		print (f"return from utiliy.py: collect_show_cmd(): {out_str_list}")
	# i = 0
	# i_list = []
	# for o in out_str_list:
	# 	if str(original_cmd) in str(o):
	# 		i_list.append(i)
	# 	i += 1
	# index = i_list[-1]
	# good_out_list = out_str_list[index:]
	good_out_list = clean_show_output_recursive(out_str_list,original_cmd)
	debug(good_out_list)
	print_output_list(good_out_list)
	return good_out_list

def show_execute_cmd(tn,cmd,**kwargs):
	if 't' in kwargs:
		timeout = kwargs['t']
	else:
		timeout = 8
	#relogin_if_needed(tn)
	original_cmd = cmd
	cmd_bytes = convert_cmd_ascii_n(cmd)
	tn.write(cmd_bytes)
	tn.write(('' + '\n').encode('ascii')) # uncomment this line if doesn't work
	tn.write(('' + '\n').encode('ascii')) # uncomment this line if doesn't work
	sleep(timeout)
	output = tn.read_very_eager()
	debug(output)
	#output = tn.read_until(("# ").encode('ascii'))
	out_list = output.split(b'\r\n')
	encoding = 'utf-8'
	out_str_list = []
	for o in out_list:
		o_str = o.decode(encoding).strip(' \r')
		out_str_list.append(o_str)
	 
	if cmd == "get router info6 bgp summary":
		print (f"return from utiliy.py: collect_show_cmd(): {out_str_list}")

	good_out_list = clean_show_output_recursive(out_str_list,original_cmd)
	print_cmd_output_from_list(good_out_list)
	debug(good_out_list)

def collect_long_execute_cmd(tn,cmd,**kwargs):
	if 't' in kwargs:
		timeout = kwargs['t']
	else:
		timeout = 8
	if "prompt" in kwargs:
		prompt = kwargs['prompt']
	else:
		prompt = "# "
	#relogin_if_needed(tn)
	original_cmd = cmd
	cmd_bytes = convert_cmd_ascii_n(cmd)
	tn.write(cmd_bytes)
	output = switch_read_console_output(tn,timeout = timeout,prompt = prompt)
	good_out_list = clean_show_output_recursive(output,original_cmd)
	print(good_out_list)
	return good_out_list

def ftg_collect_execute_cmd(tn,cmd,**kwargs):
	if 't' in kwargs:
		timeout = kwargs['t']
	else:
		timeout = 8
	#relogin_if_needed(tn)
	original_cmd = cmd
	cmd_bytes = convert_cmd_ascii_n(cmd)
	tn.write(cmd_bytes)
	tn.write(('' + '\n').encode('ascii')) # uncomment this line if doesn't work
	tn.write(('' + '\n').encode('ascii')) # uncomment this line if doesn't work
	sleep(timeout)
	output = tn.read_very_eager()
	dprint(output)
	#output = tn.read_until(("# ").encode('ascii'))
	out_list = output.split(b'\r\n')
	encoding = 'utf-8'
	out_str_list = []
	for o in out_list:
		o_str = o.decode(encoding).strip(' \r')
		out_str_list.append(o_str)
	
	dprint(out_str_list)
	return out_str_list

def collect_execute_cmd(tn,cmd,**kwargs):
	if 't' in kwargs:
		timeout = kwargs['t']
	else:
		timeout = 8
	#relogin_if_needed(tn)
	original_cmd = cmd
	cmd_bytes = convert_cmd_ascii_n(cmd)
	tn.write(cmd_bytes)
	tn.write(('' + '\n').encode('ascii')) # uncomment this line if doesn't work
	tn.write(('' + '\n').encode('ascii')) # uncomment this line if doesn't work
	sleep(timeout)
	output = tn.read_very_eager()
	dprint(output)
	#output = tn.read_until(("# ").encode('ascii'))
	out_list = output.split(b'\r\n')
	encoding = 'utf-8'
	out_str_list = []
	for o in out_list:
		o_str = o.decode(encoding).strip(' \r')
		out_str_list.append(o_str)
	 
	if cmd == "get router info6 bgp summary":
		print (f"return from utiliy.py: collect_show_cmd(): {out_str_list}")

	good_out_list = clean_show_output_recursive(out_str_list,original_cmd)
	dprint(good_out_list)
	return good_out_list

def process_show_command(output):
	out_list = output.split('\r\n')
	encoding = 'utf-8'
	out_str_list = []
	for o in out_list:
		o_str = o.decode(encoding).rstrip(' ')
		out_str_list.append(o_str)
	if cmd == "get router info6 bgp summary":
		print (f"return from utiliy.py: collect_show_cmd(): {out_str_list}")
	return out_str_list

def append_file_collect_show(filename,result):
	singleline = "-------------------------------------------------------------------------------------\n"
	with open(filename,'a+') as f:
		f.write(singleline)
		for line in result:
			f.write(time_str(f'{line}\n'))
			 

def collect_show_cmd_fast(tn,cmd,**kwargs):
	if 't' in kwargs:
		timeout = kwargs['t']
	else:
		timeout = 2
	#relogin_if_needed(tn)
	cmd = convert_cmd_ascii_n(cmd)
	tn.write(cmd)
	tn.write(('' + '\n').encode('ascii'))
	tn.write(('' + '\n').encode('ascii'))
	sleep(1)
	output = tn.read_very_eager()
	#output = tn.read_until(("# ").encode('ascii'))
	out_list = output.split(b'\r\n')
	encoding = 'utf-8'
	out_str_list = []
	for o in out_list:
		o_str = o.decode(encoding).rstrip(' ')
		out_str_list.append(o_str)
	# tprint(dir(output))
	# tprint(type(output))
	#tprint(out_list)
	# for i in out_str_list:
	# 	tprint(i)
	i = 0
	for o in out_str_list:
		if cmd in o:
			break
		out_str_list.remove(o)
	return out_str_list

def get_mac_table_size(dut):
	cmd = "diagnose switch mac-address list | grep MAC | wc -c"
	result = switch_show_cmd(dut,cmd,t=3)
	debug(result)
	r = ''
	for r in result:
		if "CLI" in r:
			break
	debug(f'r = {r}')
	if r=='':
		tprint("Error getting switch MAC table size")
		return 0
	try:
		s = r.split(":")
		size = int(s[1])
	except Exception as e:
		tprint("Error getting switch MAC table size")
		return 0
	return size

def switch_exec_cmd(tn,cmd,**kwargs):
	#relogin_if_needed(tn)
	if 't' in kwargs:
		wait = kwargs['t']
	else:
		wait = 10
	tprint(f"Executing command: {cmd}")
	cmd = convert_cmd_ascii_n(cmd)
	tn.write(cmd)
	tn.read_until(("# ").encode('ascii'),timeout=wait)
	

def switch_run_cmd(tn,cmd,**kwargs):
	#relogin_if_needed(tn)
	if 't' in kwargs:
		timeout = kwargs['t']
	else:
		timeout = 0
	cmd = convert_cmd_ascii_n(cmd)
	tn.write(cmd)
	sleep(timeout)
	 
def switch_show_cmd_name(dut_dir,cmd,**kwargs):
	#relogin_if_needed(tn)
	if 't' in kwargs:
		timeout = kwargs['t']
	else:
		timeout = 2
	tn = dut_dir['telnet']
	name = dut_dir['name']
	old_cmd = cmd
	cmd = convert_cmd_ascii_n(cmd)
	tn.write(cmd)
	sleep(timeout)
	output = tn.read_very_eager()
	#output = tn.read_until(("# ").encode('ascii'))
	out_list = output.split(b'\r\n')
	debug(f"out_list in switch_show_cmd = {out_list}")
	encoding = 'utf-8'
	out_str_list = []
	for o in out_list:
		try:
			o_str = o.decode(encoding).rstrip(' ')
			out_str_list.append(o_str)
		except Exception as e:
			pass
	# tprint(dir(output))
	# tprint(type(output))
	#tprint(out_list)
	tprint(f"----------------{name}: {old_cmd} ---------------")
	for i in out_str_list:
		tprint(i)
	return out_str_list

def print_collect_show(output):
	for i in output:
		tprint(i)

def switch_show_cmd_linux(tn,cmd,**kwargs):
	#relogin_if_needed(tn)
	if 't' in kwargs:
		timeout = kwargs['t']
	else:
		timeout = 2
	cmd = convert_cmd_ascii_n(cmd)
	tn.write(cmd)
	tn.write(('' + '\n').encode('ascii'))
	# tn.write(('' + '\n').encode('ascii'))
	# tn.write(('' + '\n').encode('ascii'))
	# tn.write(('' + '\n').encode('ascii'))
	sleep(timeout)
	output = tn.read_very_eager()
	#output = tn.read_until(("# ").encode('ascii'))
	out_list = output.split(b'\r\n')
	debug(f"out_list in switch_show_cmd = {out_list}")
	encoding = 'utf-8'
	out_str_list = []
	for o in out_list:
		try:
			o_str = o.decode(encoding).rstrip(' ')
			out_str_list.append(o_str)
		except Exception as e:
			pass
	tn.write(('' + '\n').encode('ascii'))
	tn.write(('' + '\n').encode('ascii'))
	# tprint(dir(output))
	# tprint(type(output))
	#tprint(out_list)
	for i in out_str_list:
		tprint(i)
	return out_str_list

def increment_mac_address(*args,**kwargs):
	start_mac = kwargs['start_mac']
	num = kwargs['num']

	#mac="0xaabbccdd0000"
	mac = "0x"+start_mac.replace(":","")
	mac_addresses = []
	for i in range(num):
	    mac = "{:012X}".format(int(mac, 16) + 1)
	    new_mac = (':'.join(mac[i]+mac[i+1] for i in range(0, len(mac), 2)))
	    mac_addresses.append(new_mac)
	print(mac_addresses)
	return mac_addresses


def switch_show_cmd(tn,cmd,**kwargs):
	#relogin_if_needed(tn)
	if 't' in kwargs:
		timeout = kwargs['t']
	else:
		timeout = 2
	cmd = convert_cmd_ascii_n(cmd)
	tn.write(cmd)
	tn.write(('' + '\n').encode('ascii'))
	tn.write(('' + '\n').encode('ascii'))
	tn.write(('' + '\n').encode('ascii'))
	tn.write(('' + '\n').encode('ascii'))
	sleep(timeout)
	output = tn.read_very_eager()
	#output = tn.read_until(("# ").encode('ascii'))
	out_list = output.split(b'\r\n')
	debug(f"out_list in switch_show_cmd = {out_list}")
	encoding = 'utf-8'
	out_str_list = []
	for o in out_list:
		try:
			o_str = o.decode(encoding).rstrip(' ')
			out_str_list.append(o_str)
		except Exception as e:
			pass
	tn.write(('' + '\n').encode('ascii'))
	tn.write(('' + '\n').encode('ascii'))
	#tprint(dir(output))
	# tprint(type(output))
	#tprint(out_list)
	for i in out_str_list:
		tprint(i)
	return out_str_list
###############################################################################
#   config_keys =  "configure switch interface \
#						|  edit port1 \
#						|  set status up \
#						|  end \
#				"
###############################################################################

def ist_add(proc_list_all,proc_list):

	for i in proc_list1:
		proc_list_all.append(i)


def configure_switch_file(dut,config_file):
	tprint("*****************Configure device on comserver = {},port={}".format(dut.host,dut.port))
	switch_show_cmd(dut,"get system status")
	with open(config_file, 'r') as fin:
	 	lines = fin.readlines()
	 	for cmd in lines:
	 		switch_configure_cmd(dut,cmd)

def configure_switch_batch(dut,config_keys):
	 cmds = config_keys.split('|')
	 for cmd in cmds:
	 	switch_configure_cmd(dut,"config switch trunk")

def press_any_key():
	print_dash_line()
	keyin = input(f"Press any key to continue...")

def config_cmds_lines_cisco(dut, cmdblock):
	b= cmdblock.split("\n")
	b = [x.strip() for x in b if x.strip()]
	for cmd in b:
		switch_configure_cmd_cisco(dut,cmd)

def split_f_string_lines(cmdblock):
	b= cmdblock.split("\n")
	b = [x.strip() for x in b if x.strip()]
	return b

def split_fstring_lines_generic(cmdblock):
	cmds= cmdblock.split("\n")
	print(cmds)
	while cmds and cmds[-1] is '':
	    cmds.pop()
	while cmds and cmds[0] is '':
	    cmds.pop(0)
	return cmds


def config_cmds_lines_fast(dut,cmdblock,*args,**kwargs):
	if "wait" in kwargs:
		wait_time = int(kwargs["wait"])
	else:
		wait_time = 0.2

	if "feedback" in kwargs:
		feedback = kwargs['feedback']
	else:
		feedback = False

	if "check_prompt" in kwargs:
		check_prompt = kwargs["check_prompt"]
	else:
		check_prompt = False

	b= cmdblock.split("\n")
	b = [x.strip() for x in b if x.strip()]
	config_return_list = []
	for cmd in b:
		config_return = switch_configure_cmd(dut,cmd,output=feedback,mode="fast")
		if config_return != None:
			config_return_list.append(config_return)
		sleep(wait_time)
	return config_return_list

def config_cmds_lines(dut,cmdblock,*args,**kwargs):
	
	if "wait" in kwargs:
		wait_time = int(kwargs["wait"])
	else:
		wait_time = 0.2

	if "feedback" in kwargs:
		feedback = kwargs['feedback']
	else:
		feedback = False

	if "check_prompt" in kwargs:
		check_prompt = kwargs["check_prompt"]
	else:
		check_prompt = False


	if "mode" in kwargs:
		config_mode = kwargs["mode"]
	elif "device" in kwargs:
		device= kwargs['device']
		current_time = time.time()
		if device.last_cmd_time == None:
			config_mode = "fast"
		elif (current_time - device.last_cmd_time) < 100:
			config_mode = "fast"
		else:
			config_mode = "slow"
		device.last_cmd_time = current_time
	else:
		config_mode = "slow"

	if config_mode == "fast":
		wait_time = 0.5
		check_prompt = False
	else:
		check_prompt = True

	if check_prompt:
		handle_prompt_before_commands(dut)

	b= cmdblock.split("\n")
	b = [x.strip() for x in b if x.strip()]
	config_return_list = []
	for cmd in b:
		config_return = switch_configure_cmd(dut,cmd,mode=config_mode,output=feedback)
		if config_return != None:
			config_return_list.append(config_return)

		sleep(wait_time)
	return config_return_list
		 
def print_attributes(fgt):
	attrs = vars(fgt)
	print(attrs)
	print_dict_simple(attrs)

def print_dict_simple(attrs):
	for k,v in attrs.items():
		print(f"{k}:{v}")

def config_block_cmds_new(dut, cmdblock):
	b= cmdblock.split("\n")
	b = [x.strip() for x in b if x.strip()]
	for cmd in b:
		switch_configure_cmd(dut,cmd)

def print_title(msg):
	print(f"================================ {msg} ===============================")

def config_block_cmds(dut_dir, cmdblock):
	b= cmdblock.split("\n")
	b = [x.strip() for x in b if x.strip()]
	for cmd in b:
		switch_configure_cmd_name(dut_dir,cmd)

def config_switch_port_cmd(dut,port,cmd):
		switch_configure_cmd(dut,"config switch interface")
		switch_configure_cmd(dut,"edit {}".format(port))
		switch_configure_cmd(dut,cmd)
		switch_configure_cmd(dut,"end")

def config_system_interface(dut,port,cmd):
		switch_configure_cmd(dut,"config system interface")
		switch_configure_cmd(dut,"edit {}".format(port))
		switch_configure_cmd(dut,cmd)
		switch_configure_cmd(dut,"end")

def switch_configure_cmd_name(dut_dir,cmd):
	tn = dut_dir['telnet']
	dut_name = dut_dir['name']
	# swn9k-1: config t 2 :: configuring
	# swn9k-1: line con 2 :: configuring
	# swn9k-1(config): exec-timeout 300
	# swn9k-1(config-console): end uring
	tprint(f"configuring {dut_name}: {cmd}")
	cmd = convert_cmd_ascii_n(cmd)
	tn.write(cmd)
	time.sleep(0.5)
	tn.read_until(("# ").encode('ascii'),timeout=10)

def switch_read_console_output(tn,**kwargs):
	if "timeout" in kwargs:
		t = kwargs['timeout']
	else:
		t = 10
	if "prompt" in kwargs:
		prompt = kwargs['prompt']
	else:
		prompt = "# "
	output = tn.read_until((prompt).encode('ascii'),timeout=t)
	out_list = output.split(b'\r\n')
	encoding = 'utf-8'
	out_str_list = []
	for o in out_list:
		o_str = o.decode(encoding).rstrip(' ')
		out_str_list.append(o_str)
	# tprint(dir(output))
	# tprint(type(output))
	# tprint(out_list)
	for i in out_str_list:
		tprint(i)
	return out_str_list

# def switch_config_cmd_dutinfo(original_func):
# 	def wrapper(*args,**kwargs):


def switch_configure_cmd(tn,cmd,**kwargs):
	if 'mode' in kwargs:
		mode = kwargs['mode']
	else:
		mode = None
	if 'output' in kwargs:
		output = kwargs["output"]
	else:
		output = False

	if mode == "fast":
		tprint(f"configuring {cmd}")
	else:
		dut_prompt = find_dut_prompt(tn)
		tprint("configuring {}: {}".format(dut_prompt,cmd))

	cmd = convert_cmd_ascii_n(cmd)
	tn.write(cmd)
	time.sleep(0.6)
	if output == False:
		tn.read_until(("# ").encode('ascii'),timeout=5)
		return None 
	else: 
		#sleep(0.2)
		config_output = tn.read_very_eager()
		out_list = config_output.split(b'\r\n')
		encoding = 'utf-8'
		out_str_list = []
		for o in out_list:
			o_str = o.decode(encoding).strip(' \r')
			out_str_list.append(o_str)
		 
		for n in out_str_list:
			print (f"{n}")
		return out_str_list


def telnet_send_cmd(tn,cmd,*args,**kwargs):
	cmd = convert_cmd_ascii_n(cmd) #convert_cmd_ascii_n has appended return at the end
	tn.write(('' + '\n').encode('ascii'))
	tn.write(('' + '\n').encode('ascii'))
	tn.read_until((">").encode('ascii'),timeout=2)
	tn.write(cmd)
	time.sleep(2)
	tn.read_until((">").encode('ascii'),timeout=2)
	#tn.expect(["#", ">","> ",">  ",">	"])

def switch_configure_cmd_cisco(tn,cmd,**kwargs):
	if 'mode' in kwargs:
		mode = kwargs['mode']
	else:
		mode = None

	if mode == "silent":
		pass
	else:
		dut_prompt = find_dut_prompt_cisco(tn)
	# swn9k-1: config t 2 :: configuring
	# swn9k-1: line con 2 :: configuring
	# swn9k-1(config): exec-timeout 300
	# swn9k-1(config-console): end uring
		tprint("configuring {}: {}".format(dut_prompt,cmd))
	cmd = convert_cmd_ascii_n(cmd)
	tn.write(cmd)
	time.sleep(0.2)
	tn.read_until(("# ").encode('ascii'),timeout=10)

def switch_wait_enter_yes(tn,prompt):
	prompt = convert_cmd_ascii(prompt)
	#prompt_re = (prompt + r'.*').encode('ascii')
	tn.read_until(prompt,timeout=30)
	time.sleep(1)

	answer = convert_cmd_ascii('y' )
	tn.write(answer)
	time.sleep(1)
	 
def switch_enter_yes(tn):
	# prompt = convert_cmd_ascii(prompt)
	# #prompt_re = (prompt + r'.*').encode('ascii')
	# tn.read_until(prompt,timeout=60)
	# time.sleep(1)

	answer = convert_cmd_ascii('y')
	tn.write(answer)
	time.sleep(2)

def switch_interactive_exec_bios(tn,exec_cmd,prompt):
	#relogin_if_needed(tn)
	tprint(exec_cmd)
	exec_cmd = exec_cmd
	exec_cmd = convert_cmd_ascii(exec_cmd)
	tn.write(exec_cmd)
	time.sleep(1)

	answer = convert_cmd_ascii('y')
	#answer = convert_cmd_ascii('y' + '\n')
	tn.write(answer)
	time.sleep(1)

def switch_interactive_exec(tn,exec_cmd,prompt):
	#relogin_if_needed(tn)
	tprint(exec_cmd)
	exec_cmd = exec_cmd + '\n'
	exec_cmd = convert_cmd_ascii(exec_cmd)
	tn.write(exec_cmd)
	time.sleep(1)

	prompt = convert_cmd_ascii(prompt)
	#prompt_re = (prompt + r'.*').encode('ascii')
	tn.read_until(prompt,timeout=10)
	time.sleep(1)

	answer = convert_cmd_ascii('y')
	#answer = convert_cmd_ascii('y' + '\n')
	tn.write(answer)
	tn.write(('' + '\n').encode('ascii'))
	tn.write(('' + '\n').encode('ascii'))
	tn.write(('' + '\n').encode('ascii'))
	tn.write(('' + '\n').encode('ascii'))
	time.sleep(1)

def switch_login(tn,*args,**kwargs):
	if 'mode' in kwargs:
		login_mode = kwargs['mode']
	else:
		login_mode = None

	tn.write(('\x03').encode('ascii'))
	time.sleep(0.5)
	#tprint("successful login\n")
	tn.write(('\x03').encode('ascii'))
	time.sleep(0.5)
	tn.write(('\x03').encode('ascii'))
	time.sleep(0.5)	

	tn.write(('' + '\n').encode('ascii'))
	#time.sleep(2)
	tn.write(('' + '\n').encode('ascii'))
	#time.sleep(2)
	tn.write(('' + '\n').encode('ascii'))
	#time.sleep(2)
	tn.write(('' + '\n').encode('ascii'))
	# time.sleep(1)
	tn.write(('' + '\n').encode('ascii'))
	# time.sleep(1)
	tn.write(('' + '\n').encode('ascii'))
	# time.sleep(1)
	#tprint("successful login\n")
	#tn.write(('\x03').encode('ascii'))
	#time.sleep(2)
	#tprint("successful login\n")
	#tn.write(('\x03').encode('ascii'))
	#time.sleep(2)
	#tn.write(('\x03').encode('ascii'))
	#time.sleep(2)
	# tn.read_until(("login: ").encode('ascii'),timeout=10)
	# tn.write(('admin' + '\n').encode('ascii'))
	# tn.read_until(("Password: ").encode('ascii'),timeout=10)
	# tn.write(('' + '\n').encode('ascii'))
	# sleep(1)
	# tn.read_until(("# ").encode('ascii'),timeout=10)

	# tn.write(('' + '\n').encode('ascii'))
	# sleep(1)
	# tn.write(('' + '\n').encode('ascii'))
	# sleep(1)
	# tn.write(('' + '\n').encode('ascii'))
	# sleep(1)
	if switch_find_login_prompt(tn) == True:
		tn.read_until(("login: ").encode('ascii'),timeout=10)
		tn.write(('admin' + '\n').encode('ascii'))
		tn.read_until(("Password: ").encode('ascii'),timeout=10)
		tn.write(('fortinet123' + '\n').encode('ascii'))
		sleep(1)
		tn.read_until(("# ").encode('ascii'),timeout=10)
	# tn.write(('get system status\n').encode('ascii'))
	# tn.read_until(("# ").encode('ascii'),timeout=2)
	if login_mode != 'silent':
		tprint("switch_login: Login sucessful!\n")
	switch_configure_cmd(tn,'config system global',mode="silent")
	switch_configure_cmd(tn,'set admintimeout 480',mode="silent")
	switch_configure_cmd(tn,'end',mode="silent")
	return tn

def enter_login_info(tn,*args,**kwargs):
	if "password" in kwargs:
		password = kwargs['password']
	else:
		password = 'fortinet123'
	tn.read_until(("login: ").encode('ascii'),timeout=10)
	tn.write(('admin' + '\n').encode('ascii'))
	tn.read_until(("Password: ").encode('ascii'),timeout=10)
	tn.write((password + '\n').encode('ascii'))
	sleep(1)
	tn.read_until(("# ").encode('ascii'),timeout=10)
	switch_configure_cmd(tn,'config system global',mode="silent")
	switch_configure_cmd(tn,'set admintimeout 480',mode="silent")
	switch_configure_cmd(tn,'end',mode="silent")
	return tn


def find_dut_prompt_cisco(tn):
	tn.write(('' + '\n').encode('ascii'))
	#print("Reading prompt and retrieve prompt......")
	output = tn.read_until(("#").encode('ascii'))
	out_list = output.split(b'\r\n')
	encoding = 'utf-8'
	for o in out_list:
		o_str = o.decode(encoding).rstrip(' ')
		if "#" in o_str:
			prompt = o_str.strip(' ')
			prompt = prompt.strip("#")
	#print(prompt)
	return prompt

def find_dut_prompt(tn):
	tn.write(('' + '\n').encode('ascii'))
	sleep(0.5)
	tn.write(('' + '\n').encode('ascii'))
	sleep(0.5)
	tn.write(('' + '\n').encode('ascii'))
	sleep(0.5)
	tn.write(('' + '\n').encode('ascii'))
	sleep(0.5)
	tn.write(('' + '\n').encode('ascii'))
	sleep(0.5)
	tn.write(('' + '\n').encode('ascii'))
	sleep(0.5)
	tn.write(('' + '\n').encode('ascii'))
	sleep(0.5)
	tn.write(('' + '\n').encode('ascii'))
	sleep(0.5) #added this line for fortigate 
	output = tn.read_until(("# ").encode('ascii'))
	out_list = output.split(b'\r\n')
	encoding = 'utf-8'
	for o in out_list:
	        o_str = o.decode(encoding).rstrip(' ')
	        if "#" in o_str:
	                prompt = o_str.strip(' ')
	                prompt = prompt.strip("#")
	dprint(prompt)
	return prompt


# def find_dut_prompt(tn):
# 	tn.write(('' + '\n').encode('ascii'))
# 	tn.write(('' + '\n').encode('ascii'))
# 	sleep(0.1)
# 	tn.write(('' + '\n').encode('ascii'))
# 	output = tn.read_until(("# ").encode('ascii'))
# 	out_list = output.split(b'\r\n')
# 	encoding = 'utf-8'
# 	for o in out_list:
# 		o_str = o.decode(encoding).rstrip(' ')
# 		if "#" in o_str:
# 			prompt = o_str.strip(' ')
# 			prompt = prompt.strip("#")
# 	dprint(prompt)
# 	return prompt

def reliable_telnet(ip_address,*args,**kwargs):
	if 'sig' in kwargs:
		event = kwargs['sig']
		end = event.is_set()
	else:
		end = False
	while not end:
		handle = telnet_connection(ip_address)
		if handle == False:
			sleep(3)
			if 'sig' in kwargs:
				event = kwargs['sig']
				end = event.is_set()
			else:
				end = False
			continue
		else:
			return handle

def telnet_apc(ip_address,**kwargs):
	tprint(f"APC IP interface = {str(ip_address)}")
	if "password" in kwargs:
		pwd = kwargs["password"]
	else:
		pwd = 'apc'
	if "user" in kwargs:
		user = kwargs['user']
	else:
		user = 'apc'
	#switch_login(ip_address,console_port)
	try:
		tn = telnetlib.Telnet(ip_address,23,10)
	except Exception as e: 
		tprint("!!!!!!!!!!!Telnet is either time out or not response from device, Need to retry later")
		# sleep(2)
		# tn = telnetlib.Telnet(ip_address,console_port_int)
		return False

	tn.write(('' + '\n').encode('ascii'))
	tn.write(('' + '\n').encode('ascii'))
	tn.write(('' + '\n').encode('ascii'))
	tn.read_until(("User Name : ").encode('ascii'),timeout=5)
	tn.write((user + '\n').encode('ascii'))
	tn.read_until(("Password: ").encode('ascii'),timeout=5)
	tn.write((pwd + '\n').encode('ascii'))
	tn.read_until((">").encode('ascii'),timeout=5)
	# tn.write(('' + '\n').encode('ascii'))
	# tn.write(('' + '\n').encode('ascii'))
	tn.write(('about' + '\n').encode('ascii'))
	sleep(2)
	output = tn.read_very_eager()
	print(output)
	return tn

def telnet_poe(ip_address,port,**kwargs):
	tprint(f"POE Tester Console  = {str(ip_address),port}")
	if "password" in kwargs:
		pwd = kwargs["password"]
	else:
		pwd = 'apc'
	if "user" in kwargs:
		user = kwargs['user']
	else:
		user = 'apc'
	#switch_login(ip_address,console_port)

	# status = clear_console_line(ip_address,str(port),login_pwd='fortinet123', exec_pwd='fortinet123', prompt='#')
	# if status['status'] != 1:
	# 	logger.console('unable clear console port %s' % console_port)
	# time.sleep(1)
	try:
		tn = telnetlib.Telnet(ip_address,port,10)
	except ConnectionRefusedError: 
		tprint("!!!!!!!!!!!the console is being used, need to clear it first")
		status = clear_console_line(ip_address,str(port),login_pwd='fortinet123', exec_pwd='fortinet123', prompt='#')
		if status['status'] != 1:
			logger.console('unable clear console port %s' % console_port)
			exit()
		sleep(2)
		tn = telnetlib.Telnet(ip_address,port,10)

	tn.write(('' + '\r\n').encode('utf-8'))
	tn.write(('' + '\r\n').encode('utf-8'))
	tn.write(('' + '\r\n').encode('utf-8'))
	tn.write(('' + '\r\n').encode('utf-8'))
	tn.write(('' + '\r').encode('utf-8'))
	sleep(2)
	tn.read_until((">").encode('utf-8'),timeout=5)
	# print("start enter command......")
	# #tn.write(('measure').encode('ascii'))
	# tn.write(("measure" + "\r").encode("utf-8"))
	# sleep(2)
	# #output = tn.read_until((">").encode('ascii'),timeout=5)
	# output = tn.read_very_eager()
	# tn.write(("measure" + "\r").encode("utf-8"))
	# sleep(2)
	# output = tn.read_very_eager()
	# print(output)

	# tn.write(("status" + "\r").encode("utf-8"))
	# sleep(2)
	# output = tn.read_very_eager()
	# print(output)
	return tn

def telnet_connection(ip_address,**kwargs):
	tprint(f"Device management interface = {str(ip_address)}")
	if "password" in kwargs:
		pwd = kwargs["password"]
	else:
		pwd = 'fortinet123'
	user = 'admin'
	#switch_login(ip_address,console_port)
	try:
		tn = telnetlib.Telnet(ip_address,23,10)
	except Exception as e: 
		tprint("!!!!!!!!!!!Telnet is either time out or not response from device, Need to retry later")
		# sleep(2)
		# tn = telnetlib.Telnet(ip_address,console_port_int)
		return False

	tn.write(('' + '\n').encode('ascii'))
	tn.write(('' + '\n').encode('ascii'))
	tn.read_until(("login: ").encode('ascii'),timeout=5)
	tn.write((user + '\n').encode('ascii'))
	tn.read_until(("Password: ").encode('ascii'),timeout=5)
	tn.write((pwd + '\n').encode('ascii'))
	tn.read_until(("# ").encode('ascii'),timeout=5)
	tn.write(('' + '\n').encode('ascii'))
	tn.write(('' + '\n').encode('ascii'))
	return tn

def ping_ipv4(tn,*args,**kwargs):
	ip = kwargs["ip"]
	result = collect_execute_cmd(tn,f"execute ping {ip}")
	dprint(result)
	print_cmd_output_from_list(result)

def ping_ipv6(tn,*args,**kwargs):
	ip = kwargs["ip"]
	result = collect_execute_cmd(tn,f"execute ping6 {ip}")
	dprint(result)
	print_cmd_output_from_list(result)

def ping_ipv6_extensive(*args,**kwargs):
	#ping_ipv6_extensive(console=self.switches[i].console, ip_src=ip_src,ip_dst = ip_dst,name=interface_name)
	tn = kwargs["console"]
	ip_src = kwargs["ip_src"]
	ip_dst = kwargs["ip_dst"]
	interface_name = kwargs['name']
	sw_src = kwargs['sw_src']
	sw_dst = kwargs['sw_dst']
	Info(f"=================== Ping source: {interface_name}: 2nd IPv6 {ip_src} on {sw_src} ===============")
	show_execute_cmd(tn,f"execute ping6-options source {ip_src}")
	Info(f"=================== Ping Destination: {ip_dst} on {sw_dst} ===============")
	show_execute_cmd(tn,f"execute ping6 {ip_dst}")
 
def relogin_factory_reset(*args,**kwargs):
	tn = kwargs['dut']
	hostname = kwargs['host']
	 
	tn.write(('' + '\n').encode('ascii'))
	tn.write(('' + '\n').encode('ascii'))
	time.sleep(0.2)

	tn.read_until(("login: ").encode('ascii'),timeout=5)

	tn.write(('admin' + '\n').encode('ascii'))

	tn.read_until(("Password: ").encode('ascii'),timeout=5)

	###################### Has to be 3 enters: Dont change ################
	tn.write(('' + '\n').encode('ascii'))
	tn.write(('' + '\n').encode('ascii'))
	tn.write(('' + '\n').encode('ascii'))
	############################ Dont change ##############################

	prompt = switch_find_login_prompt_new(tn)
	p = prompt[0]
	debug(prompt)
	if p == "change":
		Info(f"Login {hostname} after factory reset , changing password..... ") #This needs to rewrite to take care factory reset situation
		############################################# Dont change these lines ##################################
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii')) 
		sleep(3)       # For some console, it took long time for promopt to show up.  Keep this wait 3 sec
		############################################# Dont change these lines ###################################
		tn.read_until(("login: ").encode('ascii'),timeout=5)
		tn.write(('admin' + '\n').encode('ascii'))           # this would not work for factory reset scenario
		tn.write(('' + '\n').encode('ascii'))
		tn.read_until(("Password: ").encode('ascii'),timeout=5) #read_util() can not work with prompt with prompt with space, such as New Password
		tn.write(('fortinet123' + '\n').encode('ascii'))   #this is for factory reset scenario
		tn.read_until(("Password: ").encode('ascii'),timeout=10)
		tn.write(('fortinet123' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.read_until(("# ").encode('ascii'),timeout=10)
		# tn.read_until(("login: ").encode('ascii'),timeout=5)
		# tn.write(('admin' + '\n').encode('ascii'))           # this would not work for factory reset scenario
		# sleep(0.6)
		# tn.write(('' + '\n').encode('ascii')) #This line is needed. Don't deleted!!!!!! After enter is hit, user can enter password
		# tn.read_until(("Password: ").encode('ascii'),timeout=5) #read_util() can not work with prompt with prompt with space, such as New Password
		# tn.write(('fortinet123' + '\n').encode('ascii'))   #this is for factory reset scenario
		# #sleep(0.5) Must not have sleep in between write and read_until
		# tn.read_until(("Password: ").encode('ascii'),timeout=10)
		# tn.write(('fortinet123' + '\n').encode('ascii'))
		# sleep(0.5)
		# tn.write(('' + '\n').encode('ascii'))
		# tn.write(('' + '\n').encode('ascii'))
		# tn.read_until(("# ").encode('ascii'),timeout=10)

		switch_configure_cmd(tn,'config system global')
		switch_configure_cmd(tn,'set admintimeout 480')
		switch_configure_cmd(tn,'end')
		tprint("get_switch_telnet_connection_new: Login sucessful!\n")
		try:
			print(f"=========== Software Image = {find_dut_build(tn)[0]} ==================")
			print(f"=========== Software Build = {find_dut_build(tn)[1]} ==================")
		except Exception as e:
			pass
	else:
		ErrorNotify(f"Not able to login {hostname} after factory reset the device")
		exit()


def telnet_switch_original(ip_address, console_port,*args,**kwargs):
	tprint("console server ip ="+str(ip_address))
	tprint("console port="+str(console_port))
	if "password" in kwargs:
		pwd = kwargs["password"]
	else:
		pwd = 'Fortinet123!'
	if "platform" in kwargs:
		platform = kwargs['platform']
	else:
		platform = "fortinet"

	if 'relogin' in kwargs:
		relogin = kwargs['relogin']
	else:
		relogin = False

	if relogin:
		tn = kwargs['console']
	
	console_port_int = int(console_port)
	if relogin == False:
		if settings.CLEAR_LINE:
			status = clear_console_line(ip_address,str(console_port),login_pwd='fortinet123', exec_pwd='fortinet123', prompt='#')
			if status['status'] != 1:
				logger.console('unable clear console port %s' % console_port)
			time.sleep(1)
		try:
			tn = telnetlib.Telnet(ip_address,console_port_int)
		except ConnectionRefusedError: 
			tprint("!!!!!!!!!!!the console is being used, need to clear it first")
			status = clear_console_line(ip_address,str(console_port),login_pwd='fortinet123', exec_pwd='fortinet123', prompt='#')
			if status['status'] != 1:
				logger.console('unable clear console port %s' % console_port)
				exit()
			sleep(2)
			tn = telnetlib.Telnet(ip_address,console_port_int)
	 
	tn.write(('\x03\n').encode('ascii'))
	time.sleep(2)
	tn.write(('\x03\n').encode('ascii'))
	time.sleep(2)
	# tn.write(('x03\n').encode('ascii'))
	# time.sleep(0.2)
	# tn.write(('' + '\n').encode('ascii'))
	# time.sleep(0.2)
	# tn.write(('' + '\n').encode('ascii'))
	# time.sleep(0.2)
	# tn.write(('' + '\n').encode('ascii'))
	# time.sleep(0.2)
	# tn.write(('' + '\n').encode('ascii'))
	# time.sleep(0.2)

	tn.read_until(("login: ").encode('ascii'),timeout=5)
	tn.write(('admin' + '\n').encode('ascii'))
	tn.read_until(("Password: ").encode('ascii'),timeout=5)

	tn.write(('' + '\n').encode('ascii'))
	sleep(2)
	# tn.write(('' + '\n').encode('ascii'))
	# tn.write(('' + '\n').encode('ascii'))
	# tn.write((pwd + '\n').encode('ascii'))
	prompt = switch_find_login_prompt_new(tn,password=pwd)
	p = prompt[0]
	debug(prompt)
	if p == "change":
		Info("Login after factory reset, changing password..... ") #This needs to rewrite to take care factory reset situation
		########################################## Golden lines: Do not change #############
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		# tn.write(('' + '\n').encode('ascii'))
		# tn.write(('' + '\n').encode('ascii'))
		# tn.write(('' + '\n').encode('ascii'))
		# tn.write(('' + '\n').encode('ascii'))
		# tn.write(('' + '\n').encode('ascii'))
		# tn.write(('' + '\n').encode('ascii'))
		sleep(1)
		#################################### Don't change ################################
		tn.read_until(("login: ").encode('ascii'),timeout=5)
		tn.write(('admin' + '\n').encode('ascii'))           # this would not work for factory reset scenario
		tn.write(('' + '\n').encode('ascii'))
		tn.read_until(("Password: ").encode('ascii'),timeout=5) #read_util() can not work with prompt with prompt with space, such as New Password
		print(f"!!!!!!! Debug!!!!! setting password after factory reset. New password = {pwd}")
		tn.write((pwd + '\n').encode('ascii'))   #this is for factory reset scenario
		tn.read_until(("Password: ").encode('ascii'),timeout=10)
		tn.write((pwd + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.read_until(("# ").encode('ascii'),timeout=10)
	if p == "cisco":
		debug("Login in Cisco device......")
		tn.read_until(("login: ").encode('ascii'),timeout=10)
		tn.write(('admin' + '\n').encode('ascii'))
		tn.read_until(("Password: ").encode('ascii'),timeout=10)
		tn.write(('fortinet123' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		sleep(0.2)
		tn.read_until(("# ").encode('ascii'),timeout=10)

	if p == 'login':
		Info("Login after time out or reboot") #This needs to rewrite to take care factory reset situation
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		sleep(1)
		tn.read_until(("login: ").encode('ascii'),timeout=10)
		tn.write(('admin' + '\n').encode('ascii'))           # this would not work for factory reset scenario
		tn.read_until(("Password: ").encode('ascii'),timeout=10)
		tn.write((pwd + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		sleep(0.2)
		tn.read_until(("# ").encode('ascii'),timeout=10)
	elif p == 'shell':
		Info("Login without password")
		#prevent enter a prompt that is in a config mode
		tn.write(('end' + '\n').encode('ascii'))
		tn.write(('end' + '\n').encode('ascii'))
	elif p == 'new':
		Info(f"This first time login after factory reset, not allowing blank password, password has been changed to {pwd}")
	elif p == None:
		Info("Login prompt not seen yet, press enter a couple times to show login prompt")
		# tn.write(('\x03').encode('ascii'))
		# tn.write(('\x03').encode('ascii'))
		# tn.write(('\x03').encode('ascii'))
		# tn.write(('\x03').encode('ascii'))
		#time.sleep(1)
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		sleep(1)
		 
		tn.read_until(("login: ").encode('ascii'),timeout=10)
		tn.write(('admin' + '\n').encode('ascii'))
		tn.read_until(("Password: ").encode('ascii'),timeout=10)

		tn.write((pwd + '\n').encode('ascii'))
		sleep(0.5)
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		sleep(0.5)
		tn.read_until(("# ").encode('ascii'),timeout=10)
			 

	if platform == "fortinet":
		switch_configure_cmd(tn,'config system global')
		switch_configure_cmd(tn,'set admintimeout 480')
		switch_configure_cmd(tn,'end')
		switch_configure_cmd(tn,'config system console')
		switch_configure_cmd(tn,'set output standard')
		switch_configure_cmd(tn,'end')
		tprint("get_switch_telnet_connection_new: Login sucessful!\n")
		try:
			print(f"=========== Software Image = {find_dut_build(tn)[0]} ==================")
			print(f"=========== Software Build = {find_dut_build(tn)[1]} ==================")
		except Exception as e:
			pass
	elif platform == "fortigate":
		switch_configure_cmd(tn,'config global')
		switch_configure_cmd(tn,'config system console')
		switch_configure_cmd(tn,'set output standard')
		switch_configure_cmd(tn,'end')
		switch_configure_cmd(tn,'end')

		switch_configure_cmd(tn,'config global')
		switch_configure_cmd(tn,'config system global')
		switch_configure_cmd(tn,'set admin-console-timeout 300')
		switch_configure_cmd(tn,'end')
		switch_configure_cmd(tn,'end')

		tprint("get_switch_telnet_connection_new: Login sucessful!\n")
		try:
			print(f"=========== Software Image = {find_dut_build(tn)[0]} ==================")
			print(f"=========== Software Build = {find_dut_build(tn)[1]} ==================")
		except Exception as e:
			pass
	elif platform == "n9k":
		print("--------- TBD: utils.py get_switch_telnet_connection_new() | will configure some basic stuff like exec-timeout -----------")
		# config = f"""
		# config t
		#     line con 
		#         exec-timeout 300 
		# end
		# """
		# config_cmds_lines_cisco(tn,config)
		# switch_configure_cmd_cisco(tn,'config t')
		# switch_configure_cmd_cisco(tn,'line con')
		# switch_configure_cmd_cisco(tn,'exec-timeout 300')
		# switch_configure_cmd_cisco(tn,'end')
	else:
		print("=========== This is a default device platform, assume it is a Fortinet Switch ============")
		switch_configure_cmd(tn,'config system global')
		switch_configure_cmd(tn,'set admintimeout 480')
		switch_configure_cmd(tn,'end')
		switch_configure_cmd(tn,'config system console')
		switch_configure_cmd(tn,'set output standard')
		switch_configure_cmd(tn,'end')
		tprint("get_switch_telnet_connection_new: Login sucessful!\n")
		try:
			print(f"=========== Software Image = {find_dut_build(tn)[0]} ==================")
			print(f"=========== Software Build = {find_dut_build(tn)[1]} ==================")
		except Exception as e:
			pass
	return tn


def telnet_switch(ip_address, console_port,*args,**kwargs):
	tprint("console server ip ="+str(ip_address))
	tprint("console port="+str(console_port))
	if "password" in kwargs:
		pwd = kwargs["password"]
	else:
		pwd = 'Fortinet123!'
	if "platform" in kwargs:
		platform = kwargs['platform']
	else:
		platform = "fortinet"

	if 'relogin' in kwargs:
		relogin = kwargs['relogin']
	else:
		relogin = False

	if relogin:
		tn = kwargs['console']
	
	console_port_int = int(console_port)
	if relogin == False:
		if settings.CLEAR_LINE:
			status = clear_console_line(ip_address,str(console_port),login_pwd='fortinet123', exec_pwd='fortinet123', prompt='#')
			if status['status'] != 1:
				logger.console('unable clear console port %s' % console_port)
			time.sleep(1)
		try:
			tn = telnetlib.Telnet(ip_address,console_port_int)
		except ConnectionRefusedError: 
			tprint("!!!!!!!!!!!the console is being used, need to clear it first")
			status = clear_console_line(ip_address,str(console_port),login_pwd='fortinet123', exec_pwd='fortinet123', prompt='#')
			if status['status'] != 1:
				logger.console('unable clear console port %s' % console_port)
				exit()
			sleep(2)
			tn = telnetlib.Telnet(ip_address,console_port_int)
		except TimeoutError: 
			tprint("!!!!!!!!!!!Telnet to console server timeout, skip this switch console connection")
			tn = None 
			return tn
		except Exception as e:
			tprint("!!!!!!!!!!! Something is wrong with telnet connection, check your network connectitiy to console server")
			tn = None 
			return tn
	tn.write(('\x03\n').encode('ascii'))
	time.sleep(3)
	tn.write(('\x03\n').encode('ascii'))
	time.sleep(3)
	tn.write(('\x03\n').encode('ascii'))
	time.sleep(3)
 
	tn.read_until(("login: ").encode('ascii'),timeout=5)
	tn.write(('admin' + '\n').encode('ascii'))
	tn.read_until(("Password: ").encode('ascii'),timeout=5)

	tn.write(('' + '\n').encode('ascii'))
	sleep(1)
	tn.write(('' + '\n').encode('ascii'))
	sleep(1)
	tn.write(('' + '\n').encode('ascii'))
	sleep(1)
	tn.write(('' + '\n').encode('ascii'))
	sleep(1)


	Info("See what prompt the console is at")
	TIMEOUT = 3
	output = tn.expect([re.compile(b"login:")],timeout=TIMEOUT)
	Info(f"collect info to look for prompt: {output}")
	Info(f"output[2] = {output[2].decode().strip()}")
	Info(output[2].decode().strip())
	prompt = output[2].decode().strip()
	if "New Password:"in prompt:
		debug(f"it is a new switch that needs to change password, change password to {pwd} ")
		tn.write((pwd + '\n').encode('ascii'))
		tn.write((pwd + '\n').encode('ascii'))
		return tn
	 
	prompt = switch_find_login_prompt_new(tn,password=pwd)
	p = prompt[0]
	debug(prompt)
	if p == "change":
		Info("Login after factory reset, changing password..... ") #This needs to rewrite to take care factory reset situation
		########################################## Golden lines: Do not change #############
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		sleep(1)
		#################################### Don't change ################################
		tn.read_until(("login: ").encode('ascii'),timeout=5)
		tn.write(('admin' + '\n').encode('ascii'))           # this would not work for factory reset scenario
		tn.write(('' + '\n').encode('ascii'))
		tn.read_until(("Password: ").encode('ascii'),timeout=5) #read_util() can not work with prompt with prompt with space, such as New Password
		print(f"!!!!!!! Debug!!!!! setting password after factory reset. New password = {pwd}")
		tn.write((pwd + '\n').encode('ascii'))   #this is for factory reset scenario
		tn.read_until(("Password: ").encode('ascii'),timeout=10)
		tn.write((pwd + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.read_until(("# ").encode('ascii'),timeout=10)
	if p == "cisco":
		debug("Login in Cisco device......")
		tn.read_until(("login: ").encode('ascii'),timeout=10)
		tn.write(('admin' + '\n').encode('ascii'))
		tn.read_until(("Password: ").encode('ascii'),timeout=10)
		tn.write(('fortinet123' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		sleep(0.2)
		tn.read_until(("# ").encode('ascii'),timeout=10)

	if p == 'login':
		Info("Login after time out or reboot") #This needs to rewrite to take care factory reset situation
		tn.write(('' + '\n').encode('ascii'))
		sleep(0.5)
		tn.write(('' + '\n').encode('ascii'))
		sleep(0.5)
		tn.write(('' + '\n').encode('ascii'))
		sleep(0.5)
		tn.write(('' + '\n').encode('ascii'))
		sleep(0.5)
		tn.write(('' + '\n').encode('ascii'))
		sleep(0.5)
		tn.read_until(("login: ").encode('ascii'),timeout=10)
		tn.write(('admin' + '\n').encode('ascii'))           # this would not work for factory reset scenario
		tn.read_until(("Password: ").encode('ascii'),timeout=10)
		tn.write((pwd + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		sleep(0.2)
		tn.read_until(("# ").encode('ascii'),timeout=10)
	elif p == 'shell':
		Info("Login without password")
		#prevent enter a prompt that is in a config mode
		tn.write(('end' + '\n').encode('ascii'))
		tn.write(('end' + '\n').encode('ascii'))
	elif p == 'new':
		Info(f"This first time login after factory reset, not allowing blank password, password has been changed to {pwd}")
	elif p == None:
		Info("Not in login prompt, press enter a couple times to show login prompt")
		# tn.write(('\x03').encode('ascii'))
		# tn.write(('\x03').encode('ascii'))
		# tn.write(('\x03').encode('ascii'))
		# tn.write(('\x03').encode('ascii'))
		#time.sleep(1)
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		sleep(1)
		 
		tn.read_until(("login: ").encode('ascii'),timeout=10)
		tn.write(('admin' + '\n').encode('ascii'))
		tn.read_until(("Password: ").encode('ascii'),timeout=10)

		tn.write((pwd + '\n').encode('ascii'))
		sleep(0.5)
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		sleep(0.5)
		tn.read_until(("# ").encode('ascii'),timeout=10)
			 

	if platform == "fortinet":
		switch_configure_cmd(tn,'config system global',mode="fast")
		switch_configure_cmd(tn,'set admintimeout 480',mode="fast")
		switch_configure_cmd(tn,'end',mode="fast")
		switch_configure_cmd(tn,'config system console',mode="fast")
		switch_configure_cmd(tn,'set output standard',mode="fast")
		switch_configure_cmd(tn,'end',mode="fast")
		tprint("get_switch_telnet_connection_new: Login sucessful!\n")
		try:
			print(f"=========== Software Image = {find_dut_build(tn)[0]} ==================")
			print(f"=========== Software Build = {find_dut_build(tn)[1]} ==================")
		except Exception as e:
			pass
	elif platform == "fortigate":
		switch_configure_cmd(tn,'config global',mode ="fast")
		switch_configure_cmd(tn,'config system console',mode ="fast")
		switch_configure_cmd(tn,'set output standard',mode ="fast")
		switch_configure_cmd(tn,'end',mode ="fast")
		switch_configure_cmd(tn,'end',mode ="fast")

		switch_configure_cmd(tn,'config global',mode ="fast")
		switch_configure_cmd(tn,'config system global',mode ="fast")
		switch_configure_cmd(tn,'set admin-console-timeout 300',mode ="fast")
		switch_configure_cmd(tn,'end',mode ="fast")
		switch_configure_cmd(tn,'end',mode ="fast")

		tprint("get_switch_telnet_connection_new: Login sucessful!\n")
		try:
			print(f"=========== Software Image = {find_dut_build(tn)[0]} ==================")
			print(f"=========== Software Build = {find_dut_build(tn)[1]} ==================")
		except Exception as e:
			pass
	elif platform == "n9k":
		print("--------- TBD: utils.py get_switch_telnet_connection_new() | will configure some basic stuff like exec-timeout -----------")
		# config = f"""
		# config t
		#     line con 
		#         exec-timeout 300 
		# end
		# """
		# config_cmds_lines_cisco(tn,config)
		# switch_configure_cmd_cisco(tn,'config t')
		# switch_configure_cmd_cisco(tn,'line con')
		# switch_configure_cmd_cisco(tn,'exec-timeout 300')
		# switch_configure_cmd_cisco(tn,'end')
	else:
		print("=========== This is a default device platform, assume it is a Fortinet Switch ============")
		switch_configure_cmd(tn,'config system global',mode="fast")
		switch_configure_cmd(tn,'set admintimeout 480',mode="fast")
		switch_configure_cmd(tn,'end',mode="fast")
		switch_configure_cmd(tn,'config system console',mode="fast")
		switch_configure_cmd(tn,'set output standard',mode="fast")
		switch_configure_cmd(tn,'end',mode="fast")
		tprint("get_switch_telnet_connection_new: Login sucessful!\n")
		try:
			print(f"=========== Software Image = {find_dut_build(tn)[0]} ==================")
			print(f"=========== Software Build = {find_dut_build(tn)[1]} ==================")
		except Exception as e:
			pass
		print("=========== This is a uncognized device platform ============")
	return tn

def get_switch_telnet_connection_new(ip_address, console_port,**kwargs):
	tprint("console server ip ="+str(ip_address))
	tprint("console port="+str(console_port))
	if "password" in kwargs:
		pwd = kwargs["password"]
	else:
		pwd = ''
	if "platform" in kwargs:
		platform = kwargs['platform']
	else:
		platform = "fortinet"
	
	console_port_int = int(console_port)
	if settings.CLEAR_LINE:
		status = clear_console_line(ip_address,str(console_port),login_pwd='fortinet123', exec_pwd='fortinet123', prompt='#')
		if status['status'] != 1:
			logger.console('unable clear console port %s' % console_port)
		time.sleep(1)
	try:
		tn = telnetlib.Telnet(ip_address,console_port_int)
	except ConnectionRefusedError: 
		tprint("!!!!!!!!!!!the console is being used, need to clear it first")
		status = clear_console_line(ip_address,str(console_port),login_pwd='fortinet123', exec_pwd='fortinet123', prompt='#')
		if status['status'] != 1:
			logger.console('unable clear console port %s' % console_port)
			exit()
		sleep(2)
		tn = telnetlib.Telnet(ip_address,console_port_int)
	 
	tn.write(('\x03\n').encode('ascii'))
	tn.write(('\x03\n').encode('ascii'))
	time.sleep(0.2)

	tn.write(('' + '\n').encode('ascii'))
	tn.write(('' + '\n').encode('ascii'))
	 
	time.sleep(0.2)

	tn.read_until(("login: ").encode('ascii'),timeout=5)
	tn.write(('admin' + '\n').encode('ascii'))
	tn.read_until(("Password: ").encode('ascii'),timeout=5)

	tn.write(('' + '\n').encode('ascii'))
	tn.write(('' + '\n').encode('ascii'))
	tn.write(('' + '\n').encode('ascii'))
	tn.write((pwd + '\n').encode('ascii'))
	prompt = switch_find_login_prompt_new(tn)
	p = prompt[0]
	debug(prompt)
	if p == "change":
		Info("Login after factory reset, changing password..... ") #This needs to rewrite to take care factory reset situation
		########################################## Golden lines: Do not change #############
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		sleep(1)
		#################################### Don't change ################################
		tn.read_until(("login: ").encode('ascii'),timeout=5)
		tn.write(('admin' + '\n').encode('ascii'))           # this would not work for factory reset scenario
		tn.write(('' + '\n').encode('ascii'))
		tn.read_until(("Password: ").encode('ascii'),timeout=5) #read_util() can not work with prompt with prompt with space, such as New Password
		tn.write((pwd + '\n').encode('ascii'))   #this is for factory reset scenario
		tn.read_until(("Password: ").encode('ascii'),timeout=10)
		tn.write((pwd + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.read_until(("# ").encode('ascii'),timeout=10)
	if p == "cisco":
		debug("Login in Cisco device......")
		tn.read_until(("login: ").encode('ascii'),timeout=10)
		tn.write(('admin' + '\n').encode('ascii'))
		tn.read_until(("Password: ").encode('ascii'),timeout=10)
		tn.write(('fortinet123' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		sleep(0.2)
		tn.read_until(("# ").encode('ascii'),timeout=10)

	if p == 'login':
		Info("Login after time out or reboot") #This needs to rewrite to take care factory reset situation
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.read_until(("login: ").encode('ascii'),timeout=10)
		tn.write(('admin' + '\n').encode('ascii'))           # this would not work for factory reset scenario
		# tn.write(('fortinet123' + '\n').encode('ascii'))   #this is for factory reset scenario
		tn.read_until(("Password: ").encode('ascii'),timeout=10)
		tn.write((pwd + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		sleep(0.2)
		tn.read_until(("# ").encode('ascii'),timeout=10)
	elif p == 'shell':
		Info("Login without password")
		#prevent enter a prompt that is in a config mode
		tn.write(('end' + '\n').encode('ascii'))
		tn.write(('end' + '\n').encode('ascii'))
	elif p == 'new':
		Info("This first time login to image not allowing blank password, password has been changed ???")
	elif p == None:
		Info("Not in login prompt, press enter a couple times to show login prompt")
		# tn.write(('\x03').encode('ascii'))
		# tn.write(('\x03').encode('ascii'))
		# tn.write(('\x03').encode('ascii'))
		# tn.write(('\x03').encode('ascii'))
		#time.sleep(1)
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))

		tn.read_until(("login: ").encode('ascii'),timeout=10)
		tn.write(('admin' + '\n').encode('ascii'))
		tn.read_until(("Password: ").encode('ascii'),timeout=10)
		tn.write((pwd + '\n').encode('ascii'))
		sleep(0.5)
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		sleep(0.5)
		tn.read_until(("# ").encode('ascii'),timeout=10)

	if platform == "fortinet":
		switch_configure_cmd(tn,'config system global')
		switch_configure_cmd(tn,'set admintimeout 480')
		switch_configure_cmd(tn,'end')
		tprint("get_switch_telnet_connection_new: Login sucessful!\n")
		try:
			print(f"=========== Software Image = {find_dut_build(tn)[0]} ==================")
			print(f"=========== Software Build = {find_dut_build(tn)[1]} ==================")
		except Exception as e:
			pass
	elif platform == "n9k":
		print("--------- TBD: utils.py get_switch_telnet_connection_new() | will configure some basic stuff like exec-timeout -----------")
		# config = f"""
		# config t
		#     line con 
		#         exec-timeout 300 
		# end
		# """
		# config_cmds_lines_cisco(tn,config)
		# switch_configure_cmd_cisco(tn,'config t')
		# switch_configure_cmd_cisco(tn,'line con')
		# switch_configure_cmd_cisco(tn,'exec-timeout 300')
		# switch_configure_cmd_cisco(tn,'end')
	else:
		print("=========== This is a uncognized device platform ============")
	return tn

def config_admin_timeout(dut_list):
	for dut in dut_list:
		switch_configure_cmd(dut,'config system global')
		switch_configure_cmd(dut,'set admintimeout 480')
		switch_configure_cmd(dut,'end')

def console_timer(seconds,**kwargs):
	if 'msg' in kwargs:
		notice = kwargs['msg']
		tprint(f'========================= {notice} ==========================')
	for remaining in range(seconds, 0, -1):
		sys.stdout.write("\r")
		sys.stdout.write("============================ Timer:{:2d} seconds remaining =======================".format(remaining))
		sys.stdout.flush()
		time.sleep(1)
	sys.stdout.write("\n")

def get_switch_telnet_connection(ip_address, console_port,**kwargs):
	tprint("console server ip ="+str(ip_address))
	tprint("console port="+str(console_port))
	if "password" in kwargs:
		pwd = kwargs["password"]
	else:
		pwd = ''
	
	console_port_int = int(console_port)
	if settings.CLEAR_LINE:
		status = clear_console_line(ip_address,str(console_port),login_pwd='fortinet123', exec_pwd='fortinet123', prompt='#')
		if status['status'] != 1:
			logger.console('unable clear console port %s' % console_port)
		time.sleep(1)
	#switch_login(ip_address,console_port)
	try:
		tn = telnetlib.Telnet(ip_address,console_port_int)
	except ConnectionRefusedError: 
		tprint("!!!!!!!!!!!the console is being used, need to clear it first")
		status = clear_console_line(ip_address,str(console_port),login_pwd='fortinet123', exec_pwd='fortinet123', prompt='#')
		if status['status'] != 1:
			logger.console('unable clear console port %s' % console_port)
			exit()
		sleep(2)
		tn = telnetlib.Telnet(ip_address,console_port_int)
	#tprint("successful login\n")

	#tn.write('' + '\n')
	# tn.write(('get system status\n').encode('ascii'))
	# time.sleep(1)

	#tprint("successful login\n")

	# tn.write(('' + '\n').encode('ascii'))
	# time.sleep(1)

	#tprint("successful login\n")
	# tn.write(('\x03').encode('ascii'))
	# time.sleep(2)

	#tprint("successful login\n")
	# tn.write(('\x03').encode('ascii'))
	# time.sleep(2)

	#tprint("successful login\n")
	# tn.write(('\x03').encode('ascii'))
	# time.sleep(2)

	#tprint("successful login\n")
	tn.write(('' + '\n').encode('ascii'))
	tn.write(('' + '\n').encode('ascii'))
	tn.write(('' + '\n').encode('ascii'))
	tn.write(('' + '\n').encode('ascii'))


	tn.read_until(("login: ").encode('ascii'),timeout=5)

	tn.write(('admin' + '\n').encode('ascii'))

	tn.read_until(("Password: ").encode('ascii'),timeout=5)

	#tn.write(('' + '\n').encode('ascii'))
	tn.write((pwd + '\n').encode('ascii'))

	#tprint("before the hash sign\n")
	tn.read_until(("# ").encode('ascii'),timeout=5)

	tn.write(('' + '\n').encode('ascii'))
	sleep(1)
	tn.write(('' + '\n').encode('ascii'))
	sleep(1)
	tn.write(('' + '\n').encode('ascii'))
	sleep(1)
	if switch_need_change_password(tn) == True:
		tprint("Password is changed to *fortinet123*. Done")
		return tn
	if switch_find_login_prompt(tn) == True:
		tn.read_until(("login: ").encode('ascii'),timeout=10)
		tn.write(('admin' + '\n').encode('ascii'))
		tn.read_until(("Password: ").encode('ascii'),timeout=10)
		tn.write(('fortinet123' + '\n').encode('ascii'))
		sleep(1)
		tn.read_until(("# ").encode('ascii'),timeout=10)

	#tprint("successful login\n")

	# tn.write(('get system status\n').encode('ascii'))
	# tn.read_until(("# ").encode('ascii'),timeout=10)
	switch_configure_cmd(tn,'config system global')
	switch_configure_cmd(tn,'set admintimeout 480')
	switch_configure_cmd(tn,'end')
	tprint("get_switch_telnet_connection: Login sucessful!\n")
	return tn

def relogin_new(tn,*args,**kwargs):
	if "password" in kwargs:
		password = kwargs['password']
	else:
		password = "fortinet123"

	if settings.TELNET:
		try:
			tn.write(('' + '\n').encode('ascii'))
			sleep(2)
			tn.write(('' + '\n').encode('ascii'))
			sleep(2)
			tn.write(('' + '\n').encode('ascii'))
			sleep(2)
			tn.write(('' + '\n').encode('ascii'))
			sleep(2)
			tn.write(('' + '\n').encode('ascii'))
			sleep(2)
		except BrokenPipeError:
			return False

	if switch_find_login_prompt(tn) == True:
		# tn.read_until(("login: ").encode('ascii'),timeout=10)
		tn.write(('admin' + '\n').encode('ascii'))
		tn.read_until(("Password: ").encode('ascii'),timeout=10)
		tn.write((password + '\n').encode('ascii'))
		sleep(1)
		tn.read_until(("# ").encode('ascii'),timeout=10)
		switch_configure_cmd(tn,'config system global',mode="silent")
		switch_configure_cmd(tn,'set admintimeout 480',mode="silent")
		switch_configure_cmd(tn,'end',mode="silent")
		return True
	else:
		switch_configure_cmd(tn,'config system global',mode='silent')
		switch_configure_cmd(tn,'set admintimeout 480',mode='silent')
		switch_configure_cmd(tn,'end',mode='silent')
		return 

def relogin_if_needed(tn):
	if settings.TELNET:
		try:
			tn.write(('' + '\n').encode('ascii'))
			sleep(2)
			tn.write(('' + '\n').encode('ascii'))
			sleep(2)
			tn.write(('' + '\n').encode('ascii'))
			sleep(2)
			tn.write(('' + '\n').encode('ascii'))
			sleep(2)
			tn.write(('' + '\n').encode('ascii'))
			sleep(2)
		except BrokenPipeError:
			return False

	if switch_find_login_prompt(tn) == True:
		switch_login(tn,mode='silent')
		return True
	else:
		switch_configure_cmd(tn,'config system global',mode='silent')
		switch_configure_cmd(tn,'set admintimeout 480',mode='silent')
		switch_configure_cmd(tn,'end',mode='silent')
		return 
		
def switch_need_change_password(tn):
	TIMEOUT = 2
	# tn.write(('' + '\n').encode('ascii'))
	# time.sleep(1)

	# tn.write(('\x03').encode('ascii'))
	# time.sleep(1)
	# tn.write(('\x03').encode('ascii'))
	# time.sleep(1)
	# tn.write(('\x03').encode('ascii'))
	# time.sleep(1)
	debug("See what prompt the console is at")
	output = tn.expect([re.compile(b"New Password:")],timeout=TIMEOUT)
	debug(output[2].decode().strip())
	if output[0] < 0: 
		debug("It is a NOT a new switch that needs to change password")
		return False
	else:
		debug("it is a new switch that needs to change password, change password to *fortinet123* ")
		tn.write(('fortinet123' + '\n').encode('ascii'))
		tn.write(('fortinet123' + '\n').encode('ascii'))
		return True

def find_shell_prompt(tn,chassis_id):
	TIMEOUT = 5
	out = tn.expect([re.compile(b"#")],timeout=TIMEOUT)
	print(f"after enter password, device prompt overall prompt = {out}")
	login_result = out[0]
	device_prompt = out[2].decode().strip()
	print(f"Expecting # prompt, if return 0, # is found. return = {login_result},device prompt ={device_prompt}")
	if int(login_result) == 0 and chassis_id in device_prompt:
		print("login successful")
		return True
	else:
		return False

def enter_console_cmd(tn,cmd):
	tn.write((cmd + '\n').encode('ascii'))
	gabage = tn.read_very_eager()
	dprint(gabage)

def fgt_ssh_chassis(tn,ip,chassis_id,*args,**kwargs):
	TIMEOUT = 30
	if "more_cmd" in kwargs:
		more_cmd = kwargs['more_cmd']
	else:
		more_cmd = False
	gabage = tn.read_very_eager()
	cmd = f"exec ssh admin@{ip}" 
	tn.write((cmd + '\n').encode('ascii'))
	output = tn.expect([re.compile(b"password:"),re.compile(b"yes/no"),re.compile(b"The remote host key has changed")],timeout=TIMEOUT)
	dprint(output)
	#prompt = output[2].decode().strip()
	prompt = output[2].decode().strip()
	#print(prompt)
	#dprint(f"After entering the {cmd} command, the fortigate prompt = {prompt},type of prompt = {type(prompt)}")
	result = output[0]
	if result == 0: #this is password: prompt
		tn.write(('Fortinet123!' + '\n').encode('ascii'))
		out = tn.expect([re.compile(b"#")],timeout=TIMEOUT)
		dprint(f"after enter password, device prompt overall prompt = {out}")
		login_result = out[0]
		device_prompt = out[2].decode().strip()
		dprint(f"after entering password, login_result = {login_result},device prompt ={device_prompt}")
		if int(login_result) == 0 and chassis_id in device_prompt:
			tprint("login successful")
			if more_cmd == False:
				enter_console_cmd(tn,"exit")
			return True
	elif "#" in prompt:
		if chassis_id in prompt:
			return True
	elif result == 2 or result == 1: #this is yes/no prompt, headache
		first_time_after_upgrade_prompt = """
		Connected
 
		exec ssh admin@169.254.1.4
		FortiGate-3960E # exec ssh admin@169.254.1.4
		@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
		@    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @
		@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
		IT IS POSSIBLE THAT SOMEONE IS DOING SOMETHING NASTY!
		Someone could be eavesdropping on you right now (man-in-the-middle attack)!
		It is also possible that a host key has just been changed.
		The fingerprint for the ED25519 key sent by the remote host is
		SHA256:c7yDVxDblBbigD59G176xbR418eKCIhtNeFiNKrtXcE.
		Please contact your system administrator.
		Add correct host key in /tmp/home/admin/.ssh/known_hosts to get rid of this message.
		Offending ED25519 key in /tmp/home/admin/.ssh/known_hosts:3
		 
		The remote host key has changed. Do you want to accept the new key and continue connecting (yes/no)?  
		"""
		dprint(f"yes/no was found in the prompt, the prompt = {prompt}")
		tn.write(('yes' + '\n').encode('ascii'))
		tn.write(('Fortinet123!' + '\n').encode('ascii'))
		if find_shell_prompt(tn,chassis_id):
			return True
		else:
			return False
	else:
		ErrorNotify(f"Not able to login switch {chassis_id} with ip {ip} via fortigate .....")
		ErrorNotify(output)
		return False


def increment_32(ip,num):
	bytes = ip.split('.')
	ibytes = [int(i) for i in bytes]
	newip_list = [ip]
	for i in range(num-1):
		ibytes[3] += 1
		if ibytes[3] > 255:
			ibytes[2] += 1
			ibytes[3] = 0
			if ibytes[2] > 255:
				ibytes[1]+= 1
				ibytes[2] = 0
				if ibytes[1] > 255:
					ibytes[0]+= 1
					ibytes[1] = 0
					if ibytes[0] > 224:
						print("The range is too big for IPv4")
						return newip_list
		newip = ".".join(str(i) for i in ibytes)
		newip_list.append(newip)
	print(newip_list)
	return newip_list


def increment_24(ip,num):
	bytes = ip.split('.')
	ibytes = [int(i) for i in bytes]
	newip_list = [ip]
	for i in range(num-1):
		ibytes[2] += 1
		if ibytes[2] > 255:
			ibytes[1] += 1
			ibytes[2] = 0
			if ibytes[1] > 255:
				ibytes[0]+= 1
				ibytes[1] = 0
				if ibytes[0] > 224:
					print("The range is too big for IPv4")
					return newip_list
		newip = ".".join(str(i) for i in ibytes)
		newip_list.append(newip)
	print(newip_list)
	return newip_list

def handle_prompt_before_commands(tn,*args,**kwargs):
	Info("Before entering commands into device, find out what prompt the device is at")
	password = "Fortinet123!"
	tn.write(('' + '\n').encode('ascii'))
	sleep(0.5)
	tn.write(('' + '\n').encode('ascii'))
	sleep(0.5)
	tn.write(('' + '\n').encode('ascii'))
	sleep(0.5)
	tn.write(('' + '\n').encode('ascii'))
	sleep(0.5)
	tn.write(('' + '\n').encode('ascii'))
	sleep(0.5)
	tn.write(('' + '\n').encode('ascii'))
	sleep(0.5)
	TIMEOUT = 3
	Info("See what prompt the console is at")
	output = tn.expect([re.compile(b"login:")],timeout=TIMEOUT)
	Info(f"collect info to look for prompt: {output}")
	Info(f"output[2] = {output[2].decode().strip()}")
	#debug(output[2].decode().strip())
	prompt = output[2].decode().strip()
	if output[0] == 0:
		Info("it is a login prompt, you need to re-login because of timeout or reboot")
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		sleep(1)
		tn.read_until(("login: ").encode('ascii'),timeout=10)
		tn.write(('admin' + '\n').encode('ascii'))           # this would not work for factory reset scenario
		tn.read_until(("Password: ").encode('ascii'),timeout=10)
		tn.write((password + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		tn.write(('' + '\n').encode('ascii'))
		sleep(0.2)
		tn.read_until(("# ").encode('ascii'),timeout=10)
		return ("re-login",None)
	elif " #" in prompt or "#" in prompt: # be careful of with and without space at the front
		Info("it is a Shell prompt")
		pattern = r"[a-zA-Z0-9\-]+"
		match = re.match(pattern,prompt)
		if match:
			result = match.group()
		else:
			result = None
		return ("shell",result)
	else:
		debug("can not get any prompt, need to use robust login procedure...")
		return (None,None)


def switch_find_login_prompt_new(tn,*args,**kwargs):
	if "password" in kwargs:
		pwd = kwargs['password']
	else:
		pwd = 'fortinet123'
	TIMEOUT = 3
	# tn.write(('' + '\n').encode('ascii'))
	#time.sleep(1)

	# tn.write(('\x03').encode('ascii'))
	# time.sleep(1)

	tn.write(('\x03').encode('ascii'))
	time.sleep(2)
	tn.write(('\x03').encode('ascii'))
	time.sleep(2)

	tn.read_until(("login: ").encode('ascii'),timeout=5)

	tn.write(('admin' + '\n').encode('ascii'))

	tn.read_until(("Password: ").encode('ascii'),timeout=5)

	tn.write(('' + '\n').encode('ascii'))
	tn.write(('' + '\n').encode('ascii'))
	tn.write(('' + '\n').encode('ascii'))

	debug("See what prompt the console is at")
	output = tn.expect([re.compile(b"login:")],timeout=TIMEOUT)
	debug(f"collect info to look for prompt: {output}")
	debug(f"output[2] = {output[2].decode().strip()}")
	#debug(output[2].decode().strip())
	prompt = output[2].decode().strip()
	if 'please change your password!' in prompt:
		debug (f"The switch could be factory reset and need change password")
		return ("change",None)
	if 'Login incorrect' in prompt:
		debug (f"It is a login prompt,need to login")
		return ("login",None)
	if output[0] == -1: 
		debug("It is a NOT login prompt, Need further action to login, going through more logics......")
	if output[0] == 0:
		debug("it is a login prompt, you need to re-login")
		return ("login",None)
	elif " #" in prompt or "#" in prompt: 
		debug("it is a Shell prompt")
		pattern = r"[a-zA-Z0-9\-]+"
		match = re.match(pattern,prompt)
		if match:
			result = match.group()
		else:
			result = None
		return ("shell",result)
	elif "New Password:"in prompt:
		debug(f"it is a new switch that needs to change password, change password to {pwd} ")
		tn.write((pwd + '\n').encode('ascii'))
		tn.write((pwd + '\n').encode('ascii'))
		return ("new",None)
	else:
		debug("can not get any prompt, need to use robust login procedure...")
		return (None,None)

def switch_find_login_prompt(tn):
	TIMEOUT = 4
	# tn.write(('\x03').encode('ascii'))
	# tn.write(('\x03').encode('ascii'))
	tn.write(('\x03').encode('ascii'))
	time.sleep(2)
	tn.write(('' + '\n').encode('ascii'))
	time.sleep(1)
	tn.write(('' + '\n').encode('ascii'))
	time.sleep(1)
	tn.write(('' + '\n').encode('ascii'))
	time.sleep(1)
	tn.write(('' + '\n').encode('ascii'))
	time.sleep(1)
	#time.sleep(1)
	
	debug("See what prompt the console is at")
	output = tn.expect([re.compile(b"login:")],timeout=TIMEOUT)
	debug(output[2].decode().strip())
	if output[0] < 0: 
		debug("It is a NOT login prompt, don't have to relogin")
		return False
	else:
		debug("it is a login prompt, you need to re-login")
		return True
	 

def switch_find_shell_prompt(tn):
	TIMEOUT = 10
	tn.write(('' + '\n').encode('ascii'))
	time.sleep(1)

	tn.write(('\x03').encode('ascii'))
	time.sleep(2)
	tn.write(('\x03').encode('ascii'))
	time.sleep(2)
	tn.write(('\x03').encode('ascii'))
	time.sleep(2)
	debug("See what prompt the console is at")
	output = tn.expect([re.compile(b"#")],timeout=TIMEOUT)
	debug(output)
	if output[0] < 0: 
		debug("It is a NOT login prompt")
		return False
	else:
		debug("it is a login prompt")
		return True

def dict_lacp_boot_update(**kwargs):
    #dict_lacp_boot_update(dir_list=stat_dir_list,dut="dut1",mem=8,result=boot_result)
	tkwargs = {}
	for key, value in kwargs.items():
		tkwargs[key]=value
	debug(tkwargs)
	statlist = tkwargs["dir_list"] 
	dut = tkwargs["dut_name"] 
	mem = tkwargs["mem"]
	bootstats = tkwargs["result"]
	test = 0
	debug("!!!!!! print boot testing statistics here")
	debug(bootstats)
	for blist in bootstats:
		test+=1
		for b in blist:
			for lacp in statlist:
				if lacp["member"] == mem and lacp["test"] == test:
					working_lacp = lacp
					break
			reason = b["reason"]
			if b["tx_port"] == "1/1/2":
				host = "host2"
			elif b["tx_port"] == "1/1/1":
				host = "host1"
			else:
				ErrorHandler('Error identifying TX port', b)
			pkt_loss = b['loss_pkts'] 
			loss_time = b["loss_time"]
			try:
				tier = b["tier"]
			except Exception as e:
				tier = 0

			if tier == 1 and reason=="1st-down" and host=="host1":
				working_lacp["E4"] = pkt_loss
				working_lacp["F4"] = loss_time
			if tier == 1 and reason=="1st-down" and host=="host2":
				working_lacp["E5"] = pkt_loss
				working_lacp["F5"] = loss_time
			if tier == 1 and reason=="2nd-down" and host=="host1":
				working_lacp["E7"] = pkt_loss
				working_lacp["F7"] = loss_time
			if tier == 1 and reason=="2nd-down" and host=="host2":
				working_lacp["E8"] = pkt_loss
				working_lacp["F8"] = loss_time
			if tier == 1 and reason=="2nd-up" and host=="host1":
				working_lacp["E10"] = pkt_loss
				working_lacp["F10"] = loss_time
			if tier == 1 and reason=="2nd-up" and host=="host2":
				working_lacp["E11"] = pkt_loss
				working_lacp["F11"] = loss_time
			if tier == 1 and reason=="1st-up" and host=="host1":
				working_lacp["E13"] = pkt_loss
				working_lacp["F13"] = loss_time
			if tier == 1 and reason=="1st-up" and host=="host2":
				working_lacp["E14"] = pkt_loss
				working_lacp["F14"] = loss_time

			if tier == 2 and reason=="1st-down" and host=="host1":
				working_lacp["E16"] = pkt_loss
				working_lacp["F16"] = loss_time
			if tier == 2 and reason=="1st-down" and host=="host2":
				working_lacp["E17"] = pkt_loss
				working_lacp["F17"] = loss_time
			if tier == 2 and reason=="2nd-down" and host=="host1":
				working_lacp["E19"] = pkt_loss
				working_lacp["F19"] = loss_time
			if tier == 2 and reason=="2nd-down" and host=="host2":
				working_lacp["E20"] = pkt_loss
				working_lacp["F20"] = loss_time
			if tier == 2 and reason=="2nd-up" and host=="host1":
				working_lacp["E22"] = pkt_loss
				working_lacp["F22"] = loss_time
			if tier == 2 and reason=="2nd-up" and host=="host2":
				working_lacp["E23"] = pkt_loss
				working_lacp["F23"] = loss_time
			if tier == 2 and reason=="1st-up" and host=="host1":
				working_lacp["E25"] = pkt_loss
				working_lacp["F25"] = loss_time
			if tier == 2 and reason=="1st-up" and host=="host2":
				working_lacp["E26"] = pkt_loss
				working_lacp["F26"] = loss_time

			if dut=="dut1" and host == "host1" and reason == "down":
				working_lacp["E28"] = pkt_loss
				working_lacp["F28"] = loss_time
			elif dut=="dut1" and host == "host2" and reason == "down":
				working_lacp["E29"] = pkt_loss
				working_lacp["F29"] = loss_time
			elif dut=="dut2" and host == "host1" and reason == "down":
				working_lacp["E30"] = pkt_loss
				working_lacp["F30"] = loss_time
			elif dut=="dut2" and host == "host2" and reason == "down":
				working_lacp["E31"] = pkt_loss	
				working_lacp["F31"] = loss_time

			elif dut=="dut1" and host == "host1" and reason == "up":
				working_lacp["E33"] = pkt_loss
				working_lacp["F33"] = loss_time
			elif dut=="dut1" and host == "host2" and reason == "up":
				working_lacp["E34"] = pkt_loss	
				working_lacp["F34"] = loss_time	
			elif dut=="dut2" and host == "host1" and reason == "up":
				working_lacp["E35"] = pkt_loss
				working_lacp["F35"] = loss_time
			elif dut=="dut2" and host == "host2" and reason == "up":
				working_lacp["E36"] = pkt_loss
				working_lacp["F36"] = loss_time

			elif dut=="dut3" and host == "host1" and reason == "down":
				working_lacp["E38"] = pkt_loss
				working_lacp["F38"] = loss_time
			elif dut=="dut3" and host == "host2" and reason == "down":
				working_lacp["E39"] = pkt_loss
				working_lacp["F39"] = loss_time
			elif dut=="dut4" and host == "host1" and reason == "down":
				working_lacp["E40"] = pkt_loss
				working_lacp["F40"] = loss_time
			elif dut=="dut4" and host == "host2" and reason == "down":
				working_lacp["E41"] = pkt_loss
				working_lacp["F41"] = loss_time

			elif dut=="dut3" and host == "host1" and reason == "up":
				working_lacp["E43"] = pkt_loss
				working_lacp["F43"] = loss_time
			elif dut=="dut3" and host == "host2" and reason == "up":
				working_lacp["E44"] = pkt_loss
				working_lacp["F44"] = loss_time
			elif dut=="dut4" and host == "host1" and reason == "up":
				working_lacp["E45"] = pkt_loss
				working_lacp["F45"] = loss_time
			elif dut=="dut4" and host == "host2" and reason == "up":
				working_lacp["E46"] = pkt_loss
				working_lacp["F46"] = loss_time

def create_excel_sheets(stat_dir_list,image,**kwargs):
	runtime = kwargs["runtime"]
	mem = kwargs["mem"]
	for i in range(1,runtime+1):
		d = dict_lacp_blank(mem,image)
		d["test"] = i
		d['B4'] = "Test {}".format(i)
		d["sheetname"] = "LACP-{} Test{}".format(mem,i)
		stat_dir_list.append(d)

def dict_lacp_blank(member,image,**kwargs):
	if "runtime" in kwargs:
		runtime = kwargs["runtime"]
	else:
		runtime = 2
	lacp = {}
	lacp['member'] = member
	if member ==2: 
		lacp['B1:F1'] = "2-member LACP trunk"
	else:
		lacp['B1:F1'] = "8-member LACP trunk"
	lacp['B2:F2'] = image
	lacp['B3'] = "No."
	lacp['C3'] = "Action"
	lacp['D3:E3'] = "Frame Loss"
	lacp['F3'] = "Loss Time Sec"
	lacp['B4'] = "Test #"

	lacp['C4'] = "Tier-1:un-plug 1st active link"
	lacp['D4'] = "host1"
	lacp['D5'] = "host2"

	if member == 2:
		lacp['C7'] = "Tier-1: un-plug 2nd active link"
	elif member == 8:
		lacp['C7'] = "Tier-1: un-plug 3~4 active link"
	lacp['D7'] = "host1"
	lacp['D8'] = "host2"

	if member == 2:
		lacp['C10'] = "Tier-1: re-connect 2nd link"
	elif member == 8:
		lacp['C10'] = "Tier-1: re-connect 3~4 link"
	lacp['D10'] = "host1"
	lacp['D11'] = "host2"
	
	lacp['C13'] = "Tier-1: re-connect 1st active link"
	lacp['D13'] = "host1"
	lacp['D14'] = "host2"

	##########Tier 2 unplug rows
	lacp['C16'] = "Tier-2:un-plug 1st active link"
	lacp['D16'] = "host1"
	lacp['D17'] = "host2"

	if member == 2:
		lacp['C19'] = "Tier-2: un-plug 2nd active link"
	elif member == 8:
		lacp['C19'] = "Tier-2: un-plug 3~4 active link"
	lacp['D19'] = "host1"
	lacp['D20'] = "host2"

	if member == 2:
		lacp['C22'] = "Tier-2: re-connect 2nd link"
	elif member == 8:
		lacp['C22'] = "Tier-2: re-connect 3~4 link"
	lacp['D22'] = "host1"
	lacp['D23'] = "host2"
	
	lacp['C25'] = "Tier-2: re-connect 1st active link"
	lacp['D25'] = "host1"
	lacp['D26'] = "host2"


	# boot rows
	lacp['C28'] = "Tier-1 DUT1 Down"
	lacp['D28'] = "host1"
	lacp['D29'] = "host2"
	lacp['C30'] = "Tier-1 DUT2 Down"
	lacp['D30'] = "host1"
	lacp['D31'] = "host2"

	lacp['C33'] = "Tier-1 DUT1 Up"
	lacp['D33'] = "host1"
	lacp['D34'] = "host2"
	lacp['C35'] = "Tier-1 DUT2 Up"
	lacp['D35'] = "host1"
	lacp['D36'] = "host2"

	lacp['C38'] = "Tier-2 DUT3 Down"
	lacp['D38'] = "host1"
	lacp['D39'] = "host2"
	lacp['C40'] = "Tier-2 DUT4 Down"
	lacp['D40'] = "host1"
	lacp['D41'] = "host2"

	lacp['C43'] = "Tier-2 DUT3 Up"
	lacp['D43'] = "host1"
	lacp['D44'] = "host2"
	lacp['C45'] = "Tier-2 DUT4 Up"
	lacp['D45'] = "host1"
	lacp['D46'] = "host2"

	return lacp

def dict_2_excel(dict_list,filename):
	filePath = filename
	if os.path.exists(filePath):
	    os.remove(filePath)
	else:
	    tprint("Can not delete the file as it doesn't exists: {}".format(filePath))

	workbook = xlsxwriter.Workbook(filename)
	highlight_format = workbook.add_format({
    'bold': 1,
    'border': 1,
    'align': 'center',
    'valign': 'vcenter',
    'fg_color': 'yellow'})

	merge_format_table = workbook.add_format({
	'bold': 0,
	'border': 1,
	'align': 'center',
	'valign': 'vcenter'})

	merge_format_title = workbook.add_format({
	'bold': 1,
	'border': 1,
	'align': 'left',
	'valign': 'vcenter'})

	format_title = workbook.add_format({
	'bold': 1,
	'border': 1,
	'align': 'left',
	'valign': 'vcenter'})

	full_border = workbook.add_format({"border":1})
	
	for stat in dict_list:
		sheetname = stat["sheetname"]
		stat.pop("sheetname")
		stat.pop("member")
		stat.pop("test")
		worksheet = workbook.add_worksheet(sheetname)
		worksheet.set_column("C:C", 30)
		worksheet.set_column("D:E", 15)
		worksheet.set_column("F:F", 25)
		worksheet.conditional_format('B4:F46', {'type':'blanks', 'format': full_border})
		for key, value in stat.items():
			if ":" in key: 
				worksheet.merge_range(key,value,merge_format_title)
			elif key=="C3" or key=="B3" or key=="F3":
				worksheet.write(key,value,format_title)
			else:
				worksheet.write(key,value,full_border)
	
	workbook.close()		 

def exel_2_member_lacp_blank(filename,sheetname,title,build,test_num):

	workbook = xlsxwriter.Workbook(filename)
	worksheet = workbook.add_worksheet(sheetname)
	#worksheet.write(0,0,"6.2.0 Interim Build 168")
	#worksheet.conditional_format( 'B4:F26' , { 'type' : 'no_blanks' , 'format' : border_format} )

	worksheet.set_landscape()
	worksheet.set_paper(8)
	worksheet.set_margins(0.787402, 0.787402, 0.5, 0.787402)

	apply_border_to_range(
		workbook,
		worksheet,
		{
			"range_string": "B2:F26",
			"border_style": 5,
		},
	)

	highlight_format = workbook.add_format({
    'bold': 1,
    'border': 1,
    'align': 'center',
    'valign': 'vcenter',
    'fg_color': 'yellow'})

	merge_format_table = workbook.add_format({
	'bold': 0,
	'border': 1,
	'align': 'center',
	'valign': 'vcenter'})

	merge_format_title = workbook.add_format({
	'bold': 1,
	'border': 1,
	'align': 'left',
	'valign': 'vcenter'})

	full_border = workbook.add_format({"border":1})
	
	# for i in range(3,27):
	# 	for j in range(1,6):
	# 		worksheet.write(i,j,blank,full_border)
			
	worksheet.merge_range('B1:H1',title,merge_format_title)
	worksheet.merge_range('B2:F2',build,merge_format_table)
	worksheet.merge_range('D3:E3',"Frame Loss",merge_format_table)
	worksheet.conditional_format('B4:F26', {'type':'blanks', 'format': full_border})
	worksheet.write(2,1,"No.",full_border)
	worksheet.write(2,2,"Action",full_border)
	
	worksheet.write(2,5,"Loss Time Sec",full_border )
	worksheet.write(3,1,test_num,full_border)
	worksheet.write(3,2,"un-plug 1st active link",full_border)
	worksheet.write(3,3,"host1",full_border)
	worksheet.write(4,3,"host2",full_border)

	worksheet.write(6,2,"un-plug 2nd active link",full_border)
	worksheet.write(6,3,"host1",full_border)
	worksheet.write(7,3,"host2",full_border)

	worksheet.write(9,2,"re-connect 2nd link",full_border)
	worksheet.write(9,3,"host1",full_border)
	worksheet.write(10,3,"host2",full_border)

	worksheet.write(12,2,"re-connect 1st link",full_border)
	worksheet.write(12,3,"host1",full_border)
	worksheet.write(13,3,"host2",full_border)

	worksheet.write(15,2,"Tier-1 DUT2 Down",full_border)
	worksheet.write(15,3,"host1",full_border)
	worksheet.write(16,2,"Tier-1 DUT1  Down",full_border)
	worksheet.write(16,3,"host2",full_border)

	worksheet.write(18,2,"Tier-1 DUT2 Up",full_border)
	worksheet.write(18,3,"host1",full_border)
	worksheet.write(19,2,"Tier-1 DUT1  Up",full_border)
	worksheet.write(19,3,"host2",full_border)

	worksheet.write(21,2,"Tier-2 DUT3 Down",full_border)
	worksheet.write(21,3,"host1",full_border)
	worksheet.write(22,2,"Tier-2 DUT4 Down",full_border)
	worksheet.write(22,3,"host2",full_border)

	worksheet.write(24,2,"Tier-2 DUT3 Up",full_border)
	worksheet.write(24,3,"host1",full_border)
	worksheet.write(25,2,"Tier-2 DUT4 Up",full_border)
	worksheet.write(25,3,"host2",full_border)

	workbook.close()

def exel_8_member_lacp_blank(filename,sheetname,title,build,test_num):

	workbook = xlsxwriter.Workbook(filename)
	worksheet = workbook.add_worksheet(sheetname)
	#worksheet.write(0,0,"6.2.0 Interim Build 168")
	#worksheet.conditional_format( 'B4:F26' , { 'type' : 'no_blanks' , 'format' : border_format} )

	worksheet.set_landscape()
	worksheet.set_paper(8)
	worksheet.set_margins(0.787402, 0.787402, 0.5, 0.787402)

	apply_border_to_range(
		workbook,
		worksheet,
		{
			"range_string": "B2:F26",
			"border_style": 5,
		},
	)

	highlight_format = workbook.add_format({
    'bold': 1,
    'border': 1,
    'align': 'center',
    'valign': 'vcenter',
    'fg_color': 'yellow'})

	merge_format_table = workbook.add_format({
	'bold': 0,
	'border': 1,
	'align': 'center',
	'valign': 'vcenter'})

	merge_format_title = workbook.add_format({
	'bold': 1,
	'border': 1,
	'align': 'left',
	'valign': 'vcenter'})

	full_border = workbook.add_format({"border":1})
	
	# for i in range(3,27):
	# 	for j in range(1,6):
	# 		worksheet.write(i,j,blank,full_border)
			
	worksheet.merge_range('B1:H1',title,merge_format_title)
	worksheet.merge_range('B2:F2',build,merge_format_table)
	worksheet.merge_range('D3:E3',"Frame Loss",merge_format_table)
	worksheet.conditional_format('B4:F26', {'type':'blanks', 'format': full_border})
	worksheet.write(2,1,"No.",full_border)
	worksheet.write(2,2,"Action",full_border)
	
	worksheet.write(2,5,"Loss Time Sec",full_border )
	worksheet.write(3,1,test_num,full_border)
	worksheet.write(3,2,"un-plug 1st active link",full_border)
	worksheet.write(3,3,"host1",full_border)
	worksheet.write(4,3,"host2",full_border)

	worksheet.write(6,2,"un-plug 3~4 active link",full_border)
	worksheet.write(6,3,"host1",full_border)
	worksheet.write(7,3,"host2",full_border)

	worksheet.write(9,2,"re-connect 3~4 link",full_border)
	worksheet.write(9,3,"host1",full_border)
	worksheet.write(10,3,"host2",full_border)

	worksheet.write(12,2,"re-connect 1st link",full_border)
	worksheet.write(12,3,"host1",full_border)
	worksheet.write(13,3,"host2",full_border)

	worksheet.write(15,2,"Tier-1 DUT2 Down",full_border)
	worksheet.write(15,3,"host1",full_border)
	worksheet.write(16,2,"Tier-1 DUT1  Down",full_border)
	worksheet.write(16,3,"host2",full_border)

	worksheet.write(18,2,"Tier-1 DUT2 Up",full_border)
	worksheet.write(18,3,"host1",full_border)
	worksheet.write(19,2,"Tier-1 DUT1  Up",full_border)
	worksheet.write(19,3,"host2",full_border)

	worksheet.write(21,2,"Tier-2 DUT3 Down",full_border)
	worksheet.write(21,3,"host1",full_border)
	worksheet.write(22,2,"Tier-2 DUT4 Down",full_border)
	worksheet.write(22,3,"host2",full_border)

	worksheet.write(24,2,"Tier-2 DUT3 Up",full_border)
	worksheet.write(24,3,"host1",full_border)
	worksheet.write(25,2,"Tier-2 DUT4 Up",full_border)
	worksheet.write(25,3,"host2",full_border)
	workbook.close()

def parse_linerate(result):
	linerate = {}
	num = 0
	linerate_list = []
	port_traffic_list = []
	for line in result:
		if "port" in line:
			line_list = line.strip().split("|")
			#print(line_list)
			port_traffic = [i.strip() for i in line_list if i !=""]
			debug(port_traffic)
			#if port_traffic[0] not in linerate:
			linerate[port_traffic[0]] = {}
			linerate[port_traffic[0]]["TX"] = port_traffic[1]
			linerate[port_traffic[0]]["TX_Rate"] = float(port_traffic[2].strip("Mbps"))
			linerate[port_traffic[0]]["RX"] = port_traffic[3]
			linerate[port_traffic[0]]["RX_Rate"] = float(port_traffic[4].strip("Mbps"))
			 
	debug(linerate)
	return linerate 
		 
	 
def parse_mclag_list(result):
	mclag = {}
	found = 0
	for line in result:
		if "-----" not in line:
			temp = line
			if found == 1: 
				line_list = line.strip().split("     ")
				if len(line_list) >= 2:
					key = line_list[0]
					value = line_list[-1]
					#print(line_list)
					mclag[name][key.strip()] = value.strip()
		else:
			name = temp.strip()
			mclag[name] = {}
			found = 1
	return mclag

def find_active_trunk_port(dut):
	result = collect_show_cmd(dut,"diag switch mclag list")
	mclag = parse_mclag_list(result)
	for k, v in mclag.items():
		if "core" in k or "FlInK1_MLAG" in k:
			if "-" in mclag[k]['Local ports']:
				start,finish = mclag[k]['Local ports'].split('-')
				start = int(start)
				finish = int(finish)
				core_ports = ["port"+ str(i) for i in range(start,finish+1)]
			else:
				core_ports = mclag[k]['Local ports'].split(',')
				try:
					debug("core_ports after split format like 2,4: {}".format(core_ports))
				except Exception as e:
					debug("find_active_trunk_port: not able to print valuable: core_ports")
				core_ports = ["port"+ p for p in core_ports]
	debug(mclag)
	debug(core_ports)
	 
	result = collect_show_cmd(dut,"diag switch physical linerate up")
	send_ctrl_c_cmd(dut)
	debug(result) 
	#print(result)
	TEST_RATE = 300
	linerate = parse_linerate(result)
	for p in core_ports:
		if p in linerate:
			if linerate[p]["TX_Rate"] > TEST_RATE or linerate[p]["RX_Rate"] > TEST_RATE:
				Info("On this switch, {} is active".format(p))
				return p
	return None

def loop_command_output(dut,cmd,**kwargs):
	if "timeout" in kwargs:
		timeout = kwargs['timeout']
	else:
		timeout = 3
	result = collect_show_cmd(dut,cmd,t=timeout)
	#print_show_cmd(dut,cmd,t=timeout)
	send_ctrl_c_cmd(dut)
	return (result)

def seperate_ip_mask(ip_addr):
	if ":" in ip_addr:
		regex = r'([0-9a-fA-F:]+)\/([0-9]+)'
		matched = re.search(regex,ip_addr)
		if matched:
			ip = matched.group(1)
			net = matched.group(2)
			return ip,net
		return None,None
	else:
		regex = r'([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\/([0-9]+)'
		regex = r'([0-9.]+[0-9]+)\/([0-9]+)'
		matched = re.search(regex,ip_addr)
		if matched:
			ip = matched.group(1)
			net = matched.group(2)
			return ip,net
		return None,None

def find_inactive_trunk_port(dut):
	# print("========================= find_inactive_trunk port")
	result = collect_show_cmd(dut,"diag switch mclag list")
	mclag = parse_mclag_list(result)
	# print(mclag)
	for k, v in mclag.items():
		if "core" in k or "FlInK1_MLAG" in k:
			if "-" in mclag[k]['Local ports']:
				start,finish = mclag[k]['Local ports'].split('-')
				start = int(start)
				finish = int(finish)
				core_ports = ["port"+ str(i) for i in range(start,finish+1)]
			else:
				core_ports = mclag[k]['Local ports'].split(',')
				debug("core_ports after split ,".format(core_ports))
				core_ports = ["port"+ p for p in core_ports]
	debug(mclag)
	debug(core_ports)
	 
	result = collect_show_cmd(dut,"diag switch physical linerate up")
	send_ctrl_c_cmd(dut)
	# for line in result:
	# 	print(line)
	 
	TEST_RATE = 20
	linerate = parse_linerate(result)
	inactive_ports = []
	for p in core_ports:
		if p in linerate:
			if linerate[p]["TX_Rate"] < TEST_RATE and linerate[p]["RX_Rate"] < TEST_RATE:
				Info("On this switch, {} is INactive".format(p))
				inactive_ports.append(p)

	return inactive_ports

	
	#mclag_list = parse_mclag_list(result)
def find_dut_model(dut):
	result = collect_show_cmd(dut,"get system status",t=5)
	dprint(result)
	for line in result:
		if "Version" in line:
			image = line.split(":")[1]
			matched = re.search(r'(.+)v.+',image)
			if matched:
				return matched.group(1)
	return None

def find_dut_image(dut):
	result = collect_show_cmd(dut,"get system status",t=5,mode='fast')
	dprint(result)
	for line in result:
		if "Version" in line:
			image = line.split(":")[1]
			matched = re.search(r'v.+',image)
			if matched:
				return matched.group()
	return None

def find_dut_build(dut,*args,**kwargs):
	if "platform" in kwargs:
		platform = kwargs['platform']
	else:
		platform = "fortinet"

	if platform == "fortinet":
		result = collect_show_cmd(dut,"get system status",t=5,mode='fast')
		dprint(result)
		for line in result:
			if "Version" in line:
				image = line.split(":")[1]
				matched = re.search(r'v(\d+\.\d+\.\d+),build(\d+)',image)
				if matched:
					return matched.group(1),matched.group(2)
		return None, None
	else:
		return None, None

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def test_ssh():
	HOST="10.105.50.59"
	HOST1="172.30.172.190"
	# Ports are handled in ~/.ssh/config since we use OpenSSH
	COMMAND="get system status"
	COMMAND="ls -al"

	shell = spur.SshShell(hostname=HOST1, username="mike.zheng2008", password="Shenghuo2014+")
	result = shell.run([COMMAND])
	print (result.output) # prints hello

	# ssh = subprocess.Popen(["ssh", "%s" % HOST, COMMAND],
	#                        shell=False,
	#                        stdout=subprocess.PIPE,
	#                        stderr=subprocess.PIPE)
	# result = ssh.stdout.readlines()
	# if result == []:
	#     error = ssh.stderr.readlines()
	#     eprint(error)
	# else:
	#     print (result)

def print_interactive_line():
	print("-------------------------------- Go to the lab to take action --------------------")

def print_dash_line():
	print("------------------------------------------------------------------------------------------------------")
def print_double_line():
	print("======================================================================================================")


def find_subnet(ipaddr,mask_length):
	import ipaddress
	n = f"{ipaddr}/{mask_length}"
	net = str(ipaddress.ip_network(n, strict=False))
	subnet = (net.split('/'))[0]
	print(subnet)
	return subnet

def print_test_subject(testcase,description):
	print(f"======================= Testcase #{testcase}: {description} =============================")

def smooth_cli_line(line):
	line = line.strip()
	debug(f'old line = {line}')
	if "More" in line:
		line = line.replace("--More--",'')
		line = line.replace("\r",'')
		line = line.strip()
	debug(f'new line = {line}')
	return line

def switch_factory_reset_relogin(dut_dir):
	dut = dut_dir['telnet']
	dut_com = dut_dir['comm'] 
	dut_port = dut_dir['comm_port']

	switch_interactive_exec(dut,"execute factoryreset","Do you want to continue? (y/n)") 
	console_timer(300,msg="Wait for 5 min after reset factory default")
	tprint('-------------------- re-login Fortigate devices after factory rest-----------------------')
	dut = get_switch_telnet_connection_new(dut_com,dut_port)
	dut_dir['telnet'] = dut

def switch_factory_reset_nologin(dut_dir):
	dut = dut_dir['telnet']
	dut_com = dut_dir['comm'] 
	dut_port = dut_dir['comm_port']
	dut_name = dut_dir['name']
	tprint(f":::::::::: Factory resetting {dut_name} :::::::::::")
	switch_interactive_exec(dut,"execute factoryreset","Do you want to continue? (y/n)") 


# if __name__ == "__main__":
# 	# reliable_telnet("10.105.50.59")
# 	# exit()
# 	# test_ssh()
# 	# exit()
# 	# scp_file(file="MCLAG_Perf_548D_no_mac_log.xlsx")
# 	# scp_file(file="MCLAG_Perf_548D_mac_log.xlsx")
# 	# exit()
# 	# debug("test debug")
# 	# exit()

# 	cisco_com = "10.105.241.243"
# 	cisco_port = 2045
# 	dut1_com = "10.105.241.144"
# 	dut1_port = 2071
# 	dut2_com = "10.105.241.243"
# 	dut2_port = 2035
# 	dut3_com = "10.105.240.144"
# 	dut3_port = 2070
# 	dut4_com = "10.105.50.1"
# 	dut4_port = 2078

# 	dut1_com_2 = "10.105.50.1"
# 	dut1_port_2 = 2074
# 	dut2_com_2 = "10.105.50.1"
# 	dut2_port_2 = 2081
# 	dut3_com_2 = "10.105.50.2"
# 	dut3_port_2 = 2077
# 	dut4_com_2 = "10.105.50.2"
# 	dut4_port_2 = 2078

# 	# dut1 = get_switch_telnet_connection(dut1_com,dut1_port)
# 	# tprint(dir(dut1))
# 	dut = get_switch_telnet_connection_new(dut3_com,dut3_port)
# 	ping_ipv4(dut,ip="10.1.1.1")
# 	ping_ipv6(dut,ip="2001:1:1:1::1")
# 	exit()
# 	dut = get_switch_telnet_connection_new(dut2_com,dut2_port)
# 	dut = get_switch_telnet_connection_new(dut1_com,dut1_port)
# 	find_dut_prompt(dut)
# 	exit()
# 	image = find_dut_image(dut)
# 	print(image)
# 	exit()
# 	switch_exec_reboot(dut1,device="DUT")
# 	# result = switch_show_cmd(dut,"diag switch physical linerate up")
# 	# tprint(result)
# 	settings.DEBUG = True
# 	prompt = switch_find_login_prompt_new(dut)
# 	print (prompt)
# 	exit()
# 	# port = find_active_trunk_port(dut)
# 	# print("active_port:{}".format(port))
# 	# port_list = find_inactive_trunk_port(dut)
# 	# print("inactive ports: {}".format(port_list))
# 	# image = find_dut_image(dut)
# 	# print("image running on this device: {}".format(image))
# 	# print("**********************")

# 	# dut = get_switch_telnet_connection(dut4_com_2,dut4_port_2)
# 	# port = find_active_trunk_port(dut)
# 	# print("active_port:{}".format(port))
# 	# port_list = find_inactive_trunk_port(dut)
# 	# print("inactive ports: {}".format(port_list))

# 	exit()
# 	tprint(dir(dut1))
# 	tprint(dut1.host)
# 	tprint("sleep 90 seconds for console to timeout")
# 	sleep(90)
# 	# dut2 = get_switch_telnet_connection(dut2_com,dut2_port)
# 	# dut3 = get_switch_telnet_connection(dut3_com,dut3_port)
# 	# dut4 = get_switch_telnet_connection(dut4_com,dut4_port)
# 	if switch_find_login_prompt(dut1) == True:
# 		switch_login(dut1)
# 	# result = switch_show_cmd(dut1,"show switch trunk")
# 	# result = switch_show_cmd(dut1,"diagnose switch mclag peer-consistency-check")
# 	# result = switch_show_cmd(dut1,"get switch lldp neighbors-summary")
# 	#tprint(result)
# 	#tprint(result)


if __name__ == "__main__":
# 	debug("test debug")
    poe_tester = telnet_poe("10.105.241.44", "2072")
    exit()
    pdu = telnet_apc("10.105.253.57")
    telnet_send_cmd(pdu,f"oloff 12")
    sleep(2)
    telnet_send_cmd(pdu,f"olon 12")
    sleep(2)
    exit()
    tn = telnet_apc("10.105.50.114")
    sequences = [1,2,1,9,1,3,"YES","\n"]
    for s in sequences:
        tprint(f"sending option {s}")
        # if s != "YES" and s !="\n":
        # 	tn.read_until(("> ").encode('ascii'),timeout=2)
        # if s == "YES":
        # 	tn.read_until((" : ").encode('ascii'),timeout=2)
        # if s == "\n":
        # 	tn.read_until(("...").encode('ascii'),timeout=2)
        telnet_send_cmd(tn,str(s))
        sleep(4)
    send_ctrl_c_cmd(tn)
    sleep(2)
    telnet_send_cmd(tn,"4")