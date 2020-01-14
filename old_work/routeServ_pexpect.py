#!/usr/bin/env python
import sys
import pexpect
# query file for all route servers and put into a list
routerFile = open('route-servers', 'r')
routeServers = [i for i in routerFile] #look up list comprehension is not clear
# query file for all commands and put into a list
commandFile = open('commands.txt', 'r')
commands = [i for i in commandFile]

# Starts the loop
for router in routeServers:
    child = pexpect.spawn ('telnet', [router.strip()]) #option needs to be a list
    child.logfile = sys.stdout #display progress on screen
    child.expect ('Username:')
    #child.expect ('Password:')
    child.sendline('rviews')
    for command in commands:
        child.expect(['route-server', 'route-views']) #different options on prompt
        child.sendline(command)
        child.expect(['route-server', 'route-views'])
