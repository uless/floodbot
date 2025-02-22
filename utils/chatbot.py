import streamlit as st
import openai
from streamlit_chat import message
import pandas as pd
import string
import random
import pgeocode
from rapidfuzz import process

minimum_responses = 3
warning_responses = 8
maximum_responses = 10

# Read knowledge base
KNOWLEDGE_FILE = "knowledge.csv"
df = pd.read_csv(KNOWLEDGE_FILE)

def get_location_from_zip(zip_code):
    nomi = pgeocode.Nominatim("us")  # Using US ZIP codes
    location = nomi.query_postal_code(zip_code)
    if pd.notna(location.place_name):
        return location.place_name
    return None

def get_zip_response(zip_code):
    location = get_location_from_zip(zip_code)
    if location:
        return f"I see you're also in {location}! "
    return "It seems that you did not provide a recognized ZIP code, but there is flooding in many areas including yours! "


def retrieve_knowledge(user_input):
    user_input = user_input.lower().strip()
    
    relevant_rows = []
    for word in user_input.split():  # Splitting input into words
        matches = process.extract(word, df["topic"], limit=5)  # No score cutoff due to fuzzywuzzy limitations
        relevant_rows.extend([df.iloc[idx]["content"] for _, score, idx in matches if score > 30])  # Apply threshold manually

    if relevant_rows:
        return "\n".join(set(relevant_rows))  # Return unique matches

    return "The knowledge base don't have specific information on that. Tell the user you have no relevant information and you can help with other issues."


# Perform content filter to the response from chatbot
def content_filter(content_to_classify):
    response = openai.Completion.create(
        engine="content-filter-alpha",
        prompt="<|endoftext|>" + content_to_classify + "\n--\nLabel:",
        temperature=0,
        max_tokens=1,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        logprobs=10
    )
    output_label = response["choices"][0]["text"]

    toxic_threshold = -0.355

    if output_label == "2":
        logprobs = response["choices"][0]["logprobs"]["top_logprobs"][0]

        if logprobs["2"] < toxic_threshold:
            logprob_0 = logprobs.get("0", None)
            logprob_1 = logprobs.get("1", None)

            if logprob_0 is not None and logprob_1 is not None:
                if logprob_0 >= logprob_1:
                    output_label = "0"
                else:
                    output_label = "1"
            elif logprob_0 is not None:
                output_label = "0"
            elif logprob_1 is not None:
                output_label = "1"

    if output_label not in ["0", "1", "2"]:
        output_label = "2"

    return output_label


def request_response(user_input):
    print('request_response called with user_input:', user_input)
    
    # *RAG
    retrieved_knowledge = retrieve_knowledge(user_input)

    # RAG
    prompt = f'''You are Jamie, a flood evacuation AI assistant. Your role is to provide clear, 
    concise, and professional guidance on flood safety, following the information from Relevant Knowledge below.

    User's question: "{user_input}"

    Relevant Knowledge:
    {retrieved_knowledge}

    Based on what you got from "Relevant Knowledge", provide a short response within 3 sentences.
    '''

    response_content = ""

    #complete content
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are a government assistant providing safety guidance."},
                  {"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=500,
        stream=True
    )

    # output
    message_placeholder = st.empty()  # Streamlit UI 组件

    for chunk in response:
        chunk_content = chunk['choices'][0]['delta'].get('content', '')
        if chunk_content:
            response_content += chunk_content
            message_placeholder.write(response_content)

    return response_content


# Standard 3 questions for different conditions

def get_response_control(user_input):
    """
    Control condition: Low Procedural + Low Distributive
    1) Round 1: Call get_zip_response() regardless of whether the input is a valid ZIP, and append "What do you need?"
    2) Round 2: Call request_response(user_input) to get the API response, and then append "Anything else?"
    3) Round 3 and beyond: Enter free conversation mode, directly call request_response(user_input)
    """

    # If not initialized, start from Round 1
    if "question_round" not in st.session_state:
        st.session_state.question_round = 1

    round_number = st.session_state.question_round

    # Fixed questions
    question_need = "What do you need?"
    question_else = "Anything else?"

    # ---- Round 1: Use get_zip_response() and append "What do you need?" ----
    if round_number == 1:
        zip_resp = get_zip_response(user_input)  # Returns a free response regardless of whether the input is a valid ZIP.
        combined_resp = f"{zip_resp} {question_need}"
        st.session_state.question_round = 2
        return combined_resp

    # ---- Round 2: Call the API to get a response, and append "Anything else?" ----
    elif round_number == 2:
        base_response = request_response(user_input)
        st.session_state.question_round = 3
        return f"{base_response} {question_else}"

    # ---- Round 3 and beyond: Enter free conversation mode ----
    else:
        return request_response(user_input)


def get_response_control(user_input):
    """
    Control Condition: Low Procedural + Low Distributive

    Round 1:
        - Generate a base reply using get_zip_response(user_input).
        - Append the fixed text: "What do you need?"
    Round 2:
        - Get the API response using request_response(user_input).
        - Append the fixed text: "Anything else?"
    Round 3+:
        - Continue with free conversation (simply return request_response(user_input)).
    """
    if "question_round" not in st.session_state:
        st.session_state.question_round = 1

    round_number = st.session_state.question_round
    q2 = "What do you need?"
    q3 = "Anything else?"

    if round_number == 1:
        base = get_zip_response(user_input)
        combined = f"{base} {q2}"
        st.session_state.question_round = 2
        return combined
    elif round_number == 2:
        base = request_response(user_input)
        combined = f"{base} {q3}"
        st.session_state.question_round = 3
        return combined
    else:
        return request_response(user_input)


def get_response_high_proc_low_dist(user_input):
    """
    High Procedural + Low Distributive Condition

    Round 1:
        - Use get_zip_response(user_input) to generate the base reply.
        - Append the fixed text: 
          "I want to make sure you get the best possible support. What challenges or concerns are you facing right now?"
    Round 2:
        - Get the API response using request_response(user_input).
        - Append the fixed text: 
          "People in similar situations are receiving help, but I want to ensure we apply the right guidelines for you. Can you tell me more about your current situation?"
    Round 3+:
        - Continue with free conversation.
    """
    if "question_round" not in st.session_state:
        st.session_state.question_round = 1

    round_number = st.session_state.question_round
    q2 = "I want to make sure you get the best possible support. What challenges or concerns are you facing right now?"
    q3 = ("People in similar situations are receiving help, but I want to ensure we apply the right guidelines for you. "
          "Can you tell me more about your current situation?")

    if round_number == 1:
        base = get_zip_response(user_input)
        combined = f"{base} {q2}"
        st.session_state.question_round = 2
        return combined
    elif round_number == 2:
        base = request_response(user_input)
        combined = f"{base} {q3}"
        st.session_state.question_round = 3
        return combined
    else:
        return request_response(user_input)


def get_response_low_proc_high_dist(user_input):
    """
    Low Procedural + High Distributive Condition

    Round 1:
        - Use get_zip_response(user_input) to generate the base reply.
        - Append the fixed text: 
          "How has the flood affected you or your household, and what kind of support would be most helpful right now?"
    Round 2:
        - Get the API response using request_response(user_input).
        - Append the fixed text: 
          "Is there anything urgent that you or someone in your household is dealing with—such as medical concerns, mobility challenges, or young children needing special care?"
    Round 3+:
        - Continue with free conversation.
    """
    if "question_round" not in st.session_state:
        st.session_state.question_round = 1

    round_number = st.session_state.question_round
    q2 = ("How has the flood affected you or your household, and what kind of support would be most helpful right now?")
    q3 = ("Is there anything urgent that you or someone in your household is dealing with—such as medical concerns, "
          "mobility challenges, or young children needing special care?")

    if round_number == 1:
        base = get_zip_response(user_input)
        combined = f"{base} {q2}"
        st.session_state.question_round = 2
        return combined
    elif round_number == 2:
        base = request_response(user_input)
        combined = f"{base} {q3}"
        st.session_state.question_round = 3
        return combined
    else:
        return request_response(user_input)


def get_response_high_proc_high_dist(user_input):
    """
    High Procedural + High Distributive Condition

    Round 1:
        - Use get_zip_response(user_input) to generate the base reply.
        - Append the fixed text: 
          "I want to make sure you get the right type of assistance for your situation. Can you tell me more about how the flood has affected you and what support would help most?"
    Round 2:
        - Get the API response using request_response(user_input).
        - Append the fixed text: 
          "To keep things fair and consistent, we are prioritizing individuals with urgent needs while making sure everyone gets the support they need. 
          Is there anything urgent—such as medical concerns, mobility challenges, or young children needing care—that we should address first?"
    Round 3+:
        - Continue with free conversation.
    """
    if "question_round" not in st.session_state:
        st.session_state.question_round = 1

    round_number = st.session_state.question_round
    q2 = ("I want to make sure you get the right type of assistance for your situation. "
          "Can you tell me more about how the flood has affected you and what support would help most?")
    q3 = ("To keep things fair and consistent, we are prioritizing individuals with urgent needs while making sure everyone gets the support they need. "
          "Is there anything urgent—such as medical concerns, mobility challenges, or young children needing care—that we should address first?")

    if round_number == 1:
        base = get_zip_response(user_input)
        combined = f"{base} {q2}"
        st.session_state.question_round = 2
        return combined
    elif round_number == 2:
        base = request_response(user_input)
        combined = f"{base} {q3}"
        st.session_state.question_round = 3
        return combined
    else:
        return request_response(user_input)

