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
import logging
import resource
from types import *
from switch_class import *
from utility import *
from time import sleep
#from lib import *

class mpls_l2vpn_vc:
	def __init__(self, dut,vc_name):
		logging.basicConfig(filename='class_mpls.log',filemode = 'a',level=logging.DEBUG,datefmt='%m/%d/%Y %I:%M:%S %p')
		self.attributes = []
		cmd = 'mpls l2-vpn show vc ' + vc_name
		show_result = sw_show_cmd(dut,cmd)
		list = show_result.split('\n')
		new_list = remove_crapy_line_2(list)
		self.dut = dut
		for line in new_list:
			if 'Pseudowire ID' in line:
					key, id = line.split('|')
					id = id.strip()
					self.Pseudowire_ID = int(id)
					#print "pseudowrie_id is %s" % self.Pseudowire_ID
					self.attributes.append(key)
					continue
			if 'Customer Name' in line:
					key, self.Customer_Name = line.split('|')
					self.Customer_Name = self.Customer_Name.strip()
					self.attributes.append(key)
					continue
			if 'Pseudowire Name' in line:
					key, self.Pseudowire_Name = line.split('|')
					self.Pseudowire_Name = self.Pseudowire_Name.strip()
					self.attributes.append(key)
					continue
			if 'Signaling Type' in line:
					key, self.Signaling_Type = line.split('|')
					self.attributes.append(key)
					continue
			if 'Pseudowire Admin State' in line:
					key, self.Pseudowire_Admin_State = line.split('|')
					self.attributes.append(key)
					continue
			if 'Operational State' in line:
					key, self.Operational_State = line.split('|')
					self.attributes.append(key)
					continue
			if 'Pseudowire Blocking' in line:
					key, self.Pseudowire_Blocking = line.split('|')
					self.attributes.append(key)
					continue
			if 'Remote Peer IP Address' in line:
					key, self.Remote_Peer_IP_Address = line.split('|')
					self.attributes.append(key)
					continue
			if 'Incoming Label' in line:
					key, Label = line.split('|')
					self.Incoming_Label = int(Label)
					self.attributes.append(key)
					continue
			if 'Outgoing Label' in line:
					key, Label = line.split('|')
					self.Outgoing_Label = int(Label)
					self.attributes.append(key)
					continue
			if 'Status TLV' in line:
					key, self.Status_TLV = line.split('|')
					self.attributes.append(key)
					continue
			if 'Refresh Status Interval' in line:
					key, self.Refresh_Status_Interval = line.split('|')
					self.attributes.append(key)
					continue
			if 'Local Fault' in line:
					key, self.Local_Fault = line.split('|')
					self.attributes.append(key)
					continue
			if 'Remote Fault' in line:
					key, self.Remote_Fault = line.split('|')
					self.attributes.append(key)
					continue
			if 'PW Bundle Index' in line:
					key, self.PW_Bundle_Index = line.split('|')
					self.attributes.append(key)
					continue
			if 'PW Reversion' in line:
					key, self.PW_Reversion = line.split('|')
					self.attributes.append(key)
					continue
			if 'Reversion hold-down time' in line:
					key, self.Reversion_hold_down_time = line.split('|')
					self.attributes.append(key)
					continue
			if 'PW Protection Role' in line:
					key, role = line.split('|')
					#key, self.PW_Protection_Role = line.split('|')
					self.PW_Protection_Role = role.strip()
					self.attributes.append(key)
					continue
			if 'PW Protection State' in line:
					#key, self.PW_Protection_State = line.split('|')
					key, State = line.split('|')
					self.PW_Protection_State = State.strip()
					self.attributes.append(key)
					continue
			if 'MTU Size' in line:
					key, self.MTU_Size = line.split('|')
					self.MTU_Size = self.MTU_Size.strip()
					self.attributes.append(key)
					continue
			if 'Pseudowire Type' in line:
					key, self.Pseudowire_Type = line.split('|')
					self.Pseudowire_Type = self.Pseudowire_Type.strip()
					self.attributes.append(key)
					continue
			if 'Pseudowire Mode' in line:
					key, self.Pseudowire_Mode  = line.split('|')
					self.Pseudowire_Mode = self.Pseudowire_Mode.strip()
					self.attributes.append(key)
					continue
			if 'Forward CoS Profile Name' in line:
					key, self.Forward_CoS_Profile_Name  = line.split('|')
					self.Forward_CoS_Profile_Name = self.Forward_CoS_Profile_Name.strip()
					self.attributes.append(key)
					continue
			if 'Forward CoS Profile Index' in line:
					key, self.Forward_CoS_Profile_Index  = line.split('|')
					self.Forward_CoS_Profile_Index = self.Forward_CoS_Profile_Index.strip()
					self.attributes.append(key)
					continue
			if 'Egress L2PT Transform' in line:
					key, self.Egress_L2PT_Transform  = line.split('|')
					self.attributes.append(key)
					continue
			if 'Forward Vccv Profile Name' in line:
					key, self.Forward_Vccv_Profile_Name  = line.split('|')
					self.attributes.append(key)
					continue
			if 'Forward Vccv Profile Index' in line:
					key, self.Forward_Vccv_Profile_Index  = line.split('|')
					self.attributes.append(key)
					continue
			if 'Local CC\:CV' in line:
					print line
					key, self.Local_CC_CV  = line.split('|')
					self.attributes.append(key)
					continue
			if 'Remote CC\:CV' in line:
					key, self.Remote_CC_CV  = line.split('|')
					self.attributes.append(key)
					continue
			if 'Operating CC\:CV' in line:
					key, self.Operating_CC_CV  = line.split('|')
					self.attributes.append(key)
					continue
			if 'Tunnel Virtual Interface' in line:
					key, self.Tunnel_Virtual_Interface  = line.split('|')
					self.attributes.append(key)
					continue
			if 'Virtual Switch Name' in line:
					key, self.Virtual_Switch_Name  = line.split('|')
					if self.Virtual_Switch_Name == '':
						logging.debug('The MPLS VC %s is not attached to any virtual switch',self.Pseudowire_Name)
						#print "the VC is not attached to any virtual-switch"
					self.attributes.append(key)
					continue
			if 'Failure Reason' in line:
					key, self.Failure_Reason  = line.split('|')
					self.attributes.append(key)
					continue
			if 'Status Frames Sent' in line:
					key, self.Status_Frames_Sent  = line.split('|')
					self.attributes.append(key)
					continue
			if 'Status Frames Received' in line:
					key, self.Status_Frames_Received  = line.split('|')
					self.attributes.append(key)
					continue
			if 'Status Acks Sent' in line:
					key, self.Status_Acks_Sent  = line.split('|')
					self.attributes.append(key)
					continue
			if 'Status Acks Received' in line:
					key, self.Status_Acks_Received  = line.split('|')
					self.attributes.append(key)
					continue
			if 'Status Bad PDUs Received' in line:
					key, self.Status_Bad_PDUs_Received  = line.split('|')
					self.attributes.append(key)
					continue
			if 'Status Bad Acks Received' in line:
					key, self.Status_Bad_Acks_Received  = line.split('|')
					self.attributes.append(key)
					continue
			if 'Mac Withdrawal Frames Sent' in line:
					key, self.Mac_Withdrawal_Frames_Sent  = line.split('|')
					self.attributes.append(key)
					continue
			if 'Mac Withdrawal Frames Received' in line:
					key, self.Mac_Withdrawal_Frames_Received  = line.split('|')
					self.attributes.append(key)
					continue
			if 'Mac Withdrawal Acks Sent' in line:
					key, self.Mac_Withdrawal_Acks_Sent  = line.split('|')
					self.attributes.append(key)
					continue
			if 'Mac Withdrawal Acks Received' in line:
					key, self.Mac_Withdrawal_Acks_Received  = line.split('|')
					self.attributes.append(key)
					continue
			if 'Mac Withdrawal Bad PDUs Received' in line:
					key, self.Mac_Withdrawal_Bad_PDUs_Received  = line.split('|')
					self.attributes.append(key)
					continue
			if 'Mac Withdrawal Bad Acks Received' in line:
					key, self.Mac_Withdrawal_Bad_Acks_Received  = line.split('|')
					self.attributes.append(key)
					continue
			if 'Mac Withdrawal Sent Sequence Number' in line:
					key, self.Mac_Withdrawal_Sent_Sequence_Number  = line.split('|')
					self.attributes.append(key)
					continue
			if 'Mac Withdrawal Received Sequence Number' in line:
					key, self.Mac_Withdrawal_Received_Sequence_Number  = line.split('|')
					self.attributes.append(key)
					continue
		
		
	def protection_switchover(self):
		if self.PW_Protection_Role == 'Primary' and self.PW_Protection_State == 'Active':
			cmd = 'mpls l2-vpn protection switchover static-vc ' + self.Pseudowire_Name + ' on'
			sw_send_cmd(self.dut, cmd)
		if self.PW_Protection_Role == 'Primary' and self.PW_Protection_State == 'Manual SWO Standby':
			cmd = 'mpls l2-vpn protection switchover static-vc ' + self.Pseudowire_Name + ' off'
			sw_send_cmd(self.dut, cmd)
	

class mpls_l2vpn:
	def __init__(self, dut):
		self.dut = dut
		self.host = dut.host
		self.vc_list =[]
		self.nh_list = []
		self.vc_list_up = []
		self.vc_list_b = []
		self.num_of_vc = 0
		self.down = 0
		self.up = 0
		self.nh_up = 0
		self.nh_down = 0
		self.nh_downloaded = 0
		self.nh_not_downloaded = 0
		self.mpls_instances_list= []
		self.mpls_vc_lck = dut.host + '_mpls_vc' + '.lck'
		
		#this method will populate the vc_list and nh_list
		self.get_show_mpls_l2vpn()
		self.mpls_l2vpn_stats()

	def mpls_l2vpn_stats(self):
		logging.basicConfig(filename='class_mpls.log',filemode = 'w',level=logging.DEBUG,datefmt='%m/%d/%Y %I:%M:%S %p')
		logging.debug('Collecting stats of mpls l2vpn')
		for vc in self.vc_list:
			self.num_of_vc += 1
			if vc['flags'] == 'sDMoB' :
				self.down += 1
				self.vc_list_b.append(vc)
			elif vc['flags'] ==  'sDSbB':
				self.down += 1
				self.vc_list_b.append(vc)
			elif vc['flags'] ==  'sDSaB':
				self.down += 1
				self.vc_list_b.append(vc)
			else:
				self.up += 1
				self.vc_list_up.append(vc)

		for nh in self.nh_list:
			if nh['oper'] == 'Dn':
				self.nh_down += 1
			else:
				self.nh_up += 1

			if nh['downloaded'] == 'Yes':
				self.nh_downloaded += 1
			else:
				self.nh_not_downloaded += 1
				logging.warning('PW next hop %s is NOT downloaded!',nh['name'])
			

	def protection_switchover_all(self):
		print_line_step('start manually switchover mpls vc')
		for pw in self.mpls_instances_list:
			pw.protection_switchover()


	def build_mpls_l2vpn_instances(self):
		i = 0
		for vc in self.vc_list:
			vc_obj = mpls_l2vpn_vc(self.dut,vc['name'])
			self.mpls_instances_list.append(vc_obj)
			i = i  + 1
		print "total vc instances are: %d" % i


	def get_show_mpls_l2vpn(self):
		cmd = 'mpls l2-vpn show'
		dut = self.dut
		show_result = sw_show_cmd(dut,cmd)
		list = show_result.split('\n')
		pw_line_list = []
		nh_line_list = []
		vc_list = []
		nh_list = []
		
		pw_line_list = get_head_block(list,'PW  ID')
		nh_line_list = get_head_block(list,'NextHop')
		for line in pw_line_list:
			vc_dict = {}
			type, nh, id, name, customer, peer, in_label, out_label, flags = line.split('|')
			vc_dict['next hop'] = nh.strip()
			vc_dict['id'] = id.strip()
			vc_dict['name'] = name.strip()
			vc_dict['customer'] = customer.strip()
			vc_dict['peer'] = peer.strip()
			vc_dict['in_label'] = in_label.strip()
			vc_dict['out_label'] = out_label.strip()
			vc_dict['flags'] = flags.strip()
			vc_list.append(vc_dict)
		self.vc_list = vc_list

		for line in nh_line_list:
			nh_dict = {}
			index, nh,vif,oper,downloaded,name = line.split('|')
			nh_dict['index'] = index.strip()
			nh_dict['nh'] = nh.strip()
			nh_dict['vif'] = vif.strip()
			nh_dict['oper'] = oper.strip()
			nh_dict['downloaded'] = downloaded.strip()
			nh_dict['name'] = name.strip()
			nh_list.append(nh_dict)
		self.nh_list = nh_list

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

	def mpls_vc_stats(self):
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
		
