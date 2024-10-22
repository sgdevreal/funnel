from abc import ABC, abstractmethod
from typing import List, Optional
from .ticker import Ticker
from .bond import Bond
import pandas as pd
import yfinance as yf
from io import BytesIO
import requests
from datetime import datetime

class Exchange(ABC):
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url
        self.tickers: List[Ticker] = []
        self.bonds: List[Bond] = []
        self.last_updated: Optional[datetime] = None

    @abstractmethod
    def scrape_tickers(self):
        """Scrape tickers from the exchange and populate the tickers list."""
        pass

    @abstractmethod
    def scrape_bonds(self):
        """Scrape bonds from the exchange and populate the bonds list."""
        pass

    def list_tickers(self):
        """Print the list of tickers."""
        if self.tickers:
            for ticker in self.tickers:
                print(ticker)
        else:
            print("No tickers found.")

    def list_bonds(self):
        """Print the list of bonds."""
        if self.bonds:
            for bond in self.bonds:
                print(bond)
        else:
            print("No bonds found.")

class EuronextBrussels(Exchange):
    def __init__(self):
        super().__init__(
            'Brussels Stock Market', 
            "https://live.euronext.com/en/pd_es/data/stocks/download?mics=XBRU%2CALXB%2CMLXB%2CTNLB%2CENXB&initialLetter=&fe_type=excel&fe_decimal_separator=.&fe_date_format=d%2Fm%2FY"
        )

        self.url_bond = "https://live.euronext.com/en/pd/data/bond/download?mics=ALXB%2CXBRU%2CMLXB%2CENXB&display_datapoints=dp_bond&display_filters=df_bond2?bondIssuerType=1&initialLetter=&fe_type=csv&fe_layout=ver&fe_decimal_separator=.&fe_date_format=d%2Fm%2FY"
    
    def scrape_tickers(self):
        print("Scraping tickers ...", end="")
        response = self._fetch_data(self.url)
        if response is not None:
            df_full = pd.read_excel(BytesIO(response.content))
            df = df_full[3:]  # Remove headers

            for _, row in df.iterrows():
                ticker_symbol = row.get('Symbol')
                if pd.notna(ticker_symbol) and row.get('Market', '').split(',')[0] == 'Euronext Brussels':
                    ticker = Ticker(
                        symbol=ticker_symbol,
                        yf_symbol=f"{ticker_symbol}.BR",
                        name=row.get('Name'),
                        isin=row.get('ISIN'),
                    )
                    self.tickers.append(ticker)
            print(f" done, exchange has {len(self.tickers)} tickers.")
        else:
            print("Error fetching ticker data.")

    def scrape_bonds(self):
        print("Scraping bonds ...", end="")
        response = self._fetch_data(self.url_bond)
        if response is not None:
            df = pd.read_csv(BytesIO(response.content), sep=";", skiprows=[1, 2, 3], usecols=[i for i in range(15)],encoding="latin_1")
            
            # Clean and parse coupon and maturity
            df['coupon'] = df['Name'].str.extract(r'(\d+[.,]?\d*)%')[0].str.replace(',', '.').astype(float)
            df['Maturity'] = pd.to_datetime(df['Maturity'].replace("-", None), format='%d/%m/%Y', errors='coerce')

            for _, row in df.iterrows():
                if pd.notna(row['coupon']) and pd.notna(row['Maturity']) and row['Maturity'] > datetime.now() and row['Last'] != "-":
                    bond = Bond(
                        name=row['Name'],
                        coupon=row['coupon'],
                        maturity=row['Maturity'],
                        price=float(row['Last']),
                        isin=row.get('ISIN', ''),
                        volume=row.get('Volume',0)
                    )
                    self.bonds.append(bond)
            print(f" done, exchange has {len(self.bonds)} bonds.")
        else:
            print("Error fetching bond data.")

    def _fetch_data(self, url: str) -> Optional[requests.Response]:
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def get_bond_dataframe(self) -> pd.DataFrame:
        """Returns a DataFrame with bond information and calculated yields."""
        bond_data = []
        
        for bond in self.bonds:
            print(bond)
            nominal_ytm, real_ytm = bond.yield_to_maturity()
            bond_data.append({
                'Name': bond.name,
                'ISIN': bond.isin,
                'Coupon (%)': bond.coupon,
                'Maturity': bond.maturity.strftime('%Y-%m-%d'),
                'Price (%)': bond.price,
                'Nominal YTM (%)': nominal_ytm * 100,
                'Real YTM (%)': real_ytm * 100,
                'Nominal YTM': nominal_ytm,
                'Real YTM': real_ytm,
                'Volume':bond.volume
            })
        
        return pd.DataFrame(bond_data)




class EuronextParis(Exchange):
    def __init__(self):
        super().__init__(
            'Paris Stock Market', 
            "https://live.euronext.com/en/pd_es/data/stocks/download?mics=XBRU%2CALXB%2CMLXB%2CTNLB%2CENXB&initialLetter=&fe_type=excel&fe_decimal_separator=.&fe_date_format=d%2Fm%2FY"
        )

        self.url_bond = "https://live.euronext.com/en/pd/data/bond/download?mics=ALXP%2CXPAR%2CXMLI&display_datapoints=dp_bond&display_filters=df_bond2?initialLetter=&fe_type=csv&fe_layout=ver&fe_decimal_separator=.&fe_date_format=d%2Fm%2FY"
    
    def scrape_tickers(self):
        print("Scraping tickers ...", end="")
        response = self._fetch_data(self.url)
        if response is not None:
            df_full = pd.read_excel(BytesIO(response.content))
            df = df_full[3:]  # Remove headers

            for _, row in df.iterrows():
                ticker_symbol = row.get('Symbol')
                if pd.notna(ticker_symbol) and row.get('Market', '').split(',')[0] == 'Euronext Brussels':
                    ticker = Ticker(
                        symbol=ticker_symbol,
                        yf_symbol=f"{ticker_symbol}.BR",
                        name=row.get('Name'),
                        isin=row.get('ISIN'),
                    )
                    self.tickers.append(ticker)
            print(f" done, exchange has {len(self.tickers)} tickers.")
        else:
            print("Error fetching ticker data.")

    def scrape_bonds(self):
        print("Scraping bonds ...", end="")
        response = self._fetch_data(self.url_bond)
        if response is not None:
            df = pd.read_csv(BytesIO(response.content), sep=";", skiprows=[1, 2, 3], usecols=[i for i in range(15)],encoding="latin_1")
            
            # Clean and parse coupon and maturity
            df['coupon'] = df['Name'].str.extract(r'(\d+[.,]?\d*)%')[0].str.replace(',', '.').astype(float)
            df['Maturity'] = pd.to_datetime(df['Maturity'].replace("-", None), format='%d/%m/%Y', errors='coerce')

            for _, row in df.iterrows():
                if pd.notna(row['coupon']) and pd.notna(row['Maturity']) and row['Maturity'] > datetime.now() and row['Last'] != "-":
                    bond = Bond(
                        name=row['Name'],
                        coupon=row['coupon'],
                        maturity=row['Maturity'],
                        price=float(row['Last']),
                        isin=row.get('ISIN', ''),
                        volume=row.get('Volume',0)
                    )
                    self.bonds.append(bond)
            print(f" done, exchange has {len(self.bonds)} bonds.")
        else:
            print("Error fetching bond data.")

    def _fetch_data(self, url: str) -> Optional[requests.Response]:
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def get_bond_dataframe(self) -> pd.DataFrame:
        """Returns a DataFrame with bond information and calculated yields."""
        bond_data = []
        
        for bond in self.bonds:
            print(bond)
            nominal_ytm, real_ytm = bond.yield_to_maturity()
            bond_data.append({
                'Name': bond.name,
                'ISIN': bond.isin,
                'Coupon (%)': bond.coupon,
                'Maturity': bond.maturity.strftime('%Y-%m-%d'),
                'Price (%)': bond.price,
                'Nominal YTM (%)': nominal_ytm * 100,
                'Real YTM (%)': real_ytm * 100,
                'Nominal YTM': nominal_ytm,
                'Real YTM': real_ytm,
                'Volume':bond.volume
            })
        
        return pd.DataFrame(bond_data)