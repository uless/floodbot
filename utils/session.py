import streamlit as st
import openai
import pandas as pd
import string
import random
import torch
from sentence_transformers import SentenceTransformer, util


# load Sentence Transformer model for semantical matching
model = SentenceTransformer("all-MiniLM-L6-v2")

# read knowledge base
KNOWLEDGE_FILE = "knowledge.csv"
df = pd.read_csv(KNOWLEDGE_FILE)

# vectorize `topic` 
df["topic_embedding"] = df["topic"].apply(lambda x: model.encode(x, convert_to_tensor=True))



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

# find knowledge from the knowledge base
def retrieve_knowledge(user_input):
    user_embedding = model.encode(user_input, convert_to_tensor=True)
    similarities = [util.pytorch_cos_sim(user_embedding, topic_emb)[0].item() for topic_emb in df["topic_embedding"]]
    
    best_idx = torch.argmax(torch.tensor(similarities)).item()
    best_match = df.iloc[best_idx]
    
    if similarities[best_idx] > 0.3:  # threshold for similarity
        return best_match["content"]
    else:
        return "I don't have specific information on that, but I can still help answer your question regarding the flood!"


# Set up the state of this streamlit app session
def session_setup():

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


#Generated content with RAG
def generate_ai_response(user_input):
    
    retrieved_knowledge = retrieve_knowledge(user_input)

    prompt = """You are Jamie, a flood evacuation AI assistant. Your role is to provide clear, 
    concise, and professional guidance on flood safety, following government-approved information.

    User's question: "{user_input}"

    Relevant Knowledge:
    {retrieved_knowledge}

    Provide a short response within 5 sentences based on this relevant knowledge.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are a government assistant providing official safety guidance."},
                      {"role": "user", "content": prompt}],
            temperature=0
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"An error occurred: {e}"



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
