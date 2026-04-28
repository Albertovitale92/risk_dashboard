@echo off
REM First-time setup script for Portfolio Risk Dashboard
REM This fetches 3 years of historical data and today's snapshot

echo.
echo ============================================================
echo Portfolio Risk Dashboard - First Time Setup
echo ============================================================
echo.

cd /d C:\Users\alber\PycharmProjects\portfolio_risk_dashboard

echo Step 1: Fetching 10 years of historical data (this may take 10-15 minutes)...
echo.
.\.venv\Scripts\python.exe run.py fetch-history --years 10

echo.
echo Step 2: Fetching today's data...
echo.
.\.venv\Scripts\python.exe run.py fetch

echo.
echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo Your data is ready. Launching dashboard in 3 seconds...
echo.

timeout /t 3

echo Launching dashboard...
streamlit run dashboard.py

pause

