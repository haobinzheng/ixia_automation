#!/apollo/bin/env -e NEPython python

import argparse
import sys

from nms_ndc.credentials.odin import MappedOdinCredentialProvider
from nms_ndc.connector import DeviceConnector
from nms_ndom import operations

from nms_ndom.registry import MultiRegistry
registry = MultiRegistry()

from nms_basicops import registry as nms_basicops_registry
registry.add_registry(nms_basicops_registry)

from neteng_operations import registry as neteng_operations_registry
registry.add_registry(neteng_operations_registry)

#from nms_neighbors import registry as nms_neighbors_registry
#registry.add_registry(nms_neighbors_registry)

from neteng_operations.port_channel import PortChannel, PortChannelMember
from neteng_operations.neighbors import LLDPNeighbor


MATERIALSET_CLI = "com.amazon.networking.managed.prod.tacacs-user.neteng-auto-ro"
#MATERIALSET_SNMP = "com.amazon.networking.managed.prod.snmp.border.netmgmt"
MATERIALSET_SNMP = "com.amazon.networking.managed.prod.snmp.default"

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--device", help = "Device hostname or IP address", required = True)
parser.add_argument("-l", "--lags", help = "Space-separated list of LAGs on which to operate. Use 'all' to operate on all LAGs.", required = True, nargs = "+")
args = parser.parse_args()

device = args.device

lags = set()
interfaces = set()

class Neighbor(object):
    def __init__(self, name = "NO_NEIGHBOR_DATA", interface = "NO_NEIGHBOR_INTERFACE_DATA"):
        self.name = name
        self.interface = interface
    def __hash__(self):
        return self.name
    def __cmp__(self, other):
        if str(self) > str(other):
            return 1
        elif str(self) < str(other):
            return -1
        else:
            return 0
    def __eq__(self, other):
        return str(self) == str(other)
    def __ne__(self, other):
        return str(self) == str(other)
    def __repr__(self):
        return " ".join([self.name, self.interface])

class Interface(object):
    def __init__(self, name, status = "up", neighbor = Neighbor()):
        self.name = name
        self.status = status.lower()
        self.neighbor = neighbor
    def is_up(self):
        return self.status.lower() == "up"
    def __hash__(self):
        value = long(self.name.encode("hex"), 16) + long(self.status.encode("hex"), 16) + long(str(self.neighbor).encode("hex"), 16)
        return value
    def __cmp__(self, other):
        if str(self) > str(other):
            return 1
        elif str(self) < str(other):
            return -1
        else:
            return 0
    def __eq__(self, other):
        return str(self) == str(other)
    def __ne__(self, other):
        return str(self) == str(other)
    def __repr__(self):
        return " ".join([self.name, self.status, str(self.neighbor)])

class LAG(object):
    def __init__(self, name, members = set()):
        self.name = name
        self.members = members
    def add_interface(self, interface):
        self.members.add(interface) 
    def remove_interface(self, interface):
        self.members.remove(interface)
    def has_interface(self, interface):
        return interface in self.members
    def __hash__(self):
        value = long(self.name.encode("hex"), 16) + long(str(self.members).encode("hex"), 16)
        return value
    def __cmp__(self, other):
        if str(self) > str(other):
            return 1
        elif str(self) < str(other):
            return -1
        else:
            return 0
    def __eq__(self, other):
        return str(self) == str(other)
    def __ne__(self, other):
        return str(self) == str(other)
    def __repr__(self):
        return self.name + ": " + " ".join(str(self.members))

def connect(device, materials = {'cli': MATERIALSET_CLI, 'snmp': MATERIALSET_SNMP}):
    cred_provider = MappedOdinCredentialProvider(materials)
    connector = DeviceConnector.for_device(device, credential_provider = cred_provider)
    return connector

def do_operations(device, materials = {'cli': MATERIALSET_CLI, 'snmp': MATERIALSET_SNMP}):
    cred_provider = MappedOdinCredentialProvider(materials)
    ops = operations.for_device(device, credential_provider = cred_provider, registry = registry)
    return ops

def is_valid_interface_name(interface):
    valid_names = ['ge-', 'xe-', 'et-', 'Te', 'Gi']
    for name in valid_names:
        if name in interface:
            return True
    return False

def is_number(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

def parse_lag_list(lags):
    """Parse and organize a list of PortChannel objects that contain a list of PortChannelMember objects.
    Sample input data:
    [PortChannel(name='ae1', status=None, protocol='LACP', members=[PortChannelMember(name='xe-2/0/0', status='up'), PortChannelMember(name='xe-2/1/0', status='up'), PortChannelMember(name='xe-2/2/0', status='up'), PortChannelMember(name='xe-2/3/0', status='up')])
    PortChannel(name='ae2', status=None, protocol='LACP', members=[PortChannelMember(name='xe-0/2/1', status='down'), PortChannelMember(name='xe-0/3/1', status='down'), PortChannelMember(name='xe-0/1/1', status='down'), PortChannelMember(name='xe-0/0/2', status='down')])]
    """
    out_lags = set()
    for lag in lags:
        members = set()
        for interface in lag.members:
            members.add(Interface(name = interface.name, status = interface.status))
        out_lags.add(LAG(name = lag.name, members = members))
    return out_lags

def parse_interface_list(interfaces):
    """Parse and organize a list of LLDPNeighbor objects.
    Sample input data:
    [LLDPNeighbor(local_port_id='xe-1/2/1', chassis_id='00:1b:21:a4:6d:20', port_id='00:1b:21:a4:6d:20', port_description=None, system_name='dub2-es-svc-n113', system_description=None)
    LLDPNeighbor(local_port_id='xe-2/2/1', chassis_id='00:1b:21:a4:6f:6c', port_id='00:1b:21:a4:6f:6c', port_description=None, system_name='dub2-es-svc-n115', system_description=None)]
    """
    out_interfaces = set()
    for interface in interfaces:
        if not interface.port_id == None:
            remote_port = interface.port_id
        elif not interface.port_description == None :
            remote_port = interface.port_description
        else:
            remote_port = "NO_NEIGHBOR_INTERFACE_DATA"
        out_interfaces.add(Interface(
            name = interface.local_port_id, 
            neighbor = Neighbor(name = interface.system_name, interface = remote_port)
        ))
    return out_interfaces

def validate_interface_data(interface):
    if is_valid_interface_name(interface.neighbor.interface):
        pass
    elif is_number(interface.neighbor.interface) and ("-br-" in interface.neighbor.name or "-vc-" in interface.neighbor.name):
        print "No remote interface found for local interface %s to neighbor %s. Probing remote end... " % (interface.name, interface.neighbor.name),
        try:
            connect_neighbor = connect(interface.neighbor.name)
            connection = connect_neighbor.get_connection('cli')
            output = connection.run_command('show interfaces snmp-index ' + interface.neighbor.interface + ' terse | except Interface')
            interface.neighbor.interface = output.split(" ")[0].split(".")[0]
            print "Found %s." % interface.neighbor.interface
        except:
            interface.neighbor.interface = "NO_NEIGHBOR_INTERFACE_DATA"
            print "Could not determine remote interface."
    else:
        interface.neighbor.interface = "NO_NEIGHBOR_INTERFACE_DATA"
    return interface

ops = do_operations(device)

device_lags_raw = ops.do_get_port_channels()
device_neighbors_raw = ops.do_get_lldp_neighbors()

lags = parse_lag_list(device_lags_raw)
interfaces = parse_interface_list(device_neighbors_raw)

# Only work on the LAGs mentioned in the command line arguments
if not args.lags == "all":
    lags = {lag for lag in lags if lag.name in args.lags}

# Update LAG members with neighbor information
for lag in lags:
    for member in lag.members:
        for interface in interfaces:
            if member.name == interface.name:
                interface = validate_interface_data(interface)
                member.neighbor = interface.neighbor

print "\n\n"

for lag in sorted(lags):
    for member in sorted(lag.members):
        print "LAG " + lag.name + " MEMBER " + member.name + " REMPORT " + member.neighbor.interface
    print "\n"
