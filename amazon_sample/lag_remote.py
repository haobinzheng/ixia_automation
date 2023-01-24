#!/usr/bin/python
## very quick and dirty script to load in  LAG attributes and output the remote config
## must be run from within targetspec/border directory - since it's not path-aware
## There's only basic error checking, so try not to break it
## This also makes some strong assumptions on the IP scheme:
##  - we're using a /31, and the cidr is in the IPADDR 
##  - will look for the opposite side of the /31 from what we've found



import os
import sys


if (len(sys.argv) < 2):
	print "Usage:  %s <lag attrib file>" % (sys.argv[0])
	exit(1)

attr_file = sys.argv[1]


if (not os.path.exists(attr_file)):
	print "File not found: %s" % (attr_file)
	exit(1)
	
	

## REMHOST is attr file's target
remhost = os.path.dirname(attr_file)


lags = {}
ATTR = open(attr_file, "r")


## load all of the LAG data into a structure, we'll loop back through them and flip
## everything around for the remote side
for line in ATTR:
	line = line.strip()
	parts = line.split(" ")
	
	if (parts[0] != "LAG"):
		continue
	
	cur_lag = parts[1]
	
	if (not cur_lag in lags.keys()):
		lags[cur_lag] = {}
		
	if (parts[2] == 'REMHOST'):
		lags[cur_lag]['remhost'] = parts[3]
	
	if (parts[2] == 'REMLAG'):
		lags[cur_lag]['remlag'] = parts[3]
	
	if (parts[2] == 'IPADDR'):
		lags[cur_lag]['ipaddr'] = parts[3]
		
	if (parts[2] == 'MEMBER'):
		if (not 'members' in lags[cur_lag].keys()):
			lags[cur_lag]['members'] = []
			
		members = [parts[3], parts[5]]
		lags[cur_lag]['members'].append(members)


ATTR.close()

## walk the lags and flip the local/remote 
for lag in lags.keys():
	target = lags[lag]['remhost']
	remlag = lag
	loclag = lags[lag]['remlag']

	## strip the cidr from the address
	rem_ip = lags[lag]['ipaddr'].replace("/31","")
	
	## parse out the last octet and add 1 to get the remote side
	octets = rem_ip.split(".")
	
	if ((int(octets[3]) % 2) == 0):
		## this is the even side of the /31, remote side is +1
		octets[3] = str(int(octets[3]) + 1)
	else:
		## This is the odd side of the /31, remote side is - 1
		octets[3] = str(int(octets[3]) - 1)
		
		
	ipaddr = ".".join(octets)


	print "--> %s" % (target)
	out = ""
	
	out = out + "LAG %s REMHOST %s\n" % (loclag, remhost)
	out = out +  "LAG %s REMLAG %s\n" % (loclag, remlag)
	out = out +  "LAG %s IPADDR %s/31\n" % (loclag, ipaddr)

	for members in lags[lag]['members']:
		out = out +  "LAG %s MEMBER %s REMPORT %s\n" % (loclag, members[1], members[0])

	print out

	out_file = "%s/%s" % (target, os.path.basename(attr_file))
	## append to the output file
	ATTR = open(out_file, "a")
	ATTR.write("%s\n" % ("#"*20))
	ATTR.write(out)
	ATTR.write("%s\n" % ("#"*20))



# LAG ae31 REMHOST iad2-br-cor-r1
# LAG ae31 REMLAG ae61
# LAG ae31 IPADDR 54.240.228.134/31
# LAG ae31 MEMBER xe-0/0/39 REMPORT xe-3/0/0
# LAG ae31 MEMBER xe-0/0/40 REMPORT xe-3/0/1
# LAG ae31 MEMBER xe-0/0/41 REMPORT xe-10/0/0
# LAG ae31 MEMBER xe-0/0/42 REMPORT xe-10/0/1
# LAG ae31 MEMBER xe-0/1/8 REMPORT xe-3/0/2
# LAG ae31 MEMBER xe-0/1/9 REMPORT xe-10/0/2

# LAG ae32 REMHOST iad2-br-cor-r2
# LAG ae32 REMLAG ae61
# LAG ae32 IPADDR 54.240.228.136/31
# LAG ae32 MEMBER xe-0/0/43 REMPORT xe-3/0/0
# LAG ae32 MEMBER xe-0/0/44 REMPORT xe-3/0/1
# LAG ae32 MEMBER xe-0/0/45 REMPORT xe-10/0/0
# LAG ae32 MEMBER xe-0/0/46 REMPORT xe-10/0/1
# LAG ae32 MEMBER xe-0/1/10 REMPORT xe-3/0/2
# LAG ae32 MEMBER xe-0/1/11 REMPORT xe-10/0/2

# LAG ae33 REMHOST iad2-br-cor-r3
# LAG ae33 REMLAG ae61
# LAG ae33 IPADDR 54.240.228.138/31
# LAG ae33 MEMBER xe-0/0/47 REMPORT xe-3/0/0
# LAG ae33 MEMBER xe-0/1/1 REMPORT xe-3/0/1
# LAG ae33 MEMBER xe-0/1/2 REMPORT xe-10/0/0
# LAG ae33 MEMBER xe-0/1/3 REMPORT xe-10/0/1
# LAG ae33 MEMBER xe-0/1/12 REMPORT xe-3/0/2
# LAG ae33 MEMBER xe-0/1/13 REMPORT xe-10/0/2

# LAG ae34 REMHOST iad2-br-cor-r4
# LAG ae34 REMLAG ae61
# LAG ae34 IPADDR 54.240.229.120/31
# LAG ae34 MEMBER xe-0/1/4 REMPORT xe-3/0/0
# LAG ae34 MEMBER xe-0/1/5 REMPORT xe-3/0/1
# LAG ae34 MEMBER xe-0/1/6 REMPORT xe-10/0/0
# LAG ae34 MEMBER xe-0/1/7 REMPORT xe-10/0/1
# LAG ae34 MEMBER xe-0/1/14 REMPORT xe-3/0/2
# LAG ae34 MEMBER xe-0/1/15 REMPORT xe-10/0/2
