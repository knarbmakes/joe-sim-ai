import sys
from pdfminer.high_level import extract_text

# Simple script to extract text from a PDF and save to a file.
# Usage: python pdf_to_text.py input.pdf output.txt

def pdf_to_text(input_filepath, output_filepath):
    try:
        # Extract text from the PDF
        text = extract_text(input_filepath)
        # Save the extracted text to a file
        with open(output_filepath, 'w') as output_file:
            output_file.write(text)
        return True
    except Exception as e:
        print(f'An error occurred: {e}')
        return False

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python pdf_to_text.py input.pdf output.txt')
        sys.exit(1)
    input_filepath = sys.argv[1]
    output_filepath = sys.argv[2]
    success = pdf_to_text(input_filepath, output_filepath)
    if success:
        print(f'Text successfully extracted to {output_filepath}')
    else:
        print('Failed to extract text from the PDF.')
