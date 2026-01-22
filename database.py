import sqlite3
from config import Config
from typing import Optional, List

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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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



def add_lead(customer_phone: str,
             name: Optional[str] = None,
             address: Optional[str] = None,
             service: Optional[str] = None,
             has_voicemail: bool = False) -> int:
    """
    Add a new lead to the database
    
    Args:
        customer_phone: Customer's phone number (REQUIRED)
        name: Customer name (optional - can be None)
        address: Customer address (optional - can be None)
        service: Service they need (optional - can be None)
        has_voicemail: Whether they left voicemail (default False)
    
    Returns:
        int: ID of the newly created lead
    """
    
    connect = sqlite3.connect(Config.DATABASE_PATH)
    cursor = connect.cursor()

    cursor.execute('''
        INSERT INTO leads (
            customer_phone, name, address, service, has_voicemail)
        VALUES (?, ?, ?, ?, ?)
    ''', (customer_phone, name, address, service, has_voicemail))

    lead_id = cursor.lastrowid

    connect.commit()

    connect.close()

    return lead_id



def get_todays_leads() -> List[dict]:
    """
    Get all leads from today, sorted by most recent first
    
    Returns:
        List of dictionaries, each containing all lead info
    """

    connect = sqlite3.connect(Config.DATABASE_PATH)

    # get results in dict format instead of tuples
    connect.row_factory = sqlite3.Row

    cursor = connect.cursor()

    cursor.execute('''
        SELECT * FROM leads
        WHERE DATE(created_at) = DATE('now')
        ORDER BY created_at DESC
    ''')

    # get all results
    rows = cursor.fetchall()

    # convert to list of dictionaries by iterating through the rows
    leads = [dict(row) for row in rows]

    connect.close()

    return leads

def mark_as_called(lead_id):
    # Update status to 'called_back'
    pass

def should_send_text(phone):
    # Check if we texted this number in last 24hrs
    pass