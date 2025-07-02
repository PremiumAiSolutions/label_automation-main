import logging
import os
from app.easypost.multi_client import get_easypost_client_for_account, get_easypost_client, download_label_content
from app.converter.label_converter import convert_label_if_needed
from app.printnode.multi_printer import send_to_printnode_for_account
from app.database.models import AccountDatabase

logger = logging.getLogger(__name__)

def handle_tracker_event(event_data, account_id=None):
    """
    Process tracker events from EasyPost
    
    Args:
        event_data (dict): The webhook event payload
        account_id (str): Optional account ID for multi-account support
    
    Returns:
        dict: Processing result with label information and print job status
    """
    try:
        # Extract tracker ID from the event data
        tracker_id = event_data.get('result', {}).get('id')
        if not tracker_id:
            logger.error("No tracker ID found in event data")
            return {"success": False, "error": "No tracker ID found"}
        
        logger.info(f"Processing tracker event for tracker_id: {tracker_id} (account: {account_id or 'legacy'})")
        
        # Get tracker details from EasyPost API
        try:
            if account_id:
                client = get_easypost_client_for_account(account_id)
                if not client:
                    logger.error(f"No client available for account: {account_id}")
                    return {"success": False, "error": f"Account {account_id} not configured"}
            else:
                client = get_easypost_client()
            
            tracker = client.tracker.retrieve(tracker_id)
            logger.info(f"Retrieved tracker with tracking code: {tracker.tracking_code}")
            
            # Find associated shipment using tracking code
            # Note: This requires searching shipments that match this tracking code
            shipments = client.shipment.all(
                page_size=1,
                tracking_code=tracker.tracking_code
            )

            if not shipments or len(shipments.shipments) == 0:
                logger.error(f"No shipment found with tracking code: {tracker.tracking_code}")
                return {"success": False, "error": "No associated shipment found"}

            # Get the first matching shipment
            shipment = shipments.shipments[0]
            logger.info(f"Found associated shipment ID: {shipment.id}")

            # Get label information
            if not hasattr(shipment, 'postage_label') or not shipment.postage_label:
                logger.error(f"No label found for shipment: {shipment.id}")
                return {"success": False, "error": "No label found for this shipment"}

            # Extract label information
            label_info = {
                "shipment_id": shipment.id,
                "account_id": account_id,
                "tracking_code": tracker.tracking_code,
                "label_url": shipment.postage_label.label_url,
                "label_file_type": shipment.postage_label.label_file_type,
                "label_date": shipment.postage_label.created_at
            }

            # Print label info to console every time
            print("\n===== LABEL INFORMATION =====")
            print(f"Account: {account_id or 'Legacy'}")
            print(f"Shipment ID: {label_info['shipment_id']}")
            print(f"Tracking Code: {label_info['tracking_code']}")
            print(f"Label URL: {label_info['label_url']}")
            print(f"File Type: {label_info['label_file_type']}")
            print(f"Created At: {label_info['label_date']}")
            print("=============================\n")

            logger.info(f"Successfully retrieved label URL: {label_info['label_url']}")
            
            # Download label content
            logger.info("Downloading label content...")
            label_content = download_label_content(label_info['label_url'])
            
            if not label_content:
                logger.error("Failed to download label content")
                return {
                    "success": True, 
                    "label_info": label_info,
                    "print_job": {"success": False, "error": "Failed to download label"}
                }
            
            # Convert label if needed
            logger.info("Processing label for printing...")
            converted_label_data, converted_content = convert_label_if_needed(
                label_info, label_content
            )
            
            # Send to PrintNode for printing
            print_result = {"success": False, "error": "Printing disabled"}
            
            # Use account-specific printing if account_id is provided
            if account_id:
                logger.info(f"Sending label to PrintNode for account: {account_id}")
                print_result = send_to_printnode_for_account(
                    converted_label_data, converted_content, account_id
                )
            else:
                # Legacy printing behavior
                logger.info("Using legacy PrintNode configuration...")
                from app.printnode.printer import send_to_printnode
                
                if os.getenv('PRINTNODE_API_KEY'):
                    print_result = send_to_printnode(converted_label_data, converted_content)
                else:
                    print_result = {
                        "success": False,
                        "error": "No PrintNode configuration available",
                        "message": "Label downloaded but no printing configuration found"
                    }
            
            # Display results
            if print_result.get('success'):
                print(f"\n===== PRINT JOB SUBMITTED =====")
                print(f"Account: {account_id or 'Legacy'}")
                print(f"Job ID: {print_result.get('job_id')}")
                print(f"Printer ID: {print_result.get('printer_id')}")
                print(f"Printer Name: {print_result.get('printer_name', 'Unknown')}")
                print(f"Title: {print_result.get('title')}")
                print("==============================\n")
            elif print_result.get('message'):
                # Printer not configured case
                print(f"\n===== LABEL READY FOR PRINTING =====")
                print(f"Account: {account_id or 'Legacy'}")
                print(f"Status: {print_result.get('message')}")
                print(f"Action Needed: {print_result.get('error')}")
                print("===================================\n")
            else:
                print(f"\n===== PRINT JOB FAILED =====")
                print(f"Account: {account_id or 'Legacy'}")
                print(f"Error: {print_result.get('error')}")
                print("============================\n")

            return {
                "success": True, 
                "account_id": account_id,
                "label_info": label_info,
                "print_job": print_result
            }

        except Exception as api_error:
            logger.error(f"Error retrieving data from EasyPost API: {str(api_error)}")
            return {"success": False, "error": f"API Error: {str(api_error)}", "account_id": account_id}

    except Exception as e:
        logger.exception(f"Error handling tracker event: {str(e)}")
        return {"success": False, "error": str(e), "account_id": account_id}
