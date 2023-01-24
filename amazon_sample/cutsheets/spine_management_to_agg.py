#!/usr/bin/python

import sys
spine=str(sys.argv[1])
start_row=str(sys.argv[2])
end_row=str(sys.argv[3])
start_row=int(start_row)
end_row=int(end_row)
M=63+start_row
for B in range (start_row,end_row+1):
    print '%s-br-ctz-f1mgmt-s%d-r1, ,xe-0/1/0, , , , , ,xe-0/0/%d, ,%s-br-ctz-f1mgmt-agg-r1' % (spine, B, M, spine)
    print '%s-br-ctz-f1mgmt-s%d-r1, ,xe-0/2/0, , , , , ,xe-0/0/%d, ,%s-br-ctz-f1mgmt-agg-r2' % (spine, B, M, spine)
    M=M+1


