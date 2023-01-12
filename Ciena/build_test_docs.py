from docx import Document
from docxcompose.composer import Composer
from docx import Document as Document_compose
import openpyxl
import argparse
import re
import glob



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
 
args = parser.parse_args()

if args.config:
    config_xlsx = args.config
else:
    config_xlsx = input("Please enter the Excel file name(example:CATP_Master_Feature_List_ver5Jan23.xlsx):")

if config_xlsx == '':
        config_xlsx = "CATP_Master_Feature_List_ver5Jan23.xlsx"

if args.output:
	output_docx = args.output
else:
	output_docx = input("Please enter the output word doc name(example:output.docx):") 

if output_docx == '':
        output_docx = "output.docx"

print(f"Configure File In Microsoft Excel = {config_xlsx}")
print(f"Output File In Microsoft Word = {output_docx}")
  
# Define variable to load the dataframe
dataframe = openpyxl.load_workbook(config_xlsx)

# Define variable to read sheet
dataframe1 = dataframe.active
#for c in dataframe1['J']:
#    print(c.value)
must_list_dict = {re.search(r'\d+',c.coordinate).group():c.value for c in dataframe1['B'] if c.value is not None}
other_list_dict ={re.search(r'\d+',c.coordinate).group():c.value for c in dataframe1['E'] if c.value is not None}
#selected_list_dict =  {re.search(r"\d+",c.coordinate).group():c.value for c in dataframe1['J'] if c.value is not None and c.value != ' ' or c.value == 'x' or c.value == "X"}
selected_list_dict =  {re.search(r"\d+",c.coordinate).group():c.value for c in dataframe1['J'] if c.value is not None and c.value != ' ' and (c.value == 'x' or c.value == "X")}

print(must_list_dict,other_list_dict,selected_list_dict)

other_list = []
must_list = list(must_list_dict.values())
for k in selected_list_dict.keys():
    other_list.append(other_list_dict[k])
print(f"other_list- = {other_list}")
function_list_dict = {}

must_list.pop(0)
#other_list.pop(0)
#print(must_list)
#print(other_list)
regex_index = r'[0-9.]+'
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
#print(f"must_list_num = {must_list_num}")
print(f"other_list_num = {other_list_num}")
     
test_files = []
for file in glob.glob("test_cases_docs\*.docx"):
    test_files.append(file)
#print(test_files)
test_cases_dict = {}
for file in test_files:
    matched = re.search(regex_index,file)
    if matched:
        test_num = matched.group()
        test_num = test_num.rsplit('.',1)[0]
        test_cases_dict[test_num] = file
        continue

print(test_cases_dict)

build_tests = []                
for n in must_list_num :
   if n in test_cases_dict:
      build_tests.append(test_cases_dict[n])
#print(build_tests)
for n in other_list_num:
    if n in test_cases_dict:
      build_tests.append(test_cases_dict[n])
print(build_tests)



##files_list = [ "Input1.docx", "Input2.docx", r"C:\Users\mzheng\Coding\Python\ixia_automation\words_automation\split_by_sections_3.docx" ]

## Or you can put all files in a single directory and use glob
##Calling the function
combine_all_docx(build_tests,output_docx)
print(f"Completed!")
print(f"Output file: {output_docx}")
