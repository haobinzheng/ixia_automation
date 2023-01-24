#!/apollo/bin/env -e NetengTools python
import csv
import sys
import re
import os.path
import argparse
import pprint
import math
import ipaddr
import socket, struct
import os
import shutil
from ipaddr import IPv6Address
from ipaddr import IPv4Address
parser = argparse.ArgumentParser()
parser.add_argument('--csv', help = 'CSV file containing the cutsheet', required = True)

args = parser.parse_args()
csv_filename = args.csv

def lowest_ctz_port_index(port_tuples):
    # Pass a list of tuples of local and remote ports, return the 'index' of the lowest local port.
    # If using 40G native optics index is calculated from port number (after et-0/0/) multiplied by 4
    # e.g. et0/0/12 has an index of 48; et-0/0/7 has an index of 28
    #
    # If using 10G breakouts index is calculated from port number (after xe-0/0/) multiplied by 4 + channel number
    # e.g. xe-0/0/12:0 has an index of 48; xe-0/0/7:3 has an index of 31
    indices = []
    for element in port_tuples:
        if 'et-' in element[0]:
            stripped_port = re.sub('et-0/0/', '', element[0])
            indices.append(int(stripped_port) * 4)
        elif 'xe-' in element[0]:
            stripped_port = re.sub('xe-0/0/', '', element[0])
            if ':' not in stripped_port:
                print "xe- interfaces detected but no ':' character in Catzilla port %s. Confirm if interfaces are 10G breakout" % element[0]
                print port_tuples
                exit()
            parts = stripped_port.split(':')
            indices.append( int(parts[0]) * 4 + int(parts[1]))
    indices.sort()
    return indices[0]

def catzilla_ipv4(routername, index):
    # Given a Catzilla tier1 router name and the 'index' of a port, return the IPv4
    # address that should be assigned to that port.
    # A Catzilla tier1 (QFX5100-24Q) port's "index" is calculated from the 40G port 
    # number (after xe-0/0/) multiplied by 4 + channel number
    # eg. xe-0/0/12:0 has an index of 48; xe-0/0/7:3 has an index of 31
    p = re.compile(r'.*br-ctz-f\d+b(\d+)-t1-r(\d+)')
    m = p.match(routername)
    if m and index <= 63 and index >= 0:
  	  brick = int(m.group(1))
	  router = int(m.group(2))
	  Ctz_client_start_ip = "100.65.0.0"
	  startip = int(IPv4Address(Ctz_client_start_ip))
	  perBrick = 256 * 8     # a /21 per brick
	  perRouter = 64 * 2     # a /25 per router
	  interface = index *2   # a /31 per interface
	  return str(IPv4Address(startip + (perBrick * (brick-1)) + (perRouter * (router-1)) + interface))
    else:
	print "catzilla_ipv4 function only defined for Catzilla tier1 routers"
	exit()

def v4_in_hex(ipv4_address):
    # passed a v4 address as a string, returns last two quibbles in hex
    # e.g. v4_in_hex(100.65.7.3), returns ":6441:703"
    numbers = list(map(int, ipv4_address.split('.')))
    return '{:02x}{:02x}:{:02x}{:02x}'.format(*numbers)

# Check if file exists
if not os.path.isfile(csv_filename):
    print "ERROR: Must specify valid CSV file name."
    sys.exit(1)

# Read in cabling cutsheet
devices = {}
catzilla_name = ""
catzilla_brick_number = ""
v6_96bits = ""
with open(csv_filename, 'rb') as csvfile:
    rows = csv.reader(csvfile)
    line = 0
    for row in rows:
	line += 1
	# CSV format validation
	if len(row) < 35:
	    print "CSV format unrecognized. Insufficient number of fields."
	    sys.exit(1)
	if (line == 2) and not ("ostname" in row[0]):
	    print "CSV format unrecognized or header row missing."
	    sys.exit(1)
        elif line == 1:
	    continue
        elif line == 2: 
            continue 
	if line == 3:
	    # work out Catzilla name from first cable in cutsheet
	    p = re.compile(r'(.*br-ctz-f\d+)(b\d+)-t1-r\d+')
	    if 'br-ctz' in row[0]:
		m = p.match(row[0])
		catzilla_name = m.group(1)
                catzilla_brick_number = m.group(2).upper()
	    elif 'br-ctz' in row[35]:
		m = p.match(row[35])
		catzilla_name = m.group(1)
                catzilla_brick_number = m.group(2).upper()
	# Check the order of routeirs in CSV
	if bool(re.search('br-agg|br-fab|br-ctz', row[0])) and bool(re.search('br-agg|br-fab|br-ctz', row[35])):
	    a_device = row[0]
	    a_lag = row[2]
	    a_port = row[1]
	    z_device = row[35]
	    z_lag = row[33]
	    z_port = row[34]
            lag_check= row[33]
            
	else:
	    print "WARNING: Possible CSV format error on line " + str(line) + "."
	    print "Note: this script is only appropriate for br-agg or br-fab to br-ctz devices."
	    exit()

	# Initialize dictionaries
	if a_device not in devices.iterkeys():
	    devices[a_device] = {}
	if a_lag not in devices[a_device].iterkeys():
	    devices[a_device][a_lag] = {}
	    devices[a_device][a_lag]['peer_device'] = z_device
	    devices[a_device][a_lag]['peer_lag'] = z_lag
	    devices[a_device][a_lag]['ports'] = []
	if a_port not in devices[a_device][a_lag]['ports']:
	    devices[a_device][a_lag]['ports'].append((a_port, z_port))
	if z_device not in devices.iterkeys():
	    devices[z_device] = {}
	if z_lag not in devices[z_device].iterkeys():
	    devices[z_device][z_lag] = {}
	    devices[z_device][z_lag]['peer_device'] = a_device
	    devices[z_device][z_lag]['peer_lag'] = a_lag
	    devices[z_device][z_lag]['ports'] = []
	if z_port not in devices[z_device][z_lag]['ports']:
	    devices[z_device][z_lag]['ports'].append((z_port, a_port)) 
        
# Pull in Catzilla infrastructure v6 space for this Catzilla from GenevaBuilder
# Relevant attribute is BASEIPV6SLASH64 in /GenevaBuilder/targetspec/border/shared/<CATZILLA_NAME>.attr
home = os.path.expanduser("~")
filename = home + "/GenevaBuilderDCEdge/targetspec/border/shared/" + catzilla_name + ".attr"
#print "FILENAME: %s" % filename
with open(filename, "r") as catzilla_file:
    NotFoundv6 = 1
    NotFound_cluster = 1
    for line in catzilla_file.readlines():
	if "CONFER BASEIPV6SLASH64" in line:
	    prefix_64bits = line.split('::/64')[0].split()[-1]
	    v6_96bits = prefix_64bits + ":8000:0:"
	    NotFoundv6 = 0
        if "CONFER CLUSTERID" in line:
            cluster_id_base = line.split()[2].split('/')[0]
            NotFound_cluster = 0
    if NotFoundv6:
	print "\nCouldn't find BASEIPV6SLASH64 attribute for Catzilla %s\n" % catzilla_name
	exit()
    if NotFound_cluster:
	print "\nCouldn't find base CLUSTERID attribute for Catzilla %s\n" % catzilla_name
	exit()

# Get a list of Catzilla bricks in the cutsheet
ctz_bricks = []
for router in sorted(devices, key=devices.get):
 if 'br-ctz' in router:
        fabric_name = router.split("-t1")[0]
        if fabric_name not in ctz_bricks:
            ctz_bricks.append(fabric_name)
           
for brickname in ctz_bricks:
    for router in sorted(devices, key=devices.get):
        if brickname in router: 
	    fabric_name = router.split("-t1")[0]
            br_ctz_router = router.split("-t1-")[1]
            
      # Let's name the output file based on the CTZ brick name and the peer_device connected off ae2/ae4
            if 'ae2' in lag_check:
	    	peer_device_name = devices[router]['ae2']['peer_device'].split('-')
               
            if 'ae4' in lag_check:
            	peer_device_name = devices[router]['ae4']['peer_device'].split('-')
     
 	    temp_outfilename = brickname + "-bgp-br-" + peer_device_name[2]
            outFile = open(temp_outfilename, 'a')
	    for lag in sorted(devices[router], key=devices[router].get):
	        header = "CAT " + fabric_name + " TIER1 " + br_ctz_router + " LAG " + lag
	        outFile.write("\n" + header + " REMHOST " + devices[router][lag]['peer_device'] + "\n")
	        outFile.write(header + " REMLAG " + devices[router][lag]['peer_lag'] + "\n")
	        port_count = len(devices[router][lag]['ports'])
	        outFile.write(header + " MINLINKS %d" % math.floor(port_count * 0.75) + "\n")
	        for port in range(port_count):
		    outFile.write(header + " MEMBER " + devices[router][lag]['ports'][port][0] + \
		           " REMPORT " + devices[router][lag]['ports'][port][1] + "\n")
	        low_port_index = lowest_ctz_port_index(devices[router][lag]['ports'])
                if (low_port_index % 4 != 0):
                   outFile.write("\nWARNING: %s bundle %s does not have the lowest member port the first 10GigE port of the 40GigE port! \nExample: the lowest member port should look like: xe-0/0/Y:0\n" % (devices[router][lag]['peer_device'], lag))
  	        ipv4 = catzilla_ipv4(router, low_port_index)
	        peer_ipv4 = str(IPv4Address(int(IPv4Address(ipv4)) + 1))
	        # Stash the v4 address for reference when we do the peers
	        devices[router][lag]['ipv4dec'] = int(IPv4Address(ipv4))
	        outFile.write(header + " IPADDR " + ipv4 + "/31\n")
	        # use IPv6Address from ipaddr to sanitize my hex representation
	        ipv6 = IPv6Address(v6_96bits + v4_in_hex(ipv4))
	        peer_ipv6 = IPv6Address(v6_96bits + v4_in_hex(peer_ipv4))
	        outFile.write(header + " IPV6ADDR " + str(ipv6) + "/127\n")
	    
	        peergroup = "NO_PEERGROUP_FOUND"
	        if 'br-agg' in devices[router][lag]['peer_device']:
		    peergroup = "IBGP-BR-AGG-PTPIBGP"
	        elif 'br-fab-f1' in devices[router][lag]['peer_device']:
		    peergroup = "IBGP-BR-FAB1-PTPIBGP"
	        elif 'br-fab-f2' in devices[router][lag]['peer_device']:
		    peergroup = "IBGP-BR-FAB2-PTPIBGP"
	        header = "CAT " + fabric_name + " TIER1 " + br_ctz_router + " BGPNEIGH "
	        outFile.write(header + peergroup + " IP " + peer_ipv4 + " DESC " + devices[router][lag]['peer_device'] + "\n")
	        outFile.write(header + peergroup + " IP " + peer_ipv4 + " LOCALIP " + ipv4 + "\n")
	        outFile.write(header + "IPV6-" + peergroup + " IP " + str(peer_ipv6) + " DESC " + devices[router][lag]['peer_device'] + "\n")
	        outFile.write(header + "IPV6-" + peergroup + " IP " + str(peer_ipv6) + " LOCALIP " + str(ipv6) + "\n")
	    outFile.close()

    directory = "out"
    if not os.path.exists(directory):
         os.makedirs(directory)
    outfilename = directory + "/" + temp_outfilename + ".attr"
    shutil.copyfile(temp_outfilename,outfilename) 
    print "Wrote file: %s" % outfilename
    os.remove(temp_outfilename)
#pp = pprint.PrettyPrinter(indent=4)
#pp.pprint(devices)

for router in sorted(devices, key=devices.get):
    if 'br-agg' in router or 'br-fab' in router:
	#fabric_name = router.split("-t1")[0]
        #br_ctz_router = router.split("-t1-")[1]
        outFile = open("out/" + router, 'w')
        if 'br-fab-f1' in router:
             cluster_id = str(IPv4Address(int(IPv4Address(cluster_id_base)) + 37))
             outFile.write("\n" + "CLUSTERID_FAB1TOCTZ " + cluster_id + "\n")
        elif 'br-fab-f2' in router:
             cluster_id = str(IPv4Address(int(IPv4Address(cluster_id_base)) + 39))
             outFile.write("\n" + "CLUSTERID_FAB2TOCTZ " + cluster_id + "\n")
	if 'br-fab' in router:
            outFile.write("# Add prefixlist to open controlplane ACLs for Catzilla address space\n")
	    # Fatcats always on Brick1, so first /21 of 100.65.0.0/16 used on pt-2-pt
            outFile.write("PREFIXLIST IPV4-ADJACENT-INFRA 100.65.0.0/21\n")
	    # IPv6 equivalent of the IPv4 /21 on Brick1 is the first /117 of Catzilla Infra/64 for pt-2-pt
	    v6infra = IPv6Address(v6_96bits + v4_in_hex('100.65.0.0'))
            outFile.write("PREFIXLIST IPV6-ADJACENT-INFRA %s/117\n" % v6infra )
            outFile.write("\n" + "IBGP-BR-CTZ-PTPIBGP TURNUP\n")
        if 'br-agg' in router:
	    # determine the peergroup names from the peers
            facing_ctz_bricks = []
            for lag in devices[router].iterkeys():
		peer = devices[router][lag]['peer_device']
                p = re.compile(r'.*br-ctz-f\d+(b\d+)-t1-r\d+')
                m = p.match(peer)
                b = m.group(1).upper()
		if b not in facing_ctz_bricks:
		    facing_ctz_bricks.append(b)
	    for peergroup in facing_ctz_bricks:
                outFile.write("\n" + "BGPGROUP CTZ IBGP-BR-CTZ-{}-PTPIBGP TURNUP\n".format(peergroup))
                outFile.write("BGPGROUP CTZV6 IPV6-IBGP-BR-CTZ-{}-PTPIBGP TURNUP\n".format(peergroup))
        if 'br-fab-f1' in router:
            # Only Sites with 1 Fatcat remain. Brick 1 will be shared with L7.
	    outFile.write("\n" + "# This Fatcat shares a Catzilla brick with br-lbe's\n")
	    outFile.write("# See: https://w.amazon.com/index.php/Networking/IS/Catzilla/Index/Shared_Fatcat_Brick\n")
	    outFile.write("ALLOW_FAB_CTZ_SHARED_VIP_SPACE\n")
	for lag in sorted(devices[router], key=devices[router].get):
	    header = "LAG " + lag
	    outFile.write("\n" + header + " REMHOST " + devices[router][lag]['peer_device']+"\n")
	    outFile.write(header + " REMLAG " + devices[router][lag]['peer_lag'] + "\n")
	    port_count = len(devices[router][lag]['ports'])
	    outFile.write(header + " MINLINKS %d" % math.floor(port_count * 0.75) + "\n")
	    for port in range(port_count):
		outFile.write(header + " MEMBER " + devices[router][lag]['ports'][port][0] + \
                     " REMPORT " + devices[router][lag]['ports'][port][1] + "\n")
	    peer = devices[router][lag]['peer_device']
	    peerlag = devices[router][lag]['peer_lag']
	    peer_ipv4_dec = devices[peer][peerlag]['ipv4dec']
	    peer_ipv4 = str(IPv4Address(peer_ipv4_dec))
	    ipv4 = str(IPv4Address(peer_ipv4_dec + 1))
	    outFile.write(header + " IPADDR " + ipv4 + "/31\n")
	    # use IPv6Address from ipaddr to sanitize my hex representtion
	    ipv6 = IPv6Address(v6_96bits + v4_in_hex(ipv4))
	    peer_ipv6 = IPv6Address(v6_96bits + v4_in_hex(peer_ipv4))
	    outFile.write(header + " IPV6ADDR " + str(ipv6) + "/127\n")
	    peergroup = "IBGP-BR-CTZ-PTPIBGP"    # default for fatcat
            if 'br-agg' in router:
                p = re.compile(r'.*br-ctz-f\d+(b\d+)-t1-r\d+')
                m = p.match(peer)
                brick_num = m.group(1).upper()
                peergroup = "IBGP-BR-CTZ-{}-PTPIBGP".format(brick_num)
	    header = "BGPNEIGH "
	    outFile.write(header + peergroup + " IP " + peer_ipv4 + " DESC " + devices[router][lag]['peer_device'] + "\n")
	    outFile.write(header + peergroup + " IP " + peer_ipv4 + " LOCALIP " + ipv4 + "\n")
	    outFile.write(header + "IPV6-" + peergroup + " IP " + str(peer_ipv6) + " DESC " + devices[router][lag]['peer_device']+ "\n")
	    outFile.write(header + "IPV6-" + peergroup + " IP " + str(peer_ipv6) + " LOCALIP " + str(ipv6)+ "\n")
        outFile.close()
	print "Wrote file: out/%s" % router

#Creating .yaml for br-agg prestage
if 'br-fab' not in ",".join(devices.keys()):
    # import pdb; pdb.set_trace()
    outFile = open("out/bragg_prestage.yaml" , 'w')
    outFile.write("phases:\n")
    outFile.write("    PreShiftAway:\n")
    for router in sorted(devices, key=devices.get):
        if 'br-agg' in router:
            outFile.write("        -\n")
            outFile.write("         targets: " + router + "\n")
            outFile.write("         checks:\n")
            for lag in sorted(devices[router], key=devices[router].get):
                port_count = len(devices[router][lag]['ports'])
                for port in range(port_count):
                    outFile.write("                -\n")
                    outFile.write("                 family: general\n")
                    outFile.write("                 name: check_show_command\n")
                    outFile.write("                 args:\n")
                    outFile.write("                    command_to_run: 'configuration interfaces " + devices[router][lag]['ports'][port][0] + ' | match "address|802.3ad" | count' + "'\n")
                    outFile.write("                    expected_output: 'Count: 0 lines'\n")
            outFile.write("                -\n")
            outFile.write("                 family: general\n")
            outFile.write("                 name: check_no_chassis_alarms\n")
            outFile.write("                -\n")
            outFile.write("                 family: general\n")
            outFile.write("                 name: check_no_system_alarms\n")
            outFile.write("                -\n")
            outFile.write("                 family: general\n")
            outFile.write("                 name: check_show_command\n")
            outFile.write("                 args:\n")
            outFile.write("                    command_to_run: 'bgp group IBGP-BR-CTZ-{}-PTPIBGP | count'\n".format(catzilla_brick_number))
            outFile.write("                    expected_output: 'Count: 0 lines'\n")
            outFile.write("                -\n")
            outFile.write("                 family: general\n")
            outFile.write("                 name: check_show_command\n")
            outFile.write("                 args:\n")
            outFile.write("                    command_to_run: 'bgp group IPV6-IBGP-BR-CTZ-{}-PTPIBGP | count'\n".format(catzilla_brick_number))
            outFile.write("                    expected_output: 'Count: 0 lines'\n")
            outFile.write("                -\n")
            outFile.write("                 family: routes\n")
            outFile.write("                 name: check_routes_not_active\n")
            outFile.write("                 args:\n")
            outFile.write("                    junos_table: inet.0\n")
            outFile.write("                    routes: ")
            subnets = []
            for lag in sorted(devices[router], key=devices[router].get):
                peer = devices[router][lag]['peer_device']
                peerlag = devices[router][lag]['peer_lag']
                sub_dec = devices[peer][peerlag]['ipv4dec']
                sub = str(IPv4Address(sub_dec)) + "/31"
                sub_ipv4 = str(IPv4Address(sub_dec))
                sub_ipv6 = str(IPv6Address(v6_96bits + v4_in_hex(sub_ipv4))) + "/127"
                subnets.append(sub)
            delimiter = ','
            subnet_group = delimiter.join(subnets)
            outFile.write(subnet_group +"\n")
            outFile.write("                -\n")
            outFile.write("                 family: routes\n")
            outFile.write("                 name: check_routes_not_active\n")
            outFile.write("                 args:\n")
            outFile.write("                    junos_table: inet6.0\n")
            outFile.write("                    routes: ")
            subnets = []
            for lag in sorted(devices[router], key=devices[router].get):
                peer = devices[router][lag]['peer_device']
                peerlag = devices[router][lag]['peer_lag']
                sub_dec = devices[peer][peerlag]['ipv4dec']
                sub = str(IPv4Address(sub_dec)) + "/31"
                sub_ipv4 = str(IPv4Address(sub_dec))
                sub_ipv6 = str(IPv6Address(v6_96bits + v4_in_hex(sub_ipv4))) + "/127"
                subnets.append(sub_ipv6)
            delimiter = ','
            subnet_group = delimiter.join(subnets)
            outFile.write(subnet_group +"\n")
    outFile.write("    PostUpdateConfig:\n")
    outFile.write("         -\n")
    outFile.write("          targets: .*\n")
    outFile.write("          checks:\n")
    outFile.write("                 -\n")
    outFile.write("                  family: bgp\n")
    outFile.write("                  name: check_bgp_group_import_policy\n")
    outFile.write("                  args:\n")
    outFile.write("                     bgp_group: IBGP-BR-CTZ-{}-PTPIBGP\n".format(catzilla_brick_number))
    outFile.write("                     policy: TURNUP-FILTERLIST-66\n")
    outFile.write("                 -\n")
    outFile.write("                  family: bgp\n")
    outFile.write("                  name: check_bgp_group_export_policy\n")
    outFile.write("                  args:\n")
    outFile.write("                     bgp_group: IBGP-BR-CTZ-{}-PTPIBGP\n".format(catzilla_brick_number))
    outFile.write("                     policy: TURNUP-FILTERLIST-66\n")
    outFile.write("                 -\n")
    outFile.write("                  family: bgp\n")
    outFile.write("                  name: check_bgp_group_import_policy\n")
    outFile.write("                  args:\n")
    outFile.write("                     bgp_group: IPV6-IBGP-BR-CTZ-{}-PTPIBGP\n".format(catzilla_brick_number))
    outFile.write("                     policy: TURNUP-FILTERLIST-66\n")
    outFile.write("                 -\n")
    outFile.write("                  family: bgp\n")
    outFile.write("                  name: check_bgp_group_export_policy\n")
    outFile.write("                  args:\n")
    outFile.write("                     bgp_group: IPV6-IBGP-BR-CTZ-{}-PTPIBGP\n".format(catzilla_brick_number))
    outFile.write("                     policy: TURNUP-FILTERLIST-66\n")
    outFile.write("    PostShiftBack:\n")
    outFile.write("         -\n")
    outFile.write("          targets: .*\n")
    outFile.write("          checks:\n")
    outFile.write("                 -\n")
    outFile.write("                  family: general\n")
    outFile.write("                  name: check_no_chassis_alarms\n")
    outFile.write("                 -\n")
    outFile.write("                  family: general\n")
    outFile.write("                  name: check_no_system_alarms\n")
    outFile.write("                 -\n")
    outFile.write("                  family: traffic\n")
    outFile.write("                  name: check_interface_traffic_less_than\n")
    outFile.write("                  args:\n")
    outFile.write("                     interface: ")
    for router in sorted(devices, key=devices.get):
        if 'br-agg-r1' in router:
            lags = []
            for lag in sorted(devices[router], key=devices[router].get):
                lags.append(lag)
            delimiter = ','
            lags_group = delimiter.join(lags)
            outFile.write(lags_group + "\n")
    outFile.write("                     threshold: 100\n")
    outFile.close()
    print "Wrote file: out/bragg_prestage.yaml"


# Catzilla device
# CAT iad7-br-ctz-f1b2 TIER1 r1 LAG ae1 REMHOST iad7-br-agg-r1
# CAT iad7-br-ctz-f1b2 TIER1 r1 LAG ae1 REMLAG ae151
# CAT iad7-br-ctz-f1b2 TIER1 r1 LAG ae1 MINLINKS 4
# CAT iad7-br-ctz-f1b2 TIER1 r1 LAG ae1 MEMBER xe-0/0/0:0 REMPORT xe-0/0/4
# CAT iad7-br-ctz-f1b2 TIER1 r1 LAG ae1 MEMBER xe-0/0/1:1 REMPORT xe-1/2/5
# CAT iad7-br-ctz-f1b2 TIER1 r1 LAG ae1 MEMBER xe-0/0/2:0 REMPORT xe-8/0/4
# CAT iad7-br-ctz-f1b2 TIER1 r1 LAG ae1 MEMBER xe-0/0/3:0 REMPORT xe-9/2/4
# CAT iad7-br-ctz-f1b2 TIER1 r1 LAG ae1 IPADDR 100.65.8.0/31
# CAT iad7-br-ctz-f1b2 TIER1 r1 LAG ae1 IPV6ADDR a:b:c:d:8000:0:6441:800/127
#
# CAT iad7-br-ctz-f1b2 TIER1 r1 BGPNEIGH IBGP-BR-AGG-PTPIBGP IP 100.65.8.1 DESC iad7-br-agg-r1
# CAT iad7-br-ctz-f1b2 TIER1 r1 BGPNEIGH IBGP-BR-AGG-PTPIBGP IP 100.65.8.1 LOCALIP 100.65.8.0
# CAT iad7-br-ctz-f1b2 TIER1 r1 BGPNEIGH IPV6-IBGP-BR-AGG-PTPIBGP IP a:b:c:d:8000:0:6441:801 DESC iad7-br-agg-r1
# CAT iad7-br-ctz-f1b2 TIER1 r1 BGPNEIGH IPV6-IBGP-BR-AGG-PTPIBGP IP a:b:c:d:8000:0:6441:801 LOCALIP a:b:c:d:8000:0:6441:800

# Client device if br-fab
# LAG ae5 REMHOST iad7-br-ctz-f1b2-t1-r1
# LAG ae5 REMLAG ae5
# LAG ae5 MINLINKS 4
# LAG ae5 MEMBER xe-0/0/3 REMPORT xe-0/0/3:0
# LAG ae5 MEMBER xe-1/0/1 REMPORT xe-1/0/1:1
# LAG ae5 MEMBER xe-3/0/3 REMPORT xe-3/0/3:0
# LAG ae5 MEMBER xe-4/0/1 REMPORT xe-4/0/1:1
# LAG ae5 IPADDR 100.65.8.1/31
# LAG ae5 IPV6ADDR a:b:c:d:8000:0:6441:801/127
# BGPNEIGH IBGP-BR-CTZ-PTPIBGP IP 100.65.8.0 DESC iad7-br-ctz-f1b2-t1-r1
# BGPNEIGH IBGP-BR-CTZ-PTPIBGP IP 100.65.8.0 LOCALIP 100.65.8.1
# BGPNEIGH IPV6-IBGP-BR-CTZ-PTPIBGP IP a:b:c:d:8000:0:6441:800 DESC iad7-br-ctz-f1b2-t1-r1
# BGPNEIGH IPV6-IBGP-BR-CTZ-PTPIBGP IP a:b:c:d:8000:0:6441:800 LOCALIP a:b:c:d:8000:0:6441:801

# Client device if br-agg
# LAG ae5 REMHOST iad7-br-ctz-f1b2-t1-r1
# LAG ae5 REMLAG ae5
# LAG ae5 MINLINKS 4
# LAG ae5 MEMBER xe-0/0/3 REMPORT xe-0/0/3:0
# LAG ae5 MEMBER xe-1/0/1 REMPORT xe-1/0/1:1
# LAG ae5 MEMBER xe-3/0/3 REMPORT xe-3/0/3:0
# LAG ae5 MEMBER xe-4/0/1 REMPORT xe-4/0/1:1
# LAG ae5 IPADDR 100.65.8.1/31
# LAG ae5 IPV6ADDR a:b:c:d:8000:0:6441:801/127
# BGPNEIGH IBGP-BR-CTZ-B2-PTPIBGP IP 100.65.8.0 DESC iad7-br-ctz-f1b2-t1-r1
# BGPNEIGH IBGP-BR-CTZ-B2-PTPIBGP IP 100.65.8.0 LOCALIP 100.65.8.1
# BGPNEIGH IPV6-IBGP-BR-CTZ-B2-PTPIBGP IP a:b:c:d:8000:0:6441:800 DESC iad7-br-ctz-f1b2-t1-r1
# BGPNEIGH IPV6-IBGP-BR-CTZ-B2-PTPIBGP IP a:b:c:d:8000:0:6441:800 LOCALIP a:b:c:d:8000:0:6441:801
