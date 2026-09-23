"""Read risk-factor data from the shared Risk_Factors project."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd


def _load_risk_factors_package():
    project_dir = Path(
        os.environ.get(
            "RISK_FACTORS_PROJECT",
            Path(__file__).resolve().parents[2] / "Risk_Factors",
        )
    )
    if not project_dir.exists():
        raise FileNotFoundError(
            f"Risk_Factors project not found at {project_dir}. "
            "Set RISK_FACTORS_PROJECT to its location."
        )
    if str(project_dir) not in sys.path:
        sys.path.insert(0, str(project_dir))

    from risk_factors.api import get_risk_drivers_snapshot
    from risk_factors.data_fetching.local_store import (
        load_local_levels,
        load_local_metadata,
        update_local_levels,
    )

    return (
        project_dir,
        get_risk_drivers_snapshot,
        load_local_levels,
        load_local_metadata,
        update_local_levels,
    )


ASSET_CLASS_METRICS = {
    "equities": {"S&P 500", "EuroStoxx 50", "FTSE MIB"},
    "interest_rates": {
        "US 1M Treasury", "US 3M Treasury", "US 6M Treasury",
        "US 1Y Treasury", "US 2Y Treasury", "US 3Y Treasury",
        "US 5Y Treasury", "US 7Y Treasury", "US 10Y Treasury",
        "US 20Y Treasury", "US 30Y Treasury", "EURIBOR 3M",
        "EUR AAA 1Y", "EUR AAA 2Y", "EUR AAA 5Y", "EUR AAA 10Y",
        "EUR AAA 20Y", "EUR AAA 30Y", "ESTR ON", "ESTR 1W Realised",
        "ESTR 1M Realised", "ESTR 3M Realised", "ESTR 6M Realised",
        "ESTR 12M Realised", "ECB OIS 1M", "ECB OIS 2M", "ECB OIS 3M",
        "ECB OIS 6M", "ECB OIS 9M", "ECB OIS 12M", "ECB OIS 2Y",
        "ECB OIS 3Y", "ECB OIS 5Y", "ECB OIS 10Y",
    },
    "credit": {"VIX", "Investment Grade", "High Yield", "EUR Bond Index"},
    "forex": {"EUR/USD", "EUR/GBP", "USD/JPY", "GBP/USD"},
    "commodities": {"Brent Crude", "Gold", "Natural Gas", "Silver"},
    "crypto": {"Bitcoin", "Ethereum", "Binance Coin", "Solana"},
}


class RiskFactorsStore:
    """Adapter that keeps the dashboard independent from data-fetching code."""

    def load_historical_data(self) -> pd.DataFrame:
        project_dir, _, load_local_levels, _, _ = _load_risk_factors_package()
        levels = load_local_levels(project_dir / "data" / "raw" / "risk_factors_levels.parquet")
        if levels.empty:
            return pd.DataFrame()
        return levels.reset_index()

    def load_metadata(self) -> dict:
        project_dir, _, _, load_local_metadata, _ = _load_risk_factors_package()
        return load_local_metadata(project_dir / "data" / "raw" / "risk_factors_metadata.json")

    def refresh_historical_data(self, years: int) -> pd.DataFrame:
        project_dir, _, _, _, update_local_levels = _load_risk_factors_package()
        return update_local_levels(
            years=years,
            path=project_dir / "data" / "raw" / "risk_factors_levels.parquet",
            metadata_path=project_dir / "data" / "raw" / "risk_factors_metadata.json",
        ).reset_index()

    def get_latest_snapshot(self) -> dict | None:
        project_dir, get_snapshot, _, _, _ = _load_risk_factors_package()
        from risk_factors.data_fetching.local_store import load_local_levels

        levels = load_local_levels(
            project_dir / "data" / "raw" / "risk_factors_levels.parquet"
        )
        snapshot = levels.tail(1).reset_index()
        if snapshot.empty:
            snapshot = get_snapshot()
        if snapshot.empty:
            return None

        row = snapshot.iloc[-1]
        values = {}
        for column in levels.columns:
            if column == "date":
                continue
            series = pd.to_numeric(levels[column], errors="coerce").dropna()
            if not series.empty:
                values[str(column)] = series.iloc[-1]
        data = {
            asset_class: {
                metric: values[metric]
                for metric in metrics
                if metric in values
            }
            for asset_class, metrics in ASSET_CLASS_METRICS.items()
        }
        data = {asset_class: values for asset_class, values in data.items() if values}
        date = pd.to_datetime(row["date"]).strftime("%Y-%m-%d")
        return {
            "date": date,
            "timestamp": f"{date} 00:00:00",
            "data": data,
        }
