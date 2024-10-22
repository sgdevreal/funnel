import yfinance as yf
import pandas as pd
from typing import Optional, List, Any, Dict

class Ticker:
    def __init__(self, symbol: str, name: str, yf_symbol: str, isin: Optional[str] = None):
        self.symbol = symbol
        self.name = name
        self.yf_symbol = yf_symbol
        self.isin = isin
        self.cash_flows: Optional[List[float]] = None
        self.discount_rate: Optional[float] = None
        self.terminal_growth_rate: Optional[float] = None
        self.value: Optional[float] = None  # Stores DCF or other valuation results
        self.yf_data: Optional[Any] = None  # To cache Yahoo Finance data
        self.yf_financials: Optional[pd.DataFrame] = None  # To store financial data
        self.yf_cashflow: Optional[pd.DataFrame] = None  # To store cashflow data
        self.yf_info: Optional[Dict] = None

    def __repr__(self):
        return f"Ticker({self.symbol}, {self.name}, {self.isin or 'No ISIN'})"

    def set_user_data(self, **kwargs) -> None:
        """Generic method to dynamically set attributes. Can add new attributes if needed."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                setattr(self, key, value)  # Allow adding new attributes dynamically
                print(f"Info: Added '{key}' as a new attribute to the Ticker class.")

    def validate_data(self, required_fields: List[str]) -> bool:
        """Validates presence of required fields before performing operations."""
        missing_fields = [field for field in required_fields if getattr(self, field, None) is None]
        if missing_fields and self.yf_data is None:
            print(f"Missing data, Retrieving data")
            self.get_data_from_yf()
            return self.validate_data(required_fields)
        elif missing_fields:
            print(f"Missing data for {self.symbol}: {', '.join(missing_fields)}")
            return False
        return True

    def compute_dcf(self) -> Optional[float]:
        """Calculate the Discounted Cash Flow (DCF) valuation."""
        required_fields = ['cash_flows', 'discount_rate', 'terminal_growth_rate']
        if not self.validate_data(required_fields):
            print(f"Cannot compute DCF valuation for {self.symbol}. Insufficient data.")
            return None

        total_value = sum(cash_flow / (1 + self.discount_rate)**t for t, cash_flow in enumerate(self.cash_flows, start=1))

        terminal_value = (self.cash_flows[-1] * (1 + self.terminal_growth_rate)) / (self.discount_rate - self.terminal_growth_rate)
        terminal_value /= (1 + self.discount_rate)**len(self.cash_flows)
        
        self.value = total_value + terminal_value
        return self.value

    def get_data_from_yf(self, reset: bool = False) -> None:
        """Fetches data from Yahoo Finance based on yf_symbol and caches it.
        
        Parameters:
        - reset (bool): If True, will reset the cached data and fetch it again.
        """
        if not reset and self.yf_data:
            print(f"Using cached data for {self.symbol}.")
            return

        try:
            ticker_data = yf.Ticker(self.yf_symbol)
            self.yf_data = ticker_data  # Cache the data obj
            # Fetch cash flows and financials
            self.yf_cashflow = ticker_data.cashflow if not ticker_data.cashflow.empty else None
            self.yf_financials = ticker_data.financials if not ticker_data.financials.empty else None
            self.yf_info = ticker_data.info if len(ticker_data.info) != 0 else None
            # Populate cash_flows from yf_cashflow (Assuming 'Total Cash From Operating Activities' is relevant)
            if self.yf_cashflow is not None:
                self.cash_flows = self.yf_cashflow.loc['Free Cash Flow'].dropna().values.tolist()

            # Extract relevant financial data (like Net Income, EBITDA, etc.)
            if self.yf_financials is not None:
                self.net_income = self.yf_financials.loc['Net Income'].dropna().values.tolist() if 'Net Income' in self.yf_financials.index else None
                self.ebitda = self.yf_financials.loc['EBITDA'].dropna().values.tolist() if 'EBITDA' in self.yf_financials.index else None
                    # Fetch or estimate discount rate
            # Example: Assuming a default discount rate of 8%
            self.discount_rate = 0.08  # Replace with your logic or data if available
            
            # Fetch or estimate terminal growth rate
            # Example: Assuming a default terminal growth rate of 3%
            self.terminal_growth_rate = 0.03  # Replace with your logic or data if available

        except Exception as e:
            print(f"Error fetching data for {self.symbol}: {e}")
            self.yf_data = None  # Clear cache if there's an error

    def reset_yf_data(self) -> None:
        """Resets the cached Yahoo Finance data."""
        self.yf_data = None
        print(f"Cache for {self.symbol} has been reset.")

    def get_yf_marketcap(self) -> int:
        """Returns market cap valuation from ahoo fincance, fetches it if not available"""
        if self.yf_data is None:
            self.get_data_from_yf()
        if self.yf_info is not None:
            return self.yf_info['marketCap']
        else:
            return None

