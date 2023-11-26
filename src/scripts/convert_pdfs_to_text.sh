#!/bin/bash
# Navigate to the downloads directory
cd downloads

# Iterate over all PDF files in the current directory
for pdf in *.pdf; do
    # Use the pdf_to_text.py script to convert the PDF to text
    python3 ../scripts/pdf_to_text.py "$pdf"
done