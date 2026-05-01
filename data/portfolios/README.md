# Portfolio input store

This folder holds mock portfolio inputs for a multi-asset portfolio manager and the mapping from each position to the downloaded market risk-factor time series.

## Files

- `sample_multi_asset_portfolio.xlsx` is the Excel workbook intended for manual review and editing.
- `positions.csv` is the flat list of portfolio positions.
- `risk_factor_mapping.csv` maps each position to one or more risk factors from `data/historical_data.csv`.
- `risk_factors.csv` lists the currently available downloaded risk factors and their intended use.
- `data_dictionary.csv` documents the portfolio fields.

## Mapping convention

Use `primary_risk_factor`, `fx_risk_factor`, `rate_risk_factor`, and `volatility_risk_factor` in `positions.csv` for a compact view. Use `risk_factor_mapping.csv` when a position has several exposures or sensitivities.

Risk-factor names should match the column names in `data/historical_data.csv` whenever possible. As of the latest local data, the available historical risk factors are:

- Equities: `S&P 500`, `EuroStoxx 50`, `FTSE MIB`, `VIX`
- Rates: `US 1M Treasury`, `US 3M Treasury`, `US 6M Treasury`, `US 1Y Treasury`, `US 2Y Treasury`, `US 3Y Treasury`, `US 5Y Treasury`, `US 7Y Treasury`, `US 10Y Treasury`, `US 20Y Treasury`, `US 30Y Treasury`, `EUR AAA 1Y`, `EUR AAA 2Y`, `EUR AAA 5Y`, `EUR AAA 10Y`, `EUR AAA 20Y`, `EUR AAA 30Y`, `ESTR ON`, `ESTR 1W Realised`, `ESTR 1M Realised`, `ESTR 3M Realised`, `ESTR 6M Realised`, `ESTR 12M Realised`
- Credit: `Investment Grade`, `High Yield`
- FX: `EUR/USD`, `EUR/GBP`, `USD/JPY`, `GBP/USD`
- Commodities: `Brent Crude`, `Gold`, `Natural Gas`, `Silver`
- Crypto: `Bitcoin`, `Ethereum`, `Binance Coin`, `Solana`

EUR OIS market quotes can be uploaded in the dashboard using the downloadable manual quote template. Uploaded OIS quotes are intended to represent forward-looking risk-free market expectations; realised €STR series are backward-looking and should not be treated as OIS curve points.
