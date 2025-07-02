import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration settings"""
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
    
    # Database settings for account management
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'accounts.db')
    
    # Legacy EasyPost settings (for backward compatibility)
    EASYPOST_API_KEY = os.getenv('EASYPOST_API_KEY')
    
    # PrintNode settings
    PRINTNODE_API_KEY = os.getenv('PRINTNODE_API_KEY')
    PRINTNODE_PRINTER_ID = os.getenv('PRINTNODE_PRINTER_ID')
    
    # Management API settings
    MANAGEMENT_API_KEY = os.getenv('MANAGEMENT_API_KEY', 'change-this-secure-key')
    RASPBERRY_PI_URL = os.getenv('RASPBERRY_PI_URL', 'http://raspberrypi.local:5000')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')