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
    st.title('AI chatbot for science')
    st.info('Your goal is to find out the information with GPT-4 about **human gene editing**. Please stay on topic!')
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if user_input := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(user_input)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            response_gen = get_response(user_input)
            response = st.write(response_gen)
            
            # Add assistant response to chat history, check indense
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
