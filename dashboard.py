"""Streamlit dashboard for daily risk factors."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import math

from src.data_fetching.risk_aggregator import RiskDashboardAggregator
from src.data_fetching.interest_rates_fetcher import fetch_ecb_mmsr_ois_curve
from src.analysis.returns_calculator import ReturnsCalculator
from src.utils.logger import get_logger

logger = get_logger(__name__)


ECB_OIS_METRIC_TENORS = {
    "ECB OIS 1M": "1M",
    "ECB OIS 2M": "2M",
    "ECB OIS 3M": "3M",
    "ECB OIS 6M": "6M",
    "ECB OIS 9M": "9M",
    "ECB OIS 12M": "12M",
    "ECB OIS 2Y": "2Y",
    "ECB OIS 3Y": "3Y",
    "ECB OIS 5Y": "5Y",
    "ECB OIS 10Y": "10Y",
}


def format_date_value(value):
    """Return YYYY-MM-DD for Streamlit date widgets and pandas timestamps."""
    return pd.to_datetime(value).strftime("%Y-%m-%d")


def resolve_curve_row(curve_history, selected_date):
    """Return the latest available curve row on or before selected_date."""
    selected_ts = pd.to_datetime(selected_date)
    curve_dates = pd.to_datetime(curve_history["date"])
    available = curve_history[curve_dates <= selected_ts]
    if available.empty:
        return pd.DataFrame(), None

    row = available.tail(1)
    return row, row["date"].iloc[0]


def tenor_to_years(tenor):
    """Convert tenor strings such as 1W, 3M, 5Y into year fractions."""
    tenor_str = str(tenor).strip().upper()
    if not tenor_str:
        raise ValueError("Empty tenor")

    unit = tenor_str[-1]
    amount = float(tenor_str[:-1])
    if unit == "D":
        return amount / 365
    if unit == "W":
        return amount / 52
    if unit == "M":
        return amount / 12
    if unit == "Y":
        return amount
    raise ValueError(f"Unsupported tenor unit: {tenor}")


def prepare_ois_quotes(quotes_df):
    """Validate and sort uploaded EUR OIS quote data."""
    required = {"tenor", "rate"}
    normalized_columns = {col: str(col).strip().lower() for col in quotes_df.columns}
    quotes = quotes_df.rename(columns=normalized_columns)

    missing = required - set(quotes.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    quotes = quotes[["tenor", "rate"]].copy()
    quotes["tenor"] = quotes["tenor"].astype(str).str.strip().str.upper()
    quotes["years"] = quotes["tenor"].apply(tenor_to_years)
    quotes["rate"] = pd.to_numeric(quotes["rate"], errors="coerce")
    quotes = quotes.dropna(subset=["rate", "years"]).sort_values("years")
    quotes = quotes.drop_duplicates(subset=["years"], keep="last").reset_index(drop=True)

    if len(quotes) < 2:
        raise ValueError("Provide at least two OIS quote points.")
    return quotes


def interpolate_zero_rate(years, known_years, known_zero_rates):
    """Linear interpolation/extrapolation of zero rates on maturity."""
    if years <= known_years[0]:
        return known_zero_rates[0]
    if years >= known_years[-1]:
        return known_zero_rates[-1]

    for idx in range(1, len(known_years)):
        left_year = known_years[idx - 1]
        right_year = known_years[idx]
        if left_year <= years <= right_year:
            weight = (years - left_year) / (right_year - left_year)
            return known_zero_rates[idx - 1] + weight * (known_zero_rates[idx] - known_zero_rates[idx - 1])
    return known_zero_rates[-1]


def build_eur_ois_curve(quotes_df):
    """
    Build an indicative EUR OIS zero curve from user-supplied par quotes.

    The short end is treated as simple money-market rates. For maturities above
    one year, annual fixed-leg par swaps are bootstrapped with linear zero-rate
    interpolation between existing pillars for intermediate coupon dates.
    """
    quotes = prepare_ois_quotes(quotes_df)
    known_years = []
    known_zero_rates = []
    output_rows = []

    for _, quote in quotes.iterrows():
        maturity = float(quote["years"])
        par_rate = float(quote["rate"]) / 100

        if maturity <= 1:
            discount_factor = 1 / (1 + par_rate * maturity)
        else:
            coupon_times = list(range(1, int(math.floor(maturity)) + 1))
            if not math.isclose(coupon_times[-1], maturity):
                coupon_times.append(maturity)

            accrued_discount_sum = 0
            for payment_time in coupon_times[:-1]:
                zero_rate = (
                    interpolate_zero_rate(payment_time, known_years, known_zero_rates)
                    if known_years else par_rate
                )
                accrued_discount_sum += math.exp(-zero_rate * payment_time)

            final_accrual = maturity - coupon_times[-2] if len(coupon_times) > 1 else maturity
            discount_factor = (1 - par_rate * accrued_discount_sum) / (1 + par_rate * final_accrual)

        discount_factor = max(discount_factor, 1e-8)
        zero_rate = -math.log(discount_factor) / maturity
        known_years.append(maturity)
        known_zero_rates.append(zero_rate)
        output_rows.append({
            "tenor": quote["tenor"],
            "years": maturity,
            "par_rate": float(quote["rate"]),
            "zero_rate": zero_rate * 100,
            "discount_factor": discount_factor,
        })

    return pd.DataFrame(output_rows)


@st.cache_data(ttl=60 * 60)
def fetch_latest_ecb_ois_quotes():
    """Fetch latest free ECB MMSR OIS weighted-average rate buckets."""
    ois_curve = fetch_ecb_mmsr_ois_curve(last_n_observations=1)
    if ois_curve.empty:
        return pd.DataFrame(columns=["tenor", "rate", "source_date", "source_metric"])

    latest_by_metric = ois_curve.sort_values("date").groupby("metric").tail(1)
    return pd.DataFrame({
        "tenor": latest_by_metric["tenor"],
        "rate": latest_by_metric["value"],
        "source_date": latest_by_metric["date"].dt.strftime("%Y-%m-%d"),
        "source_metric": latest_by_metric["metric"],
    }).reset_index(drop=True)


def load_local_ecb_ois_quotes(snapshot, historical):
    """Build OIS quote input from latest local snapshot or historical data."""
    rates = snapshot.get("data", {}).get("interest_rates", {}) if snapshot else {}
    rows = []

    for metric, tenor in ECB_OIS_METRIC_TENORS.items():
        value = rates.get(metric)
        if value is not None and pd.notna(value):
            rows.append({
                "tenor": tenor,
                "rate": float(value),
                "source_date": snapshot.get("date"),
                "source_metric": metric,
            })

    if rows:
        return pd.DataFrame(rows)

    if historical.empty:
        return pd.DataFrame(columns=["tenor", "rate", "source_date", "source_metric"])

    for metric, tenor in ECB_OIS_METRIC_TENORS.items():
        if metric not in historical.columns:
            continue
        metric_history = historical[["date", metric]].dropna()
        if metric_history.empty:
            continue
        latest = metric_history.tail(1).iloc[0]
        rows.append({
            "tenor": tenor,
            "rate": float(latest[metric]),
            "source_date": latest["date"],
            "source_metric": metric,
        })

    return pd.DataFrame(rows)


# Page configuration
st.set_page_config(
    page_title="Daily Risk Factors Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
st.markdown("""
    <style>
    .metric-container {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .header {
        color: #1f77b4;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)


@st.cache_resource
def get_aggregator():
    """Initialize and cache the aggregator."""
    return RiskDashboardAggregator(data_dir="data")


def display_metric(label, value, previous_value=None, decimals=2, format_type="number"):
    """Display a single metric with optional change indicator."""
    if value is None:
        st.metric(label, "N/A", help="Data not available")
        return

    if format_type == "currency":
        formatted_value = f"${value:,.{decimals}f}"
    elif format_type == "percent":
        formatted_value = f"{value:.{decimals}f}%"
    else:  # number
        formatted_value = f"{value:,.{decimals}f}"

    if previous_value is not None and previous_value is not None:
        delta = value - previous_value
        st.metric(label, formatted_value, delta=delta)
    else:
        st.metric(label, formatted_value)


def format_dataframe_for_display(df):
    """Format dataframe for nice display."""
    return df.style.format({
        col: "{:.4f}" if df[col].dtype in ['float64', 'float32'] else "{}"
        for col in df.columns
    })


# ============================================================================
# MAIN APP
# ============================================================================

def main():
    st.title("📊 Daily Risk Factors Dashboard")

    # Sidebar controls
    with st.sidebar:
        st.header("⚙️ Controls")

        aggregator = get_aggregator()

        # Refresh button
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.session_state.refresh_key = datetime.now().timestamp()
            st.rerun()

        # Manual fetch
        if st.button("📥 Fetch Latest Snapshot", use_container_width=True):
            with st.spinner("Fetching risk factors..."):
                try:
                    snapshot = aggregator.save_daily_snapshot()
                    st.success("✓ Data fetched successfully!")
                except Exception as e:
                    st.error(f"✗ Error: {e}")

        st.divider()

        # Historical data fetch (show only if not already loaded)
        if aggregator.load_full_historical_data().empty:
            st.subheader("📅 Historical Data Setup")
            hist_years = st.radio("Years of history:", [1, 3, 5, 10], value=3, help="First time only - takes a few minutes (max 10 years)")
            if st.button("🔄 Fetch Historical Data", use_container_width=True, help="Initialize historical data database"):
                with st.spinner(f"Fetching {hist_years} years of historical data (this may take 3-5 minutes)..."):
                    try:
                        hist_data = aggregator.fetch_and_save_historical_data(years=hist_years)
                        if not hist_data.empty:
                            st.success(f"✓ Loaded {len(hist_data)} trading days of historical data!")
                            st.rerun()
                        else:
                            st.error("✗ Failed to load historical data")
                    except Exception as e:
                        st.error(f"✗ Error: {e}")
        else:
            latest_hist = aggregator.load_full_historical_data()
            if not latest_hist.empty:
                st.success(f"✅ Historical data loaded: {latest_hist['date'].min()} to {latest_hist['date'].max()}")

        st.divider()

        # Settings
        st.subheader("Display Settings")
        show_historical = st.checkbox("Show Historical Charts", value=True)
        historical_days = st.slider("Historical Days", 5, 90, 30)


    # Main content
    # Get latest snapshot
    snapshot = aggregator.get_latest_snapshot()

    # Try to load full historical data first, fall back to recent snapshots
    historical = aggregator.load_full_historical_data()
    if historical.empty:
        # Fall back to recent daily snapshots if no full history
        historical = aggregator.get_historical_data(days=historical_days)
        if not historical.empty:
            st.info("📊 Using recent daily snapshots (3-4 year historical data not yet loaded). See documentation for historical data setup.")

    if snapshot is None:
        st.warning("⚠️ No data available. Click 'Fetch Latest Snapshot' to get started.")
        return

    # Header with timestamp
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"Last Updated: {snapshot['timestamp']}")
    with col2:
        st.metric("Data Date", snapshot['date'])

    st.divider()

    # Tabs for each asset class
    tabs = st.tabs([
        "🎯 Summary",
        "⏰ Time Series",
        "📈 Equities",
        "📊 Interest Rates",
        "📉 Yield Curve",
        "💳 Credit",
        "💱 Forex",
        "⚫ Commodities",
        "₿ Cryptocurrencies"
    ])

    # ========== SUMMARY TAB ==========
    with tabs[0]:
        st.subheader("Risk Factors Overview")

        summary_data = []
        for asset_class, values in snapshot['data'].items():
            for metric, value in values.items():
                if value is not None:
                    summary_data.append({
                        "Asset Class": asset_class.replace('_', ' ').title(),
                        "Metric": metric,
                        "Value": value
                    })

        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True)
        else:
            st.info("No data available")

    # ========== TIME SERIES TAB ==========
    with tabs[1]:
        st.subheader("⏰ All Metrics - Time Series Analysis (Up to 10 Years)")
        
        if historical.empty:
            st.warning("⚠️ No historical data available. Click 'Fetch Historical Data' in sidebar to get started.")
        else:
            # Display date range
            date_min = pd.to_datetime(historical['date']).min()
            date_max = pd.to_datetime(historical['date']).max()
            date_range = f"{date_min.strftime('%Y-%m-%d')} to {date_max.strftime('%Y-%m-%d')}"
            st.info(f"📅 Data Period: {date_range} ({len(historical)} trading days)")
            
            # Date range selector for filtering
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input(
                    "Start Date",
                    value=date_min,
                    min_value=date_min,
                    max_value=date_max
                )
            with col2:
                end_date = st.date_input(
                    "End Date",
                    value=date_max,
                    min_value=date_min,
                    max_value=date_max
                )
            
            # Filter data by date range
            historical_filtered = historical[
                (pd.to_datetime(historical['date']) >= pd.Timestamp(start_date)) &
                (pd.to_datetime(historical['date']) <= pd.Timestamp(end_date))
            ].copy()
            
            if len(historical_filtered) == 0:
                st.error("No data in selected date range")
            else:
                # Metric selector
                all_metrics = [col for col in historical_filtered.columns if col not in ['date', 'timestamp']]
                selected_metrics = st.multiselect(
                    f"Select Metrics to Display ({len(all_metrics)} available)",
                    all_metrics,
                    default=all_metrics[:5] if len(all_metrics) > 5 else all_metrics,
                    key="metrics_multiselect"
                )
                
                if selected_metrics:
                    # Create time series chart
                    st.subheader("Time Series Values")
                    fig = go.Figure()
                    
                    for metric in selected_metrics:
                        fig.add_trace(go.Scatter(
                            x=historical_filtered['date'],
                            y=historical_filtered[metric],
                            mode='lines+markers',
                            name=metric,
                            hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Value: %{y:.4f}<extra></extra>'
                        ))
                    
                    fig.update_layout(
                        title=f"Risk Factors Time Series ({len(historical_filtered)} days)",
                        xaxis_title="Date",
                        yaxis_title="Value",
                        hovermode='x unified',
                        height=600,
                        template='plotly_white'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Statistics table
                    st.subheader("Statistical Summary")
                    stats_data = []
                    for metric in selected_metrics:
                        if metric in historical_filtered.columns:
                            col_data = historical_filtered[metric].dropna()
                            if len(col_data) > 0:
                                stats_data.append({
                                    "Metric": metric,
                                    "Latest": col_data.iloc[-1],
                                    "Previous": col_data.iloc[-2] if len(col_data) > 1 else None,
                                    "Change": col_data.iloc[-1] - col_data.iloc[-2] if len(col_data) > 1 else None,
                                    "Min": col_data.min(),
                                    "Max": col_data.max(),
                                    "Avg": col_data.mean(),
                                    "Std Dev": col_data.std()
                                })
                    
                    if stats_data:
                        stats_df = pd.DataFrame(stats_data)
                        st.dataframe(
                            stats_df.style.format({
                                "Latest": "{:.4f}",
                                "Previous": "{:.4f}",
                                "Change": "{:.4f}",
                                "Min": "{:.4f}",
                                "Max": "{:.4f}",
                                "Avg": "{:.4f}",
                                "Std Dev": "{:.6f}"
                            }),
                            use_container_width=True
                        )
                        
                        # Download option
                        csv_export = stats_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Statistics as CSV",
                            data=csv_export,
                            file_name=f"risk_factors_stats_{datetime.now().strftime('%Y-%m-%d')}.csv",
                            mime="text/csv"
                        )
                else:
                    st.info("Please select at least one metric to display")
                
                # Full historical data table
                st.subheader("Full Historical Data")
                st.dataframe(
                    historical_filtered.style.format({
                        col: "{:.6f}" if historical_filtered[col].dtype in ['float64', 'float32'] else "{}"
                        for col in historical_filtered.columns
                    }),
                    use_container_width=True,
                    height=400
                )

    # ========== EQUITIES TAB ==========
    with tabs[2]:
        st.subheader("📈 Equity Indices")

        equities = snapshot['data'].get('equities', {})
        if equities:
            # Display current values
            cols = st.columns(len(equities))
            for col, (metric, value) in zip(cols, equities.items()):
                with col:
                    if value is not None:
                        st.metric(metric, f"{value:,.2f}")
                    else:
                        st.metric(metric, "N/A")

            # Toggle buttons for prices vs returns
            st.subheader("Analysis View")
            col1, col2 = st.columns(2)
            with col1:
                show_eq_prices = st.button("📊 Prices", key="eq_prices_btn")
            with col2:
                show_eq_returns = st.button("📈 10-Day Returns", key="eq_returns_btn")

            # Initialize session state for toggle
            if "show_eq_returns" not in st.session_state:
                st.session_state.show_eq_returns = False
            if show_eq_prices:
                st.session_state.show_eq_returns = False
            if show_eq_returns:
                st.session_state.show_eq_returns = True

            # Prices view
            if not st.session_state.show_eq_returns and show_historical and not historical.empty:
                st.subheader("Equity Indices - Price Trends")
                
                equity_cols = ["S&P 500", "EuroStoxx 50", "FTSE MIB"]
                equity_cols = [col for col in equity_cols if col in historical.columns]

                if equity_cols:
                    fig = go.Figure()
                    for col in equity_cols:
                        fig.add_trace(go.Scatter(
                            x=historical['date'],
                            y=historical[col],
                            mode='lines+markers',
                            name=col,
                            hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Value: %{y:.2f}<extra></extra>'
                        ))

                    fig.update_layout(
                        title="Equity Indices Historical Trend",
                        xaxis_title="Date",
                        yaxis_title="Index Level",
                        hovermode='x unified',
                        height=500,
                        template='plotly_white'
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # Returns view
            elif st.session_state.show_eq_returns:
                st.subheader("Equity Indices - 10-Day Returns (%)")
                
                returns_calc = ReturnsCalculator()
                returns_df, organized_returns = returns_calc.load_and_calculate_returns()
                
                if not returns_df.empty and "equities" in organized_returns:
                    eq_returns = organized_returns["equities"]
                    
                    if not eq_returns.empty:
                        # Filter out date column and get metric columns
                        eq_metrics = [col for col in eq_returns.columns if col != 'date']
                        
                        # Plot returns
                        if eq_metrics:
                            fig = go.Figure()
                            for metric in eq_metrics:
                                fig.add_trace(go.Scatter(
                                    x=eq_returns['date'],
                                    y=eq_returns[metric],
                                    mode='lines+markers',
                                    name=metric,
                                    hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Return: %{y:.2f}%<extra></extra>'
                                ))
                            
                            fig.update_layout(
                                title="Equity Indices - 10-Day Overlapping Returns",
                                xaxis_title="Date",
                                yaxis_title="Return (%)",
                                hovermode='x unified',
                                height=500,
                                template='plotly_white'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Statistics table
                        st.subheader("Returns Statistics")
                        stats = returns_calc.get_summary_statistics(eq_returns)
                        
                        if stats:
                            stats_data = []
                            for metric, stat_dict in stats.items():
                                stats_data.append({
                                    "Metric": metric,
                                    "Latest (%)": stat_dict["latest"],
                                    "Mean (%)": stat_dict["mean"],
                                    "Std Dev (%)": stat_dict["std"],
                                    "Min (%)": stat_dict["min"],
                                    "Max (%)": stat_dict["max"]
                                })
                            
                            stats_df = pd.DataFrame(stats_data)
                            st.dataframe(
                                stats_df.style.format({
                                    "Latest (%)": "{:.2f}",
                                    "Mean (%)": "{:.2f}",
                                    "Std Dev (%)": "{:.2f}",
                                    "Min (%)": "{:.2f}",
                                    "Max (%)": "{:.2f}"
                                }),
                                use_container_width=True
                            )
                    else:
                        st.info("No equity returns data available")
                else:
                    st.info("Historical data not loaded. Click 'Fetch 3-4 Year History' in sidebar.")
        else:
            st.info("No equity data available")

    # ========== INTEREST RATES TAB ==========
    with tabs[3]:
        st.subheader("📊 Interest Rates")

        rates = snapshot['data'].get('interest_rates', {})
        if rates:
            # Display current values in columns
            cols = st.columns(len(rates))
            for col, (metric, value) in zip(cols, rates.items()):
                with col:
                    if value is not None:
                        st.metric(metric, f"{value:.4f}")
                    else:
                        st.metric(metric, "N/A")

            # Toggle buttons for prices vs returns
            st.subheader("Analysis View")
            col1, col2 = st.columns(2)
            with col1:
                show_ir_prices = st.button("📊 Prices", key="ir_prices_btn")
            with col2:
                show_ir_returns = st.button("📈 10-Day Returns", key="ir_returns_btn")

            # Initialize session state for toggle
            if "show_ir_returns" not in st.session_state:
                st.session_state.show_ir_returns = False
            if show_ir_prices:
                st.session_state.show_ir_returns = False
            if show_ir_returns:
                st.session_state.show_ir_returns = True

            # Prices view
            if not st.session_state.show_ir_returns and show_historical and not historical.empty:
                st.subheader("Interest Rates - Price Trends")
                
                # Filter interest rate columns
                treasury_order = [
                    "US 1M Treasury", "US 3M Treasury", "US 6M Treasury",
                    "US 1Y Treasury", "US 2Y Treasury", "US 3Y Treasury",
                    "US 5Y Treasury", "US 7Y Treasury", "US 10Y Treasury",
                    "US 20Y Treasury", "US 30Y Treasury"
                ]
                rate_cols = treasury_order + ["EURIBOR 3M"]
                rate_cols = [col for col in rate_cols if col in historical.columns]
                
                if rate_cols:
                    fig = go.Figure()
                    for col in rate_cols:
                        fig.add_trace(go.Scatter(
                            x=historical['date'],
                            y=historical[col],
                            mode='lines+markers',
                            name=col,
                            hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Value: %{y:.2f}<extra></extra>'
                        ))
                    
                    fig.update_layout(
                        title="Interest Rates Historical Trend",
                        xaxis_title="Date",
                        yaxis_title="Rate",
                        hovermode='x unified',
                        height=500,
                        template='plotly_white'
                    )
                    st.plotly_chart(fig, use_container_width=True)

                estr_cols = [
                    "ESTR ON", "ESTR 1W Realised", "ESTR 1M Realised",
                    "ESTR 3M Realised", "ESTR 6M Realised", "ESTR 12M Realised"
                ]
                estr_cols = [col for col in estr_cols if col in historical.columns]
                if estr_cols:
                    st.subheader("€STR Realised Rates")
                    st.caption("Backward-looking ECB €STR and compounded €STR rates; these are not forward OIS curve points.")

                    latest_estr = historical[['date'] + estr_cols].dropna(
                        subset=estr_cols,
                        how='all'
                    ).tail(1)
                    if not latest_estr.empty:
                        st.dataframe(
                            latest_estr.set_index("date").T.rename(columns={latest_estr["date"].iloc[0]: "Rate (%)"}),
                            use_container_width=True
                        )

                    fig = go.Figure()
                    for col in estr_cols:
                        fig.add_trace(go.Scatter(
                            x=historical['date'],
                            y=historical[col],
                            mode='lines',
                            name=col,
                            hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Rate: %{y:.4f}%<extra></extra>'
                        ))
                    fig.update_layout(
                        title="€STR Realised Rates",
                        xaxis_title="Date",
                        yaxis_title="Rate (%)",
                        hovermode='x unified',
                        height=420,
                        template='plotly_white'
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # Returns view
            elif st.session_state.show_ir_returns:
                st.subheader("Interest Rates - 10-Day Returns (%)")
                
                returns_calc = ReturnsCalculator()
                returns_df, organized_returns = returns_calc.load_and_calculate_returns()
                
                if not returns_df.empty and "interest_rates" in organized_returns:
                    ir_returns = organized_returns["interest_rates"]
                    
                    if not ir_returns.empty:
                        # Filter out date column and get metric columns
                        ir_metrics = [col for col in ir_returns.columns if col != 'date']
                        
                        # Plot returns
                        if ir_metrics:
                            fig = go.Figure()
                            for metric in ir_metrics:
                                fig.add_trace(go.Scatter(
                                    x=ir_returns['date'],
                                    y=ir_returns[metric],
                                    mode='lines+markers',
                                    name=metric,
                                    hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Return: %{y:.2f}%<extra></extra>'
                                ))
                            
                            fig.update_layout(
                                title="Interest Rates - 10-Day Overlapping Returns",
                                xaxis_title="Date",
                                yaxis_title="Return (%)",
                                hovermode='x unified',
                                height=500,
                                template='plotly_white'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Statistics table
                        st.subheader("Returns Statistics")
                        stats = returns_calc.get_summary_statistics(ir_returns)
                        
                        if stats:
                            stats_data = []
                            for metric, stat_dict in stats.items():
                                stats_data.append({
                                    "Metric": metric,
                                    "Latest (%)": stat_dict["latest"],
                                    "Mean (%)": stat_dict["mean"],
                                    "Std Dev (%)": stat_dict["std"],
                                    "Min (%)": stat_dict["min"],
                                    "Max (%)": stat_dict["max"]
                                })
                            
                            stats_df = pd.DataFrame(stats_data)
                            st.dataframe(
                                stats_df.style.format({
                                    "Latest (%)": "{:.2f}",
                                    "Mean (%)": "{:.2f}",
                                    "Std Dev (%)": "{:.2f}",
                                    "Min (%)": "{:.2f}",
                                    "Max (%)": "{:.2f}"
                                }),
                                use_container_width=True
                            )
                    else:
                        st.info("No interest rate returns data available")
                else:
                    st.info("Historical data not loaded. Click 'Fetch 3-4 Year History' in sidebar.")
        else:
            st.info("No interest rate data available")

    # ========== YIELD CURVE TAB ==========
    with tabs[4]:
        st.subheader("📉 Interest Rate Curve")
        st.markdown("**ALM/Treasury Strategy View**: Monitor risk-free OIS curves and secondary government-bond curves")

        st.subheader("EUR OIS / €STR Risk-Free Curve")
        st.caption(
            "Automatic source: ECB MMSR OIS weighted-average rates by maturity bucket. "
            "These are transaction-based OIS statistics, not live executable dealer quotes. "
            "Realised €STR fixings are backward-looking; OIS rates reference expected compounded overnight €STR over the contract horizon."
        )

        template_csv = (
            "tenor,rate\n"
            "1M,1.95\n"
            "2M,1.98\n"
            "3M,2.00\n"
            "6M,2.08\n"
            "9M,2.12\n"
            "1Y,2.15\n"
            "2Y,2.25\n"
            "3Y,2.35\n"
            "5Y,2.45\n"
            "10Y,2.75\n"
        )

        st.download_button(
            "Download Manual OIS Quote Template",
            data=template_csv,
            file_name="eur_ois_quotes_template.csv",
            mime="text/csv",
            use_container_width=True
        )

        auto_ois_quotes = load_local_ecb_ois_quotes(snapshot, historical)

        if st.button("Refresh ECB OIS Curve Now", use_container_width=True):
            with st.spinner("Fetching ECB MMSR OIS curve..."):
                try:
                    st.session_state.latest_ecb_ois_quotes = fetch_latest_ecb_ois_quotes()
                except Exception as e:
                    st.warning(f"ECB OIS fetch failed: {e}")

        if "latest_ecb_ois_quotes" in st.session_state and not st.session_state.latest_ecb_ois_quotes.empty:
            auto_ois_quotes = st.session_state.latest_ecb_ois_quotes

        use_manual_ois_quotes = st.checkbox(
            "Override automatic ECB OIS source with uploaded quotes",
            value=False,
            key="manual_ois_override"
        )

        uploaded_ois_quotes = None
        if use_manual_ois_quotes or auto_ois_quotes.empty:
            uploaded_ois_quotes = st.file_uploader(
                "Upload EUR OIS quotes",
                type=["csv", "xlsx"],
                key="eur_ois_quotes_upload"
            )

        ois_input_quotes = pd.DataFrame()
        ois_source_label = None
        if not use_manual_ois_quotes and not auto_ois_quotes.empty:
            ois_input_quotes = auto_ois_quotes[["tenor", "rate"]].copy()
            source_dates = sorted(auto_ois_quotes["source_date"].dropna().unique())
            if len(source_dates) == 1:
                ois_source_label = f"ECB MMSR OIS weighted-average rates, observation date {source_dates[0]}"
            else:
                ois_source_label = f"ECB MMSR OIS weighted-average rates, observation dates {source_dates[0]} to {source_dates[-1]}"
        elif uploaded_ois_quotes is not None:
            try:
                if uploaded_ois_quotes.name.lower().endswith(".xlsx"):
                    ois_input_quotes = pd.read_excel(uploaded_ois_quotes)
                else:
                    ois_input_quotes = pd.read_csv(uploaded_ois_quotes)
                ois_source_label = "Uploaded manual OIS quotes"
            except Exception as e:
                st.error(f"Could not read uploaded OIS quotes: {e}")

        if not ois_input_quotes.empty:
            try:
                ois_curve = build_eur_ois_curve(ois_input_quotes)
                st.caption(f"Curve source: {ois_source_label}")

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=ois_curve["years"],
                    y=ois_curve["par_rate"],
                    mode="lines+markers",
                    name="Input par OIS quotes",
                    text=ois_curve["tenor"],
                    hovertemplate="<b>%{text}</b><br>Par rate: %{y:.4f}%<extra></extra>"
                ))
                fig.add_trace(go.Scatter(
                    x=ois_curve["years"],
                    y=ois_curve["zero_rate"],
                    mode="lines+markers",
                    name="Indicative bootstrapped zero curve",
                    text=ois_curve["tenor"],
                    hovertemplate="<b>%{text}</b><br>Zero rate: %{y:.4f}%<extra></extra>"
                ))
                fig.update_layout(
                    title="EUR OIS / €STR Risk-Free Curve",
                    xaxis_title="Tenor (Years)",
                    yaxis_title="Rate (%)",
                    height=450,
                    template="plotly_white",
                    hovermode="x unified"
                )
                st.plotly_chart(fig, use_container_width=True)

                st.dataframe(
                    ois_curve[["tenor", "years", "par_rate", "zero_rate", "discount_factor"]].style.format({
                        "years": "{:.4f}",
                        "par_rate": "{:.4f}",
                        "zero_rate": "{:.4f}",
                        "discount_factor": "{:.8f}",
                    }),
                    use_container_width=True
                )
                st.caption(
                    "Indicative annual-pay bootstrap with linear zero-rate interpolation. "
                    "For production ALM valuation, use a licensed market-data curve with exact EUR OIS conventions."
                )
            except Exception as e:
                st.error(f"Could not build EUR OIS curve: {e}")
        else:
            st.info(
                "No local ECB OIS data available yet. Click 'Refresh ECB OIS Curve Now', "
                "run 'Fetch Latest Snapshot', or upload OIS quotes."
            )

        st.markdown("---")
        st.subheader("Government-Bond Curve Comparison")
        st.caption(
            "The EUR government-bond curve below is useful for market comparison, but it is not a pure risk-free "
            "discounting curve because it can include sovereign, liquidity, scarcity, and basket-composition premia."
        )
        
        if not historical.empty:
            curve_definitions = {
                "USD": {
                    "title": "USD Treasury Yield Curve",
                    "source": "FRED Treasury constant-maturity rates",
                    "columns": {
                        "US 1M Treasury": (1 / 12, "1M"),
                        "US 3M Treasury": (0.25, "3M"),
                        "US 6M Treasury": (0.5, "6M"),
                        "US 1Y Treasury": (1, "1Y"),
                        "US 2Y Treasury": (2, "2Y"),
                        "US 3Y Treasury": (3, "3Y"),
                        "US 5Y Treasury": (5, "5Y"),
                        "US 7Y Treasury": (7, "7Y"),
                        "US 10Y Treasury": (10, "10Y"),
                        "US 20Y Treasury": (20, "20Y"),
                        "US 30Y Treasury": (30, "30Y"),
                    },
                    "slope_pairs": [
                        ("US 2Y Treasury", "US 30Y Treasury", "30Y-2Y"),
                        ("US 2Y Treasury", "US 10Y Treasury", "10Y-2Y"),
                        ("US 10Y Treasury", "US 30Y Treasury", "30Y-10Y"),
                    ],
                },
                "EUR": {
                    "title": "EUR AAA Government Bond Spot Curve",
                    "source": "ECB AAA euro-area government-bond spot curve; secondary comparison curve, not pure OIS risk-free",
                    "columns": {
                        "EUR AAA 1Y": (1, "1Y"),
                        "EUR AAA 2Y": (2, "2Y"),
                        "EUR AAA 5Y": (5, "5Y"),
                        "EUR AAA 10Y": (10, "10Y"),
                        "EUR AAA 20Y": (20, "20Y"),
                        "EUR AAA 30Y": (30, "30Y"),
                    },
                    "slope_pairs": [
                        ("EUR AAA 2Y", "EUR AAA 30Y", "30Y-2Y"),
                        ("EUR AAA 2Y", "EUR AAA 10Y", "10Y-2Y"),
                        ("EUR AAA 10Y", "EUR AAA 30Y", "30Y-10Y"),
                    ],
                },
            }

            selected_ccy = st.radio(
                "Currency",
                options=["USD", "EUR"],
                index=0,
                horizontal=True,
                key="yield_curve_currency"
            )
            curve_definition = curve_definitions[selected_ccy]
            curve_columns = curve_definition["columns"]
            available_cols = [col for col in curve_columns if col in historical.columns]
            available_tenors = [curve_columns[col][0] for col in available_cols]
            available_labels = [curve_columns[col][1] for col in available_cols]
            curve_history = historical[['date'] + available_cols].dropna(
                subset=available_cols,
                how='all'
            ) if available_cols else pd.DataFrame()
            
            if available_cols:
                st.caption(f"{curve_definition['title']} | Source: {curve_definition['source']}")
                st.markdown("---")
                
                # Date selection for comparison
                col1, col2, col3 = st.columns(3)
                with col1:
                    curve_view = st.radio(
                        "View Type",
                        ["Latest Curve", "Curve Comparison", "Curve Evolution"],
                        help="Choose how to view the yield curve"
                    )
                
                if curve_view == "Latest Curve":
                    # Show the most recent yield curve
                    latest_date = curve_history['date'].iloc[-1] if not curve_history.empty else None
                    latest_data = curve_history[curve_history['date'] == latest_date] if latest_date else pd.DataFrame()
                    
                    if not latest_data.empty:
                        st.subheader(f"Yield Curve as of {latest_date}")
                        
                        # Prepare curve data
                        yields = []
                        for col in available_cols:
                            value = latest_data[col].iloc[0]
                            yields.append(value if pd.notna(value) else None)
                        
                        # Create curve chart
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=available_tenors,
                            y=yields,
                            mode='lines+markers',
                            name='Yield Curve',
                            line=dict(color='#1f77b4', width=3),
                            marker=dict(size=12),
                            text=available_labels,
                            hovertemplate='<b>%{text} Tenor</b><br>Yield: %{y:.4f}%<extra></extra>'
                        ))
                        
                        fig.update_layout(
                            title=f"{curve_definition['title']} - {latest_date}",
                            xaxis_title="Tenor",
                            yaxis_title="Yield (%)",
                            xaxis=dict(
                                tickmode='array',
                                tickvals=available_tenors,
                                ticktext=available_labels
                            ),
                            height=400,
                            template='plotly_white',
                            hovermode='x unified'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Slope analysis
                        st.subheader("Curve Analysis")
                        col1, col2, col3 = st.columns(3)
                        
                        yield_by_col = dict(zip(available_cols, yields))
                        for metric_col, (start_col, end_col, label) in zip(
                            [col1, col2, col3],
                            curve_definition["slope_pairs"]
                        ):
                            if pd.notna(yield_by_col.get(start_col)) and pd.notna(yield_by_col.get(end_col)):
                                spread = yield_by_col[end_col] - yield_by_col[start_col]
                                slope_color = "🟢" if spread > 0 else "🔴"
                                with metric_col:
                                    st.metric(
                                        f"{slope_color} {label} Spread",
                                        f"{spread:.4f}%",
                                        help="Curve slope"
                                    )
                
                elif curve_view == "Curve Comparison":
                    # Compare two dates
                    st.subheader("Compare Yield Curves")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        date1 = st.date_input(
                            "Select First Date",
                            value=pd.to_datetime(curve_history['date'].iloc[-1]),
                            min_value=pd.to_datetime(curve_history['date'].min()),
                            max_value=pd.to_datetime(curve_history['date'].max())
                        )
                    with col2:
                        date2 = st.date_input(
                            "Select Second Date",
                            value=pd.to_datetime(curve_history['date'].iloc[-1]),
                            min_value=pd.to_datetime(curve_history['date'].min()),
                            max_value=pd.to_datetime(curve_history['date'].max())
                        )
                    
                    # Get data for both dates
                    data1, date1_str = resolve_curve_row(curve_history, date1)
                    data2, date2_str = resolve_curve_row(curve_history, date2)
                    
                    if not data1.empty and not data2.empty:
                        selected_date1_str = format_date_value(date1)
                        selected_date2_str = format_date_value(date2)
                        if date1_str != selected_date1_str or date2_str != selected_date2_str:
                            st.caption(
                                f"Using nearest available {selected_ccy} curve dates: {date1_str} and {date2_str}."
                            )

                        yields1 = [data1[col].iloc[0] if pd.notna(data1[col].iloc[0]) else None for col in available_cols]
                        yields2 = [data2[col].iloc[0] if pd.notna(data2[col].iloc[0]) else None for col in available_cols]
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=available_tenors, y=yields1,
                            mode='lines+markers',
                            name=f'Curve - {date1_str}',
                            line=dict(width=2),
                            marker=dict(size=10),
                            text=available_labels,
                            hovertemplate='<b>%{text} Tenor</b><br>Yield: %{y:.4f}%<extra></extra>'
                        ))
                        fig.add_trace(go.Scatter(
                            x=available_tenors, y=yields2,
                            mode='lines+markers',
                            name=f'Curve - {date2_str}',
                            line=dict(width=2),
                            marker=dict(size=10),
                            text=available_labels,
                            hovertemplate='<b>%{text} Tenor</b><br>Yield: %{y:.4f}%<extra></extra>'
                        ))
                        
                        fig.update_layout(
                            title="Yield Curve Comparison",
                            xaxis_title="Tenor",
                            yaxis_title="Yield (%)",
                            xaxis=dict(
                                tickmode='array',
                                tickvals=available_tenors,
                                ticktext=available_labels
                            ),
                            height=400,
                            template='plotly_white',
                            hovermode='x unified'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Show parallel shift
                        st.subheader("Parallel Shift Analysis")
                        shifts = [yields2[i] - yields1[i] if yields1[i] and yields2[i] else None for i in range(len(yields1))]
                        shift_data = pd.DataFrame({
                            "Tenor": available_labels,
                            "Shift (bps)": [s * 100 if s is not None else None for s in shifts]
                        })
                        st.dataframe(shift_data, use_container_width=True)
                    else:
                        st.warning("⚠️ Selected dates not available in historical data")
                
                elif curve_view == "Curve Evolution":
                    # Show how curve evolves over time with animation-like slider
                    st.subheader("Yield Curve Evolution Over Time")
                    
                    date_range = pd.to_datetime(curve_history['date'])
                    selected_date = st.slider(
                        "Select Date",
                        min_value=date_range.min(),
                        max_value=date_range.max(),
                        value=date_range.max(),
                        step=pd.Timedelta(days=1),
                        format="YYYY-MM-DD"
                    )
                    
                    selected_date_str = format_date_value(selected_date)
                    
                    # Get data for selected date
                    selected_data = historical[historical['date'] == selected_date_str]
                    
                    if not selected_data.empty:
                        yields = [selected_data[col].iloc[0] if pd.notna(selected_data[col].iloc[0]) else None for col in available_cols]
                        
                        # Create interactive curve
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=available_tenors, y=yields,
                            mode='lines+markers+text',
                            name='Yield Curve',
                            line=dict(color='#1f77b4', width=3),
                            marker=dict(size=14),
                            text=[f"{y:.3f}%" if y is not None else "N/A" for y in yields],
                            textposition="top center",
                            customdata=available_labels,
                            hovertemplate='<b>%{customdata} Tenor</b><br>Yield: %{y:.4f}%<extra></extra>'
                        ))
                        
                        fig.update_layout(
                            title=f"Yield Curve Evolution - {selected_date_str}",
                            xaxis_title="Tenor",
                            yaxis_title="Yield (%)",
                            xaxis=dict(
                                tickmode='array',
                                tickvals=available_tenors,
                                ticktext=available_labels
                            ),
                            height=400,
                            template='plotly_white'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Show recent history of curve shape (last 10 trading days)
                        st.subheader("Recent Curve Shape History (Last 10 Days)")
                        
                        recent_dates = historical[['date'] + available_cols].dropna(
                            subset=available_cols,
                            how='all'
                        ).tail(10).copy()
                        
                        if not recent_dates.empty:
                            fig = go.Figure()
                            
                            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                                     '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
                            
                            for idx, (_, row) in enumerate(recent_dates.iterrows()):
                                date_label = row['date']
                                yields_hist = [row[col] if pd.notna(row[col]) else None for col in available_cols]
                                
                                fig.add_trace(go.Scatter(
                                    x=available_tenors,
                                    y=yields_hist,
                                    mode='lines',
                                    name=date_label,
                                    line=dict(color=colors[idx % len(colors)], width=1),
                                    opacity=0.6,
                                    text=available_labels,
                                    hovertemplate=f'<b>{date_label}</b><br>%{{text}} Tenor: %{{y:.4f}}%<extra></extra>'
                                ))
                            
                            fig.update_layout(
                                title="Yield Curve Shape Evolution (Last 10 Days)",
                                xaxis_title="Tenor",
                                yaxis_title="Yield (%)",
                                xaxis=dict(
                                    tickmode='array',
                                    tickvals=available_tenors,
                                    ticktext=available_labels
                                ),
                                height=500,
                                template='plotly_white',
                                hovermode='x unified'
                            )
                            st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"⚠️ {selected_ccy} yield curve data not available in historical data")
        else:
            st.info("📊 Historical data not loaded. Click 'Fetch Historical Data' in sidebar to get started.")

    # ========== CREDIT TAB ==========
    with tabs[5]:
        st.subheader("💳 Credit Indices")

        credit = snapshot['data'].get('credit', {})
        if credit:
            # Display current values in columns
            cols = st.columns(len(credit))
            for col, (metric, value) in zip(cols, credit.items()):
                with col:
                    if value is not None:
                        st.metric(metric, f"{value:,.2f}")
                    else:
                        st.metric(metric, "N/A")

            # Toggle buttons for prices vs returns
            st.subheader("Analysis View")
            col1, col2 = st.columns(2)
            with col1:
                show_cr_prices = st.button("📊 Prices", key="cr_prices_btn")
            with col2:
                show_cr_returns = st.button("📈 10-Day Returns", key="cr_returns_btn")

            # Initialize session state for toggle
            if "show_cr_returns" not in st.session_state:
                st.session_state.show_cr_returns = False
            if show_cr_prices:
                st.session_state.show_cr_returns = False
            if show_cr_returns:
                st.session_state.show_cr_returns = True

            # Prices view
            if not st.session_state.show_cr_returns and show_historical and not historical.empty:
                st.subheader("Credit Indices - Price Trends")
                
                # Filter credit columns
                credit_cols = ["VIX", "Investment Grade", "High Yield", "EUR Bond Index"]
                credit_cols = [col for col in credit_cols if col in historical.columns]
                
                if credit_cols:
                    fig = go.Figure()
                    for col in credit_cols:
                        fig.add_trace(go.Scatter(
                            x=historical['date'],
                            y=historical[col],
                            mode='lines+markers',
                            name=col,
                            hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Value: %{y:.2f}<extra></extra>'
                        ))
                    
                    fig.update_layout(
                        title="Credit Indices Historical Trend",
                        xaxis_title="Date",
                        yaxis_title="Index Level",
                        hovermode='x unified',
                        height=500,
                        template='plotly_white'
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # Returns view
            elif st.session_state.show_cr_returns:
                st.subheader("Credit Indices - 10-Day Returns (%)")
                
                returns_calc = ReturnsCalculator()
                returns_df, organized_returns = returns_calc.load_and_calculate_returns()
                
                if not returns_df.empty and "credit" in organized_returns:
                    cr_returns = organized_returns["credit"]
                    
                    if not cr_returns.empty:
                        # Filter out date column and get metric columns
                        cr_metrics = [col for col in cr_returns.columns if col != 'date']
                        
                        # Plot returns
                        if cr_metrics:
                            fig = go.Figure()
                            for metric in cr_metrics:
                                fig.add_trace(go.Scatter(
                                    x=cr_returns['date'],
                                    y=cr_returns[metric],
                                    mode='lines+markers',
                                    name=metric,
                                    hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Return: %{y:.2f}%<extra></extra>'
                                ))
                            
                            fig.update_layout(
                                title="Credit Indices - 10-Day Overlapping Returns",
                                xaxis_title="Date",
                                yaxis_title="Return (%)",
                                hovermode='x unified',
                                height=500,
                                template='plotly_white'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Statistics table
                        st.subheader("Returns Statistics")
                        stats = returns_calc.get_summary_statistics(cr_returns)
                        
                        if stats:
                            stats_data = []
                            for metric, stat_dict in stats.items():
                                stats_data.append({
                                    "Metric": metric,
                                    "Latest (%)": stat_dict["latest"],
                                    "Mean (%)": stat_dict["mean"],
                                    "Std Dev (%)": stat_dict["std"],
                                    "Min (%)": stat_dict["min"],
                                    "Max (%)": stat_dict["max"]
                                })
                            
                            stats_df = pd.DataFrame(stats_data)
                            st.dataframe(
                                stats_df.style.format({
                                    "Latest (%)": "{:.2f}",
                                    "Mean (%)": "{:.2f}",
                                    "Std Dev (%)": "{:.2f}",
                                    "Min (%)": "{:.2f}",
                                    "Max (%)": "{:.2f}"
                                }),
                                use_container_width=True
                            )
                    else:
                        st.info("No credit returns data available")
                else:
                    st.info("Historical data not loaded. Click 'Fetch 3-4 Year History' in sidebar.")
        else:
            st.info("No credit data available")

    # ========== FOREX TAB ==========
    with tabs[5]:
        st.subheader("💱 Foreign Exchange Rates")

        forex = snapshot['data'].get('forex', {})
        if forex:
            cols = st.columns(len(forex))
            for col, (pair, value) in zip(cols, forex.items()):
                with col:
                    if value is not None:
                        st.metric(pair, f"{value:.6f}")
                    else:
                        st.metric(pair, "N/A")

            # Toggle buttons for prices vs returns
            st.subheader("Analysis View")
            col1, col2 = st.columns(2)
            with col1:
                show_fx_prices = st.button("📊 Prices", key="fx_prices_btn")
            with col2:
                show_fx_returns = st.button("📈 10-Day Returns", key="fx_returns_btn")

            # Initialize session state for toggle
            if "show_fx_returns" not in st.session_state:
                st.session_state.show_fx_returns = False
            if show_fx_prices:
                st.session_state.show_fx_returns = False
            if show_fx_returns:
                st.session_state.show_fx_returns = True

            # Prices view
            if not st.session_state.show_fx_returns and show_historical and not historical.empty:
                st.subheader("FX Rates - Price Trends")
                
                fx_cols = ["EUR/USD", "EUR/GBP", "USD/JPY", "GBP/USD"]
                fx_cols = [col for col in fx_cols if col in historical.columns]

                if fx_cols:
                    fig = go.Figure()
                    for col in fx_cols:
                        fig.add_trace(go.Scatter(
                            x=historical['date'],
                            y=historical[col],
                            mode='lines+markers',
                            name=col,
                            hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Value: %{y:.6f}<extra></extra>'
                        ))

                    fig.update_layout(
                        title="FX Rates Historical Trend",
                        xaxis_title="Date",
                        yaxis_title="Exchange Rate",
                        hovermode='x unified',
                        height=500,
                        template='plotly_white'
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # Returns view
            elif st.session_state.show_fx_returns:
                st.subheader("FX Rates - 10-Day Returns (%)")
                
                returns_calc = ReturnsCalculator()
                returns_df, organized_returns = returns_calc.load_and_calculate_returns()
                
                if not returns_df.empty and "forex" in organized_returns:
                    fx_returns = organized_returns["forex"]
                    
                    if not fx_returns.empty:
                        # Filter out date column and get metric columns
                        fx_metrics = [col for col in fx_returns.columns if col != 'date']
                        
                        # Plot returns
                        if fx_metrics:
                            fig = go.Figure()
                            for metric in fx_metrics:
                                fig.add_trace(go.Scatter(
                                    x=fx_returns['date'],
                                    y=fx_returns[metric],
                                    mode='lines+markers',
                                    name=metric,
                                    hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Return: %{y:.2f}%<extra></extra>'
                                ))
                            
                            fig.update_layout(
                                title="FX Rates - 10-Day Overlapping Returns",
                                xaxis_title="Date",
                                yaxis_title="Return (%)",
                                hovermode='x unified',
                                height=500,
                                template='plotly_white'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Statistics table
                        st.subheader("Returns Statistics")
                        stats = returns_calc.get_summary_statistics(fx_returns)
                        
                        if stats:
                            stats_data = []
                            for metric, stat_dict in stats.items():
                                stats_data.append({
                                    "Metric": metric,
                                    "Latest (%)": stat_dict["latest"],
                                    "Mean (%)": stat_dict["mean"],
                                    "Std Dev (%)": stat_dict["std"],
                                    "Min (%)": stat_dict["min"],
                                    "Max (%)": stat_dict["max"]
                                })
                            
                            stats_df = pd.DataFrame(stats_data)
                            st.dataframe(
                                stats_df.style.format({
                                    "Latest (%)": "{:.2f}",
                                    "Mean (%)": "{:.2f}",
                                    "Std Dev (%)": "{:.2f}",
                                    "Min (%)": "{:.2f}",
                                    "Max (%)": "{:.2f}"
                                }),
                                use_container_width=True
                            )
                    else:
                        st.info("No FX returns data available")
                else:
                    st.info("Historical data not loaded. Click 'Fetch 3-4 Year History' in sidebar.")
        else:
            st.info("No FX data available")

    # ========== COMMODITIES TAB ==========
    with tabs[6]:
        st.subheader("⚫ Commodities Prices")

        commodities = snapshot['data'].get('commodities', {})
        if commodities:
            cols = st.columns(len(commodities))
            for col, (commodity, value) in zip(cols, commodities.items()):
                with col:
                    if value is not None:
                        st.metric(commodity, f"${value:,.2f}")
                    else:
                        st.metric(commodity, "N/A")

            # Toggle buttons for prices vs returns
            st.subheader("Analysis View")
            col1, col2 = st.columns(2)
            with col1:
                show_cm_prices = st.button("📊 Prices", key="cm_prices_btn")
            with col2:
                show_cm_returns = st.button("📈 10-Day Returns", key="cm_returns_btn")

            # Initialize session state for toggle
            if "show_cm_returns" not in st.session_state:
                st.session_state.show_cm_returns = False
            if show_cm_prices:
                st.session_state.show_cm_returns = False
            if show_cm_returns:
                st.session_state.show_cm_returns = True

            # Prices view
            if not st.session_state.show_cm_returns and show_historical and not historical.empty:
                st.subheader("Commodities - Price Trends")
                
                commodity_cols = ["Brent Crude", "Gold", "Natural Gas", "Silver"]
                commodity_cols = [col for col in commodity_cols if col in historical.columns]

                if commodity_cols:
                    fig = go.Figure()
                    for col in commodity_cols:
                        fig.add_trace(go.Scatter(
                            x=historical['date'],
                            y=historical[col],
                            mode='lines+markers',
                            name=col,
                            hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>'
                        ))

                    fig.update_layout(
                        title="Commodities Price Trend",
                        xaxis_title="Date",
                        yaxis_title="Price (USD)",
                        hovermode='x unified',
                        height=500,
                        template='plotly_white'
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # Returns view
            elif st.session_state.show_cm_returns:
                st.subheader("Commodities - 10-Day Returns (%)")
                
                returns_calc = ReturnsCalculator()
                returns_df, organized_returns = returns_calc.load_and_calculate_returns()
                
                if not returns_df.empty and "commodities" in organized_returns:
                    cm_returns = organized_returns["commodities"]
                    
                    if not cm_returns.empty:
                        # Filter out date column and get metric columns
                        cm_metrics = [col for col in cm_returns.columns if col != 'date']
                        
                        # Plot returns
                        if cm_metrics:
                            fig = go.Figure()
                            for metric in cm_metrics:
                                fig.add_trace(go.Scatter(
                                    x=cm_returns['date'],
                                    y=cm_returns[metric],
                                    mode='lines+markers',
                                    name=metric,
                                    hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Return: %{y:.2f}%<extra></extra>'
                                ))
                            
                            fig.update_layout(
                                title="Commodities - 10-Day Overlapping Returns",
                                xaxis_title="Date",
                                yaxis_title="Return (%)",
                                hovermode='x unified',
                                height=500,
                                template='plotly_white'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Statistics table
                        st.subheader("Returns Statistics")
                        stats = returns_calc.get_summary_statistics(cm_returns)
                        
                        if stats:
                            stats_data = []
                            for metric, stat_dict in stats.items():
                                stats_data.append({
                                    "Metric": metric,
                                    "Latest (%)": stat_dict["latest"],
                                    "Mean (%)": stat_dict["mean"],
                                    "Std Dev (%)": stat_dict["std"],
                                    "Min (%)": stat_dict["min"],
                                    "Max (%)": stat_dict["max"]
                                })
                            
                            stats_df = pd.DataFrame(stats_data)
                            st.dataframe(
                                stats_df.style.format({
                                    "Latest (%)": "{:.2f}",
                                    "Mean (%)": "{:.2f}",
                                    "Std Dev (%)": "{:.2f}",
                                    "Min (%)": "{:.2f}",
                                    "Max (%)": "{:.2f}"
                                }),
                                use_container_width=True
                            )
                    else:
                        st.info("No commodities returns data available")
                else:
                    st.info("Historical data not loaded. Click 'Fetch 3-4 Year History' in sidebar.")
        else:
            st.info("No commodity data available")

    # ========== CRYPTOCURRENCIES TAB ==========
    with tabs[7]:
        st.subheader("₿ Cryptocurrencies")

        cryptocurrencies = snapshot['data'].get('crypto', {})
        if cryptocurrencies:
            # Display current values
            cols = st.columns(len(cryptocurrencies))
            for col, (metric, value) in zip(cols, cryptocurrencies.items()):
                with col:
                    if value is not None:
                        st.metric(metric, f"${value:,.2f}")
                    else:
                        st.metric(metric, "N/A")

            # Toggle buttons for prices vs returns
            st.subheader("Analysis View")
            col1, col2 = st.columns(2)
            with col1:
                show_cr_prices = st.button("📊 Prices", key="crypto_prices_btn")
            with col2:
                show_cr_returns = st.button("📈 10-Day Returns", key="crypto_returns_btn")

            # Initialize session state for toggle
            if "show_crypto_returns" not in st.session_state:
                st.session_state.show_crypto_returns = False
            if show_cr_prices:
                st.session_state.show_crypto_returns = False
            if show_cr_returns:
                st.session_state.show_crypto_returns = True

            # Prices view
            if not st.session_state.show_crypto_returns and show_historical and not historical.empty:
                st.subheader("Cryptocurrencies - Price Trends")
                
                crypto_cols = ["Bitcoin", "Ethereum", "Binance Coin", "Solana"]
                crypto_cols = [col for col in crypto_cols if col in historical.columns]

                if crypto_cols:
                    fig = go.Figure()
                    for col in crypto_cols:
                        fig.add_trace(go.Scatter(
                            x=historical['date'],
                            y=historical[col],
                            mode='lines+markers',
                            name=col,
                            hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Value: $%{y:.2f}<extra></extra>'
                        ))

                    fig.update_layout(
                        title="Cryptocurrencies Historical Trend",
                        xaxis_title="Date",
                        yaxis_title="Price (USD)",
                        hovermode='x unified',
                        height=500,
                        template='plotly_white'
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # Returns view
            elif st.session_state.show_crypto_returns:
                st.subheader("Cryptocurrencies - 10-Day Returns (%)")
                
                returns_calc = ReturnsCalculator()
                returns_df, organized_returns = returns_calc.load_and_calculate_returns()
                
                if not returns_df.empty and "crypto" in organized_returns:
                    crypto_returns = organized_returns["crypto"]
                    
                    if not crypto_returns.empty:
                        # Filter out date column and get metric columns
                        crypto_metrics = [col for col in crypto_returns.columns if col != 'date']
                        
                        # Plot returns
                        if crypto_metrics:
                            fig = go.Figure()
                            for metric in crypto_metrics:
                                fig.add_trace(go.Scatter(
                                    x=crypto_returns['date'],
                                    y=crypto_returns[metric],
                                    mode='lines+markers',
                                    name=metric,
                                    hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Return: %{y:.2f}%<extra></extra>'
                                ))
                            
                            fig.update_layout(
                                title="Cryptocurrencies - 10-Day Overlapping Returns",
                                xaxis_title="Date",
                                yaxis_title="Return (%)",
                                hovermode='x unified',
                                height=500,
                                template='plotly_white'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Statistics table
                        st.subheader("Returns Statistics")
                        stats = returns_calc.get_summary_statistics(crypto_returns)
                        
                        if stats:
                            stats_data = []
                            for metric, stat_dict in stats.items():
                                stats_data.append({
                                    "Metric": metric,
                                    "Latest (%)": stat_dict["latest"],
                                    "Mean (%)": stat_dict["mean"],
                                    "Std Dev (%)": stat_dict["std"],
                                    "Min (%)": stat_dict["min"],
                                    "Max (%)": stat_dict["max"]
                                })
                            
                            stats_df = pd.DataFrame(stats_data)
                            st.dataframe(
                                stats_df.style.format({
                                    "Latest (%)": "{:.2f}",
                                    "Mean (%)": "{:.2f}",
                                    "Std Dev (%)": "{:.2f}",
                                    "Min (%)": "{:.2f}",
                                    "Max (%)": "{:.2f}"
                                }),
                                use_container_width=True
                            )
                    else:
                        st.info("No crypto returns data available")
                else:
                    st.info("Historical data not loaded. Click 'Fetch 3-4 Year History' in sidebar.")
        else:
            st.info("No cryptocurrency data available")

    st.divider()

    # Footer
    st.markdown("""
    ---
    **Dashboard Information:**
    - Updates daily with latest market data
    - Data sourced from Yahoo Finance and public market feeds
    - Charts display historical trends for analysis
    - All times in UTC
    """)


if __name__ == "__main__":
    main()

