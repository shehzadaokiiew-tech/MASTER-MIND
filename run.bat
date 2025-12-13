@echo off
echo Starting Facebook Automation Tool...
echo.
echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH!
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo Starting the application...
echo The tool will open in your default browser...
echo.
streamlit run facebook_automation.py --server.port 8501 --server.headless false

pause