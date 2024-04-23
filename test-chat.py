import streamlit as st
import random
import time

from utils.session import session_setup, modify_prompt, modify_chat_history
from utils.components import show_response_count, finish_button, show_finish_status
from utils.chatbot import get_response
from utils.database import submit_to_database

st.set_page_config(
    layout='wide',
    page_title='Chatbot for science and technology',
    page_icon='🤖'
)

def main():

    # Set up session
    session_setup()

    # Show information
    st.title('都给👴聊 聊不完别想走')
    st.info('Your goal is to find out the information with GPT-4 about **BRAIN CHIPS**. Please stay on topic!')
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            response = st.write_stream(get_response(user_input))
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        # Modify prompt
        modify_prompt(user_input, response)

        # Modify chat history
        modify_chat_history(user_input, response)

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
