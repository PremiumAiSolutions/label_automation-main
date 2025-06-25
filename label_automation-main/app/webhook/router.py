import logging
import json
import os
import datetime
from flask import Blueprint, request, jsonify, current_app
from app.handlers.tracker_handler import handle_tracker_event

# Create blueprint
webhook_bp = Blueprint('webhook', __name__)
logger = logging.getLogger(__name__)

def save_request_to_file(payload):
    """Save incoming webhook request to a file"""
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.getcwd(), 'webhook_logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Generate unique filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    event_type = payload.get('event', 'unknown')
    filename = f"{timestamp}_{event_type}.json"
    filepath = os.path.join(log_dir, filename)
    
    # Write payload to file
    with open(filepath, 'w') as file:
        json.dump(payload, file, indent=2)
    
    logger.info(f"Saved webhook request to {filepath}")
    return filepath

@webhook_bp.route('/easypost', methods=['POST'])
def easypost_webhook():
    """
    Handle incoming EasyPost webhook events
    """
    # Get the webhook event data
    payload = request.json
    
    if not payload:
        logger.error("Empty webhook payload received")
        return jsonify({'error': 'Missing payload'}), 400
    
    # Save request to file
    save_request_to_file(payload)
    
    # Log incoming webhook
    logger.info(f"Received webhook event: {payload.get('description', 'unknown event')}")
    
    # Process event based on type
    event_type = payload.get('description')
    if not event_type:
        logger.error("Missing event type in webhook payload")
        return jsonify({'error': 'Missing event type'}), 400

    try:
        # Only process tracker.created events
        if event_type == 'tracker.created':
            logger.info(f"Processing tracker.created event: {payload.get('id')}")
            result = handle_tracker_event(payload)
            return jsonify(result), 200
        else:
            # Log but don't process other event types
            logger.info(f"Received but not processing event type: {event_type}")
            return jsonify({'success': True, 'message': f'Event type {event_type} acknowledged but not processed'}), 200

    except Exception as e:
        logger.exception(f"Error processing webhook: {str(e)}")
        return jsonify({'error': f'Webhook processing error: {str(e)}'}), 500