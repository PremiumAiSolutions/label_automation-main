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
    
    # EasyPost settings
    EASYPOST_API_KEY = os.getenv('EASYPOST_API_KEY')
    
    # PrintNode settings
    PRINTNODE_API_KEY = os.getenv('PRINTNODE_API_KEY')
    PRINTNODE_PRINTER_ID = os.getenv('PRINTNODE_PRINTER_ID')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')