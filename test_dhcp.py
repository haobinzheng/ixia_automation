from pprint import pprint
import os
import sys
import time
from datetime import datetime
#ixNetPath = r'C:\Program Files (x86)\Ixia\IxNetwork\7.30-GA\API\Python'
#sys.path.append(ixNetPath)
from IxNetwork import IxNet
ixNet = IxNet()
starttime=str(datetime.now())
ixNet.connect('10.105.241.234', '-port', 8009, '-version', '8.50')
root = ixNet.getRoot()
#Retrieves all topologies in the config
topologies = ixNet.getList(root, 'topology')
#Iterating over each topology
device_count = 0
for each_topology in topologies:
    #Retrieving topology name so that DHCP server name can be excluded
    topology_name = ixNet.getAttribute(each_topology, '-name')
    print "Executing for topology %s." %topology_name
    #Execute the below code except for DHCP server topology
    if topology_name != 'N56-55-FEX103-104-EVPC':
        print topology_name
        #Retreiving the device groups in each topology
        device_groups = ixNet.getList(each_topology, 'deviceGroup')
        #Iterating over each device group in the topology
        for each_devicegroup in device_groups:
            devicegroup_name = ixNet.getAttribute(each_devicegroup, '-name')
            print "Executing for devicegroup %s." %devicegroup_name
            #Retrieving the handle for dhcpv4_client and dhcpv6_client
            #this is required to start dhcpv6 client first before starting dhcpv4 client
            dhcpv4_client = ixNet.getList(each_devicegroup + ('/ethernet:1'),'dhcpv4client')
            dhcpv6_client = ixNet.getList(each_devicegroup + ('/ethernet:1'),'dhcpv6client')
            if len(dhcpv6_client) > 0:
                print "STARTING DHCPV6 CLIENT FOR %s."%devicegroup_name
                count=int(ixNet.getAttribute(each_devicegroup, '-multiplier'))
                print count
                ixNet.execute('start', dhcpv6_client)
                if count <=10 :
                    print "sleeping for 10 seconds"
                    time.sleep(10)
                elif count <=50 :
                    print "sleeping for 10 seconds"
                    time.sleep(10)
                elif count <=100 :
                    print "sleeping for 20 seconds"
                    time.sleep(20)
            if len(dhcpv4_client) > 0:
                print "STARTING DHCPV4 CLIENT FOR %s."%devicegroup_name
                count=int(ixNet.getAttribute(each_devicegroup, '-multiplier'))
                print count
                ixNet.execute('start', dhcpv4_client)
                if count <=10 :
                    print "sleeping for 10 seconds"
                    time.sleep(10)
                elif count <=50 :
                    print "sleeping for 20 seconds"
                    time.sleep(20)
                elif count <=100 :
                    print "sleeping for 60 seconds"
                    time.sleep(60)
            #when a device-group has either static ipv4/ipv6 or ethernet only then dhcpv4_client and dhcpv6_client returns an empty list
            if len(dhcpv6_client) == 0:
                print "Starting IPv4,IPv6 and Ethernet clients for %s"%devicegroup_name
                ixNet.execute('start',each_devicegroup)
                print "Sleeping for 5 seconds"
                time.sleep(5)
#print "Total number of devices is {0}".format(device_count)
endtime=str(datetime.now())
print "program started at {0}".format(starttime)
print "program ended at {0}".format(endtime)
print "Ixia program completed"
ixNet.disconnect()