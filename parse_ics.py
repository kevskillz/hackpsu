from flask import Flask, request, jsonify
from ics import Calendar

app = Flask(__name__)

def read_ics_file(file_content):
    """Read an ICS file content and return a list of events."""
    calendar = Calendar(file_content)

    # Process events into a list
    events_list = []
    for event in calendar.events:
        event_details = {
            'name': event.name,
            'begin': event.begin.isoformat(),  # Convert to ISO format for better readability
            'end': event.end.isoformat(),        # Convert to ISO format
            'description': event.description or 'No description',  # Handle missing descriptions
            'location': event.location or 'No location',           # Handle missing locations
        }
        events_list.append(event_details)

    return events_list

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and return its content."""
    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    
    if not file.filename.endswith('.ics'):
        return jsonify({'message': 'Invalid file type. Please upload an .ics file.'}), 400
    
    try:
        # Read the file content in memory
        file_content = file.read().decode('utf-8')
        events = read_ics_file(file_content)

        return jsonify({'filename': file.filename, 'events': events}), 200
    except Exception as e:
        return jsonify({'message': f'Error reading file: {str(e)}'}), 500

@app.route('/fetch_events', methods=['GET'])
def fetch_events():
    """Fetch events from the specified ICS file content."""
    file_path = request.args.get('file_path')  # Get the file path from query parameters
    if not file_path:
        return jsonify({'error': 'File path is required.'}), 400

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
            events = read_ics_file(file_content)
            return jsonify(events), 200
    except FileNotFoundError:
        return jsonify({'error': 'File not found.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
