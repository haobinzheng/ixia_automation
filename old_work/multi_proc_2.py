import os
import time
from multiprocessing import Process
import multiprocessing
import subprocess
from snmpwalk_run import *

def f(name):
    print 'hello', name

if __name__ == '__main__':
    proc = 'snmp_run'
    p = Process(target=proc)
    p.daemon = True
    p.start()
    print p.is_alive()
    print "sleep 30 second before killing the process"
    #p.terminate()
    p.join()
    print dir(p)