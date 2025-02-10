import streamlit as st
import openai
import pandas as pd
import string
import random
import torch
from sentence_transformers import SentenceTransformer, util

# Load Sentence Transformer model for semantic matching
model = SentenceTransformer("all-MiniLM-L6-v2")

# Read knowledge base
KNOWLEDGE_FILE = "knowledge.csv"
df = pd.read_csv(KNOWLEDGE_FILE)

# Vectorize `topic`
df["topic_embedding"] = df["topic"].apply(lambda x: model.encode(x, convert_to_tensor=True))

# Generate a 10-character ID
def get_survey_id():
    return f"{random.randint(0,9)}{random.randint(0,9)}{random.choice(string.ascii_letters)}" \
           f"{random.choice(string.ascii_letters)}{random.choice(string.ascii_letters)}{random.randint(0,9)}" \
           f"{random.randint(0,9)}{random.choice(string.ascii_letters)}{random.randint(0,9)}{random.choice(string.ascii_letters)}"

# Find knowledge from the knowledge base
def retrieve_knowledge(user_input):
    user_embedding = model.encode(user_input, convert_to_tensor=True)
    similarities = [util.pytorch_cos_sim(user_embedding, topic_emb)[0].item() for topic_emb in df["topic_embedding"]]

    if not similarities:  
        return "I don't have specific information on that, but I can still help answer your question regarding the flood!"

    best_idx = torch.argmax(torch.tensor(similarities)).item()
    best_match = df.iloc[best_idx]

    if similarities[best_idx] > 0.3:
        return best_match["content"]
    else:
        return "I don't have specific information on that, but I can still help answer your question regarding the flood!"

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
