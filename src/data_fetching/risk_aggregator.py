"""Master risk dashboard aggregator - orchestrates all data fetchers."""

import json
import pandas as pd
from datetime import datetime
from pathlib import Path

from src.utils.logger import get_logger
from src.data_fetching.equity_fetcher import EquityFetcher
from src.data_fetching.interest_rates_fetcher import InterestRateFetcher
from src.data_fetching.credit_fetcher import CreditFetcher
from src.data_fetching.fx_fetcher import FXFetcher
from src.data_fetching.commodities_fetcher import CommoditiesFetcher

logger = get_logger(__name__)


class RiskDashboardAggregator:
    """Aggregates all risk factor data from various fetchers."""

    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Initialize all fetchers
        self.equity_fetcher = EquityFetcher(data_dir=str(self.data_dir))
        self.rates_fetcher = InterestRateFetcher(data_dir=str(self.data_dir))
        self.credit_fetcher = CreditFetcher(data_dir=str(self.data_dir))
        self.fx_fetcher = FXFetcher(data_dir=str(self.data_dir))
        self.commodities_fetcher = CommoditiesFetcher(data_dir=str(self.data_dir))

    def fetch_all_risk_factors(self):
        """Fetch all risk factors and aggregate results."""
        logger.info("=" * 60)
        logger.info("Starting daily risk factors fetch...")
        logger.info("=" * 60)

        today = datetime.now().strftime("%Y-%m-%d")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        aggregated = {
            "date": today,
            "timestamp": timestamp,
            "data": {}
        }

        # Fetch each asset class
        fetchers = [
            ("equities", self.equity_fetcher),
            ("interest_rates", self.rates_fetcher),
            ("credit", self.credit_fetcher),
            ("forex", self.fx_fetcher),
            ("commodities", self.commodities_fetcher),
        ]

        for asset_class, fetcher in fetchers:
            try:
                logger.info(f"\nFetching {asset_class}...")
                result = fetcher.fetch_all()
                # Extract the data portion (skip 'date' key to avoid duplication)
                data_key = list(result.keys())[1]  # Get the second key (the actual data)
                aggregated["data"][asset_class] = result[data_key]
                logger.info(f"✓ {asset_class} fetched successfully")
            except Exception as e:
                logger.error(f"✗ Failed to fetch {asset_class}: {e}")
                aggregated["data"][asset_class] = {}

        return aggregated

    def save_daily_snapshot(self):
        """Save aggregated daily snapshot to JSON and CSV."""
        today = datetime.now().strftime("%Y-%m-%d")

        # Fetch all data
        aggregated = self.fetch_all_risk_factors()

        # Save as JSON for full detail
        json_filepath = self.data_dir / f"risk_snapshot_{today}.json"
        with open(json_filepath, 'w') as f:
            json.dump(aggregated, f, indent=2)
        logger.info(f"\n✓ Full snapshot saved to {json_filepath}")

        # Create a flattened version for CSV (easier analysis)
        flat_data = {}
        for asset_class, values in aggregated["data"].items():
            flat_data.update(values)

        csv_filepath = self.data_dir / f"risk_snapshot_{today}.csv"
        df = pd.DataFrame([{
            "date": aggregated["date"],
            "timestamp": aggregated["timestamp"],
            **flat_data
        }])
        df.to_csv(csv_filepath, index=False)
        logger.info(f"✓ Flattened snapshot saved to {csv_filepath}")

        # Also save individual asset class snapshots for granular tracking
        self.equity_fetcher.save_daily_snapshot()
        self.rates_fetcher.save_daily_snapshot()
        self.credit_fetcher.save_daily_snapshot()
        self.fx_fetcher.save_daily_snapshot()
        self.commodities_fetcher.save_daily_snapshot()

        logger.info("\n" + "=" * 60)
        logger.info("Daily risk factors snapshot completed!")
        logger.info("=" * 60)

        return aggregated

    def get_latest_snapshot(self):
        """Load and return the latest available snapshot."""
        try:
            json_files = list(self.data_dir.glob("risk_snapshot_*.json"))
            if not json_files:
                logger.warning("No snapshots found")
                return None

            latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
            with open(latest_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load latest snapshot: {e}")
            return None

    def get_historical_data(self, days=30):
        """Load and aggregate historical CSV data (for trend analysis)."""
        try:
            csv_files = list(self.data_dir.glob("risk_snapshot_*.csv"))
            if not csv_files:
                logger.warning("No historical data found")
                return pd.DataFrame()

            # Sort by date and take last N days
            csv_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            csv_files = csv_files[:days]

            dfs = [pd.read_csv(f) for f in csv_files]
            historical = pd.concat(dfs, ignore_index=True)
            return historical.sort_values('date').reset_index(drop=True)
        except Exception as e:
            logger.error(f"Failed to load historical data: {e}")
            return pd.DataFrame()

