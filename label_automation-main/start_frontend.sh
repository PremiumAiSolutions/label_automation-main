#!/bin/bash
echo "Starting Label Automation Management Interface..."
echo

cd "$(dirname "$0")/frontend"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing/updating requirements..."
pip install -r requirements.txt

echo
echo "==================================================="
echo " Label Automation Management Interface"
echo "==================================================="
echo
echo " Frontend URL: http://localhost:8080"
echo " Raspberry Pi URL: ${RASPBERRY_PI_URL}"
echo
echo " Press Ctrl+C to stop the server"
echo "==================================================="
echo

python app.py 