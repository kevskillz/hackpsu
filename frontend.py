import streamlit as st
from streamlit_calendar import calendar
import datetime
import requests
import json
from ics import Calendar


# Set page configuration
st.set_page_config(page_title="TimeTickler", page_icon="📆")
st.markdown("## TimeTickler 📆")
sched = ''
# Check if the user is logged in
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Create a login page if not logged in
if not st.session_state["logged_in"]:
    st.title("Login")

    # Login form
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        user = username
        st.session_state["logged_in"] = True
        st.session_state["user"] = username

        st.success("Logged in successfully!")
        st.rerun()
            
else:
    def read_ics_file_canvas(file_content):
        calendar = Calendar(file_content)

        # Process events into a list
        events_list = []
        for event in calendar.events:
            event_details = {
                'title': event.name,
                'due_date': event.begin.isoformat(),  # Convert to ISO format for better readability
                'priority': 'Medium',
                'hours_to_complete': 1 
            }
            events_list.append(event_details)
        if len(events_list) > 10:
            return events_list[:10]
        else: return events_list
    def read_ics_file_google(file_content):
        
        calendar = Calendar(file_content)

        # Process events into a list
        events_list = []
        for event in calendar.events:
            event_details = {
                'title': event.name,
                'start': event.begin.isoformat(),  # Convert to ISO format for better readability
                'end': event.end.isoformat(),  # Convert to ISO format for better readability
            }
            events_list.append(event_details)
        if len(events_list) > 10:
                    return events_list[:10]
        else: return events_list
         # Function to call the API and add an event for a given user
    def addEventToDB(event, user):
       
        try:
            # Make a POST request to your API to add an event
            url = f'http://127.0.0.1:5000/add_event/{user}'  # Replace with your actual API URL if needed
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=event, headers=headers)
            
            if response.status_code == 201:
                print(f"Event added successfully for user {user}")
                return response.json() # Return the JSON response from the API
            else:
                print(f"Error: Failed to add event for user {user}, Status Code: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception while adding event: {e}")
            return None
    

    # Function to call the API and add an assignment for a given user
    def addAssignmentToDB(assignment, user):
        try:
            # Make a POST request to your API to add an assignment
            url = f'http://127.0.0.1:5000/add_assignment/{user}'  # Replace with your actual API URL if needed
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=assignment, headers=headers)
            
            if response.status_code == 201:
                print(f"Assignment added successfully for user {user}")
                return response.json()  # Return the JSON response from the API
            else:
                print(f"Error: Failed to add assignment for user {user}, Status Code: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception while adding assignment: {e}")
            return None

        # Function to call the API and retrieve calendar events for a given user
    def getCalendarEventsFromDB(user):
        try:
            # Make a GET request to your API to fetch calendar events
            url = f'http://127.0.0.1:5000/get_events/{user}'  # Replace with your actual API URL if needed
            response = requests.get(url)
            
            if response.status_code == 200:
                print(response.json())
                return response.json()  # Return the JSON response from the API
            else:
                print(f"Error: Failed to retrieve calendar events for user {user}, Status Code: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception while retrieving calendar events: {e}")
            return None

    # Function to call the API and retrieve assignments for a given user
    def getAssignmentsFromUser(user):
        try:
            # Make a GET request to your API to fetch assignments
            url = f'http://127.0.0.1:5000/get_assignments/{user}'  # Replace with your actual API URL if needed
            response = requests.get(url)
            
            if response.status_code == 200:
                print(response.json())
                return response.json()  # Return the JSON response from the API
            else:
                print(f"Error: Failed to retrieve assignments for user {user}, Status Code: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception while retrieving assignments: {e}")
            return None

    def update():
        with st.spinner('Generating schedule...'):
            url = "http://127.0.0.1:5000/schedule"
            print(st.session_state['user'])
            user = st.session_state['user']
            data = {
                "calendar_events": json.dumps(getCalendarEventsFromDB(user)),
                "assignments": json.dumps(getAssignmentsFromUser(user))
            }

            # data = {
            #     "calendar_events": "[{\"id\": 1, \"title\": \"Meeting\", \"start\": \"2024-10-12T09:00:00\", \"end\": \"2024-10-12T10:00:00\"]",
            #     "assignments": "[{\"id\": 2, \"title\": \"Assignment 1\", \"due_date\": \"2024-10-14T09:00:00\", \"priority\": \"High\", \"Hours to Complete\": 1}]"
            # }
            events = None
            if len(data["calendar_events"]) + len(data['assignments']) != 0:
                response = requests.post(url, json=data)

                events = response.json()
                global sched
                sched = str(events)
                if type(events) is str:
                    events = json.loads(events.strip())

            print(events)
            print(type(events))
            if events is not None and isinstance(events, list):
                st.session_state["events"] = events  # Ensure events is always a list
            else:
                st.session_state["events"] = []
        st.rerun()
        
        
    # Initialize events in session state as a list
    if "events" not in st.session_state or not isinstance(st.session_state["events"], list):
        update()

   

    source_option = st.selectbox("Choose the calendar type:", ("Events", "Assignments"))

    # File uploader for .ics calendar files
    uploaded_file = st.file_uploader("Choose a .ics calendar file to import")

    if uploaded_file is not None and st.button("Import Events"):
        # Choose the API endpoint based on the selected source
        
        import_url = "http://127.0.0.1:5000/upload/"

        try:
            # # Read the contents of the uploaded file
            file_contents = uploaded_file.read()
            # print(file_contents.decode())
            if source_option == "Events":
                for e in read_ics_file_google(file_contents.decode()):
                    addEventToDB(e, st.session_state["user"])
            elif source_option == "Assignments":
                    for e in read_ics_file_canvas(file_contents.decode()):
                        addAssignmentToDB(e, st.session_state["user"])
            st.success("Events imported successfully!")
            update()
           

        except Exception as e:
            st.error(f"An error occurred while importing events: {e}")

    # Calendar options
    calendar_options = {
        "editable": "true",
        "navLinks": "true",
        "selectable": "true",
    }

    # Modify calendar options based on the selected mode
    calendar_options.update({
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridDay,dayGridWeek,dayGridMonth",
        },
        "initialView": "dayGridMonth",
    })

    # Display the calendar with the current events
    state = calendar(
        events=st.session_state["events"],
        options=calendar_options,
        custom_css=""" 
        .fc-event-past {
            opacity: 0.8;
        }
        .fc-event-time {
            font-style: italic;
        }
        .fc-event-title {
            font-weight: 700;
        }
        .fc-toolbar-title {
            font-size: 2rem;
        }
        """,
        callbacks=['dateClick']
    )

    if st.button("Regenerate Schedule"):
        update()
        st.success("Schedule updated successfully!")

    # Check if a date was clicked
    if state.get('dateClick') is not None:
        clicked_date_str = state['dateClick']['date']
        
        # Convert the string date to a datetime.date object
        clicked_date = datetime.datetime.fromisoformat(clicked_date_str).date()

        # Create a popover for adding an event
        with st.popover(f"Add Event for {clicked_date.strftime('%Y-%m-%d')}"):
            title = st.text_input("Event Title")
            start_date = st.date_input("Start Date", clicked_date)
            start_time = st.time_input("Start Time", value=datetime.time(9, 0))  # Default to 9:00 AM
            end_date = st.date_input("End Date", clicked_date)
            end_time = st.time_input("End Time", value=datetime.time(17, 0))  # Default to 5:00 PM
            
            submit_button = st.button("Add Event")

            if submit_button and title and start_date and end_date:
                new_event = {
                    "title": title,
                    "start": f"{start_date.isoformat()}T{start_time.isoformat()}",  # Combine date and time for start
                    "end": f"{end_date.isoformat()}T{end_time.isoformat()}",  # Combine date and time for end
                }
                addEventToDB(new_event, st.session_state["user"])
                st.session_state["events"] = st.session_state["events"]
                st.session_state['events'].append(new_event)

                st.success("Event added!")

        # Create a popover for adding an assignment
        with st.popover(f"Add Assignment due on {clicked_date.strftime('%Y-%m-%d')}"):
            title = st.text_input("Assignment Title")
            end_date = st.date_input("Due Date", clicked_date)
            end_time = st.time_input("Due Time", value=datetime.time(17, 0))  # Default to 5:00 PM
            hours_to_complete = st.number_input("Hours to Complete:", min_value=0.1, max_value=100., value=1.)

            priorities = ["Low", "Medium", "High"]
            selected_priority = st.selectbox("Select Priority", priorities)
            submit_button = st.button("Add Assignment")

            if submit_button and title and selected_priority and end_date:
                new_event = {
                    "title": title,
                    "due_date": f"{end_date.isoformat()}T{end_time.isoformat()}",  # Combine date and time for end
                    "hours_to_complete": hours_to_complete,
                    "priority": selected_priority,
                }
                addAssignmentToDB(new_event, st.session_state["user"])
                new_event['start'] = new_event['due_date']
                new_event['end'] = new_event['due_date']
                st.session_state["events"] = st.session_state["events"]
                st.session_state['events'].append(new_event)
                st.success("Assignment added!")

     # Chatbot logic
    def query_chatbot(user_input):
        url = "http://127.0.0.1:5000/chatbot"  # Adjust the URL based on your actual API
        global sched
        payload = {
            "user_input": user_input,
            "schedule": sched
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.json().get("response", "Error: No response from chatbot")
        else:
            return f"Error: Failed to connect to chatbot. Status Code: {response.status_code}"

    # Chatbot UI
    st.markdown("### Ask Tickles, Our Chatbot 🤖")
    user_question = st.text_input("Ask about your schedule or assignments:")
    
    if st.button("Ask Chatbot"):
        if user_question:
            with st.spinner('Processing your question...'):
                chatbot_response = query_chatbot(user_question)
                st.markdown(f"**Tickles 🤖:** {chatbot_response}")
        else:
            st.warning("Please enter a question for the chatbot.")
