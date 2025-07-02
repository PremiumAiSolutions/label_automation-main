import logging
import os
import base64
from typing import Optional
from app.database.models import AccountDatabase, PrinterConfig

logger = logging.getLogger(__name__)

def get_printnode_client(api_key: str):
    """Get configured PrintNode client with specific API key"""
    try:
        from PrintNodeApi import Gateway
    except ImportError:
        try:
            from printnodeapi import Gateway
        except ImportError:
            raise ImportError("PrintNode API library not found. Install with: pip install PrintNodeApi")
    
    if not api_key:
        raise ValueError("PrintNode API key is required")
    return Gateway(apikey=api_key)

def send_to_printnode_for_account(label_data, label_content, account_id):
    """
    Send label to PrintNode using account-specific printer configuration
    
    Args:
        label_data (dict): Label metadata
        label_content (bytes): Raw label file content
        account_id (str): EasyPost account ID
        
    Returns:
        dict: Print job result with job ID or error info
    """
    try:
        logger.info(f"Attempting to send label to PrintNode for account: {account_id}")
        
        # Get printer configuration for account
        db = AccountDatabase()
        printer_config = db.get_default_printer_for_account(account_id)
        
        if not printer_config:
            logger.warning(f"No printer configured for account: {account_id}")
            return {
                "success": False, 
                "error": f"No printer configured for account {account_id}",
                "message": f"Label downloaded successfully but no printer configured for account {account_id}"
            }
        
        logger.info(f"Using printer: {printer_config.printer_name} (ID: {printer_config.printer_id})")
        
        # Create PrintNode client with account-specific API key
        client = get_printnode_client(printer_config.printnode_api_key)
        
        # Verify printer exists and is online
        try:
            printers = client.printers()
            target_printer = None
            
            for printer in printers:
                if isinstance(printer, dict):
                    if str(printer.get('id')) == str(printer_config.printer_id):
                        target_printer = printer
                        break
                else:
                    if str(printer[0]) == str(printer_config.printer_id):
                        target_printer = printer
                        break
            
            if not target_printer:
                logger.error(f"Printer {printer_config.printer_id} not found on PrintNode account")
                return {
                    "success": False, 
                    "error": f"Printer {printer_config.printer_id} ({printer_config.printer_name}) not found"
                }
            
            # Check if printer is online (for dict format)
            if isinstance(target_printer, dict):
                if target_printer.get('state') != 'online':
                    logger.warning(f"Printer {printer_config.printer_id} is not online (state: {target_printer.get('state', 'unknown')})")
            else:
                # For tuple format, state is usually in index 2
                state = target_printer[2] if len(target_printer) > 2 else 'unknown'
                if state != 'online':
                    logger.warning(f"Printer {printer_config.printer_id} is not online (state: {state})")
                    
        except Exception as e:
            logger.error(f"Error verifying printer {printer_config.printer_id}: {str(e)}")
            return {"success": False, "error": f"Error verifying printer: {str(e)}"}
        
        # Prepare print job
        job_title = f"Shipping Label - {label_data.get('tracking_code', 'Unknown')} ({account_id})"
        
        # Convert content to base64 for PrintNode
        content_base64 = base64.b64encode(label_content).decode('utf-8')
        
        # Determine content type based on file type
        content_type = "pdf_base64"  # Default to PDF
        if label_data.get('label_file_type', '').lower() in ['zpl', 'epl']:
            content_type = "raw_base64"
        
        # Submit print job using PrintNode's correct method
        response = client.PrintJob(
            printer=int(printer_config.printer_id),
            title=job_title,
            job_type="pdf" if content_type == "pdf_base64" else "raw",
            base64=content_base64,
            options={
                "paper": "4x6",  # Common shipping label size 
                "color": False
            }
        )
        
        if response and hasattr(response, 'id'):
            job_id = response.id
            logger.info(f"Print job submitted successfully. Job ID: {job_id}")
            return {
                "success": True, 
                "job_id": job_id,
                "printer_id": printer_config.printer_id,
                "printer_name": printer_config.printer_name,
                "account_id": account_id,
                "title": job_title
            }
        else:
            logger.error("Failed to submit print job - no valid response")
            return {"success": False, "error": "Failed to submit print job"}
            
    except Exception as e:
        logger.exception(f"Error sending label to PrintNode for account {account_id}: {str(e)}")
        return {"success": False, "error": str(e), "account_id": account_id}

def get_printer_info_for_account(account_id: str):
    """Get printer information for a specific account"""
    try:
        db = AccountDatabase()
        printers = db.get_printers_for_account(account_id)
        
        result = []
        for printer_config in printers:
            try:
                client = get_printnode_client(printer_config.printnode_api_key)
                printnode_printers = client.printers()
                
                # Find this printer in PrintNode
                printer_status = None
                for pn_printer in printnode_printers:
                    if isinstance(pn_printer, dict):
                        if str(pn_printer.get('id')) == str(printer_config.printer_id):
                            printer_status = pn_printer
                            break
                    else:
                        if str(pn_printer[0]) == str(printer_config.printer_id):
                            printer_status = {
                                'id': pn_printer[0],
                                'name': pn_printer[1] if len(pn_printer) > 1 else 'Unknown',
                                'state': pn_printer[2] if len(pn_printer) > 2 else 'unknown'
                            }
                            break
                
                result.append({
                    "config": printer_config,
                    "status": printer_status,
                    "online": printer_status and printer_status.get('state') == 'online'
                })
                
            except Exception as e:
                logger.error(f"Error getting status for printer {printer_config.id}: {e}")
                result.append({
                    "config": printer_config,
                    "status": None,
                    "online": False,
                    "error": str(e)
                })
        
        return result
        
    except Exception as e:
        logger.exception(f"Error getting printer info for account {account_id}: {str(e)}")
        return [] 