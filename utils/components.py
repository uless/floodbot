import streamlit as st


minimum_responses = 1
warning_responses = 3
maximum_responses = 5


# Show response count
def show_response_count():
    response_count = st.session_state['response_count']

    if response_count == 0:
        return

    remaining_rounds = maximum_responses - response_count
    response_count_message = f"You have completed {response_count} round(s) of conversation. You can ask up to {remaining_rounds} more round(s) of conversation."

    # Need more responses
    if response_count < warning_responses:
        response_count_message += f" You can ask up to {remaining_rounds} more round(s) of conversation."
        st.info(response_count_message)

    # Enough but can ask more
    elif warning_responses <= response_count < maximum_responses:
        response_count_message += f" Due to time limits, you can ask {remaining_rounds} more round(s)."
        st.warning(response_count_message)

    # Done
    elif response_count >= maximum_responses:
        response_count_message += " You have reached the maximum allowed rounds of conversation."
        st.success(response_count_message)


# Push button to finish the survey
def finish_button():

    response_count = st.session_state['response_count']

    if response_count == maximum_responses:
        st.session_state['survey_finished'] = True

    if not st.session_state['survey_finished'] and response_count >= minimum_responses:
        st.session_state['survey_finished'] |= st.button('Finish Chat')


# Show the survey completed message
def show_finish_status():

    if not st.session_state['survey_finished']:
        return

    survey_id = st.session_state['survey_id']
    st.success(f'''
      Please return to the survey page and paste this verification code: **{survey_id}**. 
      You can now close this page if you have submitted this code in survey.
    ''')
