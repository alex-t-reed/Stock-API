import requests
from bs4 import BeautifulSoup
import re

def get_stock_price(symbol: str) -> float:
    """
    Fetches the current price for the given stock symbol by scraping Yahoo Finance or CNN Markets as fallback.
    Args:
        symbol (str): The stock ticker symbol (e.g., 'AAPL').
    Returns:
        float: The current stock price.
    Raises:
        Exception: If the request fails or the symbol is invalid.
    """
    # Try Yahoo Finance first
    url = f"https://finance.yahoo.com/quote/{symbol}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Try to find price using the container class
        container = soup.select_one('div.container.yf-16vvaki')
        if container:
            price_span = container.find('span')
            if price_span:
                try:
                    return float(price_span.text.replace(',', ''))
                except ValueError:
                    pass
        # Fallback: Use regex to find price pattern
        match = re.search(r'"currentPrice":\{"raw":([0-9.]+),', response.text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
    # Try CNN Markets as fallback
    cnn_url = f"https://www.cnn.com/markets/stocks/{symbol}"
    response = requests.get(cnn_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        price_div = soup.select_one('div.price-2tP9m2.cnn-pcl-kld3m4')
        if price_div:
            try:
                return float(price_div.text.replace(',', '').replace('$', ''))
            except ValueError:
                pass
        # Fallback: Use regex to find price pattern
        match = re.search(r'"price":\s*"([0-9.,]+)"', response.text)
        if match:
            try:
                return float(match.group(1).replace(',', ''))
            except ValueError:
                pass
    raise Exception(f"Could not fetch price for symbol: {symbol}")

# Example export usage:
__all__ = ['get_stock_price']