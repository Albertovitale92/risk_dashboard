@echo off
REM First-time setup script for Portfolio Risk Dashboard
REM The Risk_Factors project owns data fetching and historical storage.

echo.
echo ============================================================
echo Portfolio Risk Dashboard - First Time Setup
echo ============================================================
echo.

cd /d C:\Users\alber\PycharmProjects\portfolio_risk_dashboard

echo Step 1: Ensure Risk_Factors is installed and configured.
echo.
echo Set RISK_FACTORS_PROJECT if it is not at:
echo C:\Users\alber\PycharmProjects\Risk_Factors

echo.
echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo Launching the dashboard. Use "Refresh Risk_Factors Store" in the sidebar to load data.
echo.

timeout /t 3

echo Launching dashboard...
streamlit run dashboard.py

pause
