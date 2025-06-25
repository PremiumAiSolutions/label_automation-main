# 🚀 Quick Start Guide

## Step 1: Install Dependencies

Run the installation script:
```bash
python install.py
```

Or install manually:
```bash
pip install flask easypost python-dotenv requests colorama
```

## Step 2: Configure API Keys

Edit the `.env` file and add your API keys:

```env
# EasyPost Configuration
EASYPOST_API_KEY=EZAK_your_actual_api_key_here

# PrintNode Configuration  
PRINTNODE_API_KEY=your_actual_printnode_key_here
PRINTNODE_PRINTER_ID=12345  # Your printer ID number
```

## Step 3: Test Your Setup

Check if everything is configured correctly:
```bash
python setup.py health
```

## Step 4: Start the Application

```bash
python -m app.main
```

The server will start on `http://localhost:5000`

## Step 5: Test the Webhook

In another terminal, test the webhook endpoint:
```bash
python test_webhook.py
```

## 📋 Getting Your API Keys

### EasyPost API Key:
1. Go to [EasyPost Dashboard](https://www.easypost.com/account/api-keys)
2. Copy your API key (starts with `EZAK_` for production or `EZTK_` for test)

### PrintNode API Key & Printer ID:
1. Go to [PrintNode Dashboard](https://app.printnode.com/app/api/keys)
2. Create an API key
3. Find your printer ID:
   ```bash
   python setup.py printnode
   ```

## 🔧 EasyPost Webhook Setup

1. In EasyPost Dashboard, go to Webhooks
2. Add webhook URL: `https://your-domain.com/webhook/easypost`
3. Select event: `tracker.created`
4. Save the webhook

## ✅ You're Ready!

Once configured, the system will:
1. Receive EasyPost webhook when tracker is created
2. Download the shipping label automatically
3. Print it to your configured printer
4. Log all activities for monitoring

## 🆘 Troubleshooting

- **ImportError**: Run `python install.py` to install dependencies
- **API Key Issues**: Double-check your `.env` file format
- **Printer Not Found**: Run `python setup.py printnode` to list available printers
- **Webhook Not Working**: Check that your server is publicly accessible 