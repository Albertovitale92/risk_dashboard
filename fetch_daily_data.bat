@echo off
REM Daily Risk Factors Dashboard - Data Fetch Script
REM This script fetches the latest risk factors data and can be scheduled via Windows Task Scheduler

cd /d "%~dp0"

REM Activate virtual environment
call .\.venv\Scripts\activate.bat

REM Run the fetch command
python run.py fetch

REM Pause to see results
pause

