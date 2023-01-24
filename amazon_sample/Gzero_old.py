#!/apollo/sbin/envroot "$ENVROOT/bin/python"
#-------------------------------------------------------------------------------
# Name:        Gzero.py
# Purpose:     Script to generate YAML Turn up CM from files in directory Geneva/out
#
# Author:      vcapp
#
# Created:     21/02/2013
# Copyright:   Amazon
# Licence:     Missing Cr/Approval
#----

import re
import commands


cDr = 'sfo6-21'
pDr = '-ws-dis-f1-t1-r'
#t1-routers that connects  to core 
fcr = ['1','2','3','4','57','58','59','60']
#fcr = ['5','6','7','8','61','62','63','64']
#code devices used on Geneva/out 
COR = ['101','102']
#COR = ['201','202','203','204','205','206','207','208']
PON = 1000
BW = 4
MODULE = 1
PORT = 1
FAB = "ws"

print "core_routers:"
for C in COR:
    start = MODULE - 1
    port =  PORT
    basePO = PON
    print " "  + cDr + "-" + FAB +  "-cor-r" + C +":"
    print "  port_channels:"
    for F  in fcr:
        basePO = basePO + 1
        print "   "  + str(basePO) + ":"

        command = "cat ../out/" +  cDr +  pDr +F + "/all |  grep "+ C +"| grep 'xe-' | awk '{print $3}'"
        (status,output)=commands.getstatusoutput(command)
        R2 = output.split('\n')
        command = "cat ../out/"+  cDr +  pDr  +F+ "/all | grep 'replace: " + R2[0] + " ' -A 3 | grep ae | awk '{print $2}' |  sed 's/;$//'"
        (status,lag)=commands.getstatusoutput(command)
        command = "cat ../out/"+  cDr +  pDr + F + "/all | sed -n '/replace: " + lag + " {/,/address/p' | grep address | awk '{print $2}' | sed 's/\/31;$//'"
        (status,address)=commands.getstatusoutput(command)
        addr = address.split('.')
        print "    subnet: " + addr[0] + "."  + addr[1] +  "."  + addr[2] + "."  + str(int(addr[3]) - 1) + "/31"
     
        EthString = "[ to Manually add"
#        for i in range(1,BW+1):
#            if i == ( BW ):
#	       EthString = EthString  +  "Eth" + str(start+i) + "/" + str(port)
#            else:
#	       EthString = EthString  +  "Eth" + str(start+i) + "/" + str(port) + ","
#
#        port = port + 1

        print "    interfaces: " + EthString + "]"
        print "    peer:"
        print "       name: " + cDr +  pDr + F
        print "       lag: " + lag
      


# 
#https://w.amazon.com/index.php/Networking/NetworkDeployment/Odot.py#Experiment_1
#

print "discat_routers:"
for F in fcr:
     print " "  + cDr +  pDr  + F +":"
     command = "cat ../out/" +  cDr +  pDr + F + "/all | grep -ir 'replace: router-id' | awk '{print $3}' | sed 's/\/all://' | sed 's/;$//'"
     (status,output)=commands.getstatusoutput(command)
     print "  loopback_address: " + output
     print "  lags:"
     for C in COR:
       command = "cat ../out/" +  cDr +  pDr +F+ "/all |  grep "+ C +"| grep 'xe-' | awk '{print $3}'"
       (status,output)=commands.getstatusoutput(command)
       R2 = output.split('\n')
       command = "cat ../out/"+  cDr +  pDr +F+ "/all | grep 'replace: " + R2[0] + " ' -A 3 | grep ae | awk '{print $2}' |  sed 's/;$//'"
       (status,output)=commands.getstatusoutput(command)
       print "   " + output + ":"
       print "    interfaces: [",
       for i in R2:
           if i != R2[len(R2)-1]:
              print i + ",",
           else:
              print i,
       print "]"
       command = "cat ../out/"+  cDr +  pDr + F + "/all | sed -n '/replace: " + output+ " {/,/address/p' | grep address | awk '{print $2}' | sed 's/\/31;$//'"
       (status,output)=commands.getstatusoutput(command)
       print "    address: " + output
