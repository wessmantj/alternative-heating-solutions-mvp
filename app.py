"""
Main Flask application
"""
from flask import Flask, render_template, redirect, url_for, request, jsonify
from database import get_todays_leads, update_lead_status, get_stats, init_db, get_lead_by_id, add_lead_note
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database on first run
with app.app_context():
    init_db()

@app.route('/')
def dashboard():
    """Main dashboard showing today's leads"""
    leads = get_todays_leads()
    stats = get_stats()
    return render_template('dashboard.html', leads=leads, stats=stats)

@app.route('/toggle-status/<int:lead_id>')
def toggle_status(lead_id):
    """Toggle lead status between new and called_back"""
    lead = get_lead_by_id(lead_id)
    
    if lead:
        # If called_back or scheduled, change back to new
        # If new, change to called_back
        if lead['status'] == 'called_back' or lead['status'] == 'scheduled':
            update_lead_status(lead_id, 'new')
        else:
            update_lead_status(lead_id, 'called_back')
    
    return redirect(url_for('dashboard'))

@app.route('/api/lead/<int:lead_id>')
def get_lead_json(lead_id):
    """Get lead data as JSON for modal"""
    lead = get_lead_by_id(lead_id)
    return jsonify(lead) if lead else jsonify({'error': 'Not found'}), 404

@app.route('/api/lead/<int:lead_id>/notes', methods=['POST'])
def save_lead_notes(lead_id):
    """Save notes for a lead"""
    data = request.get_json()
    notes = data.get('notes', '')
    
    # Use existing function
    success = add_lead_note(lead_id, notes)
    
    return jsonify({'success': success})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)