import os
import requests
import json
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

# Configuration
RASPBERRY_PI_URL = os.getenv('RASPBERRY_PI_URL', 'http://raspberrypi.local:5000')
MANAGEMENT_API_KEY = os.getenv('MANAGEMENT_API_KEY', 'change-this-secure-key')

def make_api_request(endpoint, method='GET', data=None):
    """Make request to Raspberry Pi management API"""
    url = f"{RASPBERRY_PI_URL}/manage{endpoint}"
    headers = {
        'X-API-Key': MANAGEMENT_API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data, timeout=10)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=10)
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None

@app.route('/')
def index():
    """Dashboard showing all accounts and their status"""
    status = make_api_request('/status')
    if not status:
        flash('Unable to connect to Raspberry Pi', 'error')
        status = {'accounts': [], 'accounts_count': 0}
    
    return render_template('dashboard.html', status=status, pi_url=RASPBERRY_PI_URL)

@app.route('/accounts')
def accounts():
    """List all accounts"""
    accounts_data = make_api_request('/accounts')
    if not accounts_data:
        flash('Unable to fetch accounts', 'error')
        accounts_data = []
    
    return render_template('accounts.html', accounts=accounts_data)

@app.route('/accounts/new', methods=['GET', 'POST'])
def new_account():
    """Create new account"""
    if request.method == 'POST':
        data = {
            'name': request.form['name'],
            'api_key': request.form['api_key'],
            'webhook_secret': request.form.get('webhook_secret', ''),
            'is_active': 'is_active' in request.form
        }
        
        result = make_api_request('/accounts', method='POST', data=data)
        if result:
            flash('Account created successfully!', 'success')
            return redirect(url_for('accounts'))
        else:
            flash('Failed to create account', 'error')
    
    return render_template('account_form.html', account=None, action='Create')

@app.route('/accounts/<account_id>/edit', methods=['GET', 'POST'])
def edit_account(account_id):
    """Edit existing account"""
    if request.method == 'POST':
        data = {
            'name': request.form['name'],
            'api_key': request.form['api_key'],
            'webhook_secret': request.form.get('webhook_secret', ''),
            'is_active': 'is_active' in request.form
        }
        
        result = make_api_request(f'/accounts/{account_id}', method='PUT', data=data)
        if result:
            flash('Account updated successfully!', 'success')
            return redirect(url_for('accounts'))
        else:
            flash('Failed to update account', 'error')
    
    # For GET request, we need to fetch current account data
    # This would require an additional API endpoint to get single account
    account = {'id': account_id, 'name': '', 'api_key': '', 'webhook_secret': '', 'is_active': True}
    return render_template('account_form.html', account=account, action='Edit')

@app.route('/accounts/<account_id>/delete', methods=['POST'])
def delete_account(account_id):
    """Delete account"""
    result = make_api_request(f'/accounts/{account_id}', method='DELETE')
    if result:
        flash('Account deleted successfully!', 'success')
    else:
        flash('Failed to delete account', 'error')
    
    return redirect(url_for('accounts'))

@app.route('/accounts/<account_id>/printers')
def account_printers(account_id):
    """List printers for an account"""
    printers_data = make_api_request(f'/accounts/{account_id}/printers')
    if not printers_data:
        flash('Unable to fetch printers', 'error')
        printers_data = []
    
    return render_template('printers.html', account_id=account_id, printers=printers_data)

@app.route('/accounts/<account_id>/printers/new', methods=['GET', 'POST'])
def new_printer(account_id):
    """Create new printer for account"""
    if request.method == 'POST':
        data = {
            'printer_name': request.form['printer_name'],
            'printnode_api_key': request.form['printnode_api_key'],
            'printer_id': request.form['printer_id'],
            'is_default': 'is_default' in request.form,
            'is_active': 'is_active' in request.form
        }
        
        result = make_api_request(f'/accounts/{account_id}/printers', method='POST', data=data)
        if result:
            flash('Printer created successfully!', 'success')
            return redirect(url_for('account_printers', account_id=account_id))
        else:
            flash('Failed to create printer', 'error')
    
    return render_template('printer_form.html', account_id=account_id, printer=None, action='Create')

@app.route('/sync')
def sync_config():
    """Sync configuration to Raspberry Pi"""
    result = make_api_request('/restart', method='POST')
    if result:
        flash('Configuration synced successfully!', 'success')
    else:
        flash('Failed to sync configuration', 'error')
    
    return redirect(url_for('index'))

@app.route('/export')
def export_config():
    """Export configuration as JSON"""
    config = make_api_request('/config/export')
    if config:
        response = app.response_class(
            response=json.dumps(config, indent=2),
            status=200,
            mimetype='application/json'
        )
        response.headers["Content-Disposition"] = f"attachment; filename=label_automation_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        return response
    else:
        flash('Failed to export configuration', 'error')
        return redirect(url_for('index'))

@app.route('/import', methods=['POST'])
def import_config():
    """Import configuration from JSON file"""
    if 'config_file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    file = request.files['config_file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    try:
        config_data = json.load(file)
        result = make_api_request('/config/import', method='POST', data=config_data)
        if result:
            flash('Configuration imported successfully!', 'success')
        else:
            flash('Failed to import configuration', 'error')
    except json.JSONDecodeError:
        flash('Invalid JSON file', 'error')
    except Exception as e:
        flash(f'Error importing configuration: {str(e)}', 'error')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080) 