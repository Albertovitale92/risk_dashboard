# ⏰ TIME SERIES TAB - Enhanced Dashboard Update

**Status:** ✅ Deployed  
**Date:** April 28, 2026  
**Feature:** New dedicated Time Series analysis tab

---

## 📊 What's New

Your dashboard now has a **dedicated Time Series tab** to analyze all 20 risk factors across recent dates!

### Dashboard Tabs (Updated)
1. 🎯 **Summary** - Overview of all metrics
2. **⏰ NEW: Time Series** - Historical trends & analysis
3. 📈 **Equities** - Equity indices
4. 📊 **Interest Rates** - USD yields & EUR curve
5. 💳 **Credit** - Credit indices
6. 💱 **Forex** - Exchange rates
7. ⚫ **Commodities** - Commodity prices

---

## 🎯 Time Series Tab Features

### 1️⃣ **Multi-Metric Selection**
```
✅ Select any combination of the 20 metrics
✅ Compare metrics side-by-side
✅ View different time scales
```

**How to use:**
- Click "Select Metrics to Display"
- Choose the metrics you want to analyze
- Charts update automatically

---

### 2️⃣ **Interactive Time Series Graph**
```
✅ All selected metrics plotted on one chart
✅ Hover to see exact values & dates
✅ Zoom, pan, and download as PNG
✅ Toggle metrics on/off by clicking legend
```

**Perfect for:**
- Comparing correlated movements (e.g., EUR/USD vs EUR interest rates)
- Identifying trends and cycles
- Spotting divergences between markets

---

### 3️⃣ **Statistical Summary Table**

For each selected metric, see:

| Statistic | What It Shows |
|-----------|--------------|
| **Latest** | Most recent data point |
| **Previous** | Previous day's value |
| **Change** | Daily move (Latest - Previous) |
| **Min** | Lowest value in period |
| **Max** | Highest value in period |
| **Avg** | Average over period |
| **Std Dev** | Volatility measure |

**Example:**
```
Metric: EUR/USD
Latest: 1.1726
Previous: 1.1720
Change: +0.0006
Min: 1.1690
Max: 1.1755
Avg: 1.1723
Std Dev: 0.0018
```

---

### 4️⃣ **Data Export**
```
📥 Download Statistics as CSV
- Get summary data for Excel analysis
- File: risk_factors_stats_YYYY-MM-DD.csv
- Includes: Latest, Previous, Change, Min, Max, Avg, Std Dev
```

---

### 5️⃣ **Full Historical Data Table**
```
✅ See all raw data points
✅ Scroll through complete history
✅ Verify individual values
✅ Copy-paste into other tools
```

---

## 🚀 Example Workflows

### Workflow 1: Monitor EUR Rate Environment
1. Navigate to **⏰ Time Series** tab
2. Select: "US 10Y Treasury", "EUR Corporate Bonds", "EUR High Yield Bonds"  
3. Observe if EUR rates following or diverging from US rates
4. Check "Change" column for daily moves
5. Identify trends over your selected date range

### Workflow 2: Track Market Stress
1. Select: "VIX", "Brent", "EUR/USD", "Gold"
2. Watch for coordinated moves (risk-off behavior)
3. Compare volatility with commodity moves
4. Check "Max" values to see stress levels

### Workflow 3: Analyze Credit Market
1. Select: "VIX", "HY Spreads", "IG Spreads", "Brent"
2. See if credit spreads widening with declining equities
3. Check if commodities moving inversely (USD flight-to-safety)
4. Download stats for your risk report

---

## 📈 Example Display

```
⏰ DATA PERIOD: 2026-04-23 to 2026-04-28 (6 snapshots)

Select Metrics to Display:
[✓] S&P 500        [✓] EUR/USD        [✓] VIX
[✓] Gold           [✓] Brent          [ ] EuroStoxx 50

[INTERACTIVE CHART WITH ALL 5 METRICS]

STATISTICAL SUMMARY:
┌─────────────────┬─────────┬──────────┬────────┬─────┬─────┬─────────┬─────────┐
│ Metric          │ Latest  │ Previous │ Change │ Min │ Max │ Avg     │ Std Dev │
├─────────────────┼─────────┼──────────┼────────┼─────┼─────┼─────────┼─────────┤
│ S&P 500         │ 7173.91 │ 7145.23  │ +28.68 │ 7100│ 7250│ 7175.42 │ 42.1234 │
│ EUR/USD         │ 1.1726  │ 1.1720   │ +0.0006│1.169│1.175│ 1.1723  │ 0.0018  │
│ VIX             │ 18.02   │ 17.95    │ +0.07  │ 17.5│ 19.2│ 18.05   │ 0.5678  │
│ Gold            │4694.80  │ 4688.50  │ +6.30  │4650 │4750 │ 4689.30 │ 28.9012 │
│ Brent           │ 101.88  │ 101.75   │ +0.13  │ 99.5│ 104 │ 101.95  │ 1.2345  │
└─────────────────┴─────────┴──────────┴────────┴─────┴─────┴─────────┴─────────┘

[DOWNLOAD STATISTICS CSV BUTTON]

["FULL HISTORICAL DATA TABLE WITH ALL ROWS"]
```

---

## 💡 Key Benefits

✅ **Compare any metrics** - Not limited to pre-defined groupings  
✅ **See full statistics** - Not just current values  
✅ **Identify patterns** - Spot correlations and divergences  
✅ **Export for analysis** - CSV download for Excel/reports  
✅ **Interactive exploration** - Zoom, pan, toggle series  
✅ **Date range control** - Set 5-90 day windows  

---

## 🎯 How to Access

### Step 1: Fetch Data
```powershell
python run.py fetch
```

### Step 2: View Dashboard
```powershell
python run.py dashboard
```

### Step 3: Go to Second Tab
Click on **⏰ Time Series** (second tab from left)

---

## 📋 Requirements for Historical Analysis

For the Time Series tab to show data:
- ✅ You need **at least 2 data snapshots** (runs at different times)
- ✅ More snapshots = better trends visible
- ✅ Automatically updated each time you run `fetch_daily_data.bat`

**Timeline:**
```
Day 1: Run fetch → 1 snapshot (Summary only)
Day 2: Run fetch → 2 snapshots (Time Series starts showing)
Day 5: Run fetch → 5 snapshots (Clear trends visible)
Day 30: Run fetch → 30 snapshots (Full monthly analysis)
```

---

## 🔧 Customization

The Time Series tab is **fully interactive**:

1. **Change number of historical days**
   - Sidebar: Adjust "Historical Days" slider (5-90 days)

2. **Select different metrics**
   - Use "Select Metrics to Display" dropdown
   - Can select 1 to 20 metrics

3. **Change date range**
   - Currently shows last N days
   - Default: 30 days (configurable)

---

## 📊 Supported Metrics (20 Total)

### Equities (3)
- S&P 500
- EuroStoxx 50
- FTSE MIB

### Interest Rates (6)
- US 10Y Treasury
- US 2Y Treasury
- US 30Y Treasury
- EUR Corporate Bonds
- EUR High Yield Bonds
- EUR Emerging Markets

### Credit (3)
- VIX
- HY Spreads
- IG Spreads

### Forex (4)
- EUR/USD
- EUR/GBP
- USD/JPY
- GBP/USD

### Commodities (4)
- Brent Crude
- Gold
- Natural Gas
- Silver

---

## ✨ Next Steps

1. **Set up daily fetches** to build historical data
2. **Explore the Time Series tab** to find patterns
3. **Export statistics** for your reports
4. **Monitor your favorite metrics** regularly

---

## 📞 Support

| Question | Answer |
|----------|--------|
| No historical data? | Run `fetch` at least 2 times (different days) |
| Want more days? | Adjust "Historical Days" slider (up to 90) |
| Want to export? | Click "📥 Download Statistics as CSV" |
| Want specific metrics? | Use "Select Metrics to Display" dropdown |

---

**Dashboard now includes:** Summary + Time Series + 5 Asset Class Tabs = **7 tabs total**  
**Status:** ✅ Production Ready  
**Total Metrics:** 20 (all with historical tracking)


