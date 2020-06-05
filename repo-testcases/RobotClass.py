from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

import telnetlib
import sys
import time
import logging
import traceback
import paramiko
import time
from time import sleep
import re
import os
from datetime import datetime
# import xlsxwriter
# from excel import *
# #from ixia_ngfp_lib import *
# import settings
# from console_util  import  *
# import pexpect
# from threading import Thread
# import subprocess
# import spur

from robot.api import logger

def printr(*args,**kwargs):
    print_string = ""
    for s in args:
        try:
            print_string = "{},{}".format(print_string,s) if print_string else s
        except Exception as print_except:
            print("Error to log to Robot console")
    logger.console(print_string)

class fortisw():
    # def __init__(self,*args, **kwargs):
    #     self.console = args[0]

    def get_lldp(self):
        self.collect_show_cmd("get switch lldp summary")

    def collect_show_cmd(self,output,**kwargs):
        printr("Enter collect_show_cmd")
        printr(output)
        #output = tn.read_until(("# ").encode('ascii'))
        out_list = output.split(b'\r\n')
        encoding = 'utf-8'
        out_str_list = []
        for o in out_list:
            o_str = o.decode(encoding).rstrip(' ')
            out_str_list.append(o_str)
        printr(out_str_list)
        return out_str_list

class fortigate():
    # def __init__(self,*args, **kwargs):
    #     self.console = args[0]

    def get_lldp(self):
        self.collect_show_cmd("get switch lldp summary")

    def collect_show_cmd(self,output,**kwargs):
        printr("Enter collect_show_cmd")
        printr(output)
        #output = tn.read_until(("# ").encode('ascii'))
        out_list = output.split(b'\r\n')
        encoding = 'utf-8'
        out_str_list = []
        for o in out_list:
            o_str = o.decode(encoding).rstrip(' ')
            out_str_list.append(o_str)
        printr(out_str_list)
        return out_str_list

def convert_cmd_ascii_n(cmd):
    cmd = cmd + '\n'
    return cmd.encode('ascii')

def collect_show_cmd(output,**kwargs):
     
    printr("Enter collect_show_cmd")
    printr(output)
    #output = tn.read_until(("# ").encode('ascii'))
    out_list = output.split(b'\r\n')
    encoding = 'utf-8'
    out_str_list = []
    for o in out_list:
        o_str = o.decode(encoding).rstrip(' ')
        out_str_list.append(o_str)
    printr(out_str_list)
    return out_str_list


def testing(*args,**kwargs):
   name = kwargs["name"]
   age = kwargs["age"]
   printr("testing")
   printr("testing name = {},age={}".format(name,age))

   b = {"name":"mike","age":14,"location":"china"}
   a = "mike"
   printr("{} is a good man".format(a))

   for k,v in b.items():
       printr(k,v)
   return a
    




# def testing(*args,**kwargs):
#     name = kwargs["name"]
#     age = kwargs["age"]
#     print "testing"
#     #print("testing name = {},age={}".format(name,age))

#     b = {"name":"mike","age":14,"location":"china"}
#     a = "mike"
#     #print("{} is a good man".format(a))

#     for k,v in b.iteritems():
#         print k,v

if __name__ == "__main__":
    testing(name="steve",age=30)
    sw = fortisw()
    sw.collect_show_cmd("this is a test")

