import logging
import os
import base64

logger = logging.getLogger(__name__)

def get_printnode_client():
    """Get configured PrintNode client"""
    try:
        from PrintNodeApi import Gateway
    except ImportError:
        try:
            from printnodeapi import Gateway
        except ImportError:
            raise ImportError("PrintNode API library not found. Install with: pip install PrintNodeApi")
    
    api_key = os.getenv('PRINTNODE_API_KEY')
    if not api_key:
        raise ValueError("PRINTNODE_API_KEY environment variable is required")
    return Gateway(apikey=api_key)

def get_printer_info():
    """Get information about the configured printer"""
    try:
        client = get_printnode_client()
        printer_id = os.getenv('PRINTNODE_PRINTER_ID')
        
        if not printer_id or printer_id == 'your-printer-id':
            # List all available printers if no specific printer configured
            printers = client.printers()
            logger.info("Available printers:")
            for printer in printers:
                # Handle both dict and tuple formats from PrintNode API
                if isinstance(printer, dict):
                    logger.info(f"  ID: {printer['id']}, Name: {printer['name']}, State: {printer['state']}")
                else:
                    # If it's a tuple or list, access by index
                    logger.info(f"  ID: {printer[0]}, Name: {printer[1]}, State: {printer[2] if len(printer) > 2 else 'unknown'}")
            return printers
        else:
            # Get specific printer from the list
            printers = client.printers()
            for printer in printers:
                # Handle both dict and tuple formats
                if isinstance(printer, dict):
                    if str(printer.get('id')) == str(printer_id):
                        logger.info(f"Configured printer: {printer['name']} (ID: {printer_id})")
                        return printer
                else:
                    # If it's a tuple or list
                    if str(printer[0]) == str(printer_id):
                        name = printer[1] if len(printer) > 1 else 'Unknown'
                        logger.info(f"Configured printer: {name} (ID: {printer_id})")
                        return printer
            
            logger.warning(f"Printer with ID {printer_id} not found")
            return None
            
    except Exception as e:
        logger.exception(f"Error getting printer info: {str(e)}")
        return None

def send_to_printnode(label_data, label_content):
    """
    Send label to PrintNode for printing
    
    Args:
        label_data (dict): Label metadata
        label_content (bytes): Raw label file content
        
    Returns:
        dict: Print job result with job ID or error info
    """
    try:
        logger.info("Attempting to send label to PrintNode")
        
        client = get_printnode_client()
        printer_id = os.getenv('PRINTNODE_PRINTER_ID')
        
        # Check if printer ID is configured
        if not printer_id or printer_id == 'your-printer-id':
            logger.warning("No printer ID configured yet")
            
            # List available printers for when they're ready
            try:
                printers = client.printers()
                if printers:
                    logger.info("Available printers for future configuration:")
                    for printer in printers:
                        logger.info(f"  ID: {printer['id']}, Name: {printer['name']}, State: {printer['state']}")
                else:
                    logger.info("No printers found on PrintNode account")
            except:
                pass
            
            return {
                "success": False, 
                "error": "No printer configured yet. Update PRINTNODE_PRINTER_ID in .env when printer arrives.",
                "message": "Label downloaded successfully but printing skipped (no printer configured)"
            }
        
        # Verify printer exists and is online
        try:
            printers = client.printers()
            target_printer = None
            
            for printer in printers:
                if isinstance(printer, dict):
                    if str(printer.get('id')) == str(printer_id):
                        target_printer = printer
                        break
                else:
                    if str(printer[0]) == str(printer_id):
                        target_printer = printer
                        break
            
            if not target_printer:
                logger.error(f"Printer {printer_id} not found on account")
                return {"success": False, "error": f"Printer {printer_id} not found"}
            
            # Check if printer is online (for dict format)
            if isinstance(target_printer, dict):
                if target_printer.get('state') != 'online':
                    logger.warning(f"Printer {printer_id} is not online (state: {target_printer.get('state', 'unknown')})")
            else:
                # For tuple format, state is usually in index 2
                state = target_printer[2] if len(target_printer) > 2 else 'unknown'
                if state != 'online':
                    logger.warning(f"Printer {printer_id} is not online (state: {state})")
                    
        except Exception as e:
            logger.error(f"Error verifying printer {printer_id}: {str(e)}")
            return {"success": False, "error": f"Error verifying printer: {str(e)}"}
        
        # Prepare print job
        job_title = f"Shipping Label - {label_data.get('tracking_code', 'Unknown')}"
        
        # Convert content to base64 for PrintNode
        content_base64 = base64.b64encode(label_content).decode('utf-8')
        
        # Determine content type based on file type
        content_type = "pdf_base64"  # Default to PDF
        if label_data.get('label_file_type', '').lower() in ['zpl', 'epl']:
            content_type = "raw_base64"
        
        # Create print job
        printjob = {
            "printer": printer_id,
            "title": job_title,
            "contentType": content_type,
            "content": content_base64,
            "options": {
                "papersize": "4x6",  # Common shipping label size
                "color": False
            }
        }
        
        # Submit print job
        response = client.printjob(printjob)
        
        if response and len(response) > 0:
            job_id = response[0]
            logger.info(f"Print job submitted successfully. Job ID: {job_id}")
            return {
                "success": True, 
                "job_id": job_id,
                "printer_id": printer_id,
                "title": job_title
            }
        else:
            logger.error("Failed to submit print job - no job ID returned")
            return {"success": False, "error": "Failed to submit print job"}
            
    except Exception as e:
        logger.exception(f"Error sending label to PrintNode: {str(e)}")
        return {"success": False, "error": str(e)}

def check_print_job_status(job_id):
    """
    Check the status of a print job
    
    Args:
        job_id (int): PrintNode job ID
        
    Returns:
        dict: Job status information
    """
    try:
        client = get_printnode_client()
        job = client.printjob(job_id)
        
        logger.info(f"Print job {job_id} status: {job.get('state', 'unknown')}")
        return {
            "success": True,
            "job_id": job_id,
            "state": job.get('state', 'unknown'),
            "created_at": job.get('createTimestamp'),
            "printer_id": job.get('printer', {}).get('id')
        }
        
    except Exception as e:
        logger.exception(f"Error checking print job status: {str(e)}")
        return {"success": False, "error": str(e)}