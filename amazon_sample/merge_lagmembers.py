#!/apollo/bin/env -e NEPython python
import sys
import re
import argparse
import os
import glob

def rewrite_attr_file(infile, attributes):
	tmp_file = "%s.tmp" % (infile)

	try:
		outfile = open(tmp_file, "w")
		outfile.write("\n".join(attributes))
		outfile.write("\n")
	except IOError, e:
		print "Failed to write temp file: %s - %s" % (tmp_file, e)
		sys.exit(1)
	else:
		outfile.close()

	## Replace original file with temp
	os.rename(tmp_file, infile)


def load_attributes(attrib_file, rewrite=True):
	lag_attrs = []
	other_attrs = []
	match_lag = re.compile("^[#]?LAG")

	
	try:
		fh = open(attrib_file, "r")

		for line in fh.readlines():
			## preserve empty lines
			if (line == "\n"):
				other_attrs.append("")
				continue

			line = line.strip()
			if (match_lag.match(line)):

				if (not line in lag_attrs):
					lag_attrs.append(line)
			else:
				if (not line in other_attrs):
					other_attrs.append(line)
			

	except IOError, e:
		print "Failed to load attribute file %s: %s" % (attrib_file, e)
	else:
		fh.close()

	## if we didn't find any LAG attributes, don't bother re-writing the file
	if (not len(lag_attrs) > 0):
		rewrite = False

	if (rewrite):
		print "Re-writing attributes for %s..." % (os.path.basename(attrib_file))
		rewrite_attr_file(attrib_file, other_attrs)
	# else:
	# 	print "No changes to %s" % (os.path.basename(attrib_file))

	return lag_attrs


def walk_attr_dir(attr_dir):
	## Walk through each attribute file in the directory
	## we're going to pull out all the LAG attributes into a list
	## all other lines will be written back out to a temp file
	## which is then swapped with the original

	match_path = os.path.join(attr_dir, "*.attr")

	lag_attrs = []
	for attrib_file in glob.glob(match_path):
		## skip symlinks - that'd just be messy
		if (os.path.islink(attrib_file)):
			continue

		result = load_attributes(attrib_file)

		lag_attrs = lag_attrs + result

	return lag_attrs



def clean_attributes(attribs):
	lags = {}
	clean_attribs = []
	

	## Remove duplicate lines - don't care about sorting since we're cleaning that up too
	for attr in list(set(attribs)):
		foo = attr.split()
		lag = foo[1]

		if (not lag in lags.keys()):
			lags[lag] = {'ipaddr':None, 'remhost':None,'remlag':None, 'members':[], 'attributes':[]}

		if (foo[2] == "MEMBER"):
			lags[lag]['members'].append(attr)

		elif (foo[2] == 'REMHOST'):
			lags[lag]['remhost'] = attr

		elif (foo[2] == 'REMLAG'):
			lags[lag]['remlag'] = attr

		elif (foo[2] == 'IPADDR'):
			lags[lag]['ipaddr'] = attr

		else:
			lags[lag]['attributes'].append(attr)

	
	## yay, we should be all cleaned up and sorted by LAG (hopefully)
	## let's order our output back into a list so we can write to the file
	for lag in lags:
		if (lags[lag]['remhost']):
			clean_attribs.append(lags[lag]['remhost'])

		if (lags[lag]['remlag']):
			clean_attribs.append(lags[lag]['remlag'])

		if (lags[lag]['ipaddr']):
			clean_attribs.append(lags[lag]['ipaddr'])

		for attribute in sorted(lags[lag]['attributes']):
			clean_attribs.append(attribute)

		for member in sorted(lags[lag]['members']):
			clean_attribs.append(member)


	return clean_attribs


def write_lag_attributes(target_file, lag_attributes):
	header = "###############################\n## Merged LAG attributes\n###############################\n"

	## write to a temp file, just in case our original file existed and was modified already
	output_file = "%s.tmp" % (target_file)

	try:
		outfile = open(output_file, "w")
		outfile.write(header)

		
		last_lag = None

		## little hack for formatting the LAGs into stanzas
		for attr in lag_attributes:
			foo = attr.split()
			cur_lag = foo[1]
			comment = ""

			if (foo[2] == "MEMBER"):
				if ((foo[3] == "TBD") or (foo[5] == "TBD")):
					## One of the interfaces is unknown - comment out the line
					comment = "#"

			if (last_lag):
				if (cur_lag != last_lag):
					outfile.write("\n")

			outfile.write("%s%s\n" % (comment,attr))

			last_lag = cur_lag
	except IOError, e:
		print "Failed to write output file: %s - %s" % (output_file, e)
		sys.exit(1)
	else:
		outfile.close()


	os.rename(output_file,target_file)








def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--dir", action="append", dest="attr_dir",help="Attribute directory to search for attributes to merge. You can specify multiple times.")
	parser.add_argument("-o", "--output", action="store", dest="out_file", help="Optional. Filename to write merged attributes. Defaults to ./lagmembers.attr")
	parser.add_argument("-f", "--file", action="append", dest="attr_file", help="Additional attribute files to load")
	args = parser.parse_args()

	lag_attributes = []

	## Walk any directories given
	if (args.attr_dir):
		for cur_dir in args.attr_dir:
			lag_attributes = lag_attributes + walk_attr_dir(cur_dir)


	## Load any additional files
	if (args.attr_file):
		for cur_file in args.attr_file:
			lag_attributes = lag_attributes + load_attributes(cur_file, False)
	

	output = args.out_file or "./lagmembers.attr"

	print "Writing merged LAG attributes to %s" % (output)
	write_lag_attributes(output, clean_attributes(lag_attributes))


if __name__ == "__main__":
	main()

