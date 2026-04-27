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


def main():
    parser = argparse.ArgumentParser(
        description="Risk Dashboard CLI - Fetch data or launch Streamlit dashboard"
    )

    parser.add_argument(
        "command",
        choices=["fetch", "dashboard"],
        help="Command to execute: 'fetch' for data collection, 'dashboard' to launch UI"
    )

    parser.add_argument(
        "--data-dir",
        default="data",
        help="Directory to store data files (default: data)"
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

    elif args.command == "dashboard":
        logger.info("Launching Streamlit dashboard...")
        import streamlit.cli as stcli
        sys.argv = ["streamlit", "run", "dashboard.py"]
        stcli.main()


if __name__ == "__main__":
    main()

