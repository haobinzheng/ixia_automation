ONBOARD_MSG = """==============================================================================================
**** REMINDER **** 	**** REMINDER ****	**** REMINDER ****	**** REMINDER ****	 
Please make sure to execute the following procedures before running the test:
	1)Make sure sensitive micro-usb console cables are connected well. 
	2)Make sure IXIA port connection is good. A bad connection will fail the script.
	3)If a test case needs 4x IXIA ports, remember to move the 1/7 and 1/8 IXIA ports from 548D setup to 448D 
	or visa versa when switching to differrent testbed. 
		IXIA 1/7 -- (port39)SW3
		IXIA 1/8 -- (port39)SW4
	4)Make sure the have -e option at CLI to run sw1 and sw2 setup
	5)Make sure to uncomment of lines under the <official run> marker 
===============================================================================================""" 
DEBUG = True
REBOOT = False
CLEAR_LINE = False
TC1_RUNTIME = 100 # Test case #1 run time = TC!_RUNTIME * 10 sec for each round of test 
IXIA_CLEANUP = False 
THREADING  = False
#MULTIPROCESSING = True
TELNET = False
FACTORY = False
build_548d = 194
FGT_REBOOT = False
STAGE_UPGRADE = True
# def init():
# 	global DEBUG
# 	DEBUG = False


def init_config(*args, **kwargs):
	init = """
	config system interface
    edit mgmt
    	set mode static
        set ip {mgmt_ip} {mgmt_mask}
        set allowaccess ping https http ssh snmp telnet radius-acct
    next
    edit vlan1
        set ip {vlan1_ip} {vlan1_mask}
        set allowaccess ping https ssh
        set vlanid 1
        set interface internal
    next
    edit "loop0"
        set ip {loop0_ip} {loop0_mask}
        set allowaccess ping https http ssh telnet
        set type loopback
    next
end
	"""