import sys
from PyPDF2 import PdfReader

# Here we're assuming that the first argument to the script is the PDF file name,
# and the script resides in the same directory as the PDF file.
pdf_file_path = sys.argv[1]
text_file_path = sys.argv[1].replace('.pdf', '.txt')

# Create a new PdfReader.
pdf = PdfReader(pdf_file_path)

text_content = ''

# Extract text from each page of the PDF.
for page in pdf.pages:
    text_content += page.extract_text() + '\n'

# Write the extracted text to a text file.
with open(text_file_path, 'w', encoding='utf-8') as text_file:
    text_file.write(text_content)

print(f'Text extracted from {pdf_file_path} to {text_file_path}')