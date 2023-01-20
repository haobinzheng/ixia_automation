#!/usr/bin/env python
import sys
import os
import pexpect
# query file for all route servers and put into a list
routerFile = open('metro_switches', 'r')
routeServers = [i for i in routerFile] #look up list comprehension is not clear
# query file for all commands and put into a list
commandFile = open('metro_commands.txt', 'r')
commands = [i for i in commandFile]

# Starts the loop
for router in routeServers:
    child = pexpect.spawn ('telnet', [router.strip()]) #option needs to be a list
    child.logfile = sys.stdout #display progress on screen
    #child.expect ('HSMC_CN8700_3(C) login:	')
    child.sendline('su')
    try: 
      child.expect ('Password:')
    except pexpect.TIMEOUT:
      raise OurException("Login prompt not received") 
    child.sendline('wwp')
    for command in commands:
        try: 
          child.expect('8700_3_C> ') #different options on prompt
        except pexpect.TIMEOUT:
          raise OurException("8700_3 prompt not received") 
        print 'this is the command to execute:----> ', command
        child.sendline(command)
        child.expect('8700_3_C> ') #different options on prompt
