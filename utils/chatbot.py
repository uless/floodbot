import streamlit as st
import openai
from streamlit_chat import message
import pandas as pd
import string
import random

from rapidfuzz import process

minimum_responses = 1
warning_responses = 3
maximum_responses = 5

# Read knowledge base
KNOWLEDGE_FILE = "knowledge.csv"
df = pd.read_csv(KNOWLEDGE_FILE)

def retrieve_knowledge(user_input):
    user_input = user_input.lower().strip()
    
    relevant_rows = []
    for word in user_input.split():  # Splitting input into words
        matches = process.extract(word, df["topic"], limit=5)  # No score cutoff due to fuzzywuzzy limitations
        relevant_rows.extend([df.iloc[idx]["content"] for _, score, idx in matches if score > 10])  # Apply threshold manually

    if relevant_rows:
        return "\n".join(set(relevant_rows))  # Return unique matches

    return "I don't have specific information on that, but I can still help answer your question!"


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

    First print what you got from "Relevant Knowledge", then provide a short response within 3 sentences based on this relevant knowledge.
    '''

    response_content = ""

    #complete content
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are a government assistant providing official safety guidance."},
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

# get response from gpt4o
def get_response(user_input):
    if not user_input:
        return None

    if st.session_state['response_count'] >= maximum_responses:
        return None

    if st.session_state['survey_finished']:
        return None

    if user_input.lower() in ['hello', 'hi', 'hello!', 'hi!']:
        return 'Hello! I am the AI assistant Jamie. Let me know if you have any questions about the flood.'

    response = request_response(user_input)
    return response
