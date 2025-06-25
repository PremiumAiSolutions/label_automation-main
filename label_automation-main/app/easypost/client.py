import logging
import os
from easypost import EasyPostClient

logger = logging.getLogger(__name__)

def get_easypost_client():
    """Get configured EasyPost client"""
    api_key = os.getenv('EASYPOST_API_KEY')
    if not api_key:
        raise ValueError("EASYPOST_API_KEY environment variable is required")
    return EasyPostClient(api_key)

def get_label_from_shipment(shipment_id):
    """
    Retrieve shipping label from a shipment
    
    Args:
        shipment_id (str): EasyPost shipment ID
        
    Returns:
        dict: Label data with URL and metadata, or None if not found
    """
    try:
        logger.info(f"Getting label for shipment: {shipment_id}")
        
        client = get_easypost_client()
        shipment = client.shipment.retrieve(shipment_id)
        
        if not hasattr(shipment, 'postage_label') or not shipment.postage_label:
            logger.error(f"No label found for shipment: {shipment_id}")
            return None
            
        label_data = {
            "shipment_id": shipment_id,
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