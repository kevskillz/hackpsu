from flask import Flask, request, jsonify
from pymongo import MongoClient
from pymongo.server_api import ServerApi

app = Flask(__name__)

# MongoDB connection setup
uri = "mongodb+srv://cjgiles8:hackpsu24@cluster0.7cwrg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'), tlsAllowInvalidCertificates=True)

# Ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

# Access your database and collections
db = client['Cluster0']  # Ensure this is your database name
assignments_collection = db['Assignments']  # Ensure this is your assignments collection name
events_collection = db['Events']  # Ensure this is your events collection name

@app.route('/')
def home():
    return "Welcome to the AI Calendar/Scheduler!"

@app.route('/add_assignment/<user_id>', methods=['POST'])
def add_assignment(user_id):
    data = request.json
    
    # Check if the request contains JSON data
    if not data:
        return jsonify({'error': 'No input data provided'}), 400
    
    # Extract assignment details from the request
    assignment_name = data.get('name')
    due_date = data.get('due_date')
    priority = data.get('priority')
    
    # Validate the input
    if not assignment_name or not due_date or not priority:
        return jsonify({'error': 'Missing required fields'}), 400

    # Create a new assignment document
    assignment = {
        'userId': user_id,  # Use userId from the URL parameter
        'name': assignment_name,
        'due_date': due_date,
        'priority': priority
    }

    # Insert the assignment into the collection
    try:
        assignments_collection.insert_one(assignment)
        print(f"Inserted assignment: {assignment}")  # Log the inserted assignment
    except Exception as e:
        return jsonify({'error': f'Failed to insert assignment: {e}'}), 500

    return jsonify({'message': 'Assignment added successfully', 'assignment': assignment}), 201

@app.route('/add_event/<user_id>', methods=['POST'])
def add_event(user_id):
    data = request.json
    
    # Check if the request contains JSON data
    if not data:
        return jsonify({'error': 'No input data provided'}), 400
    
    # Extract event details from the request
    event_name = data.get('name')
    start_time = data.get('start')
    end_time = data.get('end')
    
    # Validate the input
    if not event_name or not start_time or not end_time:
        return jsonify({'error': 'Missing required fields'}), 400

    # Create a new event document
    event = {
        'userId': user_id,  # Use userId from the URL parameter
        'name': event_name,
        'start': start_time,
        'end': end_time
    }

    # Insert the event into the collection
    try:
        events_collection.insert_one(event)
        print(f"Inserted event: {event}")  # Log the inserted event
    except Exception as e:
        return jsonify({'error': f'Failed to insert event: {e}'}), 500

    return jsonify({'message': 'Event added successfully', 'event': event}), 201

@app.route('/get_assignments/<user_id>', methods=['GET'])
def get_assignments(user_id):
    try:
        assignments = list(assignments_collection.find({'userId': user_id}))
        for assignment in assignments:
            assignment['_id'] = str(assignment['_id'])  # Convert ObjectId to string
        return jsonify(assignments), 200
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve assignments: {e}'}), 500

@app.route('/get_events/<user_id>', methods=['GET'])
def get_events(user_id):
    try:
        events = list(events_collection.find({'userId': user_id}))
        for event in events:
            event['_id'] = str(event['_id'])  # Convert ObjectId to string
        return jsonify(events), 200
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve events: {e}'}), 500

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True)