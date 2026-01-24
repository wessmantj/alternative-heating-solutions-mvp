import os
from datetime import timedelta

class Config:
    
    # database variable
    DATABASE_PATH = 'leads.db'
    

    # flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-later'

    # business + notification settings
    BUSINESS_NAME = "Alternative Heating Solutions" 
    BUSINESS_PHONE = "XXX-XXX-XXXX"
    PERSONAL_PHONE = "508-328-9372"
    TWILIO_PHONE = "XXX-XXX-XXXX"

    # auto-text settings
    RESPONSE_TIME_HOURS = 3
    DUPLICATE_TEXT_WINDOW = timedelta(hours=24) # don't text back same number within 24hrs