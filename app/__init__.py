import os
from flask import Flask
from twilio.rest import Client
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    # database
    DATABASE_PATH = 'leads.db'
    # flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-later')
    # business settings (not sensitive)
    BUSINESS_NAME = "Alternative Heating Solutions"
    BUSINESS_PHONE = "+1XXXXXXXXXX"
    TWILIO_PHONE = "+18886038816"
    # sensitive — pulled from .env
    PERSONAL_PHONE = os.getenv('PERSONAL_PHONE')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    # auto-text settings
    RESPONSE_TIME_HOURS = 3
    DUPLICATE_TEXT_WINDOW = timedelta(hours=24)


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