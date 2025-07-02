import logging
import os
from datetime import datetime
from flask import Blueprint, request, jsonify
from app.handlers.tracker_handler import handle_tracker_event
from app.utils.logger import save_request_to_file

logger = logging.getLogger(__name__)

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/health', methods=['GET'])
def webhook_health():
    """Webhook blueprint health check"""
    return jsonify({'status': 'healthy', 'service': 'webhook'}), 200

@webhook_bp.route('/easypost', methods=['POST'])
def easypost_webhook():
    """
    Handle incoming EasyPost webhook events (legacy endpoint)
    """
    return handle_easypost_webhook(account_id=None)

@webhook_bp.route('/easypost/<account_id>', methods=['POST'])
def easypost_webhook_account(account_id):
    """
    Handle incoming EasyPost webhook events for specific account
    """
    return handle_easypost_webhook(account_id=account_id)

def handle_easypost_webhook(account_id=None):
    """
    Common webhook handler for EasyPost events
    
    Args:
        account_id (str): Optional account ID for multi-account support
    """
    # Get the webhook event data
    payload = request.json
    
    if not payload:
        logger.error("Empty webhook payload received")
        return jsonify({'error': 'Missing payload'}), 400
    
    # Add account info to payload for processing
    if account_id:
        payload['account_id'] = account_id
        logger.info(f"Processing webhook for account: {account_id}")
    
    # Save request to file
    save_request_to_file(payload, account_id)
    
    # Log incoming webhook
    logger.info(f"Received webhook event: {payload.get('description', 'unknown event')} (account: {account_id or 'legacy'})")
    
    # Process event based on type
    event_type = payload.get('description')
    if not event_type:
        logger.error("Missing event type in webhook payload")
        return jsonify({'error': 'Missing event type'}), 400

    try:
        # Only process tracker.created events
        if event_type == 'tracker.created':
            logger.info(f"Processing tracker.created event: {payload.get('id')} (account: {account_id or 'legacy'})")
            result = handle_tracker_event(payload, account_id)
            return jsonify(result), 200
        else:
            # Log but don't process other event types
            logger.info(f"Received but not processing event type: {event_type}")
            return jsonify({
                'success': True, 
                'message': f'Event type {event_type} acknowledged but not processed',
                'account_id': account_id
            }), 200

    except Exception as e:
        logger.exception(f"Error processing webhook: {str(e)}")
        return jsonify({'error': f'Webhook processing error: {str(e)}', 'account_id': account_id}), 500