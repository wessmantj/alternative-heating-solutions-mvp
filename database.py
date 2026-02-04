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
            original_message TEXT,
            voicemail_url TEXT,
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
             has_voicemail: bool = False,
             voicemail_url: Optional[str] = None,
             original_message: Optional[str]= None) -> Optional[int]:
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
            customer_phone, name, address, service, has_voicemail, voicemail_url, original_message)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (customer_phone, name, address, service, has_voicemail, voicemail_url, original_message))

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

def update_lead_status(lead_id: int, status: str) -> bool:
    """
    Update a lead's status
    
    Args:
        lead_id: The lead's database ID
        status: New status ('new', 'called_back', 'scheduled', 'closed')
    
    Returns:
        bool: True if successful, False otherwise
    """
    connect = sqlite3.connect(Config.DATABASE_PATH)
    cursor = connect.cursor()

    cursor.execute('''
        UPDATE leads
        SET status = ?
        WHERE id = ?
        ''', (status, lead_id))
    
    rows_affected = cursor.rowcount

    connect.commit()
    connect.close()

    return rows_affected > 0


def should_send_text(phone_number: str) -> bool:
    """
    Check if we should send auto-text to this number
    Prevents duplicate texts within 24 hours
    
    Args:
        phone_number: Customer's phone number
    
    Returns:
        bool: True if we should text, False if already texted recently
    """
    connect = sqlite3.connect(Config.DATABASE_PATH)
    cursor = connect.cursor()

    cursor.execute('''
        SELECT * FROM call_log
        WHERE phone_number = ?
        AND texted_at > datetime('now', '-24 hours')
    ''', (phone_number,))

    recent_text = cursor.fetchone()

    connect.close()

    return recent_text is None


def log_autotext(phone_number: str) -> None:
    """
    Log that we sent an auto-text to this number
    
    Args:
        phone_number: Customer's phone number
    """
    
    connect = sqlite3.connect(Config.DATABASE_PATH)
    cursor = connect.cursor()
    
    cursor.execute('''
        INSERT INTO call_log (phone_number)
        VALUES (?)
    ''', (phone_number,))
    
    connect.commit()
    connect.close()


def get_lead_by_id(lead_id: int) -> Optional[dict]:
    """
    Get a specific lead by ID
    
    Args:
        lead_id: The lead's database ID
    
    Returns:
        Dictionary with lead info, or None if not found
    """
    
    connect = sqlite3.connect(Config.DATABASE_PATH)
    connect.row_factory = sqlite3.Row

    cursor = connect.cursor()

    cursor.execute('''
        SELECT * FROM leads
        WHERE id = ? 
    ''', (lead_id,))

    row = cursor.fetchone()

    connect.close()

    if row:
        return dict(row)
    else:
        return None
    

def add_lead_note(lead_id: int, note: str) -> bool:
    """
    Add a note to a lead (appends to existing notes)
    
    Args:
        lead_id: The lead's database ID
        note: Note text to add
    
    Returns:
        bool: True if successful, False otherwise
    """

    connect = sqlite3.connect(Config.DATABASE_PATH)
    cursor = connect.cursor()

    cursor.execute('SELECT notes FROM leads WHERE id = ?', (lead_id,))
    row = cursor.fetchone()

    if row is None:
        # if row doesn't exist
        connect.close()
        return False

    existing_notes = row[0] or ""
    if existing_notes:
        updated_notes = existing_notes + "\n" + note
    else:
        updated_notes = note
    
    cursor.execute('''
        UPDATE leads
        SET notes = ?
        WHERE id = ?
    ''', (updated_notes, lead_id))

    connect.commit()
    connect.close()

    return True


def get_stats() -> dict:
    """
    Get statistics for dashboard
    Counts today's leads and breaks down by status
    
    Returns:
        Dictionary with lead counts:
        {
            'total_leads_today': 8,
            'new': 5,
            'called_back': 2,
            'scheduled': 1,
            'closed': 0
        }
    """

    connect = sqlite3.connect(Config.DATABASE_PATH)
    cursor = connect.cursor()

    cursor.execute('''
        SELECT COUNT(*) FROM leads
        WHERE DATE(created_at) = DATE('now')
    ''')

    total_today = cursor.fetchone()[0]

    cursor.execute('''
        SELECT status, COUNT(*) FROM leads
        WHERE DATE(created_at) = DATE('now')
        GROUP BY status
    ''')

    status_counts = cursor.fetchall()

    connect.close()

    stats = {
        'total_leads_today': total_today,
        'new': 0,
        'called_back': 0,
        'scheduled': 0,
        'closed': 0
    }

    for status, count in status_counts:
        stats[status] = count

    return stats