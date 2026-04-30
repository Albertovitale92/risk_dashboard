# Daily Risk Factors Dashboard 📊

A comprehensive Python-based dashboard for tracking daily financial risk factors across multiple asset classes. Built with Streamlit for interactive visualization and automated data fetching.

## Features

### Tracked Risk Factors

#### 📈 **Equities**
- S&P 500
- EuroStoxx 50
- FTSE MIB
- VIX (Equity Volatility)

#### 📊 **Interest Rates**
- USD Treasury curve: 1M, 3M, 6M, 1Y, 2Y, 3Y, 5Y, 7Y, 10Y, 20Y, 30Y
- EUR AAA spot curve: 1Y, 2Y, 5Y, 10Y, 20Y, 30Y
- EURIBOR 3M monthly average, sourced from the ECB Data Portal
- Realised €STR rates: ON, 1W, 1M, 3M, 6M, 12M
- User-uploaded EUR OIS market quotes for indicative forward-looking risk-free curve construction

#### 💳 **Credit Indices**
- iTraxx Europe Main
- iTraxx Crossover

#### 💱 **Foreign Exchange**
- EUR/USD
- EUR/GBP
- USD/JPY
- GBP/USD

#### ⚫ **Commodities**
- Brent Crude Oil
- Gold
- Natural Gas (bonus)
- Silver (bonus)

## Installation

### 1. Clone or Set Up Project
```bash
cd portfolio_risk_dashboard
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv
.\venv\Scripts\activate  # On Windows
# or
source venv/bin/activate  # On macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Usage

### Quick Start - Fetch Risk Data
```bash
python run.py fetch
```

This will:
- Fetch latest data for all risk factors
- Save daily snapshots as CSV and JSON
- Display results in console
- Store files in `data/` directory

### Launch Interactive Dashboard
```bash
python run.py dashboard
```

Or directly:
```bash
streamlit run dashboard.py
```

The dashboard will open at `http://localhost:8501` with:
- **Summary Tab**: Overview of all metrics
- **Equities Tab**: Stock indices with historical charts
- **Interest Rates Tab**: Rate data with trends
- **Credit Tab**: Credit indices visualization
- **Forex Tab**: Currency pairs and trends
- **Commodities Tab**: Commodity prices and trends

## Project Structure

```
portfolio_risk_dashboard/
├── src/
│   ├── __init__.py
│   ├── data_fetching/
│   │   ├── __init__.py
│   │   ├── equity_fetcher.py           # S&P 500, EuroStoxx, FTSE MIB
│   │   ├── interest_rates_fetcher.py   # EUR OIS, Euribor, Bund yields
│   │   ├── credit_fetcher.py           # iTraxx indices, VIX
│   │   ├── fx_fetcher.py               # EUR/USD, EUR/GBP, etc.
│   │   ├── commodities_fetcher.py      # Brent, Gold, etc.
│   │   └── risk_aggregator.py          # Master orchestrator
│   └── utils/
│       ├── __init__.py
│       └── logger.py                   # Logging configuration
├── data/                               # Data storage (auto-created)
│   ├── equities_YYYY-MM-DD.csv
│   ├── interest_rates_YYYY-MM-DD.csv
│   ├── credit_YYYY-MM-DD.csv
│   ├── forex_YYYY-MM-DD.csv
│   ├── commodities_YYYY-MM-DD.csv
│   ├── risk_snapshot_YYYY-MM-DD.json   # Full snapshot
│   └── risk_snapshot_YYYY-MM-DD.csv    # Flattened snapshot
├── logs/                               # Log files (auto-created)
│   └── portfolio_risk.log
├── dashboard.py                        # Streamlit dashboard UI
├── run.py                              # CLI entry point
├── requirements.txt                    # Python dependencies
└── README.md                           # This file
```

## Data Storage

### CSV Files
Each asset class generates daily CSV files:
- `equities_YYYY-MM-DD.csv`
- `interest_rates_YYYY-MM-DD.csv`
- `credit_YYYY-MM-DD.csv`
- `forex_YYYY-MM-DD.csv`
- `commodities_YYYY-MM-DD.csv`

### JSON Snapshots
- `risk_snapshot_YYYY-MM-DD.json` - Full detailed snapshot with timestamps
- `risk_snapshot_YYYY-MM-DD.csv` - Flattened version for easy analysis

## Logging

All activities are logged to:
- **Console**: Real-time output during fetch operations
- **File**: `logs/portfolio_risk.log` (rotated daily, 7-day retention)

## Architecture

### Modular Fetchers
Each fetcher follows the same pattern:
```python
class AssetClassFetcher:
    def fetch_all(self) -> dict
    def save_daily_snapshot() -> str
```

### Risk Aggregator
The `RiskDashboardAggregator` orchestrates all fetchers:
```python
aggregator = RiskDashboardAggregator()
snapshot = aggregator.save_daily_snapshot()
```

### Streamlit UI
Interactive dashboard with:
- Multi-tab interface (Summary, Equities, Rates, Credit, FX, Commodities)
- Real-time data metrics
- Historical trend charts (Plotly)
- Configurable display options
- Data refresh controls

## Scheduling (Optional)

### Windows Task Scheduler
```batch
REM Create a scheduled task to run daily at 9:00 AM
schtasks /create /tn "DailyRiskFactors" /tr "python C:\path\to\run.py fetch" /sc daily /st 09:00
```

### Linux/macOS Cron
```bash
# Add to crontab
0 9 * * * /path/to/venv/bin/python /path/to/run.py fetch
```

### Python Scheduler (APScheduler)
```python
from apscheduler.schedulers.background import BackgroundScheduler
from src.data_fetching.risk_aggregator import RiskDashboardAggregator

scheduler = BackgroundScheduler()
scheduler.add_job(
    RiskDashboardAggregator().save_daily_snapshot,
    'cron',
    hour=9,
    minute=0
)
scheduler.start()
```

## Data Sources

- **Equities**: Yahoo Finance (yfinance)
- **Interest Rates**: FRED for USD Treasury constant-maturity yields; ECB Data Portal for EURIBOR 3M
- **Credit Indices**: Yahoo Finance (VIX proxy)
- **FX Pairs**: Yahoo Finance
- **Commodities**: Yahoo Finance (futures)

## Environment Variables (Optional)

Create a `.env` file for configuration:
```ini
DATA_DIR=data
LOG_DIR=logs
FETCH_TIMEOUT=30
DASHBOARD_PORT=8501
```

## Troubleshooting

### No Data Available
- Check internet connection
- Verify Yahoo Finance is accessible
- Check `logs/portfolio_risk.log` for specific errors

### Missing Metrics
Some metrics may return `N/A` if:
- Market is closed
- Data source temporarily unavailable
- Ticker changed or deprecated

### Streamlit Issues
```bash
# Clear Streamlit cache
streamlit cache clear

# Run with verbose logging
streamlit run dashboard.py --logger.level=debug
```

## Future Enhancements

- [ ] Database storage (SQLite/PostgreSQL)
- [ ] Real-time data streaming (WebSocket)
- [ ] Email/Slack alerts for threshold breaches
- [ ] Risk metrics calculations (VaR, correlation matrix)
- [ ] Multi-region support
- [ ] API endpoint for data access
- [ ] Advanced charting with technical indicators
- [ ] Portfolio-specific risk calculations
- [ ] Historical volatility tracking
- [ ] Scenario analysis tools

## Dependencies

- `yfinance` - Market data fetching
- `pandas` - Data manipulation
- `streamlit` - Web UI framework
- `plotly` - Interactive charts
- `requests` - HTTP requests
- `numpy` - Numerical operations
- `pydantic` - Data validation

## License

[Specify your license]

## Support

For issues or feature requests, please contact or open an issue.

---

**Last Updated**: April 2026
**Version**: 1.0.0

