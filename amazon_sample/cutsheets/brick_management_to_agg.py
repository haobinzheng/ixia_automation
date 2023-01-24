#!/usr/bin/python

import sys
#spine=raw_input(' Please tell me the NZ (example = iad6) = ')
#start_row=raw_input(' Please input the first brick number = ')
#end_row=raw_input(' Please input the last brick number = ')
spine=str(sys.argv[1])
start_row=str(sys.argv[2])
end_row=str(sys.argv[3])
start_row=int(start_row)
end_row=int(end_row)
M=(start_row-1)*2
for B in range (start_row,end_row+1):
    print '%s-br-ctz-f1mgmt-b%d-r1, ,xe-0/1/0, , , , , ,xe-0/0/%d, ,%s-br-ctz-f1mgmt-agg-r1' % (spine, B, M, spine)
    print '%s-br-ctz-f1mgmt-b%d-r1, ,xe-0/2/0, , , , , ,xe-0/0/%d, ,%s-br-ctz-f1mgmt-agg-r2' % (spine, B, M, spine)
    M=M+1
    print '%s-br-ctz-f1mgmt-b%d-r2, ,xe-0/1/0, , , , , ,xe-0/0/%d, ,%s-br-ctz-f1mgmt-agg-r1' % (spine, B, M, spine)
    print '%s-br-ctz-f1mgmt-b%d-r2, ,xe-0/2/0, , , , , ,xe-0/0/%d, ,%s-br-ctz-f1mgmt-agg-r2' % (spine, B, M, spine)
    M=M+1


