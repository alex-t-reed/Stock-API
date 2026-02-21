import unittest
from stock_api import get_stock_price

class TestStockAPI(unittest.TestCase):
    def test_valid_symbol(self):
        # Test with a valid symbol, should return a float greater than 0
        price = get_stock_price('AAPL')
        self.assertIsInstance(price, float)
        self.assertGreater(price, 0)

    def test_invalid_symbol(self):
        # Test with an invalid symbol, should raise Exception
        with self.assertRaises(Exception):
            get_stock_price('INVALIDSYMBOL123')

if __name__ == "__main__":
    unittest.main()
