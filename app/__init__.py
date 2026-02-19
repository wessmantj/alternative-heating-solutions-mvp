import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from config import Config
from twilio.rest import Client


def create_app():
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')
    app.config.from_object(Config)

    # Initialize Twilio client and attach to app
    app.twilio_client = Client(
        app.config['TWILIO_ACCOUNT_SID'],
        app.config['TWILIO_AUTH_TOKEN']
    )

    # Register blueprints
    from app.routes.dashboard import dashboard_bp
    from app.routes.webhooks import webhooks_bp
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(webhooks_bp)

    # Initialize database
    from app.services.database import init_db
    with app.app_context():
        init_db()

    return app