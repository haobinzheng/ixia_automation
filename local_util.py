import telnetlib
import sys
import time
import logging
import traceback
import paramiko
import time
from time import sleep
import re
import os
from datetime import datetime
from threading import Thread
import subprocess

from robot.api import logger

DEBUG = True


def check_p2p_config(*argc,**kwargs):
    output = kwargs['output']
    state = kwargs["state"]
    output_list = transform_robot_output(output)

    printr("debug: state = {}".format(repr(state)))
    state = robot_2_python(state)
    printr("debug: state = {}".format(repr(state)))
    if  state == "disable":
        for line in output_list:
            if "portlink-p2p" in line:
                return False
        return True
    if state == "enable":
        for line in output_list:
            if state in line:
                return True
        return False
        
def Check_Find_P2p(func):
    def inner1(*args, **kwargs):
          
        print("before Execution")
          
        # getting the returned value
        returned_value = func(*args, **kwargs)
        print("after Execution")
          
        # returning the value to the original frame
        return returned_value
          
    return inner1

def wait(number):
    printr("\n============ Waiting for {} Seconds ..... =========".format(number))
    sleep(int(number))

def wait_with_timer(seconds,**kwargs):
    if 'msg' in kwargs:
        notice = kwargs['msg']
        print('========================= {} =========================='.format(notice))
    for remaining in range(int(seconds), 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write("\n============================ Timer:{:2d} seconds remaining =======================".format(remaining))
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\n")

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
        output = tn.read_until(('#').encode('ascii'), 5)
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


def switch_find_login_prompt_new(tn):
    TIMEOUT = 3
    # tn.write(('' + '\n').encode('ascii'))
    #time.sleep(1)

    # tn.write(('\x03').encode('ascii'))
    # time.sleep(1)
    # tn.write(('\x03').encode('ascii'))
    # time.sleep(1)
    # tn.write(('\x03').encode('ascii'))
    # time.sleep(1)
    printr("See what prompt the console is at")
    output = tn.expect([re.compile(b"login:")],timeout=TIMEOUT)
    printr(output)
    printr(output[2].decode().strip())
    prompt = output[2].decode().strip()
    if output[0] == -1: 
        printr("It is a NOT login prompt, Need further action to login")
    if output[0] == 0:
        printr("it is a login prompt, you need to re-login")
        return ("login",None)
    elif " #" in prompt: 
        printr("it is a Shell prompt")
        pattern = r"[a-zA-Z0-9\-]+"
        match = re.match(pattern,prompt)
        if match:
            result = match.group()
        else:
            result = None
        return ("shell",result)
    elif "New Password:"in prompt:
        printr("it is a new switch that needs to change password, change password to *Fortinet123!* ")
        tn.write(('Fortinet123!' + '\n').encode('ascii'))
        tn.write(('Fortinet123!' + '\n').encode('ascii'))
        return ("new",None)
    else:
        printr("can not get any prompt, need to use robust login procedure...")
        return (None,None)



def convert_cmd_ascii_n(cmd):
    cmd = cmd + '\n'
    return cmd.encode('ascii')

def switch_show_cmd(tn,cmd,**kwargs):
    #relogin_if_needed(tn)
    if 't' in kwargs:
        timeout = kwargs['t']
    else:
        timeout = 2
    cmd = convert_cmd_ascii_n(cmd)
    tn.write(cmd)
    tn.write(('' + '\n').encode('ascii'))
    tn.write(('' + '\n').encode('ascii'))
    tn.write(('' + '\n').encode('ascii'))
    tn.write(('' + '\n').encode('ascii'))
    sleep(timeout)
    output = tn.read_very_eager()
    out_list = output.split('\r\n')
    debug("out_list in switch_show_cmd = {}".format(out_list))
    encoding = 'utf-8'
    out_str_list = []
    for o in out_list:
        try:
            o_str = o.strip()
            o_str = o_str.encode(encoding).strip()
            if o_str:
                out_str_list.append(o_str)
        except Exception as e:
            pass
    tn.write(('' + '\n').encode('ascii'))
    tn.write(('' + '\n').encode('ascii'))
    # tprint(dir(output))
    # tprint(type(output))
    #tprint(out_list)
    for i in out_str_list:
        tprint(i)
    return out_str_list
    

def collect_show_cmd(output,**kwargs):
     
    printr("Enter collect_show_cmd")
    printr(output)
    #output = tn.read_until(("# ").encode('ascii'))
    out_list = output.split(b'\r\n')
    encoding = 'utf-8'
    out_str_list = []
    for o in out_list:
        o_str = o.decode(encoding).rstrip(' ')
        out_str_list.append(o_str)
    printr(out_str_list)
    return out_str_list


def debug(msg):
    # global DEBUG
    # print(DEBUG)
    if DEBUG:
        if type(msg) == list:
            for m in msg:
                tprint("Debug: {}".format(m))
        else:
            tprint("Debug: {}".format(msg))

def dprint(msg):
    # global DEBUG
    # print(DEBUG)
    if DEBUG:
        if type(msg) == list:
            for m in msg:
                tprint("Debug: {}".format(m))
        else:
            tprint("Debug: {}".format(msg))


def find_dut_prompt(tn):
    tn.write(('' + '\n').encode('ascii'))
    output = tn.read_until(("# ").encode('ascii'))
    out_list = output.split(b'\r\n')
    encoding = 'utf-8'
    for o in out_list:
        o_str = o.decode(encoding).rstrip(' ')
        if "#" in o_str:
            prompt = o_str.strip(' ')
            prompt = prompt.strip("#")
    dprint(prompt)
    return prompt

def Info(*args, **kwargs):
    tempa = ' '.join(str(a) for a in args)
    tempk = ' '.join([str(kwargs[k]) for k in kwargs])
    temp = tempa + ' ' + tempk # puts a space between the two for clean output
    printr(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + " :: " + "Info: " + temp)
    printr('\n')

def printr(*args,**kwargs):
    print_string = ""
    for s in args:
        try:
            print_string = "{},{}".format(print_string,s) if print_string else s
        except Exception as print_except:
            print("Error to log to Robot console")
    logger.console(print_string)

def tprint(*args, **kwargs):
    tempa = ' '.join(str(a) for a in args)
    tempk = ' '.join([str(kwargs[k]) for k in kwargs])
    temp = tempa + ' ' + tempk # puts a space between the two for clean output
    printr(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + " :: " + temp)

def log_with_time(*args, **kwargs):
    tempa = ' '.join(str(a) for a in args)
    tempk = ' '.join([str(kwargs[k]) for k in kwargs])
    temp = tempa + ' ' + tempk # puts a space between the two for clean output
    printr(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + " :: " + temp)

def switch_configure_cmd_name(dut_dir,cmd):
    tn = dut_dir['telnet']
    dut_name = dut_dir['name']
    tprint("configuring {}: {}".format(dut_name,cmd))
    cmd = convert_cmd_ascii_n(cmd)
    tn.write(cmd)
    time.sleep(0.5)
    tn.read_until(("# ").encode('ascii'),timeout=10)

def switch_configure_cmd(tn,cmd,**kwargs):
    if 'mode' in kwargs:
        mode = kwargs['mode']
    else:
        mode = None

    if mode == "silent":
        pass
    else:
        dut_prompt = find_dut_prompt(tn)
        tprint("configuring {}: {}".format(dut_prompt,cmd))
    cmd = convert_cmd_ascii_n(cmd)
    tn.write(cmd)
    time.sleep(0.1)
    tn.read_until(("# ").encode('ascii'),timeout=10)

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

def clear_console_line(url, port, login_pwd='Fortinet123!', exec_pwd='Fortinet123!', prompt='#'):
    """
    clear console port
    """
    printr("Trying to clear line on comm_server: {} port: {}".format(url,port))
    try:
        status_data = {'status':0}
        login_status = login(url, login_pwd, exec_pwd, prompt)
        if login_status['status'] != 1:
            logger.console('unable telent to %s' % options.url)
            exit()
        else:
            logger.console("login sucessfully into {}".format(url))
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

def TelnetConsole(ip_address, console_port,**kwargs):
    printr("console server ip ="+str(ip_address))
    printr("console port="+str(console_port))
    if "password" in kwargs:
        pwd = kwargs["password"]
    else:
        pwd = ''
    
    console_port_int = int(console_port)
    # if settings.CLEAR_LINE:
    #     status = clear_console_line(ip_address,str(console_port),login_pwd='Fortinet123!', exec_pwd='Fortinet123!', prompt='#')
    #     if status['status'] != 1:
    #         logger.console('unable clear console port %s' % console_port)
    #     time.sleep(1)
    #switch_login(ip_address,console_port)
    try:
        tn = telnetlib.Telnet(ip_address,console_port_int)
    except Exception as  ConnectionRefusedError: 
        tprint("!!!!!!!!!!!the console is being used, need to clear it first")
        status = clear_console_line(ip_address,str(console_port),login_pwd='Fortinet123!', exec_pwd='Fortinet123!', prompt='#')
        if status['status'] != 1:
            logger.console('unable clear console port %s' % console_port)
            exit()
        sleep(2)
        tn = telnetlib.Telnet(ip_address,console_port_int)
    
    tn.write(('\x03').encode('ascii'))
    tn.write(('\x03').encode('ascii'))
    tn.write(('\x03').encode('ascii'))
    tn.write(('\x03').encode('ascii'))
    time.sleep(1)

    #tprint("successful login\n")
    tn.write(('' + '\n').encode('ascii'))
    tn.write(('' + '\n').encode('ascii'))
    tn.write(('' + '\n').encode('ascii'))
    tn.write(('' + '\n').encode('ascii'))
    time.sleep(1)

    tn.read_until(("login: ").encode('ascii'),timeout=5)

    tn.write(('admin' + '\n').encode('ascii'))

    tn.read_until(("Password: ").encode('ascii'),timeout=5)

    #tn.write(('' + '\n').encode('ascii'))
    tn.write((pwd + '\n').encode('ascii'))

    prompt = switch_find_login_prompt_new(tn)
    p = prompt[0]
    debug(prompt)
    if p == 'login':
        Info("This is new software image, login back without passord ")
        tn.write(('' + '\n').encode('ascii'))
        tn.write(('' + '\n').encode('ascii'))
        tn.write(('' + '\n').encode('ascii'))
        tn.write(('' + '\n').encode('ascii'))
        tn.read_until(("login: ").encode('ascii'),timeout=10)
        tn.write(('Fortinet123!' + '\n').encode('ascii'))
        tn.read_until(("Password: ").encode('ascii'),timeout=10)
        tn.write(('Fortinet123!' + '\n').encode('ascii'))
        tn.write(('' + '\n').encode('ascii'))
        tn.write(('' + '\n').encode('ascii'))
        sleep(1)
        tn.read_until(("# ").encode('ascii'),timeout=10)
    elif p == 'shell':
        Info("Login without password")
        #prevent enter a prompt that is in a config mode
        tn.write(('end' + '\n').encode('ascii'))
        tn.write(('end' + '\n').encode('ascii'))
    elif p == 'new':
        Info("This first time login to image not allowing blank password, password has been changed to <Fortinet123!>")
    elif p == None:
        Info("Not in login prompt, press enter a couple times to show login prompt")
        tn.write(('\x03').encode('ascii'))
        tn.write(('\x03').encode('ascii'))
        tn.write(('\x03').encode('ascii'))
        tn.write(('\x03').encode('ascii'))
        time.sleep(1)
        tn.write(('' + '\n').encode('ascii'))
        sleep(1)
        tn.write(('' + '\n').encode('ascii'))
        sleep(1)
        tn.write(('' + '\n').encode('ascii'))
        tn.write(('' + '\n').encode('ascii'))
        tn.write(('' + '\n').encode('ascii'))
        tn.write(('' + '\n').encode('ascii'))
        tn.write(('' + '\n').encode('ascii'))

        tn.read_until(("login: ").encode('ascii'),timeout=10)
        tn.write(('admin' + '\n').encode('ascii'))
        tn.read_until(("Password: ").encode('ascii'),timeout=10)
        tn.write(('Fortinet123!' + '\n').encode('ascii'))
        tn.write(('' + '\n').encode('ascii'))
        tn.write(('' + '\n').encode('ascii'))
        sleep(1)
        tn.read_until(("# ").encode('ascii'),timeout=10)
    
    switch_configure_cmd(tn,'config system global')
    switch_configure_cmd(tn,'set admintimeout 480')
    switch_configure_cmd(tn,'end')
    tprint("get_switch_telnet_connection_new: Login sucessful!\n")
    return tn

