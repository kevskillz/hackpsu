from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Replace 'YOURTOKEN' with your actual token
API_TOKEN = 'Y5VS2VVKF3S9NHD6TFKECPFNZYC8KHOR0SPKS7FXGK4J'

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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        calendar_events_input = request.form.get('calendar_events')
        assignments_input = request.form.get('assignments')
        
        if calendar_events_input and assignments_input:
            # Construct the prompt
            prompt = f"""
            You are a scheduling assistant. Given the following calendar events and assignments, generate an optimal schedule of events.

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
            [{{ "id": , "name": , "start_date": , "start_time":, "end_date":, "end_time":}},... ]
            """
            
            # Get the response from the OpenAI API
            response = get_chat_completion(prompt)

            # Render the response in the template
            return render_template('index.html', response=response, calendar_events=calendar_events_input, assignments=assignments_input)
        else:
            error_message = "Please enter valid calendar events and assignments in JSON format!"
            return render_template('index.html', error=error_message)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
