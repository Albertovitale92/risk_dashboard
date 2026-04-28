# ⚡ QUICK REFERENCE - Time Series Dashboard

**Print this or bookmark it!** Your go-to guide for using the new Time Series tab.

---

## 🚀 Three Simple Commands

```powershell
# 1. Get today's data
fetch_daily_data.bat

# 2. View dashboard
launch_dashboard.bat

# 3. Click ⏰ Time Series tab → Done!
```

---

## 📊 Time Series Tab - At a Glance

### What You See
```
📅 Data Period: Shows date range & number of snapshots

🎛️ Select Metrics: Click dropdown, choose 1-20 metrics

📈 Chart: Interactive graph showing all selected metrics

📋 Statistics: Table with Latest, Previous, Change, Min, Max, Avg, Std Dev

📥 CSV Export: Download button for Excel

📊 Data Table: All raw historical values
```

### What to Do
```
1. Select metrics you care about
2. Look at the chart for trends
3. Check the "Change" column for daily moves
4. Look at Min/Max for period ranges
5. Download CSV if you need to share/analyze
```

---

## 📊 20 Metrics Available

```
Equities      │ Rates              │ Credit
S&P 500       │ US 10Y Treasury   │ VIX
EuroStoxx 50  │ US 2Y Treasury    │ HY Spreads
FTSE MIB      │ US 30Y Treasury   │ IG Spreads
              │ EUR Corporate     │
              │ EUR High Yield    │
              │ EUR Emerging      │

Forex         │ Commodities
EUR/USD       │ Brent Crude
EUR/GBP       │ Gold
USD/JPY       │ Natural Gas
GBP/USD       │ Silver
```

---

## 💡 Common Use Cases (Copy-Paste These)

### Morning Market Check
```
Select: S&P 500, VIX, Brent, EUR/USD
Check: "Change" column
Time: 5 minutes
```

### Credit Team Analysis
```
Select: VIX, HY Spreads, IG Spreads, Brent
Check: Are spreads widening?
Export: Download CSV
Time: 10 minutes
```

### Rate Analyst Review
```
Select: All 6 interest rates
Check: Curve slope changes (2Y vs 10Y vs 30Y)
Compare: USD vs EUR performance
Export: For your report
Time: 15 minutes
```

### FX Trading
```
Select: EUR/USD, EUR/GBP, USD/JPY, GBP/USD
Check: Min/Max for trading ranges
Alert: Spot new breakouts
Time: 10 minutes
```

---

## 🔄 How to Get More Data

### Option 1: Schedule It (Best)
Run this **once** in PowerShell (as Administrator):
```powershell
$t = New-ScheduledTaskTrigger -Daily -At 9:00AM
$a = New-ScheduledTaskAction -Execute "C:\Users\alber\PycharmProjects\portfolio_risk_dashboard\fetch_daily_data.bat"
Register-ScheduledTask -TaskName "Daily Risk Factors" -Trigger $t -Action $a -Force
```
Then forget about it. ✅ Auto-runs every day at 9 AM.

### Option 2: Manual Daily
Each morning at 9 AM (or whenever you want):
```powershell
fetch_daily_data.bat
```

### Timeline to Good Data
```
Day 1:  1 snapshot  (just starting)
Day 2:  2 snapshots (trends appear)
Day 5:  5 snapshots (clear patterns)
Day 30: 30 snapshots (full analysis)
```

---

## 🎯 Best Practices

✅ **DO:**
- Select 3-5 metrics at a time
- Use dashboard daily
- Schedule automatic fetches
- Download CSV for reports
- Compare related metrics

❌ **DON'T:**
- Select all 20 metrics at once (too crowded)
- Run fetch only once (no trends)
- Ignore "Change" column (shows daily moves)
- Skip CSV export (useful for others)

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "No data" or "empty chart" | Run `fetch_daily_data.bat` at least 2 times |
| Chart too crowded | Select fewer metrics (3-5 instead of 20) |
| Missing a metric in dropdown | Need to run fetch first |
| Can't download CSV | Scroll down to "Download Statistics CSV" button |
| Dashboard won't open | Try: `streamlit cache clear` |

---

## 📞 Key Files & Guides

```
📌 Pinned Resources:
├─ START_HERE.md           (2 min intro)
├─ QUICKSTART.md           (5 min setup)
├─ README.md               (Full reference)
│
📊 Time Series Specific:
├─ TIME_SERIES_READY.md    (How to use)
├─ TIME_SERIES_UPDATE.md   (Features)
└─ FEATURE_COMPLETE.md     (What's new)
```

---

## 📈 Statistics Table Explained

```
Latest    = Most recent value
Previous  = Yesterday's value
Change    = Today - Yesterday (the daily move!)
Min       = Lowest value in the date range
Max       = Highest value in the date range
Avg       = Average during the period
Std Dev   = How volatile it's been
```

📍 **Focus on "Change" column for daily moves!**

---

## ⚡ One-Minute Cheat Sheet

```
🎯 Your Goal: View dashboard every day

📌 Step 1: Download data
   fetch_daily_data.bat

📌 Step 2: Open dashboard
   launch_dashboard.bat

📌 Step 3: Go to ⏰ Time Series tab

📌 Step 4: Select metrics you care about

📌 Step 5: Analyze charts & download CSV

✅ Done in 5 minutes!
```

---

## 🚀 First Time Setup (Today)

```
1. Open PowerShell in project folder
2. Run: fetch_daily_data.bat
3. Wait for it to complete
4. Run: launch_dashboard.bat
5. Browser opens at http://localhost:8501
6. Click ⏰ Time Series tab
7. Select 3-5 metrics
8. Explore the charts!
9. Bookmark this page for daily use
```

---

## 💾 Data Storage (Auto-managed)

Your data is automatically saved to:
```
data/
├─ risk_snapshot_2026-04-28.json  (full data)
├─ risk_snapshot_2026-04-28.csv   (analysis ready)
└─ [individual asset class files]  (specific tracking)

Logs:
└─ portfolio_risk.log              (activity log)
```

Everything is automatic. You just use the dashboard!

---

## 🎊 You're Ready!

### Command to Get Started Now:
```powershell
cd "C:\Users\alber\PycharmProjects\portfolio_risk_dashboard"
fetch_daily_data.bat
launch_dashboard.bat
```

Then click the **⏰ Time Series** tab!

---

## 📞 Support

**Quick Help:**
- 2-minute intro → START_HERE.md
- Setup help → QUICKSTART.md
- Time Series specifics → TIME_SERIES_READY.md
- Deep dive → README.md

**Feature highlights:**
- 20 metrics
- Interactive charts
- Statistics (Latest, Previous, Change, Min, Max, Avg, Std Dev)
- CSV export
- Historical data table
- 30-day rolling window (configurable 5-90 days)

---

## ⚡ Quick Links Inside Dashboard

```
Sidebar Menu:
├─ 🔄 Refresh Data          (get latest values)
├─ 📥 Fetch Latest Snapshot (fetch fresh data)
├─ Show Historical Charts   (toggle on/off)
└─ Historical Days          (adjust 5-90 days)

Tabs:
├─ 🎯 Summary              (all metrics table)
├─ ⏰ Time Series          (YOUR NEW TAB!) ← Start here
├─ 📈 Equities             (equity indices)
├─ 📊 Interest Rates       (rates detail)
├─ 💳 Credit               (credit detail)
├─ 💱 Forex                (FX detail)
└─ ⚫ Commodities          (commodities detail)
```

---

## 🎯 Today's Action Items

```
☐ 1. Run: fetch_daily_data.bat
☐ 2. Run: launch_dashboard.bat
☐ 3. Click: ⏰ Time Series tab
☐ 4. Select: 3-5 metrics
☐ 5. Review: Chart & statistics
☐ 6. Download: CSV (optional)
☐ 7. Bookmark: This dashboard
☐ 8. Schedule: Daily runs (see above)
```

**Estimated time: 5-10 minutes**

---

## 🌟 You Have

✅ Production-ready dashboard  
✅ 20 real-time metrics  
✅ Time series visualization  
✅ Statistical analysis  
✅ Data export  
✅ Daily automation ready  
✅ Professional UI  
✅ Comprehensive docs  

### Start now! → `fetch_daily_data.bat`

---

**Quick Reference Card v1.0**  
**For additional help, see TIME_SERIES_READY.md**


