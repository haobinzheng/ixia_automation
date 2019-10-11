ONBOARD_MSG = """==============================================================================================
**** REMINDER **** 	**** REMINDER ****	**** REMINDER ****	**** REMINDER ****	 
Please make sure to execute the following procedures before running the test:
	1)Make sure sensitive micro-usb console cables are connected well. 
	2)Make sure IXIA port connection is good. A bad connection will fail the script.
	3)Remember to move the 3rd and 4th IXIA port from 548D setup to 448D or visa versa 
	when switching to differrent testbed
	4)Make sure the have -e option at CLI to run sw1 and sw2 setup
	5)Make sure to uncomment of lines under the <official run> marker 
===============================================================================================""" 
DEBUG = False
REBOOT = False
CLEAR_LINE = False
TC1_RUNTIME = 6 # Test case #1 run time = TC!_RUNTIME * 10 sec for each round of test 
IXIA_CLEANUP = False 
THREADING  = False
#MULTIPROCESSING = True
TELNET = False
FACTORY = False
build_548d = 192
FGT_REBOOT = True
STAGE_UPGRADE = False
# def init():
# 	global DEBUG
# 	DEBUG = False
