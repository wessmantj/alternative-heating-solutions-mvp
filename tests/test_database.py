from database import *

# Delete old database
import os
if os.path.exists('leads.db'):
    os.remove('leads.db')

# Test 1: Initialize
print("Test 1: Initialize database")
init_db()

# Test 2: Add leads
print("\nTest 2: Add leads")
id1 = add_lead("4015551111", "John Smith", "123 Main St", "cleaning")
id2 = add_lead("4015552222", "Jane Doe", "456 Oak Ave", "repair")
id3 = add_lead("4015553333")
print(f"Added leads: {id1}, {id2}, {id3}")

# Test 3: Get today's leads
print("\nTest 3: Get today's leads")
leads = get_todays_leads()
print(f"Found {len(leads)} leads")
for lead in leads:
    print(f"  {lead['id']}: {lead['name']}")

print("\nTest 4: Get lead by ID")
print(f"id1 value is: {id1}")
lead = get_lead_by_id(id1)
print(f"lead is: {lead}")

if lead:
    print(f"Lead {id1}: {lead['name']} - {lead['status']}")
else:
    print(f"ERROR: Lead {id1} not found!")

# Test 5: Update status
print("\nTest 5: Update status")
if lead:
    update_lead_status(id1, 'called_back')
    lead = get_lead_by_id(id1)
    print(f"Lead {id1} status now: {lead['status']}")

# Test 6: Add note
print("\nTest 6: Add note")
if lead:
    add_lead_note(id1, "Test note")
    lead = get_lead_by_id(id1)
    print(f"Notes: {lead['notes']}")

# Test 7: Text duplicate check
print("\nTest 7: Duplicate text check")
print(f"Can text: {should_send_text('4015551111')}")
log_autotext('4015551111')
print(f"Can text again: {should_send_text('4015551111')}")

# Test 8: Stats
print("\nTest 8: Statistics")
stats = get_stats()
print(stats)

print("\n All tests complete!")