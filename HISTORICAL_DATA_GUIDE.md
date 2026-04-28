# 📈 3-4 YEAR HISTORICAL DATA - Complete Guide

**Status:** ✅ **IMPLEMENTED & READY**  
**Date:** April 28, 2026  
**Feature:** Multi-year time series analysis

---

## 🎉 What You Got

Your dashboard now supports **3-4 years of daily historical data** for all 20 risk factors, enabling long-term trend analysis!

### Key Improvements
- ✅ **3-4 years of daily data** - Not just recent weeks
- ✅ **Single cumulative file** - `historical_data.csv` 
- ✅ **Date range selector** - Choose any period to analyze
- ✅ **Long-term trends** - See multi-year patterns
- ✅ **Complete statistics** - Over 3-4 year periods
- ✅ **Easy setup** - One-click initialization

---

## 🚀 Quick Start Setup

### Option A: Via Sidebar (Easiest)
1. Open dashboard: `launch_dashboard.bat`
2. Look for **"Fetch 3-4 Year History"** button in sidebar
3. Select years (1-4, default 3)
4. Click the button
5. Wait 3-5 minutes
6. ✅ Done! Your data is ready

### Option B: Via Command Line
```powershell
# Fetch 3 years of history
python run.py fetch-history

# Or specific years (1-4)
python run.py fetch-history --years 4
```

---

## 📊 How It Works

### Day 1: Initial Setup
```
Dashboard opened for first time
├─ No historical_data.csv exists yet
├─ Sidebar shows: "Fetch 3-4 Year History" button
└─ Time Series tab shows message to initialize
```

### Day 1 (After Click):
```
Fetching starts...
├─ Connects to Yahoo Finance
├─ Downloads 3 years of daily data for all 20 metrics
├─ Takes 3-5 minutes (first time only)
└─ Saves to: data/historical_data.csv
```

### Day 1 (Complete):
```
data/
├─ historical_data.csv          (3-4 years of daily data)
├─ historical_metadata.json     (info about the data)
└─ risk_snapshot_2026-04-28.csv (today's daily snapshot)
```

### Day 2+ (Running normally):
```
Daily fetch runs...
├─ Gets today's data from Yahoo Finance
├─ Updates historical_data.csv with today's values
└─ Appends to cumulative file
```

---

## 💾 Data Storage Structure

### historical_data.csv Format
```
date         | S&P 500 | EuroStoxx 50 | FTSE MIB | US 10Y Treasury | ... (20 metrics)
2023-04-28   | 7100.5  | 5800.2       | 47500.0  | 3.45            | ...
2023-04-29   | 7105.2  | 5805.1       | 47520.0  | 3.47            | ...
...          | ...     | ...          | ...      | ...             | ...
2026-04-28   | 7138.83 | 5836.10      | 48040.24 | 4.354           | ...
```

### File Sizes (Approximate)
```
3 years  × 250 trading days/year × 20 metrics ≈ 400 KB
4 years  × 250 trading days/year × 20 metrics ≈ 530 KB
```

### Historical Metadata (JSON)
```json
{
  "fetch_date": "2026-04-28 22:00:00",
  "start_date": "2023-04-28",
  "end_date": "2026-04-28",
  "years": 3,
  "rows": 750,
  "metrics": [20 metric names]
}
```

---

## 🎯 Time Series Tab - Enhanced Features

### Date Range Selector
```
New fields in tab:
├─ Start Date picker (min: earliest data)
├─ End Date picker (max: today)
└─ Automatically filters chart & statistics
```

### Example Scenarios

#### Scenario 1: Analyze Last Quarter
1. Set Start Date: 3 months ago
2. Set End Date: Today
3. Select: S&P 500, VIX, Brent
4. Watch quarter's performance

#### Scenario 2: Compare Years
1. Set Start Date: April 27, 2023
2. Set End Date: April 27, 2024
3. Select: All interest rates
4. Compare year-over-year curve positions

#### Scenario 3: Find Stress Events
1. Set Start Date: 3 years ago
2. Set End Date: Today
3. Select: VIX
4. Zoom chart to find volatility spikes
5. Note the dates
6. Investigate what happened

#### Scenario 4: Volatility Analysis
1. Use full 3-4 year range
2. Select: Gold, USD/JPY, VIX
3. Check Std Dev values
4. Understand "normal" volatility levels

---

## 📊 Statistical Analysis Over 3-4 Years

### What Statistics Mean Over Long Periods

```
Latest     = Today's closing price
Previous   = Yesterday's closing price
Change     = Today's daily move (Latest - Previous)
Min        = Lowest price IN ENTIRE 3+ YEARS
Max        = Highest price IN ENTIRE 3+ YEARS
Avg        = Average price over 3+ years
Std Dev    = Volatility (standard deviation) over entire period
```

### Example Interpretations

#### S&P 500 (Last 3 years)
```
Latest:    7138.83  (today)
Previous:  7145.23  (yesterday)
Change:    -6.40    (down 0.09%)
Min:       6500.00  (March 2023 low)
Max:       7300.00  (January 2024 high)
Avg:       6950.12  (average over 3 years)
Std Dev:   185.34   (typical daily range ~1.8%)
```

**Interpretation:**
- S&P is near all-time highs (7138 close to 7300 max)
- Average volatility: ~185 points per day
- Today's move of -6.4 is below average volatility

#### EUR/USD (Last 3 years)
```
Latest:    1.1726   
Min:       1.0600   (lowest in 3 years)
Max:       1.2400   (highest in 3 years)
Avg:       1.1550   
Std Dev:   0.0325   
```

**Interpretation:**
- EUR recent weakness (low within range)
- Trading band: 1.06 to 1.24
- Current at upper-mid range

---

## 🔄 Workflow: Daily + Historical

### Setup Day (once)
```
1. Run: fetch-history command
2. Wait 3-5 minutes
3. ✅ 3-4 year data loaded
4. No need to repeat
```

### Every Trading Day
```
1. Task Scheduler runs: fetch_daily_data.bat
2. New daily snapshot added to historical_data.csv
3. Historical data continuously updated
4. Dashboard always has latest + history
```

### Example Timeline
```
May 1, 2026:  1st setup fetch-history
              ├─ Loads April 28, 2023 to April 28, 2026 (3 years)
              └─ historical_data.csv created (750 rows)

May 2, 2026:  Daily fetch runs
              ├─ Adds May 1, 2026 row
              └─ historical_data.csv now has 751 rows

May 3, 2026:  Daily fetch runs
              ├─ Adds May 2, 2026 row
              └─ historical_data.csv now has 752 rows

...

May 30, 2027: Daily fetch runs
              ├─ Adds May 29, 2027 row
              └─ historical_data.csv now has 1000+ rows (4 years!)
```

---

## 🎛️ Configuration Options

### Years Selection
```
fetch-history --years 1  # ~250 rows (1 year)
fetch-history --years 2  # ~500 rows (2 years)
fetch-history --years 3  # ~750 rows (3 years) [DEFAULT]
fetch-history --years 4  # ~1000 rows (4 years)
```

### What Happens After Initial Load
```
After you fetch historical once, it stays there forever
├─ Only thing that changes: daily new rows added
├─ You don't need to re-fetch history
└─ Automatically stays current as new data comes in
```

---

## 📈 Analysis Capabilities Unlock

### Now Possible (With 3-4 Years)
✅ **Long-term trends** - See multi-year cycle patterns  
✅ **Volatility regimes** - Compare normal vs stress periods  
✅ **Correlation analysis** - How markets moved together over years  
✅ **Extreme events** - Identify historical highs/lows  
✅ **Seasonality** - See if April always behaves similarly  
✅ **Mean reversion** - Does it bounce back to historical avg?  
✅ **Growth rates** - How fast are things growing?  
✅ **Risk measurement** - Real historical volatility  

### Examples: Powerful Analysis

#### Analysis 1: Identify Normal Market Stress
```
Select: VIX (over 3 years range)
Observe:
├─ Normal VIX: 15-20
├─ Stressed: 25-35
├─ Crisis: 35+
Import: Today's VIX 18 = normal environment
```

#### Analysis 2: Find Currency Trading Ranges
```
Select: EUR/USD (over 3 years range)
Observe:
├─ Min: 1.06 (3-year low)
├─ Max: 1.24 (3-year high)
├─ Avg: 1.15 (center)
├─ Trading range: 1.06-1.24
Import: Current 1.1726 = middle of range, no extremes
```

#### Analysis 3: Market Correlation Study
```
Select: S&P 500, VIX, Gold (3 years)
Observe:
├─ When S&P up → VIX usually down, Gold mixed
├─ When S&P crashes → VIX & Gold spike
Import: Normal risk-off behavior consistent
```

---

## 💡 Pro Tips

### Tip 1: First Time Takes a Bit
- First `fetch-history` takes 3-5 minutes
- Don't interrupt - let it complete
- Future daily fetches are fast (< 1 minute)

### Tip 2: Update Daily Data Regularly
- Task Scheduler runs automatically (if set up)
- Or manually: `fetch_daily_data.bat` daily
- This keeps historical_data.csv current

### Tip 3: Backup Your Data
```powershell
# Once you have 3-4 years, backup this file:
Copy-Item "data/historical_data.csv" "backup_$(Get-Date -Format 'yyyy-MM-dd').csv"
```

### Tip 4: Use for Your Reports
```
Each quarter:
1. Open Time Series tab
2. Set date range to this quarter
3. Select your key metrics
4. Download CSV
5. Attach to quarterly report
```

### Tip 5: Find Extremes
```
To find biggest daily moves ever:
1. Full 3-4 year range
2. Focus on "Change" column
3. Sort descending
4. Spot historical outliers
```

---

## 🔧 Technical Details

### Data Sources (Yahoo Finance)
```
20 metrics pulled from:
├─ Stock tickers: GSPC, STOXX50E, FTSEMIB.MI
├─ ETFs: LQD, HYG, VXUS
├─ Indices: ^VIX, ^TNX, ^IRX, ^TYX
└─ Forex: EURUSD=X, EURGBP=X, USDJPY=X, GBPUSD=X
   Futures: BZ=F, GC=F, NG=F, SI=F
```

### Frequency
```
Daily data (1 day bar)
├─ Trading days only (weekends/holidays skipped)
├─ Captured at market close
└─ Approximately 250 rows per calendar year
```

### Accuracy
```
Source:    Yahoo Finance (reliable, widely used)
Coverage:  Recent 3-4 years available
Gaps:      Filled by Yahoo (weekends/holidays excluded)
Precision: 4-6 decimals (sufficient for analysis)
```

---

## 📝 Commands Reference

### Initialize 3-4 Year History (Do Once)
```powershell
# Default: 3 years
python run.py fetch-history

# Or specific years:
python run.py fetch-history --years 4  # 4 years
python run.py fetch-history --years 2  # 2 years
```

### Daily Fetch (Do Every Day)
```powershell
# Adds today's data to historical file
python run.py fetch

# Or batch:
fetch_daily_data.bat
```

### View Dashboard (Do Anytime)
```powershell
python run.py dashboard
# or
launch_dashboard.bat
```

---

## 🎯 Monthly Routine

```
Month 1 (Starting):
├─ Day 1: Run fetch-history (once)
└─ Daily: Automated daily fetch (via scheduler)

Month 2+:
├─ Daily: Automatic fetches (no action needed)
├─ Weekly: Check dashboard trends
├─ Monthly: Export data for reporting
└─ Quarterly: Run deeper analysis
```

---

## ✅ Verification

After initialization, verify with:

```powershell
# Check file exists
Get-Item data/historical_data.csv

# Check file size
Get-Item data/historical_data.csv | Select-Object Length

# Preview data
Import-Csv data/historical_data.csv | Select-Object -First 5

# Check row count (approximately):
# 250 trading days/year × years = rows
# 3 years ≈ 750 rows
# 4 years ≈ 1000 rows
```

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| **Fetch taking too long** | Normal for first time (3-5 min). Don't interrupt. |
| **Internet connection breaks** | Re-run command. It will resume from where it stopped. |
| **Yahoo Finance not accessible** | Try again later (temporary issue). |
| **File too large** | It's only 400-500 KB. Not an issue. |
| **Old data missing** | Only loads last 3-4 years (by design). |
| **Want to restart** | Delete `historical_data.csv` and re-run fetch-history |

---

## 📊 Next Steps

### Today
```
☐ 1. Open dashboard
☐ 2. Click "Fetch 3-4 Year History" in sidebar
☐ 3. Wait 3-5 minutes
☐ 4. Go to ⏰ Time Series tab
☐ 5. Explore the data!
```

### This Week
```
☐ 1. Set up daily scheduler (if not already)
☐ 2. Practice with date range selector
☐ 3. Export a CSV for analysis
☐ 4. Show dashboard to team
```

### This Month
```
☐ 1. Run daily fetches consistently
☐ 2. Build comfort with long-term data
☐ 3. Create first quarterly report
☐ 4. Identify key historical levels
```

---

## 🎊 You're Ready!

### Commands to Get Started

**First Time (Setup):**
```powershell
python run.py fetch-history
# Wait 3-5 minutes...
```

**Then Every Day (Automatic or Manual):**
```powershell
fetch_daily_data.bat  # Auto via scheduler
# or
python run.py fetch
```

**Analyze Anytime:**
```powershell
launch_dashboard.bat
# Click ⏰ Time Series tab
```

---

## 📈 Your Dashboard Now Supports

✅ 20 real-time metrics  
✅ 3-4 years of daily history  
✅ Date range selection  
✅ Long-term statistical analysis  
✅ Multi-year trend visualization  
✅ Powerful analysis capabilities  
✅ Automatic daily updates  

---

**Status:** ✅ **PRODUCTION READY**  
**Data Scope:** 3-4 years daily  
**Update Frequency:** Daily  
**Analysis Depth:** Professional Grade  

### Start today! 🚀📊


