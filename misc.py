from robot.api import logger
import os, sys, re, time
import paramiko
from os.path import expanduser
import glob
import pdb
from datetime import datetime
from datetime import timedelta
import difflib
import tableparser
from os.path import splitext
import random
import json

"""
    This is a common library for all other libraries
"""
def nested_print(obj, nested_level=0, output=sys.stdout):
    '''
    This python API display the given message in indented fation
    '''
    spacing = '   '
    if type(obj) == dict:
        logger.console('%s' % ((nested_level) * spacing))
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                logger.console('%s%s:' % ((nested_level + 1) * spacing, k))
                nested_print(v, nested_level + 1, output)
            else:
                logger.console('%s%s: %s' % ((nested_level + 1) * spacing, k, v))
        logger.console('%s' % (nested_level * spacing))
    elif type(obj) == list:
        logger.console('%s[' % ((nested_level) * spacing))
        for v in obj:
            if hasattr(v, '__iter__'):
                nested_print(v, nested_level + 1, output)
            else:
                logger.console('%s%s' % ((nested_level + 1) * spacing, v))
        logger.console('%s]' % ((nested_level) * spacing))
    else:
        logger.console('%s%s' % (nested_level * spacing, obj))

def get_nested_diction(d, keys):
    '''
    This python API returns the value of nested keys in the diction since Robor Framework does not provide it
    '''
    for k in keys.split('.'):
        if type(d) != dict:
            break
        else:
            d = d[k]
    return(d)

def remove_whitespace(instring):
    '''
    This python API removes whitespace and returns the trimed string
    '''
    return instring.strip()

def list_to_string(*args):
    '''
    This python API converts a list to string. Because Robot Framework canot pass in a list 
    as single argument, we have to convert the list to string
    '''
    tcs = ""
    for arg in args:
        tcs += arg + '\n'
    return(tcs)

def restruct_dev_ports(link_ports):
    '''
    This python API returns a diction with key as device and value as ports
    '''
    link_ports_dict = {}
    link_ports = link_ports.split()
    for link_port in link_ports:
        for link in link_port.split(','):
            link = re.sub(r':', ' ', link).split()
            dev = link[0]
            port = link[1]
            if dev in link_ports_dict:
                dev_ports = link_ports_dict[dev]
                dev_ports = dev_ports + ' ' + port
                link_ports_dict[dev] = dev_ports
            else:
                link_ports_dict[dev] = port
    return(link_ports_dict)


def increment_mac(mac, offset):
    '''
    This python API increment mac address
    '''
    if mac.find(":")>0:
        mac = mac.replace(":","")
        mac_out = "{:012X}".format(int(str(mac), 16) + int(offset))
        mac_out = ':'.join(s.encode('hex') for s in mac_out.decode('hex'))
    elif mac.find(".")>0:
        mac = mac.replace(".","")
        mac_out = "{:012X}".format(int(str(mac), 16) + int(offset))
        mac_out = '.'.join(s.encode('hex') for s in mac_out.decode('hex'))
    else :
        mac_out = "{:012X}".format(int(str(mac), 16) + int(offset))
       
    return mac_out

def parse_link(link):
    '''
    This python API rebuild link by removing the middle port which is for matrix
    '''
    port_list = link.split('-')
    if len(port_list) == 3:
        p1 = re.search(r'[a-zA-Z0-9]+:(.*)', port_list[0])
        p2 = re.search(r'[a-zA-Z0-9]+:(.*)', port_list[2])
        if not p1 or not p2:
            logger.console('Unknown format of the port link: %s' % link)
            return 0,0
        return p1.group(1), p2.group(1)
    elif len(port_list) == 1:
        port_list = link.split(',')
        if len(port_list) != 2:
            logger.console('Unknown format of the port link: %s' % link)
            return 0,0
        p1 = re.search(r'[a-zA-Z0-9]+:(.*)', port_list[0])
        p2 = re.search(r'[a-zA-Z0-9]+:(.*)', port_list[1])
        if not p1 or not p2:
            logger.console('Unknown format of the port link: %s' % link)
            return 0,0
        return p1.group(1), p2.group(1)
    else:
        logger.console('Unknown format of the port link: %s' % link)
        return 0,0

def copy_image(image, dst):
    '''
    This python API check if an image exists in the destination folder, copy the image to destination folder in not
    '''
    try:
        status_data = {'status':0}
        if not os.path.isfile(image):
            raise Exception("Image %s does not exists" % image)
        src_image_name = os.path.basename(image)
        dst_images = glob.glob("%s/*.out" % dst)
        image_copied = 0
        for dst_image in dst_images:
            dst_image_name = os.path.basename(dst_image)
            if dst_image_name == src_image_name:
                image_copied = 1
                break
        if image_copied == 0:
            os.system("cp %s %s" % (image, dst))
            image_copied = 1
        status_data = {'status':1, 'copied':image_copied}
    except Exception as msg:
        status_data = {'status':0, 'msg':msg}
    except:
        status_data = {'status':0, 'msg':sys.exc_info()[0]}
    finally:
        return(status_data)

def change_mac(mac, offset):
    mac = mac.replace(":","")
    mac_out = "{:012X}".format(int(str(mac), 16) + int(offset))
    mac_out = ':'.join(s.encode('hex') for s in mac_out.decode('hex'))
    return mac_out

def dict_nested_str(obj, string='', nested_level=0):
    '''
    This python API creates the given message to a string in indented fation
    '''
    indent = '       '
    string += '%s\n' % ((nested_level) * indent)
    for k, v in obj.items():
        if hasattr(v, '__iter__'):
            string += '%s%s:' % ((nested_level + 1) * indent, k)
            string = dict_nested_str(v, string, nested_level + 1)
        else:
            string += '%s%s: %s\n' % ((nested_level + 1) * indent, k, v)
    return(string)

def get_image_name(module_image_str, module_name):
    '''
    This python API parses image name string. The format of the string is:
    module=image,module=image,....
    '''
    image_name = ''
    module_image_list = module_image_str.split(',')
    for module_image in module_image_list:
        module,image = module_image.split('=')
        if module == module_name:
            image_name = image
            break
    return(image_name)

def add_chassis_number(chassis_numb, port):
    '''
    This python API adds chassis number to the post
    '''
    return('%s/%s' % (chassis_numb, port))

def get_string_from_info(*args):
    '''
    This python code returns the string from given info
    '''
    func_name = 'get_string_from_info'
    try:
        status_data = {'status':0}
        temp_var = '-1'
        cli_output = args[0]
        lines = cli_output.split('\n')
        search_expression = args[1]
        for line in lines:
            if re.search(search_expression, line):
                temp_var = line
                break
        if temp_var == '-1':
            raise Exception("Fail to find the info line")
        if len(args) == 3:
            temp_dict = args[2]
            for key in temp_dict:
                temp_item = temp_dict[key]
                original_string = temp_item[0].strip()
                replace_String = temp_item[1].strip()
                temp_var = re.sub(original_string, replace_String, temp_var)
        status_data = {'status':1,'data':temp_var}
    except:
        e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
        status_data = {'status':0, 'msg':e}
    finally:
        return(status_data)

def save_contents_to_file(file_name,contents):
    '''
    This python code save contents to a file
    '''
    func_name = 'save_contents_to_file'
    try:
        status_data = {'status':0}
        file_dir = os.path.dirname(file_name)
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        #nested_print('save_contents_to_file: %s with contents: %s' % (file_name, contents))
        FO = open(file_name, 'w')
        FO.write(contents)
        FO.close()
        status_data = {'status':1}
    except:
        e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
        status_data = {'status':0, 'msg':e}
    finally:
        return(status_data)

def save_contents_to_existing_file(file_name,contents):
    '''
    This python code save contents to a file
    '''
    func_name = 'save_contents_to_existing_file'
    try:
        status_data = {'status':0}
        file_dir = os.path.dirname(file_name)
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        #nested_print('save_contents_to_file: %s with contents: %s' % (file_name, contents))
        FO = open(file_name, 'a')
        FO.write(contents)
        FO.close()
        status_data = {'status':1}
    except:
        e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
        status_data = {'status':0, 'msg':e}
    finally:
        return(status_data)
		
def get_strings_from_info(info, string):
    '''
    This python code returns all strings from given info that matching searching patten in str
    '''
    func_name = 'get_strings_from_info'
    try:
        status_data = {'status':0}
        matches = [] 
        for line in info.split('\n'):
            line = line.strip()
            if re.search(string, line):
                matches.append(line)
        status_data = {'status':1,'data':matches}
    except:
        e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
        status_data = {'status':0, 'msg':e}
    finally:
        return(status_data)

def if_start_within(string, info):
    '''
        This Python code returns 1 if string starts within info
    '''
    func_name = 'if_start_within'
    try:
        ret = 0
        if re.search('^%s' % string, info):
            ret = 1
    except:
        e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
        nested_print(e)
    finally:
        return(ret)

def if_string_in_info(info, string):
    '''
    This python code returns 1 if string in info, otherwise returns 0
    '''
    func_name = 'if_string_in_info'
    try:
        ret = 0
        string = string.strip()
        string = re.sub(r'"', '', string, re.DOTALL)
        string = re.sub(r' +', ' ', string, re.DOTALL)
        string = re.sub(r'_', ' ', string, re.DOTALL)
        string = re.sub(r'\(', '', string, re.DOTALL)
        string = re.sub(r'\)', '', string, re.DOTALL)
        for line in info.split('\n'):
            line = line.strip()
	    line = re.sub(r'"', '', line, re.DOTALL)
            line = re.sub(r' +', ' ', line, re.DOTALL)
            line = re.sub(r'_', ' ', line, re.DOTALL)
            line = re.sub(r'\(', '', line, re.DOTALL)
            line = re.sub(r'\)', '', line, re.DOTALL)
            if re.search(string, line):
                ret = 1
                break
    except:
        e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
        nested_print(e)
    finally:
        return(ret)

def get_flash_config_id(config_info, config_name):
    '''
    This python code returns flash config id
    '''
    func_name = 'get_flash_config_id'
    try:
        status_data = {'status':0}
        for line in config_info.split('\n'):
            line = line.strip()
            if re.search(config_name, line):
                match = re.search(r'^([0-9]+) ', line)
                if match:
                    status_data = {'status':1,'id':match.group(1)}
    except:
        e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
        status_data = {'status':0, 'msg':e}
    finally:
        return(status_data)

def get_specific_item_else_return_zero( info , indexInList):
    '''
    This python code will return the size of list
    '''
    func_name = 'get_specific_item_else_return_zero'
    try:
        status_data = {'status':0}
	length = len(info)
	value = -1
	index = int(indexInList)
	if (length <= index):
	    value = 0
	else:
	    if(length > index ):
		temp_value = str(info[index])
		if(temp_value.find(',') != -1):
			temp_value = temp_value.replace(',','')
		if(temp_value.find('/s') != -1):
			temp_value = temp_value.replace('/s','')
		value = int(temp_value)
	    else:
		value = -1
	if (length != -1 and value != -1):
		status_data = {'status':1,'value':value}
    except:
        e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
	status_data = {'status':0, 'msg':e}
    finally:
	return(status_data)	  	

def parse_keyColonValue_table(table):
    '''
    This python code parses table and return a dict
    '''
    func_name = 'parse_keyColonValue_table'
    try:
        status_data = {'status':0}
        parsed_data = {}
        lines = table.split('\n')
        for line in lines:
            line = line.strip()
            index = line.find(':')
            if index == -1:
                continue
            else:
                key=line[:index].strip()
                value_start = index + 1
                value=line[value_start:].strip()
                key=key.encode('ascii','ignore')
                value=value.encode('ascii','ignore')
                value = re.sub(r'\s+', ' ', value, re.DOTALL)
                if key in parsed_data:
                    key = re.sub(r'\s+', ' ', key, re.DOTALL)
                    parsed_data[key].append(value)
                else:
                    key = re.sub(r'\s+', ' ', key, re.DOTALL)
                    parsed_data[key] = [value]
        status_data = {'status':1, 'data':parsed_data}
    except:
        e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
        status_data = {'status':0, 'msg':e}
    finally:
        return(status_data)

def parse_diag_switch_pducounters_list_table(table):
    '''
    This python code parses 'diag switch pdu-counters list' table and return a dict
S224DF3X15000030 # diag switch pdu-counters list
primary CPU counters:
  packet receive error :        0
  Non-zero port counters:
  port17:
    LLDP packet                   :   394044
  port18:
    LLDP packet                   :   394047
  port21:
    STP packet                    :       40
    LLDP packet                   :       16
  port22:
    STP packet                    :      160
    LLDP packet                   :      117

S224DF3X15000030 #
    '''
    func_name = 'parse_diag_switch_pducounters_list_table'
    try:
        status_data = {'status':0}
        parsed_data = {}
        lines = table.split('\n')
        keys = []
        for line in lines:
            line = line.strip()
            index = line.find(':')
            if index == -1:
                continue
            else:
                key=line[:index].strip()
                value_start = index + 1
                value=line[value_start:].strip()
                if len(value) != 0:
                    if len(keys) == 0:
                        key=key.encode('ascii','ignore')
                        value=value.encode('ascii','ignore')
                        value = re.sub(r'\s+', ' ', value, re.DOTALL)
                        if key in parsed_data:
                            key = re.sub(r'\s+', ' ', key, re.DOTALL)
                            parsed_data[key].append(value)
                        else:
                            key = re.sub(r'\s+', ' ', key, re.DOTALL)
                            parsed_data[key] = [value]
                    else:
                        length_keys = len(keys)
                        if length_keys == 1:
                            if keys[0] not in parsed_data:
                                parsed_data[keys[0]] = {}
                            parsed_data[keys[0]][key] = value
                        elif length_keys == 2:
                            if keys[0] not in parsed_data:
                                parsed_data[keys[0]] = {}
                            if keys[1] not in parsed_data[keys[0]]:
                                parsed_data[keys[0]][keys[1]] = {}
                            parsed_data[keys[0]][keys[1]][key] = value
                        elif length_keys == 3:
                            if keys[0] not in parsed_data:
                                parsed_data[keys[0]] = {}
                            if keys[1] not in parsed_data[keys[0]]:
                                parsed_data[keys[0]][keys[1]] = {}
                            if keys[2] not in parsed_data[keys[0]][keys[1]]:
                                parsed_data[keys[0]][keys[1]][keys[2]] = {}
                            parsed_data[keys[0]][keys[1]][keys[2]][key] = value
                        elif length_keys == 4:
                            if keys[0] not in parsed_data:
                                parsed_data[keys[0]] = {}
                            if keys[1] not in parsed_data[keys[0]]:
                                parsed_data[keys[0]][keys[1]] = {}
                            if keys[2] not in parsed_data[keys[0]][keys[1]]:
                                parsed_data[keys[0]][keys[1]][keys[2]] = {}
                            if keys[3] not in parsed_data[keys[0]][keys[1]][keys[2]]:
                                parsed_data[keys[0]][keys[1]][keys[2]][keys[3]] = {}
                            parsed_data[keys[0]][keys[1]][keys[2]][keys[3]][key] = value
                        else:
                            raise Exception('The length of the list of keys is too long %s, length_keys %s' % (length_keys, length_keys))
                else:
                    if re.search('port[0-9]+',key):
                        keys[-1] = key
                    else:
                        keys.append(key)
        status_data = {'status':1, 'data':parsed_data}
    except:
        e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
        status_data = {'status':0, 'msg':e}
    finally:
        return(status_data)

def parse_keyEqualValue_string(string):
    '''
    This python code parses string and return a dict
    string format: <?xml version="1.0" encoding="UTF-8"?><imdata totalCount="1"><vnsVDev childAction="" ctxName="vrf1" deallocTime="1969-12-31T16:00:00.000-08:00" dn="uni/vDev-[uni/tn-AutoTest1/lDevVip-FG1500_L2]-tn-[uni/tn-AutoTest1]-ctx-vrf1" faultCode="0" faultMessage="" faultSeverity="minor" id="14100" lcOwn="local" modTs="2019-02-28T12:11:20.105-08:00" monPolDn="uni/tn-common/monepg-default" name="" nameAlias="" priKey="uni/tn-AutoTest1/lDevVip-FG1500_L2" st="allocated" status="" tnDn="uni/tn-AutoTest1" trunking="no"/></imdata>
    '''
    func_name = 'parse_keyEqualValue_string'
    try:
        status_data = {'status':0}
        parsed_data = {}
        lines = string.split()
        for line in lines:
            line = line.strip()
            index = line.find('=')
            if index == -1:
                continue
            else:
                key=line[:index].strip()
                value_start = index + 1
                value=line[value_start:].strip()
                key=key.encode('ascii','ignore')
                value=value.encode('ascii','ignore')
                value = re.sub(r'\s+', ' ', value, re.DOTALL)
                value = re.sub(r'"', '', value, re.DOTALL)
                if key in parsed_data:
                    key = re.sub(r'\s+', ' ', key, re.DOTALL)
                    parsed_data[key].append(value)
                else:
                    key = re.sub(r'\s+', ' ', key, re.DOTALL)
                    parsed_data[key] = [value]
        status_data = {'status':1, 'data':parsed_data}
    except:
        e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
        status_data = {'status':0, 'msg':e}
    finally:
        return(status_data)

def get_remote_file(ip, user, password, remote_log):
    '''
    This python code tftp to remote server and get file
    '''
    func_name = 'get_remote_file'
    try:
        status_data = {'status':0}
        local_home = expanduser("~")
        log_file = os.path.basename(remote_log)
        local_log = '%s/%s' % (local_home, log_file)
        status_data = {'status':0, 'remote_log':remote_log, 'local_log':local_log}
        # ssh to remote server
        ssh = paramiko.SSHClient()
        ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
        ssh.connect(ip,username='%s' % user, password='%s' % password)
        # get remote file
        sftp = ssh.open_sftp()
        sftp.get(remote_log, local_log)
        # get the comment of the log file
        if not os.path.isfile(local_log):
            raise Exception('%s, Invaild log: %s' % (func_name, local_log))
        fid = open(local_log, 'r')
        iperf_log = fid.read()
        fid.close()
        # delete remote log file
        sftp.remove(remote_log)
        status_data = {'status':1, 'data':iperf_log}
    except:
        e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
        status_data = {'status':0, 'msg':e}
    finally:
        sftp.close()
        ssh.close()
        return(status_data)

def get_regexp_matches(info,pattern):
    '''
	This Python code will search the pattern which is str from the info 
    '''
    func_name = 'get_regexp_matches'
    try:
	status_data = {'status':0}
	regex = str(pattern)
	matches = re.findall(regex,info)
	if(matches):
		searches = []
		for match in matches:
			searches.append(match)
		status_data = {'status':1,'data':searches}
	else:
		status_data = {'status':1,'data':NONE}
    except:
	e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
	status_data = {'status':0, 'msg':e}
    finally:
	return(status_data)

def search_matches(info, pattern):
    '''
        This Python code will search the pattern which is str from the info
    '''
    func_name = 'search_matches'
    #pattern = str(pattern)
    pattern = re.sub(r'\[', '\[', pattern)
    pattern = re.sub(r'\]', '\]', pattern)
    pattern = re.sub(r'\(', '\(', pattern)
    pattern = re.sub(r'\)', '\)', pattern)
    pattern = re.sub(r' ', '\s+', pattern)
    info = re.sub(r'(\\r)+', '', info, re.DOTALL)
    info_list = info.split('\n')
    status = 0
    for line in info_list:
        if re.search(pattern, line):
            status = 1
            break
    return(status)

def mac_to_link_local_ipv6(mac):
    '''
	This Python code will give the IPv6 link local address
	passed the MAC Address
	only accept MACs separated by a colon
    '''
    func_name = 'mac_2_link_local_ipv6'
    try:
	status_data = {'status':0}
	parts = mac.split(":")
    	# modify parts to match IPv6 value
	parts.insert(3, "ff")
        parts.insert(4, "fe")
        parts[0] = "%x" % (int(parts[0], 16) ^ 2)

        # format output
        ipv6Parts = []
    	for i in range(0, len(parts), 2):
        	ipv6Parts.append("".join(parts[i:i+2]))
	ipv6 = "fe80::%s" % (":".join(ipv6Parts))
	status_data = {'status':1,'data':ipv6} 
    except:
	e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
	status_data = {'status':0, 'msg':e}
    finally:
	return(status_data)

def link_local_ipv6_to_mac(ipv6):
    '''
	This Python code will give the Mac Address out of the link local IPv6 Address
    '''
    func_name = 'link_local_ipv6_to_mac'
    try:
	status_data = {'status':0}
	# remove subnet info if given
    	subnetIndex = ipv6.find("/")
    	if subnetIndex != -1:
        	ipv6 = ipv6[:subnetIndex]
	ipv6Parts = ipv6.split(":")
	macParts = []
    	for ipv6Part in ipv6Parts[-4:]:
        	while len(ipv6Part) < 4:
 	           ipv6Part = "0" + ipv6Part
        	macParts.append(ipv6Part[:2])
	        macParts.append(ipv6Part[-2:])

    	# modify parts to match MAC value
    	macParts[0] = "%02x" % (int(macParts[0], 16) ^ 2)
    	del macParts[4]
    	del macParts[3]
	mac_address = ":".join(macParts)
	status_data = {'status':1,'data':mac_address}
    except:
	e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
	status_data = {'status':0, 'msg':e}
    finally:
	return(status_data) 

def remove_leading_zeros_from_link_local_address(link_local_address):
    '''
	This function will remove leading zeros from each octet of the string
    '''
    func_name = 'remove_leading_zeros_from_link_local_address'
    try:
	status_data = {'status':0}
	parts = link_local_address.split(":")
	leading_removed = [part.lstrip("0") for part in parts]
	link_local_addr = "%s" % (":".join(leading_removed))
	status_data = {'status':1, 'data':link_local_addr}
    except:
	e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
	status_data = {'status':0, 'msg':e}
    finally:
	return(status_data)

def if_file_exists(filename):
    '''
        This Python code returns 1 if given file exists. Otherwise returns 0
    '''
    func_name = 'if_file_exists'
    try:
        ret = 0
        # Check if file exists
        if os.path.isfile(filename):
            ret = 1
    except:
        e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
        nested_print(e)
    finally:
        return(ret)

def if_file_exists_at_infosite(filename):
    '''
        This Python code returns 1 if given file exists. Otherwise returns 0
    '''
    func_name = 'if_file_exists_at_infosite'
    try:
        ret = 0
        # Check if file exists
        for index in range(0, 3):
            if os.path.isfile(filename):
                ret = 1
                break
            else:
                nested_print('\t%s is missing. Waiting 5 seconds and check again....' % filename)
                time.sleep(5)
    except:
        e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
        nested_print(e)
    finally:
        return(ret)

def add_new_pair_to_dict(dictionary, key, value):
    '''
        This Python code add key and value to dictionary and returns it
    '''
    func_name = 'add_to_dictionary'
    try:
        if key in dictionary:
            dictionary[key] = value
        else:
            dictionary[key] = value
    except:
        e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
        nested_print(e)
    finally:
        return(dictionary)

def is_empty_dictionary(dictionary):
    '''
        This Python code will verify whether the dictionary is Empty or not
    '''
    func_name = 'is_empty_dic'
    try:
	ret = 1
        if not dictionary:
            ret = 0
        else:
	    ret = 1
    except:
        e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
        nested_print(e)
    finally:
        return(ret)

def set_dict(dictionary, key, value):
    '''
        This Python code add key and value to dictionary and returns it
    '''
    func_name = 'set_dict'
    try:
        # remove subnet info if given
        if key in dictionary:
            dictionary[key].append(value)
        else:
            dictionary[key] = [value]
    except:
        e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
        nested_print(e)
    finally:
        return(dictionary)

def get_value_in_dict(dictionary, key):
    '''
        This Python code returns the value if given key in dictionary. Otherwise returns 0
    '''
    func_name = 'get_value_in_dict'
    try:
        ret = []
        # remove subnet info if given
        if key in dictionary:
            ret = dictionary[key]
    except:
        e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
        nested_print(e)
    finally:
        return(ret)

def if_in_list(listname, value):
    '''
        This Python code returns 1 if value in listname, otherwise returns 0
    '''
    func_name = 'if_in_list'
    try:
        ret = '0'
        # remove subnet info if given
        if value in listname:
            ret = 1
    except:
        e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
        nested_print(e)
    finally:
        return(ret)

def get_port_major_number(port):
    '''
        This Python code returns the major number of the port
    '''
    func_name = 'get_port_major_number'
    try:
        ret = 0
        # remove subnet info if given
        match = re.search('port([0-9]+)\.?', port)
        if match:
            ret = match.group(1)
    except:
        e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
        nested_print(e)
    finally:
        return(ret)

def if_contains_in_list(listname, value):
    '''
        This Python code returns 1 if value in list, otherwise returns 0
    '''
    func_name = 'if_contains_in_list'
    try:
        ret = '0'
        # remove subnet info if given
        for iteam in listname:
            if re.search(value, iteam):
                ret = 1
    except:
        e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
        nested_print(e)
    finally:
        return(ret)

def if_key_in_dict(dict, key):
    '''
        This Python code returns 1 if key in dictionary, otherwise returns 0
    '''
    func_name = 'if_key_in_dict'
    try:
        ret = '0'
        # remove subnet info if given
        if key in dict:
            ret = 1
    except:
        e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
        nested_print(e)
    finally:
        return(ret)

def get_asic_type(sku):
    '''
        This Python code will return the asic type the sku belongs
    '''
    func_name = 'get_asic_type'
    try:
	status_data = {'status':0, 'asic_type':'None'}

        # remove subnet info if given
        brcm_asic_sku = ['matrix','S124D','S124D','S1D24','S1D48','S224DF','S248D','S3D32','S424D','S448D','S524D','S548D','SR24D','S224E','S248E','FS1E48','FS3E32','S148E','S426E']
        xcat_asic_sku = ['SR12D','FS108D','FS224D','S124E','S108E']
        find_match = 0
        for brcm_asic_sku_name in brcm_asic_sku:
            if re.search(brcm_asic_sku_name, sku):
	        status_data = {'status':1, 'asic_type':'BRCM'}
                find_match = 1
                break
        if find_match == 0:
            for xcat_asic_sku_name in xcat_asic_sku:
                if re.search(xcat_asic_sku_name, sku):
	            status_data = {'status':1, 'asic_type':'XCAT'}
                    find_match = 1
                    break
    except:
        e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
        status_data = {'status':0, 'msg':e}
    finally:
        return(status_data)

def if_support_vrrp(sku):
    '''
        This Python code will return 1 if sku supports vrrp, returns 0 otherwise
    '''
    func_name = 'if_support_vrrp'
    try:
        ret = 0

        # remove subnet info if given
        vrrp_sku = ['S1D24','S1D48','S3D32','S424D','S448D','S524D','S548D','FS1E48','FS3E32','S426E']
        for platform in vrrp_sku:
            if re.search(platform, sku):
                ret = 1
                break
    except:
        e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
        nested_print(e)
    finally:
        return(ret)

def get_platform_family(sku):
    '''
        This Python code will return the platform_family type: PPC, Firescout, XCAT, Realtech or Wolfhound
    '''
    func_name = 'get_platform_family'
    try:
        status_data = {'status':0, 'type':'None'}

        # remove subnet info if given
        ppc_sku = ['S1D24','S1D48','S3D32','FS1E48','FS3E32']
        firescount_sku = ['S524D','S548D']
        wolfhound_sku = ['S124D','S224DF','S248D','S424D','S448D','SR24D','S426E','S224E','S248E']
        xcat_sku = ['SR12D','FS108D','FS224D']
        realTech_sku = ['S124E','S108E','S148E']
        find_match = 0
        for platform in ppc_sku:
            if re.search(platform, sku):
                status_data = {'status':1, 'type':'PPC'}
                find_match = 1
                break
        if find_match == 0:
            for platform in firescount_sku:
                if re.search(platform, sku):
                    status_data = {'status':1, 'type':'Firescout'}
                    find_match = 1
                    break
        if find_match == 0:
            for platform in wolfhound_sku:
                if re.search(platform, sku):
                    status_data = {'status':1, 'type':'Wolfhound'}
                    find_match = 1
                    break
        if find_match == 0:
            for platform in xcat_sku:
                if re.search(platform, sku):
                    status_data = {'status':1, 'type':'XCAT'}
                    find_match = 1
                    break
        if find_match == 0:
            for platform in realTech_sku:
                if re.search(platform, sku):
                    status_data = {'status':1, 'type':'RealTech'}
                    find_match = 1
                    break
    except:
        e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
        status_data = {'status':0, 'msg':e}
    finally:
        return(status_data)

def get_platform_maximum_mac(sku):
    '''
        This Python code will return maximum mac supported bt give platform
    '''
    func_name = 'get_platform_maximum_mac'
    try:
        status_data = {'status':0}
        if re.search('(S124D|S248D|S224DF|S424D|S448D|SR24D|S224EN|FS1E48|S426E)', sku):
            status_data = {'status':1, 'maximum_mac':16000}
        elif re.search('(S524D|S548D)', sku):
            status_data = {'status':1, 'maximum_mac':24000}
        elif re.search('(S1D24|S1D48|S3D32|S3E32)', sku):
            status_data = {'status':1, 'maximum_mac':30000}
        elif re.search('(SR12D|FS108D|FS224D|S224E|S248E|S148E)', sku):
            status_data = {'status':1, 'maximum_mac':16000}
        elif re.search('(S124E|S108E)', sku):
            status_data = {'status':1, 'maximum_mac':8000}
    except:
        e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
        status_data = {'status':0, 'msg':e}
    finally:
        return(status_data)

def get_port_count(sku):
    '''
        This Python code will return the port number of the switch
    '''
    func_name = 'get_port_count'
    try:
        # remove subnet info if given
        port_count = 0
        if re.search('108', sku):
             port_count = 10
        elif re.search('12D',sku):
            port_count = 12
        elif re.search('(124|1D24|224|424|524|24D)',sku):
            port_count = 24
        elif re.search('(FS3D32|FS3E32)',sku):
            port_count = 32
        elif re.search('(1D48|248|448|548|1E48|148E)',sku):
            port_count = 48
        elif re.search('(S426E)',sku):
            port_count = 26
    except:
        e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
        nested_print(e)
    finally:
        return(port_count)

def get_build_info(image_name):
    '''
        This Python code will Get sw_ver, build_version_num, and build_subnumber from first 100 bytes of buildfile.
    '''
    func_name = 'get_build_info'
    try:
        status_data = {'status':0}
        if os.path.isfile(image_name):
            image_path = image_name
        else:
            image_path = '/tftpboot/' + image_name
            if not os.path.isfile(image_path):
                raise Exception("Could not find build information in %s header!!!" % image_path)
        fp = open(image_path, 'rb')
        file_header = fp.read(100)
        fp.seek(0)
        fp.close()

        match = re.search(r'(\w+)-(\d\.)0(\d+)-FW-build(\d+)-(\d+)', file_header)
        if match:
            device_type = match.groups()[0]
            sw_ver = match.groups()[1] + match.groups()[2]
            build_version_num = match.groups()[3]
            build_subnumber = match.groups()[4]
            status_data = {'status':1, 'device_type':device_type, 'sw_ver':sw_ver, 'build_version_num':build_version_num, 'build_subnumber':build_subnumber}
        else:
            raise Exception("Could not find build information in %s file header!!!" % image_path)
    except Exception as msg:
        status_data = {'status':0, 'msg':msg}
    except:
        status_data = {'status':0, 'msg':sys.exc_info()[0]}
    finally:
        return(status_data)

def get_dev_port_data(dev_port_dict, link):
    '''
        This Python code returns the collection of dev & port in dict
    '''
    func_name = 'get_dev_port_data'
    try:
        status_data = {'status':0}
        # Match means this is a link of connecting dev and trafgen
        # Otherwise it is a link betwenn devices
        match = re.search(r'-', link)
        if match:
            link_list = link.split('-')
            dev, port = link_list[0].split(':')
            if dev not in dev_port_dict:
                dev_port_dict[dev] = [port]
            else:
                dev_port_dict[dev].append(port)
            trafgen, trafgenport = link_list[2].split(':')
            if re.search('vm[0-9]', trafgen):
                status_data = {'status':2, 'data':dev_port_dict}
            else:
                status_data = {'status':1, 'data':dev_port_dict}
        else:
            devp1, devp2 = link.split(',')
            dev, port = devp1.split(':')
            if dev not in dev_port_dict:
                dev_port_dict[dev] = [port]
            else:
                dev_port_dict[dev].append(port)
            dev, port = devp2.split(':')
            if dev not in dev_port_dict:
                dev_port_dict[dev] = [port]
            else:
                dev_port_dict[dev].append(port)
            status_data = {'status':1, 'data':dev_port_dict}
    except Exception as msg:
        status_data = {'status':0, 'msg':msg}
    except:
        status_data = {'status':0, 'msg':sys.exc_info()[0]}
    finally:
        return(status_data)

def get_up_ports(port_list, status_list, ignore_ports):
    '''
        This Python code returns up ports in a list
    '''
    func_name = 'get_up_ports'
    try:
        status_data = {'status':0}
        up_ports = []
        port_list_length = len(port_list)
        status_list_length = len(status_list)
        if port_list_length != status_list_length:
            raise Exception("The length of port_list (%s) and the length of status_list (%s) are different" % (port_list_length, status_list_length))
        for port, status in zip(port_list, status_list):
            if re.search(r'port', port) and status == 'up' and port not in ignore_ports:
                up_ports.append(port)
            status_data = {'status':1, 'data':up_ports}
    except Exception as msg:
        status_data = {'status':0, 'msg':msg}
    except:
        status_data = {'status':0, 'msg':sys.exc_info()[0]}
    finally:
        return(status_data)

def check_release(release):
    '''
        This Python code returns 0 when release is unknown, 1 when release is 3.5, 2 when release is 3.6, 3 when release is 6.0 ...
    '''
    func_name = 'check_release'
    release = release.encode('ascii','ignore')
    try:
        if '3.5' == release:
            ret = 1
        elif '3.6' == release or re.search(r'npi', release, re.IGNORECASE):
            ret = 2
        elif re.match('6\.[0-9]', release):
            ret = 3
        else:
            ret = 0
    except:
        nested_print(sys.exc_info()[0])
    finally:
        return(ret)

def if_release_is(release_base, release):
    '''
        This Python code returns 0 when release version is below the given release base, returns 1 otherwise.
    '''
    func_name = 'if_release_is'
    release_b = release_base.encode('ascii','ignore')
    release_n = release.encode('ascii','ignore')
    try:
        ret = 1
        release_base_digits = release_b.split('.')
        release_digits = release_n.split('.')
        release_digit_pair = zip(release_base_digits, release_digits)
        for release_digit in release_digit_pair:
            digit1 = int(release_digit[0])
            digit2 = int(release_digit[1])
            if digit1 > digit2:
                ret = 0
                break
    except:
        nested_print(sys.exc_info()[0])
    finally:
        return(ret)

def sort_by_number(str_list):
    '''
        This Python code returns a new list which is sorted by number in the string
    '''
    return list(map(int, re.findall(r'\d+', str_list)))

def get_alpha_string_only(string):
    '''
        This Python code returns a new string which has alpha characters only
    '''
    string = re.sub(r'(\(|\))', '', string)
    match = re.match(r'([a-zA-Z]+)', string)
    if match:
        return(match.group(1))
    else:
        return(string)


def get_list_of_mac_addr_entries_of_particular_mac_addr(info,expected_mac_address):
    '''
	this python code will take the mac address table info output
	and it will give the list of entries for the particular mac address
    '''
    func_name = 'get_list_of_mac_addr_entries_of_particular_mac_addr'
    try:
        status_data = {'status':0}
	list_of_entries = []
        mac_address_table = info.split('\n')
	for line in mac_address_table:
		if(expected_mac_address in line):
			list_of_entries.append(line)
	status_data = {'status':1, 'data':list_of_entries}
    except Exception as msg:
        status_data = {'status':0, 'msg':msg}
    except:
        status_data = {'status':0, 'msg':sys.exc_info()[0]}
    finally:
        return(status_data)

def get_port_major_id(port):
    '''
        this python code parses the port name and return its major id: port3->id:3, port34->id:34, port5.1->id:5
    '''
    func_name = 'get_port_major_id'
    match = re.search(r'([0-9]+)', port)
    if match:
        return(match.group(1))
    else:
        return(0)

def check_superset_topo(current_topo, new_topo):
    '''
        This Python code returns 1 if current_topo is a supset topo of the new_topo. Otherwise return 0
        Due to the connection might change when topo has multiple devices, only returns 1 when such topos are the same
    '''
    if len(current_topo) != len(new_topo):
        return(0)

    match = re.search(r'([a-z]+Sw)', current_topo)
    if match:
        current_topo_type = match.group(1)
    else:
        return(0)

    match = re.search(r'([a-z]+Sw)', new_topo)
    if match:
        new_topo_type = match.group(1)
    else:
        return(0)

    if current_topo_type != new_topo_type:
        return(0)

    # Check the number of Trafgen 
    match = re.search(r'([0-9])Trafgen', current_topo)
    if match:
        current_topo_trafgens = match.group(1)
    else:
        match = re.search(r'Trafgen', current_topo)
        if match:
            current_topo_trafgens = 1
        else:
            current_topo_trafgens = 0

    match = re.search(r'([0-9])Trafgen', new_topo)
    if match:
        new_topo_trafgens = match.group(1)
    else:
        match = re.search(r'Trafgen', new_topo)
        if match:
            new_topo_trafgens = 1
        else:
            new_topo_trafgens = 0

    # Check the number of Links 
    match = re.search(r'([0-9])Links', current_topo)
    if match:
        current_topo_links = match.group(1)
    else:
        match = re.search(r'Link', current_topo)
        if match:
            current_topo_links = 1
        else:
            current_topo_links = 0

    match = re.search(r'([0-9])Links', new_topo)
    if match:
        new_topo_links = match.group(1)
    else:
        match = re.search(r'Link', new_topo)
        if match:
            new_topo_links = 1
        else:
            new_topo_links = 0

    if new_topo_type == 'singleSw':
        if current_topo_trafgens >= new_topo_trafgens and current_topo_links >= new_topo_links:
            return(1)
        else:
            return(0)
    else:
        if current_topo_trafgens == new_topo_trafgens and current_topo_links == new_topo_links:
            return(1)
        else:
            return(0)

def compare_dates(year,month,day,hour,min,second=0):
    '''
        this python api will compare two date time stamps
    '''
    try:
        status_data = {'status':0}
        last_year = int(year)
        last_month = int(month)
        last_day = int(day)
        last_hour = int(hour)
        last_min = int(min)
        last_second = int(second)
        nested_print('conversion is ok')
        expected_finish_time  = datetime(last_year, last_month, last_day, last_hour, last_min, last_second)
        present_time = datetime.now()
        flag = 100
        if( present_time < expected_finish_time ):
                flag = 1
        else:
                flag = 0
        status_data = {'status':1, 'flag':flag}
    except:
        status_data = {'status':0, 'msg':sys.exc_info()[0]}
    finally:
        return(status_data)

def create_datetime_object(year,month,day,hour=0,min=0,second=0):
    '''
        this python api will create datetime object
    '''
    try:
        status_data = {'status':0}
        last_year = int(year)
        last_month = int(month)
        last_day = int(day)
        last_hour = int(hour)
        last_min = int(min)
        last_second = int(second)
        converted_time  = datetime(last_year, last_month, last_day, last_hour, last_min, last_second)
        status_data = {'status':1, 'data':converted_time}
    except:
        status_data = {'status':0, 'msg':sys.exc_info()[0]}
    finally:
        return(status_data)

def get_datetime_difference(datetime1, datetime2):
    '''
        this python api will give us the difference in between two datetime objects
    '''
    try:
        status_data = {'status':0}
	if(datetime1>datetime2):
	    diff = datetime1 - datetime2
	else:
	    diff = datetime2 - datetime1
	diff_in_seconds = diff.seconds
        status_data = {'status':1, 'data':diff_in_seconds}
    except:
        status_data = {'status':0, 'msg':sys.exc_info()[0]}
    finally:
        return(status_data)
	

def collect_leftover_configuration(suite_name, init_file, final_file):
    '''
        this python api finds delta data within init_file and final_file and append them to delta_file
    '''
    try:
        status_data = {'status':0}
        # Check if init_file exists
        if not os.path.isfile(init_file):
            raise Exception("Initial File %s does not exists" % init_file)
        # Check if final_file exists
        if not os.path.isfile(final_file):
            raise Exception("Final File %s does not exists" % init_file)
        file_dir = os.path.dirname(final_file)
        t = datetime.now()
        start_t = t.strftime("%Y%m%d-%H%M%S")
        # Find the diff
        init_fd = open(init_file, 'r')
        final_fd = open(final_file, 'r')
        diff = difflib.context_diff(init_fd.readlines(), final_fd.readlines())
        delta = ''.join(diff).split('\n')

        leftover_data = ''
        begin_rsa_private_key = 0
        for line in delta:
            if re.search(r'^ +#', line):
                continue
            if re.search(r'^! #', line):
                continue
            if re.search(r'ENC', line):
                continue
            if re.search(r'(show full-configuration|config system certificate local|Fortinet_Factory)', line):
                continue
            if begin_rsa_private_key == 1:
                continue
            if re.search(r'BEGIN RSA PRIVATE KEY', line):
                begin_rsa_private_key = 1
                continue
            if re.search(r'END RSA PRIVATE KEY', line):
                begin_rsa_private_key = 0
                continue
            else:
                leftover_data += '%s\n' % line

        suite_name = re.sub('\.', '_', suite_name, re.DOTALL)
        suite_name = re.sub(' ', '_', suite_name, re.DOTALL)
        # save leftover data to a file
        fd = open('%s/%s_leftover.cfg' % (file_dir, suite_name), 'w')
        fd.write(leftover_data)
        fd.close()
        # remove init_file and final_file
        os.remove(init_file)
        os.remove(final_file)
        status_data = {'status':1}
    except Exception as msg:
        status_data = {'status':0, 'msg':msg}
    except:
        status_data = {'status':0, 'msg':sys.exc_info()[0]}
    finally:
        return(status_data)

def get_image_size(image_name):
    '''
        This Python code will Get Image Size.
    '''
    func_name = 'get_image_size'
    try:
        if os.path.isfile(image_name):
            image_path = image_name
        else:
            image_path = '/tftpboot/' + image_name
            if not os.path.isfile(image_path):
                raise Exception("Could not find build information in %s header!!!" % image_path)
        statinfo = os.stat(image_path)
        with open(image_path, 'rb') as f:
            try:
                checksum = f.read(4);			
                length = f.read(8)
            except:
                nested_print('\r\nUnexpected eof\r\n');
                sys.exit(100);
        filesize = int(statinfo.st_size)

        if (int(length) == int(statinfo.st_size)):
            nested_print('File size matches\r\n');
            return filesize
        else:
            nested_print('\r\nABORT: Invalid file by size check\r\n');
            sys.exit(105);
    except Exception as msg:
        nested_print(msg)

def check_ip_ping(info):
    '''
        This Python code check given info and returns 1 "0% packet loss", otherwise returns 0
    '''
    func_name = 'check_ip_ping'
    try:
        ret = 0
        lines = info.split('\n')
        for line in lines:
	    match = re.search(r'([0-9]+)% packet loss', line)
	    if match:
	        if match.group(1) == '0':
	            ret = 1
    except:
        nested_print(sys.exc_info()[0])
    finally:
        return(ret)

def check_fgt_stage_image(sku, image, info):
    '''
FG1K5D3I14800830 (global) # execute switch-controller list-swtp-image
SWTP Images on AC:
ImageName              ImageSize(B)   ImageInfo             ImageMTime
S524DF-IMG.swtp        23316283       S524DF-v3.6-build373  Thu Oct 26 17:28:53 2017
FS108D-IMG.swtp        16817088       FS108D-v3.6-build390  Fri Oct 27 11:01:56 2017
FS224D-IMG.swtp        16819923       FS224D-v3.6-build390  Fri Oct 27 11:43:23 2017

FG1K5D3I14800830 (global) #
    '''
    func_name = 'check_fgt_stage_image'
    try:
        status_data = {'status':0}
        sku_type = sku[:6]
        image_ver_info = re.search(r'((v[0-9]+\.[0-9]|v[0-9]+))-build([0-9]+)-FORTINET', image)        
        if not image_ver_info:
            raise Exception("Invalid Image Name Format %s" % image)
        info_list = info.split('\n')
        for line in info_list:
            if len(line) < 80:
                continue
            line_list = line.split()
            build = image_ver_info.group(3)[1:]
            if re.search(sku_type, line_list[2]) and re.search(image_ver_info.group(1), line_list[2]) and re.search(build, line_list[2]):
                status_data = {'status':1, 'image':line_list[0]}
                break
    except Exception as msg:
        status_data = {'status':0, 'msg':msg}
    except:
        status_data = {'status':0, 'msg':sys.exc_info()[0]}
    finally:
        return(status_data)

def check_fgt_image_download_process(info):
    '''
FG1K5D3I14800830 (sw-flink) # execute switch-controller push-swtp-image FS224D3Z16000059 FS224D-IMG.swtp
Image download process: 100%

FG1K5D3I14800830 (sw-flink) #
    '''
    func_name = 'check_fgt_image_download_process'
    try:
        ret = 0
        match = re.search(r'Image download process: ([0-9]+)%', info)
        if not match:
            raise Exception("Unknown Format of push-swtp-image Info %s" % info)
        if match.group(1) == '100':
            ret = 1
    except Exception as msg:
        nested_print(msg)
    except:
        nested_print(sys.exc_info()[0])
    finally:
        return(ret)

def get_image_type(image):
    '''
        this api check image and returns its type. Either "Nightly_Build" or "CM_Build"
    '''
    func_name = 'get_image_type'
    try:
        ret = 'CM_Build'
        file_name,extention = splitext(image)
        match = re.search('deb', extention)
        if match:
            ret = 'Nightly_Build'
    except:
        nested_print(sys.exc_info()[0])
    finally:
        return(ret)

def get_fortilink_trunk_names(sw1, sw2, sw1_port, sw2_port, info):
    '''
        this api parse the info using sw sereil-ids, switch ports and return fortilink trunk names
        Format of the info api will be parsing:
          FS1D243Z17000023(port21/D243Z16000155-0)  <<------------------>> FS1D243Z16000155(port21/D243Z17000023-0)
    '''
    func_name = 'get_image_typlink_trunk_names'
    try:
        status_data = {'status':0}
        info_list = info.split('\n')
        search_patten = sw1 + '\(' + sw1_port + '/' + '(.*)' + '\)' + '.*' + sw2 + '\(' + sw2_port + '/' + '(.*)' + '\)'
        for line in info_list:
            match = re.search(search_patten, line)
            if match:
                trunk_names = [match.group(1), match.group(2)]
                status_data = {'status':1, 'trunk_names':trunk_names}
                break
    except:
        status_data = {'status':0, 'msg': sys.exc_info()[0]}
    finally:
        return(status_data)

def check_fortilink_icl_ports(icl_ports, info):
    '''
        this api parse the info using to ensure info contains icl-ports correctly
    '''
    func_name = 'check_fortilink_icl_ports'
    try:
        status_data = {'status':0}
        info_list = info.split('\n')
        see_icl_ports_line = 0
        for line in info_list:
            match_icl_ports = re.search('icl-ports', line)
            if match_icl_ports:
                see_icl_ports_line += 1
                ports = line.split()
                for icl_port in icl_ports:
                    if icl_port not in ports:
                        raise Exception('icl_port %s is missing in "%s"' % (icl_port, line))
        if see_icl_ports_line == 1:
            status_data = {'status':1}
    except Exception as msg:
        status_data = {'status':0, 'msg':msg}
    except:
        status_data = {'status':0, 'msg': sys.exc_info()[0]}
    finally:
        return(status_data)

def parse_switch_vlan_list(vlan, delimiter, ports, info):
    '''
        this api parse the output of cli "diagnose switch vlan list 10" and ensure all ports are in the port list
    '''
    func_name = 'parse_switch_vlan_list'
    try:
        status_data = {'status':0}
        header = 'VlanId Ports'
        table_info = {
            'table':info,
            'header':header,
            'delimiter':delimiter,
        }
        t = tableparser.tableParserInPosition(table_info)
        if t['status'] != 1:
            raise Exception('parse_switch_vlan_list tableParserInPosition fail')
        if t['data']['VlanId'][0] != vlan:
            raise Exception('parse_switch_vlan_list fail due to incorrct vlanid')
        port_str = ''.join(map(str, t['data']['Ports']))
        missing_ports = []
        for port in ports:
            if re.search('port[0-9][0-9]', port):
                _port = port
            else:
                _port = '%s ' % port
            if _port not in port_str:
                missing_ports.append(port)
        if len(missing_ports) == 0:
            status_data = {'status':1, 'msg':''}
        else:
            status_data = {'status':0, 'msg':missing_ports}
        
    except Exception as msg:
        status_data = {'status':0, 'msg':msg}
    except:
        status_data = {'status':0, 'msg': sys.exc_info()[0]}
    finally:
        return(status_data)

def parse_physicalPort_datarates(info):
    '''
        this api parse the output of cli "diagnose switch physical-ports datarate" and return all info in a dictionary
    '''
    func_name = 'parse_physicalPort_datarates'
    try:
        status_data = {'status':0}
        header = 'Port | TX_Packets | TX_Rate || RX_Packets | RX_Rate |'
        table_info = {
            'table':info,
            'header':header,
            'delimiter':'ctrl-c to stop',
            'special':1,
        }
        t = tableparser.tableParserInPosition(table_info)
        if t['status'] != 1:
            raise Exception('parse_physicalPort_datarates tableParserInPosition fail')
        status_data = {'status':1, 'data':t['data']}
    except Exception as msg:
        status_data = {'status':0, 'msg':msg}
    except:
        status_data = {'status':0, 'msg': sys.exc_info()[0]}
    finally:
        return(status_data)

def parse_physicalPort_mapping_get_portid(info, port):
    '''
        this api parse the output of cli "diagnose switch physical-ports mapping" and return portid of given port
    '''
    func_name = 'parse_physicalPort_mapping_get_portid'
    try:
        status_data = {'status':0}
        header = 'Port_Name PortID | Unit Port Driver_Name'
        table_info = {
            'table':info,
            'header':header,
            'delimiter':'internal',
            'special':1,
        }
        t = tableparser.tableParserInPosition(table_info)
        if t['status'] != 1:
            raise Exception('parse_physicalPort_mapping_get_portid tableParserInPosition fail')
        ports = t['data']['Port_Name____________PortID']
        for p in ports:
            port_info = p.split()
            if port == port_info[0]:
               status_data = {'status':1, 'portid': port_info[1]} 
               break
    except Exception as msg:
        status_data = {'status':0, 'msg':msg}
    except:
        status_data = {'status':0, 'msg': sys.exc_info()[0]}
    finally:
        return(status_data)

def diagnose_switch_mclag_peer_consistency_check(host, info, trunname, lcl_ports, rt_ports):
    '''
        this api parse the output of cli "diagnose switch mclag peer-consistency-check and ensure all ports are in the port list
    '''
    func_name = 'diagnose_switch_mclag_peer_consistency_check'
    try:
        status = 1
        mismatch_sate = ''
        wrong_sate = ''
        missing_lcl_ports = []
        missing_remote_ports = []
        header = 'mclag-trunk-name peer-config lacp-state stp-state local-ports remote-ports'
        table_info = {
            'table':info,
            'header':header,
            'delimiter':host,
        }
        t = tableparser.tableParserInPosition(table_info)
        if t['status'] != 1:
            raise Exception('diagnose_switch_mclag_peer_consistency_check tableParserInPosition fail: %s' % t['data'])
        mclag_trunk_name_list = t['data']['mclag-trunk-name']
        index = 0
        for mclag_trunk_name in mclag_trunk_name_list:
            mclag_trunk_name = re.sub(r'\*', '', mclag_trunk_name)
            if mclag_trunk_name == trunname:
                break
            else:
                index += 1
        if index >= len(mclag_trunk_name_list):
            nested_print('diagnose_switch_mclag_peer_consistency_check fail due to unable to find mclag-trunk-name: %s' % trunname)
            status = 0
        else:
            peer_config = t['data']['peer-config'][index]
            lacp_state = t['data']['lacp-state'][index]
            stp_state = t['data']['stp-state'][index]
            local_ports = t['data']['local-ports'][index].split()
            remote_ports = t['data']['remote-ports'][index].split()
            #if peer_config != 'OK':
            #    wrong_sate += 'peer_config is not OK,'
            #if lacp_state != 'UP':
            #    wrong_sate += 'lacp-state is not UP,'
            if stp_state == 'MISMATCH':
                mismatch_sate += ' stp_state is MISMATCH '
                nested_print('diagnose_switch_mclag_peer_consistency_check fail due to %s: %s\n' % (host, mismatch_sate))
            elif stp_state != 'OK':
                wrong_sate += ' stp_state is not OK '
                raise Exception('diagnose_switch_mclag_peer_consistency_check fail due to %s: %s\n' % (host, wrong_sate))
            for lcl_port in lcl_ports:
                if lcl_port not in local_ports:
                    missing_lcl_ports.append(lcl_port)
            for rt_port in rt_ports:
                if rt_port not in remote_ports:
                    missing_remote_ports.append(rt_port)
            if len(missing_lcl_ports) != 0:
                raise Exception('diagnose_switch_mclag_peer_consistency_check fail due to %s missing_lcl_ports: %s\n' % (host, missing_lcl_ports))
            if len(missing_remote_ports) != 0:
                raise Exception('diagnose_switch_mclag_peer_consistency_check fail due to %s missing_remote_ports: %s\n' % (host, missing_remote_ports))
    except Exception as msg:
        nested_print(msg)
        status = 0
    except:
        nested_print('diagnose_switch_mclag_peer_consistency_check fail: %s' % sys.exc_info()[0])
        status = 0
    finally:
        return(status)

def parse_stp_inst_list(host, info, ports):
    '''
        this api parse the output of cli "diagnose stp inst list" and return the info of ports in a dictionary
    '''
    func_name = 'parse_stp_inst_list'
    try:
        status_data = {'status':0}
        v = if_string_in_info(info, 'Port Speed Cost Priority Role State Edge STP-Status Loop_Protection')
        if v == 1:
            header = 'Port Speed Cost Priority Role State Edge STP-Status Loop_Protection'
        else:
            header = 'Port Speed Cost Priority Role State HelloTime Flags'
        table_info = {
            'table':info,
            'header':header,
            'delimiter':host,
        }
        t = tableparser.tableParserInPosition(table_info)
        if t['status'] != 1:
            raise Exception('parse_stp_inst_list tableParserInPosition fail')
        ports_list = []
        speed_list = []
        cost_list = []
        priority_list = []
        role_list = []
        state_list = []
        edge_list = []
        stp_status_list = []
        loop_protection_list = []
        parsed_ports_list = t['data']['Port']
        parsed_speed_list = t['data']['Speed']
        parsed_cost_list = t['data']['Cost']
        parsed_priority_list = t['data']['Priority']
        parsed_role_list = t['data']['Role']
        parsed_state_list = t['data']['State']
        for port in ports:
            index = parsed_ports_list.index(port)
            ports_list.append(port)
            speed_list.append(parsed_speed_list[index])
            cost_list.append(parsed_cost_list[index])
            priority_list.append(parsed_priority_list[index])
            role_list.append(parsed_role_list[index])
            state_list.append(parsed_state_list[index])
        stp_inst_dict = {
            'Port':ports_list,
            'Speed':speed_list,
            'Cost':cost_list,
            'Priority':priority_list,
            'Role':role_list,
            'State':state_list,
        }
        status_data = {'status':1, 'data':stp_inst_dict}
    except Exception as msg:
        status_data = {'status':0, 'msg':msg}
    except:
        status_data = {'status':0, 'msg': sys.exc_info()[0]}
    finally:
        return(status_data)

def parse_stp_inst_list_60(info):
    '''
        this api parse the output of cli "diagnose stp inst list" before table and return the info in a dictionary
    '''
    func_name = 'parse_stp_inst_list_60'
    try:
        status_data = {'status':0}
        instance_ID = []
        config_priority = []
        root_priority = []
        root_path_cost = []
        root_remaining_hops = []
        regional_root_priority = []
        regional_root_path_cost = []
        regional_port = []
        mapped_vlans = []
        for line in info.split('\n'):
            line = line.strip()
            match = re.search('Instance ID ([0-9]+)', line)
            if match:
                instance_ID.append(match.group(1))
                continue
            match = re.search('Config +Priority ([0-9]+), VLANs (.*)', line)
            if match:
                config_priority.append(match.group(1))
                mapped_vlans.append(match.group(2))
                continue
            match = re.search('Config +Priority ([0-9]+)', line)
            if match:
                config_priority.append(match.group(1))
                continue
            match = re.search('Root +MAC (.*), Priority (.*), Path Cost ([0-9]+), Remaining Hops ([0-9]+)', line)
            if match:
                root_priority.append(match.group(2))
                root_path_cost.append(match.group(3))
                root_remaining_hops.append(match.group(4))
                continue
            match = re.search('Regional Root +MAC (.*), Priority (.*), Path Cost ([0-9]+), Root Port (.*)', line)
            if match:
                regional_root_priority.append(match.group(2))
                regional_root_path_cost.append(match.group(3))
                regional_port.append(match.group(4))
                continue
            match = re.search('Regional Root +MAC (.*), Priority (.*), Path Cost ([0-9]+)', line)
            if match:
                regional_root_priority.append(match.group(2))
                regional_root_path_cost.append(match.group(3))
                continue
        stp_data = {
           'Instance ID':instance_ID,
           'Switch Priority':config_priority,
           'Root Priority':root_priority,
           'Root Pathcost':root_path_cost,
           'Regional Root Priority':regional_root_priority,
           'Regional Root Path Cost':regional_root_path_cost,
           'Regional Root Port':regional_port,
           'Remaining Hops':root_remaining_hops,
           'Mapped VLANs':mapped_vlans,
        }
        status_data = {'status':1,
           'data':stp_data,
        } 
    except Exception as msg:
        status_data = {'status':0, 'msg':msg}
    except:
        status_data = {'status':0, 'msg': sys.exc_info()[0]}
    finally:
        return(status_data)

def parse_number_from_string(info):
    '''
        this api convert string to number by removing charactors
    '''
    func_name = 'parse_number_from_string'
    try:
        status_data = {'status':0}
        match = re.search('([0-9\.]+)', info)
        if match:
            status_data = {'status':1, 'data':match.group(1)}
    except:
        status_data = {'status':0, 'msg': sys.exc_info()[0]}
    finally:
        return(status_data)

def check_execute_license_status(sku, info):
    '''
        this api parse the output of cli "execute license status" and return 1 if license is installed correctly
    '''
    func_name = 'check_execute_license_status'
    try:
        ret = 1
        enhanced_debugging_Active_line = 0
        FS_SW_LIC_Active_line = 0
        info_list = info.split('\n')
        for line in info_list:
            match = re.search('enhanced-debugging +: Active', line)
            if match:
                enhanced_debugging_Active_line = 1
                continue
            match = re.search('FS-SW-LIC-[0-9]+ +: Active', line)
            if match:
                FS_SW_LIC_Active_line = 1
                continue
        if enhanced_debugging_Active_line == 0:
            ret = 0
        else:
            sku_info = get_asic_type(sku)
            if sku_info['status'] == 1 and sku_info['asic_type'] != 'XCAT' and FS_SW_LIC_Active_line == 0:
                ret = 0
	    if 'SR24D' in sku: #somehow "SR24D" is defined as BROADCOM in get_asic_type, but it should be XCAT
		ret = 1
    except:
        nested_print(sys.exc_info()[0])
        ret = 0
    finally:
        return(ret)

def replace_vlanid_port_in_string(info, vlanid, ports):
    '''
        this api replace VLANID and PORTNAME in string with real info
    '''
    func_name = 'replace_vlanid_port_in_string'
    try:
        ret_info = ''
        vlanid_mod = int(vlanid) % 1024
        if vlanid_mod == 0:
            vlanid_mod = 1024
        port = int(vlanid) % int(ports)
        if port == 0:
            port = int(ports)
        portname = 'port%d' % port
        info_list = info.split('\n')
        action = ''
        for line in info_list:
            match = re.search(r'config switch acl (.*)', line)
            if match:
                action = match.group(1)
                break
        if len(action) == 0:
            raise Exception('Unknown Action')
        for line in info_list:
            if re.search(r'VLANID', line):
                line = re.sub(r'VLANID', str(vlanid_mod), line)
            elif re.search(r'PORTNAME', line):
                if action == 'ingress':
                    line = re.sub(r'PORTNAME', 'ingress-interface %s' % portname, line)
                else:
                    line = re.sub(r'PORTNAME', 'interface %s' % portname, line)
            ret_info += '%s\n' % line
    except Exception as msg:
        nested_print(msg)
    except:
        nested_print(sys.exc_info()[0])
    finally:
        return(ret_info)

def get_group_number_in_range(group, group_start, group_end):
    '''
        this api returns increaging group number in group_start and group_end range
    '''
    func_name = 'get_group_number_in_range'
    try:
        group_ret = int(group) % int(group_end)
        if group_ret == 0:
            group_ret = int(group_end)
        if group_ret < int(group_start):
            group_ret = int(group_start)
    except:
        nested_print(sys.exc_info()[0])
    finally:
        return(group_ret)

def if_mac_in_range(mac, mac_start, mac_end):
    '''
        this api returns 1 if given mac is in the range
    '''
    func_name = 'if_mac_in_range'
    try:
        ret = 1
        mac_octet_list = mac.split(':')
        mac_start_octet_list = mac_start.split(':')
        mac_start_octet_list = mac_end.split(':')

        for index in range(6):
            mac_octet = int(mac_octet_list[index])
            macstart_octet = int(mac_start_octet_list[index])
            macend_octet = int(mac_start_octet_list[index])
            if mac_octet > macend_octet or mac_octet < macstart_octet:
                ret = 0            
                break
    except:
        nested_print(sys.exc_info()[0])
    finally:
        return(ret)

def split_string_into_lines(info, delimiter):
    '''
        this api 
    '''
    func_name = 'split_string_into_small_strings'
    try:
    	status_data = {'status':0}
        info_list = info.split(delimiter)
        status_data = {'status':1, 'data':info_list}
    except:
        status_data = {'status':0, 'msg': sys.exc_info()[0]}
    finally:
        return(status_data)

def modify_output_for_fortiswitch_command_advanced_func(info):
    '''
	this api will remove first two lines and last two lines from the output
    '''
    func_name = 'modify_output_for_fortiswitch_command_advanced_func'
    try:
	status_data = {'status':0}
	final_output_list = []
	output_list = info.split("\n")
	for line in output_list:
	    line = str(line)
	    if(len(line.strip())==0):
		final_output_list.append(line)
		continue
	    match = re.search(r'.*get\s+system\s+status.*', line)			
	    if(match):
		continue
	    else:
		match = re.search(r'Version', line)
		if(match):
			continue
	    	else:
			final_output_list.append(line)
	final_output = "\n".join(final_output_list[1:])
	status_data = {'status':1, 'data':final_output}
    except:
	print(sys.exc_info())
	status_data = {'status':0, 'msg': sys.exc_info()[0]}
    finally:
	return(status_data) 

def modify_output_for_fortiswitch_command_advanced_func2(info,hostname,cli):
    '''
	this api will remove first two lines and last two lines from the output
    '''
    func_name = 'modify_output_for_fortiswitch_command_advanced_func2'
    try:
	status_data = {'status':0}
	final_output_list = []
	output_list = info.split("\n")

	length_of_list = len(output_list)

	start_of_host_line = -1
	flag_for_start_host_line = -1

	for i in range(0,length_of_list):
	    line = output_list[i]
	    line = str(line.strip())
	    regexp1 = ".*"+str(hostname)+".*"+str(cli)+".*"
	    match = re.search(regexp1, line)
	    if(match):
		start_of_host_line = i
		flag_for_start_host_line = 0
		break

	if(start_of_host_line == -1):
	    start_of_host_line = 0
	    #raise Exception('Start of Line with host name and Cli does not found')
	    

	for j in range(start_of_host_line,length_of_list):
	    line = output_list[j]
	    line = str(line.strip())
	    if(len(line.strip())==0):
		final_output_list.append(line)
		continue
	    match = re.search(r'.*get\s+system\s+status.*', line)			
	    if(match):
		continue
	    else:
		match = re.search(r'Version', line)
		if(match):
			continue
	    	else:
			final_output_list.append(line)
	#final_output = "\n".join(final_output_list)

	temp_string = "\n"

	if(flag_for_start_host_line == 0):
		final_output = temp_string.join(final_output_list)
	elif(flag_for_start_host_line == -1):
		final_output = temp_string.join(final_output_list[1:])
	else:
		raise Exception('flag for start_host_line is not 0 or -1')

	status_data = {'status':1, 'data':final_output}
		
    except:
	print(sys.exc_info())
	status_data = {'status':0, 'msg': sys.exc_info()[0]}
    finally:
	return(status_data) 


	
def parse_bpduguard_status(host, info):
    '''
        this api parse the output of cli "diagnose bpdu-guard display status" and return the info of ports in a dictionary
    '''
    func_name = 'parse_bpduguard_status'
    try:
        status_data = {'status':0}
        v = if_string_in_info(info, 'Portname State Status Timeout(m) Count Last-Event')
        if v == 1:
            header = 'Portname State Status Timeout(m) Count Last-Event'
        else:
            header = 'Portname Status Timeout(m) Count Last-Event'
        table_info = {
            'table':info,
            'header':header,
            'delimiter':host,
        }
        t = tableparser.tableParserInPosition(table_info)
        if t['status'] != 1:
            raise Exception('parse_bpduguard_status tableParserInPosition fail')
        status_data = {'status':1, 'data':t['data']}
    except Exception as msg:
        status_data = {'status':0, 'msg':msg}
    except:
        status_data = {'status':0, 'msg': sys.exc_info()[0]}
    finally:
        return(status_data)

def sleep_with_message(sleeptime, interval=10):
    '''
        sleep and display message
    '''
    func_name = 'sleep_with_message'
    try:
        sleeptime_int = int(sleeptime)
        sleep_range, sleep_remain = divmod(sleeptime_int, interval)
        if sleep_range == 0:
            nested_print('\tPlease Wait for %s seconds ....' % sleep_remain)
            time.sleep(sleep_remain)
        else:
            for index in range(0, sleep_range):
                nested_print('\tPlease Wait for %s seconds ....' % interval)
                time.sleep(interval)
            if sleep_remain != 0:
                nested_print('\tPlease Wait for %s seconds ....' % sleep_remain)
                time.sleep(sleep_remain)
    except:
        status_data = {'status':0, 'msg': sys.exc_info()[0]}
    finally:
        return

def merge_lists(list1, list2):
    '''
        returns merged list
    '''
    func_name = 'merge_lists'
    try:
        merged_list = list1 + list2
    except:
        nested_print(sys.exc_info()[0])
        merged_list = []
    finally:
        return(merged_list)


def exrtact_ip_octets(ip_str):
    '''
	this function will return all octets of ip address
    '''
    func_name = 'exrtact_ip_octets'
    try:
	status_data = {'status':0}
	l = re.split('(.*)\.(.*)\.(.*)\.(.*)',ip_str)
	lr = l[1:-1]
	status_data = {'status':1, 'data':lr}
    except Exception as msg:
	status_data = {'status':0, 'msg':msg}
    except:
	status_data = {'status':0, 'msg':sys.exc_info()[0]}
    finally:
	return(status_data)


def increment_ip_address(ip_str,increment_step):
    '''
	this function will increment the ip address based on provided step
    '''
    func_name = 'increment_ip_address'
    try:
	status_data = {'status':0}
	l = re.split('(.*)\.(.*)\.(.*)\.(.*)',ip_str)
	#logger.console(l)
	lr = l[1:-1]
	#logger.console(lr)
	in_step = re.split('(.*)\.(.*)\.(.*)\.(.*)',increment_step)
	in_step_list = in_step[1:-1]
	#logger.console(in_step_list)
	y = []
	temp = int(lr[0]) + int(in_step_list[0])
	#logger.console(temp)
	if(temp > 255):
	    raise Exception('Highest Octet is greater than 255, Fails')
	y.append(temp)
	#logger.console("--------------"+str(y))
	temp = int(lr[1]) + int(in_step_list[1])
	if(temp > 255):
	    temp = 0
	    y[0] = y[0] + 1
	    if(y[0] > 255 ):
		raise Exception('Highest Octet is greater than 255, Fails')
	y.append(temp)
	#logger.console("--------------"+str(y))
	temp = int(lr[2]) + int(in_step_list[2])
	if(temp > 255):
	    temp = 0
	    y[1] = y[1] + 1
	    if(y[1] > 255):
	        y[1] = 0
	        y[0] = y[0] + 1
		if(y[0] > 255):
		    raise Exception('Highest Octet is greater than 255, Fails')
	y.append(temp)
	#logger.console("--------------"+str(y))
	temp = int(lr[3]) + int(in_step_list[3])
	if(temp > 255):
	    temp = 0
	    y[2] = y[2] + 1
    	    if(y[2] > 255):
	        y[2] = 0
		y[1] = y[1] + 1
		if(y[1] > 255):
		    y[1] = 0
		    y[0] = y[0] + 1
	       	    if(y[0] > 255):
		        raise Exception('Highest Octet is greater than 255, Fails') 
	y.append(temp)
	#logger.console(y)
	temp_str = str(y[0])+"."+str(y[1])+"."+str(y[2])+"."+str(y[3])
	#logger.console(temp_str)
	status_data = {'status':1, 'data':temp_str}
    except Exception as msg:
	status_data = {'status':0, 'msg':msg}
    finally:
	return(status_data)
		
	
	
	



def modify_switch_configuration_for_debug(info):
    '''
	this function will remove the data in between line1 and line2
	line1 should come first, then line2
    '''
    func_name = 'modify_switch_configuration_for_debug'
    try:
	status_data = {'status':0}
	info = info.splitlines()
	temp_str = "\n"
	temp_flag_1 = 0
	for line in info:
	    if re.search(r'config switch acl service custom', line):
		temp_flag_1 = 1
		continue
	    elif temp_flag_1 == 1:
		if re.search(r'set protocol IP', line):
		    temp_flag_1 = 0     
		    continue
	    else:
		temp_str = temp_str + line + str("\n")
	status_data = {'status':1, 'data':temp_str}
    except Exception as msg:
	status_data = {'status':0, 'msg':msg}
    finally:
	return(status_data)


def modify_switch_configuration_for_debug2(info):
    '''
        this function will remove the data in between line1 and line2
        line1 should come first, then line2
    '''
    func_name = 'modify_switch_configuration_for_debug2'
    try:
        status_data = {'status':0}
        info = info.splitlines()
        temp_str = "\n"
        temp_flag_1 = 0
        temp_flag_2 = 0
        temp_flag_3 = 0
        for line in info:
            if re.search(r'config switch acl service custom', line):
                temp_flag_1 = 1
                continue
            elif re.search(r'config switch stp instance', line):
                temp_flag_2 = 1
                continue
            elif re.search(r'config switch physical-port', line):
                temp_flag_3 = 1
                continue
            elif temp_flag_1 == 1:
                if re.search(r'set protocol IP', line):
                    temp_flag_1 = 0
                    continue
            elif temp_flag_2 == 1:
                if re.search(r'internal', line):
                    temp_flag_2 = 0
                    continue
            elif temp_flag_3 == 1:
                if re.search(r'internal', line):
                    temp_flag_3 = 0
                    continue
            else:
                temp_str = temp_str + line + str("\n")
        status_data = {'status':1, 'data':temp_str}
    except Exception as msg:
        status_data = {'status':0, 'msg':msg}
    finally:
        return(status_data)

def get_random_vlan_number():
    '''
        this function generate ramdom_vlan_number between 900 to 999
    '''
    return(random.randint(900,999))

def get_snmp_interface_counter(info):
    '''
        this function parses info and return snmp interface counter value
        info format: iso.3.6.1.2.1.16.1.1.1.18.2 = Counter32: 8373
        return value should be an integer: 8373
    '''
    ret = 0
    try:
        match = re.search(': ([0-9]+)', info)
        if match:
            ret = int(match.group(1))
    except:
        logger.console(sys.exc_info()[0])
    finally:
        return(ret)

def create_system_id_from_mac_addr(str):
    '''
	this function will create string like 0001.0001.0001 from mac
	00:01:00:01:00:01
    '''
    func_name = 'create_system_id_from_mac_addr'
    try:
	status_data = {'status':0}
	l = str.split(":")
	temp_str = l[0]+l[1]+"."+l[2]+l[3]+"."+l[4]+l[5]
	status_data = {'status':1, 'data':temp_str}
    except Exception as msg:
	status_data = {'status':0, 'msg':msg}
    except:
	status_data = {'status':0, 'msg':sys.exc_info()[0]}
    finally:
	return(status_data)

def compare_two_mac_address(mac1,mac2):
    '''
	mac address should be in 90:6c:ac:6d:d6:9b this format
	this function will compare two mac address , if they are equal it will return 0 
	if mac1 > mac2 , then it will return 1 
	if mac2 > mac1 , then it will return 2
    '''
    func_name = 'compare_two_mac_address'
    try:
	status_data = {'status':0}
	l1 = mac1.split(":")
	l2 = mac2.split(":")
	flag = 0 
	for x in range(6):
		i1 = l1[x]
		i2 = l2[x]
		d1 = int(i1,16)
		d2 = int(i2,16)
		if(d1 == d2):
			continue
		elif(d1 > d2):
			flag = 1
			break
		elif(d2 > d1):
			flag = 2
			break	
	status_data = {'status':1, 'data':flag}
    except Exception as msg:
	status_data = {'status':0, 'msg':msg}
    except:
	status_data = {'status':0, 'msg':sys.exc_info()[0]}
    finally:
	return(status_data)

def check_daemon_cpu_usage(info, daemon, usage):
    '''
        return 1 if the deamon cpu usage is less than given usage. Otherwise return 0
        info should be in format of:
Run Time:  0 days, 1 hours and 2 minutes
2U, 11S, 87I; 487T, 276F
      fortilinkd      853      S       1.1     1.7
          fsmgrd      854      S       0.9     1.9
        lldpmedd      849      S       0.9     1.8
          newcli     1532      R <     0.7     1.6
            lpgd      840      S       0.3     1.6
            dmid      850      S       0.3     1.5
            lfgd      822      S       0.3     1.5
            stpd      839      S       0.1     1.7
       forticron      821      R       0.1     1.7
          alertd      824      S       0.1     1.6
         pyfcgid      816      S       0.0     6.3
         cmdbsvr      682      S       0.0     2.5
          newcli     1449      S <     0.0     2.3
          httpsd      817      S       0.0     2.3
 initXXXXXXXXXXX        1      S       0.0     2.2
     ipconflictd      846      S       0.0     2.1
       eap_proxy      852      S       0.0     1.8
           snmpd     1528      S       0.0     1.8
           authd      851      S       0.0     1.8
         miglogd      818      S       0.0     1.8
    '''
    func_name = 'check_daemon_cpu_usage'
    try:
        status_data = {'status':0}
        for deamon_info in info.split('\n'):
            match = re.search('%s\s+[0-9]+\s+(.*)\s+(.*)\s+(.*)' % daemon, deamon_info)
            if match:
                real_cpu_usage = float(match.group(2))
                expect_cpu_usage = float(usage)
                logger.console('\treal_cpu_usage=%s, expect_cpu_usage=%s' % (real_cpu_usage, expect_cpu_usage))
                if real_cpu_usage > expect_cpu_usage:
                    status_data = {'status':1, 'usage':0}
                else:
                    status_data = {'status':1, 'usage':1}
                break
    except Exception as msg:
        status_data = {'status':0, 'msg':msg}
    except:
        status_data = {'status':0, 'msg':sys.exc_info()[0]}
    finally:
        return(status_data)

def get_vm_inc_mac(info, inc):
    '''
        return mac of VM INC MAC address
    '''
    func_name = 'get_vm_inc_mac'
    try:
        status_data = {'status':0}
        for line in info.split('\n'):
            match = re.search('%s +.*HWaddr ([0-9a-z:]+)' % inc, line)
            if match:
                status_data = {'status':1, 'mac':match.group(1)}
                break
    except Exception as msg:
        status_data = {'status':0, 'msg':msg}
    except:
        status_data = {'status':0, 'msg':sys.exc_info()[0]}
    finally:
        return(status_data)

def get_managed_down_switches_number(info):
    '''
        return the number of Managed-Switches Down number
    '''
    func_name = 'get_managed_down_switches_number'
    try:
        status_data = {'status':0}
        for line in info.split('\n'):
            match = re.search('Managed-Switches: [0-9]+ UP: [0-9]+ DOWN: ([0-9]+)', line)
            if match:
                status_data = {'status':1, 'down_switches_number':match.group(1)}
                break
    except Exception as msg:
        status_data = {'status':0, 'msg':msg}
    except:
        status_data = {'status':0, 'msg':sys.exc_info()[0]}
    finally:
        return(status_data)

def compare_two_ip_addresses(ip1,ip2):
    '''
        ip addresses should be in X.X.X.X Format
        this function will compare Two IP Address, [ It will check Each Octet From Left To Right ]
        If they are Equal It will Return 0
        If ip1 > ip2 , It Will Return 1
        If ip2 > ip1, It Will Return 2
    '''
    func_name = 'compare_two_ip_addresses'
    try:
        status_data = {'status':0}
        l1 = ip1.split(".")
        l2 = ip2.split(".")
        flag = 0
        for x in range(4):
                i1 = l1[x]
                i2 = l2[x]
                d1 = int(i1,10)
                d2 = int(i2,10)
                if(d1 == d2):
                        continue
                elif(d1 > d2):
                        flag = 1
                        break
                elif(d2 > d1):
                        flag = 2
                        break
        status_data = {'status':1, 'data':flag}
    except Exception as msg:
        status_data = {'status':0, 'msg':msg}
    except:
        status_data = {'status':0, 'msg':sys.exc_info()[0]}
    finally:
        return(status_data)

def mac_to_ipv6_linklocal(mac):
    '''
        return ipv6 linklocal MAC 
        mac is in the format of 08:5b:0e:e9:eb:79
    '''
    func_name = 'mac_to_ipv6_linklocal'
    try:
        # Remove the most common delimiters; dots, dashes, etc.
        mac_value = int(mac.translate(None, ' .:-'), 16)

        # Split out the bytes that slot into the IPv6 address
        # XOR the most significant byte with 0x02, inverting the 
        # Universal / Local bit
        high2 = mac_value >> 32 & 0xffff ^ 0x0200
        high1 = mac_value >> 24 & 0xff
        low1 = mac_value >> 16 & 0xff
        low2 = mac_value & 0xffff
        ipv6_linklocal = 'fe80::{:x}:{:x}ff:fe{:x}:{:x}'.format(high2, high1, low1, low2)
        status_data = {'status':1, 'data':ipv6_linklocal}
    except Exception as msg:
        status_data = {'status':0, 'msg':msg}
    except:
        status_data = {'status':0, 'msg':sys.exc_info()[0]}
    finally:
        return(status_data)

def mac_to_ipv6_mac(mac):
    '''
        return ipv6 MAC
        mac is in the format of 08:5b:0e:e9:eb:79
    '''
    func_name = 'mac_to_ipv6_linklocal'
    try:
        # Remove the most common delimiters; dots, dashes, etc.
        mac_value = int(mac.translate(None, ' .:-'), 16)

        # Split out the bytes that slot into the IPv6 address
        # XOR the most significant byte with 0x02, inverting the
        # Universal / Local bit
        high2 = mac_value >> 32 & 0xffff ^ 0x0200
        high1 = mac_value >> 24 & 0xff
        low1 = mac_value >> 16 & 0xff
        low2 = mac_value & 0xffff
        ipv6_linklocal = '2001:db8:1:0:{:x}:{:x}ff:fe{:x}:{:x}'.format(high2, high1, low1, low2)
        status_data = {'status':1, 'data':ipv6_linklocal}
    except Exception as msg:
        status_data = {'status':0, 'msg':msg}
    except:
        status_data = {'status':0, 'msg':sys.exc_info()[0]}
    finally:
        return(status_data)

def modify_prometheus_config_file(filename, vm_ip, mgmt_ip):
    '''
        this api modify prometheus_config_file by replacing VM_IP and MGMT_IP with given value
    '''
    try:
        status_data = {'status':0}
        new_filedata = ''
        fname, fextension = os.path.splitext(filename)
        base_file = fname + '.base'
        if not os.path.isfile(filename):
            raise Exception('Invalid yml filename: %s' % filename)
        if not os.path.isfile(base_file):
            raise Exception('Invalid base filename: %s' % base_file)
        fid = open(base_file, 'r')
        filedata = fid.read()
        fid.close()
        filelines = filedata.split('\n')
        for line in filelines:
            line = re.sub('VM_IP', vm_ip, line)
            line = re.sub('MGMT_IP', mgmt_ip, line)
            new_filedata += '%s\n' % line
        fid = open(filename, 'w')
        fid.write(new_filedata)
        fid.close()
        status_data = {'status':1}
    except Exception as msg:
        logger.console('%s: %s' % (datetime.datetime.now(), msg))
    except:
        logger.console('%s: %s' % (datetime.datetime.now(), sys.exec_info()[0]))
    finally:
        return(status_data)

def get_everage_snmp_performence_time(info):
    '''
        this api returns everage snmp performence time
    '''
    try:
        status_data = {'status':0}
        catched_lines = 0
        everage_performence_time = 0.0
        performence_time_summary = 0.0
        info_lines = info.split('\n')
        for line in info_lines:
            if re.search('Request timeout', line):
                raise Exception('Error getting target: Request timeout')
        for line in info_lines:
            match = re.search('Scrape of target.*took ([0-9.]+) seconds', line)
            if match:
                performence_time_summary += float(match.group(1))
                catched_lines += 1
        if catched_lines != 0:
            everage_performence_time = performence_time_summary / catched_lines
            status_data = {'status':1, 'time':everage_performence_time}
    except Exception as msg:
        logger.console('%s: %s' % (datetime.datetime.now(), msg))
    except:
        logger.console('%s: %s' % (datetime.datetime.now(), sys.exec_info()[0]))
    finally:
        return(status_data)

def get_snmp_sysobjectId(info):
    '''
        this api returns switch's sysobjectId
    '''
    try:
        info_list = info.split('.')
        sysobjectId = info_list[-1]
    except Exception as msg:
        logger.console('%s: %s' % (datetime.datetime.now(), msg))
    except:
        logger.console('%s: %s' % (datetime.datetime.now(), sys.exec_info()[0]))
    finally:
        return(sysobjectId)

def string_to_dict(str):
    '''
        this api returns a dictionary from given string. The format of the string has to be: str1,str2,str3. Will use ',' to split the string
    '''
    try:
        str_list = str.split(',')
    except Exception as msg:
        logger.console('%s: %s' % (datetime.datetime.now(), msg))
    except:
        logger.console('%s: %s' % (datetime.datetime.now(), sys.exec_info()[0]))
    finally:
        return(str_list)

def get_switch_sysObjectId(model):
    '''
        this api returns switch sysObjectId
    '''
    try:
        sysObjectId = 0
        sysObjectIds = {
            'FSR_112D_POE':'1121',
            'FSR_124D':'1243',
            'FSW_1024D':'10241',
            'FSW_1048D':'10481',
            'FSW_1048E':'10482',
            'FSW_108D_POE':'1081',
            'FSW_108E':'1082',
            'FSW_108E_POE':'1083',
            'FSW_108E_FPOE':'1084',
            'FSW_124D':'1241',
            'FSW_124D_POE':'1242',
            'FSW_124E':'1244',
            'FSW_124E_FPOE':'1246',
            'FSW_24E_POE':'1245',
            'FSW_224D_FPOE':'2242',
            'FSW_224D_POE':'2241', 
            'FSW_224D_POE':'2241',
            'FSW_224E':'2243',
            'FSW_224E_POE':'2244',
            'FSW_248D':'2483',
            'FSW_248D_FPOE':'2482',
            'FSW_248D_POE':'2481',
            'FSW_248E_FPOE':'2484',
            'FSW_3032D':'30321',
            'FSW_424D':'4241',
            'FSW_424D_FPOE':'4243',
            'FSW_424D_POE':'4242',
            'FSW_448D':'4482',
            'FSW_448D_FPOE':'4483',
            'FSW_448D_POE':'4484',
            'FSW_524D':'5242',
            'FSW_524D_FPOE':'5241',
            'FSW_548D':'5482',
            'FSW_548D_FPOE':'5481',
            'FSW_3032E':'30322',
            'FSW_148E':'1247',
            'FSW_148E_POE':'1248',
        }
        if model in sysObjectIds:
            sysObjectId = sysObjectIds[model]
    except:
        logger.console('%s: %s' % (datetime.datetime.now(), sys.exec_info()[0]))
    finally:
        return(sysObjectId)

def get_devices_in_imagePath(imagePath):
    '''
        this api parses imagePath and returns a list of devices
        Format of the imagePath: [{"sn":"FS1D243Z14000063","path":"1534454378-3\/FSW_1024D-v6-build0036-FORTINET.out","dev1":"dev2"},{"sn":"S524DF4K16000052","path":"1534454378-3\/FSW_524D_FPOE-v6-build0036-FORTINET.out","dev3":"dev1"}]
    '''
    try:
        devices = []
        imagePath = fix_unicode(imagePath)
        for image_info in imagePath:
            for image_info_key in image_info.keys():
                if re.search('dev[0-9]+', image_info_key):
                    devices.append(image_info[image_info_key])
    except:
        logger.console('%s: %s' % (datetime.datetime.now(), sys.exec_info()[0]))
    finally:
        return(devices)

def get_image_in_imagePath(host, imagePath):
    '''
        this api parses imagePath and returns a list of images
        imagePath in the same format of get_devices_in_imagePath 
    '''
    try:
        status_data = {'status':0}
        imagePath = fix_unicode(imagePath)
        for image_info in imagePath:
            if image_info['sn'] == host:
                status_data = {'status':1,'image':image_info['path']}
    except:
        logger.console('%s: %s' % (datetime.datetime.now(), sys.exec_info()[0]))
    finally:
        return(status_data)

def get_image_and_type_in_imagePath(host, imagePath):
    '''
        this api parses imagePath and returns a list of images
        imagePath in the same format of get_devices_in_imagePath
    '''
    try:
        status_data = {'status':0, 'host':host, 'imagePath':imagePath}
        imagePath = fix_unicode(imagePath)
        for image_info in imagePath:
            if image_info['sn'] == host:
                if re.search('^v[0-9]-build[0-9]+-FORTINET\.out', image_info['path']):
                    image_type = "standard"
                else:
                    image_type = "private"
                status_data = {'status':1,'image':image_info['path'], 'type':image_type}
    except:
        logger.console('%s: %s' % (datetime.datetime.now(), sys.exec_info()[0]))
    finally:
        return(status_data)

def get_infra_image_type(image):
    '''
        this api parses image and returns either standard or private
    '''
    try:
        if re.search('(^FSW_.*|^v[0-9])-build[0-9]+-FORTINET\.out', image):
            image_type = "standard"
        else:
            image_type = "private"
    except:
        logger.console('%s: %s' % (datetime.datetime.now(), sys.exec_info()[0]))
    finally:
        return(image_type)

def get_device_in_ImagePath_only(host, topo, imagePath):
    '''
        this api return the host that is in imagePath dict. But not in topo
        imagePath in the same format of get_devices_in_imagePath
    '''
    try:
        status_data = 0
        find_host_in_imagePath = 0
        topo = fix_unicode(topo)
        imagePath = fix_unicode(imagePath)
        for image_info in imagePath:
            if image_info['sn'] == host:
                find_host_in_imagePath = 1
                break
        if find_host_in_imagePath == 0:
            raise Exception('Unable to find host %s from imagePath' % host)
        for key in image_info.keys():
            if re.search('dev[0-9]+', key) and image_info[key] not in topo.keys():
                status_data = 1
                break
    except Exception as msg:
        logger.console('\t%s: %s' % (datetime.datetime.now(), msg))
    except:
        logger.console('\t%s: %s' % (datetime.datetime.now(), sys.exec_info()[0]))
    finally:
        return(status_data)

def unicode_to_string(myIn):
    '''
    This python API converts a unicode to string.
    '''
    tcs = str(myIn)
    return(tcs)

def string_to_float(myIn):
    '''
    This python API converts a string to float.
    '''
    tcs = float(myIn)
    return(tcs)

def unicode_to_float(myIn):
    '''
    This python API converts a unicode to float.
    '''
    tcs1 = unicode_to_string(myIn)
    tcs = string_to_float(tcs1)
    return(tcs)


def fix_unicode(data):
    '''
        this api convert unicode data to original data type: string, list or dictionary
    '''
    try:
        if isinstance(data, unicode):
            str_data = data.encode('ascii')
            data = json.loads(str_data)
    except:
        logger.console('Unexpected error: %s' % sys.exc_info()[0])
    finally:
        return data

def get_image_buildnpi_tag_name(release, build):
    '''
        this api return ImageBuildNPI and ImageTag based on release and build info
    '''
    try:
        status_data = {'status':0}
        imageBuildNPI = 'unknown'
        imageTag = 'unknown'
        if re.search('v6', release):
            imageBuildNPI = 'fswos_6-0_fsw_npi'
            match = re.search('build([0-9]+)', build)
            if match:
                imageTag = 'build_tag_' + match.group(1)
        elif re.search('v3', release):
            imageBuildNPI = 'fswos_3_fsw_npi'
            imageTag = build
        if imageBuildNPI != 'unknown' and imageTag != 'unknown':
            status_data = {'status':1, 'imageBuildNPI':imageBuildNPI, 'imageTag':imageTag}
    except:
        logger.console('Unexpected error: %s' % sys.exc_info()[0])
    finally:
        return(status_data)

def change_key_value_map(dev_pairs):
    '''
        this api return change key and value map. value becomes to kay and key becomes value
    '''
    try:
        vdev_pairs = {}
        for ddev in dev_pairs.keys():
            vdev = dev_pairs[ddev]
            vdev_pairs[vdev] = ddev
        vdev_pairs_list = [vdev_pairs]
    except:
        logger.console('Unexpected error: %s' % sys.exc_info()[0])
    finally:
        return(vdev_pairs_list)

def link_type_allow(vtype, dtype):
    '''
        this api return 1 if vtype and dtype allows. Otherwise return 0
        vtype  |  dtype  | return
        -------+---------+---------
        ICL    |  ICL    | 1
        PIM    |  ICL    | 1
        Gig    |  ICL    | 1
        ICL    |  PIM    | 0
        PIM    |  PIM    | 1
        Gig    |  PIM    | 1
        ICL    |  Gig    | 0
        PIM    |  Gig    | 0
        Gig    |  Gig    | 1
    '''
    try:
        ret = 0
        if vtype != 'GigabitEthernet' and vtype != 'PIM' and vtype != 'ICL':
            raise Exception('Unknown vtype value: %s' % vtype)
        if dtype != 'GigabitEthernet' and dtype != 'PIM' and dtype != 'ICL':
            raise Exception('Unknown dtype value: %s' % dtype)
        if vtype == 'ICL' and dtype == 'ICL':
            ret = 1
        elif vtype == 'PIM' and dtype == 'ICL':
            ret = 1
        elif vtype == 'GigabitEthernet' and dtype == 'ICL':
            ret = 1
        elif vtype == 'ICL' and dtype == 'PIM':
            ret = 0
        elif vtype == 'PIM' and dtype == 'PIM':
            ret = 1
        elif vtype == 'GigabitEthernet' and dtype == 'PIM':
            ret = 1
        elif vtype == 'ICL' and dtype == 'GigabitEthernet':
            ret = 0
        elif vtype == 'PIM' and dtype == 'GigabitEthernet':
            ret = 0
        elif vtype == 'GigabitEthernet' and dtype == 'GigabitEthernet':
            ret = 1
    except Exception as msg:
        logger.console(msg)
    except:
        logger.console('Unexpected error: %s' % sys.exc_info()[0])
    finally:
        return(ret)

def check_device_lldp_neighbor(device, tb_info, lldp_neighbor_summary):
    '''
        this api checks device lldp_neighbor return a list with miss-matching links
    '''
    try:
        status_data = {'status':0}
        missmatch_links = []

        # parse lldp_neighbor_summary table
        header = 'Portname Status Device-name TTL Capability MED-type Port-ID'
        table_info = {
            'table':lldp_neighbor_summary,
            'header':header,
        }
        t = tableparser.tableParserInPosition(table_info)
        if t['status'] != 1:
            raise Exception('parsing lldp_neighbor_summary tableParserInPosition fail')
        portname_list = t['data']['Portname']
        Status_list = t['data']['Status']
        devicename_list = t['data']['Device-name']
        PortID_list = t['data']['Port-ID']

        # get connections
        tb_connections = tb_info['connections']
        for connection in tb_connections:
            port_pair = tb_connections[connection]['link'].split('-')
            if len(port_pair) == 1:
               first, second = port_pair[0].split(',')
               first_name, first_port = first.split(':')
               second_name, second_port = second.split(':')
               #if re.search(first_name, device):
               if device == first_name:
                   neighbor = tb_info[second_name]['hostname']
                   list_index = portname_list.index(first_port)
                   lldp_device_portname = portname_list[list_index]
                   lldp_device_portstatus = Status_list[list_index]
                   lldp_neighbor = devicename_list[list_index]
                   lldp_neighbor_port = PortID_list[list_index]
                   if lldp_device_portname != first_port or lldp_device_portstatus != 'Up' or lldp_neighbor != neighbor or lldp_neighbor_port != second_port:
                       missmatch_links.append(connection)
                       logger.console('\tConnection %s (%s) check fail' % (connection, port_pair))
                   else:
                       logger.console('\tConnection %s (%s) check complete' % (connection, port_pair))
               #elif re.search(second_name, device):
               elif device == second_name:
                   neighbor = tb_info[first_name]['hostname']
                   list_index = portname_list.index(second_port)
                   lldp_device_portname = portname_list[list_index]
                   lldp_device_portstatus = Status_list[list_index]
                   lldp_neighbor = devicename_list[list_index]
                   lldp_neighbor_port = PortID_list[list_index]
                   if lldp_device_portname != second_port or lldp_device_portstatus != 'Up' or lldp_neighbor != neighbor or lldp_neighbor_port != first_port:
                       missmatch_links.append(connection)
                       logger.console('\tConnection %s (%s) check fail' % (connection, port_pair))
                   else:
                       logger.console('\tConnection %s (%s) check complete' % (connection, port_pair))
            elif len(port_pair) == 3:
               first_name, first_port = port_pair[0].split(':')
               second, dummy = port_pair[1].split(',')
               second_name, second_port = second.split(':')
               if re.search(device, first_name):
                   neighbor = tb_info[second_name]['hostname']
                   list_index = portname_list.index(first_port)
                   lldp_device_portname = portname_list[list_index]
                   lldp_device_portstatus = Status_list[list_index]
                   lldp_neighbor = devicename_list[list_index]
                   lldp_neighbor_port = PortID_list[list_index]
                   if lldp_device_portname != first_port or lldp_device_portstatus != 'Up' or lldp_neighbor != neighbor or lldp_neighbor_port != second_port:
                       missmatch_links.append(connection)
                       logger.console('\tConnection %s (%s) check fail' % (connection, port_pair))
                   else:
                       logger.console('\tConnection %s (%s) check complete' % (connection, port_pair))
            else:
               logger.console('\tConnection %s (%s) check fail' % (connection, port_pair))
               missmatch_links.append(connection)
        if len(missmatch_links) != 0:
            status_data = {'status':0, 'msg':missmatch_links}
        else:
            status_data = {'status':1}

    except Exception as msg:
        status_data = {'status':0, 'msg':msg}
    except:
        status_data = {'status':0, 'msg': sys.exc_info()[0]}
    finally:
        return(status_data)

def check_dump_network_upgrade_status(device, info):
    '''
        return 1 if the Status of the device is (0/100/100)
        info is a dictionary
    '''
    func_name = 'check_dump_network_upgrade_status'
    try:
        status_data = {'status':0}
        info = fix_unicode(info)
        devices = info['Device']
        Status = info['Next-boot']
        if not device in devices:
            raise Exception("device=%s is missing in the table=%s" % (device, info))
        device_index = devices.index(device)
        device_status = Status[device_index]
	match = re.search('([0-9]+)/([0-9]+)/([0-9]+)', device_status)
        if not match:
            raise Exception('parse dump network-upgrade status Fial: %s' % device_status)
        if match.group(1) != '0' or match.group(2) != '100' or match.group(3) != '100':
            status_data = {'status':1, 'data':0}
        else:
            status_data = {'status':1, 'data':1}
    except Exception as msg:
        status_data = {'status':0, 'msg':msg}
    except:
        status_data = {'status':0, 'msg':sys.exc_info()[0]}
    finally:
        return(status_data)

def get_exclude_mantis(root, valid_dirs):
    '''
    This python code returns all excluded mantis in all excoude files
    '''
    func_name = 'get_exclude_mantis'
    try:
        status_data = {'status':0}
        if not os.path.exists(root):
            raise Exception("invalid root dir=%s" % root)
        # read all files in directory and subdirectories
        mantis_dict = {}
        for root, dirs, files in os.walk(root):
            project_name = root.rsplit('/')[-1]
            if project_name not in valid_dirs:
                continue
            if project_name not in mantis_dict:
                mantis_dict[project_name] = {}
            for file_name in files:
                print('root=%s, filename=%s' % (root, file_name))
                mantis_dict[project_name][file_name] = []
                fd = open(os.path.join(root, file_name), "r")
                excludes = fd.read()
                fd.close
                exclude_lines = excludes.split('\n')
                for line in exclude_lines:
                    match = re.search(r'(m|M)antis: +([0-9]+)', line)
                    if match:
                        mantis_dict[project_name][file_name].append(match.group(2))
        status_data = {'status':1, 'mantis':mantis_dict}
    except:
        e = '%s, Unexpected error: %s' % (func_name, sys.exec_info()[0])
        status_data = {'status':0, 'msg':e}
    finally:
        return(status_data)

def catenate_strings(*args):
    '''
    This python code catenate all given string
    '''
    func_name = 'catenate_strings'
    strings = ''
    try:
        for string in args:
            if len(string) != 0:
                strings += '%s\n\t\t' % string
    except:
        nested_print('%s, Unexpected error: %s' % (func_name, sys.exec_info()[0]))
    finally:
        return(strings)

def add_minutes_to_time(time1, timedelta_minute):
    '''
        this python api will add time provided as timedelta to given time time1
    '''
    try:		
        status_data = {'status':0}
        converted_time  = (datetime.strptime(time1, "%H:%M %Y/%m/%d") + timedelta(minutes=int(timedelta_minute))).strftime("%H:%M %Y/%m/%d")
        status_data = {'status':1, 'data':converted_time}
    except ValueError as ve:
        logger.console('ERROR : %s' % ve)	
        status_data = {'status':0, 'msg':sys.exc_info()[0]}
    finally:
        return(status_data)
     		
def check_systemtime_has_passed(time1, time2):
    '''
        this python api will check if time2 is greater than time1(system time)
    '''
    try: 			
        status_data = {'status':0}
        time1  =  datetime.strptime(time1, '%H:%M %Y/%m/%d')
        time2  =  datetime.strptime(time2, '%H:%M %Y/%m/%d')
        if time2 > time1:
            status_data = {'status':1, 'result':0}
        else:
            status_data = {'status':1, 'result':1}
    except:
        status_data = {'status':0, 'msg':sys.exc_info()[0]}
    finally:
        return(status_data)
       
if __name__ == "__main__":
    table = '''
untrusted ports       : port2 port3 port4 port5 port6 port7 port8 port9 port10 port11
                 port12 port13 port14 port15 port16 port17 port18 port19 port20 port22
                 port23 port24 port25 port26 port27 port28 TRUNK_1
'''
    t = if_string_in_info(table, 'port22 ')
    print(t)
