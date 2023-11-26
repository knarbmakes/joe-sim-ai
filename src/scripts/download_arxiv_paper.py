import requests
from bs4 import BeautifulSoup
import os
from concurrent.futures import ThreadPoolExecutor

# Ensure the downloads folder exists
os.makedirs('downloads', exist_ok=True)

# Function to download a single PDF
def download_pdf(pdf_url, filename):
    response = requests.get(pdf_url)
    response.raise_for_status()
    file_path = os.path.join('downloads', filename+'.pdf')
    with open(file_path, 'wb') as file:
        file.write(response.content)
    print(f'Downloaded {filename}.pdf')

# Endpoint for recent computer science submissions on arXiv
url = 'https://arxiv.org/list/cs/recent'

# Perform an HTTP GET request
response = requests.get(url)
response.raise_for_status()

# Parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')

# Find all 'dt' tags because they contain the paper links
paper_dt_tags = soup.find_all('dt')

# Download each paper using ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = []
    for paper_dt in paper_dt_tags:
        paper_link_tag = paper_dt.find('a', title='Download PDF')
        if paper_link_tag:
            pdf_href = paper_link_tag.get('href')
            if pdf_href.startswith('/'):
                pdf_href = f'https://arxiv.org{pdf_href}'
                filename = pdf_href.split('/')[-1]
                futures.append(executor.submit(download_pdf, pdf_href, filename))

    # Wait for all downloads to complete
    for future in futures:
        future.result()