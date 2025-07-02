@echo off
echo Starting Label Automation Management Interface...
echo.

cd /d "%~dp0frontend"

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing/updating requirements...
pip install -r requirements.txt

echo.
echo ===================================================
echo  Label Automation Management Interface
echo ===================================================
echo.
echo  Frontend URL: http://localhost:8080
echo  Raspberry Pi URL: %RASPBERRY_PI_URL%
echo.
echo  Press Ctrl+C to stop the server
echo ===================================================
echo.

python app.py

pause 