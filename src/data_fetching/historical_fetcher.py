"""Historical data fetcher - Retrieves 3-4 years of daily data for all risk factors."""

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path
import json

from src.utils.logger import get_logger

logger = get_logger(__name__)


class HistoricalDataFetcher:
    """Fetches and manages 3-4 years of historical data."""

    def __init__(self, data_dir="data", years=3):
        """
        Initialize historical data fetcher.
        
        Args:
            data_dir: Directory to store data
            years: Number of years of history to fetch (default 3, max 4)
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.years = min(years, 4)  # Cap at 4 years max
        self.start_date = (datetime.now() - timedelta(days=365 * self.years)).strftime("%Y-%m-%d")
        self.end_date = datetime.now().strftime("%Y-%m-%d")
        self.historical_file = self.data_dir / "historical_data.csv"
        self.metadata_file = self.data_dir / "historical_metadata.json"

    def fetch_historical_data(self):
        """Fetch 3-4 years of historical data for all metrics."""
        logger.info("=" * 60)
        logger.info(f"Fetching historical data ({self.years} years)...")
        logger.info(f"Period: {self.start_date} to {self.end_date}")
        logger.info("=" * 60)

        historical_data = []

        # Define all tickers to fetch
        tickers = {
            # Equities
            "S&P 500": "^GSPC",
            "EuroStoxx 50": "^STOXX50E",
            "FTSE MIB": "FTSEMIB.MI",
            
            # Interest Rates (using ETFs as proxies for rates)
            "US 10Y Treasury": "^TNX",
            "US 2Y Treasury": "^IRX",
            "US 30Y Treasury": "^TYX",
            "EUR Corporate Bonds": "LQD",
            "EUR High Yield Bonds": "HYG",
            "EUR Emerging Markets": "VXUS",
            
            # Credit
            "VIX": "^VIX",
            "HY OAS": "HYG",
            "Investment Grade": "LQD",
            
            # Forex
            "EUR/USD": "EURUSD=X",
            "EUR/GBP": "EURGBP=X",
            "USD/JPY": "USDJPY=X",
            "GBP/USD": "GBPUSD=X",
            
            # Commodities
            "Brent Crude": "BZ=F",
            "Gold": "GC=F",
            "Natural Gas": "NG=F",
            "Silver": "SI=F",

            # Cryptocurrencies
            "Bitcoin": "BTC-USD",
            "Ethereum": "ETH-USD",
            "Binance Coin": "BNB-USD",
            "Solana": "SOL-USD",
        }

        # Fetch data for each ticker
        for metric_name, ticker in tickers.items():
            try:
                logger.info(f"Fetching historical data for {metric_name} ({ticker})...")
                
                # Fetch from Yahoo Finance
                data = yf.download(
                    ticker,
                    start=self.start_date,
                    end=self.end_date,
                    progress=False,
                    interval="1d"
                )

                if data.empty:
                    logger.warning(f"No data found for {metric_name}")
                    continue

                # Use closing price - handle MultiIndex columns from yfinance
                if isinstance(data, pd.DataFrame) and 'Close' in data.columns.get_level_values(0):
                    # MultiIndex columns case
                    close_prices = data['Close'].iloc[:, 0]  # Get first column of Close
                elif isinstance(data, pd.DataFrame) and 'Close' in data.columns:
                    # Single level columns case
                    close_prices = data['Close']
                else:
                    close_prices = data

                # Add to historical data
                if hasattr(close_prices, 'items'):
                    # It's a pandas Series
                    for date, value in close_prices.items():
                        # Handle different date formats from yfinance
                        if hasattr(date, 'strftime'):
                            # It's a datetime object
                            date_str = date.strftime("%Y-%m-%d")
                        else:
                            # It's already a string
                            date_str = str(date)

                        historical_data.append({
                            "date": date_str,
                            "metric": metric_name,
                            "value": float(value)
                        })
                else:
                    # Fallback for other formats
                    logger.warning(f"Unexpected data format for {metric_name}, skipping")
                    continue

                logger.info(f"✓ {metric_name}: {len(close_prices)} data points")

            except Exception as e:
                logger.error(f"✗ Failed to fetch {metric_name}: {e}")

        # Convert to wide format (dates as rows, metrics as columns)
        if historical_data:
            df_long = pd.DataFrame(historical_data)
            df_wide = df_long.pivot(index='date', columns='metric', values='value')
            df_wide = df_wide.reset_index()
            df_wide.sort_values('date', inplace=True)

            # Save to CSV
            self.historical_file.write_text(df_wide.to_csv(index=False))
            logger.info(f"\n✓ Historical data saved to {self.historical_file}")
            logger.info(f"  Rows: {len(df_wide)} trading days")
            logger.info(f"  Columns: {len(df_wide.columns) - 1} metrics")

            # Save metadata
            metadata = {
                "fetch_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "start_date": self.start_date,
                "end_date": self.end_date,
                "years": self.years,
                "rows": len(df_wide),
                "metrics": list(df_wide.columns[1:])
            }
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            logger.info("\n" + "=" * 60)
            logger.info("Historical data fetch completed!")
            logger.info("=" * 60)

            return df_wide
        else:
            logger.error("No historical data collected!")
            return pd.DataFrame()

    def load_historical_data(self):
        """Load historical data from file."""
        try:
            if self.historical_file.exists():
                df = pd.read_csv(self.historical_file)
                logger.info(f"Loaded {len(df)} rows of historical data")
                return df
            else:
                logger.warning("Historical data file not found")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Failed to load historical data: {e}")
            return pd.DataFrame()

    def update_historical_data(self, new_snapshot):
        """
        Update historical data file with new daily snapshot.
        
        Args:
            new_snapshot: Dict with {metric: value, ...}
        """
        try:
            # Load existing data
            if self.historical_file.exists():
                df = pd.read_csv(self.historical_file)
            else:
                df = pd.DataFrame()

            # Create new row
            today = datetime.now().strftime("%Y-%m-%d")
            new_row = {"date": today}
            new_row.update(new_snapshot)

            # Check if today's data already exists
            if not df.empty and (df['date'] == today).any():
                # Update existing row
                df.loc[df['date'] == today] = new_row
                logger.info(f"Updated today's data in historical file")
            else:
                # Add new row
                new_df = pd.DataFrame([new_row])
                df = pd.concat([df, new_df], ignore_index=True)
                logger.info(f"Added today's data to historical file")

            # Save
            df.to_csv(self.historical_file, index=False)
            logger.info(f"Historical data file updated: {len(df)} total rows")

        except Exception as e:
            logger.error(f"Failed to update historical data: {e}")


if __name__ == "__main__":
    # Fetch historical data for 3 years
    fetcher = HistoricalDataFetcher(years=3)
    df = fetcher.fetch_historical_data()
    print(f"\nDate range: {df['date'].min()} to {df['date'].max()}")
    print(f"Shape: {df.shape}")
