from flask import Flask, request, jsonify
from icalendar import Calendar
from datetime import datetime
import pytz
import os
import tkinter as tk
from tkinter import filedialog

app = Flask(__name__)
events = []  # Global variable to store events

def fetch_and_parse_ical(file_path):
    """Fetch and parse the .ics file, returning a list of events."""
    try:
        # Check if the file exists
        if not os.path.isfile(file_path):
            print("File not found.")
            return None
        
        # Read the iCalendar file from the local file system
        with open(file_path, 'rb') as file:
            ical_data = file.read()
            calendar = Calendar.from_ical(ical_data)

            # Debug: Print calendar data
            print("\nCalendar Data:")
            print(ical_data.decode('utf-8'))  # Print raw iCalendar data

            # Extract events
            extracted_events = []
            for component in calendar.walk():
                if component.name == "VEVENT":  # Look for events
                    event_summary = component.get('summary')
                    
                    # Extract start time (always exists)
                    event_start = component.get('dtstart').dt
                    
                    # Ensure event_start is timezone-aware (convert if necessary)
                    if event_start.tzinfo is None:
                        event_start = pytz.utc.localize(event_start)  # Assume UTC if no timezone provided
                    
                    # Extract end time (may not exist)
                    event_end = component.get('dtend')
                    if event_end is not None:
                        event_end = event_end.dt
                    else:
                        event_end = "No end time specified"  # Handle missing end time
                    
                    # Extract description (optional)
                    event_description = component.get('description', '')

                    # Format the datetime objects
                    event_start_str = event_start.strftime('%Y-%m-%d %H:%M:%S')
                    if isinstance(event_end, datetime):
                        event_end_str = event_end.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        event_end_str = event_end

                    extracted_events.append({
                        'summary': event_summary,
                        'start': event_start_str,
                        'end': event_end_str,
                        'description': event_description
                    })

            # Sort events by start time
            extracted_events.sort(key=lambda x: x['start'])
            return extracted_events

    except Exception as e:
        print(f"Error reading or parsing the iCalendar file: {e}")
        return None

def upload_file():
    """Open a file dialog to select a .ics file and return its path."""
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(
        title="Select an ICS file",
        filetypes=[("ICS Files", "*.ics")],
    )
    return file_path

@app.route('/upload', methods=['POST'])
def upload():
    """Handle the upload of the ICS file and parse it."""
    global events
    file_path = upload_file()

    # Ensure a file was selected
    if file_path:
        # Process the .ics file
        events = fetch_and_parse_ical(file_path)

        if events:
            return jsonify({'events': events}), 200
        else:
            return jsonify({'error': 'No events found or failed to retrieve the calendar.'}), 404
    else:
        return jsonify({'error': 'No file selected.'}), 400

@app.route('/events', methods=['GET'])
def get_events():
    """Return the list of parsed events as JSON."""
    if events:
        return jsonify({'events': events}), 200
    else:
        return jsonify({'error': 'No events available.'}), 404

if __name__ == "__main__":
    app.run(debug=True)
