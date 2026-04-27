# 🚀 Quick Start Guide - Daily Risk Factors Dashboard

## Installation (First Time Only)

1. **Navigate to project directory:**
   ```powershell
   cd C:\Users\alber\PycharmProjects\portfolio_risk_dashboard
   ```

2. **Activate virtual environment:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   python -m pip install -r requirements.txt
   ```

## Daily Usage

### Option 1: Fetch Data (Recommended for Scheduling)
```powershell
# Simple double-click or schedule with Windows Task Scheduler
fetch_daily_data.bat
```

Or manually:
```powershell
.\.venv\Scripts\python.exe run.py fetch
```

### Option 2: Launch Interactive Dashboard
```powershell
# Simple double-click
launch_dashboard.bat
```

Or manually:
```powershell
.\.venv\Scripts\python.exe run.py dashboard
```

Then open your browser to: **http://localhost:8501**

## File Summary

### 📊 Dashboard Files Created
After each run, the following files are created in `data/`:
- `risk_snapshot_2026-04-27.json` - Full detailed snapshot
- `risk_snapshot_2026-04-27.csv` - Flattened snapshot for analysis
- `equities_2026-04-27.csv` - Equity data only
- `interest_rates_2026-04-27.csv` - Interest rates only  
- `credit_2026-04-27.csv` - Credit indices only
- `forex_2026-04-27.csv` - FX rates only
- `commodities_2026-04-27.csv` - Commodity prices only

### 📝 Log Files
All activity logged to: `logs/portfolio_risk.log`

## What's Being Tracked?

### 📈 Equities (3 indices)
- S&P 500
- EuroStoxx 50  
- FTSE MIB

### 📊 Interest Rates (3 yields)
- 10Y Treasury Yield
- 2Y Treasury Yield
- 30Y Treasury Yield

### 💳 Credit (3 metrics)
- VIX (Equity volatility)
- HY OAS (High Yield spreads proxy via HYG ETF)
- Investment Grade (via LQD ETF)

### 💱 Forex (4 pairs)
- EUR/USD
- EUR/GBP
- USD/JPY
- GBP/USD

### ⚫ Commodities (4 items)
- Brent Crude Oil
- Gold
- Natural Gas
- Silver

## Dashboard Tabs

1. **🎯 Summary** - Overview of all metrics
2. **📈 Equities** - Stock indices with 30-day trend chart
3. **📊 Interest Rates** - Treasury yields with historical trends
4. **💳 Credit** - Credit indices and volatility measures  
5. **💱 Forex** - Currency pairs with historical data
6. **⚫ Commodities** - Commodity prices with trends

### Key Dashboard Features
- ✅ Real-time metric display with current values
- ✅ Historical charts (configurable 5-90 days)
- ✅ One-click refresh of latest data
- ✅ Manual fetch button
- ✅ Adjustable display settings
- ✅ Data export capability

## Scheduling with Windows Task Scheduler

### Quick Setup (Manual)
1. Open **Task Scheduler** on Windows
2. Create Basic Task
3. Set trigger: Daily at 9:00 AM (or your preferred time)
4. Set action to: Start a program
5. Program: `C:\Users\alber\PycharmProjects\portfolio_risk_dashboard\fetch_daily_data.bat`

### Via PowerShell (Automated)
```powershell
$trigger = New-ScheduledTaskTrigger -Daily -At 9:00AM
$action = New-ScheduledTaskAction -Execute "C:\Users\alber\PycharmProjects\portfolio_risk_dashboard\fetch_daily_data.bat"
Register-ScheduledTask -TaskName "Daily Risk Factors" -Trigger $trigger -Action $action -Description "Daily portfolio risk factor data collection"
```

## Troubleshooting

### Dashboard won't launch
```powershell
# Check Streamlit is installed
.\.venv\Scripts\python.exe -m streamlit --version

# Clear Streamlit cache
streamlit cache clear
```

### Data shows as "N/A"
- Market may be closed
- Check internet connection
- Review logs: `logs/portfolio_risk.log`
- Some metrics may be temporarily unavailable

### Permission errors on scheduled task
- Run Task Scheduler as Administrator
- Ensure Python path is absolute: `C:\Users\alber\PycharmProjects\portfolio_risk_dashboard\...`

## Data Analysis

### Load Historical Data in Python
```python
import pandas as pd
from src.data_fetching.risk_aggregator import RiskDashboardAggregator

aggregator = RiskDashboardAggregator()
historical = aggregator.get_historical_data(days=30)

# Analyze equities
equity_cols = ['S&P 500', 'EuroStoxx 50', 'FTSE MIB']
print(historical[['date'] + equity_cols].describe())
```

### Export to Excel
```python
import pandas as pd

df = pd.read_csv('data/risk_snapshot_2026-04-27.csv')
df.to_excel('risk_analysis.xlsx', index=False)
```

## Next Steps

### To do more with this dashboard:

1. **Add alerts** - Monitor threshold breaches
2. **Export reports** - Generate daily PDF summaries
3. **API integration** - Connect to portfolio management system
4. **Email alerts** - Get notified of market moves
5. **Database** - Store historical data in SQLite/PostgreSQL
6. **Mobile app** - Access dashboard on phone

See README.md for advanced features and architecture details.

---

**Need help?** Check the logs in `logs/portfolio_risk.log` for detailed error messages.

