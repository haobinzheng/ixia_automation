#!/apollo/bin/env -e NetengTools python

# ctz_fabic_attr.py
# This script generates the Geneva Builder attributes for the Catzilla Bricks and Spine Rows in a set of 8 Bricks (16 B-TORs) and 8 Spine Rows (8 S-TORS).
# The IP blocks allocated for the connection between the B-TORs and the T1/T2/T3 devices are /23s and the connection between S-TORs and T1/T2/T3 devices are /24s.
# These /23s and /24s may NOT be contiguous.
# In a /23 there can be 16 B-TORs (8 Bricks) and in a /24 there can be 8 S-TORs (8 Spine rows)

# The scripts get the variables from a txt file stored at the same path with this script
# Example of the variable file:
### AZ                  = 'dub8'              # What is the AZ? Ex: iad7
### brick_set_no        = '1'                 # Please enter the number of the 8-bricks set: Ex: 1 for the first 8 Bricks, 2 for the Bricks 9 to 16, etc...
### brick_range         = [1,3]               # Range of bricks in this deployment as list. For single brick repeat number: [4,4] to deploy only brick 4
### spine_row_set_no    = '1'                 # Please enter the number of the 8-spine_row set: Ex: 1 for the first 8 Spine_Rows or 2 for the Spine_Rows 9 to 16
### brick_base_ip       = '100.90.54.0'       # Enter the IP address block B-TOR to Rack Devices - a /23 without the mask: Ex: 100.90.6.0 . This would have been assigned during the MGMT build .
### spine_base_ip       = '100.90.56.0'       # Enter the IP address block S-TOR to Rack Devices - a /24 without the mask: Ex: 100.90.8.0 . This would have been assigned during the MGMT build .
### os_version          = '14.1X53-D28.4'     # Enter JunOS code version
### fw_version          = 'V0018.7'           # Enter Firmware version (BIOS)
### turnup_state        = 'TURNUP'            # OPTIONAL (comment line out if unneeded): Enter the Turnup state: Ex: TURNUP
### cluster_id          = '0.7.10.64'         # OPTIONAL (if brick set 1 and brick is 1 or 2): Enter the Cluster ID block - a /26 without the mask: Ex: 0.7.3.0 - needed if 'brick_set_no' = '1'
### ipv6_subnet         = '2a01:578:0:4009::' # OPTIONAL (if brick set 1 and brick is 1 or 2): Enter the ipv6 /64 infrastructure subnet for the ctz - a /64 without the mask: Ex: 2804:800:0:4000::
### s3_public_subnet    = '2a05:d050:8020::'  # OPTIONAL (if brick set 1 and brick is 1 or 2): Enter the S3 public ipv6 subnet - a /44 without the mask: Ex: 2600:1fa0:e080::
### s3_vpc_endpoint     = '2a05:d079:8020::'  # OPTIONAL (if brick set 1 and brick is 1 or 2): Enter the S3 vpcendpoint subnet - a /46 without the mask: Ex: 2600:1ff8:e080::
### vpc_endpoint_subnet = '2a05:d07c:8020::'  # OPTIONAL (if brick set 1 and brick is 1 or 2): Enter the non-S3 vpc endpoint subnet - a /46 without the mask: Ex: 2600:1ffc:e080::

# Change Log:
# Version    Author       Date          Comments
# 1.0        radupa@      2015.10.02    Initial version of script
# 2.0        jorulu@      2016.12.16    Added generation of additional attributes if this is the brick_set_no = 1, code is based on muctz_fabric_attr.py
#                                       b[12]-brickspecific.attr, b2-statics.attr, shared/br-ctz-f1.attr, shared/ipv6/../prefixlist-, shared/ipv6/../static-
# 2.3        adadod@      2017.08.16    Script cleans up after itself, moving attributes to proper directories, deleting its out folder, adds CONFER BRICKS
#                                       attribute based on number of bricks, and no longer ouptputs Fatcat attributes.

import sys
import socket, struct
import os.path
import shutil
import argparse
import ipaddr
from distutils import dir_util
from distutils import file_util
from distutils import log
from ipaddr import IPv4Address
#from ipaddr import IPAddrBase
from ipaddr import IPv6Network

parser = argparse.ArgumentParser()
parser.add_argument('--txt', help = 'TXT file containing the variables', required = True)
args = parser.parse_args()
var_file = args.txt

# Check if file exists
if not os.path.isfile(var_file):
    print "ERROR: Must specify valid TXT file name."
    sys.exit(1)

# Define the function that pulls the variables from a txt file

def getVarFromFile(var_file):
  import imp
  with open(var_file) as f:
      global data
      data = imp.new_module('data')
      exec(f.read(), data.__dict__)
      f.close()
getVarFromFile(os.getcwd() + '/'+var_file)
AZ = data.AZ
brick_set_no = int(data.brick_set_no)
spine_row_set_no = int(data.spine_row_set_no)
brick_base_ip = data.brick_base_ip
brick_lower = int(data.brick_range[0])
brick_upper = int(data.brick_range[1])
brick_range = data.brick_range
spine_base_ip = data.spine_base_ip
os_version = data.os_version
fw_version = data.fw_version 
try:
  turnup_state = data.turnup_state     
except:
  pass

# Pre-validation of the variable file
if brick_set_no not in range(1,5):
    print'There is a maximum of 32 Bricks, thus a maximum of 4 sets of 8 Bricks.\nPlease set "the brick_set_no" value from the [1-4] interval!'
    exit()
if spine_row_set_no not in range(1,3):
    print'There is a maximum of 16 Spine rows, thus a maximum of 2 sets of 8 Spine rows.\nPlease set the "spine_row_set_no" 1 or 2!'
    exit()
if not (int(brick_base_ip.split('.')[3]) == 0):
    print 'The values for "brick_base_ip" is not a valid one.\n You entered: ' + brick_base_ip
    exit()
if not (int(spine_base_ip.split('.')[3]) == 0):
    print 'The values for "spine_base_ip" is not a valid one.\n You entered: ' + spine_base_ip
    exit()
if brick_lower > brick_upper:
    print "Lower brick '{}' can't be greater than upper brick '{}'".format(brick_lower, brick_upper)
    exit()
if brick_lower < 1:
    print "You entered '{}' as your lower range for bricks. You can't have less than one brick!".format(brick_lower)
    exit()

# Define REGION:
REGION = str(AZ.split()[0][:3])

dec_brick_base_ip = int(IPv4Address(brick_base_ip))
dec_spine_base_ip = int(IPv4Address(spine_base_ip))
first_brick = (brick_set_no-1)*8
first_spine_row = (spine_row_set_no-1)*8

# Dictionaries:
brick_subnets = {}    # Here we will have the /27 for all the Brick Racks
spine_subnets = {}    # Here we will have the /27 for all the Spine Racks

# Delete the "out_ctz_attr" folder if one exists because otherwise every cicle of the script will append data to the existing
# attr files from the "out_ctz_attr" directory
if os.path.exists('out_ctz_attr'):
   os.system('rm -r out_ctz_attr')

#############
## Generates the attributes for all the Brick and output the content in the "out_ctz_attr" file
#############

for i in range(1,9): 
        brick_name = "brick_" + str(i+first_brick) + "_rack_1";
        brick_subnets[brick_name] = ""
        brick_subnets[brick_name] = dec_brick_base_ip + (i*2-2)*32
        brick_name = "brick_" + str(i+first_brick) + "_rack_2";
        brick_subnets[brick_name] = dec_brick_base_ip + (i*2-1)*32


for i in sorted(brick_subnets):
        #Get brick number and rack number
    (brick_no, rack_no)=(int(i.split('_')[1]), int(i.split('_')[3]))
    attr_file_name = AZ + "-br-ctz-f1b"+str(brick_no)+"-fabric.attr"
    fabric_name = AZ + "-br-ctz-f1b"+str(brick_no)
    path = 'out_ctz_attr/'+fabric_name+'/'
    if not os.path.exists(path):
       os.makedirs(path)
    outfile = path+ attr_file_name
    outFile = open(outfile, 'a')

    if not (rack_no%2 == 0):
        outFile.write("# File auto-generated by Catzilla ctz_fabric_attr.py\n# Do NOT edit by hand!\n\n")
        outFile.write('#################################################\n##' + fabric_name + '\n##\n#################################################\n\n')
        outFile.write("## I'm here just to make substitution not break\n")
        outFile.write("FABRICNAME " + fabric_name + "\n" + "TOPOLOGY ctzbrick24q\n")
        outFile.write("MGMT TOR "+ AZ +"-br-ctz-f1mgmt-b"+str(brick_no)+"-r1\n")
        outFile.write("MGMT TOR "+ AZ +"-br-ctz-f1mgmt-b"+str(brick_no)+"-r2\n")
        try:
           outFile.write("CAT "+ fabric_name +" CONFER BUILDSTATE "+ turnup_state + "\n\n")
        except:
           pass
        outFile.write("CAT "+ fabric_name +" CONFER FABRICNAME "+ fabric_name + "\n")
        outFile.write("CAT "+ fabric_name +" CONFER OS-VERSION " + os_version + "\n")
        outFile.write("CAT "+ fabric_name +" CONFER FW-VERSION " + fw_version + "\n\n")
        outFile.write("CAT "+ fabric_name + " TEMPLATE ctz-brick.attr\n")
        outFile.write("CAT "+ fabric_name + " TEMPLATE ctz-b" + str(brick_no) +".attr\n")
        outFile.write("CAT "+ fabric_name + " TEMPLATE ctz-brick-t1-to-t2.attr\n")
        outFile.write("CAT "+ fabric_name + " TEMPLATE ctz-brick-t2-to-t1.attr\n")
        outFile.write("CAT "+ fabric_name + " TEMPLATE "+ AZ +"-br-ctz-f1.attr\n\n")
        outFile.write("CAT "+ fabric_name + " CONFER MGMT-MASK /27\n")
        outFile.write("CAT "+ fabric_name + " MGMT MGMT-NET " + str(IPv4Address(brick_subnets[i])) +"/27\n")
        outFile.write("CAT "+ fabric_name + " MGMT MGMT-NET " + str(IPv4Address(brick_subnets[i]+32)) +"/27\n")
        
        outFile.write("\n## IP address attributes for Rack 1")
        outFile.write("\n# Management IPs Rack 1\n")
        for y in range(2,18):
            var_rack1 = brick_subnets[i] +y
            if (y < 10):
                router_no = ((y-1)*2)-1
                outFile.write("CAT "+ fabric_name + " TIER1 r" + str(router_no) + " MANAGEMENTIP " + str(IPv4Address(var_rack1))+"\n")
            else:
                router_no = ((y-9)*2)-1
                outFile.write("CAT "+ fabric_name + " TIER2 r" + str(router_no) + " MANAGEMENTIP " + str(IPv4Address(var_rack1))+"\n")    
        outFile.write("# Management BGP peer Rack 1\n")
        for z in range(2,18):
            if (z < 10):
                router_no = ((z-1)*2)-1
                outFile.write("CAT "+ fabric_name + " TIER1 r" + str(router_no) + " MGMTPBGPIP " + str(IPv4Address(brick_subnets[i]+1))+"\n")
            else:
                router_no = ((z-9)*2)-1
                outFile.write("CAT "+ fabric_name + " TIER2 r" + str(router_no) + " MGMTPBGPIP " + str(IPv4Address(brick_subnets[i]+1))+"\n")
        
        outFile.write("\n## IP address attributes for Rack 2")
        outFile.write("\n# Management IPs Rack 2\n")
        for y in range(2,18):
            var_rack2 = brick_subnets[i]+32 +y
            if (y < 10):
                router_no = ((y-1)*2)
                outFile.write("CAT "+ fabric_name + " TIER1 r" + str(router_no) + " MANAGEMENTIP " + str(IPv4Address(var_rack2))+"\n")
            else:
                router_no = ((y-9)*2)
                outFile.write("CAT "+ fabric_name + " TIER2 r" + str(router_no) + " MANAGEMENTIP " + str(IPv4Address(var_rack2))+"\n")
        outFile.write("# Management BGP peer Rack 2\n")
        for z in range(2,18):
            if (z < 10):
                router_no = ((z-1)*2)
                outFile.write("CAT "+ fabric_name + " TIER1 r" + str(router_no) + " MGMTPBGPIP " + str(IPv4Address(brick_subnets[i]+33))+"\n")
            else:
                router_no = ((z-9)*2)
                outFile.write("CAT "+ fabric_name + " TIER2 r" + str(router_no) + " MGMTPBGPIP " + str(IPv4Address(brick_subnets[i]+33))+"\n")
        outFile.write("\n## Breaking up 40GigE ports to 10GigE ports\n")
        outFile.write("# This is not done via the DEFINE template approach because we will have in the future customers that will need 40GigE ports\n")
        outFile.write("# on some of the T1 routers. DEFINE template will confer the same ranges to ALL T1s.\n")
        for i in range (1,17):
            outFile.write("CAT " + fabric_name + " TIER1 r" + str(i) + " CHASSIS PIC 0 RANGE 0 TO 15 SPEED 10\n")
    outFile.close()

#############
## Generates the attributes for all the Spine TORs and output the content in a per router folder
#############

for i in range(1,9):
        spine_name = "spine_row_" + str(i+first_spine_row);
        spine_subnets[spine_name] = ""
        spine_subnets[spine_name] = dec_spine_base_ip + (i-1)*32

for i in sorted(spine_subnets):
        #Get spine row number
   spine_no=int(i.split('_')[2])
   attr_file_name = AZ + "-br-ctz-f1s"+str(spine_no)+"-fabric.attr"
   fabric_name = AZ + "-br-ctz-f1s"+str(spine_no)
   path = 'out_ctz_attr/'+fabric_name+'/'
   if not os.path.exists(path):
      os.makedirs(path)
   outfile = path + attr_file_name
   outFile = open(outfile, 'a')
   outFile.write("# File auto-generated by Catzilla ctz_fabric_attr.py\n# Do NOT edit by hand!\n\n")
   outFile.write('#################################################\n##' + fabric_name + '\n##\n#################################################\n\n')
   outFile.write("## I'm here just to make substitution not break\n")
   outFile.write("FABRICNAME " + fabric_name + "\n" + "TOPOLOGY ctzbrick24q\n")
   outFile.write("MGMT TOR "+ AZ +"-br-ctz-f1mgmt-s"+str(spine_no)+"-r1\n")
   try:
      outFile.write("CAT "+ fabric_name +" CONFER BUILDSTATE "+ turnup_state + "\n\n")
   except:
      pass
   outFile.write("CAT "+ fabric_name +" CONFER FABRICNAME "+ fabric_name + "\n")
   outFile.write("CAT "+ fabric_name +" CONFER OS-VERSION " + os_version + "\n")
   outFile.write("CAT "+ fabric_name +" CONFER FW-VERSION " + fw_version + "\n\n")
   outFile.write("CAT "+ fabric_name + " TEMPLATE ctz-spine.attr\n")
   outFile.write("CAT "+ fabric_name + " TEMPLATE ctz-s" + str(spine_no) +".attr\n")
   outFile.write("CAT "+ AZ +"-br-ctz-f1s" + str(spine_no) +" TIER3 DEFINE WIDTH 16\n")
   outFile.write("CAT "+ fabric_name + " TEMPLATE "+ AZ +"-br-ctz-f1.attr\n\n")
   outFile.write("CAT "+ fabric_name + " CONFER MGMT-MASK /27\n")
   outFile.write("CAT "+ fabric_name + " MGMT MGMT-NET " + str(IPv4Address(spine_subnets[i])) +"/27\n")

   outFile.write("\n## IP address attributes")
   outFile.write("\n# Management IPs Spine Row "+str(spine_no)+ "\n")
   
   ## BGP neighbors / bgp.attr"
   for y in range(2,18):
      var = spine_subnets[i] + y
      outFile.write("CAT "+ fabric_name + " TIER3 r" + str(y-1) + " MANAGEMENTIP " + str(IPv4Address(var))+"\n")
   outFile.write("# Management BGP peer Spine Row "+str(spine_no)+"\n")
   for z in range(2,18):
      var = spine_subnets[i] + y
      outFile.write("CAT "+ fabric_name + " TIER3 r" + str(z-1) + " MGMTPBGPIP " + str(IPv4Address(spine_subnets[i]+1))+"\n")  
   outFile.close()

# The rest of the attributes are for the initial deployment of a catzilla. 
# Only generate the attributes if this is brick set 1 and bricks 1 or 2.
if brick_set_no == 1 and (1 or 2) in brick_range:
    cluster_id = data.cluster_id
    ipv6_subnet = data.ipv6_subnet
    s3_public_subnet = data.s3_public_subnet
    s3_vpc_endpoint = data.s3_vpc_endpoint
    vpc_endpoint_subnet = data.vpc_endpoint_subnet
    try:
      turnup_state = data.turnup_state     
    except:
      pass

# Creating S3 public /46 subnets
    s3_public_44 = IPv6Network(s3_public_subnet+'/44')
    s3_public_46 = list(s3_public_44.Subnet(prefixlen_diff=2))


### COMMENTING OUT CONNECTION TO BR-FAB BECAUSE AS OF 8/16/17 ALL FATCATS SHOULD HAVE BEEN MIGRATED/MIGRATING
##############
### Generates the brickspecific.attr file for brick 1 and outputs the contents in the "out_ctz_attr" directory
##############
#
#    attr_file_name = AZ + "-br-ctz-f1b1-brickspecific.attr"
#    fabric_name = AZ + "-br-ctz-f1b1"
#    path = 'out_ctz_attr/'+fabric_name+'/'
#    outfile = path+ attr_file_name
#    outFile = open(outfile, 'a')
#
#    outFile.write('#################################################\n## Brick specific configurations for\n## '+ AZ +'-br-ctz-f1b1 go in this file\n#################################################\n\n')
#    outFile.write('# This tells modulespec to grab the bgpgroup-ibgp-ctz-br-fab module\n')
#    outFile.write("CAT "+ AZ +"-br-ctz-f1b1 CONFER BRICK-FUNCTION br-fab\n")
#    outFile.close()

#############
## Generates the brickspecific.attr file for brick 2 and outputs the contents in the "out_ctz_attr" directory
#############

    attr_file_name = AZ + "-br-ctz-f1b2-brickspecific.attr"
    fabric_name = AZ + "-br-ctz-f1b2"
    path = 'out_ctz_attr/'+fabric_name+'/'
    outfile = path+ attr_file_name
    outFile = open(outfile, 'a')

    outFile.write('#################################################\n## Brick specific configurations for\n## '+ AZ +'-br-ctz-f1b2 go in this file\n#################################################\n\n')
    outFile.write('# This tells modulespec to grab the bgpgroup-ibgp-ctz-br-agg module\n')
    outFile.write("CAT "+ AZ +"-br-ctz-f1b2 CONFER BRICK-FUNCTION br-agg\n")
    outFile.close()

#############
## Generates the statics.attr file for brick 2 and outputs the contents in the "out_ctz_attr" directory
#############

    attr_file_name = AZ + "-br-ctz-f1b2-statics.attr"
    fabric_name = AZ + "-br-ctz-f1b2"
    path = 'out_ctz_attr/'+fabric_name+'/'
    outfile = path+ attr_file_name
    outFile = open(outfile, 'a')

    outFile.write('# Pull in the IPv4 statics for '+ AZ +'-br-ctz-f1b2\n')
    for i in range (1,17):
        outFile.write("CAT "+ AZ +"-br-ctz-f1b2 TIER2 r"+ str(i) +" TEMPLATE ipv4/" + str(AZ.split()[0][:3]) +"/static-IPV4-"+ AZ.upper() +"-BR-CTZ-F1B2-tiedown.attr\n")
    outFile.write('\n# Pull in the IPv6 statics for '+ AZ +'-br-ctz-f1b2\n')
    for i in range (1,17):
        outFile.write("CAT "+ AZ +"-br-ctz-f1b2 TIER2 r"+ str(i) +" TEMPLATE ipv6/" + str(AZ.split()[0][:3]) +"/static-IPV6-"+ AZ.upper() +"-BR-CTZ-F1B2-tiedown.attr\n")
    outFile.close()

#############
## Generates the br-ctz-f1.attr file for the Catzilla and outputs the contents in the "out_ctz_attr" directory
#############

    attr_file_name = AZ + "-br-ctz-f1.attr"
    path = 'out_ctz_attr/shared/'
    if not os.path.exists(path):
       os.makedirs(path)
    outfile = path+ attr_file_name
    outFile = open(outfile, 'a')

    outFile.write('#################################################\n## Attributes Common to '+ AZ +'-br-ctz-f1\n#################################################\n\n')
    outFile.write('# The number of spine rows each brick connects to.\n')
    outFile.write("CONFER SPINEROWS 8\n\n")
    outFile.write('# The number of bricks each spine row connects to.\n')
    outFile.write("CONFER BRICKS " + str(brick_upper) + "\n\n")
    outFile.write('# CLUSTERID is the /26 assigned to this Catzilla instance.\n')
    outFile.write('# Brick and spine cluster IDs will be auto-generated out of this range.\n')
    outFile.write("CONFER CLUSTERID "+ str(cluster_id) +"/26\n\n")
    outFile.write('# BASEIPV6SLASH64 is taken from infrastructure space for Catzilla IPv6 addressing\n')
    outFile.write("CONFER BASEIPV6SLASH64 "+ str(ipv6_subnet) +"/64\n\n")
    outFile.write('# Catzilla-wide aggregates, automatically split into 32 subnets (one per brick)\n')
    outFile.write('# S3 Public\n')
    outFile.write('CONFER AUTO-AGGREGATES '+ str(s3_public_subnet) +'/44 DESC "S3 Public VIPs"\n')
    outFile.write('CONFER AUTO-AGGREGATES '+ str(s3_public_subnet) +'/44 SPARSE-ASSIGN /46\n')
    outFile.write('CONFER AUTO-AGGREGATES '+ str(s3_public_subnet) +'/44 COMMUNITY 16509:104\n')
    outFile.write('CONFER AUTO-AGGREGATES '+ str(s3_public_subnet) +'/44 COMMUNITY 16509:122\n')
    outFile.write('# S3 VPC Endpoint space\n')
    outFile.write('CONFER AUTO-AGGREGATES '+ str(s3_vpc_endpoint) +'/46 DESC "S3 VPCEndpoint VIPs"\n')
    outFile.write('CONFER AUTO-AGGREGATES '+ str(s3_vpc_endpoint) +'/46 COMMUNITY 16509:104\n')
    outFile.write('CONFER AUTO-AGGREGATES '+ str(s3_vpc_endpoint) +'/46 COMMUNITY 16509:122\n')
    outFile.write('# VPC Endpoint space (non-S3, i.e. for DDB, SQS, etc)\n')
    outFile.write('CONFER AUTO-AGGREGATES '+ str(vpc_endpoint_subnet) +'/46 DESC "VPCEndpoint VIPs non-S3"\n')
    outFile.write('CONFER AUTO-AGGREGATES '+ str(vpc_endpoint_subnet) +'/46 COMMUNITY 16509:104\n')
    outFile.write('CONFER AUTO-AGGREGATES '+ str(vpc_endpoint_subnet) +'/46 COMMUNITY 16509:122\n')
    outFile.close()

#############
## Generates the static tiedown.attr file for the Catzilla and outputs the contents in the "out_ctz_attr" directory
#############

    attr_file_name = "static-IPV6-"+ AZ.upper() +"-BR-CTZ-F1B2-tiedown.attr"
    path = 'out_ctz_attr/shared/ipv6/'+ REGION +'/'
    if not os.path.exists(path):
       os.makedirs(path)
    outfile = path+ attr_file_name
    outFile = open(outfile, 'a')

    outFile.write('# IPv6 static tiedowns for '+ AZ +'-br-ctz-f1b2 (br-agg-r facing brick)\n# The br-agg facing brick typically has the tiedowns for:\n#    * IPv6 S3 Public space for the entire Catzilla (a /44 typically)\n#    * IPv6 S3 VPCEndpoint space for the entire Catzilla (a /46 typically)\n#    * IPv6 VPCEndpoint space (non-S3) for the entire Catzilla (a /46 typically)\n# Background: https://w.amazon.com/index.php/Networking/IS/IPv6_Customer_Assignment_Overview\n\n')
    outFile.write('# S3 Public VIPs\n')
    outFile.write('STATICROUTEV6 '+ str(s3_public_44) +' DESC "S3 public VIPs b2"\n')
    outFile.write('STATICROUTEV6 '+ str(s3_public_44) +' DISCARD b2\n')
    outFile.write('STATICROUTEV6 '+ str(s3_public_44) +' TAG 300 b2\n')
    outFile.write('STATICROUTEV6 '+ str(s3_public_44) +' COMMUNITY 16509:104 b2\n')
    outFile.write('# S3 Public VIPs space, four more-specifics to facilitate Internet TE\n')
    for i in s3_public_46:
        outFile.write('STATICROUTEV6 '+ str(i) +' DESC "S3 public Tiedown TE more-specific b2"\n')
        outFile.write('STATICROUTEV6 '+ str(i) +' DISCARD b2\n')
        outFile.write('STATICROUTEV6 '+ str(i) +' TAG 16509 b2\n')
        outFile.write('STATICROUTEV6 '+ str(i) +' COMMUNITY 16509:154 b2\n')
        outFile.write('STATICROUTEV6 '+ str(i) +' COMMUNITY 16509:104 b2\n')
    outFile.write('\n# S3 VPC Endpoint space\n')
    outFile.write('STATICROUTEV6 '+ str(s3_vpc_endpoint) +'/46 DESC "S3 VPCEndpoint VIPs b2"\n')
    outFile.write('STATICROUTEV6 '+ str(s3_vpc_endpoint) +'/46 DISCARD b2\n')
    outFile.write('STATICROUTEV6 '+ str(s3_vpc_endpoint) +'/46 TAG 300 b2\n')
    outFile.write('STATICROUTEV6 '+ str(s3_vpc_endpoint) +'/46 COMMUNITY 16509:104 b2\n')
    outFile.write('STATICROUTEV6 '+ str(s3_vpc_endpoint) +'/46 COMMUNITY 65139:0 b2\n')
    outFile.write('STATICROUTEV6 '+ str(s3_vpc_endpoint) +'/46 COMMUNITY 65239:0 b2\n')
    outFile.write('STATICROUTEV6 '+ str(s3_vpc_endpoint) +'/46 COMMUNITY 65030:0 b2\n\n')
    outFile.write('# VPC Endpoint space (non-S3, i.e. for DDB, SQS, etc)\n')
    outFile.write('# The first fatcat gets the first /51 out of the /46 assigned to the NZ for this purpose\n')
    outFile.write('STATICROUTEV6 '+ str(vpc_endpoint_subnet) +'/46 DESC "VPCEndpoint VIPs non-S3" b2\n')
    outFile.write('STATICROUTEV6 '+ str(vpc_endpoint_subnet) +'/46 DISCARD b2\n')
    outFile.write('STATICROUTEV6 '+ str(vpc_endpoint_subnet) +'/46 TAG 300 b2\n')
    outFile.write('STATICROUTEV6 '+ str(vpc_endpoint_subnet) +'/46 COMMUNITY 16509:104 b2\n')
    outFile.write('STATICROUTEV6 '+ str(vpc_endpoint_subnet) +'/46 COMMUNITY 65139:0 b2\n')
    outFile.write('STATICROUTEV6 '+ str(vpc_endpoint_subnet) +'/46 COMMUNITY 65239:0 b2\n')
    outFile.write('STATICROUTEV6 '+ str(vpc_endpoint_subnet) +'/46 COMMUNITY 65030:0 b2\n\n')
    outFile.close()

    attr_file_name = "static-IPV4-"+ AZ.upper() +"-BR-CTZ-F1B2-tiedown.attr"
    path = 'out_ctz_attr/shared/ipv4/'+ REGION +'/'
    if not os.path.exists(path):
       os.makedirs(path)
    outfile = path+ attr_file_name
    outFile = open(outfile, 'a')
    outFile.write('# File auto-generated by s3_nz_aggregates_tiedowns.py\n')
    outFile.write('# Do NOT edit by hand!\n')
    outFile.write('# https://w.amazon.com/bin/view/Networking/Edge/AUTO_S3_NZ_AGGREGATES\n')
    outFile.close()

#############
## Generates the prefixlist VIPS.attr file for the Catzilla and outputs the contents in the "out_ctz_attr" directory
#############

    attr_file_name = "prefixlist-IPV6-"+ AZ.upper() +"-BR-CTZ-F1-VIPS.attr"
    path = 'out_ctz_attr/shared/ipv6/'+ REGION +'/'
    if not os.path.exists(path):
       os.makedirs(path)
    outfile = path+ attr_file_name
    outFile = open(outfile, 'a')

    outFile.write('# IPv6 prefixlists for '+ AZ +'-br-ctz-f1\n')
    outFile.write('# S3 Public VIPs\n')
    outFile.write('PREFIXLIST IPV6-S3-PUBLIC-'+ AZ.upper() +'-BR-CTZ-F1-VIPS '+ str(s3_public_subnet) +'/44\n\n')
    outFile.write('# S3 VPC Endpoint VIPs\n')
    outFile.write('PREFIXLIST IPV6-S3-VPCENDPOINT-'+ AZ.upper() +'-BR-CTZ-F1-VIPS '+ str(s3_vpc_endpoint) +'/46\n\n')
    outFile.write('# VPC Endpoint VIPs (non-S3, i.e. for DDB, SQS, etc)\n')
    outFile.write('PREFIXLIST IPV6-VPCENDPOINT-'+ AZ.upper() +'-BR-CTZ-F1-VIPS '+ str(vpc_endpoint_subnet) +'/46\n')

#############
## Cleaning up
## 1. Copies specified bricks to GenevaBuilderDCEdge/targetspec/border/<brick_dir>
## 2. Removes output dir
## 3. Prints var file to screen
#############

path = 'out_ctz_attr/'

print '\nAll attributes file have been successfully generated and exported in this folder:\n' + os.getcwd() + "/" + path +"\n"

log.set_verbosity(log.INFO)
log.set_verbosity(log.INFO)

# Update CONFER BRICKS attribute with number of bricks
br_ctz_f1_attr = '../../../targetspec/border/shared/' + AZ + '-br-ctz-f1.attr'
if os.path.isfile(br_ctz_f1_attr) == False:
    file_util.copy_file(path + 'shared/' + AZ + '-br-ctz-f1.attr', br_ctz_f1_attr, verbose=1)
else:
    with open(br_ctz_f1_attr) as text, open('./tempfile', 'w') as new_text:
        print "Updating CONFER BRICKS in " + br_ctz_f1_attr
        new_text.write(''.join("CONFER BRICKS " + str(brick_upper) + "\n" if line.startswith("CONFER BRICKS") else line
                       for line in text))
    shutil.copy('./tempfile', br_ctz_f1_attr)
    os.remove('./tempfile')

# Check if shared files already exist. If they do, don't overwrite them
if os.path.isfile('../../../targetspec/border/shared/ipv4/' + REGION + '/static-IPV4-' + AZ.upper() + '-BR-CTZ-F1B2-tiedown.attr') == False:
    file_util.copy_file(path + 'shared/ipv4/' + REGION + '/static-IPV4-' + AZ.upper() + '-BR-CTZ-F1B2-tiedown.attr', '../../../targetspec/border/shared/ipv4/' + REGION + '/static-IPV4-' + AZ.upper() + '-BR-CTZ-F1B2-tiedown.attr', verbose=1)
else:
    print '../../../targetspec/border/shared/ipv4/' + REGION + '/static-IPV4-' + AZ.upper() + '-BR-CTZ-F1B2-tiedown.attr already exists. Skipping copy!'

if os.path.isfile('../../../targetspec/border/shared/ipv6/' + REGION + '/prefixlist-IPV6-' + AZ.upper() + '-BR-CTZ-F1-VIPS.attr') == False:
    file_util.copy_file(path + 'shared/ipv6/' + REGION + '/prefixlist-IPV6-' + AZ.upper() + '-BR-CTZ-F1-VIPS.attr', '../../../targetspec/border/shared/ipv6/' + REGION + '/prefixlist-IPV6-' + AZ.upper() + '-BR-CTZ-F1-VIPS.attr', verbose=1)
else:
    print '../../../targetspec/border/shared/ipv6/' + REGION + '/prefixlist-IPV6-' + AZ.upper() + '-BR-CTZ-F1-VIPS.attr already exists. Skipping copy!'

if os.path.isfile('../../../targetspec/border/shared/ipv6/' + REGION + '/static-IPV6-' + AZ.upper() + '-BR-CTZ-F1B2-tiedown.attr') == False:
    file_util.copy_file(path + 'shared/ipv6/' + REGION + '/static-IPV6-' + AZ.upper() + '-BR-CTZ-F1B2-tiedown.attr', '../../../targetspec/border/shared/ipv6/' + REGION + '/static-IPV6-' + AZ.upper() + '-BR-CTZ-F1B2-tiedown.attr', verbose=1)
else:
    print '../../../targetspec/border/shared/ipv6/' + REGION + '/static-IPV6-' + AZ.upper() + '-BR-CTZ-F1B2-tiedown.attr already exists. Skipping copy!'

for b in range(brick_lower,brick_upper+1):
    source_dir = path + AZ + "-br-ctz-f1b" + str(b)
    dir_util.copy_tree(source_dir, '../../../targetspec/border/' + AZ + '-br-ctz-f1b' + str(b) + '/', verbose=1)

# check if spine rows already exist. If they do, don't overwrite them.
for s in range(1,9):
    source_dir = path + AZ + "-br-ctz-f1s" + str(s)
    if os.path.isfile('../../../targetspec/border/' + AZ + '-br-ctz-f1s' + str(s) + '/' + AZ + '-br-ctz-f1s' + str(s) + '-fabric.attr') == False:
        dir_util.copy_tree(source_dir, '../../../targetspec/border/' + AZ + '-br-ctz-f1s' + str(s) + '/', verbose=1)
    else:
        print '../../../targetspec/border/' + AZ + '-br-ctz-f1s' + str(s) + '/' + AZ + '-br-ctz-f1s' + str(s) + '-fabric.attr already exists. Skipping copy!'

dir_util.remove_tree(path)

print('\n\n=== Var file output for reference: ===\n======================================\n')

with open(var_file) as f:
    print f.read()
