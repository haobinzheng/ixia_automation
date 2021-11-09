from robot.api import logger
from optparse import OptionParser
from easyprocess import EasyProcess
import re, sys, time
import pdb

"""
   apc class for all APC pdu related methods
"""
class apc(object):

    def __init__(self):
        self.apc_oid = '.1.3.6.1.4.1.318.1.1.12.3.3.1.1.4'

    def get_status(self, url, outlets):
        '''
        This python API returns outlet status
        '''
        func_name = 'get_status'
        try:
            status_data = {'status':0}
            outlet_list = outlets.split(',')
            outlet_status = {}
            for outlet in outlet_list:
                oid = self.apc_oid + '.' + outlet
                output = EasyProcess('snmpget -v2c -c public %s %s' % (url, oid)).call(timeout=5).stdout
                o = re.search(r'INTEGER: ([0-9])', output)
                if o:
                    if o.group(1) == '1':
                        outlet_s = 'On'
                    elif o.group(1) == '2':
                        outlet_s = 'Off'
                    else:
                        outlet_s = 'Unknown'
                    outlet_status[outlet] = outlet_s
                else:
                    raise Exception(output)
            status_data = {
                'status':1,
                'outlets':outlet_status
            }
        except Exception as msg:
            e = '%s Exception: %s' % (func_name, msg)
            status_data = {'status':0, 'msg':e}
        except:
            e = '%s, Unexpected error: %s' % (func_name, sys.exc_info()[0])
            status_data = {'status':0, 'msg':e}
        finally:
            return(status_data)

    def set_off(self, url, outlets):
        '''
        This python API sets off
        '''
        func_name = 'set_off'
        try:
            status_data = {'status':0}
            outlet_list = outlets.split(',')
            for outlet in outlet_list:
                oid = self.apc_oid + '.' + outlet
                EasyProcess('snmpset -v2c -c private %s %s i 2' % (url, oid)).call(timeout=5).stdout
                for i in range(4):
                    time.sleep(2)
                    output = self.get_status(url, outlet)
                    if output['status'] != 1:
                        raise Exception('Unable set outlet: %s off due to error: %s' % (outlet, output))
                    if outlet not in output['outlets']:
                        raise Exception('Unable set outlet: %s off due to unknown outlet id %s' % (outlet, output['outlets']))
                    if  output['outlets'][outlet] == 'Off':
                        logger.console('%s: outlet %s status is Off' % (i, outlet))
                        break
                    else:
                        logger.console('%s: outlet status is %s, please wait 2 seconds ....' % (i, output['outlets'][outlet]))
                if i >= 3:
                    raise Exception('Power off Device fails')
            status_data = {'status':1}
        except Exception as msg:
            e = '%s Exception: %s' % (func_name, msg)
            status_data = {'status':0, 'msg':e}
        except:
            e = '%s, Unexpected error: %s' % (func_name, sys.exc_info()[0])
            status_data = {'status':0, 'msg':e}
        finally:
            return(status_data)

    def set_on(self, url, outlets):
        '''
        This python API sets outlets on
        '''
        func_name = 'set_on'
        try:
            status_data = {'status':0}
            outlet_list = outlets.split(',')
            for outlet in outlet_list:
                oid = self.apc_oid + '.' + outlet
                EasyProcess('snmpset -v2c -c private %s %s i 1' % (url, oid)).call(timeout=5).stdout
                for i in range(4):
                    time.sleep(2)
                    output = self.get_status(url, outlet)
                    if output['status'] != 1:
                        raise Exception('Unable set outlet: %s on due to error: %s' % (outlet, output))
                    if outlet not in output['outlets']:
                        raise Exception('Unable set outlet: %s on due to unknown outlet id: %s' % (outlet, output['outlets']))
                    if  output['outlets'][outlet] == 'On':
                        logger.console('%s: outlet %s status is On' % (i, outlet))
                        break
                    else:
                        logger.console('$s: outlet status is %s, please wait 2 seconds ....' % (i, output['outlets'][outlet]))
                if i >= 3:
                    raise Exception('Power on Device fails')
            status_data = {'status':1}
        except Exception as msg:
            e = '%s Exception: %s' % (func_name, msg)
            status_data = {'status':0, 'msg':e}
        except:
            e = '%s, Unexpected error: %s' % (func_name, sys.exc_info()[0])
            status_data = {'status':0, 'msg':e}
        finally:
            return(status_data)

    def set_reboot(self, url, outlets):
        '''
        This python API sets outlets reboot
        '''
        func_name = 'set_reboot'
        try:
            status_data = {'status':0}
            outlet_list = outlets.split(',')
            # set outlets off
            for outlet in outlet_list:
                oid = self.apc_oid + '.' + outlet
                EasyProcess('snmpset -v2c -c private %s %s i 2' % (url, oid)).call(timeout=5).stdout
                for i in range(4):
                    time.sleep(2)
                    output = self.get_status(url, outlet)
                    if output['status'] != 1:
                        raise Exception('Unable set outlet: %s on due to error: %s' % (outlet, output))
                    if outlet not in output['outlets']:
                        raise Exception('Unable set outlet: %s on due to unknown outlet id: %s' % (outlet, output['outlets']))
                    if  output['outlets'][outlet] == 'Off':
                        logger.console('%s: outlet %s status is Off' % (i, outlet))
                        break
                    else:
                        logger.console('$s: outlet status is %s, please wait 2 seconds ....' % (i, output['outlets'][outlet]))
                if i >= 3:
                    raise Exception('Power off Device fails')
            # sleep 5 seconds
            time.sleep(5)
            # set outlets on
            for outlet in outlet_list:
                oid = self.apc_oid + '.' + outlet
                EasyProcess('snmpset -v2c -c private %s %s i 1' % (url, oid)).call(timeout=5).stdout
                for i in range(4):
                    time.sleep(2)
                    output = self.get_status(url, outlet)
                    if output['status'] != 1:
                        raise Exception('Unable set outlet: %s on due to error: %s' % (outlet, output))
                    if outlet not in output['outlets']:
                        raise Exception('Unable set outlet: %s on due to unknown outlet id: %s' % (outlet, output['outlets']))
                    if  output['outlets'][outlet] == 'On':
                        logger.console('%s: outlet %s status is On' % (i, outlet))
                        break
                    else:
                        logger.console('$s: outlet status is %s, please wait 2 seconds ....' % (i, output['outlets'][outlet]))
                if i >= 3:
                    raise Exception('Power on Device fails')
            status_data = {'status':1}
        except Exception as msg:
            e = '%s Exception: %s' % (func_name, msg)
            status_data = {'status':0, 'msg':e}
        except:
            e = '%s, Unexpected error: %s' % (func_name, sys.exc_info()[0])
            status_data = {'status':0, 'msg':e}
        finally:
            return(status_data)

if __name__ == "__main__":
    usage = 'python apc.py -u apc_url -o outlets -a action'
    parser = OptionParser(usage)
    parser.add_option('-u', '--apc_url', dest='apc_url', default='10.105.50.114', help='url of APC pdu', metavar='URL')
    parser.add_option('-o', '--outlets', dest='outlets', help='comma separate outlets')
    parser.add_option('-a', '--action', dest='action', default='get_status', help='power off/on/cycle or get status')
    (options, args) = parser.parse_args()

    a = apc()
    Status = {}
    if options.action == 'get_status':
        Status = a.get_status(options.apc_url, options.outlets)
    elif options.action == 'off':
        Status = a.set_off(options.apc_url, options.outlets)
    elif options.action == 'on':
        Status = a.set_on(options.apc_url, options.outlets)
    elif options.action == 'cycle':
        Status = a.set_reboot(options.apc_url, options.outlets)
    else:
        Status = {'status':0, 'msg':'Unknown Action'}
    print(Status)
