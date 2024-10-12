import requests
from icalendar import Calendar
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

def fetch_and_parse_ical(ical_url):
    try:
        # Fetch the iCalendar file
        response = requests.get(ical_url)

        if response.status_code == 200:
            # Parse the iCalendar file
            ical_data = response.content
            calendar = Calendar.from_ical(ical_data)

            # Extract events and other details
            events = []
            for component in calendar.walk():
                if component.name == "VEVENT":  # Look for events
                    event_summary = component.get('summary')

                    # Extract start time (always exists)
                    event_start = component.get('dtstart').dt

                    # Extract end time (may not exist)
                    event_end = component.get('dtend')
                    if event_end is not None:
                        event_end = event_end.dt
                    else:
                        event_end = "No end time specified"  # Handle missing end time

                    # Extract description (optional)
                    event_description = component.get('description', '')

                    # Format the datetime objects
                    if isinstance(event_start, datetime):
                        event_start = event_start.strftime('%Y-%m-%d %H:%M:%S')
                    if isinstance(event_end, datetime):
                        event_end = event_end.strftime('%Y-%m-%d %H:%M:%S')

                    events.append({
                        'summary': event_summary,
                        'start': event_start,
                        'end': event_end,
                        'description': event_description
                    })
            return events
        else:
            print(f"Failed to fetch iCalendar file. Status code: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the iCalendar file: {e}")
        return None

@app.route('/fetch_events', methods=['GET'])
def fetch_events():
    ical_url = request.args.get('ical_url')  # Get the iCalendar URL from query parameters
    if not ical_url:
        return jsonify({'error': 'iCalendar URL is required.'}), 400

    events = fetch_and_parse_ical(ical_url)
    
    if events:
        return jsonify(events), 200
    else:
        return jsonify({'error': 'No events found or failed to retrieve the calendar.'}), 404

if __name__ == '__main__':
    app.run(debug=True)
