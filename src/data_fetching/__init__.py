"""Data fetching module for risk factors."""

from .equity_fetcher import EquityFetcher
from .interest_rates_fetcher import InterestRateFetcher
from .credit_fetcher import CreditFetcher
from .fx_fetcher import FXFetcher
from .commodities_fetcher import CommoditiesFetcher
from .risk_aggregator import RiskDashboardAggregator

__all__ = [
    "EquityFetcher",
    "InterestRateFetcher",
    "CreditFetcher",
    "FXFetcher",
    "CommoditiesFetcher",
    "RiskDashboardAggregator",
]

