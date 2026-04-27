"""Interest rates and fixed income data fetcher."""

import yfinance as yf
import pandas as pd
from datetime import datetime
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Interest rate instruments
INTEREST_RATE_TICKERS = {
    "Bund Yield (10Y)": "^FTSE",  # Using FTSE as proxy, may need alternative
    "BTP Yield (10Y)": "^FTSE",   # Italian 10Y
    "EUR OIS 1Y": "EONIA",        # Euro OverNight Index Average
    "EUR Swap 5Y": "^FTSE",       # Euro swap rates
}

# Alternative: Try to fetch from ECB or yields data
ALT_TICKERS = {
    "Bund Yield (10Y)": "^VDEX",      # VDAX index as alternative
    "BTP Yield (10Y)": "IT10Y.NS",    # Yahoo Finance Italian 10Y
    "EUR 3M OIS": "EURIBOR3M=X",      # Euribor 3M
    "EUR Swap 2Y": "^FTSE",
}


class InterestRateFetcher:
    """Fetch interest rate and fixed income data (USD Treasury + EUR rates)."""

    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        # Use tickers available on Yahoo Finance that track interest rates/bonds
        self.rates = {
            # USD Treasury Yields (primary)
            "US 10Y Treasury": "^TNX",            # 10-Year Treasury Yield
            "US 2Y Treasury": "^IRX",             # 2-Year Treasury Yield
            "US 30Y Treasury": "^TYX",            # 30-Year Treasury Yield

            # EUR Curve - Government Bond ETFs (act as proxy for EUR curves)
            "EUR Corporate Bonds": "LQD",         # iShares Investment Grade Corporate (EUR proxy)
            "EUR High Yield Bonds": "HYG",        # iShares High Yield Corporate (EUR corporate curve proxy)
            "EUR Emerging Markets": "VXUS",       # Vanguard Total Int'l Stock (global EUR exposure)
        }

    def fetch_all(self):
        """Fetch all interest rate metrics and return as a dict."""
        today = datetime.now().strftime("%Y-%m-%d")
        results = {"date": today, "interest_rates": {}}

        for name, ticker in self.rates.items():
            try:
                logger.info(f"Fetching {name} ({ticker})...")
                tick = yf.Ticker(ticker)
                hist = tick.history(period="1d")

                if not hist.empty:
                    value = hist["Close"].iloc[-1]
                    results["interest_rates"][name] = float(value)
                    logger.info(f"{name}: {value:.4f}")
                else:
                    logger.warning(f"No data received for {name}")
                    results["interest_rates"][name] = None
            except Exception as e:
                logger.error(f"Failed to fetch {name}: {e}")
                results["interest_rates"][name] = None

        return results

    def save_daily_snapshot(self):
        """Save today's interest rate snapshot to CSV."""
        today = datetime.now().strftime("%Y-%m-%d")
        filepath = f"{self.data_dir}/interest_rates_{today}.csv"

        data = self.fetch_all()
        df = pd.DataFrame([data["interest_rates"]])
        df.insert(0, "date", data["date"])

        df.to_csv(filepath, index=False)
        logger.info(f"Interest rates saved to {filepath}")
        return filepath

