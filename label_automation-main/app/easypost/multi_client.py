import logging
import os
from typing import Optional, Dict
from easypost import EasyPostClient
from app.database.models import AccountDatabase, EasyPostAccount

logger = logging.getLogger(__name__)

class MultiEasyPostManager:
    """Manager for multiple EasyPost accounts"""
    
    def __init__(self, db_path: str = None):
        self.db = AccountDatabase(db_path or os.getenv('DATABASE_PATH', 'accounts.db'))
        self._clients: Dict[str, EasyPostClient] = {}
    
    def get_client(self, account_id: str) -> Optional[EasyPostClient]:
        """Get EasyPost client for a specific account"""
        if account_id in self._clients:
            return self._clients[account_id]
        
        account = self.db.get_easypost_account(account_id)
        if not account or not account.is_active:
            logger.error(f"Account {account_id} not found or inactive")
            return None
        
        try:
            client = EasyPostClient(account.api_key)
            self._clients[account_id] = client
            logger.info(f"Created client for account: {account.name}")
            return client
        except Exception as e:
            logger.error(f"Failed to create client for account {account_id}: {e}")
            return None
    
    def get_legacy_client(self) -> Optional[EasyPostClient]:
        """Get client using legacy environment variable (backward compatibility)"""
        api_key = os.getenv('EASYPOST_API_KEY')
        if not api_key:
            return None
        
        if 'legacy' not in self._clients:
            try:
                self._clients['legacy'] = EasyPostClient(api_key)
                logger.info("Created legacy EasyPost client")
            except Exception as e:
                logger.error(f"Failed to create legacy client: {e}")
                return None
        
        return self._clients['legacy']
    
    def get_account_for_client(self, account_id: str) -> Optional[EasyPostAccount]:
        """Get account configuration"""
        return self.db.get_easypost_account(account_id)
    
    def list_accounts(self):
        """List all active accounts"""
        return self.db.get_all_easypost_accounts()
    
    def refresh_client(self, account_id: str):
        """Refresh client cache for an account"""
        if account_id in self._clients:
            del self._clients[account_id]

# Global instance
multi_client_manager = MultiEasyPostManager()

def get_easypost_client_for_account(account_id: str) -> Optional[EasyPostClient]:
    """Get EasyPost client for a specific account"""
    return multi_client_manager.get_client(account_id)

def get_easypost_client():
    """Get legacy EasyPost client (backward compatibility)"""
    # Try legacy client first
    client = multi_client_manager.get_legacy_client()
    if client:
        return client
    
    # Fall back to first active account
    accounts = multi_client_manager.list_accounts()
    if accounts:
        return multi_client_manager.get_client(accounts[0].id)
    
    raise ValueError("No EasyPost configuration found")

def get_label_from_shipment(shipment_id: str, account_id: str = None):
    """
    Retrieve shipping label from a shipment
    
    Args:
        shipment_id (str): EasyPost shipment ID
        account_id (str): Optional account ID, uses legacy if not provided
        
    Returns:
        dict: Label data with URL and metadata, or None if not found
    """
    try:
        logger.info(f"Getting label for shipment: {shipment_id} (account: {account_id or 'legacy'})")
        
        if account_id:
            client = get_easypost_client_for_account(account_id)
        else:
            client = get_easypost_client()
        
        if not client:
            logger.error(f"No client available for account: {account_id}")
            return None
        
        shipment = client.shipment.retrieve(shipment_id)
        
        if not hasattr(shipment, 'postage_label') or not shipment.postage_label:
            logger.error(f"No label found for shipment: {shipment_id}")
            return None
            
        label_data = {
            "shipment_id": shipment_id,
            "account_id": account_id,
            "label_url": shipment.postage_label.label_url,
            "label_file_type": shipment.postage_label.label_file_type,
            "tracking_code": shipment.tracking_code,
            "created_at": shipment.postage_label.created_at
        }
        
        logger.info(f"Successfully retrieved label: {label_data['label_url']}")
        return label_data
        
    except Exception as e:
        logger.exception(f"Error retrieving label for shipment {shipment_id}: {str(e)}")
        return None

def download_label_content(label_url):
    """
    Download label content from URL
    
    Args:
        label_url (str): URL to the label file
        
    Returns:
        bytes: Label file content, or None if download fails
    """
    try:
        import requests
        
        logger.info(f"Downloading label from: {label_url}")
        
        response = requests.get(label_url, timeout=30)
        response.raise_for_status()
        
        logger.info(f"Successfully downloaded label ({len(response.content)} bytes)")
        return response.content
        
    except Exception as e:
        logger.exception(f"Error downloading label from {label_url}: {str(e)}")
        return None 