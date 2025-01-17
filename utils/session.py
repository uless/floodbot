import streamlit as st
import openai
import string
import random


# Generate a 10 characters ID of pattern:
#   0     1     2     3     4     5     6     7     8     9
# [0-9] [0-9] [A-Z] [A-Z] [A-Z] [0-9] [0-9] [A-Z] [0-9] [A-Z]
def get_survey_id():
    survey_id = ''
    survey_id = survey_id + str(random.randint(0, 9))
    survey_id = survey_id + str(random.randint(0, 9))
    survey_id = survey_id + random.choice(string.ascii_letters)
    survey_id = survey_id + random.choice(string.ascii_letters)
    survey_id = survey_id + random.choice(string.ascii_letters)
    survey_id = survey_id + str(random.randint(0, 9))
    survey_id = survey_id + str(random.randint(0, 9))
    survey_id = survey_id + random.choice(string.ascii_letters)
    survey_id = survey_id + str(random.randint(0, 9))
    survey_id = survey_id + random.choice(string.ascii_letters)
    return survey_id


# Set up the state of this streamlit app session
def session_setup():

    if 'prompt' not in st.session_state:
        st.session_state['prompt'] = '''You are an AI assistant for flood evacuation. Your name is Jamie. 
        Make sure you greet the user with your self introduction: "Hi, I am Jamie, the flood evacuation AI assistant." in your first response only.
        Your response should not exceed 3 sentences. Your only knowledge are as follows:
        Flooding is a temporary overflow of water onto land that is normally dry. Floods are the most common disaster in the United States. Failing to evacuate flooded areas or entering flood waters can lead to injury or death.
        Floods may:
        Result from rain, snow, coastal storms, storm surges and overflows of dams and other water systems.
        Develop slowly or quickly. Flash floods can come with no warning.
        Cause outages, disrupt transportation, damage buildings and create landslides.
 
        If you are under a flood warning:
        Find safe shelter right away.
        Do not walk, swim or drive through flood waters. Turn Around, Don’t Drown!
        Remember, just six inches of moving water can knock you down, and one foot of moving water can sweep your vehicle away.
        Stay off bridges over fast-moving water.
        Depending on the type of flooding:
        Evacuate if told to do so.
        Move to higher ground or a higher floor.
        Stay where you are.

        To stay safe during a flood, you should:
        Evacuate immediately, if told to evacuate. Never drive around barricades. Local responders use them to safely direct traffic out of flooded areas.
        Contact your healthcare provider If you are sick and need medical attention. Wait for further care instructions and shelter in place, if possible. If you are experiencing a medical emergency, call 9-1-1.
        Listen to EAS, NOAA Weather Radio or local alerting systems for current emergency information and instructions regarding flooding.
        Do not walk, swim or drive through flood waters. Turn Around. Don’t Drown!
        Stay off bridges over fast-moving water. Fast-moving water can wash bridges away without warning.
        Stay inside your car if it is trapped in rapidly moving water. Get on the roof if water is rising inside the car.
        Get to the highest level if trapped in a building. Only get on the roof if necessary and once there signal for help. Do not climb into a closed attic to avoid getting trapped by rising floodwater. '''

    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = 'Your chat with GPT-4 will appear here!\n\n'

    if 'response_count' not in st.session_state:
        st.session_state['response_count'] = 0

    if 'survey_id' not in st.session_state:
        st.session_state['survey_id'] = get_survey_id()

    if 'survey_finished' not in st.session_state:
        st.session_state['survey_finished'] = False

    if 'submitted_to_database' not in st.session_state:
        st.session_state['submitted_to_database'] = False

    openai.api_key = st.secrets["openai_api_key"]


# Save prompt
def modify_prompt(user_input, response):

    prompt = st.session_state['prompt']
    prompt = prompt + 'Human: ' + user_input + '\n'
    prompt = prompt + 'AI: ' + response + '\n'
    st.session_state['prompt'] = prompt


# Save chat history
def modify_chat_history(user_input, response):

    history = st.session_state['chat_history']
    history = history + 'Participant: ' + user_input + '\n'
    history = history + 'GPT-4: ' + response + '\n'
    st.session_state['chat_history'] = history
