#!/apollo/env/SDETools/bin/python

import csv
import argparse
import sys
import os.path
import re

DEFAULT_GBPATH = "/GenevaBuilderDCEdge/targetspec/border/shared"

parser = argparse.ArgumentParser()
parser.add_argument('--csv', help = 'CSV file containing the cutsheet', required = True)
parser.add_argument('--removev6', action='store_false', help = 'do not include v6 outputs in attribute files', required = False)
parser.add_argument("--path", dest="path", default= os.path.expanduser("~") + DEFAULT_GBPATH, required = False, help="Path to GenevaBuilder attributes, default: ~" + DEFAULT_GBPATH)

args = parser.parse_args()

csv_filename = args.csv
output_v6 = args.removev6
fabric_attr_dir = args.path

# Check if file exists
if not os.path.isfile(csv_filename):
    print "ERROR: Must specify valid CSV file name."
    sys.exit(1)
# Check if GB attribute folder exists
if not os.path.isdir(fabric_attr_dir):
    print "ERROR: Invalid path to GB attribute files: " + fabric_attr_dir
    print "       Try the commandline parameter '--path <path-to-your-GenevaBuilderDCedge-folder>'"
    sys.exit(1)

routers_bgp = {}
routers_iface = {}


# Initialize v6 customer prefix dictionary by pulling BASEIPV6SLASH64
# attributes from GenevaBuilder
if output_v6:
    V6PrefixDict96Bits = {}
    for file in os.listdir(fabric_attr_dir):
        if file.endswith(".attr"):
            pathname = (os.path.join(fabric_attr_dir, file))
            with open(pathname, "r") as current_file:
                for line in current_file:
                    if re.match("^[^#].*BASEIPV6SLASH64", line):
                        prefix_64bits = re.match('.*?((\w+:)+(\w)+)::/64', line).group(1)
                        prefix_96bits = prefix_64bits + ":8000:0:"

                        # filename should be of the format fabric-<dc>-<fabric_number> 
                        # but nothing currently enforces this :-(
                        dcfab = re.search("fabric-([a-z]{3}\d+)-f?(\d+)", file, re.IGNORECASE)
                        if dcfab:
                            fatcat_id = dcfab.group(1) + "-br-fab-f" + dcfab.group(2)
                            V6PrefixDict96Bits[ fatcat_id ] = prefix_96bits
                        else:
                            print "WARNING: Skipping " + "`" + file + "\' unexpected file name format! \'fabric-<dc>-<fabric_number>\'"


with open(csv_filename, 'rb') as csvfile:
    rows = csv.reader(csvfile)

    line = 0
    for row in rows:
        line += 1

        # CSV format validation
        if len(row) < 20:
            print "CSV format unrecognized."
            sys.exit(1)

        if (line == 1) and not ("ostname" in row[0]):
            print "CSV format unrecognized."
            sys.exit(1)
        elif line == 1:
            continue

        # Check the order of routers in CSV
        if 'br-agg' in row[0] and 'br-fab' in row[20]:
            br_agg = row[0]
            br_agg_port = row[2]
            br_fab = row[20]
            br_fab_port = row[18]
        elif 'br-agg' in row[20] and 'br-fab' in row[0]:
            br_agg = row[20]
            br_agg_port = row[18]
            br_fab = row[0]
            br_fab_port = row[2]
        else:
            print "WARNING: CSV format error on line " + str(line) + "."
            continue

        Lookup_Fatcat_id = str.split(br_fab, 't1-r')
        if output_v6:
            v6Prefix = V6PrefixDict96Bits[Lookup_Fatcat_id[0]]

        br_fab_port_number = int(br_fab_port.split("/")[2])
        br_fab_number = int(br_fab.split("-")[4][1:])
        
        def ipv4_2nd_half():
            (quotient,remainder) = divmod(br_fab_number,4)
            if remainder != 0:
                third_octet = 16+divmod(br_fab_number,4)[0]
                forth_octet = (remainder - 1) * 64 + br_fab_port_number * 2
                return (third_octet,forth_octet)
            else:
                third_octet = 16+divmod(br_fab_number,4)[0]-1
                forth_octet = (4 - 1) * 64 + br_fab_port_number * 2
            return (third_octet,forth_octet)

        br_fab_address = "100.64." + str(ipv4_2nd_half()[0]) + "." + str(ipv4_2nd_half()[1])
        br_fab_address_mask = br_fab_address + "/31"

        def fab_last_v6_quibble():
            (quotient,remainder) = divmod(br_fab_number,4)
            if remainder != 0:
                fab_last_v6_quibble = hex(((16+divmod(br_fab_number,4)[0])*256) + (remainder - 1) * 64 + br_fab_port_number * 2 )[2:]
            else:
                fab_last_v6_quibble = hex(((16+divmod(br_fab_number,4)[0]-1)*256) + (4 - 1) * 64 + br_fab_port_number * 2 )[2:]
            return fab_last_v6_quibble

        def agg_last_v6_quibble():
            (quotient,remainder) = divmod(br_fab_number,4)
            if remainder != 0:
                agg_last_v6_quibble = hex(((16+divmod(br_fab_number,4)[0])*256) + (remainder - 1) * 64 + br_fab_port_number * 2 + 1)[2:]
            else:
                agg_last_v6_quibble = hex(((16+divmod(br_fab_number,4)[0]-1)*256) + (4 - 1) * 64 + br_fab_port_number * 2 + 1)[2:]
            return agg_last_v6_quibble


        if output_v6:
            br_fab_address_v6 = v6Prefix + "6440:" + str(fab_last_v6_quibble())
            br_fab_address_mask_v6 = br_fab_address_v6 + "/127"

        br_agg_address = "100.64." + str(ipv4_2nd_half()[0]) + "." + str(ipv4_2nd_half()[1] + 1)
        br_agg_address_mask = br_agg_address + "/31"

        if output_v6:
            br_agg_address_v6 = v6Prefix + "6440:" + str(agg_last_v6_quibble())
            br_agg_address_mask_v6 = br_agg_address_v6 + "/127"

        # Initialize dictionaries
        if br_fab not in routers_bgp.iterkeys():
            routers_bgp[br_fab] = ""
            routers_iface[br_fab] = ""

        if br_agg not in routers_bgp.iterkeys():
            routers_bgp[br_agg] = ""
            routers_iface[br_agg] = ""

        # Generate attribute files: br-fab side
        routers_bgp[br_fab] += "BGPNEIGH IBGP-BR-AGG-PTPIBGP IP " + br_agg_address + " DESC " + br_agg + "\n"
        routers_bgp[br_fab] += "BGPNEIGH IBGP-BR-AGG-PTPIBGP IP " + br_agg_address + " LOCALIP " + br_fab_address + "\n"

        if output_v6:
            routers_bgp[br_fab] += "BGPNEIGH IPV6-IBGP-BR-AGG-PTPIBGP IP " + br_agg_address_v6 + " DESC " + br_agg + "\n"
            routers_bgp[br_fab] += "BGPNEIGH IPV6-IBGP-BR-AGG-PTPIBGP IP " + br_agg_address_v6 + " LOCALIP " + br_fab_address_v6 + "\n\n"
        else:
            routers_bgp[br_fab] += "\n"

        routers_iface[br_fab] += "IFACE L3 " + br_fab_port + " DESC " + '"' + br_fab + " " + br_fab_port + " --> " + br_agg_port + " " + br_agg + '"\n'
        routers_iface[br_fab] += "IFACE L3 " + br_fab_port + " MTU 9192\n"
        routers_iface[br_fab] += "IFACE L3 " + br_fab_port + " UNIT 0 IP " + br_fab_address_mask + "\n"
        routers_iface[br_fab] += "IFACE L3 " + br_fab_port + " UNIT 0 MTU 9100\n"

        if output_v6:
            routers_iface[br_fab] += "IFACE L3 " + br_fab_port + " UNIT 0 IPV6 " + br_fab_address_mask_v6 + "\n\n"
        else:
            routers_iface[br_fab] += "\n"

        # Generate attribute files: br-agg side
        routers_bgp[br_agg] += "BGPNEIGH IBGP-BR-FABRIC-PTPIBGP IP " + br_fab_address + " DESC " + br_fab + "\n"
        routers_bgp[br_agg] += "BGPNEIGH IBGP-BR-FABRIC-PTPIBGP IP " + br_fab_address + " LOCALIP " + br_agg_address + "\n"

        if output_v6:
            routers_bgp[br_agg] += "BGPNEIGH IPV6-IBGP-BR-FABRIC-PTPIBGP IP " + br_fab_address_v6 + " DESC " + br_fab + "\n"
            routers_bgp[br_agg] += "BGPNEIGH IPV6-IBGP-BR-FABRIC-PTPIBGP IP " + br_fab_address_v6 + " LOCALIP " + br_agg_address_v6 + "\n\n"
        else:
            routers_bgp[br_agg] += "\n"

        routers_iface[br_agg] += "IFACE L3 " + br_agg_port + " DESC " + '"' + br_agg + " " + br_agg_port + " --> " + br_fab_port + " " + br_fab + '"\n'
        routers_iface[br_agg] += "IFACE L3 " + br_agg_port + " MTU 9192\n"
        routers_iface[br_agg] += "IFACE L3 " + br_agg_port + " UNIT 0 IP " + br_agg_address_mask + "\n"
        routers_iface[br_agg] += "IFACE L3 " + br_agg_port + " UNIT 0 MTU 9100\n"

        if output_v6:
            routers_iface[br_agg] += "IFACE L3 " + br_agg_port + " UNIT 0 IPV6 " + br_agg_address_mask_v6 + "\n\n"
        else:
            routers_iface[br_agg] += "\n"

# Print the resulting attributes
for router in sorted(routers_bgp.iterkeys()):
    print "\n\n"
    print "=== %s bgp.attr ===\n" % router
    print routers_bgp[router]
    print "\n\n"
    print "=== %s iface-l3interface.attr ===\n" % router
    print routers_iface[router]
