import aspose.words as aw

# load Word document
doc = aw.Document(r"C:\Users\mzheng\Coding\Python\ixia_automation\words_automation\doc2.docx")

# get page count
pageCount = doc.page_count

# loop through pages
for page in range(0, pageCount):
  
    # save each page as a separate document
    extractedPage = doc.extract_pages(page, 1)
    extractedPage.save(f"C:\\Users\\mzheng\\Coding\\Python\\ixia_automation\\words_automation\\split_by_sections_{page}.docx")
 