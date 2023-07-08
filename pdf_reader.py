##### >>>> BOT
import PyPDF2

def get_pdf_content(file_path):
    pdf_file = open(file_path, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_file)
    num_pages = pdf_reader.numPages
    text_content = ""
    for num in range(num_pages):
        page = pdf_reader.getPage(num)
        text_content += page.extractText()
    pdf_file.close()
    return text_content
##### >>>> BOT
import PyPDF2

def get_pdf_content(file_path):
    with open(file_path, 'rb') as file:
        pdf = PyPDF2.PdfFileReader(file)
        text = ''
        for i in range(pdf.getNumPages()):
            text += pdf.getPage(i).extractText()
    return text
