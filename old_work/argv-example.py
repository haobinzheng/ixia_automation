#! /usr/bin/env python
import sys 

arg1 = sys.argv[1]
arg2 = sys.argv[2]
try: 
	print arg1 + arg2
except ValueError: 
	print "no argument"
 

