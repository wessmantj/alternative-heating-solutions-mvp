import sqlite3
from config import Config

def init_db():
    '''
    Initialize the database with the required tables
    Creates leads and call_log tables if they don't exist
    '''

    # connects to database
    connect = sqlite3.connect(Config.DATABASE_PATH)

    # create a cursor
    cursor = connect.cursor()

    # execute SQL to create leads table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_phone TEXT NOT NULL,
            name TEXT,
            address TEXT,
            service TEXT,
            has_voicemail BOOLEAN DEFAULT 0,
            status TEXT DEFAULT 'new',
            created_ad TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT
        )
    ''')
    # execute SQL to create call_log table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS call_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT NOT NULL,
            texted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    connect.commit()

    connect.close()

    print("Database initialized.")



def add_lead(phone, name, address, service):
    # Insert new lead
    pass

def get_todays_leads():
    # Get all leads from today
    pass

def mark_as_called(lead_id):
    # Update status to 'called_back'
    pass

def should_send_text(phone):
    # Check if we texted this number in last 24hrs
    pass