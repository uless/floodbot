import streamlit as st
import openai
import pandas as pd
import string
import random
from sentence_transformers import SentenceTransformer, util


# Generate a 10-character ID
def get_survey_id():
    return f"{random.randint(0,9)}{random.randint(0,9)}{random.choice(string.ascii_letters)}" \
           f"{random.choice(string.ascii_letters)}{random.choice(string.ascii_letters)}{random.randint(0,9)}" \
           f"{random.randint(0,9)}{random.choice(string.ascii_letters)}{random.randint(0,9)}{random.choice(string.ascii_letters)}"

# Set up Streamlit session state
def session_setup():
    if 'prompt' not in st.session_state:
        st.session_state['prompt'] = ""  

    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = 'Your chat with Jamie will appear here!\n\n'

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
