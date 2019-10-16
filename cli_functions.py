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
import xlsxwriter
from excel import *
from ixia_ngfp_lib import *
import settings
from console_util  import  *
import pexpect
from threading import Thread
import subprocess
import spur
import multiprocessing

from ixia_ngfp_lib import *
from utils import *
from settings import *

def fgt_switch_controller_GetConnectionStatus(fgt):
	con_status_sample = """
	FortiGate-3960E # execute switch-controller get-conn-status 
	Managed-devices in current vdom root:
	 
	STACK-NAME: FortiSwitch-Stack-fortilink
	SWITCH-ID         VERSION           STATUS         FLAG   ADDRESS              JOIN-TIME            NAME            
	S448DP3X17000253  v6.2.0 (184)      Authorized/Up   -   169.254.1.7     Fri Oct 11 22:24:53 2019    -               
	S448DPTF18000161  v6.2.0 (184)      Authorized/Up   -   169.254.1.6     Fri Oct 11 22:24:45 2019    -               
	S548DF4K16000653  v6.2.0 (192)      Authorized/Up   E   169.254.1.5     Fri Oct 11 22:24:40 2019    -               
	S548DF4K17000014  v6.2.0 (192)      Authorized/Up   C   169.254.1.3     Fri Oct 11 22:04:48 2019    -               
	S548DF4K17000028  v6.2.0 (192)      Authorized/Up   -   169.254.1.4     Fri Oct 11 22:23:58 2019    -               
	S548DN4K17000133  v6.2.0 (192)      Authorized/Up   -   169.254.1.2     Fri Oct 11 22:24:30 2019    -               
	 
		 Flags: C=config sync, U=upgrading, S=staged, D=delayed reboot pending, E=configuration sync error
		 Managed-Switches: 6 (UP: 6 DOWN: 0)
	 
	"""