from typing import Tuple, Optional
from config import Config
from datetime import datetime


def format_autotext_message() -> str:
    """
    Generate the auto-text sent when customer doesn't leave voicemail
    
    Returns:
        str: The message text
    """
    message = f"""Thanks for reaching out to {Config.BUSINESS_NAME}.
    We're unavailable for a call right now, but please reply with:
     - Your name
     - Your address
     - Your inquiry
    
    We'll call you back from {Config.BUSINESS_PHONE} within {Config.RESPONSE_TIME_HOURS} hours.
    
    Thank you for choosing {Config.BUSINESS_NAME}."""

    return message


def format_voicemail_confirmation(service: Optional[str] = None) -> str:
    """
    Generate confirmation text when customer leaves voicemail
    
    Args:
        service: What they need (optional)
    
    Returns:
        str: The confirmation message
    """
    if service:
        confirmation_message = (
            f"Thank you for reaching out to {Config.BUSINESS_NAME}.\n"
            f"We got your voicemail about {service}. We'll call you back within {Config.RESPONSE_TIME_HOURS} hours.\n\n"
            f"Thank you for choosing {Config.BUSINESS_NAME}."
    )
    else:
        confirmation_message = (
            "Thank you for reaching out to {Config.BUSINESS_NAME}.\n"
            f"We're unable to take your call but will respond to your voicemail within {Config.RESPONSE_TIME_HOURS} hours.\n\n"
            f"Thank you for choosing {Config.BUSINESS_NAME}."
    )

    return confirmation_message


def format_lead_notification(lead: dict) -> str:
    """
    Format notification text to send to dad
    
    Args:
        lead: Dictionary with lead info from database
    
    Returns:
        str: Formatted notification
    """
    name = lead.get('name', 'No name provided')
    phone = lead.get('customer_phone')
    address = lead.get('address', 'No address provided')
    service = lead.get('service', 'No service provided')
    timestamp = lead.get('created_at')

    time_str = format_time(timestamp)

    lead_notification = (
        f"NEW LEAD - {service}\n\n"
        f"{name}\n"
        f"📞 {phone}\n"
        f"📍 {address}\n\n"
        f"Time Received: {time_str}"
    )

    return lead_notification


def format_time(timestamp) -> str:
    """
    Convert timestamp to readable format
    
    Args:
        timestamp: datetime object or ISO string
    
    Returns:
        str: Formatted time like "2:34 PM"
    """
    if isinstance(timestamp, str):
        dt = datetime.fromisoformat(timestamp)
    else:
        dt = timestamp

    return dt.strftime("%-I:%M %p")
