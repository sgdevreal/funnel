# tests/test_ticker.py
import unittest
from pynance.ticker import Ticker

class TestTicker(unittest.TestCase):
    def test_ticker_creation(self):
        ticker = Ticker("AAPL", "Apple Inc.", 175.0)
        self.assertEqual(ticker.symbol, "AAPL")
        self.assertEqual(ticker.price, 175.0)

if __name__ == '__main__':
    unittest.main()