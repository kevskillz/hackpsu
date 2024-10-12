from flask import Flask, jsonify, request
from ics import Calendar

app = Flask(__name__)

def read_ics_file(file_path):
    # Open and read the .ics file
    with open(file_path, 'r', encoding='utf-8') as file:
        calendar = Calendar(file.read())
    
    # Process events into a list
    events_list = []
    for event in calendar.events:
        event_details = {
            'name': event.name,
            'begin': event.begin.isoformat(),  # Convert to ISO format for better readability
            'end': event.end.isoformat(),        # Convert to ISO format
            'description': event.description,
            'location': event.location,
        }
        events_list.append(event_details)

    return events_list

@app.route('/fetch_events', methods=['GET'])
def fetch_events():
    file_path = request.args.get('file_path')  # Get the file path from query parameters
    if not file_path:
        return jsonify({'error': 'File path is required.'}), 400

    try:
        events = read_ics_file(file_path)
        return jsonify(events), 200
    except FileNotFoundError:
        return jsonify({'error': 'File not found.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
