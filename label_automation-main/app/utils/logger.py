import logging
import os
import json
from datetime import datetime

def setup_logger():
    """Setup application logging"""
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log')
        ]
    )

def save_request_to_file(request_data, account_id=None):
    """
    Save webhook request to file for debugging
    
    Args:
        request_data (dict): The request payload
        account_id (str): Optional account ID for organization
    """
    try:
        # Create logs directory if it doesn't exist
        logs_dir = "webhook_logs"
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        
        # Create filename with timestamp and account info
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        account_suffix = f"_{account_id}" if account_id else "_legacy"
        event_type = request_data.get('description', 'unknown').replace('.', '_')
        filename = f"{timestamp}{account_suffix}_{event_type}.json"
        filepath = os.path.join(logs_dir, filename)
        
        # Add metadata to the request data
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "account_id": account_id,
            "event_type": request_data.get('description'),
            "payload": request_data
        }
        
        # Write to file
        with open(filepath, 'w') as f:
            json.dump(log_data, f, indent=2, default=str)
        
        logging.info(f"Webhook request saved to: {filepath}")
        
    except Exception as e:
        logging.error(f"Failed to save request to file: {str(e)}")