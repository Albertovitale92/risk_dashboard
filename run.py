"""Entry point script for running risk dashboard."""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Portfolio risk dashboard launcher"
    )

    parser.add_argument(
        "command",
        choices=["dashboard"],
        help="Launch the dashboard UI"
    )

    args = parser.parse_args()

    if args.command == "dashboard":
        logger.info("Launching Streamlit dashboard...")
        import streamlit.web.cli as stcli
        sys.argv = ["streamlit", "run", "dashboard.py"]
        stcli.main()


if __name__ == "__main__":
    main()
