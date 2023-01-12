from docx import Document
from docxcompose.composer import Composer
from docx import Document as Document_compose
import openpyxl
import argparse
import re

fileNames = [ "Input1.docx", "Input2.docx", r"C:\Users\mzheng\Coding\Python\ixia_automation\words_automation\split_by_sections_4.docx" ]


def combine_word_documents(files):
    merged_document = Document()

    for index, file in enumerate(files):
        sub_doc = Document(file)

        # Don't add a page break if you've reached the last file.
        if index < len(files)-1:
           sub_doc.add_page_break()

        for element in sub_doc.element.body:
            merged_document.element.body.append(element)

    merged_document.save('merged_output.docx')

def combine_all_docx(files_list):
    number_of_sections=len(files_list)
    master = Document_compose(None)
    composer = Composer(master)
    for i in range(0, number_of_sections):
        doc_temp = Document_compose(files_list[i])
        composer.append(doc_temp)
    composer.save("combined_file_1.docx")
#For Example
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", type=str,help="Provide the config file in Microsoft Excel File,For Example: CATP_Master_Feature_List_ver5Jan23.xlsx", )
parser.add_argument("-o", "--output", type=str,help="Provide the output filename in Microsoft Excel File,For Example: CATP_Master_Result.xlsx", )
 
args = parser.parse_args()

if args.config:
	config_xlsx = args.config
else:
	config_xlsx = input("Please enter the Excel file name(example:feature.xlsx):")

if args.output:
	output_docx = args.output
else:
	output_docx = input("Please enter the output word doc name(example:output.docx):")
print(f"Configure File In Microsoft Excel = {config_xlsx}")
print(f"Output File In Microsoft Word = {output_docx}")
  
# Define variable to load the dataframe
dataframe = openpyxl.load_workbook(config_xlsx)
 
# Define variable to read sheet
dataframe1 = dataframe.active
must_list = [c.value for c in dataframe1['B'] if c.value is not None]
other_list =[c.value for c in dataframe1['E'] if c.value is not None]
must_list.pop(0)
other_list.pop(0)
print(must_list)
print(other_list)
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
print(f"must_list_num = {must_list_num}")
print(f"other_list_num = {other_list_num}")
     

files_list = [ "Input1.docx", "Input2.docx", r"C:\Users\mzheng\Coding\Python\ixia_automation\words_automation\split_by_sections_3.docx" ]

# Or you can put all files in a single directory and use glob
#Calling the function
combine_all_docx(files_list)
