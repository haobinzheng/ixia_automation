#!/apollo/bin/env -e NEPython python

# On Neteng-Bastion execute using the NEPython environment. On console bastions execute using the NSSTools environment.
#!/apollo/bin/env -e NEPython python
#!/apollo/bin/env -e NSSTools python 

# This script assumes the routers return valid interface names via LLDP. Make sure the following option is enabled on the routers:
# set protocols lldp port-id-subtype interface-name

import argparse
import sys
import os
import logging
import getpass
import re
import requests
import json

from subprocess import Popen, PIPE, call
from collections import namedtuple
from contextlib import closing
from csv import DictReader, reader

from nms_ndc.credentials.odin import MappedOdinCredentialProvider
from nms_ndc.credentials.base import SimpleCredentialProvider, CredentialPair
from nms_ndc.credentials.multi import MultiCredentialProvider
from nms_ndc.connector import DeviceConnector
from nms_ndc.common import AuthenticationFailure, CannotConnect, NotConnected


# Shamelessly borrowed from rafaelo's cutsheet.py
f_verbose = 1

############################################################
## Some output handling
############################################################
def say(msg, level=1):
    global f_verbose
    if (level <= f_verbose):
        print msg

############################################################
## Die pleasantly
############################################################
def euthanize(msg):
    print "ERROR: %s" % (msg)
    sys.exit(1)

############################################################
## Open the CSV file and load into a list
############################################################
def load_csv(cfile):
    lines = []
    cparts = []
    skipped = 0

    # Make the LAG field optional
    #columns = ['a_hostname', 'a_lag', 'a_interface', 'z_hostname', 'z_lag', 'z_interface']
    columns = ['a_hostname', 'a_interface', 'z_hostname', 'z_interface']

    say("Loading cutsheet from %s." % (cfile))

    try:
        CSHEET = open(cfile, "rb")
        try:
            headers = reader(CSHEET).next()
            rdr = DictReader(CSHEET, headers)

            for col in columns:
                if (not col in rdr.fieldnames):
                    CSHEET.close()
                    euthanize("Could not locate field %s in cutsheet." % (col))
                else:
                    say("Found %s in column %d" % (col, rdr.fieldnames.index(col)), 5)

            for row in rdr:
                #line = line.strip()

                # Make the LAG field optional
                #parts = [ row['a_hostname'], row['a_lag'], row['a_interface'], row['z_interface'], row['z_lag'], row['z_hostname'] ]
                parts = [ row['a_hostname'], row['a_interface'], row['z_interface'], row['z_hostname'] ]
                parts = [p.strip() for p in parts]

                if ("" in parts):
                    say("Skipping line: %s" % (",".join(parts)),5)
                    skipped += 1
                    continue

                lines.append(parts)
        finally:
            CSHEET.close()
    except IOError, e:
        euthanize("Failed to open %s.\n%s" % (cfile, e))

    say("Cutsheet loaded: %d rows - %d rows skipped" % (len(lines), skipped), 2)

    return lines


#Neighbor = namedtuple('Neighbor', ['name', 'interface'])
#Interface = namedtuple('Interface', ['status', 'optical_level', 'neighbor'])
#Console = namedtuple('Console', ['address', 'port'])
#Device = namedtuple('Device', ['interfaces', 'console'])

class Neighbor(object):
    __slots__ = ('name', 'interface')
    def __init__(self, name='', interface=''):
        self.name = name
        self.interface = interface
    def __repr__(self):
        return '{0.__class__.__name__}(name={0.name!r}, interface={0.interface!r})'.format(self)

class Interface(object):
    __slots__ = ('up', 'optical_level', 'neighbor')
    def __init__(self, up=False, optical_level='', neighbor=Neighbor()):
        self.up = up
        self.optical_level = optical_level
        self.neighbor = neighbor
    def __repr__(self):
        return '{0.__class__.__name__}(up={0,up!r}, optical_level={0.optical_level!r}, neighbor={0.neighbor!r})'.format(self)

class Console(object):
    __slots__ = ('address', 'port')
    def __init__(self, address='', port=''):
        self.address = address
        self.port = port
    def __repr__(self):
        return '{0.__class__.__name__}(address={0.address!r}, port={0.port!r})'.format(self)

class Device(object):
    __slots__ = ('interfaces', 'console', 'polled')
    def __init__(self, interfaces={}, console=Console(), polled=False):
        self.interfaces = interfaces
        self.console = console
        self.polled = polled
    def __repr__(self):
        return '{0.__class__.__name__}(interfaces={0.interfaces!r}, console={0.console!r}, polled={0.polled!r})'.format(self)

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--csv", help="Cutsheet in CSV format", required=True)
parser.add_argument("--low", help="Optical low threshold (default = -6 dBm)", default="-6")
parser.add_argument("--high", help="Optical high threshold (default = 0 dBm)", default="0")
parser.add_argument("--log", help="Logging level (default = WARNING)", default="WARNING")
parser.add_argument("--no-local-credentials", help="Use only your own credentials for all logins", action='store_true', default=False)
parser.add_argument("--all-credentials", help="Use all built-in credentials; useful for weird console logins", action='store_true', default=False)
parser.add_argument("--additional-credentials", help="Prompt for additional credentials to use", action='store_true', default=False)
args = parser.parse_args()
csv_file = args.csv
optical_low = args.low
optical_high = args.high
loglevel = args.log
logfile = os.path.expanduser("~") + "/" + os.path.basename(__file__) + ".log"

logging.basicConfig(filename=logfile, level=loglevel.upper())

no_local_credentials = args.no_local_credentials
all_credentials = args.all_credentials
additional_credentials = args.additional_credentials

# Commenting for now because it seems this is not needed.
#def has_kerberos_ticket():
#    return True if call(['klist', '-s']) == 0 else False
#
#if not has_kerberos_ticket():
#    euthanize('You need a valid Kerberos ticket! Do "kinit -f" once before running this script.')

if no_local_credentials and all_credentials:
    euthanize("The --no-local-credentials and --all-credentials options are mutually exclusive.")

MATERIALSET_CLI_NETENG = "com.amazon.networking.managed.prod.local-user.neteng"
MATERIALSET_CLI_ENABLE = "com.amazon.networking.managed.prod.local-user.enable"
MATERIALSET_CLI_DATATECH = "com.amazon.networking.managed.prod.local-user.datatech"
MATERIALSET_CONSOLE_NETENG = "com.amazon.networking.managed.prod.console.neteng"
MATERIALSET_CONSOLE_ENABLE = "com.amazon.networking.managed.prod.console.enable"
MATERIALSET_CONSOLE_DATATECH = "com.amazon.networking.managed.prod.console.datatech"
MATERIALSET_SNMP = "com.amazon.networking.managed.prod.snmp.default"

username = raw_input("Your username [{}]: ".format(getpass.getuser()))
if username == "":
    username = getpass.getuser()
password = getpass.getpass("Your password: ")

if additional_credentials:
    additional_username = ""
    while additional_username == "":
        additional_username = raw_input("Additional username: ")
    additional_password = getpass.getpass("Additional password: ")

def get_device_connector(username, password, device_hostname, console_address, console_port):
    providers = []
    providers.append(SimpleCredentialProvider(console = [CredentialPair(username, password)]))
    providers.append(SimpleCredentialProvider(cli = [CredentialPair(username, password)]))
    
    if additional_credentials:
        providers.append(SimpleCredentialProvider(console = [CredentialPair(additional_username, additional_password)]))
        providers.append(SimpleCredentialProvider(cli = [CredentialPair(additional_username, additional_password)]))
    if not no_local_credentials:
        providers.append(MappedOdinCredentialProvider({'console': MATERIALSET_CONSOLE_NETENG}))
        providers.append(MappedOdinCredentialProvider({'cli': MATERIALSET_CLI_NETENG}))
    if not no_local_credentials and all_credentials:
        providers.append(MappedOdinCredentialProvider({'console': MATERIALSET_CONSOLE_ENABLE}))
        providers.append(MappedOdinCredentialProvider({'console': MATERIALSET_CONSOLE_DATATECH}))
        providers.append(MappedOdinCredentialProvider({'console': MATERIALSET_CLI_NETENG}))
        providers.append(MappedOdinCredentialProvider({'cli': MATERIALSET_CLI_ENABLE}))
        providers.append(MappedOdinCredentialProvider({'cli': MATERIALSET_CLI_DATATECH}))
        providers.append(MappedOdinCredentialProvider({'cli': MATERIALSET_CONSOLE_NETENG}))

    providers.append(MappedOdinCredentialProvider({'snmp': MATERIALSET_SNMP}))

    cred_provider = MultiCredentialProvider(*providers)

    connector = DeviceConnector.for_device_console(
        console_address = console_address,
        console_port = console_port,
        device_hostname = device_hostname,
        platform_family = 'junos',
        credential_provider = cred_provider,
        disabled_transport_type = ['native-ssh', 'ssh'],
        #disabled_connections = ['native-ssh', 'ssh'],
    )
    return connector

# Function shamelessly borrwed from:
# https://code.amazon.com/packages/NetengAutoChecks/blobs/mainline/--/lib/autochecks_utils/services.py
def get_consoledb_information(device):
    """ Get the information stored at https://network-console.amazon.com about the target

    It will send a GET request for the given target device.

    Returns:
        a dictionary with all the keys and values returned in the GET response
    """

    network_console_url = "https://network-console.amazon.com/console-port-db/readonly-api.cgi"
    console_db_link = "{}?method=search&keywords={}".format(network_console_url, device)

    session = requests.Session()
    try:
        response = session.get(console_db_link, verify=False)
    except Exception:
        #return None
        euthanize("Could not find console information for %s." % device)

    response = json.loads(response.text)
    if not response:
        #return None
        euthanize("Could not find console information for %s." % device)

    for entry in response:
        if entry['Host_Name'].lower() == device.lower():
            console_address = str(entry['Server_Name'])
            console_port = str(entry['Server_Port'])
            return Console(address=console_address, port=console_port)

    # No matching device found in ConsoleDB
    euthanize("Could not find console information for %s." % device)

    #console_info = {
    #    str(key): str(value)
    #    for key, value in response[0].items()
    #}
    #
    #return console_info

def get_blank_interface():
    interface = Interface(
        up = False,
        optical_level="",
        neighbor=Neighbor(
            name="",
            interface="",
        )
    )
    return interface

def populate_device_fields(dev_connector, device_name, device_fields):
    with closing(dev_connector.get_connection('cli')) as conn:
        say("Successfully connected to %s." % (device_name))

        # Check if "set protocols lldp port-id-subtype interface-name" is enabled,
        # as this is a requirement to get the needed LLDP information
        command_lldp_enabled = 'show configuration | display set | grep "set protocols lldp port-id-subtype interface-name"'
        output_lldp_enabled = conn.run_command(command_lldp_enabled)
        lldp_enabled_regex = r'set protocols lldp port-id-subtype interface-name'
        lldp_enabled_match = re.search(lldp_enabled_regex, output_lldp_enabled)
        if not lldp_enabled_match:
            say('LLDP "set protocols lldp port-id-subtype interface-name" not enabled. Skipping LLDP checks for %s.' % (device_name))

        for interface_name, interface_fields in device_fields.interfaces.iteritems():
            command_status = 'show interfaces ' + interface_name + ' | grep Physical'
            command_optical_level = 'show interfaces diagnostics optics ' + interface_name + ' | grep "Receiver signal average optical power"'
            command_lldp = 'show lldp neighbors interface ' + interface_name + ' | grep "^Port ID|^System name"'

            output_status = conn.run_command(command_status)
            output_optical_level = conn.run_command(command_optical_level)
            output_lldp = conn.run_command(command_lldp)

            # Parse interface status
            # Examples of output:
            #output_status = """Physical interface: xe-1/0/0, Enabled, Physical link is Up"""
            #output_status = """Physical interface: xe-7/0/0, Administratively down, Physical link is Down"""
            status_regex = r'Physical interface: (ge|xe|et)-.+, (Enabled|Administratively down), Physical link is (Up|Down)'
            status_match = re.search(status_regex, output_status)
            if status_match == None:
                status = ""
            else:
                status = status_match.group(3)

            if (status.lower() == 'up'):
                up = True
            else:
                up = False

            # Parse optical level
            # Examples of output:
            #output_optical_level = """    Receiver signal average optical power     :  0.5475 mW / -2.62 dBm"""
            #output_optical_level = """    Receiver signal average optical power     :  0.0002 mW / -36.99 dBm"""
            #output_optical_level = """    Receiver signal average optical power     :  0.0001 mW / -40.00 dBm"""
            #output_optical_level = """    Receiver signal average optical power     :  0.0000 mW / - Inf dBm"""
            #output_optical_level = """    Receiver signal average optical power     :  1.0695 mW / 0.29 dBm"""
            optical_level_regex = r'\s*Receiver signal average optical power\s*:.* mW \/ (.*) dBm'
            optical_level_match = re.search(optical_level_regex, output_optical_level)
            if optical_level_match == None or optical_level_match.group(1) == "- Inf":
                optical_level = "n/a"
            else:
                optical_level = optical_level_match.group(1)

            if lldp_enabled_match:
                # Parse LLDP
                # Examples of output:
#                output_lldp = \
#"""Port ID            : xe-1/0/0
#System name        : dub2-br-agg-r2"""
                #output_lldp = """"""

                # If LLDP output is not a format we expect
                if output_lldp == "" or output_lldp == "\n" or len(output_lldp.splitlines()) < 2:
                    lldp_neighbor_name = ""
                    lldp_neighbor_interface = ""
                else:
                    output_lldp_interface = output_lldp.splitlines()[0]
                    lldp_interface_regex = r'Port ID\s*: ((ge|xe|et)-.+)'
                    lldp_interface_match = re.search(lldp_interface_regex, output_lldp_interface)
                    if lldp_interface_match == None:
                        lldp_neighbor_interface = ""
                    else:
                        lldp_neighbor_interface = lldp_interface_match.group(1)

                    output_lldp_name = output_lldp.splitlines()[1]
                    lldp_name_regex = r'System name\s*: (.*)'
                    lldp_name_match = re.search(lldp_name_regex, output_lldp_name)
                    if lldp_name_match == None:
                        lldp_neighbor_name = ""
                    else:
                        lldp_neighbor_name = lldp_name_match.group(1)
            else:
                lldp_neighbor_name = ""
                lldp_neighbor_interface = ""

            interface_fields.up = up
            interface_fields.optical_level = optical_level
            interface_fields.neighbor.name = lldp_neighbor_name
            interface_fields.neighbor.interface = lldp_neighbor_interface

        # At this point we've successfully polled the device
        device_fields.polled = True


def connect_console(device_name, device_fields):
    say("Connecting to %s via %s:%s." % (device_name, device_fields.console.address, device_fields.console.port))

    dev_connector = get_device_connector(
        username = username,
        password = password,
        device_hostname = device_name,
        console_address = device_fields.console.address,
        # Work-around for weird NDCL console handling where reverse SSH port needs to be specified as the last 3 digits
        # (e.g. 23 for port 2023), whereas Telnet port needs to be specified in full (e.g. 2023)
        console_port = device_fields.console.port[1:],
    )

    try:
        populate_device_fields(dev_connector, device_name, device_fields)

    except CannotConnect as e:

        dev_connector = get_device_connector(
            username = username,
            password = password,
            device_hostname = device_name,
            console_address = device_fields.console.address,
            console_port = device_fields.console.port,
        )

        try:
            populate_device_fields(dev_connector, device_name, device_fields)
 
        except CannotConnect as e:
            message = "Failed to connect to %s via console.\n%s" % (device_name, e)
            logging.warning(message)
            say("WARNING: " + message)
            #euthanize(message)

        except AuthenticationFailure as e:
            message = "Authentication failure when trying to connect to %s via console.\n%s" % (device_name, e)
            logging.warning(message)
            say("WARNING: " + message)
            #euthanize(message)

    except AuthenticationFailure as e:
        message = "Authentication failure when trying to connect to %s via console.\n%s" % (device_name, e)
        logging.warning(message)
        say("WARNING: " + message)
        #euthanize(message)


def get_device_list(csv_contents):
    devices = {}

    for line in csv_contents:
        a_device = line[0]
        a_interface = line[1]
        z_device = line[3]
        z_interface = line[2]
        
        for (device, interface) in [(a_device, a_interface), (z_device, z_interface)]:
            if device not in devices.iterkeys():
                console = get_consoledb_information(device)
                interfaces = {interface: get_blank_interface()}
                devices[device] = Device(interfaces=interfaces, console=console, polled=False)
            elif interface not in devices[device].interfaces.iterkeys():
                devices[device].interfaces[interface] = get_blank_interface()
            # We already have this device and interface!
            else:
                euthanize("Duplicate interface found: %s %s!" % (device, interface))

    say("Successfully loaded devices from cutsheet %s." % csv_file)
    say("Attempting to extract interface information.")

    for device_name, device_fields in sorted(devices.iteritems()):
        connect_console(device_name, device_fields)

    return devices

def check_links(csv_contents, devices):
    for line in csv_contents:
        a_device = line[0]
        a_interface = line[1]
        z_device = line[3]
        z_interface = line[2]

        a_polled = devices[a_device].polled
        a_up = devices[a_device].interfaces[a_interface].up
        a_optical_level = devices[a_device].interfaces[a_interface].optical_level
        a_neighbor_name = devices[a_device].interfaces[a_interface].neighbor.name
        a_neighbor_interface = devices[a_device].interfaces[a_interface].neighbor.interface

        z_polled = devices[z_device].polled
        z_up = devices[z_device].interfaces[z_interface].up
        z_optical_level = devices[z_device].interfaces[z_interface].optical_level
        z_neighbor_name = devices[z_device].interfaces[z_interface].neighbor.name
        z_neighbor_interface = devices[z_device].interfaces[z_interface].neighbor.interface

        fail = False
        status = ""
        
        if a_polled:
            # Validate a_device interface status
            if (not a_up): 
                fail = True
                status += "lhs DOWN "
            else:
                status += "lhs UP "

            # Validate a_device interface optical level
            if a_optical_level.lower() == "n/a":
                fail = True
            elif float(optical_low) >= float(a_optical_level) or float(a_optical_level) >= float(optical_high):
                fail = True
            status += a_optical_level + " dBm "
        else:
            fail = True
            status += "A device not polled "

        status += "<--> "
        
        if z_polled:
            # Validate z_device interface status
            if (not z_up): 
                fail = True
                status += "rhs DOWN "
            else:
                status += "rhs UP "

            # Validate z_device interface optical level
            if z_optical_level.lower() == "n/a":
                fail = True
            elif float(optical_low) >= float(z_optical_level) or float(z_optical_level) >= float(optical_high):
                fail = True
            status += z_optical_level + " dBm "
        else:
            fail = True
            status += "Z device not polled "

        if a_polled and z_polled:
            # Validate LLDP information
            if (
                    len(a_neighbor_name) == 0 or
                    len(a_neighbor_interface) == 0 or
                    len(z_neighbor_name) == 0 or
                    len(z_neighbor_interface) == 0):
                fail = True
                status += "LLDP data not found "
            elif (
                    a_neighbor_name.lower() == z_device.lower() and
                    a_neighbor_interface.lower() == z_interface.lower() and
                    z_neighbor_name.lower() == a_device.lower() and
                    z_neighbor_interface.lower() == a_interface.lower()):
                status += "LLDP match "
            else:
                fail = True
                status += "LLDP mismatch: A-side actual neighbor is {}:{}; Z-side actual neighbor is {}:{}".format(a_neighbor_name, a_neighbor_interface, z_neighbor_name, z_neighbor_interface)
        else:
            fail = True
        
        # Store the check result
        if fail:
            line.append("FAIL")
        else:
            line.append("PASS")
        line.append(status)

    return csv_contents

def print_csv(csv_contents):
    print "\n"
    print "Result: \n"

    # Make the LAG field optional
    #header = ['a_hostname', 'a_lag', 'a_interface', 'z_interface', 'z_lag', 'z_hostname', 'status', 'result']
    header = ['a_hostname', 'a_interface', 'z_interface', 'z_hostname', 'status', 'result']
    print ",".join(header)

    for line in csv_contents:
        print ",".join(line)


csv_contents = load_csv(csv_file)
devices = get_device_list(csv_contents)
print_csv(check_links(csv_contents, devices))
