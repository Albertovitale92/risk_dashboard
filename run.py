"""Entry point script for running risk dashboard."""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.data_fetching.risk_aggregator import RiskDashboardAggregator
from src.utils.logger import get_logger

logger = get_logger(__name__)


def fetch_risk_data(data_dir="data"):
    """Fetch and save daily risk factors data."""
    aggregator = RiskDashboardAggregator(data_dir=data_dir)
    snapshot = aggregator.save_daily_snapshot()
    return snapshot


def fetch_historical_data(data_dir="data", years=3):
    """Fetch historical data for specified number of years."""
    aggregator = RiskDashboardAggregator(data_dir=data_dir)
    logger.info(f"Fetching {years} years of historical data...")
    historical = aggregator.fetch_and_save_historical_data(years=years)
    if not historical.empty:
        logger.info(f"✓ Successfully loaded {len(historical)} trading days of data")
        logger.info(f"  Date range: {historical['date'].min()} to {historical['date'].max()}")
    else:
        logger.error("✗ Failed to fetch historical data - no data returned")
    return historical


def main():
    parser = argparse.ArgumentParser(
        description="Risk Dashboard CLI - Fetch data or launch Streamlit dashboard"
    )

    parser.add_argument(
        "command",
        choices=["fetch", "fetch-history", "dashboard"],
        help="Command: 'fetch' = daily data, 'fetch-history' = historical data (1-10+ years), 'dashboard' = UI"
    )

    parser.add_argument(
        "--data-dir",
        default="data",
        help="Directory to store data files (default: data)"
    )

    parser.add_argument(
        "--years",
        type=int,
        default=3,
        help="Years of historical data to fetch (1-10+, default: 3)"
    )

    args = parser.parse_args()

    if args.command == "fetch":
        logger.info("Fetching daily risk factors...")
        snapshot = fetch_risk_data(data_dir=args.data_dir)
        logger.info("✓ Fetch completed successfully")
        print("\n" + "="*60)
        print("RISK FACTORS SNAPSHOT")
        print("="*60)
        for asset_class, metrics in snapshot['data'].items():
            print(f"\n{asset_class.upper()}:")
            for metric, value in metrics.items():
                if value is not None:
                    print(f"  {metric}: {value}")
                else:
                    print(f"  {metric}: N/A")
        print("="*60)

    elif args.command == "fetch-history":
        logger.info(f"Fetching {args.years} years of historical data...")
        historical = fetch_historical_data(data_dir=args.data_dir, years=args.years)
        if not historical.empty:
            logger.info("✓ Historical data fetch completed successfully")
            print("\n" + "="*60)
            print("HISTORICAL DATA SUMMARY")
            print("="*60)
            print(f"Trading days: {len(historical)}")
            print(f"Date range: {historical['date'].min()} to {historical['date'].max()}")
            print(f"Metrics: {len([c for c in historical.columns if c != 'date'])}")
            print("="*60)
        else:
            logger.error("✗ Historical data fetch failed")
            print("\n" + "="*60)
            print("HISTORICAL DATA FETCH FAILED")
            print("="*60)
            print("No data was collected. Check logs for details.")
            print("="*60)

    elif args.command == "dashboard":
        logger.info("Launching Streamlit dashboard...")
        import streamlit.web.cli as stcli
        sys.argv = ["streamlit", "run", "dashboard.py"]
        stcli.main()


if __name__ == "__main__":
    main()

