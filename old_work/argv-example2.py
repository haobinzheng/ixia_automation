#!/usr/bin/env python

import sys

lower = 'abcdefifdsfdafdfa'
upper = 'ABCDDFDFAFDFSCDAF'
u_dict = {}
l_dict = {}

for c in lower:
	l_dict.setdefault(c,0)
for c in upper:
	u_dict.setdefault(1,0)


filename = sys.argv[1]

try:	
	with open(filename) as f:
		filedata = f.read()
except EnvironmentError:
	print "Problem with opening file!"

for line in filedata:
	for char in line:
		if char in lower:
			l_dict[char] += 1
		elif char in upper:
			u_dirt[char] +=  1

for k in sorted(l_dict):
	print "cout of %s:%s" % (k,l_dict[k])

for k in sorted(u_dict):
	print "count of %s: %s" % (k, u_dict[k])