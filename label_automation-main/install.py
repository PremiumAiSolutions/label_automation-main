#!/usr/bin/env python3
"""
Installation script for Label Automation System
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a Python package using pip"""
    try:
        print(f"📦 Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def install_from_requirements():
    """Install packages from requirements.txt"""
    if os.path.exists("requirements.txt"):
        try:
            print("📦 Installing from requirements.txt...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ All requirements installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install from requirements.txt: {e}")
            return False
    else:
        print("❌ requirements.txt not found")
        return False

def install_core_packages():
    """Install core packages manually"""
    packages = [
        "flask",
        "easypost",
        "python-dotenv",
        "requests",
        "colorama",
    ]
    
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    return success_count == len(packages)

def main():
    """Main installation function"""
    print("🚀 Label Automation System - Installation Script")
    print("=" * 50)
    
    # Try installing from requirements.txt first
    if install_from_requirements():
        print("\n✅ Installation completed successfully!")
    else:
        print("\n⚠️  Installing core packages individually...")
        if install_core_packages():
            print("\n✅ Core packages installed successfully!")
        else:
            print("\n❌ Some packages failed to install")
            return False
    
    print("\n" + "=" * 50)
    print("🎉 Installation complete!")
    print("\nNext steps:")
    print("1. Update .env with your API keys")
    print("2. Run: python setup.py health")
    print("3. Start the app: python -m app.main")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 