from flask import Flask
from app.webhook.router import webhook_bp
from app.management.api import management_bp
from app.config import Config
from app.utils.logger import setup_logger

def create_app(config_class=Config):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Setup logging
    setup_logger()
    
    # Register blueprints
    app.register_blueprint(webhook_bp, url_prefix='/webhook')
    app.register_blueprint(management_bp, url_prefix='/manage')
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Simple health check endpoint"""
        return {'status': 'healthy'}, 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=app.config['PORT'])