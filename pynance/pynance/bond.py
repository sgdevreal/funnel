from datetime import datetime
from typing import Optional

class Bond:
    def __init__(self, name: str, coupon: float, maturity: datetime, price: float, isin: str = "", symbol: Optional[str] = None, inflation_rate: Optional[float] = 0.02,volume: int = 0):
        self.symbol = symbol
        self.name = name
        self.isin = isin
        self.coupon = self._validate_coupon(coupon)
        self.maturity = self._validate_maturity(maturity)
        self.price = price  # in % of nominal value (assumed face value = 100)
        self.face_value = 100  # Assumed face value of the bond
        self.tax_rate = 0.30  # 30% tax on coupon
        self.inflation_rate = inflation_rate  # Expected inflation rate
        self.volume = volume

    def __repr__(self) -> str:
        return f"Bond(symbol={self.symbol!r}, name={self.name!r}, isin={self.isin!r}, coupon={self.coupon}, maturity={self.maturity}; price={self.price})"

    def __str__(self) -> str:
        return f"{self.name} ({self.isin}): Coupon {self.coupon}% - Matures on {self.maturity.strftime('%d-%b-%Y')} - Price: {self.price}%"

    @staticmethod
    def _validate_coupon(coupon: float) -> float:
        if coupon < 0:
            raise ValueError("Coupon rate cannot be negative.")
        return coupon

    @staticmethod
    def _validate_maturity(maturity: datetime) -> datetime:
        if maturity < datetime.now():
            raise ValueError("Maturity date must be in the future.")
        return maturity

    @property
    def time_to_maturity(self) -> int:
        """Returns the number of days until the bond matures."""
        return (self.maturity - datetime.now()).days

    def years_to_maturity(self) -> float:
        """Returns the number of years until the bond matures."""
        return self.time_to_maturity / 365

    def yield_to_maturity(self) -> float:
        """Calculate the Yield to Maturity (YTM) based on cash flows."""
        cash_flows = []
        years = int(self.years_to_maturity())
        for year in range(0, years + 1):
            coupon_payment = ( self.coupon / 100 ) * (1 - self.tax_rate)  * self.face_value
            cash_flows.append(coupon_payment)
        cash_flows[-1] += self.face_value
        
        total_cash_flows = sum(cash_flows)
        
        # Calculate nominal YTM
        nominal_ytm = ( total_cash_flows / self.price ) ** ( 1 / self.years_to_maturity()) -1

        # Adjust for inflation to get real yield
        real_ytm = (1 + nominal_ytm) / (1 + self.inflation_rate) - 1

        return nominal_ytm.real, real_ytm.real