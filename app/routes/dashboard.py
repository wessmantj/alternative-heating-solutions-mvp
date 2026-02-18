from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from app.services.database import (
    get_recent_leads,
    get_stats,
    get_lead_by_id,
    update_lead_status,
    add_lead_note
)

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def dashboard():
    """Main dashboard showing last 72 hours of leads"""
    leads = get_recent_leads(hours=72)
    stats = get_stats()
    return render_template('dashboard.html', leads=leads, stats=stats)


@dashboard_bp.route('/toggle-status/<int:lead_id>')
def toggle_status(lead_id):
    """Toggle lead status between new and called_back"""
    lead = get_lead_by_id(lead_id)
    if lead:
        if lead['status'] in ('called_back', 'scheduled'):
            update_lead_status(lead_id, 'new')
        else:
            update_lead_status(lead_id, 'called_back')
    return redirect(url_for('dashboard.dashboard'))


@dashboard_bp.route('/api/lead/<int:lead_id>')
def get_lead_json(lead_id):
    """Get lead data as JSON for modal"""
    lead = get_lead_by_id(lead_id)
    return jsonify(lead) if lead else (jsonify({'error': 'Not found'}), 404)


@dashboard_bp.route('/api/lead/<int:lead_id>/notes', methods=['POST'])
def save_lead_notes(lead_id):
    """Save notes for a lead"""
    data = request.get_json()
    notes = data.get('notes', '')
    success = add_lead_note(lead_id, notes)
    return jsonify({'success': success})