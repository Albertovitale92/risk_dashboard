"""Calculate 10-day overlapping returns for all risk factors."""

import pandas as pd
import numpy as np
from pathlib import Path
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ReturnsCalculator:
    """Compute 10-day overlapping returns for time series data."""

    def __init__(self, data_dir="data"):
        """
        Initialize returns calculator.

        Args:
            data_dir: Directory containing historical data
        """
        self.data_dir = Path(data_dir)

        # Asset class organization
        self.asset_classes = {
            "equities": ["S&P 500", "EuroStoxx 50", "FTSE MIB"],
            "interest_rates": [
                "US 1M Treasury", "US 3M Treasury", "US 6M Treasury",
                "US 1Y Treasury", "US 2Y Treasury", "US 3Y Treasury",
                "US 5Y Treasury", "US 7Y Treasury", "US 10Y Treasury",
                "US 20Y Treasury", "US 30Y Treasury", "EURIBOR 3M",
                "EUR AAA 1Y", "EUR AAA 2Y", "EUR AAA 5Y",
                "EUR AAA 10Y", "EUR AAA 20Y", "EUR AAA 30Y",
                "ESTR ON", "ESTR 1W Realised", "ESTR 1M Realised",
                "ESTR 3M Realised", "ESTR 6M Realised", "ESTR 12M Realised"
            ],
            "credit": ["VIX", "Investment Grade", "High Yield", "EUR Bond Index"],
            "forex": ["EUR/USD", "EUR/GBP", "USD/JPY", "GBP/USD"],
            "commodities": ["Brent Crude", "Gold", "Natural Gas", "Silver"],
            "crypto": ["Bitcoin", "Ethereum", "Binance Coin", "Solana"]
        }

    def calculate_10d_returns(self, df):
        """
        Calculate 10-day overlapping returns (%) for all numeric columns.

        Formula: (Price_t - Price_t-10) / Price_t-10 * 100

        Args:
            df: DataFrame with date column and price columns

        Returns:
            DataFrame with 10-day returns for each metric
        """
        df_copy = df.copy()

        # Identify metric columns (exclude date and timestamp)
        metric_cols = [col for col in df_copy.columns if col not in ['date', 'timestamp']]

        # Create returns dataframe
        returns_df = pd.DataFrame()
        returns_df['date'] = df_copy['date']

        # Calculate 10-day percentage returns for each metric
        for metric in metric_cols:
            if pd.api.types.is_numeric_dtype(df_copy[metric]):
                # Calculate percentage change over 10 periods
                returns_df[metric] = (df_copy[metric].pct_change(periods=10)) * 100
            else:
                returns_df[metric] = np.nan

        return returns_df

    def get_returns_by_asset_class(self, returns_df):
        """
        Organize returns by asset class.

        Args:
            returns_df: DataFrame with 10-day returns

        Returns:
            Dict organized by asset class: {class: DataFrame}
        """
        organized_returns = {}

        for asset_class, metrics in self.asset_classes.items():
            # Get columns for this asset class that exist in returns_df
            class_metrics = [m for m in metrics if m in returns_df.columns]

            if class_metrics:
                organized_returns[asset_class] = returns_df[['date'] + class_metrics].copy()
            else:
                organized_returns[asset_class] = pd.DataFrame()

        return organized_returns

    def load_and_calculate_returns(self):
        """
        Load historical data and calculate 10-day returns.

        Returns:
            Tuple of (returns_df, organized_returns_dict)
        """
        historical_file = self.data_dir / "historical_data.csv"

        if not historical_file.exists():
            logger.warning(f"Historical data file not found: {historical_file}")
            return pd.DataFrame(), {}

        try:
            # Load historical data
            df = pd.read_csv(historical_file)
            logger.info(f"Loaded {len(df)} rows of historical data")

            # Calculate returns
            returns_df = self.calculate_10d_returns(df)

            # Organize by asset class
            organized_returns = self.get_returns_by_asset_class(returns_df)

            logger.info(f"Calculated 10-day returns for {len(returns_df)} dates")

            return returns_df, organized_returns

        except Exception as e:
            logger.error(f"Error calculating returns: {e}")
            return pd.DataFrame(), {}

    def get_summary_statistics(self, returns_df):
        """
        Calculate summary statistics for returns.

        Args:
            returns_df: DataFrame with returns data

        Returns:
            Dict with statistics: {metric: {stat: value, ...}, ...}
        """
        if returns_df.empty:
            return {}

        statistics = {}
        metric_cols = [col for col in returns_df.columns if col not in ['date', 'timestamp']]

        for metric in metric_cols:
            if metric in returns_df.columns and pd.api.types.is_numeric_dtype(returns_df[metric]):
                data = returns_df[metric].dropna()

                if len(data) > 0:
                    statistics[metric] = {
                        "latest": data.iloc[-1] if len(data) > 0 else np.nan,
                        "mean": data.mean(),
                        "std": data.std(),
                        "min": data.min(),
                        "max": data.max(),
                        "count": len(data)
                    }

        return statistics

    def get_asset_class_returns(self, asset_class):
        """
        Get returns for a specific asset class.

        Args:
            asset_class: Asset class name (e.g., "equities", "credit")

        Returns:
            DataFrame with returns for that asset class
        """
        _, organized_returns = self.load_and_calculate_returns()

        if asset_class in organized_returns:
            return organized_returns[asset_class]
        else:
            logger.warning(f"Asset class {asset_class} not found")
            return pd.DataFrame()


def load_historical_data(data_dir="data"):
    """
    Convenience function to load historical data.

    Args:
        data_dir: Directory containing historical data

    Returns:
        DataFrame with historical data
    """
    historical_file = Path(data_dir) / "historical_data.csv"

    if historical_file.exists():
        return pd.read_csv(historical_file)
    else:
        logger.warning(f"Historical data not found at {historical_file}")
        return pd.DataFrame()


if __name__ == "__main__":
    # Example usage
    calc = ReturnsCalculator()
    returns_df, organized = calc.load_and_calculate_returns()

    if not returns_df.empty:
        print(f"Calculated returns for {len(returns_df)} dates")
        stats = calc.get_summary_statistics(returns_df)
        print(f"\nStatistics for {len(stats)} metrics")

