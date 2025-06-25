@echo off
cd /d "D:\repos\label_automation-main\label_automation-main"
echo Starting Label Automation Server...
echo Server will be available at: http://localhost:5000/health
echo Press Ctrl+C to stop the server
python -m app.main
pause 