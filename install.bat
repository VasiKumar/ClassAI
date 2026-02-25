@echo off
REM Installation script for Windows
echo ============================================================
echo Student Focus Monitor - Windows Installation
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo Step 1: Installing dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Step 2: Running setup verification...
python setup_test.py

echo.
echo ============================================================
echo Installation complete!
echo ============================================================
echo.
echo Next steps:
echo 1. Prepare your name.zip file with student photos
echo 2. Run: python student_monitor.py
echo.
echo For help, see README.md or QUICKSTART.md
echo ============================================================
pause
