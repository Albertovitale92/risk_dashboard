@echo off
REM Daily Risk Factors Dashboard - Streamlit Web UI
REM This script launches the interactive web dashboard

cd /d "%~dp0"

REM Activate virtual environment
call .\.venv\Scripts\activate.bat

REM Launch Streamlit app
echo Launching Risk Dashboard...
echo Open your browser at http://localhost:8501
echo Press Ctrl+C to stop the dashboard
timeout /t 2

streamlit run dashboard.py

pause

