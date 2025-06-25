import logging
import os
from easypost import EasyPostClient
from app.easypost.client import get_easypost_client, download_label_content
from app.converter.label_converter import convert_label_if_needed
from app.printnode.printer import send_to_printnode

logger = logging.getLogger(__name__)

def handle_tracker_event(event_data):
    """
    Process tracker events from EasyPost
    
    Args:
        event_data (dict): The webhook event payload
    
    Returns:
        dict: Processing result with label information and print job status
    """
    try:
        # Extract tracker ID from the event data
        tracker_id = event_data.get('result', {}).get('id')
        if not tracker_id:
            logger.error("No tracker ID found in event data")
            return {"success": False, "error": "No tracker ID found"}
        
        logger.info(f"Processing tracker event for tracker_id: {tracker_id}")
        
        # Get tracker details from EasyPost API
        try:
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
                "tracking_code": tracker.tracking_code,
                "label_url": shipment.postage_label.label_url,
                "label_file_type": shipment.postage_label.label_file_type,
                "label_date": shipment.postage_label.created_at
            }

            # Print label info to console every time
            print("\n===== LABEL INFORMATION =====")
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
            
            # Check if PrintNode is configured
            if os.getenv('PRINTNODE_API_KEY'):
                logger.info("Sending label to PrintNode...")
                print_result = send_to_printnode(converted_label_data, converted_content)
                
                if print_result.get('success'):
                    print(f"\n===== PRINT JOB SUBMITTED =====")
                    print(f"Job ID: {print_result.get('job_id')}")
                    print(f"Printer ID: {print_result.get('printer_id')}")
                    print(f"Title: {print_result.get('title')}")
                    print("==============================\n")
                elif print_result.get('message'):
                    # Printer not configured case
                    print(f"\n===== LABEL READY FOR PRINTING =====")
                    print(f"Status: {print_result.get('message')}")
                    print(f"Action Needed: {print_result.get('error')}")
                    print("===================================\n")
                else:
                    print(f"\n===== PRINT JOB FAILED =====")
                    print(f"Error: {print_result.get('error')}")
                    print("============================\n")
            else:
                logger.warning("PrintNode not configured - skipping printing")
                print("\n===== PRINTING SKIPPED =====")
                print("PrintNode API key not configured")
                print("============================\n")

            return {
                "success": True, 
                "label_info": label_info,
                "print_job": print_result
            }

        except Exception as api_error:
            logger.error(f"Error retrieving data from EasyPost API: {str(api_error)}")
            return {"success": False, "error": f"API Error: {str(api_error)}"}

    except Exception as e:
        logger.exception(f"Error handling tracker event: {str(e)}")
        return {"success": False, "error": str(e)}
