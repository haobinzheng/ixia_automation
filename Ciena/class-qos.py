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


#Currently only VLAN based VS will support queue-map
class rcos-map():
	def __init__(self,router):
		self.dut = router
		self.rcos_map_list = []
		pass

	def config_rcos_map_all_queue(self):
		for i in range(0,8):
			rcos_map_name = dut.name + 'rcos-map-' + str(i)
			self.rcos_map_list.append(rcos_map_name)
			queue = i
			self.config_rcos_map(rcos_map_name,queue)

		cmd = 'port set port ' + port + ' max-frame-size ' + mtu
		self.sw_send_cmd(cmd)	
	
	def config_rcos_map(self,name,queue):
		for i in range(0,8):
			cmd = 'traffic-services queuing queue-map set rcos-map '  + name + ' rcos ' + str(i) ' queue ' + str(queue)
			sw_send_cmd(self.dut,cmd)