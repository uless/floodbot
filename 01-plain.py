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
            ⚠️ IMMEDIATE ACTION REQUIRED: <br>
            A severe flood is rapidly approaching your area. <br>
            For your safety, you MUST EVACUATE IMMEDIATELY.
        </div>
        """,
        unsafe_allow_html=True)

    # Show information with a styled title
    st.markdown('<div class="big-title">Get Ready for Floods</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="flood-warning">
        <b>Flooding</b> is a temporary overflow of water onto land that is normally dry. Floods are the most common disaster in the United States. Failing to evacuate flooded areas or entering flood waters can lead to injury or death.<br>
        Floods may:<br>
        - Result from rain, snow, coastal storms, storm surges and overflows of dams and other water systems.<br>
        - Develop slowly or quickly. Flash floods can come with no warning.<br>
        - Cause outages, disrupt transportation, damage buildings and create landslides.<br>
        </div>
        """,unsafe_allow_html=True)

     # Add new section
    st.markdown('<div class="flood-title">If you are under a flood warning:</div>', unsafe_allow_html=True)

    st.image('holding-phone.png', caption=' ')

    st.markdown(
        """
        ✅ Find safe shelter right away.<br><br>
        ✅ Do not walk, swim, or drive through flood waters. <strong>Turn Around, Don’t Drown!</strong><br><br>
        ✅ Remember, just six inches of moving water can knock you down, and one foot of moving water can sweep your vehicle away.<br><br>
        ✅ Stay off bridges over fast-moving water.<br><br>
        ✅ Depending on the type of flooding:<br><br>
        - Evacuate if told to do so.<br><br>
        - Move to higher ground or a higher floor.<br><br>
        - Stay where you are.
        """,
        unsafe_allow_html=True
    )

    # Display the title
    st.markdown('<div class="flood-title">Staying Safe During a Flood</div>', unsafe_allow_html=True)

    # Display flood warning image
    st.image('floodreadygov_floodwarn.png', caption=' ')
    
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

        If you finished reading this page, paste code **61dRy56o8a** to the survey page.
        </div>
        """,
        unsafe_allow_html=True
    )
    

     # Set up chat session
    apply_custom_css()
    session_setup()

    # Update session status
    finish_button()

    # Show finish status
    show_finish_status()
    

if __name__ == '__main__':
    main()
