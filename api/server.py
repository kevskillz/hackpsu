from flask import Flask, request, jsonify
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import requests
from ics import Calendar

app = Flask(__name__)

# MongoDB connection setup
uri = "mongodb+srv://cjgiles8:hackpsu24@cluster0.7cwrg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'), tlsAllowInvalidCertificates=True)

print(client)
# Ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

# Access your database and collections
# db = client['Cluster0']  # Ensure this is your database name
assignments_collection = client['Cluster0']['Assignments']  # Ensure this is your assignments collection name
events_collection = client['Cluster0']['Events']  # Ensure this is your events collection name

# OpenAI API token
API_TOKEN = 'Y5VS2VVKF3S9NHD6TFKECPFNZYC8KHOR0SPKS7FXGK4J0RC9IINLYEVGXSBA5X8J'

# Function to get a chat completion from OpenAI API
def get_chat_completion(user_input):
    url = 'https://jamsapi.hackclub.dev/openai/chat/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_TOKEN}'
    }
    data = {
        'model': 'gpt-4o-mini',
        'messages': [
            {
                'role': 'user',
                'content': user_input
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        response_data = response.json()
        return response_data['choices'][0]['message']['content']
    else:
        return f"Error: {response.status_code}, {response.text}"
    
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
    file = request.files['file']
    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request'}), 400
    
    print(request.files)
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    
    if not file.filename.endswith('.ics'):
        return jsonify({'message': 'Invalid file type. Please upload an .ics file.'}), 400
    
    try:
        # Read the file content in memory
        file_content = file.read().decode('utf-8')
        events = read_ics_file(file_content)
        print(events)

        return jsonify({'filename': file.filename, 'events': events}), 200
    except Exception as e:
        print(e)

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

@app.route('/')
def home():
    return "Welcome to the AI Calendar/Scheduler!"

# Add assignment
@app.route('/add_assignment/<user_id>', methods=['POST'])
def add_assignment(user_id):
    data = request.json
    
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    assignment_name = data.get('title')
    due_date = data.get('due_date')
    priority = data.get('priority')
    
    if not assignment_name or not due_date or not priority:
        return jsonify({'error': 'Missing required fields'}), 400

    assignment = {
        'userId': user_id,
        'title': assignment_name,
        'due_date': due_date,
        'priority': priority,
        'hours_to_complete': data.get('hours_to_complete')
    }

    try:
        assignments_collection.insert_one(assignment)
        print(f"Inserted assignment: {assignment}")
    except Exception as e:
        return jsonify({'error': f'Failed to insert assignment: {e}'}), 500

    return jsonify({'message': 'Assignment added successfully', 'assignment': assignment}), 201

# Add event
@app.route('/add_event/<user_id>', methods=['POST'])
def add_event(user_id):
    data = request.json
    
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    event_name = data.get('title')
    start_time = data.get('start')
    end_time = data.get('end')
    
    if not event_name or not start_time or not end_time:
        return jsonify({'error': 'Missing required fields'}), 400

    event = {
        'userId': user_id,
        'title': event_name,
        'start': start_time,
        'end': end_time
    }

    # try:
    events_collection.insert_one(event)
    print(f"Inserted event: {event}")
    # except Exception as e:
    #     return jsonify({'error': f'Failed to insert event: {e}'}), 500

    return jsonify({'message': 'Event added successfully', 'event': event}), 201

# Get assignments
@app.route('/get_assignments/<user_id>', methods=['GET'])
def get_assignments(user_id):
    try:
        assignments = list(assignments_collection.find({'userId': user_id}))
        for assignment in assignments:
            assignment['_id'] = str(assignment['_id'])  # Convert ObjectId to string
        print((assignments))
        return jsonify(assignments), 200
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve assignments: {e}'}), 500

# Get events
@app.route('/get_events/<user_id>', methods=['GET'])
def get_events(user_id):
    try:
        events = list(events_collection.find({'userId': user_id}))
        for event in events:
            event['_id'] = str(event['_id'])  # Convert ObjectId to string
        print((events))
        return jsonify(events), 200
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve events: {e}'}), 500

# Schedule optimization route
@app.route('/schedule', methods=['POST'])
def schedule():
    data = request.json

    calendar_events_input = data.get('calendar_events')
    assignments_input = data.get('assignments')
    from datetime import datetime

    # Current datetime
    current_datetime = datetime.now().isoformat()
    if calendar_events_input and assignments_input:
        prompt = f"""
        You are a scheduling assistant. Given the following calendar events and assignments, generate an optimal schedule of events.
        It is currenly {current_datetime}.

        Calendar Events (fixed):
        {calendar_events_input}

        Assignments (to be optimized):
        {assignments_input}

        Ensure that:
        - All assignments are completed by their due dates.
        - Higher priority assignments are scheduled earlier.
        - Calendar events remain fixed in their time slots, while assignments are scheduled around them.
        - Each event/assignment should only appear once in the generated schedule.

        Return an optimized schedule of assignments & calendar events with the following format without any other text. Ensure each id is only showing up ONCE.
        [{{ "id": , "title": , "start": , "end":,}},... ]
        """
        
        response = get_chat_completion(prompt)
        print(response)
        return jsonify(response.replace('\n', '').replace('    ','')), 200
    else:
        return jsonify({'error': 'Please provide valid calendar events and assignments!'}), 400

if __name__ == '__main__':
    app.run(debug=True)
