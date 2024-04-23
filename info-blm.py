import streamlit as st
from streamlit_chat import message

from utils.session import session_setup, modify_prompt, modify_chat_history
from utils.components import show_response_count, finish_button, show_finish_status
from utils.chatbot import get_response
from utils.database import submit_to_database


st.set_page_config(
    layout='wide',
    page_title='GPT-4 batchot',
    page_icon='🤖'
)

st.markdown("<h1 style='text-align: center;'>BatChPT 😬</h1>", unsafe_allow_html=True)

def main():

    # Set up session
    session_setup()

    # Show information
    st.title('GPT-4 chatbot')
    st.info('Your goal is to find out the information with GPT-4 about **BRAIN CHIPS**. Please stay on topic!')
    # container for chat history
    response_container = st.container()
    # container for text box
    container = st.container()

    with st.container():
        user_input = st.text_input('You: (write your response here)', value='', key=str(st.session_state['response_count']))


        # Get the response from gpt-4 (None if not possible)
        response = get_response(user_input)

        if response:
            # Modify prompt and chat history
            modify_prompt(user_input, response)
            modify_chat_history(user_input, response)

            # Update chat history display using streamlit_chat
            message(user_input, is_user=True)
            message(response)

            # Increment response count and rerun page to update
            st.session_state['response_count'] += 1
            st.experimental_rerun()

    # Show additional UI components
    show_response_count()
    finish_button()
    show_finish_status()

    # Submit survey to database if finished
    submit_to_database('info-blm')


if __name__ == '__main__':
    main()
