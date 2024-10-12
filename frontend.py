import streamlit as st
from streamlit_calendar import calendar
import datetime

st.set_page_config(page_title="Demo for streamlit-calendar", page_icon="📆")

st.markdown("## Calendar App 📆")

# Initialize events in session state as a list
if "events" not in st.session_state or not isinstance(st.session_state["events"], list):
    st.session_state["events"] = []  # Ensure events is always a list

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
        
        color = st.color_picker("color", "#FF6C6C")
        submit_button = st.button("Add Event")

        if submit_button and title and start_date and end_date:
            new_event = {
                "title": title,
                "color": color,
                "start": f"{start_date.isoformat()}T{start_time.isoformat()}",  # Combine date and time for start
                "end": f"{end_date.isoformat()}T{end_time.isoformat()}",  # Combine date and time for end
            }
            st.session_state["events"].append(new_event)  # Append the new event to the list
            
            # Display the calendar with the current events
            print(st.session_state['events'])
            st.success("Event added!")
    # Create a popover for adding an event
    with st.popover(f"Add Assignment due on {clicked_date.strftime('%Y-%m-%d')}"):
        title = st.text_input("Assignment Title")
        end_date = st.date_input("Due Date", clicked_date)
        end_time = st.time_input("Due Time", value=datetime.time(17, 0))  # Default to 5:00 PM
        priorities = ["Low", "Medium", "High"]
        selected_priority = st.selectbox("Select Priority", priorities)
        color = st.color_picker("Color", "#FF6C6C")
        submit_button = st.button("Add Assignment")

        if submit_button and title and selected_priority and end_date:
            new_event = {
                "title": title,
                "color": color,
                "start": f"{end_date.isoformat()}T{end_time.isoformat()}",  # Combine date and time for start
                "end": f"{end_date.isoformat()}T{end_time.isoformat()}",  # Combine date and time for end
                "priority": selected_priority
            }
            st.session_state["events"].append(new_event)  # Append the new event to the list
            
            # Display the calendar with the current events
            print(st.session_state['events'])
            st.success("Assignment added!")

# Display the current state of events
st.write("Current Events:", st.session_state["events"])
