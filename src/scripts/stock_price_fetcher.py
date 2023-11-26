import requests
from bs4 import BeautifulSoup
import sys

# Mapping of known ticker changes - this can be updated as needed
TICKER_CHANGES = {
    'FB': 'META',
    # Add more mappings here as they occur
}

def fetch_stock_price(ticker):
    url = f"https://finance.yahoo.com/quote/{ticker}"
    response = requests.get(url)
    if response.status_code != 200:
        # Handle response errors (page not found, server error, etc.)
        return f"Error fetching stock data: {response.status_code}"
    
    soup = BeautifulSoup(response.text, 'html.parser')
    price_tag = soup.find('fin-streamer', {'data-symbol': ticker})
    
    if not price_tag:
        new_ticker = TICKER_CHANGES.get(ticker)
        if new_ticker:
            print(f"Redirecting to new ticker symbol: {new_ticker}")
            return fetch_stock_price(new_ticker)
        return f"Stock ticker {ticker} not found."
    
    return price_tag['value']

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python stock_price_fetcher.py <ticker>")
        sys.exit(1)
    ticker = sys.argv[1]
    price = fetch_stock_price(ticker)
    print(f"Current price of {ticker} stock: {price}")
