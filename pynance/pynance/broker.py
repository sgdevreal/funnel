from abc import ABC, abstractmethod
from .ticker import Ticker
from .bond import Bond
from typing import List, Optional
from datetime import datetime
import pandas as pd

class Broker(ABC):
    def __init__(self, name: str, url: str = ""):
        self.name = name
        self.url = url
        self.listed_tickers: List[Ticker] = []
        self.lisbonds_bonds: List[Bond] = []
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

    def get_bond_dataframe(self) -> pd.DataFrame:
        """Returns a DataFrame with bond information and calculated yields."""
        bond_data = []
        
        for bond in self.lisbonds_bonds:
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


class KeytradeBroker(Broker):
    def __init__(self):
        super().__init__(
            'Keytrade broker', 
        )
    def scrape_tickers(self):
        return super().scrape_tickers()
    
    def scrape_bonds(self):
        df = pd.read_excel('pynance/data/export.xls')
        df['Durée de vie'] = pd.to_datetime(df['Durée de vie'].replace("-", None), format='%d/%m/%Y', errors='coerce')
        for _, row in df.iterrows():
            if row['Ask'] != "-":
                coupon = float(row['Coupon'].replace("%","").strip(" "))
                maturity = row['Durée de vie']
                bond = Bond(
                    name=row['Emetteur'],
                    coupon=coupon,
                    maturity=row['Durée de vie'],
                    price=float(row['Ask']),
                    isin=row.get('ISIN', ''),
                    volume=row.get('Volume',0)
                )
                self.lisbonds_bonds.append(bond)
        print(f" done, broker has {len(self.lisbonds_bonds)} bonds.")

