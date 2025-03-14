import streamlit as st
import random
import time

from utils.session import session_setup, modify_prompt, modify_chat_history
from utils.components import show_response_count, finish_button, show_finish_status
from utils.chatbot import get_response
from utils.database import submit_to_database

st.set_page_config(
    layout='centered',
    page_title='Floods|Ready.gov',
    page_icon='✅'
)

# Apply custom CSS for aggressive styling
def set_background():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #FFFFFF; /* White background */
        }
        .big-title, .flood-title, .flood-warning, .st-chat-message, .user-message, .assistant-message {
            color: black;
        }
        .big-title {
            font-size: 50px;
            font-weight: bold;
        }
        .flood-title {
            font-size: 36px;
            font-weight: bold;
        }
        .flood-warning {
            background-color: white; 
            padding: 20px; 
            font-size: 18px;
        }
        .user-message, .assistant-message {
            background-color: #F0F0F0;  /* Light grey background */
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        
        </style>
        """,
        unsafe_allow_html=True
    )
    
def apply_custom_css():
    st.markdown(
        """
        <style>
        /* Style the user and assistant chat messages */
        .user-message, .assistant-message {
            color: black !important;  /* Black text color */
            background-color: #F0F0F0;  /* Light grey background */
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .st-chat-message {  /* Override any default white background */
            background-color: #F0F0F0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
def main():

    set_background()

    # Show information with a styled title
    st.markdown('<div class="big-title">Get Ready for Floods</div>', unsafe_allow_html=True)

    # Display the title
    st.markdown('<div class="flood-title">Staying Safe During a Flood</div>', unsafe_allow_html=True)

    # Display flood warning image
    st.image('floodreadygov_floodwarn.png', caption='Staying Safe During a Flood')

    st.markdown(
    """
    <style>
    .evacuate-now {
        background-color: #ffcccc;  /* Light red background */
        color: red !important;  /* Force red text color */
        font-weight: bold; 
        font-size: 24px;  /* Larger text size */
        padding: 20px; 
        border-radius: 10px; 
        border: 3px solid red; 
        text-align: center;
        margin-top: 20px;
    }
    </style>
    <div class="evacuate-now">
        ⚠️ Please evacuate now
    </div>
    """,
    unsafe_allow_html=True)
    
    # Display flood warning information with aggressive styling
    st.markdown(
        """
        <div class="flood-warning">
        ✅ Evacuate immediately if told to evacuate. Never drive around barricades. Local responders use them to safely direct traffic out of flooded areas.<br><br>
        ✅ Contact your healthcare provider if you are sick and need medical attention. Wait for further care instructions and shelter in place if possible. If you are experiencing a medical emergency, call 9-1-1.<br><br>
        ✅ Listen to EAS, NOAA Weather Radio, or local alerting systems for current emergency information and instructions regarding flooding.<br><br>
        ✅ Do not walk, swim, or drive through flood waters. <strong>Turn Around. Don’t Drown!</strong><br><br>
        ✅ Stay off bridges over fast-moving water. Fast-moving water can wash bridges away without warning.<br><br>
        ✅ Stay inside your car if it is trapped in rapidly moving water. Get on the roof if water is rising inside the car.<br><br>
        ✅ Get to the highest level if trapped in a building. Only get on the roof if necessary and once there, signal for help. Do not climb into a closed attic to avoid getting trapped by rising floodwater.<br><br>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(
    """
    <div style="
        background-color: white; 
        color: black; 
        padding: 10px; 
        border-radius: 5px; 
        border: 1px solid #ccc;">
        If you have any questions, please do not hesitate to chat with our <b>interactive chatbot</b>!
    </div>
    """,
    unsafe_allow_html=True
)
    
     # Set up chat session
    apply_custom_css()
    session_setup()
    
     # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # Apply specific class for user or assistant messages
            class_name = "user-message" if message["role"] == "user" else "assistant-message"
            st.markdown(f'<div class="{class_name}">{message["content"]}</div>', unsafe_allow_html=True)

    # Accept user input
    if user_input := st.chat_input("If you have any questions, please do not hesitate to chat with our interactive chatbot!"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(f'<div class="user-message">{user_input}</div>', unsafe_allow_html=True)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            response_gen = get_response(user_input)
            response = st.markdown(f'<div class="assistant-message">{response_gen}</div>', unsafe_allow_html=True)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response_gen})
            
            # Modify prompt
            modify_prompt(user_input, response_gen)

            # Modify chat history
            modify_chat_history(user_input, response_gen)

            # Increment response count
            st.session_state['response_count'] += 1

            # Rerun page
            st.experimental_rerun()

    # Show response count
    show_response_count()

    # Update session status
    finish_button()

    # Show finish status
    show_finish_status()

    # Submit survey to database if finished
    submit_to_database('info-blm')
    

if __name__ == '__main__':
    main()
