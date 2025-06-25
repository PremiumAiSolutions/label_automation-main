#!/usr/bin/env python3
"""
Test script for Label Automation System webhook functionality
"""

import json
import requests
import sys
from datetime import datetime

def create_test_webhook_payload():
    """Create a test webhook payload similar to what EasyPost sends"""
    return {
        "id": "evt_test_12345",
        "object": "Event",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "description": "tracker.created",
        "mode": "test",
        "previous_attributes": {},
        "pending_urls": [],
        "completed_urls": [],
        "result": {
            "id": "trk_test_12345",
            "object": "Tracker",
            "mode": "test",
            "tracking_code": "TEST_TRACKING_CODE_123",
            "status": "in_transit",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "carrier": "USPS",
            "tracking_details": []
        }
    }

def send_test_webhook(base_url="http://localhost:5000", endpoint="/webhook/easypost"):
    """Send a test webhook to the local server"""
    url = f"{base_url}{endpoint}"
    payload = create_test_webhook_payload()
    
    print(f"🚀 Sending test webhook to: {url}")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'EasyPost/Webhook-Test'
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"\n📡 Response Status: {response.status_code}")
        print(f"📡 Response Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"📡 Response Body: {json.dumps(response_json, indent=2)}")
        except:
            print(f"📡 Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Test webhook sent successfully!")
        else:
            print(f"❌ Webhook failed with status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the server running?")
        print("   Start the server with: python -m app.main")
    except Exception as e:
        print(f"❌ Error sending webhook: {str(e)}")

def test_health_endpoint(base_url="http://localhost:5000"):
    """Test the health endpoint"""
    url = f"{base_url}/health"
    
    print(f"🏥 Testing health endpoint: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Health endpoint is working!")
            print(f"📡 Response: {response.json()}")
        else:
            print(f"❌ Health endpoint failed with status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the server running?")
        return False
    except Exception as e:
        print(f"❌ Error testing health endpoint: {str(e)}")
        return False
    
    return True

def main():
    """Main test function"""
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help", "help"]:
        print("""
Label Automation Webhook Test Script

Usage:
    python test_webhook.py [base_url]

Arguments:
    base_url    Base URL of the server (default: http://localhost:5000)

Examples:
    python test_webhook.py                          # Test local server
    python test_webhook.py http://localhost:8080    # Test custom port
    python test_webhook.py https://your-domain.com  # Test production server

This script will:
1. Test the health endpoint
2. Send a test webhook payload to /webhook/easypost
""")
        return
    
    # Get base URL from command line or use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    base_url = base_url.rstrip('/')  # Remove trailing slash
    
    print("🧪 Label Automation System - Webhook Test")
    print(f"🎯 Target Server: {base_url}")
    print("=" * 50)
    
    # Test health endpoint first
    if not test_health_endpoint(base_url):
        print("\n❌ Server is not responding. Please start the server and try again.")
        return
    
    print("\n" + "=" * 50)
    
    # Send test webhook
    send_test_webhook(base_url)
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")
    print("\nNote: This sends a test payload. For real testing, you need:")
    print("1. Valid EasyPost API keys")
    print("2. A real tracker ID that exists in your EasyPost account")
    print("3. Associated shipment with a label")

if __name__ == "__main__":
    main() 