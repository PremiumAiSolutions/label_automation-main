import logging
import uuid
from flask import Blueprint, request, jsonify, current_app
from functools import wraps
from app.database.models import AccountDatabase, EasyPostAccount, PrinterConfig
from app.easypost.multi_client import multi_client_manager

logger = logging.getLogger(__name__)

management_bp = Blueprint('management', __name__)

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        expected_key = current_app.config.get('MANAGEMENT_API_KEY')
        
        if not api_key or api_key != expected_key:
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

@management_bp.route('/health', methods=['GET'])
def management_health():
    """Management API health check"""
    return jsonify({'status': 'healthy', 'service': 'management'}), 200

@management_bp.route('/config/export', methods=['GET'])
@require_api_key
def export_config():
    """Export current configuration"""
    try:
        db = AccountDatabase()
        config = db.export_config()
        return jsonify(config), 200
    except Exception as e:
        logger.error(f"Error exporting config: {e}")
        return jsonify({'error': str(e)}), 500

@management_bp.route('/config/import', methods=['POST'])
@require_api_key
def import_config():
    """Import configuration from JSON"""
    try:
        config_data = request.json
        if not config_data:
            return jsonify({'error': 'No configuration data provided'}), 400
        
        db = AccountDatabase()
        success = db.import_config(config_data)
        
        if success:
            # Refresh client cache
            for account in config_data.get('accounts', []):
                multi_client_manager.refresh_client(account['id'])
            
            return jsonify({'message': 'Configuration imported successfully'}), 200
        else:
            return jsonify({'error': 'Failed to import configuration'}), 500
    
    except Exception as e:
        logger.error(f"Error importing config: {e}")
        return jsonify({'error': str(e)}), 500

@management_bp.route('/accounts', methods=['GET'])
@require_api_key
def list_accounts():
    """List all EasyPost accounts"""
    try:
        db = AccountDatabase()
        accounts = db.get_all_easypost_accounts()
        return jsonify([{
            'id': acc.id,
            'name': acc.name,
            'is_active': acc.is_active,
            'created_at': acc.created_at,
            'updated_at': acc.updated_at
        } for acc in accounts]), 200
    except Exception as e:
        logger.error(f"Error listing accounts: {e}")
        return jsonify({'error': str(e)}), 500

@management_bp.route('/accounts', methods=['POST'])
@require_api_key
def create_account():
    """Create new EasyPost account"""
    try:
        data = request.json
        if not data or not all(k in data for k in ['name', 'api_key']):
            return jsonify({'error': 'Missing required fields: name, api_key'}), 400
        
        account_id = data.get('id', str(uuid.uuid4()))
        account = EasyPostAccount(
            id=account_id,
            name=data['name'],
            api_key=data['api_key'],
            webhook_secret=data.get('webhook_secret'),
            is_active=data.get('is_active', True)
        )
        
        db = AccountDatabase()
        success = db.add_easypost_account(account)
        
        if success:
            return jsonify({'message': 'Account created successfully', 'id': account_id}), 201
        else:
            return jsonify({'error': 'Failed to create account'}), 500
    
    except Exception as e:
        logger.error(f"Error creating account: {e}")
        return jsonify({'error': str(e)}), 500

@management_bp.route('/accounts/<account_id>', methods=['PUT'])
@require_api_key
def update_account(account_id):
    """Update EasyPost account"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        db = AccountDatabase()
        account = db.get_easypost_account(account_id)
        
        if not account:
            return jsonify({'error': 'Account not found'}), 404
        
        # Update fields
        if 'name' in data:
            account.name = data['name']
        if 'api_key' in data:
            account.api_key = data['api_key']
        if 'webhook_secret' in data:
            account.webhook_secret = data['webhook_secret']
        if 'is_active' in data:
            account.is_active = data['is_active']
        
        success = db.update_easypost_account(account)
        
        if success:
            # Refresh client cache
            multi_client_manager.refresh_client(account_id)
            return jsonify({'message': 'Account updated successfully'}), 200
        else:
            return jsonify({'error': 'Failed to update account'}), 500
    
    except Exception as e:
        logger.error(f"Error updating account: {e}")
        return jsonify({'error': str(e)}), 500

@management_bp.route('/accounts/<account_id>', methods=['DELETE'])
@require_api_key
def delete_account(account_id):
    """Delete EasyPost account"""
    try:
        db = AccountDatabase()
        success = db.delete_easypost_account(account_id)
        
        if success:
            # Refresh client cache
            multi_client_manager.refresh_client(account_id)
            return jsonify({'message': 'Account deleted successfully'}), 200
        else:
            return jsonify({'error': 'Account not found'}), 404
    
    except Exception as e:
        logger.error(f"Error deleting account: {e}")
        return jsonify({'error': str(e)}), 500

@management_bp.route('/accounts/<account_id>/printers', methods=['GET'])
@require_api_key
def list_printers(account_id):
    """List printers for an account"""
    try:
        db = AccountDatabase()
        printers = db.get_printers_for_account(account_id)
        return jsonify([{
            'id': p.id,
            'printer_name': p.printer_name,
            'printer_id': p.printer_id,
            'is_default': p.is_default,
            'is_active': p.is_active,
            'created_at': p.created_at,
            'updated_at': p.updated_at
        } for p in printers]), 200
    except Exception as e:
        logger.error(f"Error listing printers: {e}")
        return jsonify({'error': str(e)}), 500

@management_bp.route('/accounts/<account_id>/printers', methods=['POST'])
@require_api_key
def create_printer(account_id):
    """Create new printer configuration"""
    try:
        data = request.json
        if not data or not all(k in data for k in ['printer_name', 'printnode_api_key', 'printer_id']):
            return jsonify({'error': 'Missing required fields: printer_name, printnode_api_key, printer_id'}), 400
        
        printer_config_id = data.get('id', str(uuid.uuid4()))
        printer = PrinterConfig(
            id=printer_config_id,
            account_id=account_id,
            printer_name=data['printer_name'],
            printnode_api_key=data['printnode_api_key'],
            printer_id=data['printer_id'],
            is_default=data.get('is_default', False),
            is_active=data.get('is_active', True)
        )
        
        db = AccountDatabase()
        success = db.add_printer_config(printer)
        
        if success:
            return jsonify({'message': 'Printer created successfully', 'id': printer_config_id}), 201
        else:
            return jsonify({'error': 'Failed to create printer'}), 500
    
    except Exception as e:
        logger.error(f"Error creating printer: {e}")
        return jsonify({'error': str(e)}), 500

@management_bp.route('/restart', methods=['POST'])
@require_api_key
def restart_service():
    """Restart the label automation service"""
    try:
        # In a real deployment, this would restart the service
        # For now, just refresh all client connections
        for account in AccountDatabase().get_all_easypost_accounts():
            multi_client_manager.refresh_client(account.id)
        
        return jsonify({'message': 'Service restarted successfully'}), 200
    except Exception as e:
        logger.error(f"Error restarting service: {e}")
        return jsonify({'error': str(e)}), 500

@management_bp.route('/status', methods=['GET'])
@require_api_key
def get_status():
    """Get system status"""
    try:
        db = AccountDatabase()
        accounts = db.get_all_easypost_accounts()
        
        status = {
            'accounts_count': len(accounts),
            'accounts': []
        }
        
        for account in accounts:
            printers = db.get_printers_for_account(account.id)
            status['accounts'].append({
                'id': account.id,
                'name': account.name,
                'is_active': account.is_active,
                'printers_count': len(printers),
                'webhook_url': f"/webhook/easypost/{account.id}"
            })
        
        return jsonify(status), 200
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': str(e)}), 500 