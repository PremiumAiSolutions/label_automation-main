# Label Automation System

A Flask-based webhook service that automatically processes EasyPost tracking events and prints shipping labels via PrintNode.

## 🚀 Features

- **EasyPost Integration**: Receives webhook events when trackers are created
- **Automatic Label Retrieval**: Downloads shipping labels from EasyPost
- **PrintNode Integration**: Automatically prints labels to configured printers
- **Label Format Support**: Handles PDF, ZPL, and EPL label formats
- **Webhook Security**: Supports HMAC signature verification
- **Comprehensive Logging**: Detailed logging for debugging and monitoring

## 📋 Prerequisites

- Python 3.7+
- EasyPost account with API key
- PrintNode account with API key
- A configured printer accessible via PrintNode

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd label_automation-main
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   - Copy the `.env` file and update with your API keys:
   ```bash
   cp .env .env.local
   ```
   - Edit `.env` with your actual values:
   ```env
   # Flask Configuration
   SECRET_KEY=your-secret-key-here-change-in-production
   DEBUG=false
   PORT=5000
   LOG_LEVEL=INFO

   # EasyPost Configuration
   EASYPOST_API_KEY=your-easypost-api-key-here

   # PrintNode Configuration
   PRINTNODE_API_KEY=your-printnode-api-key-here
   PRINTNODE_PRINTER_ID=your-printer-id-here
   ```

## 🔧 Configuration

### EasyPost Setup

1. Get your EasyPost API key from the [EasyPost Dashboard](https://www.easypost.com/account/api-keys)
2. Set up a webhook endpoint in EasyPost pointing to: `https://your-domain.com/webhook/easypost`
3. Configure the webhook to send `tracker.created` events

### PrintNode Setup

1. Get your PrintNode API key from the [PrintNode Dashboard](https://app.printnode.com/app/api/keys)
2. Find your printer ID by running:
   ```python
   from app.printnode.printer import get_printer_info
   printers = get_printer_info()  # This will list all available printers
   ```

## 🚀 Running the Application

### Development
```bash
python -m app.main
```

### Production
For production deployment, use a WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app.main:create_app()"
```

## 📡 API Endpoints

### Health Check
```
GET /health
```
Returns the application health status.

### EasyPost Webhook
```
POST /webhook/easypost
```
Receives EasyPost webhook events. Processes `tracker.created` events to automatically print shipping labels.

## 🔄 Workflow

1. **Webhook Received**: EasyPost sends a `tracker.created` webhook
2. **Tracker Processing**: System retrieves tracker details from EasyPost
3. **Shipment Lookup**: Finds associated shipment using tracking code
4. **Label Download**: Downloads the shipping label from EasyPost
5. **Label Conversion**: Converts label format if needed (PDF/ZPL/EPL)
6. **Printing**: Sends label to PrintNode for automatic printing

## 📝 Logging

The application provides comprehensive logging:

- **Console Output**: Real-time label information and print job status
- **File Logging**: Webhook requests are saved to `webhook_logs/` directory
- **Structured Logs**: All API interactions and errors are logged

## 🔧 Troubleshooting

### Common Issues

1. **Missing API Keys**:
   - Ensure all required environment variables are set
   - Check that API keys are valid and have proper permissions

2. **Printer Not Found**:
   - Verify printer ID is correct
   - Check that printer is online and accessible via PrintNode

3. **Label Download Failures**:
   - Check EasyPost API permissions
   - Verify shipment has an associated label

4. **Webhook Not Receiving Events**:
   - Ensure webhook URL is publicly accessible
   - Check EasyPost webhook configuration
   - Verify webhook endpoint URL and method

### Debug Mode

Enable debug mode for detailed logging:
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

## 🔒 Security

- **HMAC Verification**: Enable webhook signature verification (optional)
- **Environment Variables**: Store sensitive data in environment variables
- **HTTPS**: Use HTTPS in production for webhook endpoints

## 📚 Project Structure

```
label_automation-main/
├── app/
│   ├── config.py           # Application configuration
│   ├── main.py            # Flask application factory
│   ├── converter/         # Label format conversion
│   ├── easypost/          # EasyPost API integration
│   ├── handlers/          # Event processing logic
│   ├── printnode/         # PrintNode API integration
│   ├── utils/             # Utility functions
│   └── webhook/           # Webhook handling
├── requirements.txt       # Python dependencies
├── .env                  # Environment configuration template
└── README.md             # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

[Add your license information here]

## 🆘 Support

For support and questions:
- Check the troubleshooting section above
- Review application logs for error details
- Open an issue in the repository 