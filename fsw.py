from misc import *
import pdb

"""
   FortiSwitch class for all switch related methods
"""
class fsw(object):

    def get_svi_mac(self, info):
        '''
        This python API parses and return svi mac address
        '''
        func_name = 'get_svi_mac'
        try:
            status_data = {'status':0}
            t_info = re.sub(r'(\\r)+', '', info, re.DOTALL)
            svi_mac = 0
            for line in t_info.split('\n'):
                nested_print(line)
                s = re.search(r'hw_addr=(([0-9a-f][0-9a-f]:){5}[0-9a-f][0-9a-f])', line, re.U)
                if s:
                    svi_mac = s.group(1)
                    break
            if svi_mac != 0:
                status_data = {
                    'status':1,
                    'svi_mac':svi_mac,
                }
        except:
            e = '%s, Unexpected error: %s' % (func_name, sys.exc_info()[0])
            status_data = {'status':0, 'msg':e}
        finally:
            return(status_data)

    def parse_system_status(self, info):
        '''
        This python API parses and return system status in a dictionary format
        '''
        func_name = 'parse_system_status'
        try:
            status_data = {'status':0}
            t_info = re.sub(r'(\\r)+', '', info, re.DOTALL)
            system_status = {}
            for line in t_info.split('\n'):
                s = re.search(r'(.*):\s(.*)', line, re.U)
                if s:
                    title = s.group(1).strip()
                    value = s.group(2).strip()
                    system_status[title] = value
            if system_status != {}:
                status_data = {
                    'status':1,
                    'system_status':system_status,
                }
        except:
            e = '%s, Unexpected error: %s' % (func_name, sys.exc_info()[0])
            status_data = {'status':0, 'msg':e}
        finally:
            return(status_data)

    def get_module_name(self, module_info):
        '''
        This python API parses and return module name
        '''
        func_name = 'get_module_name'
        try:
            status_data = {'status':0}
            s = re.search(r'^FortiSwitch-([0-9A-Z\-]+) ', module_info, re.U)
            if s:
                status_data = {
                    'status':1,
                    'module_name':s.group(1)
                }
        except:
            e = '%s, Unexpected error: %s' % (func_name, sys.exc_info()[0])
            status_data = {'status':0, 'msg':e}
        finally:
            return(status_data)

    def check_table(self, info, table):
        '''
        This python API checks the info content and returns fail if a table content is missing table in info
        '''
        func_name = 'check_table'
        try:
            status_data = {'status':0}
            missing_string = ""
            info = re.sub(r'(\\r)+', '', info, re.DOTALL)
            table = re.sub(r'(\\r)+', '', table, re.DOTALL)
            for t_line in table.split('\n'):
                t_line = t_line.strip()
                line_match  = 0
                for i_line in info.split('\n'):
                    i_line = i_line.strip()
                    i_line = re.sub(r'\s+', ' ', i_line, re.DOTALL)
                    if i_line == t_line:
                        line_match = 1
                        break
                if line_match == 0:
                    missing_string = missing_string + t_line
            if missing_string == "":
                status_data = {
                    'status':1,
                }
            else:
                status_data = {
                    'status':0,
                    'missing_string': missing_string
                }
        except:
            e = '%s, Unexpected error: %s' % (func_name, sys.exc_info()[0])
            status_data = {'status':0, 'msg':e}
        finally:
            return(status_data)

    def compare_info(self, cli_info, info):
        '''
        This python API compare two info content's and returns fail if there is any mismatch
        '''
        func_name = 'compare_info'
        try:
            status_data = {'status':0}
            mismatch_lines = []
            cli_info_list = cli_info.split('\n')
            info_list = info.split('\n')
            cli_info_list_len = len(cli_info_list)
            info_list_len = len(info_list)
            if cli_info_list_len != info_list_len:
                raise Exception('The length of these two info are different: cli_info=%s, info=%s' % (cli_info_list_len, info_list_len))
            mismatch_lines = [i for i, j in zip(info_list, cli_info_list) if i != j]
            if len(mismatch_lines) == 0:
                status_data = {'status':1}
            else:
                status_data = {
                    'status':0,
                    'mismatch_lines':mismatch_lines,
                }
        except Exception as msg:
            status_data = {'status':0, 'msg':msg}
        except:
            e = '%s, Unexpected error: %s' % (func_name, sys.exc_info()[0])
            status_data = {'status':0, 'msg':e}
        finally:
            return(status_data)

    def check_image_loads(self, system_status_info, image_version):
        '''
        This python API check if image already loads by comparing the image_info with the output of "get system status"
        return 1 if image already loads and return 0 if image does not load
        '''
        func_name = 'check_image_loads'
        try:
            dev_image_info = re.search(r'Version: FortiSwitch.*-(.*) (v[0-9]+\.[0-9]+\.[0-9]+),(build[0-9]+),', system_status_info)
            image_ver_info = re.search(r'((v[0-9]+\.[0-9]|v[0-9]+))-(build[0-9]+)-FORTINET', image_version)
            if not dev_image_info or not image_ver_info:
                ret = 0
            dev_image_ver = dev_image_info.group(2)
            dev_image_build = dev_image_info.group(3)
            image_ver = image_ver_info.group(1)
            image_build = image_ver_info.group(3)
            
            if not re.search(image_ver, dev_image_ver) or dev_image_build != image_build:
                ret = 0
            else:
                ret = 1
        except:
            ret = 0
        finally:
            return(ret)

    def parse_image_info(self, image):
        '''
        This python API parses image name and return a dict with version number and build number
        '''
        func_name = 'parse_image_info'
        try:
            status_data = {'status':0}
            image_info = re.search(r'(v[0-9]).*-(build[0-9]+)', image)
            if image_info:
                if image_info.group(1) == 'v1':
                    image_ver = 'v1.00'
                elif image_info.group(1) == 'v2':
                    image_ver = 'v2.00'
                elif image_info.group(1) == 'v3':
                    image_ver = 'v3.00'
                elif image_info.group(1) == 'v6':
                    image_ver = 'v6.00'
                status_data = {'status':1, 'version':image_ver, 'build': image_info.group(2)}
        except:
            e = '%s, Unexpected error: %s' % (func_name, sys.exc_info()[0])
            status_data = {'status':0, 'msg':e}
        finally:
            return(status_data)

    def parse_broadcom_shell_command(self, info):
        '''
        This python API parses the output of broadcom shell command
        '''
        func_name = 'parse_broadcom_shell_command'
        try:
            status_data = {'status':0}
            data = {}
            t_info = re.sub(r'(\\r)+', '', info, re.DOTALL)
            for line in t_info.split('\n'):
                parsed_line = re.search(r'(.*):(.*)', line)
                if parsed_line:
                    key = parsed_line.group(1).strip()
                    key = re.sub(r'UC_', '', key)
                    data[key] = []
                    columns = parsed_line.group(2).split()
                    column_len = len(columns)
                    for column in range (0, column_len):
                        data[key].append(columns[column].strip())
            if len(data) != 0:
                status_data = {'status':1, 'data':data}
        except:
            e = '%s, Unexpected error: %s' % (func_name, sys.exc_info()[0])
            status_data = {'status':0, 'msg':e}
        finally:
            return(status_data)

    def check_diagnose_switch_mclag_icl(self, info, lcl_ports, eb_ports):
        '''
        This python API check lcl_ports and egress_block_ports in info
        '''
        func_name = 'check_diagnose_switch_mclag_icl'
        try:
            status_data = {'status':0}
            status = 1
            missing_lcl_ports = []
            missing_egress_block_ports = []
            t_info = re.sub(r'(\\r)+', '', info, re.DOTALL)
            for line in t_info.split('\n'):
                icl_ports_line = re.search(r'icl-ports (.*)', line)
                if icl_ports_line:
                    icl_ports = icl_ports_line.group(1).strip()
                    icl_port_list = []
                    icl_port_temp = icl_ports.split(',')
                    #icl_port_temp = icl_ports.split()
                    for port in icl_port_temp:
                        if re.search(r'-', port):
                            ports = port.split('-')
                            icl_port_num = range(int(ports[0]), int(ports[1])+1)
                            for port_num in icl_port_num:
                                port_name = 'port%d' % port_num
                                icl_port_list.append(port_name)
                        else:
                            if re.search('port', port):
                                icl_port_list.append(port)
                            else:
                                port_name = 'port%s' % port
                                icl_port_list.append(port_name)
                    for lcl_port in lcl_ports:
                        if lcl_port not in icl_port_list:
                            missing_lcl_ports.append(lcl_port)
                    continue
                egress_block_ports_line = re.search(r'egress-block-ports (.*)', line)
                if egress_block_ports_line:
                    egress_block_ports = egress_block_ports_line.group(1).strip()
                    egress_block_port_list = []
                    egress_block_port_temp = egress_block_ports.split(',')
                    #egress_block_port_temp = egress_block_ports.split()
                    for port in egress_block_port_temp:
                        if re.search(r'-', port):
                            ports = port.split('-')
                            egress_block_port_num = range(int(ports[0]), int(ports[1])+1)
                            for port_num in egress_block_port_num:
                                port_name = 'port%d' % port_num
                                egress_block_port_list.append(port_name)
                        else:
                            if re.search('port', port):
                                egress_block_port_list.append(port)
                            else:
                                port_name = 'port%s' % port
                                egress_block_port_list.append(port_name)
                    for eb_port in eb_ports:
                        if eb_port not in egress_block_port_list:
                            missing_egress_block_ports.append(eb_port)
            if len(missing_lcl_ports) != 0:
                nested_print('missing_lcl_ports=%s' % missing_lcl_ports)
                status = 0
            if len(missing_egress_block_ports) != 0:
                nested_print('missing_egress_block_ports=%s' % missing_egress_block_ports)
                status = 0
        except:
            nested_print('%s, Unexpected error: %s' % (func_name, sys.exc_info()[0]))
        finally:
            return(status)

    def verify_ping_packets_pass(self, info):
        '''
        This python API check ping packets pass
        '''
        func_name = 'verify_ping_packets_pass'
        try:
            status_data = {'status':0}
            t_info = re.sub(r'(\\r)+', '', info, re.DOTALL)
            for line in t_info.split('\n'):
                r = re.search(r'([0-9]+) packets transmitted, ([0-9]+) packets received', line, re.U)
                if r:
                    if r.group(1) == r.group(2):
                        status_data = {'status':1}
                        break
        except:
            e = '%s, Unexpected error: %s' % (func_name, sys.exc_info()[0])
            status_data = {'status':0, 'msg':e}
        finally:
            return(status_data)

    def parse_dai_stats(self, info):
        '''
        This python API parse and return cli "diag show arp-inspection stats" in a dictionary format
        Input Argument : below command output.
        FS1D483Z16000222 # diagnose switch arp-inspection stats
        vlan 10            arp-request               arp-reply
        -----------------------------------------------------------------------
        received                5                        0
        forwarded               1                        1
        dropped                 4                        0
        return: Below dictionary output
        {'dai_stats': {'received': {'arp_reply': '0', 'arp_request': '5'}, 'forwarded': {'arp_reply': '0', 'arp_request': '4'}, 'dropped': {'arp_reply': '1', 'arp_request': '1'}}}

        '''
        func_name = 'parse_dai_stats'
        try:
            stats_dict = {'status':0}
            t_info = re.sub(r'(\\r)+', '', info, re.DOTALL)
            for line in t_info.split('\n'):
                if 'received' in line:
                    out1=re.search(r'received.*([\d]+).*([\d]+)', line)
                if 'forwarded' in line:
                    out2=re.search(r'forwarded.*([\d]+).*([\d]+)', line)
                if 'dropped' in line:
                    out3=re.search(r'dropped.*([\d]+).*([\d]+)', line)
            if out1 and out2 and out3:
                stats_dict.update({'dai_stats':{'received':{'arp_request':list(out1.groups())[0],'arp_reply':list(out1.groups())[1]},'forwarded':{'arp_request':list(out2.groups())[0],'arp_reply':list(out2.groups())[1]},'dropped':{'arp_request':list(out3.groups())[0],'arp_reply':list(out3.groups())[1]}}})

        except:
            e = '%s, Unexpected error: %s' % (func_name, sys.exc_info()[0])
            stats_dict = {'status':0, 'msg':e}
        finally:
            return(stats_dict)


    def check_diagnose_switch_mclag_list(self, info, lcl_ports, p_ports):
        '''
        This python API check local_ports and peer_posts in info
        '''
        func_name = 'check_diagnose_switch_mclag_list'
        try:
            status_data = {'status':0}
            status = 1
            missing_lcl_ports = []
            missing_peer_ports = []
            t_info = re.sub(r'(\\r)+', '', info, re.DOTALL)
            for line in t_info.split('\n'):
                icl_ports_line = re.search(r'Local ports (.*)', line)
                if icl_ports_line:
                    icl_ports = icl_ports_line.group(1).strip()
                    icl_port_list = icl_ports.split('-')
                    icl_port_list = icl_ports.split(',')
                    for lcl_port in lcl_ports:
                        lcl_port = re.sub(r'port', '', lcl_port)
                        if lcl_port not in icl_port_list:
                            missing_lcl_ports.append(lcl_port)
                    continue
                peer_ports_line = re.search(r'Peer ports (.*)', line)
                if peer_ports_line:
                    peer_ports = peer_ports_line.group(1).strip()
                    peer_ports_list = peer_ports.split('-')
                    for p_port in p_ports:
                        p_port = re.sub(r'port', '', p_port)
                        if p_port not in peer_ports_list:
                            missing_peer_ports.append(p_port)
            if len(missing_lcl_ports) != 0:
                nested_print('missing_lcl_ports=%s' % missing_lcl_ports)
                status = 0
            if len(missing_peer_ports) != 0:
                nested_print('missing_peer_ports=%s' % missing_peer_ports)
                status = 0
        except:
            nested_print('%s, Unexpected error: %s' % (func_name, sys.exc_info()[0]))
        finally:
            return(status)

if __name__ == "__main__":
    table = '''
FS1D243Z17000023 # diagnose switch mclag icl
#     icl-ports            21-22
#     egress-block-ports   19-20,23-24
#     interface-mac        70:4c:a5:30:5a:0d
#     lacp-serial-number   FS1D243Z17000023
#     peer-mac             90:6c:ac:d0:09:57
#     peer-serial-number   FS1D243Z16000155
#     Local uptime         0 days  2h:52m:14s
#     Peer uptime          0 days  2h:45m:31s
#     MCLAG-STP-mac        70:4c:a5:30:5a:0c
#     keepalive interval   1
#     keepalive timeout    60
#
# Counters
#     received keepalive packets          1663
#     transmited keepalive packets        1861
#     receive keepalive miss              3

FS1D243Z17000023 #
    '''
    icl_ports=['port21', 'port22']
    peer_ports=['port19','port20','port23','port24']
    f = fsw()
    t = f.check_diagnose_switch_mclag_icl(table, icl_ports, peer_ports)
    print(t)
