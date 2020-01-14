#! /usr/bin/python

import os
import sys

def dup(aa):
  for i in range(len(aa)):
    if aa[i] in aa[:i]:
      aa.pop(i)
      return dup(aa)
  

if __name__=="__main__":
  
 aa = [9, 1, 3, 6, 5, 8, 10, 9, 11, 4, 10]
 dup(aa)
 print aa 


