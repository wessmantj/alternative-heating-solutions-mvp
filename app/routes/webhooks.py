from flask import Blueprint, request, current_app
from twilio.twiml.voice_response import VoiceResponse
from twilio.twiml.messaging_response import MessagingResponse
from app.services.database import (
    add_lead, 
    get_recent_leads, 
    add_lead_note, 
    update_lead_original_message, 
    get_lead_by_id
)
from app.services.parser import parse_customer_response
from app import Config

webhooks_bp = Blueprint('webhooks', __name__, url_prefix='/webhooks')


@webhooks_bp.route('/twilio/voice', methods=['POST'])
def handle_incoming_call():
    """Handle incoming calls - play greeting and record voicemail"""
    response = VoiceResponse()
    
    # Greeting
    response.say(
        f"Thank you for calling {Config.BUSINESS_NAME}. "
        "We're currently unavailable. Please leave a message after the beep.",
        voice='alice'
    )
    
    # Record voicemail
    response.record(
        timeout=3,
        transcribe=True,
        transcribe_callback='/webhooks/twilio/transcription',
        action='/webhooks/twilio/voicemail-complete',
        max_length=120  # 2 minutes max
    )
    
    return str(response), 200, {'Content-Type': 'text/xml'}


@webhooks_bp.route('/twilio/voicemail-complete', methods=['POST'])
def voicemail_complete():
    """Called after voicemail is recorded"""
    from_number = request.form.get('From')
    recording_url = request.form.get('RecordingUrl')
    
    print(f"[VOICEMAIL] Received from {from_number}")
    print(f"[VOICEMAIL] Recording URL: {recording_url}")
    
    # Add to database 
    lead_id = add_lead(
        customer_phone=from_number,
        has_voicemail=True,
        voicemail_url=recording_url
    )
    
    print(f"[VOICEMAIL] Created lead ID: {lead_id}")
    
    # Text dad immediately
    send_dad_notification(lead_id, from_number, "New voicemail")
    
    # Respond to Twilio
    response = VoiceResponse()
    response.say("Thank you. We'll call you back soon.", voice='alice')
    response.hangup()
    
    return str(response), 200, {'Content-Type': 'text/xml'}


@webhooks_bp.route('/twilio/transcription', methods=['POST'])
def handle_transcription():
    """Called when voicemail transcription is ready (can take 2-5 minutes)"""
    from_number = request.form.get('From')
    transcription_text = request.form.get('TranscriptionText')
    recording_sid = request.form.get('RecordingSid')
    
    print(f"[TRANSCRIPTION] Received for {from_number}")
    print(f"[TRANSCRIPTION] Text: {transcription_text}")
    
    # Find the lead by phone number and update with transcription
    leads = get_recent_leads(hours=1)  # Look at last hour
    
    for lead in leads:
        if lead['customer_phone'] == from_number and lead['has_voicemail']:
            # Update with transcription
            update_lead_original_message(lead['id'], transcription_text)
            
            # Also add as a note
            add_lead_note(lead['id'], f"Voicemail transcription: {transcription_text}")
            
            print(f"[TRANSCRIPTION] Updated lead {lead['id']}")
            
            # Send updated notification to dad with transcription
            send_dad_notification(lead['id'], from_number, "Voicemail transcribed", include_transcription=True)
            break
    
    return '', 200


@webhooks_bp.route('/twilio/sms', methods=['POST'])
def handle_incoming_sms():
    """Handle incoming SMS from customers (after toll-free verification)"""
    from_number = request.form.get('From')
    message_body = request.form.get('Body')
    
    print(f"[SMS] Received from {from_number}: {message_body}")
    
    # Parse the message
    name, address, service = parse_customer_response(message_body)
    
    print(f"[SMS] Parsed - Name: {name}, Address: {address}, Service: {service}")
    
    # Add to database
    lead_id = add_lead(
        customer_phone=from_number,
        name=name,
        address=address,
        service=service,
        original_message=message_body
    )
    
    print(f"[SMS] Created lead ID: {lead_id}")
    
    # Notify dad
    send_dad_notification(lead_id, from_number, "New lead via SMS")
    
    # Respond to customer 
    response = MessagingResponse()
    response.message(
        f"Thank you! We received your information and will call you back "
        f"within {Config.RESPONSE_TIME_HOURS} hours from {Config.BUSINESS_PHONE}."
    )
    
    return str(response), 200, {'Content-Type': 'text/xml'}


def send_dad_notification(lead_id, phone_number, message_type, include_transcription=False):
    """
    Send SMS notification to dad
    
    Args:
        lead_id: ID of the lead
        phone_number: Customer's phone number
        message_type: Type of notification (e.g., "New voicemail")
        include_transcription: Whether to include transcription text
    """
    lead = get_lead_by_id(lead_id)
    
    if not lead:
        print(f"[NOTIFICATION] Lead {lead_id} not found")
        return
    
    # Build notification text
    notification_text = f"{message_type.upper()}\n\n"
    notification_text += f"From: {phone_number}\n"
    
    if lead.get('name'):
        notification_text += f"Name: {lead['name']}\n"
    
    if lead.get('address'):
        notification_text += f"Address: {lead['address']}\n"
    
    if lead.get('service'):
        notification_text += f"Service: {lead['service']}\n"
    
    if include_transcription and lead.get('original_message'):
        # Truncate to 200 chars to keep SMS short
        transcription = lead['original_message'][:200]
        if len(lead['original_message']) > 200:
            transcription += "..."
        notification_text += f"\nTranscription:\n{transcription}\n"
    
    if lead.get('voicemail_url'):
        notification_text += f"\nListen: {lead['voicemail_url']}\n"
    
    notification_text += f"\nView dashboard to manage leads"
    
    # Send to dad
    try:
        twilio_client = current_app.twilio_client
        message = twilio_client.messages.create(
            body=notification_text,
            from_=Config.TWILIO_PHONE,
            to=Config.PERSONAL_PHONE
        )
        print(f"[NOTIFICATION] Sent to dad: {message.sid}")
    except Exception as e:
        print(f"[NOTIFICATION] Failed to send: {e}")