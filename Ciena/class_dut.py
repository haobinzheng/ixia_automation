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
from switch_class import *
from class_mpls import *
from lib import *

class CN_5142_A(cienaswitch):
	def __init__(self,router):
		cienaswitch.__init__(self,router)
		self.vc_2C_name_list = []
		self.vc_2B_name_list = []
		self.vs_name_list = []

	def upgrade(self,build):
		cmd = 'software upgrade package saos-06-13-00-0' + build + ' tftp-server 10.25.34.238 package-path ciena/packages/saos-06-13-00-0' + build + ' service-disruption allow'
		sw_send_cmd(self,cmd)

	def configuration_attach_vs(self,num):
		for i in range(0,num):
			if i == 1000:
				sleep(20)
			if i == 2000:
				sleep(20)
			if i == 2500:
				sleep(20)
			if i == 2800:
				sleep(20)
			if i == 2900:
				sleep(10)
			cmd1 = 'virtual-switch ethernet attach mpls-vc ' + self.vc_2C_name_list[i] + ' vs ' + self.vs_name_list[i]	
			cmd2 = 'virtual-switch ethernet attach mpls-vc ' + self.vc_2B_name_list[i] + ' vs ' + self.vs_name_list[i]	
			print cmd1
			print cmd2
			sw_send_cmd(self,cmd1)
			sw_send_cmd(self,cmd2)

	def configuration_attach_port(self,num):
		vlan_base = 100 
		for i in range(0,num):
			if i == 1000:
				sleep(20)
			if i == 2000:
				sleep(20)
			if i == 2500:
				sleep(20)
			if i == 2800:
				sleep(20)
			if i == 2900:
				sleep(10)
			vlan = str(vlan_base + i)
			cmd1 = 'virtual-switch ethernet add vs ' + self.vs_name_list[i] + ' port 23 vlan ' + vlan	
			print cmd1
			sw_send_cmd(self,cmd1)
		
	def mis_configuration_attach_vs(self,num):
		for i in range(0,num):
			cmd1 = 'virtual-switch ethernet attach mpls-vc ' + self.vc_2C_name_list[i] + 'mis' + ' vs ' + self.vs_name_list[i]	
			cmd2 = 'virtual-switch ethernet attach mpls-vc ' + self.vc_2B_name_list[i] + 'mis' + ' vs ' + self.vs_name_list[i]	
			sw_send_cmd(self,cmd1)
			sw_send_cmd(self,cmd2)

	def configuration_vs(self,num):
		vs_name_num = 0
		vs_name_base = 'VS-F001-S'
		for i in range(0,num):
			if i == 1000:
				sleep(20)
			if i == 2000:
				sleep(20)
			if i == 2500:
				sleep(20)
			if i == 2800:
				sleep(20)
			if i == 2900:
				sleep(10)
			vs_name_num = vs_name_num + 1
			#print "vs_name_num = %d" % vs_name_num
			vs_name_num_str = "%04i" % vs_name_num
			vs_name_str = vs_name_base + vs_name_num_str
			self.vs_name_list.append(vs_name_str)
			cmd = 'virtual-switch ethernet create vs ' + vs_name_str + ' mode vpls'
			print cmd
			sw_send_cmd(self,cmd)
			
	def configuration_pw(self,num):
		pw_C_A_1 = mpls_l2vpn_vc(self,'C->A-F001-S0001')
		pw_A_B_1 = mpls_l2vpn_vc(self,'A->B-F001-S0001')
		#change this line to decide where to start with incoming label
		c_a_vc_name_base = 'C->A-F001-S'
		c_a_lsp_name_base = 'Pri-Sta-Co-8700C-->5142A-'
		c_a_vc_id_base = 1
		c_a_lsp_id_base = 1
		pw_id_base = pw_C_A_1.Pseudowire_ID
		print "pw_C_A_1.Incoming_Label = %d" % pw_C_A_1.Incoming_Label
		print "pw_C_A_1.Outgoing_Label = %d" % pw_C_A_1.Outgoing_Label
		print "pw_C_A_1.Pseudowire_ID  = %d" % pw_C_A_1.Pseudowire_ID
		print "pw_C_A_1.Remote_Peer_IP_Address = %s" % pw_C_A_1.Remote_Peer_IP_Address
		pw_C_A_1.Incoming_Label= 206001
		pw_C_A_1.Outgoing_Label= 206001
		pw_C_A_1.Pseudowire_ID = 206001
		pw_C_A_1.Remote_Peer_IP_Address = '10.11.99.123'
		c_a_in_label_base = pw_C_A_1.Incoming_Label
		c_a_out_label_base = pw_C_A_1.Outgoing_Label
		#now only use lsp number 1 -- 10. If going forward more LSP will be used, change
		#this following line
		lsp_iteration = 10
		lsp_num = 0
		for i in range(0,num):
			if i == 500:
				pw_C_A_1.Incoming_Label= 230001
				pw_C_A_1.Outgoing_Label= 230001
				pw_C_A_1.Pseudowire_ID = 230001
				c_a_in_label_base = pw_C_A_1.Incoming_Label
				c_a_out_label_base = pw_C_A_1.Outgoing_Label
				pw_id_base = pw_C_A_1.Pseudowire_ID
			if i == 1000:
				sleep(20)
			if i == 2000:
				sleep(20)
			if i == 2500:
				sleep(20)
			if i == 2800:
				sleep(20)
			if i == 2900:
				sleep(10)
			c_a_vc_id = c_a_vc_id_base + i
			c_a_in_label = c_a_in_label_base + i
			c_a_out_label = c_a_out_label_base + i
			lsp_num = lsp_num + 1
			lsp_num_used = lsp_num
			if lsp_num == lsp_iteration:
				lsp_num = 0	
			pw_id = pw_id_base + i
			vc_name_num_str = "%04i" % c_a_vc_id
			lsp_num_str = "%03i" % lsp_num_used

			c_a_vc_name_str = c_a_vc_name_base + vc_name_num_str
			pw_id_str = str(pw_id)
			peer_str = pw_C_A_1.Remote_Peer_IP_Address
			c_a_in_label_str = str(c_a_in_label)
			c_a_out_label_str = str(c_a_out_label)
			lsp_name_str = c_a_lsp_name_base + lsp_num_str
			self.vc_2C_name_list.append(c_a_vc_name_str)
			cmd = 'mpls l2-vpn create static-vc ' + c_a_vc_name_str + ' pw-id ' + pw_id_str + ' peer ' + peer_str + ' in-label ' + c_a_in_label_str + ' out-label ' + c_a_out_label_str + ' tp-tunnel-egrs-corout-static ' + lsp_name_str  + ' pw-mode spoke status-tlv on ' 
			print cmd		
			sw_send_cmd(self,cmd)


		print pw_A_B_1.Pseudowire_Name
		print pw_A_B_1.Remote_Peer_IP_Address
		print pw_A_B_1.Incoming_Label
		print pw_A_B_1.Pseudowire_ID
		print pw_A_B_1.Incoming_Label
		print pw_A_B_1.Outgoing_Label
		print pw_A_B_1.Outgoing_Label
		pw_A_B_1.Remote_Peer_IP_Address = '10.11.99.122'
		pw_A_B_1.Incoming_Label = 200101
		pw_A_B_1.Outgoing_Label = 200101
		pw_A_B_1.Pseudowire_ID = 200101
		#change this line to decide where to start with incoming label
		in_label_base = pw_A_B_1.Incoming_Label 
		out_label_base = pw_A_B_1.Outgoing_Label
		vc_name_base = 'A->B-F001-S'
		lsp_name_base = 'Pri-Sta-Co-5142A-->8700B-'
		prime_vc_base = 'C->A-F001-S'
		vc_id_base = 1
		lsp_id_base = 1
		pw_id_base = pw_A_B_1.Pseudowire_ID
		#now only use lsp number 1 -- 10. If going forward more LSP will be used, change
		#this following line
		lsp_iteration = 10
		lsp_num = 0
		for i in range(0,num):
			if i == 900:
				pw_A_B_1.Incoming_Label = 235001
				pw_A_B_1.Outgoing_Label = 235001
				pw_A_B_1.Pseudowire_ID =  235001
				in_label_base = pw_A_B_1.Incoming_Label
				out_label_base = pw_A_B_1.Outgoing_Label
				pw_id_base = pw_A_B_1.Pseudowire_ID
			if i == 1000:
				sleep(20)
			if i == 2000:
				sleep(20)
			if i == 2500:
				sleep(20)
			if i == 2800:
				sleep(20)
			if i == 2900:
				sleep(10)
			vc_id = vc_id_base + i
			in_label = in_label_base + i
			out_label = out_label_base + i
			lsp_num = lsp_num + 1
			lsp_num_used = lsp_num
			if lsp_num == lsp_iteration:
				lsp_num = 0	
			pw_id = pw_id_base + i
			vc_name_num_str = "%04i" % vc_id
			lsp_num_str = "%03i" % lsp_num_used

			vc_name_str = vc_name_base + vc_name_num_str
			prime_vc_str = prime_vc_base + vc_name_num_str
			pw_id_str = str(pw_id)
			peer_str = pw_A_B_1.Remote_Peer_IP_Address
			in_label_str = str(in_label)
			out_label_str = str(out_label)
			lsp_name_str = lsp_name_base + lsp_num_str
			self.vc_2B_name_list.append(vc_name_str)
			cmd = 'mpls l2-vpn protection create static-vc ' + vc_name_str + ' primary-vc-name ' + prime_vc_str + ' secondary-pw-id ' + pw_id_str + ' peer ' + peer_str + ' in-label ' + in_label_str + ' out-label ' + out_label_str + ' tp-tunnel-ingr-corout ' + lsp_name_str 
			print cmd		
			sw_send_cmd(self,cmd)
		


class CN_8700_C(cienaswitch):
	def __init__(self,router):
		cienaswitch.__init__(self,router)
		self.vc_name_list = []
		self.vs_name_list = []

	def configuration_attach_vs(self,num):
		for i in range(0,num):
			if i == 1000:
				sleep(20)
			if i == 2000:
				sleep(20)
			if i == 2500:
				sleep(20)
			if i == 2800:
				sleep(20)
			if i == 2900:
				sleep(10)
			#print self.vc_name_list[i]
			#print self.vs_name_list[i]
			cmd1 = 'virtual-switch interface attach mpls-vc ' + self.vc_name_list[i] + ' vs ' + self.vs_name_list[i]	
			print cmd1
			sw_send_cmd(self,cmd1)

	def configuration_vs(self,num):
		vs_name_num = 0
		vs_name_base = 'VS-F001-S'
		for i in range(0,num):
			if i == 1000:
				sleep(20)
			if i == 2000:
				sleep(20)
			if i == 2500:
				sleep(20)
			if i == 2800:
				sleep(20)
			if i == 2900:
				sleep(10)
			vs_name_num = vs_name_num + 1
			#print "vs_name_num = %d" % vs_name_num
			vs_name_num_str = "%04i" % vs_name_num
			vs_name_str = vs_name_base + vs_name_num_str
			self.vs_name_list.append(vs_name_str)
			#print self.vs_name_list
			cmd = 'virtual-switch create vs ' + vs_name_str 
			print cmd
			sw_send_cmd(self,cmd)

	def configuration_pw(self,num):
		pw_C_A_1 = mpls_l2vpn_vc(self,'C->A-F001-S0001')
		#change this line to decide where to start with incoming label
		print "pw_C_A_1.Incoming_Label = %s " % pw_C_A_1.Incoming_Label
		print "pw_C_A_1.Outgoing_Label = %s " % pw_C_A_1.Outgoing_Label
		print "pw_C_A_1.Pseudowire_ID = %s " % pw_C_A_1.Pseudowire_ID
		print "peer ip address  = %s" %  pw_C_A_1.Remote_Peer_IP_Address
		c_a_in_label_base = pw_C_A_1.Incoming_Label 
		c_a_out_label_base = pw_C_A_1.Outgoing_Label
		c_a_vc_name_base = 'C->A-F001-S'
		c_a_lsp_name_base = 'Pri-Sta-Co-8700C-->5142A-'
		c_a_vc_id_base = 1
		c_a_lsp_id_base = 1
		pw_id_base = pw_C_A_1.Pseudowire_ID
		#now only use lsp number 1 -- 10. If going forward more LSP will be used, change
		#this following line
		lsp_iteration = 10
		lsp_num = 0
		for i in range(0,num):
			if i == 500:
				pw_C_A_1.Incoming_Label= 230001
				pw_C_A_1.Outgoing_Label= 230001
				pw_C_A_1.Pseudowire_ID = 230001
				c_a_in_label_base = pw_C_A_1.Incoming_Label
				c_a_out_label_base = pw_C_A_1.Outgoing_Label
				pw_id_base = pw_C_A_1.Pseudowire_ID
			if i == 1000:
				sleep(20)
			if i == 2000:
				sleep(20)
			if i == 2500:
				sleep(20)
			if i == 2800:
				sleep(20)
			if i == 2900:
				sleep(10)
			c_a_vc_id = c_a_vc_id_base + i
			c_a_in_label = c_a_in_label_base + i
			c_a_out_label = c_a_out_label_base + i
			lsp_num = lsp_num + 1
			lsp_num_used = lsp_num
			if lsp_num == lsp_iteration:
				lsp_num = 0	
			pw_id = pw_id_base + i
			vc_name_num_str = "%04i" % c_a_vc_id
			lsp_num_str = "%03i" % lsp_num_used

			c_a_vc_name_str = c_a_vc_name_base + vc_name_num_str
			self.vc_name_list.append(c_a_vc_name_str)
			pw_id_str = str(pw_id)
			peer_str = pw_C_A_1.Remote_Peer_IP_Address
			c_a_in_label_str = str(c_a_in_label)
			c_a_out_label_str = str(c_a_out_label)
			lsp_name_str = c_a_lsp_name_base + lsp_num_str
			cmd = 'mpls l2-vpn create static-vc ' + c_a_vc_name_str + ' pw-id ' + pw_id_str + ' peer ' + peer_str + ' in-label ' + c_a_in_label_str + ' out-label ' + c_a_out_label_str + ' tp-tunnel-ingr-corout ' + lsp_name_str  + ' pw-mode spoke status-tlv on ' 
			print cmd		
			sw_send_cmd(self,cmd)

class CN_8700_B(cienaswitch):
	def __init__(self,router):
		cienaswitch.__init__(self,router)
		self.vc_name_list = []
		self.vs_name_list = []

	def configuration_attach_vs(self,num):
		for i in range(0,num):
			if i == 1000:
				sleep(20)
			if i == 2000:
				sleep(20)
			if i == 2500:
				sleep(20)
			if i == 2800:
				sleep(20)
			if i == 2900:
				sleep(10)
			cmd1 = 'virtual-switch interface attach mpls-vc ' + self.vc_name_list[i] + ' vs ' + self.vs_name_list[i]	
			print cmd1
			sw_send_cmd(self,cmd1)

	def configuration_vs(self,num):
		vs_name_num = 0
		vs_name_base = 'VS-F001-S'
		for i in range(0,num):
			if i == 1000:
				sleep(20)
			if i == 2000:
				sleep(20)
			if i == 2500:
				sleep(20)
			if i == 2800:
				sleep(20)
			if i == 2900:
				sleep(10)
			vs_name_num = vs_name_num + 1
			print "vs_name_num = %d" % vs_name_num
			vs_name_num_str = "%04i" % vs_name_num
			vs_name_str = vs_name_base + vs_name_num_str
			self.vs_name_list.append(vs_name_str)
			cmd = 'virtual-switch create vs ' + vs_name_str 
			print cmd
			sw_send_cmd(self,cmd)

	def configuration_pw(self,num):
		pw_A_B_1 = mpls_l2vpn_vc(self,'A->B-F001-S0001')

		print pw_A_B_1.Pseudowire_Name
		print pw_A_B_1.Remote_Peer_IP_Address
		print pw_A_B_1.Incoming_Label
		print pw_A_B_1.Pseudowire_ID
		print pw_A_B_1.Incoming_Label
		print pw_A_B_1.Outgoing_Label
		print pw_A_B_1.Outgoing_Label
		print "pw_A_B_1.Incoming_Label = %s " % pw_A_B_1.Incoming_Label
		print "pw_A_B_1.Outgoing_Label = %s " % pw_A_B_1.Outgoing_Label
		print "pw_A_B_1.Pseudowire_ID = %s " % pw_A_B_1.Pseudowire_ID
		print "peer IP address = %s" % pw_A_B_1.Remote_Peer_IP_Address
		#change the following lines to decide where to start with incoming label
		pw_A_B_1.Incoming_Label = 200101
		pw_A_B_1.Outgoing_Label = 200101
		pw_A_B_1.Pseudowire_ID = 200101
		in_label_base = pw_A_B_1.Incoming_Label 
		out_label_base = pw_A_B_1.Outgoing_Label
		pw_A_B_1.Remote_Peer_IP_Address = '10.11.99.121'
		peer_str = pw_A_B_1.Remote_Peer_IP_Address
		vc_name_base = 'A->B-F001-S'
		lsp_name_base = 'Pri-Sta-Co-5142A-->8700B-'
		vc_id_base = 1
		lsp_id_base = 1
		pw_id_base = pw_A_B_1.Pseudowire_ID
		#now only use lsp number 1 -- 10. If going forward more LSP will be used, change
		#this following line
		lsp_iteration = 10
		lsp_num = 0
		for i in range(0,num):
			if i == 900:
				pw_A_B_1.Incoming_Label = 235001
				pw_A_B_1.Outgoing_Label = 235001
				pw_A_B_1.Pseudowire_ID =  235001
				in_label_base = pw_A_B_1.Incoming_Label
				out_label_base = pw_A_B_1.Outgoing_Label
				pw_id_base = pw_A_B_1.Pseudowire_ID
			if i == 1000:
				sleep(20)
			if i == 2000:
				sleep(20)
			if i == 2500:
				sleep(20)
			if i == 2800:
				sleep(20)
			if i == 2900:
				sleep(10)
			vc_id = vc_id_base + i
			in_label = in_label_base + i
			out_label = out_label_base + i
			lsp_num = lsp_num + 1
			lsp_num_used = lsp_num
			if lsp_num == lsp_iteration:
				lsp_num = 0	
			pw_id = pw_id_base + i
			vc_name_num_str = "%04i" % vc_id
			lsp_num_str = "%03i" % lsp_num_used

			vc_name_str = vc_name_base + vc_name_num_str
			self.vc_name_list.append(vc_name_str)
			pw_id_str = str(pw_id)
			peer_str = pw_A_B_1.Remote_Peer_IP_Address
			in_label_str = str(in_label)
			out_label_str = str(out_label)
			lsp_name_str = lsp_name_base + lsp_num_str
			cmd = 'mpls l2-vpn create static-vc ' + vc_name_str + ' pw-id ' + pw_id_str + ' peer ' + peer_str + ' in-label ' + in_label_str + ' out-label ' + out_label_str + ' tp-tunnel-egrs-corout-static ' + lsp_name_str  + ' pw-mode spoke status-tlv on ' 
			print cmd		
			sw_send_cmd(self,cmd)


class CN_5160_J(cienaswitch):
	def __init__(self,router):
		cienaswitch.__init__(self,router)
		self.vc_2D_name_list = []
		self.vc_2E_name_list = []
		self.vs_name_list = []

	def configuration_vs(self,num):
		vs_name_num = 0
		vs_name_base = 'VS-F001-S'
		for i in range(0,num):
			if i == 1000:
				sleep(20)
			if i == 2000:
				sleep(20)
			if i == 2500:
				sleep(20)
			if i == 2800:
				sleep(20)
			if i == 2900:
				sleep(10)
			vs_name_num = vs_name_num + 1
			#print "vs_name_num = %d" % vs_name_num
			vs_name_num_str = "%04i" % vs_name_num
			vs_name_str = vs_name_base + vs_name_num_str
			self.vs_name_list.append(vs_name_str)
			cmd = 'virtual-switch ethernet create vs ' + vs_name_str + ' mode vpls'
			print cmd
			sw_send_cmd(self,cmd)


	def configuration_attach_vs(self,num):
		for i in range(0,num):
			cmd1 = 'virtual-switch ethernet attach mpls-vc ' + self.vc_2D_name_list[i] + ' vs ' + self.vs_name_list[i]	
			cmd2 = 'virtual-switch ethernet attach mpls-vc ' + self.vc_2E_name_list[i] + ' vs ' + self.vs_name_list[i]	
			print cmd1
			print cmd2
			sw_send_cmd(self,cmd1)
			sw_send_cmd(self,cmd2)

	def configuration_attach_port(self,num):
		vlan_base = 100
		for i in range(0,num):
			vlan = str(vlan_base + i)
			cmd1 = 'virtual-switch ethernet add vs ' + self.vs_name_list[i] + ' port 3 vlan ' + vlan	
			print cmd1
			sw_send_cmd(self,cmd1)

	def upgrade(self,build):
		cmd = 'software upgrade package saos-06-13-00-0' + build + ' tftp-server 10.25.34.238 package-path ciena/packages/saos-06-13-00-0' + build + ' service-disruption allow'
		sw_send_cmd(self,cmd)

	def configuration_pw(self,num):
		pw_D = mpls_l2vpn_vc(self,'D->J-F001-S0001')
		pw_E = mpls_l2vpn_vc(self,'J->E-F001-S0001')
		#change this line to decide where to start with incoming label
		D_vc_name_base = 'D->J-F001-S'
		D_lsp_name_base = 'Pri-Sta-Co-8700D-->5160J-'
		print "pw_D.Incoming_Label = %d" % pw_D.Incoming_Label
		print "pw_D.Outgoing_Label = %d" % pw_D.Outgoing_Label
		print "pw_D.Pseudowire_ID  = %d" % pw_D.Pseudowire_ID
		print "pw_D.Remote_Peer_IP_Address = %s" % pw_D.Remote_Peer_IP_Address
		pw_D.Incoming_Label = 216601
		pw_D.Outgoing_Label = 216601
		pw_D.Pseudowire_ID  = 216601
		pw_D.Remote_Peer_IP_Address =  '10.11.99.124'
		#pw_C_A_1.Incoming_Label= 206001
		#pw_C_A_1.Outgoing_Label= 206001
		#pw_C_A_1.Pseudowire_ID = 206001
		#pw_C_A_1.Remote_Peer_IP_Address = '10.11.99.123'
		D_in_label_base = pw_D.Incoming_Label
		D_out_label_base = pw_D.Outgoing_Label
		peer_str = pw_D.Remote_Peer_IP_Address
		#now only use lsp number 1 -- 10. If going forward more LSP will be used, change
		#this following line
		vc_id_base = 1
		lsp_id_base = 1
		vc_name_base = D_vc_name_base
		lsp_name_base = D_lsp_name_base
		pw_id_base = pw_D.Pseudowire_ID
		in_label_base = pw_D.Incoming_Label
		out_label_base = pw_D.Outgoing_Label
		lsp_iteration = 62
		lsp_num = 0
		for i in range(0,num):
			if i == 500:
				sleep(10)
			if i == 1000:
				sleep(20)
			if i == 2000:
				sleep(20)
			if i == 2500:
				sleep(20)
			if i == 2800:
				sleep(20)
			if i == 2900:
				sleep(10)
			vc_id = vc_id_base + i
			in_label = in_label_base + i
			out_label = out_label_base + i
			lsp_num = lsp_num + 1
			lsp_num_used = lsp_num
			if lsp_num == lsp_iteration:
				lsp_num = 0	
			pw_id = pw_id_base + i
			vc_name_num_str = "%04i" % vc_id
			lsp_num_str = "%03i" % lsp_num_used

			vc_name_str = vc_name_base + vc_name_num_str
			pw_id_str = str(pw_id)
			in_label_str = str(in_label)
			out_label_str = str(out_label)
			lsp_name_str = lsp_name_base + lsp_num_str
			self.vc_2D_name_list.append(vc_name_str)
			cmd = 'mpls l2-vpn create static-vc ' + vc_name_str + ' pw-id ' + pw_id_str + ' peer ' + peer_str + ' in-label ' + in_label_str + ' out-label ' + out_label_str + ' tp-tunnel-egrs-corout-static ' + lsp_name_str  + ' pw-mode spoke status-tlv on ' 
			print cmd		
			sw_send_cmd(self,cmd)


		#Configuration of protection PW
		print "pw_E.Incoming_Label = %d" % pw_E.Incoming_Label
		print "pw_E.Outgoing_Label = %d" % pw_E.Outgoing_Label
		print "pw_E.Pseudowire_ID  = %d" % pw_E.Pseudowire_ID
		print "pw_E.Remote_Peer_IP_Address = %s" % pw_E.Remote_Peer_IP_Address
		E_in_label_base = pw_E.Incoming_Label
		E_out_label_base = pw_E.Outgoing_Label
		pw_id_base = pw_E.Pseudowire_ID
		peer_str = pw_E.Remote_Peer_IP_Address
		in_label_base = pw_E.Incoming_Label 
		out_label_base = pw_E.Outgoing_Label
		vc_name_base = 'J->E-F001-S'
		lsp_name_base = 'Pri-Sta-Co-5160J-->8700E-'
		prime_vc_base = 'D->J-F001-S'
		vc_id_base = 1
		lsp_id_base = 1
		#now only use lsp number 1 -- 10. If going forward more LSP will be used, change
		#this following line
		lsp_iteration = 62 
		lsp_num = 0
		for i in range(0,num):
			if i == 500:
				sleep(10)
			if i == 1000:
				sleep(20)
			if i == 2000:
				sleep(20)
			if i == 2500:
				sleep(20)
			if i == 2800:
				sleep(20)
			if i == 2900:
				sleep(10)
			vc_id = vc_id_base + i
			in_label = in_label_base + i
			out_label = out_label_base + i
			lsp_num = lsp_num + 1
			lsp_num_used = lsp_num
			if lsp_num == lsp_iteration:
				lsp_num = 0	
			pw_id = pw_id_base + i
			vc_name_num_str = "%04i" % vc_id
			lsp_num_str = "%03i" % lsp_num_used

			vc_name_str = vc_name_base + vc_name_num_str
			prime_vc_str = prime_vc_base + vc_name_num_str
			pw_id_str = str(pw_id)
			in_label_str = str(in_label)
			out_label_str = str(out_label)
			lsp_name_str = lsp_name_base + lsp_num_str
			self.vc_2E_name_list.append(vc_name_str)
			cmd = 'mpls l2-vpn protection create static-vc ' + vc_name_str + ' primary-vc-name ' + prime_vc_str + ' secondary-pw-id ' + pw_id_str + ' peer ' + peer_str + ' in-label ' + in_label_str + ' out-label ' + out_label_str + ' tp-tunnel-ingr-corout ' + lsp_name_str
			print cmd
			sw_send_cmd(self,cmd)


	def change_port_mtu(self,port,mtu):
		cmd = 'port set port ' + port + ' max-frame-size ' + mtu
		self.sw_send_cmd(cmd)	
	
	def sweep_port_mtu(self,port):
		for i in range(1522,9216):
			self.change_port_mtu(port,str(i))

	def sweep_active_port_mtu(self):
		port = [1,2,3]
		for p in port:
			self.sweep_port_mtu(str(p))
			sleep(2)

	def disable_ports(self):
		port = [1,2,3]
		for p in port:
			cmd = 'port disable port ' + str(p)
			self.sw_send_cmd(cmd)
			sleep(30)
	
	def enable_ports(self):
		port = [1,2,3]
		for p in port:
			cmd = 'port enable port ' + str(p)
			self.sw_send_cmd(cmd)
			sleep(30)

class CN_5142_F(cienaswitch):
	def __init__(self,router):
		cienaswitch.__init__(self,router)

	def sweep_active_port_mtu(self):
		port = [22,21]
		for p in port:
			self.sweep_port_mtu(str(p))
			sleep(2)

	def disable_ports(self):
		port = [21,22]
		for p in port:
			cmd = 'port disable port ' + str(p)
			self.sw_send_cmd(cmd)
			sleep(30)
	
	def enable_ports(self):
		port = [21,22]
		for p in port:
			cmd = 'port enable port ' + str(p)
			self.sw_send_cmd(cmd)
			sleep(30)


class CN_3190_G(cienaswitch):
	def __init__(self,router):
		cienaswitch.__init__(self,router)

	def sweep_active_port_mtu(self):
		port = [10,9]
		for p in port:
			self.sweep_port_mtu(str(p))
			sleep(2)

	def disable_ports(self):
		port = [10,9]
		for p in port:
			cmd = 'port disable port ' + str(p)
			self.sw_send_cmd(cmd)
			sleep(30)
	
	def enable_ports(self):
		port = [10,9]
		for p in port:
			cmd = 'port enable port ' + str(p)
			self.sw_send_cmd(cmd)
			sleep(30)

class CN_8700_D(cienaswitch):
	def __init__(self,router):
		cienaswitch.__init__(self,router)
		self.vc_name_list = []
		self.vs_name_list = []

	def configuration_attach_vs(self,num):
		for i in range(0,num):
			if i == 1000:
				sleep(20)
			if i == 2000:
				sleep(20)
			if i == 2500:
				sleep(20)
			if i == 2800:
				sleep(20)
			if i == 2900:
				sleep(10)
			#print self.vc_name_list[i]
			#print self.vs_name_list[i]
			cmd1 = 'virtual-switch interface attach mpls-vc ' + self.vc_name_list[i] + ' vs ' + self.vs_name_list[i]	
			print cmd1
			sw_send_cmd(self,cmd1)

	def configuration_vs(self,num):
		vs_name_num = 0
		vs_name_base = 'VS-F001-S'
		for i in range(0,num):
			if i == 1000:
				sleep(20)
			if i == 2000:
				sleep(20)
			if i == 2500:
				sleep(20)
			if i == 2800:
				sleep(20)
			if i == 2900:
				sleep(10)
			vs_name_num = vs_name_num + 1
			#print "vs_name_num = %d" % vs_name_num
			vs_name_num_str = "%04i" % vs_name_num
			vs_name_str = vs_name_base + vs_name_num_str
			self.vs_name_list.append(vs_name_str)
			#print self.vs_name_list
			cmd = 'virtual-switch create vs ' + vs_name_str 
			print cmd
			sw_send_cmd(self,cmd)

	def configuration_pw(self,num):
		pw_D = mpls_l2vpn_vc(self,'D->J-F001-S0001')
		#change this line to decide where to start with incoming label
		print "pw_D.Incoming_Label = %s " % pw_D.Incoming_Label
		print "pw_D.Outgoing_Label = %s " % pw_D.Outgoing_Label
		print "pw_D.Pseudowire_ID = %s " % pw_D.Pseudowire_ID
		print "peer ip address  = %s" %  pw_D.Remote_Peer_IP_Address
		in_label_base = pw_D.Incoming_Label 
		out_label_base = pw_D.Outgoing_Label
		pw_id_base = pw_D.Pseudowire_ID
		vc_name_base = 'D->J-F001-S'
		lsp_name_base = 'Pri-Sta-Co-8700D-->5160J-'
		vc_id_base = 1
		lsp_id_base = 1
		#now only use lsp number 1 -- 10. If going forward more LSP will be used, change
		#this following line
		lsp_iteration = 62 
		lsp_num = 0
		for i in range(0,num):
			if i == 500:
				sleep(10)
			if i == 1000:
				sleep(20)
			if i == 2000:
				sleep(20)
			if i == 2500:
				sleep(20)
			if i == 2800:
				sleep(20)
			if i == 2900:
				sleep(10)
			vc_id = vc_id_base + i
			in_label = in_label_base + i
			out_label = out_label_base + i
			lsp_num = lsp_num + 1
			lsp_num_used = lsp_num
			if lsp_num == lsp_iteration:
				lsp_num = 0	
			pw_id = pw_id_base + i
			vc_name_num_str = "%04i" % vc_id
			lsp_num_str = "%03i" % lsp_num_used

			vc_name_str = vc_name_base + vc_name_num_str
			self.vc_name_list.append(vc_name_str)
			pw_id_str = str(pw_id)
			peer_str = pw_D.Remote_Peer_IP_Address
			in_label_str = str(in_label)
			out_label_str = str(out_label)
			lsp_name_str = lsp_name_base + lsp_num_str
			cmd = 'mpls l2-vpn create static-vc ' + vc_name_str + ' pw-id ' + pw_id_str + ' peer ' + peer_str + ' in-label ' + in_label_str + ' out-label ' + out_label_str + ' tp-tunnel-ingr-corout ' + lsp_name_str  + ' pw-mode spoke status-tlv on ' 
			print cmd		
			sw_send_cmd(self,cmd)


class CN_8700_E(cienaswitch):
	def __init__(self,router):
		cienaswitch.__init__(self,router)
		self.vc_name_list = []
		self.vs_name_list = []

	def configuration_attach_vs(self,num):
		for i in range(0,num):
			if i == 1000:
				sleep(20)
			if i == 2000:
				sleep(20)
			if i == 2500:
				sleep(20)
			if i == 2800:
				sleep(20)
			if i == 2900:
				sleep(10)
			#print self.vc_name_list[i]
			#print self.vs_name_list[i]
			cmd1 = 'virtual-switch interface attach mpls-vc ' + self.vc_name_list[i] + ' vs ' + self.vs_name_list[i]	
			print cmd1
			sw_send_cmd(self,cmd1)

	def configuration_vs(self,num):
		vs_name_num = 0
		vs_name_base = 'VS-F001-S'
		for i in range(0,num):
			if i == 1000:
				sleep(20)
			if i == 2000:
				sleep(20)
			if i == 2500:
				sleep(20)
			if i == 2800:
				sleep(20)
			if i == 2900:
				sleep(10)
			vs_name_num = vs_name_num + 1
			#print "vs_name_num = %d" % vs_name_num
			vs_name_num_str = "%04i" % vs_name_num
			vs_name_str = vs_name_base + vs_name_num_str
			self.vs_name_list.append(vs_name_str)
			#print self.vs_name_list
			cmd = 'virtual-switch create vs ' + vs_name_str 
			print cmd
			sw_send_cmd(self,cmd)


	def configuration_pw(self,num):
		pw_E = mpls_l2vpn_vc(self,'J->E-F001-S0001')
		#change this line to decide where to start with incoming label
		print "pw_E.Incoming_Label = %s " % pw_E.Incoming_Label
		print "pw_E.Outgoing_Label = %s " % pw_E.Outgoing_Label
		print "pw_E.Pseudowire_ID = %s " % pw_E.Pseudowire_ID
		print "peer ip address  = %s" %  pw_E.Remote_Peer_IP_Address
		in_label_base = pw_E.Incoming_Label
		out_label_base = pw_E.Outgoing_Label
		pw_id_base = pw_E.Pseudowire_ID
		vc_name_base = 'J->E-F001-S'
		lsp_name_base = 'Pri-Sta-Co-5160J-->8700E-'
		peer_str = pw_E.Remote_Peer_IP_Address
		vc_id_base = 1
		lsp_id_base = 1
		#now only use lsp number 1 -- 10. If going forward more LSP will be used, change
		#this following line
		lsp_iteration = 62
		lsp_num = 0
		for i in range(0,num):
			if i == 500:
				sleep(10)
			if i == 1000:
				sleep(20)
			if i == 2000:
				sleep(20)
			if i == 2500:
				sleep(20)
			if i == 2800:
				sleep(20)
			if i == 2900:
				sleep(10)
			vc_id = vc_id_base + i
			in_label = in_label_base + i
			out_label = out_label_base + i
			lsp_num = lsp_num + 1
			lsp_num_used = lsp_num
			if lsp_num == lsp_iteration:
				lsp_num = 0	
			pw_id = pw_id_base + i
			vc_name_num_str = "%04i" % vc_id
			lsp_num_str = "%03i" % lsp_num_used

			vc_name_str = vc_name_base + vc_name_num_str
			self.vc_name_list.append(vc_name_str)
			pw_id_str = str(pw_id)
			in_label_str = str(in_label)
			out_label_str = str(out_label)
			lsp_name_str = lsp_name_base + lsp_num_str
			cmd = 'mpls l2-vpn create static-vc ' + vc_name_str + ' pw-id ' + pw_id_str + ' peer ' + peer_str + ' in-label ' + in_label_str + ' out-label ' + out_label_str + ' tp-tunnel-egrs-corout ' + lsp_name_str  + ' pw-mode spoke status-tlv on ' 
			print cmd		
			sw_send_cmd(self,cmd)