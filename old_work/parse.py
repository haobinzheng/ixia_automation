import os
import sys
import re


def main():
	filename = sys.argv[1] 
	print filename
	with open(filename, 'r') as f:
		pattern = r' +Network +Next +'
		for line in f:
			found = re.search(pattern, line)
			if found != None:
				print found.group()
			
if __name__ == "__main__":
	main()
	exit(1)
