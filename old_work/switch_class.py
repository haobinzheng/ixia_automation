#!/usr/local/bin/python
import time
import os
import select
from sys import stdout
from sys import stdin
from termios import VEOF, VINTR
import sys
import pexpect
import re
import csv
import fileinput
import termios
import pty
import tty
import fcntl
import struct
import resource
from types import *
from utility import *
from time import sleep


class switch():

   def __init__(self,switch_line): 
      self.ip,self.hostname,self.con,self.port,self.chassis = switch_line.split()
      self.original_config_file = self.hostname + '.config'
      self.processed_config_file = self.hostname + '_processed.config'
      self.prompt = self.hostname + '> ' 
      self.prompt2 = self.hostname + '\*' + '> ' 
      self.prompt3 = self.hostname + ' ' + 'login:'

   def display_switch(self):
      print('display IP address = %s' % self.ip) 
      print('display hostname = %s ' % self.hostname) 
      print('display console server IP = %s' % self.con)
      print('display console port of the switch = %s' %self.port)
      print('display vty prompt =%s ' % self.prompt)
      print('display vty prompt2 =%s ' % self.prompt2)


class cienaswitch_con():
   def __init__(self,router):
      self.prompt = router.prompt
      self.prompt2 = router.prompt2
      self.prompt3 = router.prompt3
      self.ip = router.ip
      self.console  = 'telnet' + ' ' + router.con + ' ' + router.port 
      self.host = router.hostname
      self.vc_list =[]
      self.bfd_list = []
      self.vcnh_list =[]
      self.vc_db = ""
      self.child = pexpect.spawn (self.console)
      self.child.timeout = 100000
      self.child.maxread = 100000000
      #self.child.logfile_send = sys.stdout
      self.child.logfile_read = sys.stdout
      self.child.sendline('\n')
      #self.child.expect([self.prompt, self.prompt2])
      i = self.child.expect([self.prompt2, self.prompt,self.prompt3])
      #i = self.child.expect(self.prompt)
      if i == 0 or i == 1:
         pass
      else:
        print("no prompt has been expected")
        self.child.sendline('su')
        self.child.expect('Password:')
        self.child.sendline('wwp')
        i = self.child.expect([self.prompt2, self.prompt])

   def send_cmds(command):

      self.child.logfile = sys.stdout
      self.child.sendline('su')
      router.child.expect(router.prompt)


	
class cienaswitch():
	def __init__(self,router):
		self.prompt = router.prompt
		self.prompt2 = router.prompt2
		self.prompt3 = router.prompt3
		self.ip = router.ip
		self.host = router.hostname
		self.name = self.host
		self.chassis = router.chassis
		self.vc_list =[]
		self.users_list = []
		self.user_name_list = []
		self.bfd_list = []
		self.bfd_profile = []
		self.vcnh_list =[]
		self.vc_db ='' 
		self.telnet()

	def telnet(self):
		try:
			self.child = pexpect.spawn ('telnet',[self.ip.strip()])
		except (ImportError, OSError, IOError, termios.error, ValueError):
			self.child = pexpect.spawn ('telnet',[self.ip.strip()])
			print("IO error")
		#the time out is needed to set to avoid child expect to time out,don't set to 5000
		self.child.timeout = 10000
		self.child.maxread = 1000000000
		#self.child.logfile_send = sys.stdout
		self.child.logfile_read = sys.stdout
		self.child.expect([self.prompt2, self.prompt,self.prompt3])
		self.child.sendline('gss')
		self.child.expect('Password:')
		self.child.sendline('lablab1')
		#self.child.expect([self.prompt, self.prompt2])
		i = self.child.expect([self.prompt2, self.prompt])
		 #i = self.child.expect(self.prompt)
		if i == 0:
			pass
		#print 'multiple match: prompt is %s' % self.prompt2
		elif i == 1:
			pass
		#print 'multiple match: prompt is %s' % self.prompt
		elif i == 2:
			pass
		#print 'nothing match'

	def get_show_user(self):
		cmd = 'user show'
		show_result = sw_show_cmd(self,cmd)
		list = show_result.split('\n')
		user_list = get_head_block(list,'Username')
		for user in user_list:
			user_dict = {}
			key,val = user.split('|')
			user_dict[key.strip()] = val.strip()
			self.users_list.append(user_dict)
			self.user_name_list.append(key.strip())
		return user_list

	def change_pass(self):
		self.get_show_user()
		for u in self.user_name_list:
			if self.chassis == '8700':
				cmd = 'user set user ' + u + ' password lablab1'
				print cmd
				self.child.sendline(cmd)
				self.child.expect([self.prompt2, self.prompt])
			else: 			# this is 6.x devivce
				cmd = 'user set user ' + u + ' echoless-password'
				print cmd
				self.child.sendline(cmd)
				self.child.expect('Enter Password:')
				self.child.sendline('lablab1')
				self.child.expect(["Verify Password:"])
				self.child.sendline('lablab1')

	def recover_pass(self):
		self.get_show_user()
		for u in self.user_name_list:
			cmd = 'user set user ' + u + ' echoless-password'
			if self.chassis == '8700':
				if u == 'gss':
					cmd = 'user set user ' + u + ' password pureethernet'
				else:
					cmd = 'user set user ' + u + ' password wwp'
				self.child.sendline(cmd)
				self.child.expect([self.prompt2, self.prompt])
			else:
				self.child.sendline(cmd)
				self.child.expect('Enter Password:')
				if u == 'gss':
					self.child.sendline('pureethernet')
					self.child.expect(["Verify Password:"])
					self.child.sendline('pureethernet')
				else:
					self.child.sendline('wwp')
					self.child.expect(["Verify Password:"])
					self.child.sendline('wwp')

	def sw_log_cmd(self,cmd):
		no_more = 'system shell set global-more off'
		more = 'system shell set global-more on'
		self.child.sendline(cmd)
		self.child.expect([self.prompt2, self.prompt])

	def change_port_mtu(self,port,mtu):
		cmd = 'port set port ' + port + ' max-frame-size ' + mtu
		self.sw_send_cmd(cmd)

	def sweep_port_mtu(self,port):
		for i in range(1522,9216):
			self.change_port_mtu(port,str(i))


	def sw_send_cmd(self,cmd):
		self.child.logfile_read = None
		no_more = 'system shell set global-more off'
		more = 'system shell set global-more on'
		self.child.sendline(cmd)
		self.child.expect([self.prompt2, self.prompt])

	def send_cmds(command):
		self.child.logfile = sys.stdout
		self.child.sendline('su')
		self.child.expect(router.prompt)

class backdoor2(cienaswitch):
	def  __init__(self, router):
		cienaswitch.__init__(self,router)
		#self.telnet()
		
	def telnet(self):
		try:
			self.child = pexpect.spawn ('telnet',[self.ip.strip()])
		except (ImportError, OSError, IOError, termios.error, ValueError):
			self.child = pexpect.spawn ('telnet',[self.ip.strip()])
			print("IO error")
		#the time out is needed to set to avoid child expect to time out,don't set to 5000
		self.child.timeout = 10000
		self.child.maxread = 1000000000
		self.child.logfile_send = sys.stdout
		self.child.logfile_read = sys.stdout
		self.child.expect([self.prompt2, self.prompt,self.prompt3])
		self.child.sendline('gss')
		self.child.expect('Password:')
		#self.child.sendline('wwp')
		self.child.sendline('pureethernet')
		#self.child.expect([self.prompt, self.prompt2])
		i = self.child.expect([self.prompt2, self.prompt])
		 #i = self.child.expect(self.prompt)
		if i == 0:
			pass
		#print 'multiple match: prompt is %s' % self.prompt2
		elif i == 1:
			pass
		#print 'multiple match: prompt is %s' % self.prompt
		elif i == 2:
			pass
		#print 'nothing match'

class backdoor(cienaswitch):
	def __init__(self,router):
		self.prompt = router.prompt
		self.prompt2 = router.prompt2
		self.prompt3 = router.prompt3
		self.ip = router.ip
		self.host = router.hostname
		self.name = self.host
		self.chassis = router.chassis
		self.users_list = []
		self.user_name_list = []
		self.telnet()

	def telnet(self):
		try:
			self.child = pexpect.spawn ('telnet',[self.ip.strip()])
		except (ImportError, OSError, IOError, termios.error, ValueError):
			self.child = pexpect.spawn ('telnet',[self.ip.strip()])
			print("IO error")
		#the time out is needed to set to avoid child expect to time out,don't set to 5000
		self.child.timeout = 10000
		self.child.maxread = 1000000000
		#self.child.logfile_send = sys.stdout
		self.child.logfile_read = sys.stdout
		self.child.expect([self.prompt2, self.prompt,self.prompt3])
		self.child.sendline('gss')
		self.child.expect('Password:')
		self.child.sendline('lablab1')
		self.child.expect([self.prompt2, self.prompt])

class virtual_switch_list():
	def __init__(self,dut):
		self.dut = dut
		self.vs_num = 0
		self.vs_list = show_vs(dut)
		self.vs_vpls_num = 0
		self.vs_vpws_num = 0
		self.vs_instance_list = self.build_all_vs()
		#self.build_all_vs()

	def vs_list_stats(self):
		for list in self.vs_list:
			if list['mode'] == 'vpls':
				self.vs_vpls_num += 1
			else:
				self.vs_vpws_num += 1

	def build_all_vs(self):
		list = []
		for i in self.vs_list:
			name = i['name']
			vs = virtual_switch(self.dut, i['name'])
			vs.ac_count = i['ac_count']
			vs.vc_count = i['vc_count']
			vs.mode = i['mode']
			vs.description = i['description']
			vs.cpt = i['cpt']
			list.append(vs)
		return list

	def flush_mac_all_vs(self):
		for vs in self.vs_instance_list:
			vs.flow_flush()

		
	def enable_mac_all_vs(self):
		for vs in self.vs_instance_list:
			vs.enable_mac_learning()


	def disable_mac_all_vs(self):
		for vs in self.vs_instance_list:
			vs.disable_mac_learning()

class virtual_switch():
	def __init__(self, dut, vs_name):
		self.name = vs_name
		self.dut = dut
		self.ac_count = 0
		self.vc_couint = 0
		self.mode = ' '
		self.description = ' '
		self.cpt = ' '
		self.show_result = self.show_vs()
		self.vs_vc_list = get_vs_name_vc(self.show_result)	
		self.port = get_vs_name_port(self.show_result)
		if self.port['No Members'] == 'Yes':
			self.have_port = False
		else:
			self.have_port = True 
		self.port_name = self.port['name']
		self.port_vlan = self.port['vlan']
		self.ingress_transform = self.port['intran']
		self.egress_transform = self.port['etran']
		self.encap_cos = self.port['encap_cos']
		self.encap_dot1dpri = self.port['pri']
		self.tpid = self.port['tpid']
		

	def show_vs(self):
		cmd = 'virtual-switch show vs ' + self.name
		show_result = sw_show_cmd(self.dut,cmd)
		return show_result

	def remove_port(self):
		cmd = 'virtual-switch ethernet remove vs ' + self.name +  ' port ' + self.port['name'] + ' vlan ' + self.port['vlan']
		sw_send_cmd(self.dut, cmd)

	def add_port(self):
		cmd = 'virtual-switch ethernet add vs ' + self.name +  ' port ' + self.port['name'] + ' vlan ' + self.port['vlan']
		sw_send_cmd(self.dut, cmd)

	def detach_vc(self):
		for vc in self.vs_vc_list:
			cmd = 'virtual-switch ethernet detach mpls-vc ' + vc['vc_name']
			sw_send_cmd(self.dut, cmd)

	def attach_vc(self):
		for vc in self.vs_vc_list:
			cmd = 'virtual-switch ethernet atta mpls-vc ' + vc['vc_name'] + ' vs ' + self.name
			print(cmd)
			sw_send_cmd(self.dut,cmd)

	def flow_flush(self):
		cmd = 'flow mac-addr flush vs ' + self.name
		sw_send_cmd(self.dut,cmd)

	def enable_mac_learning(self):
		cmd = 'flow learning enable vs ' + self.name
		sw_send_cmd(self.dut,cmd)

	def disable_mac_learning(self):
		cmd = 'flow learning disable vs ' + self.name
		sw_send_cmd(self.dut,cmd)



class mpls_vc:
	def __init__(self, sw, vc_csv):
		self.dut = sw
		self.host = sw.host
		self.vc_list =[]
		self.vcnh_list = []
		self.vc_list_up = []
		self.vc_list_b = []
		dut = self.dut
		self.lsp_log = dut.host + '_lsp' + '.log'
		self.mpls_vc_lck = dut.host + '_mpls_vc' + '.lck'
		
		lck = 'class_mpls_vc_init_file.lck'
		seek_lock(lck)

		with open(vc_csv, mode = 'r') as infile:
			reader = csv.reader(infile)
			with open('test_temp.log', mode = 'w') as outfile:
				writer = csv.writer(outfile)
				self.num_of_vc = 0
				self.down = 0
				self.up = 0
				self.nh_down = 0
				self.nh_up = 0
				for line in reader:
					vc = {}
					nh = {}
					if len(line) == 10:
						vc['pw_id'] = line[3].strip()
						vc['name'] = line[4].strip()
						vc['peer_ip'] = line[5].strip()
						vc['label'] = line[6].strip()
						vc['out_label'] = line[7].strip()
						vc['flag'] = line[8].strip()
						if vc['flag'] == 'sDMoB':
							self.down += 1
							self.vc_list_b.append(vc)
						elif vc['flag'] ==  'sDSbB':
							self.down += 1
							self.vc_list_b.append(vc)
						elif vc['flag'] ==  'sDSaB':
							self.down += 1
							self.vc_list_b.append(vc)
						else:
							self.up += 1
							self.vc_list_up.append(vc)

						self.vc_list.append(vc)
						self.num_of_vc += 1

					else:
						nh['name'] = line[6].strip()
						nh['op'] = line[4].strip()
						if nh['op'] == 'Dn':
							self.nh_down += 1
						else:
							self.nh_up += 1
						self.vcnh_list.append(nh)
				#print self.vc_list

				sw.vc_list = self.vc_list
				sw.vcnh_list = self.vcnh_list

		release_lock(lck)


	def show_mpls_vc(self):
		#print type(self.vc_list)
		print(self.vc_list)

	def show_mpls_vc_name(self):
		for vc in self.vc_list:
			print(vc['name'])

	def show_vc_all(self):
		for vc in self.vc_list:
			cmd = 'mpls l2-vpn show vc  ' + vc['name']
			sw_send_cmd(self.dut,cmd)

	def change_status_interval_all(self,time):
		for vc in self.vc_list:
			cmd = 'mpls l2-vpn set static-vc ' + vc['name'] + ' refresh-status-interval ' + time
			sw_send_cmd(self.dut,cmd)

	def turn_pw_reversion_all_off(self):
		for vc in self.vc_list:
			cmd = 'mpls l2-vpn set static-vc ' + vc['name'] + ' pw-reversion off ' 
			sw_send_cmd(self.dut,cmd)

	def turn_pw_reversion_all_on(self):
		for vc in self.vc_list:
			cmd = 'mpls l2-vpn set static-vc ' + vc['name'] + ' pw-reversion on ' 
			sw_send_cmd(self.dut,cmd)

	def flush_mac_all_vc(self):
		for vc in self.vc_list:
			cmd = 'flow mac-addr flush mpls-vc ' + vc['name']
			sw_send_cmd(self.dut,cmd)
			sleep(1)


	def update_mpls_vc_stat(self):
		pass

	def mpls_vc_stat(self):
		print("\n##################################################################################")
		print("#			MPLS L2-VPN Statistics Dump											")
		print("#			Switch Name: 	%s"	% self.host)
		print("##################################################################################")
		print("	")
		print('Total number of MPLS VC in the switch is -------->%d		' % self.num_of_vc)
		print('Total number of MPLS VC in blocking mode is ----> %d'	% self.down)
		print('Total number of MPLS VC in up mode is ------>%d' % self.up)
		print('Total number of MPLS VC next hop in Op Up mode ----->%d' % self.nh_up)
		print('Total number of MPLS VC next hop in Op Down mode ----> %d' % self.nh_down)
		

class ais: 
	def __init__(self,dut):
		self.dut = dut
		self.profile_list = []
		self.create_profile()
		dut.ais_profile_list = self.profile_list
		
		
	def create_profile(self):
		cmd_list = []

		cmd = 'ais profile create profile test-1B tlv-mode single-byte' 
		cmd_list.append(cmd)
		self.profile_list.append('test-1B')

		cmd = 'ais profile create profile test-2B tlv-mode double-byte' 
		cmd_list.append(cmd)
		self.profile_list.append('test-2B')

		cmd = 'ais profile create profile test-rdi-disable ais-rdi disable'
		cmd_list.append(cmd)
		self.profile_list.append('test-rdi-disable')

		cmd = 'ais profile create profile test-rdi-enable ais-rdi enable'
		cmd_list.append(cmd)
		self.profile_list.append('test-rdi-ensable')

		cmd = 'ais profile create profile test-1B-rdi-enable tlv-mode single-byte ais-rdi enable'
		cmd_list.append(cmd)
		self.profile_list.append('test-1B-rdi-enable')

		cmd = 'ais profile create profile test-1B-rdi-disable tlv-mode single-byte ais-rdi disable'
		cmd_list.append(cmd)
		self.profile_list.append('test-1B-rdi-disable')

		cmd = 'ais profile create profile test-2B-rdi-enable tlv-mode double-byte ais-rdi enable'
		cmd_list.append(cmd)
		self.profile_list.append('test-2B-rdi-enable')

		cmd = 'ais profile create profile test-2B-rdi-disable tlv-mode double-byte ais-rdi disable'
		cmd_list.append(cmd)
		self.profile_list.append('test-2B-rdi-disable')

		for i in range(1,21):
			profile_name = 'test-refresh-' + str(i)
			timer = str(i)
			cmd = 'ais profile create profile ' + profile_name + ' refresh-timer ' + timer
			print cmd
			cmd_list.append(cmd)
			self.profile_list.append(profile_name)

		for p in cmd_list:
			sw_send_cmd(self.dut,p)


class bfd:
	def __init__(self,dut):
		self.dut = dut
		self.platform = '6.x' 
		self.bfd_profile_list = dut.bfd_list
		self.bfd_global_dict = {}	
		self.bfd_infor_dict = {}	
		self.bfd_ipbfd_dict = {}	
		self.bfd_lspbfd_dict = {}	
		self.bfd_profile_dict = {}	
		self.global_list = []
		self.infor_list = []
		self.ipbfd_list = []
		self.lspbfd_list = []
		self.profile_gatch7_cmd_list = []
		self.profile_gatch7_list = []
		self.profile_gatch22_cmd_list = []
		self.profile_gatch22_list = []
		self.profile_name_list = []
		self.get_show_bfd()
		self.create_sw_bfd_profiles()
		self.configure_sw_bfd_profiles()
		self.admin = self.bfd_global_dict['Admin State']
		self.hw = self.bfd_global_dict['HW Acceleration']
		self.hw_sessions = self.bfd_global_dict['HW Sessions']
		self.bfd_created = self.bfd_infor_dict['Sessions Created']
		self.bfd_admin_up = self.bfd_infor_dict['Sessions Admin Up']
		self.bfd_op_up = self.bfd_infor_dict['Sessions Oper Up']
		self.ipbfd_created = self.bfd_ipbfd_dict['Sessions Created']
		self.ipbfd_admin_up = self.bfd_ipbfd_dict['Sessions Admin Up']
		self.ipbfd_op_up = self.bfd_ipbfd_dict['Sessions Oper Up']
		self.lspbfd_created = self.bfd_lspbfd_dict['Sessions Created']
		self.lspbfd_admin_up = self.bfd_lspbfd_dict['Sessions Admin Up']
		self.lspbfd_op_up = self.bfd_lspbfd_dict['Sessions Oper Up']

	def create_sw_bfd_profiles(self):
		interval_list = ['3.3msec','10msec','100msec','1sec','10sec']
		if self.platform == '6.x':
			for interval in interval_list:
				profile_dict_7 = {}
				profile_dict_22 = {}
				profile_name = 'bfd_sw_profile_gatch7_' + interval
				self.profile_name_list.append(profile_name)
				profile_dict_7[interval] = profile_name
				cmd = 'bfd profile create profile ' + profile_name + ' transmit-interval ' + interval + ' receive-interval ' + interval + ' lsp-gachtype 7'
				self.profile_gatch7_cmd_list.append(cmd)
				self.profile_gatch7_list.append(profile_dict_7)

				profile_name = 'bfd_sw_profile_gatch22_' + interval
				self.profile_name_list.append(profile_name)
				profile_dict_22[interval] = profile_name
				cmd = 'bfd profile create profile ' + profile_name + ' transmit-interval ' + interval + ' receive-interval ' + interval + ' lsp-gachtype 22'
				self.profile_gatch22_cmd_list.append(cmd)
				self.profile_gatch22_list.append(profile_dict_22)

	def configure_sw_bfd_profiles(self):
		for cmd in self.profile_gatch7_cmd_list:
			sw_send_cmd(self.dut,cmd)
		for cmd in self.profile_gatch22_cmd_list:
			sw_send_cmd(self.dut,cmd)

	def remove_sw_bfd_profiles(self):
		for name in self.profile_name_list:
			cmd = 'bfd profile delete profile ' + name
			sw_send_cmd(self.dut,cmd)
				
	
	def get_show_bfd(self):
		dut = self.dut
		cmd = 'bfd show'
		show_result = sw_show_cmd(dut,cmd)
		list = show_result.split('\n')
		global_list = []
		infor_list = []
		ipbfd_list = []
		lspbfd_list = []
		profile_list = []
		global_list = get_head_block(list,'BFD GLOBAL')
		infor_list = get_head_block(list,'BFD SESSION')
		ipbfd_list = get_head_block(list,'IP BFD SESSION')
		lspbfd_list = get_head_block(list,'LSP BFD SESSION')
		profile_list = get_head_block(list,'BFD PROFILE')
		bfd_global_dict = {}	
		bfd_infor_dict = {}	
		bfd_ipbfd_dict = {}	
		bfd_lspbfd_dict = {}	
		bfd_profile_dict = {}	
		for line in global_list:
			key,val = line.split('|')
			bfd_global_dict[key.strip()] = val.strip()
		for line in infor_list:
			key,val = line.split('|')
			bfd_infor_dict[key.strip()] = val.strip()
		for line in ipbfd_list:
			key,val = line.split('|')
			bfd_ipbfd_dict[key.strip()] = val.strip()
		for line in lspbfd_list:
			key,val = line.split('|')
			bfd_lspbfd_dict[key.strip()] = val.strip()
		for line in profile_list:
			key,val = line.split('|')
			bfd_profile_dict[key.strip()] = val.strip()
		self.bfd_global_dict = bfd_global_dict
		self.bfd_infor_dict = bfd_infor_dict
		self.bfd_ipbfd_dict = bfd_ipbfd_dict
		self.bfd_lspbfd_dict = bfd_lspbfd_dict
		self.bfd_profile_dict = bfd_profile_dict

class corout_tunnel:
	def __init__(self, dut,tunnel_detail):
		self.dut = dut
		self.name = tunnel_detail['Tunnel Name']
		self.index = tunnel_detail['Tunnel Index']
		self.role =  tunnel_detail['Nodal Role']
		self.dest =  tunnel_detail['Destination IP Address']
		self.src =  tunnel_detail['Source      IP Address']
		self.admin = tunnel_detail['Admin State']
		self.op = tunnel_detail['Oper  State']
		self.bfd_m = tunnel_detail['BFD Monitoring']
		self.bfd_id = tunnel_detail['BFD Profile ID']
		self.bfd_profile = tunnel_detail['BFD Profile Name']
		self.bfd_id = tunnel_detail['BFD Session ID']
		self.bfd_name = tunnel_detail['BFD Session Name']
		self.bfd_error = tunnel_detail['BFD Session Error Code']
		if ('case1' in tunnel_detail) == True:
			self.bfd_fault = tunnel_detail['BFD Monitor Fault Received']
		else:
			self.bfd_fault = 'BFD Monitoring is disabled, bfd report is irrelevant'
		self.ais_m = tunnel_detail['AIS Monitoring']
		self.ais_profile = tunnel_detail['AIS Profile Name']
		self.ais_fault = tunnel_detail['AIS Monitor Fault Received']

	def disable_tunnel_bfd(self):
		cmd = 'bfd session disable session ' + self.bfd_name
		sw_send_cmd(self.dut, cmd)


	def enable_tunnel_bfd(self):
		cmd = 'bfd session ensable session ' + self.bfd_name
		sw_send_cmd(self.dut, cmd)

class corout_ingress_tunnel(corout_tunnel):
	def __init__(self, dut,tunnel_detail ):
		corout_tunnel.__init__(self, dut,tunnel_detail)
		self.fout_label = tunnel_detail['Forward Out-Label']
		self.rin_label = tunnel_detail['Reverse In-Label']
		self.next_ip =  tunnel_detail['Next-Hop    IP Address']
		self.dest_ip =  tunnel_detail['Destination IP Address']
		self.lsp_group = tunnel_detail['Forward Tunnel Group Index']
		self.protection = tunnel_detail['Forward Protection Role']
		self.active = tunnel_detail['Forward Protection State']
		self.recovery = tunnel_detail['Forward Recovery Disjoint']
		self.tunnel_show = {}		# save the gmpls tp-tunnel show command result
		if self.protection == 'Primary':
			self.protection_tun = tunnel_detail['Forward Backup Tunnel Name']
			self.primary = tunnel_detail['Forward Backup Tunnel Name']
			self.reversion = tunnel_detail['Forward Tunnel Reversion']
			self.hold = tunnel_detail['Forward Reversion Hold-Time']
		else:
			self.protection_tun = tunnel_detail['Forward Primary Tunnel Name']
			self.protection = 'Backup'
			self.backup = tunnel_detail['Forward Primary Tunnel Name']
		self.cos_profile = tunnel_detail['Forward CoS Profile Name']
		self.cos_index = tunnel_detail['Forward CoS Profile Index']

	def tunnel_switch_over(self):
		if self.active == 'Active':
			cmd = 'gmpls tp-tunnel switchover static-ingress-corout ' + self.name
			sw_send_cmd(self.dut,cmd)	
			sleep(0.5)
			self.show_tunnel()
			if self.if_active() == 'True':
				print("!!!!!! Ingress Tunnel switchover failed at %s !!!!!!!!!" % self.name)
			else:
				print("Success: Ingress Tunnel %s has been switched over" % self.name)
		
	def tunnel_delete(self):
		cmd = 'gmpls tp-tunnel delete static-ingress-corout ' + self.name
		sw_send_cmd(self.dut,cmd)

	def tunnel_create(self):
		cmd = 'gmpls tp-tunnel create static-ingress-corout ' + self.name +  ' dest-ip ' +  self.dest_ip + ' next-hop-ip ' + self.next_ip + ' forward-out-label ' + self.fout_label + ' reverse-in-label ' + self.rin_label + ' bfd-monitor enable ais-monitor enable'
		sw_send_cmd(self.dut,cmd)

	def if_active(self):
		if self.active == 'Active':
			return 'True'
		else:
			return 'False'

	def set_hw_bfd(self):
		disable_bfd_cmd = 'gmpls tp-tunnel set static-ingress-corout ' + self.name + ' ' + 'bfd-monitor disable' 
		print(disable_bfd_cmd)
		sw_send_cmd(self.dut, disable_bfd_cmd)
		set_bfd_cmd = 'gmpls tp-tunnel set static-ingress-corout ' + self.name + ' ' + 'bfd-profile' + ' ' + 'hw-profile-lsp-2' + ' ' + 'bfd-monitor enable'
		print(set_bfd_cmd)
		sw_send_cmd(self.dut, set_bfd_cmd)
		
	def set_hw_bfd_profile(self,profile):
		disable_bfd_cmd = 'gmpls tp-tunnel set static-ingress-corout ' + self.name + ' ' + 'bfd-monitor disable' 
		print(disable_bfd_cmd)
		sw_send_cmd(self.dut, disable_bfd_cmd)
		set_bfd_cmd = 'gmpls tp-tunnel set static-ingress-corout ' + self.name + ' ' + 'bfd-profile' + ' ' + profile + ' ' + 'bfd-monitor enable'
		print(set_bfd_cmd)
		sw_send_cmd(self.dut, set_bfd_cmd)
		
	def set_sw_bfd_profile(self,profile):
		disable_bfd_cmd = 'gmpls tp-tunnel set static-ingress-corout ' + self.name + ' ' + 'bfd-monitor disable' 
		print(disable_bfd_cmd)
		sw_send_cmd(self.dut, disable_bfd_cmd)
		set_bfd_cmd = 'gmpls tp-tunnel set static-ingress-corout ' + self.name + ' ' + 'bfd-profile' + ' ' + profile + ' bfd-monitor enable'
		print set_bfd_cmd
		sw_send_cmd(self.dut, set_bfd_cmd)

	def set_ais_profile(self,profile):
		set_ais_cmd = 'gmpls tp-tunnel set static-ingress-corout ' + self.name + ' ' + 'ais-profile' + ' ' + profile 
		print set_ais_cmd
		sw_send_cmd(self.dut, set_ais_cmd)

	def set_sw_bfd(self):
		disable_bfd_cmd = 'gmpls tp-tunnel set static-ingress-corout ' + self.name + ' ' + 'bfd-monitor disable' 
		print(disable_bfd_cmd)
		sw_send_cmd(self.dut, disable_bfd_cmd)
		set_bfd_cmd = 'gmpls tp-tunnel set static-ingress-corout ' + self.name + ' ' + 'bfd-profile' + ' ' + 'Active-LSP' + ' ' + 'bfd-monitor enable'
		print(set_bfd_cmd)
		sw_send_cmd(self.dut, set_bfd_cmd)

	def display_tunnel(self):
		show_cmd = 'gmpls tp-tunnel show static-ingress-corout ' + self.name 
		sw_send_cmd(self.dut, show_cmd)

	def show_tunnel(self):
		show_cmd = 'gmpls tp-tunnel show static-ingress-corout ' + self.name 
		show_result = sw_show_cmd(self.dut, show_cmd)
		#print show_result
		list = show_result.split('\n')
		tunnel_detail = {}
		for item in list:
			#item = item.strip('\n')
			item = item.strip()
			line = item.strip('|')
			if '|' in line and 'Parameter' not in line: 
				key, val = line.split('|')
				tunnel_detail[key.strip()] = val.strip()
				tunnel_detail['name'] = self.name

		self.tunnel_show = tunnel_detail
		self.name = tunnel_detail['Tunnel Name']
		self.index = tunnel_detail['Tunnel Index']
		self.role =  tunnel_detail['Nodal Role']
		self.dest =  tunnel_detail['Destination IP Address']
		self.src =  tunnel_detail['Source      IP Address']
		self.admin = tunnel_detail['Admin State']
		self.op = tunnel_detail['Oper  State']
		self.bfd_m = tunnel_detail['BFD Monitoring']
		self.bfd_id = tunnel_detail['BFD Profile ID']
		self.bfd_profile = tunnel_detail['BFD Profile Name']
		self.bfd_id = tunnel_detail['BFD Session ID']
		self.bfd_name = tunnel_detail['BFD Session Name']
		self.bfd_error = tunnel_detail['BFD Session Error Code']

		r = tunnel_detail.get('BFD Monitor Fault Received')
		if r == None:
			self.bfd_fault = 'NA'
		else:
			self.bfd_fault = tunnel_detail['BFD Monitor Fault Received']
		self.ais_m = tunnel_detail['AIS Monitoring']
		self.ais_profile = tunnel_detail['AIS Profile Name']
		self.ais_fault = tunnel_detail['AIS Monitor Fault Received']

		self.fout_label = tunnel_detail['Forward Out-Label']
		self.rin_label = tunnel_detail['Reverse In-Label']
		self.next_ip =  tunnel_detail['Next-Hop    IP Address']
		self.lsp_group = tunnel_detail['Forward Tunnel Group Index']
		self.protection = tunnel_detail['Forward Protection Role']
		self.active = tunnel_detail['Forward Protection State']
		self.recovery = tunnel_detail['Forward Recovery Disjoint']
		self.tunnel_show = {}		# save the gmpls tp-tunnel show command result
		if self.protection == 'Primary':
			self.protection_tun = tunnel_detail['Forward Backup Tunnel Name']
			self.primary = tunnel_detail['Forward Backup Tunnel Name']
			self.reversion = tunnel_detail['Forward Tunnel Reversion']
			self.hold = tunnel_detail['Forward Reversion Hold-Time']
		else:
			self.protection_tun = tunnel_detail['Forward Primary Tunnel Name']
			self.protection = 'Backup'
			self.backup = tunnel_detail['Forward Primary Tunnel Name']
		self.cos_profile = tunnel_detail['Forward CoS Profile Name']
		self.cos_index = tunnel_detail['Forward CoS Profile Index']

		return self.tunnel_show

	def print_tunnel_details(self):
		print("\n =============Printing individual tunnel details===============")
		print("Tunnel Name is %s" % self.name)
		print("Tunnel Index is %s" % self.index)
		print("Nodal Role is  %s " % self.role)
		print("Destination IP Address %s " % self.dest)
		print("Source      IP Address %s " % self.src)
		print("Next-Hop    IP Address %s " % self.next_ip)
		print("Admin State is %s " % self.admin)
		print("Oper  State is %s  " % self.op)
		print("Forward Out-Label is %s " % self.fout_label)
		print("Reverse -Label is %s " % self.rin_label)
		print("Forward Tunnel Group Index is %s " % self.lsp_group)
		print("Forward Protection Role is %s " % self.protection)
		print("Forward Protection State is %s " % self.active)
		print("Forward Backup Tunnel Name is %s " % self.protection_tun)
		if self.protection == 'Primary':
			print("Forward Tunnel Reversion is %s " % self.reversion)
			print("Forward Tun Reversion Hold-Time is %s " % self.hold)
		print("Forward CoS-Profile Name is %s " % self.cos_profile)
		print("Forward CoS-Profile Index is %s " % self.cos_index)
		print("BFD Monitoring is %s " % self.bfd_m)
		print("BFD Profile ID is %s " % self.bfd_id)
		print("BFD Profile Name is %s " % self.bfd_profile)
		print("BFD Session ID is %s " % self.bfd_id)
		print("BFD Session Name is %s " % self.bfd_name)
		print("BFD Session Error Code is %s " % self.bfd_error)
		print("BFD Monitor Fault Received is %s " % self.bfd_fault)
		print("AIS Monitoring is %s " % self.ais_m)
		print("AIS Profile Name is %s " % self.ais_profile)
		print("AIS Monitor Fault Received is %s " % self.ais_fault)


class corout_egress_tunnel(corout_tunnel):
	def __init__(self, dut,tunnel_detail ):
		corout_tunnel.__init__(self, dut, tunnel_detail)
		self.fin_label = tunnel_detail['Forward In-Label']
		self.rout_label = tunnel_detail['Reverse Out-Label']
		self.src_ip =  tunnel_detail['Source      IP Address']
		self.previous_ip =  tunnel_detail['Prev-Hop    IP Address']
		self.lsp_group = tunnel_detail['Reverse Tunnel Group Index']
		self.protection = tunnel_detail['Reverse Protection Role']
		# protection tunnel: could be the name of backup tunnel or primiary  tunnel
		if self.protection == 'Primary':
			self.protection_tun = tunnel_detail['Reverse Backup Tunnel Name']
			self.reversion = tunnel_detail['Reverse Tunnel Reversion']
			self.hold = tunnel_detail['Reverse Tunl Reversion Time']
		else:
			self.protection_tun = tunnel_detail['Reverse Primary Tunnel Name']
		self.active = tunnel_detail['Reverse Protection State']
		self.recovery = tunnel_detail['Reverse Recovery Disjoint']
		self.cos_profile = tunnel_detail['Reverse CoS-Profile Name']
		self.cos_index = tunnel_detail['Reverse CoS-Profile Index']

	def display_tunnel(self):
		show_cmd = 'gmpls tp-tunnel show static-egress-corout ' + self.name 
		sw_send_cmd(self.dut, show_cmd)

	def tunnel_delete(self):
		cmd = 'gmpls tp-tunnel delete static-egress-corout ' + self.name
		sw_send_cmd(self.dut,cmd)


	def tunnel_create(self):
		cmd = 'gmpls tp-tunnel create static-egress-corout ' + self.name +  ' src-ip ' +  self.src_ip + ' prev-hop-ip ' + self.previous_ip + ' forward-in-label ' + self.fin_label + ' reverse-out-label ' + self.rout_label + ' bfd-monitor enable ais-monitor enable'
		sw_send_cmd(self.dut,cmd)

	def tunnel_config(self):
		cmd = 'gmpls tp-tunnel create static-egress-corout ' + self.name +  ' src-ip ' +  self.src_ip + ' prev-hop-ip ' + self.previous_ip + ' forward-in-label ' + self.fin_label + ' reverse-out-label ' + self.rout_label + ' bfd-monitor enable ais-monitor enable'
		sw_send_cmd(self.dut,cmd)

	def print_tunnel_details(self):
		print("Tunnel Name is %s" % self.name)
		print("Tunnel Index is %s" % self.index)
		print("Nodal Role is  %s " % self.role)
		print("Destination IP Address %s " % self.dest)
		print("Source      IP Address %s " % self.src)
		print("Prev-Hop    IP Address %s " % self.previous_ip)
		print("Admin State is %s " % self.admin)
		print("Oper  State is %s  " % self.op)
		print("Forward In-Label is %s " % self.fin)
		print("Reverse Out-Label is %s " % self.rout)
		print("Reverse Tunnel Group Index is %s " % self.lsp_group)
		print("Reverse Protection Role is %s " % self.protection)
		print("Reverse Protection State is %s " % self.active)
		print("Reverse Backup Tunnel Name is %s " % self.backup)
		if self.protection == 'Primary':
			print("Reverse Tunnel Reversion is %s " % self.reversion)
			print("Reverse Tunl Reversion Time is %s " % self.hold)
		print("Reverse CoS-Profile Name is %s " % self.cos_profile)
		print("Reverse CoS-Profile Index is %s " % self.cos_index)
		print("BFD Monitoring is %s " % self.bfd_m)
		print("BFD Profile ID is %s " % self.bfd_id)
		print("BFD Profile Name is %s " % self.bfd_profile)
		print("BFD Session ID is %s " % self.bfd_id)
		print("BFD Session Name is %s " % self.bfd_name)
		print("BFD Session Error Code is %s " % self.bfd_error)
		print("BFD Monitor Fault Received is %s " % self.bfd_fault)
		print("AIS Monitoring is %s " % self.ais_m)
		print("AIS Profile Name is %s " % self.profile)
		print("AIS Monitor Fault Received is %s " % self.ais_fault)


	def tunnel_switch_over(self):
		if self.active == 'Active':
			cmd = 'gmpls tp-tunnel switchover static-egress-corout ' + self.name
			sw_send_cmd(self.dut,cmd)	
			sleep(0.5)
			self.show_tunnel()
			if self.if_active() == 'True':
				print "!!!!!! %s Tunnel switchover failed !!!!!!!!!" % self.name
			else:
				print("Success: Egress Tunnel %s has been switched over" % self.name)
		

	def if_active(self):
		if self.active == 'Active':
			return 'True'
		else:
			return 'False'

	# this method sets the default bfd hw profile
	def set_hw_bfd(self):
		disable_bfd_cmd = 'gmpls tp-tunnel set static-egress-corout ' + self.name + ' ' + 'bfd-monitor disable' 
		sw_send_cmd (self.dut, disable_bfd_cmd)
		set_bfd_cmd = 'gmpls tp-tunnel set static-egress-corout ' + self.name + ' ' + 'bfd-profile' + ' ' + 'hw-profile-lsp-2' + ' ' + 'bfd-monitor enable'
		sw_send_cmd( self.dut, set_bfd_cmd)
		
	# this method sets bfd hw profile with different intervals
	def set_hw_bfd_profile(self,profile):
		disable_bfd_cmd = 'gmpls tp-tunnel set static-ingress-corout ' + self.name + ' ' + 'bfd-monitor disable' 
		print(disable_bfd_cmd)
		sw_send_cmd(self.dut, disable_bfd_cmd)
		set_bfd_cmd = 'gmpls tp-tunnel set static-ingress-corout ' + self.name + ' ' + 'bfd-profile' + ' ' + profile + ' ' + 'bfd-monitor enable'
		print(set_bfd_cmd)

	def set_ais_profile(self,profile):
		set_ais_cmd = 'gmpls tp-tunnel set static-egress-corout ' + self.name + ' ' + 'ais-profile' + ' ' + profile 
		print set_ais_cmd
		sw_send_cmd(self.dut, set_ais_cmd)

	def set_sw_bfd_profile(self,profile):
		disable_bfd_cmd = 'gmpls tp-tunnel set static-egress-corout ' + self.name + ' ' + 'bfd-monitor disable' 
		sw_send_cmd (self.dut, disable_bfd_cmd)
		set_bfd_cmd = 'gmpls tp-tunnel set static-egress-corout ' + self.name + ' ' + 'bfd-profile' + ' ' + profile + ' bfd-monitor enable'
		sw_send_cmd( self.dut, set_bfd_cmd)

	def set_sw_bfd(self):
		disable_bfd_cmd = 'gmpls tp-tunnel set static-egress-corout ' + self.name + ' ' + 'bfd-monitor disable' 
		sw_send_cmd (self.dut, disable_bfd_cmd)
		set_bfd_cmd = 'gmpls tp-tunnel set static-egress-corout ' + self.name + ' ' + 'bfd-profile' + ' ' + 'Active-LSP' + ' ' + 'bfd-monitor enable'
		sw_send_cmd( self.dut, set_bfd_cmd)

	def show_tunnel(self):
		show_cmd = 'gmpls tp-tunnel show static-egress-corout ' + self.name 
		show_result = sw_show_cmd(self.dut, show_cmd)
		#print show_result
		list = show_result.split('\n')
		tunnel_detail = {}
		for item in list:
			#item = item.strip('\n')
			item = item.strip()
			line = item.strip('|')
			if '|' in line and 'Parameter' not in line: 
				key, val = line.split('|')
				tunnel_detail[key.strip()] = val.strip()
				tunnel_detail['name'] = self.name

		self.tunnel_show = tunnel_detail

		self.fin_label = tunnel_detail['Forward In-Label']
		self.rout_label = tunnel_detail['Reverse Out-Label']
		self.previous_ip =  tunnel_detail['Prev-Hop    IP Address']
		self.lsp_group = tunnel_detail['Reverse Tunnel Group Index']
		self.protection = tunnel_detail['Reverse Protection Role']
		# protection tunnel: could be the name of backup tunnel or primiary  tunnel
		if self.protection == 'Primary':
			self.protection_tun = tunnel_detail['Reverse Backup Tunnel Name']
			self.reversion = tunnel_detail['Reverse Tunnel Reversion']
			self.hold = tunnel_detail['Reverse Tunl Reversion Time']
		else:
			self.protection_tun = tunnel_detail['Reverse Primary Tunnel Name']
		self.active = tunnel_detail['Reverse Protection State']
		self.recovery = tunnel_detail['Reverse Recovery Disjoint']
		self.cos_profile = tunnel_detail['Reverse CoS-Profile Name']
		self.cos_index = tunnel_detail['Reverse CoS-Profile Index']
		self.name = tunnel_detail['Tunnel Name']
		self.index = tunnel_detail['Tunnel Index']
		self.role =  tunnel_detail['Nodal Role']
		self.dest =  tunnel_detail['Destination IP Address']
		self.src =  tunnel_detail['Source      IP Address']
		self.admin = tunnel_detail['Admin State']
		self.op = tunnel_detail['Oper  State']
		self.bfd_m = tunnel_detail['BFD Monitoring']
		self.bfd_id = tunnel_detail['BFD Profile ID']
		self.bfd_profile = tunnel_detail['BFD Profile Name']
		self.bfd_id = tunnel_detail['BFD Session ID']
		self.bfd_name = tunnel_detail['BFD Session Name']
		self.bfd_error = tunnel_detail['BFD Session Error Code']
		self.bfd_fault = tunnel_detail['BFD Monitor Fault Received']
		self.ais_m = tunnel_detail['AIS Monitoring']
		self.ais_profile = tunnel_detail['AIS Profile Name']
		self.ais_fault = tunnel_detail['AIS Monitor Fault Received']

		return self.tunnel_show

class tunnel:
	def __init__(self, dut):
		self.lsp_log = dut.host + '_lsp' + '.log'
		self.lsp_log_lck = dut.host + '_lsp' + '.log' + '.lck'
		self.lsp_csv = dut.host + '_lsp' + '.csv'
		self.lsp_csv_lck = dut.host + '_lsp' + '.csv' + '.lck'

		lck = 'class_tunnel_init_file.lck'
		seek_lock(lck)
		self.result_lsp = sw_read_cmd(dut, self.lsp_log, 'gmpls tp-tunnel show')
		process_log_file(self.lsp_log)  # Process the log file to remove not needed stuff 
		self.i_lsp_list = read_lsp(self.lsp_log, 'INGRESS')
		self.e_lsp_list = read_lsp(self.lsp_log, 'EGRESS')
		self.t_lsp_list = read_lsp(self.lsp_log, 'TRANSIT')
		self.dut  = dut 
		self.host = dut.host
		self.lsp_list = []
		self.lsp_detail_list = []
		self.bfd_list = []
		self.tu_num = 0
		self.tu_up = 0
		self.tu_down = 0
		self.tu_p = 0
		self.tu_p_active = 0
		self.tu_p_standby = 0
		self.tu_b = 0
		self.tu_b_active = 0
		self.tu_b_standby = 0
		release_lock(lck)

	def show_tunnel(self):
		for line in self.lsp_list:
			print(line) 

	def set_sw_bfd_profile_all(self,profile):
		for tu in self.tunnel_instances_list:
			tu.set_sw_bfd_profile(profile)

	def set_ais_profile_all(self,profile):
		for tu in self.tunnel_instances_list:
			tu.set_ais_profile(profile)

	def lsp_stat(self):
		pass


class ingress_tunnel(tunnel):
	def __init__(self, sw ):
		tunnel.__init__(self, sw)
		self.type = 'static-ingress-corout'
		self.lsp_detail_list = []
		self.tunnel_instances_list = []
		for line in self.i_lsp_list:
			self.tu_num += 1
			tu = {}
			tu['index'] = line[3].strip()
			tu['name'] = line[4].strip()
			tu['destination'] = line[5].strip()
			tu['forward_out_label'] = line[6].strip()
			tu['reverse_in_label'] = line[7].strip()
			tu['admin'] = line[8].strip()
			tu['op'] = line[9].strip()
			tu['pb'] = line[10].strip()
			tu['lr'] = line[11].strip()
			tu['as'] = line[12].strip()
			tu['type'] = 'static-ingress-corout'
			self.lsp_list.append(tu)
			if tu['op'] == 'ENA':
				self.tu_up += 1
			else:
				self.tu_down += 1
			if tu['pb'] == 'P':
				self.tu_p += 1
			if tu['pb'] == 'B':
				self.tu_b += 1
			if (tu['pb'] == 'P') and (tu['as'] == 'A'):
				self.tu_p_active += 1
			if (tu['pb'] == 'P') and (tu['as'] == 'S'):
				self.tu_p_standby += 1
			if (tu['pb'] == 'B') and (tu['as'] == 'A'):
				self.tu_b_active += 1
			if (tu['pb'] == 'B') and (tu['as'] == 'S'):
				self.tu_b_standby += 1

		if  os.path.exists(self.lsp_log_lck):
			file = self.lsp_log_lck
			os.remove(file)
	
		if  os.path.exists(self.lsp_csv_lck):
			file = self.lsp_csv_lck
			os.remove(file)


	def switchover_tunnel_all(self):
		for tu in self.tunnel_instances_list:
			tu.tunnel_switch_over()

	def delete_tunnel_all(self):
		for tu in self.tunnel_instances_list:
			tu.tunnel_delete()

	def delete_tunnel_some(self,num):
		i = 0
		for tu in self.tunnel_instances_list:
			tu.tunnel_delete()
			i += 1
			if i > num:
				break

	def create_tunnel_all(self):
		for tu in self.tunnel_instances_list:
			tu.tunnel_create()
			sleep(1)

	def show_tunnel_all(self):
		for tu in self.tunnel_instances_list:
			tu.display_tunnel()

	def set_sw_bfd_all(self):
		for tu in self.tunnel_instances_list:
			tu.set_sw_bfd()



	def show_tunnel_stats(self):
		print_line_stats()
		print("Total number of ingress LSP is:------------> %d" % self.tu_num)
		print("Total number of UP ingress LSP is:------------> %d" % self.tu_up)
		print("Total number of DOWN ingress LSP is:------------> %d" % self.tu_down)
		print("Total number of PRIMARY ingress LSP is:------------> %d" % self.tu_p)
		print("Total number of BACKUP ingress LSP is:------------> %d" % self.tu_b)
		print("Total number of PRIMARY ingress LSP that is ACTIVE is:------------> %d" % self.tu_p_active)
		print("Total number of PRIMARY ingress LSP that is STANDBY is:------------> %d" % self.tu_p_standby)
		print("Total number of BACKUP ingress LSP that is ACTIVE is:------------> %d" % self.tu_b_active)
		print("Total number of BACKUP ingress LSP that is STANDBY is:------------> %d" % self.tu_b_standby)

	def build_tunnel_all(self):
		lck = 'def_build_tunnel_details_file.lck'
		seek_lock(lck)
		self.get_tunnel_details()
		for d in self.lsp_detail_list:
			dut = self.dut
			self.tunnel_instances_list.append(corout_ingress_tunnel(dut,d))
		release_lock(lck)

	
	def set_hw_bfd_all(self):
		for tu in self.tunnel_instances_list:
			tu.set_hw_bfd()

	def set_hw_bfd_all_profile(self,profile):
		for tu in self.tunnel_instances_list:
			tu.set_hw_bfd(profile)

	def get_tunnel_details(self):
		lck = 'def_get_tunnel_details_file.lck'
		seek_lock(lck)
		i = 0
		for lsp in self.lsp_list:
			show_cmd = 'gmpls tp-tunnel show static-ingress-corout ' + lsp['name']
			show_result = sw_show_cmd(self.dut, show_cmd)
			#show_result = sw_read_cmd(self.dut, 'get_tunnel_details.log',show_cmd)
			i = i + 1
			#print show_result
			list = show_result.split('\n')
			tunnel_show = {}
			for item in list:
				#item = item.strip('\n')
				item = item.strip()
				line = item.strip('|')
				if '|' in line and 'Parameter' not in line: 
					#print line
					key, val = line.split('|')
					tunnel_show[key.strip()] = val.strip()
					tunnel_show['name'] = lsp['name']
					#print tunnel_show
			self.lsp_detail_list.append(tunnel_show)
			self.bfd_list.append(tunnel_show['BFD Session Name'])
		#print self.lsp_detail_list
		#print self.bfd_list
		release_lock(lck)
			

	def get_tunnel_details_byname(self):
		pass


	def lsp_disable(self):
		num = 1
		print("\nDisabling %s GMPLS TUNEL in the number of ......\n" % self.type)
		for tunnel in self.lsp_list:
			cmd = 'gmpls tp-tunnel disable ' + tunnel['type'] + ' ' + tunnel['name'] 
			type = tunnel['type']
			sw_send_cmd(self.dut, cmd)
			flush_print(num)
			num += 1
			sleep(1)

			
	def lsp_enable(self):
		num = 1
		print("\nEanbling %s GMPLS TUNEL in the number of ......\n" % self.type)
		for tunnel in self.lsp_list:
			cmd = 'gmpls tp-tunnel enable ' + tunnel['type'] + ' ' + tunnel['name'] 
			type = tunnel['type']
			sw_send_cmd(self.dut, cmd)
			flush_print(num)
			num += 1
			sleep(1)



	def lsp_stat(self):
		print("\n##################################################################################")
		print("#			MPLS %s LSP Statistics Dump											" % self.type)
		print("#			Switch Name: 	%s"	% self.host)
		print("##################################################################################")
		print("	")
		print('Total number of %s LSP in the switch is --------> %d		' % (self.type, self.tu_num))
		print('Total number of LSP in operational ENABLE  mode is ----> %d'	% self.tu_up)
		print('Total number of LSP in operational DISABLE mode is ----> %d'	% self.tu_down)
		print('Total number of Primary LSP in the switch is --------> %d		' % self.tu_p) 
		print('Total number of Backup LSP in the switch is --------> %d		' % self.tu_b)
		print('Total number of Primary LSP in ACTIVE mode is ----> %d'	% self.tu_p_active)
		print('Total number of Primary LSP in STANDBY mode is ----> %d'	% self.tu_p_standby)
		print('Total number of Backup LSP in ACTIVE mode is ----> %d'	% self.tu_b_active)
		print('Total number of Backup LSP in STANDBY mode is ----> %d'	% self.tu_b_standby)


class egress_tunnel(tunnel):
	def __init__(self,sw ):
		tunnel.__init__(self,sw)
		self.type = 'static-egress-corout'	
		self.lsp_detail_list = []
		self.tunnel_instances_list = []
		for line in self.e_lsp_list:
			self.tu_num += 1
			tu = {}
			tu['type'] = 'static-egress-corout'
			tu['index'] = line[3].strip()
			tu['name'] = line[4].strip()
			tu['source'] = line[5].strip()
			tu['forward_in_label'] = line[6].strip()
			tu['reverse_out_label'] = line[7].strip()
			tu['admin'] = line[8].strip()
			tu['op'] = line[9].strip()
			tu['pb'] = line[10].strip()
			tu['lr'] = line[11].strip()
			tu['as'] = line[12].strip()
			self.lsp_list.append(tu)
			if tu['op'] == 'ENA':
				self.tu_up += 1
			else:
				self.tu_down += 1
			if tu['pb'] == 'P':
				self.tu_p += 1
			if tu['pb'] == 'B':
				self.tu_b += 1
			if tu['pb'] == 'P' and tu['as'] == 'A':
				self.tu_p_active += 1
			if tu['pb'] == 'P' and tu['as'] == 'S':
				self.tu_p_standby += 1
			if tu['pb'] == 'B' and tu['as'] == 'A':
				self.tu_b_active += 1
			if tu['pb'] == 'B' and tu['as'] == 'S':
				self.tu_b_standby += 1

		if  os.path.exists(self.lsp_log_lck):
			file = self.lsp_log_lck
			os.remove(file)
	
		if  os.path.exists(self.lsp_csv_lck):
			file = self.lsp_csv_lck
			os.remove(file)


	def show_tunnel_all(self):
		for tu in self.tunnel_instances_list:
			tu.display_tunnel()

	def set_sw_bfd_all(self):
		for tu in self.tunnel_instances_list:
			tu.set_sw_bfd()

	def set_hw_bfd_all(self):
		for tu in self.tunnel_instances_list:
			tu.set_hw_bfd()

	def set_hw_bfd_all_profile(self,profile):
		for tu in self.tunnel_instances_list:
			tu.set_hw_bfd(profile)

	def switchover_tunnel_all(self):
		for tu in self.tunnel_instances_list:
			tu.tunnel_switch_over()

	def build_tunnel_all(self):
		self.get_tunnel_details()
		for d in self.lsp_detail_list:
			dut = self.dut
			self.tunnel_instances_list.append(corout_egress_tunnel(dut,d))

	def delete_tunnel_all(self):
		for tu in self.tunnel_instances_list:
			tu.tunnel_delete()

	def delete_tunnel_some(self,num):
		i = 0
		for tu in self.tunnel_instances_list:
			tu.tunnel_delete()
			i += 1
			if i > num:
				break

	def create_tunnel_all(self):
		for tu in self.tunnel_instances_list:
			tu.tunnel_create()
			sleep(1)

	def get_tunnel_details(self):
		for lsp in self.lsp_list:
			show_cmd = 'gmpls tp-tunnel show static-egress-corout ' + lsp['name']
			#self.dut.child.sendline('\n')
			show_result = sw_show_cmd(self.dut, show_cmd)
			#print show_result
			list = show_result.split('\n')
			tunnel_show = {}
			for item in list:
				#item = item.strip('\n')
				item = item.strip()
				line = item.strip('|')
				if '|' in line and 'Parameter' not in line: 
					#print line
					key, val = line.split('|')
					tunnel_show[key.strip()] = val.strip()
					#print tunnel_show
				#print "~~~~~~~~~~~~~~~~~~"
			self.lsp_detail_list.append(tunnel_show)
			self.bfd_list.append(tunnel_show['BFD Session Name'])
			#print "\n====================================="
		#print self.lsp_detail_list
		#print self.bfd_list

	def lsp_stat(self):
		print("\n##################################################################################")
		print("#			MPLS %s LSP Statistics Dump											" % self.type)
		print("#			Switch Name: 	%s"	% self.host)
		print("##################################################################################")
		print("	")
		print('Total number of %s LSP in the switch is --------> %d		' % (self.type, self.tu_num))
		print('Total number of LSP in operational ENABLE  mode is ----> %d'	% self.tu_up)
		print('Total number of LSP in operational DISABLE mode is ----> %d'	% self.tu_down)
		print('Total number of Primary LSP in the switch is --------> %d		' % self.tu_p) 
		print('Total number of Backup LSP in the switch is --------> %d		' % self.tu_b)
		print('Total number of Primary LSP in ACTIVE mode is ----> %d'	% self.tu_p_active)
		print('Total number of Primary LSP in STANDBY mode is ----> %d'	% self.tu_p_standby)
		print('Total number of Backup LSP in ACTIVE mode is ----> %d'	% self.tu_b_active)
		print('Total number of Backup LSP in STANDBY mode is ----> %d'	% self.tu_b_standby)


	def lsp_disable(self):
		num = 1
		print("\nDisabling %s GMPLS TUNEL in the number of ......\n" % self.type)
		for tunnel in self.lsp_list:
			cmd = 'gmpls tp-tunnel disable ' + tunnel['type'] + ' ' + tunnel['name'] 
			type = tunnel['type']
			sw_send_cmd(self.dut, cmd)
			flush_print(num)
			num += 1

			
	def lsp_enable(self):
		num = 1
		print("\nEanbling %s GMPLS TUNEL in the number of ......\n" % self.type)
		for tunnel in self.lsp_list:
			cmd = 'gmpls tp-tunnel enable ' + tunnel['type'] + ' ' + tunnel['name'] 
			type = tunnel['type']
			sw_send_cmd(self.dut, cmd)
			flush_print(num)
			num += 1

class transit_tunnel(tunnel):
	def __init__(self,sw):
		tunnel.__init__(self, sw)
		self.type = 'static-transit-corout'	
		for line in self.t_lsp_list:
			tu = {}
			tu['index'] = line[3].strip()
			tu['name'] = line[4].strip()
			tu['admin'] = line[5].strip()
			tu['op'] = line[6].strip()
			tu['forward_in_label'] = line[7].strip()
			tu['forward_out_label'] = line[8].strip()
			tu['reverse_in_label'] = line[9].strip()
			tu['reverse_out_label'] = line[10].strip()
			tu['type'] = 'static-transit-corout'
			self.lsp_list.append(tu)

def update_mpls_vc_db(dut):
		sw_send_cmd(dut,'system shell set global-more off')
		vc_log = dut.host + '_vc' + '.log'
		vc_csv = dut.host + '_vc' + '.csv'
		lck = 'def_update_mpls_vc_file.lck'
		seek_lock(lck)
		result = sw_read_cmd(dut, vc_log, 'mpls l2-vpn show')
		print "update mpls_result %s" % result
		#sw_send_cmd(dut,'system shell set global-more on')
		process_log_file(vc_log)   # Process the log file to remove not needed stuff
		vc_str = 'F00'             # The string being used to identify VC name
		lsp_str= 'Sta'             # The string being used to identify LSP name
		create_vc_csv(vc_log, vc_csv,vc_str, lsp_str)
		vc_db = mpls_vc(dut, vc_csv)
		dut.vc_db = vc_db
		#release_lock(lck)

##############################################################################
# flap_mpls_vc(dut,flap_cmd)
# Flapping MPLS VCs.  
##############################################################################
def flap_mpls_vc(dut,flap_cmd):
	num = 1
	print("flapping mpls vc number......\n")
	for vc in dut.vc_db.vc_list:
		if flap_cmd == 'disable':
			cmd = 'mpls l2-vpn disable vc ' + vc['name']
		elif flap_cmd == 'enable':
			cmd = 'mpls l2-vpn enable vc ' + vc['name']
		else:
			print("invalid mpls vc command")
			return
		sw_send_cmd(dut, cmd)
		flush_print(num)
		num += 1

	update_mpls_vc_db(dut)       #upate mpls vc database after some commands
	print("\n-----------------------------------------------------------")
	print("After %s mpls vc, showing mpls l2-vpn statistics and details\n" % flap_cmd)
	dut.vc_db.mpls_vc_stat()
	#show mpls vpn after flapping vc next hops
	show_cmd(dut, 'mpls l2-vpn show',1)

##############################################################################
#    For now it is assumed egress tunnel at 5160_J DUT
##############################################################################
def flap_vc_nh(dut,flap_cmd):
	#dut.child.logfile_send = sys.stdout
	num = 1
	print("Flapping mpls vc next hops in the number of ......\n")
	for vcnh in dut.vc_db.vcnh_list:
		if flap_cmd == 'disable':
			cmd = 'gmpls tp-tunnel disable static-egress-corout ' + vcnh['name']
		elif flap_cmd == 'enable':
			cmd = 'gmpls tp-tunnel enable static-egress-corout ' + vcnh['name']
		else:
			print("invalid gmpls tunnel command")
			return
		sw_send_cmd(dut, cmd)
		flush_print(num)
		num += 1

	update_mpls_vc_db(dut)       #upate mpls vc database after some commands
	print("\n-----------------------------------------------------------")
	print("After %s mpls vc next hops, showing mpls l2-vpn statistics and details \n" % flap_cmd)
	dut.vc_db.mpls_vc_stat()
	#show mpls vpn after flapping vc next hops
	show_cmd(dut, 'mpls l2-vpn show',1)


def show_cmd (dut, cmd, cmd_num):
	#dut.child.logfile_send = sys.stdout
	dut.child.logfile_read = sys.stdout
	for i in range(cmd_num):
		sw_show_cmd(dut,cmd)
		sleep(2)
	dut.child.logfile_read = None

def port_stat_cmd (dut, stat_num):
	#dut.child.logfile_send = sys.stdout
	dut.child.logfile_read = sys.stdout
	sw_send_cmd(dut,'port clear statistics')
	for i in range(stat_num):
		result = sw_show_cmd(dut,'port show throughput active scale none')
		print result
		sleep(2)
	dut.child.logfile_read = None

def flush_print(vc_num):
    	stdout.write("\r%d" % vc_num)
    	stdout.flush()
    	sleep(0.005)
	#stdout.write("\n")

def sw_send_cmd_nowait(router,cmd):
     router.child.sendline(cmd)

def sw_send_cmd(router,cmd):
     #router.child.expect([router.prompt, router.prompt2])
     # turn off more for expecting the prompt
     router.child.logfile_read = None
     no_more = 'system shell set global-more off'
     more = 'system shell set global-more on'
     #router.child.sendline('\n')
     #router.child.expect([router.prompt2, router.prompt])
     #router.child.sendline(no_more)
     #router.child.expect([router.prompt2, router.prompt])
     router.child.sendline(cmd)
     #router.child.sendline('\n')
     router.child.expect([router.prompt2, router.prompt])
     # turn on more for manual CLI 
     #print 'in sw_send_cmd which one is matched %d' % i


def sw_show_cmd(router,cmd):
	lck = 'def_sw_show_cmd_file.lck'
	seek_lock(lck)
	router.child.logfile_read = None
	no_more = 'system shell set global-more off'
	router.child.sendline(no_more)
	router.child.expect([router.prompt2, router.prompt])
	router.child.sendline(cmd)
	router.child.expect([router.prompt2, router.prompt])
	result = router.child.before
	release_lock(lck)
	return result 

def sw_read_cmd(router, log_file, cmd):
	lck = 'def_sw_read_cmd_file.lck'
	seek_lock(lck)
	f = open(log_file,'w')
	router.child.logfile_read = f
	no_more = 'system shell set global-more off'
	router.child.sendline(no_more)
	router.child.expect([router.prompt2, router.prompt])
	router.child.sendline(cmd)
	#this line can not be deleted as it needs to wait for prompt to read result
	router.child.expect([router.prompt2, router.prompt])
	result = router.child.before
	#print "for debugging lsp display sw_read_cmd result = %s" % result
	f.close()
	release_lock(lck)
	return result 


#########################################################
#This is to read file into libary. This doesn't work yet
#  Currently it has bug.
#  Example: For the following file
#  City: Guangzhou
#  Name: Mike_Zheng
#  Age: 30
#
#  The output is:
#  {'': '', 'City : Guangzhou': '', 'Name:': 'Mike_Zheng', 'Age:': '30'}
##########################################################
 
def get_dictionary(filename):
    results = {}
    lck = 'def_get_dictionary_file.lck'
    seek_lock(lck)
    with open(filename, "r") as cache:
        # read file into a list of lines
        lines = cache.readlines()
        # loop through lines
        for line in lines:
            # skip lines starting with "--".
            if not line.startswith("--"):
                # replace random amount of spaces (\s) with tab (\t),
                # strip the trailing return (\n), split into list using
                # "\t" as the split pattern
                line = re.sub("\s\s+", "\t", line).strip().split("\t")
                # use first item in list for the key, join remaining list items
                # with ", " for the value.
                results[line[0]] = ", ".join(line[1:])
    release_lock(lck)
    return results

##########################################################
# This is a csv read procedure
##########################################################
def get_csv(filename):
    f = open (filename)
    csv_f = csv.reader(f)

def read_log_file(file,col):
	with open(file, mode = 'r') as infile:
		reader = csv.reader(infile)
		with open('test_temp.log', mode = 'w') as outfile:
			writer = csv.writer(outfile)
			for line in reader:
				print(line[col].strip())



############################################################################
#	Get mpls vc names -- This is hack for the time being
############################################################################:w
def get_mpls_vc_names(file):
	with open(file, mode = 'r') as infile:
		reader = csv.reader(infile)
		with open('test_temp.log', mode = 'w') as outfile:
			writer = csv.writer(outfile)
			for line in reader:
				print(line[4].strip())


########################################################################################
#   Read column in the csv file which saves 'show mpls vc'
########################################################################################
def create_vc_csv(file, csv_file, vc_str, lsp_str ):
	lck = 'def_create_vc_csv_file.lck'
	seek_lock(lck)
	open(csv_file,'w').writelines([ line for line in open(file) if vc_str in line])
	open(csv_file,'a').writelines([ line for line in open(file) if lsp_str in line])
	release_lock(lck)

##################################################################
#   process_log_file(filename)
#
#   Process log files: remove empty lines and unwanted characters
##################################################################

def process_log_file(filename):
	lck = 'def_process_log_file.lck'
	seek_lock(lck)
	remove_empty_line(filename)
	replace_word(filename,'|',',')
	replace_word(filename,'/',' ')
	release_lock(lck)

def remove_empty_line(file):
	lck = 'def_remove_empty_line.lck'
	f2 = open(file,'rw')
	f1 = open('test_test.log','w')
	data_str = f2.readlines()
	f2.close()
	#for lines in fileinput.FileInput(f2):
	for lines in data_str:
		lines = lines.rstrip()
		if lines == '':
			pass	
		else:
			f1.writelines(lines + '\n')
	f1.close()
	os.rename(file, file + '.bak' )
	os.rename(f1.name, file)
	release_lock(lck)

def del_empty_line(infile):
	lck = 'def_empty_line.lck'
	seek_lock(lck)
	with open(infile,'rw') as file:
		for line in file:
			if len(line) > 1 or line !='n' or line.strip():
				file.write(line)
	release_lock(lck)

def empty_line(filename):
	lck = 'def_empty_line.lck'
	seek_lock(lck)
	fh = open(filename,'r')
	data_str = fh.readlines()
	fh.close()
	mylist = data_str.split('\n')
	new_str = ""
	for item in mylist:
	    if item:
	        new_str += item + '\n'
	release_lock(lck)

###########################################################
#    replace word in a file 
###########################################################
def replace_word(infile,old_word,new_word):
    lck = 'def_replace_word.lck'
    seek_lock(lck)
    if not os.path.isfile(infile):
        print(("Error on replace_word, not a regular file: "+infile))
        sys.exit(1)

    f1=open(infile,'r').read()
    f2=open(infile,'w')
    m=f1.replace(old_word,new_word)
    f2.write(m) 
    release_lock(lck)


#def remove_logical_id(infile,outfile):
#	lck = 'def_remove_logical_id.lck'
#	seek_lock(lck)
#	if not os.path.isfile(infile):
#		print(("Error on replace_word, not a regular file: "+infile))
#		sys.exit(1)
#	f1 = open(infile,'r')
#	f2 = open(outfile,'w')
#	str = f1.read()
#	str2 = re.sub(r"logical-id .\d* ","",str)
#	f2.write(str2) 
#	f1.close()
#	f2.close()
#	release_lock(lck)

##########################################################
# get device ip and hostname
##########################################################
def get_switch(filename):
    f = open (filename)
    csv_f = csv.reader(f)
    for row in csv_f:
      print(row)

def get_show_bfd(dut):
	dut = dut
	cmd = 'bfd show'
	show_result = sw_show_cmd(dut,cmd)
	list = show_result.split('\n')
	global_list = get_head_block(list,'BFD GLOBAL')
	infor_list = get_head_block(list,'BFD SESSION')
	ipbfd_list = get_head_block(list,'IP BFD SESSION')
	lspbfd_list = get_head_block(list,'LSP BFD SESSION')
	profile_list = get_head_block(list,'BFD PROFILE')
	bfd_global_dict = {}	
	bfd_infor_dict = {}	
	bfd_ipbfd_dict = {}	
	bfd_lspbfd_dict = {}	
	bfd_profile_dict = {}	
	for line in global_list:
		key,val = line.split('|')
		bfd_global_dict[key.strip()] = val.strip()
	for line in infor_list:
		key,val = line.split('|')
		bfd_infor_dict[key.strip()] = val.strip()
	for line in ipbfd_list:
		key,val = line.split('|')
		bfd_ipbfd_dict[key.strip()] = val.strip()
	for line in lspbfd_list:
		key,val = line.split('|')
		bfd_lspbfd_dict[key.strip()] = val.strip()
	for line in profile_list:
		key,val = line.split('|')
		bfd_profile_dict[key.strip()] = val.strip()

def get_head_block(list,str):
	found = 0
	start = 0
	block = []
	for line in list:
		if str in line and found == 0:
			found = 1
			continue
		elif found == 1 and start == 0 and is_dash_line(line) == 'True':
			start = 1
			continue
		elif found == 1 and start == 1 and is_dash_line(line) == 'False':
			block.append(line)
			continue
		elif found == 1 and start == 1 and is_dash_line(line) == 'True': 
			#end of the block search
			break
	block = remove_crapy_line(block)
	return block


def get_vs_name_port(show_result):
	list = show_result.split('\n')
	attach_port_list = []
	port_cos_found = 0
	port_transform_found = 0
	list = remove_dash_line(list)
	port_dict = {}
	for line in list:
		line = line.strip('\r')
		line = line.strip('|')
		line = line.strip()
		if 'Encap Cos Policy' in line and port_cos_found == 0:
			port_cos_found = 1
			continue
		if port_cos_found == 1 and port_transform_found == 0:
			if 'no members' in line:
				port_dict['No Members'] = 'Yes'
				port_dict['name'] = ''
				port_dict['vlan'] = ''
				port_dict['encap_cos'] = ''
				port_dict['pri'] = ''
				port_dict['tpid'] = ''
				port_dict['intran'] = ''
				port_dict['etran'] = ''
				return port_dict
			else:
				port,vlan,encap_cos,pri,tpid = line.split('|')
				port_cos_found = 0
				continue
		if 'Ingress L2 Transform' in line and port_transform_found == 0:
			port_transform_found = 1
			continue
		if port_transform_found == 1 and port_cos_found == 0:
			port,vlan,intran,etran = line.split('|')
			break
	port_dict['No Members'] = 'No'
	port_dict['name'] = port.strip()
	port_dict['vlan'] = vlan.strip()
	port_dict['encap_cos'] = encap_cos.strip()
	port_dict['pri'] = pri.strip()
	port_dict['tpid'] = tpid.strip()
	port_dict['intran'] = intran.strip()
	port_dict['etran'] = etran.strip()
	return port_dict


def get_vs_name_vc(show_result):
	list = show_result.split('\n')
	attach_vc_list = []
	vc_found = 0
	vc_start = 0
	for line in list:
		vc_dict = {}
		line = line.strip('\r')
		line = line.strip('|')
		line = line.strip()
		if 'Virtual Circuits' not in line and vc_found == 0 and vc_start ==0:
			continue
		if 'Virtual Circuits' in line and vc_found == 0 and vc_start == 0:
			vc_found = 1
			continue
		if 'Name' in line and vc_found == 1 and vc_start == 0:
			continue
		if '-----' in line and vc_found == 1 and vc_start == 0:
			vc_start = 1
			continue
		if '----' in line and vc_found == 1 and vc_start == 1:
			return attach_vc_list
		if '----' not in line and vc_start == 1 and vc_found == 1:
			if 'No attached virtual circuits' in line:
				break
			vc_name,decap_label, encap_label = line.split('|')
			vc_dict['vc_name'] = vc_name.strip()
			vc_dict['decap_label'] = decap_label.strip()
			vc_dict['encap_label'] = encap_label.strip()
			attach_vc_list.append(vc_dict)
	return attach_vc_list


	
def show_vs(dut):
	cmd = 'virtual-switch show'
	show_result = sw_show_cmd(dut, cmd)
	list = show_result.split('\n')
	vs_list = []
	found = 0
	start = 0
	for line in list:
		vs_show = {}
		line = line.strip('\r')
		line = line.strip('|')
		line = line.strip()
		if 'Name' not in line and found == 0 and start == 0:
			continue
		if 'Name' in line and found == 0 and start == 0:
			found = 1
			continue
		if found == 1 and  '--------' in line and start == 0:
			start = 1
			continue
		if found == 1 and "------" in line and start == 1:
			break
		if found == 1 and '---' not in line and start == 1:
			name,cpt,mode,vc_count,ac_count,description = line.split('|')
			vs_show['name'] = name.strip()
			vs_show['cpt'] = cpt.strip()
			vs_show['vc_count'] = vc_count.strip()
			vs_show['ac_count'] = ac_count.strip()
			vs_show['mode'] = mode.strip()
			vs_show['description'] = description.strip()
			vs_list.append(vs_show)
	return vs_list


def get_each_vs(vs_list):
	pass

def turn_on_hw_bfd(dut):
	cmd = 'bfd disable'
	sw_send_cmd(dut,cmd)
	cmd = 'bfd set hw-acceleration on'
	sw_send_cmd(dut,cmd)
	cmd = 'bfd enable'
	sw_send_cmd(dut,cmd)
	cmd = 'bfd profile create profile hw-profile-lsp-0-3ms hw-acceleration enable transmit-interval 3.3msec receive-interval 3.3msec'
	dut.bfd_list.append('hw-profile-lsp-0-3ms')
	sw_send_cmd(dut,cmd)
	cmd = 'bfd profile create profile hw-profile-lsp-1-10ms hw-acceleration enable transmit-interval 10msec receive-interval 10msec'
	dut.bfd_list.append('hw-profile-lsp-1-10ms')
	sw_send_cmd(dut,cmd)
	# hw-profile-lsp-2 is the default profile with 100msec interval
	cmd = 'bfd profile create profile hw-profile-lsp-2 hw-acceleration enable transmit-interval 100msec receive-interval 100msec'
	dut.bfd_list.append('hw-profile-lsp-2')
	sw_send_cmd(dut,cmd)
	cmd = 'bfd profile create profile hw-profile-lsp-3-300ms hw-acceleration enable transmit-interval 300msec receive-interval 300msec'
	dut.bfd_list.append('hw-profile-lsp-3-300ms')
	sw_send_cmd(dut,cmd)
	cmd = 'bfd profile create profile hw-profile-lsp-4-1sec hw-acceleration enable transmit-interval 1sec receive-interval 1sec'
	dut.bfd_list.append('hw-profile-lsp-4-1sec')
	sw_send_cmd(dut,cmd)
	cmd = 'bfd profile create profile hw-profile-lsp-5-10sec hw-acceleration enable transmit-interval 10sec receive-interval 10sec'
	dut.bfd_list.append('hw-profile-lsp-5-10sec')
	sw_send_cmd(dut,cmd)

def turn_off_hw_bfd(dut):
	cmd = 'bfd disable'
	sw_send_cmd(dut,cmd)
	cmd = 'bfd set hw-acceleration off'
	sw_send_cmd(dut,cmd)
	cmd = 'bfd enable'
	sw_send_cmd(dut,cmd)

def collect_dut_vc(dut):
	vc_log = dut.host + '_vc' + '.log'
	vc_csv = dut.host + '_vc' + '.csv'

	lck = 'def_collect_dut_file.lck'
	seek_lock(lck)
	result = sw_show_cmd(dut, vc_log, 'mpls l2-vpn show')
	process_log_file(vc_log)   # Process the log file to remove not needed stuff
	vc_str = 'F00'             # The string being used to identify VC name
	lsp_str= 'Sta'             # The string being used to identify LSP name
	create_vc_csv(vc_log, vc_csv,vc_str, lsp_str)
	vc_db = mpls_vc(dut, vc_csv)
	dut.vc_db = vc_db
	vc_db.mpls_vc_stat()
	release_lock(lck)
	return vc_db


def turn_off_hw_bfd(dut):
	cmd = 'bfd disable'
	sw_send_cmd(dut,cmd)
	cmd = 'bfd set hw-acceleration off'
	sw_send_cmd(dut,cmd)
	cmd = 'bfd enable'
	sw_send_cmd(dut,cmd)

def collect_dut_vc(dut):
	vc_log = dut.host + '_vc' + '.log'
	vc_csv = dut.host + '_vc' + '.csv'
	result = sw_read_cmd(dut, vc_log, 'mpls l2-vpn show')
	process_log_file(vc_log)   # Process the log file to remove not needed stuff
	vc_str = 'F00'             # The string being used to identify VC name
	lsp_str= 'Sta'             # The string being used to identify LSP name
	create_vc_csv(vc_log, vc_csv,vc_str, lsp_str)
	vc_db = mpls_vc(dut, vc_csv)
	dut.vc_db = vc_db
	vc_db.mpls_vc_stat()

def show_macaddr(dut):
	cmd = 'flow show mac-addr'
	sw_send_cmd(dut,cmd)

def sw_log_cmd(self,cmd):
	no_more = 'system shell set global-more off'
	more = 'system shell set global-more on'
	self.child.sendline(cmd)
	self.child.expect([self.prompt2, self.prompt])
