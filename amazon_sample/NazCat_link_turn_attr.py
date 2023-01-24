#!/apollo/env/SDETools/bin/python

import csv
import argparse
import sys
import os.path


parser = argparse.ArgumentParser()
parser.add_argument('--csv', help = 'CSV file containing the cutsheet', required = True)
parser.add_argument('--fabric', help = 'Fabric we are generating attr for (ex. dub50-br-fab-f1)', required = True)
parser.add_argument('--removev6', action='store_false', help = 'do not include v6 outputs in attribute files', required = False)
parser.add_argument('--out', help = 'output directory name', required = True)

args = parser.parse_args()

csv_filename = args.csv
output_v6 = args.removev6
target_fabric = args.fabric
FABRIC=args.fabric.lower()
outdir = args.out


# Check if file exists
if not os.path.isfile(csv_filename):
    print "ERROR: Must specify valid CSV file name."
    sys.exit(1)

if not os.path.exists(outdir):
    os.makedirs(outdir)

routers_bgp = {}
routers_iface = {}


# Initialize v6 customer prefix dictionary by pulling BASEIPV6SLASH64
# attributes from GenevaBuilder
home = os.path.expanduser("~")
fabric_attr_dir = home + "/GenevaBuilder/targetspec/border/" + target_fabric
if output_v6:
    V6PrefixDict96Bits = {}
    for file in os.listdir(fabric_attr_dir):
        if file.endswith(".attr"):
            pathname = (os.path.join(fabric_attr_dir, file))
            with open(pathname, "r") as current_file:
                for line in current_file:
                    if "BASEIPV6SLASH64" in line:
                        prefix_total = line.split('"');
                        prefix_64bits = prefix_total[1].split('::/')
                        prefix_96bits = prefix_64bits[0] + ":8000:0:"

                        # filename should be of the format fabric-<dc>-<fabric_number> 
                        # but nothing currently enforces this :-(
                        filename_parts = file.split('-')
                        fabric_number = filename_parts[3]
                        fatcat_id = filename_parts[0] + "-br-fab-f" + fabric_number
                        V6PrefixDict96Bits[ fatcat_id ] = prefix_96bits

with open(csv_filename, 'rb') as csvfile:
    rows = csv.reader(csvfile)

    line = 0
    for row in rows:
        line += 1

        # CSV format validation
        if len(row) < 10:
            print "CSV format unrecognized."
            sys.exit(1)

        if (line == 1) and not ("ostname" in row[0]):
            print "CSV format unrecognized."
            sys.exit(1)
        elif line == 1:
            continue

        # Check the order of routers in CSV
        if 'br-agg' in row[0]:
            br_agg = row[0]
            br_agg_port = row[2]
            br_fab = row[10]
            br_fab_port = row[8]
        elif 'br-agg' in row[10]:
            br_agg = row[10]
            br_agg_port = row[8]
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

#####################################################################################################################
## Generate V4 and V6 IP addresses for br-fab-f1-r[1-4]
#####################################################################################################################

        # For Ports xe-0/0/0 to xe-0/0/15
        if br_fab_port_number < 16 and br_fab_number <= 2:
            #print "Port: %d and Router Num: %d" % (br_fab_port_number, br_fab_number)
            br_fab_address = "100.64.16." + str( (br_fab_number - 1) * 128 + br_fab_port_number * 2)
            br_fab_address_mask = br_fab_address + "/31"

            fab_last_v6_quibble = hex((16*256) + (br_fab_number - 1) * 128 + br_fab_port_number * 2 )[2:]
            if output_v6:
                br_fab_address_v6 = v6Prefix + "6440:" + str(fab_last_v6_quibble)
                br_fab_address_mask_v6 = br_fab_address_v6 + "/127"

        if br_fab_port_number < 16 and br_fab_number > 2:
            br_fab_address = "100.64.17." + str( (br_fab_number - 3) * 128 + br_fab_port_number * 2)
            br_fab_address_mask = br_fab_address + "/31"

            fab_last_v6_quibble = hex(256 + (16*256) + (br_fab_number - 3) * 128 + br_fab_port_number * 2 )[2:]
            if output_v6:
                br_fab_address_v6 = v6Prefix + "6440:" + str(fab_last_v6_quibble)
                br_fab_address_mask_v6 = br_fab_address_v6 + "/127"

        # For ports xe-0/0/24 to xe-0/0/47
        if br_fab_port_number > 23 and br_fab_port_number < 48 and br_fab_number <= 2:
            br_fab_address = "100.64.16." + str( (br_fab_number - 1) * 128 + (br_fab_port_number - 8) * 2)
            br_fab_address_mask = br_fab_address + "/31"

            fab_last_v6_quibble = hex((16*256) + (br_fab_number - 1) * 128 + (br_fab_port_number - 8) * 2 )[2:]
            if output_v6:
                br_fab_address_v6 = v6Prefix + "6440:" + str(fab_last_v6_quibble)
                br_fab_address_mask_v6 = br_fab_address_v6 + "/127"

        if br_fab_port_number > 23 and br_fab_port_number < 48 and br_fab_number > 2:
            br_fab_address = "100.64.17." + str( (br_fab_number - 3) * 128 + (br_fab_port_number - 8) * 2)
            br_fab_address_mask = br_fab_address + "/31"

            fab_last_v6_quibble = hex(256 + (16*256) + (br_fab_number - 3) * 128 + (br_fab_port_number - 8) * 2 )[2:]
            if output_v6:
                br_fab_address_v6 = v6Prefix + "6440:" + str(fab_last_v6_quibble)
                br_fab_address_mask_v6 = br_fab_address_v6 + "/127"

        # For ports xe-0/0/48 to xe-0/0/71
        if br_fab_port_number > 47 and br_fab_port_number < 72 and br_fab_number <= 2:
            br_fab_address = "100.64.16." + str( (br_fab_number - 1) * 128 + (br_fab_port_number - 16) * 2)
            br_fab_address_mask = br_fab_address + "/31"

            fab_last_v6_quibble = hex((16*256) + (br_fab_number - 1) * 128 + (br_fab_port_number - 16) * 2 )[2:]
            if output_v6:
                br_fab_address_v6 = v6Prefix + "6440:" + str(fab_last_v6_quibble)
                br_fab_address_mask_v6 = br_fab_address_v6 + "/127"

        if br_fab_port_number > 47 and br_fab_port_number < 72 and br_fab_number > 2:
            br_fab_address = "100.64.17." + str( (br_fab_number - 3) * 128 + (br_fab_port_number - 16) * 2)
            br_fab_address_mask = br_fab_address + "/31"

            fab_last_v6_quibble = hex(256 + (16*256) + (br_fab_number - 3) * 128 + (br_fab_port_number - 16) * 2 )[2:]
            if output_v6:
                br_fab_address_v6 = v6Prefix + "6440:" + str(fab_last_v6_quibble)
                br_fab_address_mask_v6 = br_fab_address_v6 + "/127"

        # For ports xe-0/0/72 to xe-0/0/95
        if br_fab_port_number > 71 and br_fab_port_number < 96 and br_fab_number <= 2:
            br_fab_address = "100.64.16." + str( (br_fab_number - 1) * 128 + (br_fab_port_number - 24) * 2)
            br_fab_address_mask = br_fab_address + "/31"

            fab_last_v6_quibble = hex((16*256) + (br_fab_number - 1) * 128 + (br_fab_port_number - 24))[2:]
            if output_v6:
                br_fab_address_v6 = v6Prefix + "6440:" + str(fab_last_v6_quibble)
                br_fab_address_mask_v6 = br_fab_address_v6 + "/127"

        if br_fab_port_number > 71 and br_fab_port_number < 96 and br_fab_number > 2:
            br_fab_address = "100.64.17." + str( (br_fab_number - 3) * 128 + (br_fab_port_number - 24) * 2)
            br_fab_address_mask = br_fab_address + "/31"

            fab_last_v6_quibble = hex(256 + (16*256) + (br_fab_number - 3) * 128 + (br_fab_port_number - 24) * 2 )[2:]
            if output_v6:
                br_fab_address_v6 = v6Prefix + "6440:" + str(fab_last_v6_quibble)
                br_fab_address_mask_v6 = br_fab_address_v6 + "/127"

#####################################################################################################################
## Generate V4 and V6 IP addresses for br-agg-r[1-4]
#####################################################################################################################

        # For Ports xe-0/0/0 to xe-0/0/15
        if br_fab_port_number < 16 and br_fab_number <= 2:
            br_agg_address = "100.64.16." + str( (br_fab_number - 1) * 128 + br_fab_port_number * 2 + 1)
            br_agg_address_mask = br_agg_address + "/31"

            agg_last_v6_quibble = hex((16*256) + (br_fab_number - 1) * 128 + br_fab_port_number * 2 + 1)[2:]
            if output_v6:
                br_agg_address_v6 = v6Prefix + "6440:" + str(agg_last_v6_quibble)
                br_agg_address_mask_v6 = br_agg_address_v6 + "/127"

        if br_fab_port_number < 16 and br_fab_number > 2:
            br_agg_address = "100.64.17." + str( (br_fab_number - 3) * 128 + br_fab_port_number * 2 + 1)
            br_agg_address_mask = br_agg_address + "/31"

            agg_last_v6_quibble = hex(256 + (16*256) + (br_fab_number - 3) * 128 + br_fab_port_number * 2 + 1)[2:]
            if output_v6:
                br_agg_address_v6 = v6Prefix + "6440:" + str(agg_last_v6_quibble)
                br_agg_address_mask_v6 = br_agg_address_v6 + "/127"

        # For ports xe-0/0/24 to xe-0/0/47
        if br_fab_port_number > 23 and br_fab_port_number < 48 and br_fab_number <= 2:
            br_agg_address = "100.64.16." + str( (br_fab_number - 1) * 128 + (br_fab_port_number - 8) * 2 + 1)
            br_agg_address_mask = br_agg_address + "/31"

            agg_last_v6_quibble = hex((16*256) + (br_fab_number - 1) * 128 + (br_fab_port_number - 8) * 2 + 1)[2:]
            if output_v6:
                br_agg_address_v6 = v6Prefix + "6440:" + str(agg_last_v6_quibble)
                br_agg_address_mask_v6 = br_agg_address_v6 + "/127"

        if br_fab_port_number > 23 and br_fab_port_number < 48 and br_fab_number > 2:
            br_agg_address = "100.64.17." + str( (br_fab_number - 3) * 128 + (br_fab_port_number - 8) * 2 + 1)
            br_agg_address_mask = br_agg_address + "/31"

            agg_last_v6_quibble = hex(256 + (16*256) + (br_fab_number - 3) * 128 + (br_fab_port_number - 8) * 2 + 1)[2:]
            if output_v6:
                br_agg_address_v6 = v6Prefix + "6440:" + str(agg_last_v6_quibble)
                br_agg_address_mask_v6 = br_agg_address_v6 + "/127"

        # For ports xe-0/0/48 to xe-0/0/71
        if br_fab_port_number > 47 and br_fab_port_number < 72 and br_fab_number <= 2:
            br_agg_address = "100.64.16." + str( (br_fab_number - 1) * 128 + (br_fab_port_number - 16) * 2 + 1)
            br_agg_address_mask = br_agg_address + "/31"

            agg_last_v6_quibble = hex((16*256) + (br_fab_number - 1) * 128 + (br_fab_port_number - 16) * 2 + 1)[2:]
            if output_v6:
                br_agg_address_v6 = v6Prefix + "6440:" + str(agg_last_v6_quibble)
                br_agg_address_mask_v6 = br_agg_address_v6 + "/127"

        if br_fab_port_number > 47 and br_fab_port_number < 72 and br_fab_number > 2:
            br_agg_address = "100.64.17." + str( (br_fab_number - 3) * 128 + (br_fab_port_number - 16) * 2 + 1)
            br_agg_address_mask = br_agg_address + "/31"

            agg_last_v6_quibble = hex(256 + (16*256) + (br_fab_number - 3) * 128 + (br_fab_port_number - 16) * 2 + 1)[2:]
            if output_v6:
                br_agg_address_v6 = v6Prefix + "6440:" + str(agg_last_v6_quibble)
                br_agg_address_mask_v6 = br_agg_address_v6 + "/127"

        # For ports xe-0/0/72 to xe-0/0/95
        if br_fab_port_number > 71 and br_fab_port_number < 96 and br_fab_number <= 2:
            br_agg_address = "100.64.16." + str( (br_fab_number - 1) * 128 + (br_fab_port_number - 24) * 2 + 1)
            br_agg_address_mask = br_agg_address + "/31"

            agg_last_v6_quibble = hex((16*256) + (br_fab_number - 1) * 128 + (br_fab_port_number - 24) * 2 + 1)[2:]
            if output_v6:
                br_agg_address_v6 = v6Prefix + "6440:" + str(agg_last_v6_quibble)
                br_agg_address_mask_v6 = br_agg_address_v6 + "/127"

        if br_fab_port_number > 71 and br_fab_port_number < 96 and br_fab_number > 2:
            br_agg_address = "100.64.17." + str( (br_fab_number - 3) * 128 + (br_fab_port_number - 24) * 2 + 1)
            br_agg_address_mask = br_agg_address + "/31"

            agg_last_v6_quibble = hex(256 + (16*256) + (br_fab_number - 3) * 128 + (br_fab_port_number - 24) * 2 + 1)[2:]
            if output_v6:
                br_agg_address_v6 = v6Prefix + "6440:" + str(agg_last_v6_quibble)
                br_agg_address_mask_v6 = br_agg_address_v6 + "/127"


#####################################################################################################################
## Old Code for br-agg
#####################################################################################################################
#
#        br_agg_address = "100.64.16." + str((br_fab_number - 1) * 64 + br_fab_port_number * 2 + 1)
#        br_agg_address_mask = br_agg_address + "/31"
#
#        agg_last_v6_quibble = hex((16*256) + (br_fab_number - 1) * 64 + br_fab_port_number * 2 + 1)[2:]
#        if output_v6:
#            br_agg_address_v6 = v6Prefix + "6440:" + str(agg_last_v6_quibble)
#            br_agg_address_mask_v6 = br_agg_address_v6 + "/127"
#
#####################################################################################################################
## Initialize dictionaries
#####################################################################################################################

        if br_fab not in routers_bgp.iterkeys():
            routers_bgp[br_fab] = ""
            routers_iface[br_fab] = ""

        if br_agg not in routers_bgp.iterkeys():
            routers_bgp[br_agg] = ""
            routers_iface[br_agg] = ""

        # Generate attribute files: br-fab side
        routers_bgp[br_fab] += "CAT " + FABRIC + " TIER1 " + "t1-r"+Lookup_Fatcat_id[1] + " BGPNEIGH IBGP-BR-AGG-PTPIBGP IP " + br_agg_address + " DESC " + br_agg + "\n"
        routers_bgp[br_fab] += "CAT " + FABRIC + " TIER1 " + "t1-r"+Lookup_Fatcat_id[1] + " BGPNEIGH IBGP-BR-AGG-PTPIBGP IP " + br_agg_address + " LOCALIP " + br_fab_address + "\n"

        if output_v6:
            routers_bgp[br_fab] += "CAT " + FABRIC + " TIER1 " + "t1-r"+Lookup_Fatcat_id[1] + " BGPNEIGH IPV6-IBGP-BR-AGG-PTPIBGP IP " + br_agg_address_v6 + " DESC " + br_agg + "\n"
            routers_bgp[br_fab] += "CAT " + FABRIC + " TIER1 " + "t1-r"+Lookup_Fatcat_id[1] + " BGPNEIGH IPV6-IBGP-BR-AGG-PTPIBGP IP " + br_agg_address_v6 + " LOCALIP " + br_fab_address_v6 + "\n\n"
        else:
            routers_bgp[br_fab] += "\n"

        routers_iface[br_fab] += "CAT " + FABRIC + " TIER1 " + "t1-r"+Lookup_Fatcat_id[1] + " CATIF " + br_fab_port + " ROLE BR-AGG " "\n"
        routers_iface[br_fab] += "CAT " + FABRIC + " TIER1 " + "t1-r"+Lookup_Fatcat_id[1] + " CATIF " + br_fab_port + " REMIFACE " + br_agg_port + "\n"
        routers_iface[br_fab] += "CAT " + FABRIC + " TIER1 " + "t1-r"+Lookup_Fatcat_id[1] + " CATIF " + br_fab_port + " REMHOST " + br_agg + "\n\n"
        
              
        

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
# output files will be saved under Azx-br-fab-f1

for router in sorted(routers_bgp.iterkeys()):
    if os.path.exists(os.path.join(outdir, router+"-fab-bgp.attr")):
          os.remove(os.path.join(outdir, router+"-fab-bgp.attr"))
          with open(os.path.join(outdir, router+"-fab-bgp.attr"),"a") as bgp_file:
               bgp_file.write(routers_bgp[router])
    else:
         with open(os.path.join(outdir, router+"-fab-bgp.attr"),"a") as bgp_file:
               bgp_file.write(routers_bgp[router])
         
    if os.path.exists(os.path.join(outdir,router+"-fab-iface-l3interface.attr")):
          os.remove(os.path.join(outdir,router+"-fab-iface-l3interface.attr"))
          with open(os.path.join(outdir,router+"-fab-iface-l3interface.attr"),"a") as l3interface_file:
               l3interface_file.write(routers_iface[router])
    else:
         with open(os.path.join(outdir,router+"-fab-iface-l3interface.attr"),"a") as l3interface_file:
               l3interface_file.write(routers_iface[router])

    #print "\n\n"
    #print "=== %s bgp.attr ===\n" % router
    #print routers_bgp[router]
    #print "\n\n"
    #print "=== %s iface-l3interface.attr ===\n" % router
    #print routers_iface[router]
