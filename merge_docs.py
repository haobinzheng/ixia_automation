from docx import Document
from docxcompose.composer import Composer
from docx import Document as Document_compose

files = ['Input1.docx', 'Input2.docx']

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

def combine_all_docx(filename_master,files_list):
    number_of_sections=len(files_list)
    master = Document_compose(filename_master)
    composer = Composer(master)
    for i in range(0, number_of_sections):
        doc_temp = Document_compose(files_list[i])
        composer.append(doc_temp)
    composer.save("combined_file.docx")
#For Example
filename_master="file1.docx"
#files_list=["file2.docx","file3.docx","file4.docx",file5.docx"]
files_list=["Input1.docx","Input2.docx"]
# Or you can put all files in a single directory and use glob
#Calling the function
combine_all_docx(filename_master,files_list)
