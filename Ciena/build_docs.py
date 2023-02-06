from docx import Document
from docxcompose.composer import Composer
from docx import Document as Document_compose
import openpyxl
import argparse
import re
import glob
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# import ../db.py
from utils import *

DEBUG = True

def tprint(*args, **kwargs):
    tempa = ' '.join(str(a) for a in args)
    tempk = ' '.join([str(kwargs[k]) for k in kwargs])
    temp = tempa + ' ' + tempk # puts a space between the two for clean output
    print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + " :: " + temp)


def print_double_line():
	print("======================================================================================================")


def dprint(msg):
	if DEBUG:
		if type(msg) == list:
			for m in msg:
				tprint("Debug: {}".format(m))
		else:
			tprint("Debug: {}".format(msg))

def combine_word_documents(files,output):
    merged_document = Document()

    for index, file in enumerate(files):
        sub_doc = Document(file)

        # Don't add a page break if you've reached the last file.
        if index < len(files)-1:
           sub_doc.add_page_break()

        for element in sub_doc.element.body:
            merged_document.element.body.append(element)

    merged_document.save('merged_output.docx')

def combine_all_docx(files_list,output):
    number_of_sections=len(files_list)
    master = Document_compose(None)
    composer = Composer(master)
    for i in range(0, number_of_sections):
        doc_temp = Document_compose(files_list[i])
        composer.append(doc_temp)
    composer.save(output)
#For Example
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", type=str,help="Provide the config file in Microsoft Excel File,For Example: CATP_Master_Feature_List_ver5Jan23.xlsx", )
parser.add_argument("-o", "--output", type=str,help="Provide the output filename in Microsoft Excel File,For Example: CATP_Master_Result.xlsx", )
parser.add_argument("-f", "--folder", type=str,help="Provide the name of the folder where test case docs are located,For Example: test_cases_docs", )
 
args = parser.parse_args()

if args.config:
    config_xlsx = args.config
else:
    config_xlsx = input("Please enter the Excel file name(default:CATP_Master_Feature_List.xlsx):")

if config_xlsx == '':
        config_xlsx = "CATP_Master_Feature_List.xlsx"

if args.output:
	output_docx = args.output
else:
	output_docx = input("Please enter the output word doc name(default:output.docx):") 

if output_docx == '':
        output_docx = "output.docx"

if args.folder:
	docx_folder = args.folder
else:
	docx_folder = input("Please enter folder under the current directory where the test case docs reside(default:test_cases_docs_1):") 

if docx_folder == '':
    docx_folder = "test_cases_docs_1"

print_double_line()
print(f"Folder that contain all the test case docx = {docx_folder}")
print(f"Deployment requirment file In Microsoft Excel = {config_xlsx}")
print(f"Output File In Microsoft Word = {output_docx}")
print_double_line()  
# Define variable to load the dataframe
dataframe = openpyxl.load_workbook(config_xlsx)

# Define variable to read sheet
dataframe1 = dataframe.active
#for c in dataframe1['F']:
#    print(c.value)
must_list_dict = {re.search(r'\d+',c.coordinate).group():c.value for c in dataframe1['B'] if c.value is not None}
other_list_dict ={re.search(r'\d+',c.coordinate).group():c.value for c in dataframe1['E'] if c.value is not None}
#selected_list_dict =  {re.search(r"\d+",c.coordinate).group():c.value for c in dataframe1['F'] if c.value is not None and c.value != ' ' or c.value == 'x' or c.value == "X"}
selected_list_dict =  {re.search(r"\d+",c.coordinate).group():c.value for c in dataframe1['F'] if c.value is not None and c.value != ' ' and (c.value == 'x' or c.value == "X" or c.value == 'y' or c.value == 'Y' )}
must_selected_list_dict =  {re.search(r"\d+",c.coordinate).group():c.value for c in dataframe1['D'] if c.value is not None and c.value != ' ' and (c.value == 'x' or c.value == "X" or c.value == 'y' or c.value == 'Y' )}

dprint(f"must_list_dict = {must_list_dict}")
dprint(f"other_list_dict = {other_list_dict}")
      
dprint(f"selected_list_dict = {selected_list_dict}")
dprint(f"must_selected_list_dict = {must_selected_list_dict}")

other_list = []
#must_list = list(must_list_dict.values())
must_list = [must_list_dict[i] for i in must_selected_list_dict.keys()]
for k in selected_list_dict.keys():
    other_list.append(other_list_dict[k])
dprint(f"other_list = {other_list}")
dprint(f"must_list = {must_list}")
function_list_dict = {}

#Only must list needs to pop the first element which is the description of E column
#must_list.pop(0)   
#other_list has all the final selected test cases, not need to pop
#other_list.pop(0)
#print(must_list)
#print(other_list)
regex_index = r'[0-9.]{2,}' #this regex match 5.1, 5.1.1, 5.1.1.1 etc.  But will not match test_case_1 
must_list_num = []
other_list_num = []

for i in must_list:
    matched = re.match(regex_index,i)
    if matched:
        num = (matched.group())
        #print(num)
        must_list_num.append(num)
for i in other_list:
    matched = re.match(regex_index,i)
    if matched:
        num = (matched.group())
        #print(num)
        other_list_num.append(num)
dprint(f"must_list_num = {must_list_num}")
dprint(f"other_list_num = {other_list_num}")
     
test_files = []
for file in glob.glob(f"{docx_folder}\*.docx"):
    test_files.append(file)
dprint(test_files)
test_cases_dict = {}
for file in test_files:
    matched = re.search(regex_index,file)
    if matched:
        test_num = matched.group()
        test_num = test_num.rsplit('.',1)[0]
        test_cases_dict[test_num] = file
        continue

dprint(f"This is the dict with index: filename. test_cases_dict = {test_cases_dict}" )

build_tests = []                
for n in must_list_num :
   if n in test_cases_dict:
      build_tests.append(test_cases_dict[n])
dprint(build_tests)
for n in other_list_num:
    if n in test_cases_dict:
      build_tests.append(test_cases_dict[n])
dprint(build_tests)



##files_list = [ "Input1.docx", "Input2.docx", r"C:\Users\mzheng\Coding\Python\ixia_automation\words_automation\split_by_sections_3.docx" ]

## Or you can put all files in a single directory and use glob
##Calling the function
combine_all_docx(build_tests,output_docx)
print(f"Completed!")
print(f"Output file: {output_docx}")
