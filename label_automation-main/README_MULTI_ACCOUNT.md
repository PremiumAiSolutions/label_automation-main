# 🎉 Multi-Account Label Automation System

**Version 2.0** - Now with support for multiple EasyPost accounts and web-based management!

## 🚀 What's New

### ✅ Multi-Account Support
- Manage multiple EasyPost accounts from a single system
- Each account can have its own printers and configurations
- Dedicated webhook URLs for each account

### ✅ Web Management Interface
- Beautiful web interface to manage accounts and printers
- Runs on your computer (localhost:8080)
- Remotely configures your Raspberry Pi

### ✅ Enhanced Features
- Import/export configurations
- Account-specific printer settings
- Real-time status monitoring
- Secure API communication

### ✅ Backward Compatibility
- Existing single-account setup continues to work
- No breaking changes to current workflows
- Gradual migration path

## 🏗️ System Overview

```
┌─────────────────┐    HTTP API    ┌─────────────────┐
│   Your Computer │ ◄────────────► │  Raspberry Pi   │
│                 │                │                 │
│  Frontend App   │                │  Label Service  │
│  (localhost:8080)│                │  (port 5000)    │
└─────────────────┘                └─────────────────┘
                                            ▲
                                            │ Webhooks
                                            ▼
                                   ┌─────────────────┐
                                   │    EasyPost     │
                                   │   (Multiple     │
                                   │   Accounts)     │
                                   └─────────────────┘
```

## 🚀 Quick Setup

### 1. Update Raspberry Pi

```bash
cd label_automation-main
git pull  # If using git, or re-download the files

# Install new dependencies
pip install -r requirements.txt

# Copy the new environment template
cp .env.multi .env
nano .env  # Edit with your settings
```

Set your management API key in `.env`:
```env
MANAGEMENT_API_KEY=your-secure-api-key-12345
```

Start the enhanced service:
```bash
python -m app.main
```

### 2. Start Frontend (Your Computer)

**Windows:**
```cmd
start_frontend.bat
```

**Linux/Mac:**
```bash
./start_frontend.sh
```

**Manual:**
```bash
cd frontend
pip install -r requirements.txt
python app.py
```

### 3. Access Management Interface

Open your browser to: `http://localhost:8080`

## 📋 Step-by-Step Setup

### Step 1: Add Your First Account

1. Open the management interface (`http://localhost:8080`)
2. Click "Add Account"
3. Fill in your EasyPost details:
   - **Name**: "Main Store" (or whatever you prefer)
   - **API Key**: Your EasyPost API key
   - **Active**: ✅ Checked

### Step 2: Configure a Printer

1. Click on your account in the dashboard
2. Click "Add Printer"
3. Configure your printer:
   - **Printer Name**: "Main Label Printer"
   - **PrintNode API Key**: Your PrintNode API key
   - **Printer ID**: Your PrintNode printer ID
   - **Default**: ✅ Checked (for first printer)

### Step 3: Update EasyPost Webhook

1. Go to your EasyPost Dashboard → Webhooks
2. Update your webhook URL to: `http://your-pi-ip:5000/webhook/easypost/your-account-id`
3. You can copy this URL directly from the management interface

## 🔗 Webhook URLs

Your system now supports multiple webhook endpoints:

- **Legacy (existing)**: `http://your-pi:5000/webhook/easypost`
- **Account-specific**: `http://your-pi:5000/webhook/easypost/{account-id}`

Each account gets its own unique webhook URL displayed in the management interface.

## 🎯 Key Features

### Dashboard
- Overview of all accounts and printers
- Quick access to webhook URLs (copy with one click)
- System status monitoring

### Account Management
- Add unlimited EasyPost accounts
- Edit account details and API keys
- Enable/disable accounts
- Each account isolated from others

### Printer Management
- Multiple printers per account
- Set default printers per account
- Different PrintNode accounts per printer
- Test printer connectivity

### Configuration Management
- Export all settings as JSON
- Import configurations from backup
- Sync changes to Raspberry Pi instantly
- Remote management - no SSH required

## 🔧 Advanced Features

### Multiple PrintNode Accounts
Each printer can use a different PrintNode API key, allowing you to:
- Use separate PrintNode accounts for different locations
- Isolate billing and monitoring per printer
- Manage permissions granularly

### Account Isolation
- Each EasyPost account processes independently
- Account-specific error handling
- Separate logging and monitoring

### Security
- API key authentication between frontend and Pi
- Masked API keys in the interface
- Secure configuration sync

## 🛠️ Migration Guide

### From Single Account Setup

**Option 1: Keep Current Setup (Recommended)**
- Your existing setup continues to work unchanged
- Add new accounts through the management interface
- Migrate gradually as needed

**Option 2: Full Migration**
1. Create your first account in the management interface
2. Copy your existing API keys to the new account  
3. Add your printer configuration
4. Update your EasyPost webhook URL
5. Test thoroughly before removing legacy config

## 🔍 Monitoring & Troubleshooting

### Logs
- **Application**: `app.log`
- **Webhooks**: `webhook_logs/` (organized by account)
- **Frontend**: Console output

### Status Checking
- Management interface shows real-time status
- Printer online/offline status
- Account activity monitoring

### Common Issues

**Frontend can't connect to Pi:**
- Check `RASPBERRY_PI_URL` in `frontend/.env`
- Verify `MANAGEMENT_API_KEY` matches on both systems

**Labels not printing:**
- Check account is active
- Verify printer is set as default
- Confirm PrintNode printer is online

## 📊 Configuration Files

### Raspberry Pi (`label_automation-main/.env`)
```env
# Management API
MANAGEMENT_API_KEY=your-secure-key

# Legacy support (optional)
EASYPOST_API_KEY=your-easypost-key
PRINTNODE_API_KEY=your-printnode-key
PRINTNODE_PRINTER_ID=your-printer-id

# System
DATABASE_PATH=accounts.db
PORT=5000
```

### Frontend (`frontend/.env`)
```env
RASPBERRY_PI_URL=http://your-pi-ip:5000
MANAGEMENT_API_KEY=your-secure-key
FRONTEND_PORT=8080
```

## 🎉 Benefits

### For Multiple Stores/Warehouses
- Each location gets its own EasyPost account
- Dedicated printers per location
- Centralized management from one interface
- Independent processing and monitoring

### For Multiple Businesses
- Separate EasyPost accounts per business
- Isolated billing and configurations
- Unified management platform
- Scalable architecture

### For Development/Testing
- Test accounts with dedicated printers
- Production accounts with live printers
- Easy switching between configurations
- Safe testing environment

## 🆘 Support & Backup

### Backup Strategy
1. **Export configuration** regularly from the frontend
2. **Save environment files** (`.env` files)
3. **Backup database** (`accounts.db` file)

### Getting Help
1. Check the management interface for status
2. Review logs for error messages
3. Test with legacy single-account mode
4. Export configuration for troubleshooting

## 🎯 Next Steps

1. **Start the frontend** on your computer
2. **Add your EasyPost accounts** via the web interface
3. **Configure printers** for each account
4. **Update webhooks** in EasyPost to use new URLs
5. **Test with sample shipments**
6. **Create configuration backups**

---

🎉 **Congratulations!** You now have a powerful multi-account label automation system that can scale with your business needs while providing a user-friendly management interface.

For detailed setup instructions, see `MULTI_ACCOUNT_SETUP.md`. 