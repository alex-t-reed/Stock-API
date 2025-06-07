from stock_api import get_stock_price
import time

def print_prices(symbols):
    for symbol in symbols:
        try:
            price = get_stock_price(symbol)
            print(f"Current price of {symbol}: ${price}")
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
        time.sleep(1)  # Avoid rate limiting

if __name__ == "__main__":
    symbols = ['AAPL', 'GOOGL', 'AMZN', 'TSLA']
    print_prices(symbols)
    try:
        price = get_stock_price('AAPL')
        print(f"Current price of AAPL: ${price}")
    except Exception as e:
        print(f"Error fetching AAPL: {e}")
