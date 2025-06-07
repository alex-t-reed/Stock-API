# Portfolio Tracker

Built with Python and Node.js (Express + EJS)

## Python Stock API

This project includes a Python API to fetch the current price of a specific stock by scraping Yahoo Finance and CNN Markets as a fallback.

### Requirements
- Python 3.x
- requests
- beautifulsoup4

Install dependencies:
```bash
pip install -r requirements.txt
```

### Usage Example
To fetch and print the price of AAPL, run:
```bash
python test.py
```

This will print the current prices for AAPL, GOOGL, AMZN, and TSLA, and handle errors gracefully.

### API
- `get_stock_price(symbol: str) -> float`: Fetches the current price for the given stock symbol. Raises an exception if the price cannot be fetched.

### Unit Testing
To run unit tests:
```bash
python -m unittest test_stock_api.py
```

### Error Handling
If the price cannot be fetched, an exception is raised and handled in the test scripts.