#!/usr/local/bin/python
import time
import os
import select
from sys import stdout
from sys import stdin
from termios import VEOF, VINTR
import sys
import pexpect
import collections
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
import socket

def remove_first_line(filename):
	with open(filename, 'r') as fin:
		data = fin.read().splitlines(True)
	with open(filename, 'w') as fout:
		fout.writelines(data[1:])

def get_head(filename, lines_to_delete=1):
	queue = collections.deque()
	lines_to_delete = max(0, lines_to_delete) 
	for line in fileinput.input(filename, inplace=True, backup='.bak'):
		queue.append(line)
		if lines_to_delete == 0:
			print queue.popleft(),
		else:
			lines_to_delete -= 1
	queue.clear()



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

def seek_lock(lck_file):
	while os.path.exists(lck_file):
		print "wait until someone release the lock"
		sleep (3)
		if not os.path.exists(lck_file):
			file = lck_file
			open('file', 'w').close()

def release_lock(lck_file):
	if os.path.exists(lck_file):
		file = lck_file
		os.remove(file)

def remove_crapy_line(list):
	newlist = []
	for line in list:
		line = line.strip('\r')
		line = line.strip('|')
		line = line.strip()
		line_new = line.replace("/","|")
		newlist.append(line_new)
		return newlist

def remove_logical_id(infile,outfile):
	lck = 'def_remove_logical_id.lck'
	seek_lock(lck)
	if not os.path.isfile(infile):
		print(("Error on replace_word, not a regular file: "+infile))
		sys.exit(1)
	f1 = open(infile,'r')
	f2 = open(outfile,'w')
	str = f1.read()
	str2 = re.sub(r"logical-id .\d* ","",str)
	f2.write(str2)
	f1.close()
	f2.close()
	get_head(outfile,1)
	remove_first_line(outfile)
	release_lock(lck)

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])


#def get_head_block(list,str):
#	found = 0
#	start = 0
#	block = []
#	for line in list:
#		if str in line and found == 0:
#			found = 1
#			continue
#		elif found == 1 and start == 0 and is_dash_line(line) == 'True':
#			start = 1
#			continue
#		elif found == 1 and start == 1 and is_dash_line(line) == 'False':
#			block.append(line)
#			continue
#		elif found == 1 and start == 1 and is_dash_line(line) == 'True':
#			 #end of the block search
#			break
#		block = remove_crapy_line(block)
#		return block

