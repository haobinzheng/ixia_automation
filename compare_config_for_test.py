#!/usr/bin/python

import sys

import telnetlib

import re

import string

import time


#HOST = "10.105.240.31"


def get_switch_telnet_connection(ip_address, console_port):
	print("\nconsole server ip ="+str(ip_address))
	print("\nconsole port="+str(console_port))

	console_port_int = int(console_port)
	
	tn = telnetlib.Telnet(ip_address,console_port_int)

	print("successful login\n")


	tn.write('' + '\n')
	time.sleep(1)

	print("successful login\n")


	tn.write('' + '\n')
	time.sleep(1)

	print("successful login\n")

	
	tn.write('\x03')
	time.sleep(2)

	print("successful login\n")


	tn.write('\x03')
	time.sleep(2)

	print("successful login\n")


	tn.write('\x03')
	time.sleep(2)

	print("successful login\n")


	tn.read_until("login: ")

	tn.write('admin' + '\n')

	tn.read_until("Password: ")

	tn.write('' + '\n')

	#print("before the hash sign\n")

	tn.read_until("# ")

	print("successful login\n")

	tn.write('get system status\n')
	tn.read_until("# ")

	print("Return from telnet function\n")

	return tn
	
	
	


def retrieve_full_configuration(ip_address, port_number, file_name_where_to_save_output):


	tn = get_switch_telnet_connection(ip_address, port_number)

	tn.write('' + '\n')
	tn.read_until("# ")

	tn.write('config system console\n')
	tn.read_until("# ")

	tn.write('set output standard\n')
	tn.read_until("# ")

	tn.write('end\n')
	tn.read_until("# ")

	tn.write('show full-configuration\n')
	output = tn.read_until("# ")

	tn.close()

	file = open(file_name_where_to_save_output, 'w')
	file.write(output)
	file.close()


def compare_files_and_save_to_third_file(file1_in,file2_in,difference_file):

	with open(file1_in, 'r') as file1:
	    with open(file2_in, 'r') as file2:
        	same = set(file1).intersection(file2)

	same.discard('\n')

	with open(difference_file, 'w') as file_out:
	    for line in same:
        	file_out.write(line)
	
	file1.close()
	file2.close()
	file_out.close()


def compare_files_and_save_to_third_file_2(file1_in,file2_in,difference_file):

	file1 = open(file1_in, 'r')
	file2 = open(file2_in, 'r')
	FO = open(difference_file, 'w')

	for line1 in file1:
	    for line2 in file2:
        	if line1 == line2:
	            FO.write("%s\n" %(line1))

	FO.close()
	file1.close()
	file2.close()


def compare_files_and_save_to_third_file_3(file1_in,file2_in,difference_file):

	f1 = open(file1_in, 'r')
	f2 = open(file2_in, 'r')
	FO = open(difference_file, 'w')

	# Print confirmation
	print("-----------------------------------")
	print("Comparing files----"+file1_in+"----"+file2_in+"-----")
	print("-----------------------------------")


	# Read the first line from the files
	f1_line = f1.readline()
	f2_line = f2.readline()

	# Initialize counter for line number
	line_no = 1

	# Loop if either file1 or file2 has not reached EOF
	while f1_line != '' or f2_line != '':

	    # Strip the leading whitespaces
	    f1_line = f1_line.rstrip()
	    f2_line = f2_line.rstrip()
    
	    # Compare the lines from both file
	    if f1_line != f2_line:
		FO.write("First_File--"+str(f1_line)+"\n")
		FO.write("second_File--"+str(f2_line)+"\n")
		FO.write("=================================================================\n")

    	    #Read the next line from the file
	    f1_line = f1.readline()
	    f2_line = f2.readline()


	    #Increment line counter
	    line_no += 1

	# Close the files
	f1.close()
	f2.close()

	FO.close()


def compare_files_and_save_to_third_file_4(file1_in,file2_in,difference_file):

	f1 = open(file1_in, 'r')
	number_of_lines1 = 0
	for line in f1:
		number_of_lines1 = number_of_lines1 + 1
	f1.close()


	
	f2 = open(file2_in, 'r')
	number_of_lines2 = 0
	for line in f2:
		number_of_lines2 = number_of_lines2 + 1
	f2.close()

	

	# Print confirmation
	print("-----------------------------------")
	print("Comparing files----"+file1_in+"----"+file2_in+"-----")
	print(" Number of lines in first file = "+str(number_of_lines1))
	print(" Number of lines in second file = "+str(number_of_lines2))

	print("-----------------------------------")

	
	
	if(number_of_lines1 >= number_of_lines2):

		f1 = open(file1_in, 'r')	
		f2 = open(file2_in, 'r')
		FO = open(difference_file, 'w')

		shorlines = set(line.rstrip() for line in f2)
		
		
		for line in f1:
			line = line.rstrip()
			if line not in shorlines:
				FO.write("\n============================================\n")
				FO.write(line)
				FO.write("\n")
		f1.close()
		f2.close()
		FO.close()
	elif(number_of_lines2 > number_of_lines1):
		f1 = open(file1_in, 'r')	
		f2 = open(file2_in, 'r')
		FO = open(difference_file, 'w')

		shorlines = set(line.rstrip() for line in f1)
		
		for line in f2:
			line = line.rstrip()
			if line not in shorlines:
				FO.write("\n============================================\n")
				FO.write(line)
				FO.write("\n")
		f1.close()
		f2.close()
		FO.close()
	else:
		print("Something Wrong With Number of lines")



			
def compare_files_and_save_to_third_file_5(file1_in,file2_in,difference_file):

	f1 = open(file1_in, 'r')
	number_of_lines1 = 0
	for line in f1:
		number_of_lines1 = number_of_lines1 + 1
	f1.close()


	
	f2 = open(file2_in, 'r')
	number_of_lines2 = 0
	for line in f2:
		number_of_lines2 = number_of_lines2 + 1
	f2.close()

	

	# Print confirmation
	print("-----------------------------------")
	print("Comparing files----"+file1_in+"----"+file2_in+"-----")
	print(" Number of lines in first file = "+str(number_of_lines1))
	print(" Number of lines in second file = "+str(number_of_lines2))

	print("-----------------------------------")

	flag_begin_certificate = 0
	flag_dek_info = 0
	
	if(number_of_lines1 >= number_of_lines2):

		f1 = open(file1_in, 'r')	
		f2 = open(file2_in, 'r')
		FO = open(difference_file, 'w')

		shorlines = set(line.rstrip() for line in f2)
		for line in f1:
			line = line.rstrip()
			if(flag_begin_certificate == 1 and "END CERTIFICATE" not in line):
				continue
			elif("END CERTIFICATE" in line):
				flag_begin_certificate = 0
				continue
			elif("BEGIN CERTIFICATE" in line):
				flag_begin_certificate = 1
				continue
			elif("ENC" in line):
				continue
			elif("DEK-Info" in line):
				flag_dek_info = 1
				continue
			elif(flag_dek_info == 1	and "END RSA PRIVATE KEY" not in line):
				continue
			elif("END RSA PRIVATE KEY" in line):
				flag_dek_info = 0
				continue
			elif("conf_file_ver" in line):
				continue
			elif("show full-configuration" in line):
				continue
			elif line not in shorlines:
				FO.write("\n============================================\n")
				FO.write(line)
				FO.write("\n")
		f1.close()
		f2.close()
		FO.close()
	elif(number_of_lines2 > number_of_lines1):
		f1 = open(file1_in, 'r')	
		f2 = open(file2_in, 'r')
		FO = open(difference_file, 'w')

		shorlines = set(line.rstrip() for line in f1)
		
		for line in f2:
			line = line.rstrip()
			if(flag_begin_certificate == 1 and "END CERTIFICATE" not in line):
				continue
			elif("END CERTIFICATE" in line):
				flag_begin_certificate = 0
				continue
			elif("BEGIN CERTIFICATE" in line):
				flag_begin_certificate = 1
				continue
			elif("ENC" in line):
				continue
			elif("DEK-Info" in line):
				flag_dek_info = 1
				continue
			elif(flag_dek_info == 1	and "END RSA PRIVATE KEY" not in line):
				continue
			elif("END RSA PRIVATE KEY" in line):
				flag_dek_info = 0
				continue
			elif("conf_file_ver" in line):
				continue
			elif("show full-configuration" in line):
				continue
			elif line not in shorlines:
				FO.write("\n============================================\n")
				FO.write(line)
				FO.write("\n")
		f1.close()
		f2.close()
		FO.close()
	else:
		print("Something Wrong With Number of lines")		




if __name__ == "__main__":

	if(len(sys.argv) < 2):
		print("Need function name - RETRIEVE or COMPARE")
		sys.exit(1)

	retrieve_or_compare = sys.argv[1]

	if(retrieve_or_compare == 'RETRIEVE'):
		if(len(sys.argv) < 4):
			print('retrieving the full configuration, required parameters = 5\n')
			print('0- python file name')
			print('1- Retrieve or compare')
			print('2 - ip address')
			print('3 - port_number')
			print('4 - file_where_to_save')
			sys.exit(1)
		else:
			ip_address = sys.argv[2]
			port_number = sys.argv[3]
			file_name_to_save = sys.argv[4]
			retrieve_full_configuration(ip_address,port_number,file_name_to_save)

	elif(retrieve_or_compare == 'COMPARE'):
		if(len(sys.argv) < 5):
			print('Comparing files required parameters = 5\n')
			print('0- python file name')
			print('1- Retrieve or compare')
			print('2 - first_file to compare')
			print('3 - second_file to compare')
			print('4 - file where to write comparision')
			sys.exit(1)
		else:
			first_file = sys.argv[2]
			second_file = sys.argv[3]
			compare_file = sys.argv[4]
			compare_files_and_save_to_third_file_5(first_file,second_file,compare_file)
	else:
		print("Need function name - RETRIEVE or COMPARE")
		sys.exit(1)


		
			

		

		
