#!/usr/bin/python
from robot.api import logger
from optparse import OptionParser
import re, sys
import telnetlib
import pdb
import paramiko
import time

#sys.path.append('/home/jimhe/git-repo/automation/lib/util')

#import misc

"""
Defines API for telnet to cisco terminal server
"""
def login(ip, user, password, prompt):
    """
    login to the device
    """
    try:
        status_data = {'status':0}
        tn = telnetlib.Telnet(ip)
        output = tn.read_until(('Password: ').encode('ascii'), 2)
        logger.console(output)
        tn.write((user + '\n').encode('ascii'))
        output = tn.read_until(('#').encode('ascii'), 2)
        #output = tn.read_until('#', 2)
        logger.console(output)
        if "#".encode('ascii') not in output:
            tn.write(('enable\n').encode('ascii'))
            output = tn.read_until(('Password:').encode('ascii'), 2)
            logger.console(output)
            tn.write((password + '\n').encode('ascii'))
            output = tn.read_until(prompt.encode('ascii'), 2)
            logger.console(output)
        status_data = {'status':1, 'msg':tn}
    except:
        status_data = {'status':0, 'msg':sys.exc_info()[0]}
    finally:
        #print(status_data)
        return(status_data)

def logout(tn):
    """
    logout the device
    """
    try:
        status_data = {'status':0}
        tn.close()
        status_data = {'status':1}
    except:
        status_data = {'status':0, 'msg':sys.exc_info()[0]}
    finally:
        return(status_data)

def command(tn, prompt, port):
    """
    Command sends to device
    """
    try:
        status_data = {'status':0}
        tn.write(('clear line {}'.format(port)).encode('ascii'))
        output = tn.read_until('\[confirm\]'.encode('ascii'), 1)
        logger.console(output)
        tn.write(('\n').encode('ascii'))
        output = tn.read_until(('\[OK\]').encode('ascii'), 1)
        logger.console(output)
        tn.write(('\n').encode('ascii'))
        output = tn.read_until(prompt.encode('ascii'), 1)
        logger.console(output)
        status_data = {'status':1, 'msg':output}
    except:
        status_data = {'status':0, 'msg':sys.exc_info()[0]}
    finally:
        #print(status_data)
        return(status_data)

def clear_console_line(url, port, login_pwd='fortinet123', exec_pwd='fortinet123', prompt='#'):
    """
    clear console port
    """
    print("Trying to clear line on comm_server: {} port: {}".format(url,port))
    try:
        status_data = {'status':0}
        login_status = login(url, login_pwd, exec_pwd, prompt)
        if login_status['status'] != 1:
            logger.console('unable telent to %s' % options.url)
            exit()
        else:
            print("login sucessfully into {}".format(url))
        tn = login_status['msg']
        #port = port.encode('ascii','ignore')
        #print("console_port before stripping off leading 20: {}".format(port))

        console_port = re.sub('20', '', port)
        #print("console_port after stripping off leading 20: {}".format(console_port))
        command_status = command(tn, prompt, console_port)
        if command_status['status'] != 1:
            logger.console('unable to clear console line: %s (%s)' % (port, command_status['msg']))
        else:
            status_data = {'status':1, 'msg':"clear line sucessfully"}
        show_users_output = command_status['msg']
        #logger.console('clear line command status %s' % show_users_output)
        logout_status = logout(tn)
        if logout_status['status'] != 1:
            logger.console('unable to logout %s' % logout_status['msg'])
    except:
        status_data = {'status':0, 'msg':sys.exc_info()[0]}
    finally:
        #print("clear_console_line: status_data = {}".format(status_data))
        return(status_data)

def ssh(ip,username,password,cmd):
    port = 22
    try:
        ssh = paramiko.SSHClient()  # ??ssh??
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=ip, port=int(port), username=username, password=password,timeout=5)
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=10)
        result = stdout.read()
        result1 = result.decode()
        error = stderr.read().decode('utf-8')

        if not error:
            ret = {"ip":ip,"data":result1}
            ssh.close()
            return ("Success",ret)
    except Exception as e:
        error = "???????,{}".format(e)
        ret = {"ip": ip, "data": error}
        return ("Failed",ret)


if __name__ == "__main__":
    result = ssh("10.105.50.59","admin","admin","get system status") 
    print (result)
    usage = 'python clear-console.py -u url -p port -l login_pwd -e exec_pwd -t prompt'
    parser = OptionParser(usage)
    parser.add_option('-u', '--url', dest='url', default='', help='telnet ip address of the device')
    parser.add_option('-p', '--port', dest='port', default='', help='console port')
    parser.add_option('-l', '--login_pwd', dest='login_pwd', default='fortinet123', help='login password')
    parser.add_option('-e', '--exec_pwd', dest='exec_pwd', default='fortinet123', help='exec passwor')
    parser.add_option('-t', '--prompt', dest='prompt', default='#', help='prompt of the device')
    (options, args) = parser.parse_args()

    status = clear_console_line(options.url, options.port, options.login_pwd, options.exec_pwd, options.prompt)
    if status['status'] != 1:
        logger.console('unable clear console port %s' % options.port)
