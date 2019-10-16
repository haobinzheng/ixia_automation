
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


output = """

FortiGate-3960E # execute dhcp lease-list fortilink
fortilink
  IP			MAC-Address		Hostname		VCI			Expiry
  169.254.1.5		90:6c:ac:62:14:3f	S548DF4K16000653		FortiSwitch-548D-FPOE		Tue Oct 22 13:14:33 2019
  169.254.1.2		70:4c:a5:79:22:5b	S548DN4K17000133		FortiSwitch-548D		Tue Oct 22 13:14:33 2019
  169.254.1.4		70:4c:a5:82:99:83	S548DF4K17000028		FortiSwitch-548D-FPOE		Tue Oct 22 17:26:17 2019
  169.254.1.3		70:4c:a5:82:96:73	S548DF4K17000014		FortiSwitch-548D-FPOE		Tue Oct 22 17:26:31 2019
  169.254.1.7		70:4c:a5:65:93:65	S448DP3X17000253		FortiSwitch-448D-POE		Tue Oct 22 13:14:34 2019

"""