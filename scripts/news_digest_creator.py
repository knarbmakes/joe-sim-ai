import os
import sys
import requests
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()

# Retrieve the API keys
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# News API URL for fetching top headlines
NEWS_API_URL = 'https://newsapi.org/v2/top-headlines'

# Set the headers with the News API Key
headers = {
    'Authorization': f'Bearer {NEWS_API_KEY}'
}

# Function to fetch top headlines
def fetch_top_headlines(topic):
    # Define the parameters for the query
    params = {
        'q': topic, # The topic to search for
        'language': 'en', # The language of the articles
        'pageSize': 5 # The number of articles to return
    }
    # Make the request to the News API
    response = requests.get(NEWS_API_URL, headers=headers, params=params)
    # Check if the response is successful
    if response.status_code == 200:
        # Extract the articles from the response
        return response.json().get('articles', [])
    else:
        # Return an error message if the call was unsuccessful
        return f'Error: {response.status_code} with message {response.json().get("message")}'

# Get topic from command line arguments
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python news_digest_creator.py <topic>')
        sys.exit(1)
    topic = sys.argv[1]
    articles = fetch_top_headlines(topic)
    if isinstance(articles, str):
        print(articles) # Print the error message
    else:
        for article in articles:
            print(f'{article.get("title")}\n{article.get("url")}\n{article.get("description")}\n')
