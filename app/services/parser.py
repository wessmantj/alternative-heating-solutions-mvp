"""
Parse customer text message responses
"""
from typing import Tuple, Optional

def parse_customer_response(message: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Extract name, address, and service from customer's text message
    
    Handles various formats:
    - Line by line: "John Smith\n123 Main St\nCleaning"
    - With labels: "Name: John\nAddress: 123 Main\nService: Cleaning"
    - Mixed formats
    
    Args:
        message: The customer's text message
    
    Returns:
        Tuple of (name, address, service) - any can be None if not found
    """
    
    # split message into lines
    lines = message.split('\n')

    # remove whitespace
    lines = [line.strip() for line in lines if line.strip()]

    name = None
    address = None
    service = None

    # identify name, address, service
    for line in lines:
        line_lower = line.lower()
    
        if 'name' in line_lower:
            if ':' in line:
                name = line.split(':', 1)[1].strip()

        elif 'address' in line_lower:
            if ':' in line:
                address = line.split(':', 1)[1].strip()

        elif 'service' in line_lower or 'need' in line_lower:
            if ':' in line:
                service = line.split(':', 1)[1].strip()
        
        elif not name:
            name = line
        elif not address:
            address = line
        elif not service:
            service = line

    
    return (name, address, service)