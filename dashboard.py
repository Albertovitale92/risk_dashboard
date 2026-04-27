"""Streamlit dashboard for daily risk factors."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

from src.data_fetching.risk_aggregator import RiskDashboardAggregator
from src.utils.logger import get_logger

logger = get_logger(__name__)

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

        # Settings
        st.subheader("Display Settings")
        show_historical = st.checkbox("Show Historical Charts", value=True)
        historical_days = st.slider("Historical Days", 5, 90, 30)


    # Main content
    # Get latest snapshot
    snapshot = aggregator.get_latest_snapshot()
    historical = aggregator.get_historical_data(days=historical_days)

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
        "📈 Equities",
        "📊 Interest Rates",
        "💳 Credit",
        "💱 Forex",
        "⚫ Commodities"
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

    # ========== EQUITIES TAB ==========
    with tabs[1]:
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

            # Historical chart
            if show_historical and not historical.empty:
                st.subheader("Equity Indices - Historical Trend")

                equity_cols = [col for col in historical.columns if col not in ['date', 'timestamp']]
                equity_cols = [col for col in equity_cols if any(idx in col for idx in ['S&P', 'EuroStoxx', 'FTSE'])]

                if equity_cols:
                    fig = go.Figure()
                    for col in equity_cols:
                        fig.add_trace(go.Scatter(
                            x=historical['date'],
                            y=historical[col],
                            mode='lines+markers',
                            name=col
                        ))

                    fig.update_layout(
                        title="Equity Indices Trend",
                        xaxis_title="Date",
                        yaxis_title="Value",
                        hovermode='x unified',
                        height=500
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No equity data available")

    # ========== INTEREST RATES TAB ==========
    with tabs[2]:
        st.subheader("📊 Interest Rates & Fixed Income")

        rates = snapshot['data'].get('interest_rates', {})
        if rates:
            cols = st.columns(len(rates))
            for col, (metric, value) in zip(cols, rates.items()):
                with col:
                    if value is not None:
                        st.metric(metric, f"{value:.4f}")
                    else:
                        st.metric(metric, "N/A")

            # Historical chart
            if show_historical and not historical.empty:
                st.subheader("Interest Rates - Historical Trend")

                rate_cols = [col for col in historical.columns if any(x in col for x in ['Bund', 'EUR', 'USD', 'Euribor', 'OIS'])]

                if rate_cols:
                    fig = go.Figure()
                    for col in rate_cols:
                        fig.add_trace(go.Scatter(
                            x=historical['date'],
                            y=historical[col],
                            mode='lines+markers',
                            name=col
                        ))

                    fig.update_layout(
                        title="Interest Rates Trend",
                        xaxis_title="Date",
                        yaxis_title="Rate",
                        hovermode='x unified',
                        height=500
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No interest rate data available")

    # ========== CREDIT TAB ==========
    with tabs[3]:
        st.subheader("💳 Credit Indices")

        credit = snapshot['data'].get('credit', {})
        if credit:
            cols = st.columns(len(credit))
            for col, (metric, value) in zip(cols, credit.items()):
                with col:
                    if value is not None:
                        st.metric(metric, f"{value:,.2f}")
                    else:
                        st.metric(metric, "N/A")

            # Historical chart
            if show_historical and not historical.empty:
                st.subheader("Credit Indices - Historical Trend")

                credit_cols = [col for col in historical.columns if any(x in col for x in ['iTraxx', 'VIX', 'HY', 'Credit'])]

                if credit_cols:
                    fig = go.Figure()
                    for col in credit_cols:
                        fig.add_trace(go.Scatter(
                            x=historical['date'],
                            y=historical[col],
                            mode='lines+markers',
                            name=col
                        ))

                    fig.update_layout(
                        title="Credit Indices Trend",
                        xaxis_title="Date",
                        yaxis_title="Index Level",
                        hovermode='x unified',
                        height=500
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No credit data available")

    # ========== FOREX TAB ==========
    with tabs[4]:
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

            # Historical chart
            if show_historical and not historical.empty:
                st.subheader("FX Rates - Historical Trend")

                fx_cols = [col for col in historical.columns if '/' in col or any(x in col for x in ['EUR', 'GBP', 'USD', 'JPY'])]

                if fx_cols:
                    fig = go.Figure()
                    for col in fx_cols:
                        fig.add_trace(go.Scatter(
                            x=historical['date'],
                            y=historical[col],
                            mode='lines+markers',
                            name=col
                        ))

                    fig.update_layout(
                        title="FX Rates Trend",
                        xaxis_title="Date",
                        yaxis_title="Exchange Rate",
                        hovermode='x unified',
                        height=500
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No FX data available")

    # ========== COMMODITIES TAB ==========
    with tabs[5]:
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

            # Historical chart
            if show_historical and not historical.empty:
                st.subheader("Commodities - Historical Trend")

                commodity_cols = [col for col in historical.columns if any(x in col for x in ['Brent', 'Gold', 'Natural Gas', 'Silver', 'Crude'])]

                if commodity_cols:
                    fig = go.Figure()
                    for col in commodity_cols:
                        fig.add_trace(go.Scatter(
                            x=historical['date'],
                            y=historical[col],
                            mode='lines+markers',
                            name=col
                        ))

                    fig.update_layout(
                        title="Commodities Price Trend",
                        xaxis_title="Date",
                        yaxis_title="Price (USD)",
                        hovermode='x unified',
                        height=500
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No commodity data available")

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

