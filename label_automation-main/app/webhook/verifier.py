import hmac
import hashlib
import logging

logger = logging.getLogger(__name__)

def verify_easypost_signature(signature, payload, webhook_secret):
    """
    Verify that the webhook request is from EasyPost using HMAC signature
    
    Args:
        signature (str): The HMAC signature from the X-Easypost-Signature header
        payload (bytes): The raw request body
        webhook_secret (str): The EasyPost webhook signing secret
        
    Returns:
        bool: True if signature is valid, False otherwise
    """
    if not signature or not webhook_secret:
        logger.warning("Missing signature or webhook secret")
        return False
    
    try:
        # Create HMAC-SHA256 signature using webhook secret
        computed_signature = hmac.new(
            key=webhook_secret.encode('utf-8'),
            msg=payload,
            digestmod=hashlib.sha256
        ).hexdigest()
        
        # Compare signatures using constant-time comparison
        return hmac.compare_digest(computed_signature, signature)
    
    except Exception as e:
        logger.exception(f"Error verifying signature: {str(e)}")
        return False