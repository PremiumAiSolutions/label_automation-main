#!/usr/bin/env python3
"""
Setup script for Label Automation System
"""

import os
import sys
from dotenv import load_dotenv

def check_environment():
    """Check if all required environment variables are set"""
    load_dotenv()
    
    required_vars = [
        'EASYPOST_API_KEY',
        'PRINTNODE_API_KEY'
    ]
    
    optional_vars = [
        'PRINTNODE_PRINTER_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease update your .env file with the missing values.")
        return False
    
    print("✅ All required environment variables are set!")
    
    # Check optional variables
    missing_optional = []
    for var in optional_vars:
        if not os.getenv(var) or os.getenv(var) == 'your-printer-id':
            missing_optional.append(var)
    
    if missing_optional:
        print("⚠️  Optional environment variables not set:")
        for var in missing_optional:
            print(f"   - {var} (will be needed when printer arrives)")
    
    return True

def test_easypost_connection():
    """Test EasyPost API connection"""
    try:
        from app.easypost.client import get_easypost_client
        
        print("🔄 Testing EasyPost connection...")
        client = get_easypost_client()
        
        # Try to get user info to test the connection
        user = client.user.retrieve_me()
        print(f"✅ EasyPost connected successfully! User: {user.email}")
        return True
        
    except Exception as e:
        print(f"❌ EasyPost connection failed: {str(e)}")
        return False

def test_printnode_connection():
    """Test PrintNode API connection and list printers"""
    try:
        from app.printnode.printer import get_printnode_client, get_printer_info
        
        print("🔄 Testing PrintNode connection...")
        client = get_printnode_client()
        
        # Test connection by getting printers (which validates the API key)
        try:
            printers = client.printers()
            print(f"✅ PrintNode connected successfully! Found {len(printers)} printers on account.")
        except Exception as e:
            print(f"❌ PrintNode API test failed: {str(e)}")
            return False
        
        # List printers
        print("\n📋 Available printers:")
        printer_info = get_printer_info()
        
        if isinstance(printer_info, list):
            if len(printer_info) == 0:
                print("   No printers found")
            else:
                for printer in printer_info:
                    # Handle both dict and tuple formats from PrintNode API
                    if isinstance(printer, dict):
                        status = "🟢" if printer['state'] == 'online' else "🔴"
                        print(f"   {status} ID: {printer['id']} | Name: {printer['name']} | State: {printer['state']}")
                    else:
                        # If it's a tuple or list, access by index
                        state = printer[2] if len(printer) > 2 else 'unknown'
                        status = "🟢" if state == 'online' else "🔴"
                        name = printer[1] if len(printer) > 1 else 'Unknown'
                        printer_id = printer[0] if len(printer) > 0 else 'Unknown'
                        print(f"   {status} ID: {printer_id} | Name: {name} | State: {state}")
        else:
            # Single printer configured
            if printer_info:
                if isinstance(printer_info, dict):
                    status = "🟢" if printer_info['state'] == 'online' else "🔴"
                    print(f"   {status} Configured printer: {printer_info['name']} (State: {printer_info['state']})")
                else:
                    state = printer_info[2] if len(printer_info) > 2 else 'unknown'
                    status = "🟢" if state == 'online' else "🔴"
                    name = printer_info[1] if len(printer_info) > 1 else 'Unknown'
                    print(f"   {status} Configured printer: {name} (State: {state})")
        
        return True
        
    except Exception as e:
        print(f"❌ PrintNode connection failed: {str(e)}")
        return False

def run_health_check():
    """Run a complete health check of the system"""
    print("🏥 Running Label Automation System Health Check\n")
    
    checks = [
        ("Environment Variables", check_environment),
        ("EasyPost Connection", test_easypost_connection),
        ("PrintNode Connection", test_printnode_connection)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n--- {check_name} ---")
        if not check_func():
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 All checks passed! Your system is ready to go!")
        print("\nTo start the application:")
        print("   python -m app.main")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        sys.exit(1)

def show_usage():
    """Show usage information"""
    print("""
Label Automation System Setup

Usage:
    python setup.py [command]

Commands:
    health      Run health check on all system components
    easypost    Test EasyPost API connection only
    printnode   Test PrintNode API connection only
    env         Check environment variables only
    help        Show this help message

Examples:
    python setup.py health     # Run full health check
    python setup.py printnode  # Test just PrintNode connection
""")

def main():
    """Main setup function"""
    if len(sys.argv) < 2:
        show_usage()
        return
    
    command = sys.argv[1].lower()
    
    if command == "health":
        run_health_check()
    elif command == "easypost":
        check_environment()
        test_easypost_connection()
    elif command == "printnode":
        check_environment()
        test_printnode_connection()
    elif command == "env":
        check_environment()
    elif command == "help":
        show_usage()
    else:
        print(f"Unknown command: {command}")
        show_usage()

if __name__ == "__main__":
    main() 