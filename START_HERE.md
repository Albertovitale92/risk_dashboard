# 🎯 START HERE - Daily Risk Factors Dashboard

**Welcome!** Your daily risk factors dashboard is ready. Here's how to get started in 2 minutes.

---

## 🚀 Quick Start (Choose One)

### Option A: Fetch Today's Data
```powershell
fetch_daily_data.bat
```

### Option B: View Interactive Dashboard
```powershell
launch_dashboard.bat
```

### Option C: Manual Commands
```powershell
# Activate environment (first time)
.\.venv\Scripts\Activate.ps1

# Fetch data
python run.py fetch

# Or view dashboard
python run.py dashboard
```

---

## 📚 Documentation Guide

**Read in this order:**

1. **[QUICKSTART.md](QUICKSTART.md)** ← Start here (5 min read)
2. **[README.md](README.md)** ← Full reference (20 min read)
3. **[BUILD_SUMMARY.md](BUILD_SUMMARY.md)** ← Architecture (10 min read)
4. **[CHECKLIST.md](CHECKLIST.md)** ← What was built (5 min read)

---

## 📊 What You Have

### ✨ 17 Real-Time Metrics
| Category | Metrics |
|----------|---------|
| 📈 **Equities** | S&P 500, EuroStoxx 50, FTSE MIB |
| 📊 **Rates** | 10Y, 2Y, 30Y Treasury Yields |
| 💳 **Credit** | VIX, HY Spreads, IG Spreads |
| 💱 **Forex** | EUR/USD, EUR/GBP, USD/JPY, GBP/USD |
| ⚫ **Commodities** | Brent, Gold, Natural Gas, Silver |

### 🎨 Interactive Dashboard
- 6 organized tabs
- Real-time metrics
- Historical charts
- One-click refresh
- Settings panel

### 📁 Data Storage
- CSV for Excel analysis
- JSON for code integration
- Automatic daily snapshots
- 7-day log retention

---

## ⚡ Next Steps

### Step 1: Test It Works
```powershell
python run.py fetch
```

You should see all 17 metrics with real market data ✅

### Step 2: View the Dashboard
```powershell
python run.py dashboard
```

Open: **http://localhost:8501**

### Step 3: Schedule Daily Runs
See [QUICKSTART.md](QUICKSTART.md#scheduling-optional)

---

## 🆘 Quick Help

### "Dashboard won't start"
```powershell
streamlit cache clear
python run.py dashboard --logger.level=debug
```

### "No data showing"
- Check internet connection
- Review logs: `logs/portfolio_risk.log`
- Market might be closed outside trading hours

### "Permission error"
- Run PowerShell as Administrator
- Check `data/` folder exists

---

## 📂 Project Files

```
START HERE →
├── QUICKSTART.md         ← 5-minute setup guide
├── README.md             ← Full documentation
├── BUILD_SUMMARY.md      ← Architecture overview
├── CHECKLIST.md          ← What was built
├── COMPLETE.md           ← Feature summary
│
├── fetch_daily_data.bat  ← Click to fetch data
├── launch_dashboard.bat  ← Click to view dashboard
│
├── dashboard.py          ← Interactive UI
├── run.py                ← Command-line interface
│
├── src/
│   ├── data_fetching/    ← Data collection
│   └── utils/            ← Logging & utilities
│
├── data/                 ← Daily snapshots (auto-created)
└── logs/                 ← Activity logs (auto-created)
```

---

## 💡 Common Tasks

### Fetch latest market data
```powershell
python run.py fetch
# Creates: data/risk_snapshot_2026-04-27.csv
```

### View dashboard
```powershell
python run.py dashboard
# Opens: http://localhost:8501
```

### Check logs
```
logs/portfolio_risk.log
```

### Export data for analysis
```
data/risk_snapshot_YYYY-MM-DD.csv
```

---

## 🎯 3-Minute Quick Test

### Test 1: Fetch works?
```powershell
python run.py fetch
```
✅ Should show 17 metrics with real values

### Test 2: Dashboard works?
```powershell
python run.py dashboard
```
✅ Should open browser to http://localhost:8501

### Test 3: Data saved?
```
data/risk_snapshot_2026-04-27.csv
```
✅ Should contain 17 columns of data

---

## 📞 Support

| Question | Answer |
|----------|--------|
| **How do I get started?** | Run `fetch_daily_data.bat` → `launch_dashboard.bat` |
| **What metrics are tracked?** | See table above (17 total) |
| **Can I automate this?** | Yes! See [QUICKSTART.md](QUICKSTART.md#scheduling) |
| **How do I export data?** | Data in `data/` folder as CSV/JSON |
| **Where do I find logs?** | `logs/portfolio_risk.log` |
| **Can I customize it?** | Yes! See [README.md](README.md) |
| **How often updates?** | Daily (configurable) |

---

## ✨ Features at a Glance

✅ **Automatic Data Collection** - Fetches 17 metrics daily  
✅ **Beautiful Dashboard** - Interactive charts & metrics  
✅ **Historical Analysis** - 30+ day trend charts  
✅ **Data Export** - CSV & JSON formats  
✅ **Schedule-Ready** - Windows Task Scheduler integration  
✅ **Well Documented** - 5 comprehensive guides  
✅ **Production Ready** - Tested & verified  
✅ **Easy Setup** - Just run batch files  

---

## 🚀 You're Ready!

Your dashboard is **fully functional and tested** with real market data.

### Pick your first action:
1. **📥 Fetch data:** `fetch_daily_data.bat`
2. **📊 View dashboard:** `launch_dashboard.bat`  
3. **📖 Read docs:** [QUICKSTART.md](QUICKSTART.md)

---

**Need more help?**  
→ Read [QUICKSTART.md](QUICKSTART.md) (5 minutes)  
→ Read [README.md](README.md) (comprehensive guide)  
→ Check [CHECKLIST.md](CHECKLIST.md) (what was built)

---

*Daily Risk Factors Dashboard v1.0.0 - Ready to use! 🎉*

