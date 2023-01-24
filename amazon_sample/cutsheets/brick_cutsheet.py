#!/usr/bin/python

import sys
spine=str(sys.argv[1])
K=[4, 5, 10, 11, 16, 17, 22, 23]
print ' T1 router name , T1 router interface , T2 router interface , T2 router '
for B in range(1,33):
   for X in range(0,16):
	T=0
	M=0
        for Y in range(0,16):
               if Y<8:
                 Z=K[Y]
	         print '%sb%d-t1-r%d,et-0/0/%d,et-0/0/%d,%sb%d-t2-r%d' % (spine, B, X+1, Z, X, spine, B, Y+1)
               else: 
                     if Y<12:
                        print '%sb%d-t1-r%d,et-0/1/%d,et-0/0/%d,%sb%d-t2-r%d' % (spine, B, X+1, T, X, spine, B, Y+1)
                        T=T+1
		     else:
			print '%sb%d-t1-r%d,et-0/2/%d,et-0/0/%d,%sb%d-t2-r%d' % (spine, B, X+1, M, X,spine, B, Y+1)
		        M=M+1
