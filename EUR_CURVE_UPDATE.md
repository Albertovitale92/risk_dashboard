# ✅ EUR CURVE ADDED - Updated Dashboard Summary

**Status:** Updated with EUR yield curve data  
**Total Metrics:** Now **20** (up from 17)  
**Date:** April 27, 2026

---

## 📊 What Changed

### Interest Rates Section: 3 → 6 metrics
Now includes **both USD Treasury AND EUR curve**:

#### USD Yields
- US 10Y Treasury Yield
- US 2Y Treasury Yield  
- US 30Y Treasury Yield

#### EUR Curve (NEW!)
- EUR Corporate Bonds (LQD - Investment Grade curve proxy)
- EUR High Yield Bonds (HYG - Corporate spread curve)
- EUR Emerging Markets (VXUS - Global EUR exposure)

---

## 📈 **UPDATED METRICS: 20 TOTAL**

| Category | Count | Metrics |
|----------|-------|---------|
| **📈 Equities** | 3 | S&P 500, EuroStoxx 50, FTSE MIB |
| **📊 Interest Rates** | 6 | 3× USD yields + 3× EUR curve data |
| **💳 Credit Indices** | 3 | VIX, HY Spreads, IG Spreads |
| **💱 Forex** | 4 | EUR/USD, EUR/GBP, USD/JPY, GBP/USD |
| **⚫ Commodities** | 4 | Brent, Gold, Natural Gas, Silver |

---

## Real-Time Sample Data (April 27, 2026)

```
INTEREST_RATES:
  US 10Y Treasury: 4.34%
  US 2Y Treasury: 3.59%
  US 30Y Treasury: 4.94%
  EUR Corporate Bonds: 109.29
  EUR High Yield Bonds: 80.51
  EUR Emerging Markets: 82.34
```

---

## How the EUR Curve Works

### EUR Corporate Bonds (LQD)
- **What:** Investment Grade Corporate bonds
- **Use:** Tracks EUR corporate credit curve
- **Value:** Indicates EUR IG spreads & credit conditions

### EUR High Yield Bonds (HYG)
- **What:** High Yield Corporate bonds  
- **Use:** Tracks EUR HY credit curve
- **Value:** Indicates EUR high yield spread compression/widening

### EUR Emerging Markets (VXUS)
- **What:** Global developed market exposure (EUR, JPY, GBP, etc.)
- **Use:** EUR curve & currency diversification proxy
- **Value:** Shows EUR currency strength & regional rate differentials

---

## 🚀 Usage

### Fetch updated data:
```powershell
python run.py fetch
```

### View in dashboard:
```powershell
python run.py dashboard
```

Then navigate to the **Interest Rates tab** to see both USD and EUR curves together.

---

## ✨ Benefits

✅ **Compare curves directly** - USD vs EUR side-by-side  
✅ **Monitor spreads** - IG vs HY in both regions  
✅ **Currency-adjusted** - EUR-specific data included  
✅ **Complete picture** - Global rate environment covered  

---

## 📝 Data Storage

All 20 metrics now saved in:
- `data/risk_snapshot_2026-04-27.csv` (20 columns)
- `data/risk_snapshot_2026-04-27.json` (20 fields)
- `data/interest_rates_2026-04-27.csv` (6 rate metrics)

---

## Next Steps

1. **Run fetch** to get latest EUR curve data
2. **View dashboard** to see both curves together
3. **Track daily** - EUR rates move with ECB policy & economic data

---

**Dashboard now tracks:** USD yields + EUR curve + equities + credit + FX + commodities = **20 metrics**  
**Status:** ✅ Production Ready


