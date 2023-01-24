#!/usr/bin/python

import sys
print 'T2 router name,T2 router interface,T3 router interface,T3 router'
spine=raw_input(' Please tell me the name of the spine = ')
start_row=raw_input(' Please input the start row of the spine = ')
end_row=raw_input(' Please input the end row of the spine = ')
start_row=int(start_row)-1
end_row=int(end_row)
T=0
M=0
for B in range(1,33):
 if B<25:
   for X in range(0,16):
        for Y in range (start_row,end_row):
               if Y<8:
		 print '%sb%d-t2-r%d,et-0/0/%d,et-0/0/%d,%ss%d-t3-r%d' % (spine, B, X+1, Y+16, B-1, spine, Y+1, X+1)
               else: 
                     if Y<12:
                        print '%sb%d-t2-r%d,et-0/1/%d,et-0/0/%d,%ss%d-t3-r%d' % (spine, B, X+1, T, B-1, spine, Y+1, X+1)
                        if T==3:
			   T=0
		        else:			
			   T=T+1
		     else:
			print '%sb%d-t2-r%d,et-0/2/%d,et-0/0/%d,%ss%d-t3-r%d' % (spine, B, X+1, M, B-1, spine, Y+1, X+1)
                        if M==3:
                           M=0
                        else:
                           M=M+1
 else:
   if B<29:
      for X in range(0,16):
        for Y in range (start_row,end_row):
               if Y<8:
                 print '%sb%d-t2-r%d,et-0/0/%d,et-0/1/%d,%ss%d-t3-r%d' % (spine, B, X+1, Y+16, B-25, spine, Y+1, X+1)
               else:
                     if Y<12:
                        print '%sb%d-t2-r%d,et-0/1/%d,et-0/1/%d,%ss%d-t3-r%d' % (spine, B, X+1, T, B-25, spine, Y+1, X+1)
                        if T==3:
                           T=0
                        else:
                           T=T+1
		     else:
                        print '%sb%d-t2-r%d,et-0/2/%d,et-0/1/%d,%ss%d-t3-r%d' % (spine, B, X+1, M, B-25, spine, Y+1, X+1)
                        if M==3:
                           M=0
                        else:
                           M=M+1
   else:
      for X in range(0,16):
        for Y in range (start_row,end_row):
               if Y<8:
                 print '%sb%d-t2-r%d,et-0/0/%d,et-0/2/%d,%ss%d-t3-r%d' % (spine, B, X+1, Y+16, B-29, spine, Y+1, X+1)
               else:
                     if Y<12:
                        print '%sb%d-t2-r%d,et-0/1/%d,et-0/2/%d,%ss%d-t3-r%d' % (spine, B, X+1, T, B-29, spine, Y+1, X+1)
                        if T==3:
                           T=0
                        else:
                           T=T+1
                     else:
                        print '%sb%d-t2-r%d,et-0/2/%d,et-0/2/%d,%ss%d-t3-r%d' % (spine, B, X+1, M, B-29, spine, Y+1, X+1)
                        if M==3:
                           M=0
                        else:
			   M=M+1
