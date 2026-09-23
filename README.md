# Portfolio Risk Dashboard

Streamlit visualization and descriptive analysis layer for the shared
`Risk_Factors` project. This repository does **not** download market data.

## Data ownership

`Risk_Factors` is the single source for risk-factor data, historical storage,
market-data providers, curves, and risk analytics. Install or make it
available at:

```text
C:\Users\alber\PycharmProjects\Risk_Factors
```

For another location, set:

```powershell
$env:RISK_FACTORS_PROJECT = "C:\path\to\Risk_Factors"
```

The dashboard reads the shared Parquet store at
`Risk_Factors\data\raw\risk_factors_levels.parquet`. Use the **Refresh
Risk_Factors Store** button in the sidebar to update it. Existing legacy CSV
files under this repository's `data\` directory are not used by the
dashboard.

## Running

Install the dependencies for both projects, then launch:

```powershell
streamlit run dashboard.py
```

or:

```powershell
python run.py dashboard
```

`launch_dashboard.bat` provides the Windows shortcut.

## Dashboard features

- current risk-factor snapshot grouped by asset class;
- historical levels and interactive time-series charts;
- global date filters, including the last 60 days and custom ranges;
- 10-day overlapping returns and descriptive statistics;
- USD Treasury and EUR AAA yield-curve views;
- EUR OIS/€STR curve construction from the shared Risk_Factors source;
- curve comparisons, slopes, and recent curve evolution.

The dashboard does not calculate portfolio P&L, position-level exposures, VaR,
or Expected Shortfall. Those capabilities belong in `Risk_Factors`.
