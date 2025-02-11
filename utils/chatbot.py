import streamlit as st
import openai
from streamlit_chat import message
import pandas as pd
import string
import random
import pgeocode

from rapidfuzz import process

minimum_responses = 1
warning_responses = 3
maximum_responses = 5

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
        return f"I see you're also in {location}! How can I assist you with the flood situation here?"
    return "It seems that you did not provide a recognized ZIP code, but there is flooding in many areas including yours! How can I assist you?"


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

def get_response(user_input):
    if not user_input:
        return None

    # ZIP Code Detection - Only respond with ZIP-specific message and exit early
    if user_input.isdigit() and len(user_input) == 5:  
        return get_zip_response(user_input)  # Return ZIP response only (no RAG applied)

    if st.session_state.get('survey_finished', False):  # Prevent responses if session is finished
        return None

    if user_input.lower() in ['hello', 'hi', 'hello!', 'hi!']:
        return 'Hello! I am the AI assistant Jamie. Let me know if you have any questions about the flood.'

    # Apply RAG-based retrieval for non-ZIP inputs only
    return request_response(user_input)
