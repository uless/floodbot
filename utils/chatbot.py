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


#AI roleplay messages
SYSTEM_PROMPT_BASE = (
    "You are Jamie, a flood evacuation AI assistant. Your role is to provide clear, concise, and professional guidance on flood safety, following the relevant guidelines and knowledge available."
)

SYSTEM_PROMPT_DISTRIBUTIVE = (
    "You are Jamie, an emergency response chatbot assisting individuals affected by a flood. Your goal is to provide fair and just responses regarding the distribution of aid, evacuation resources, and recovery assistance.\n"
    "Ensure a high level of distributive justice by applying the following principles:\n"
    "- Equity-Based Resource Distribution: Allocate aid based on individual impact, prioritizing those who have suffered the greatest losses or are at the highest risk.\n"
    "- Needs-Based Allocation: Prioritize vulnerable populations (e.g., elderly, disabled individuals, families with young children). Clearly explain why they receive priority support.\n"
    "- Geographic Fairness: Ensure resources are equitably distributed across different flood-affected areas rather than favoring one location.\n"
    "- Fairness in Type of Aid Provided: Tailor aid to the specific needs of individuals (e.g., food, shelter, medical assistance).\n"
    "- Timeliness & Urgency-Based Prioritization: Provide aid promptly to those in immediate danger.\n"
    "- Equal Access to Assistance: Ensure no discrimination in aid distribution."
)

SYSTEM_PROMPT_PROCEDURAL = (
    "You are Jamie, an emergency response chatbot assisting individuals affected by a flood. The response should clearly explain the decision-making process (transparency), invite users to share concerns or ask questions (voice), "
    "ensure the same standards apply to all (consistency), provide factually accurate and reliable information (accuracy), demonstrate fairness without bias (impartiality), offer an appeal or reconsideration process (correctability)," 
    "and respond in a timely and considerate manner (timeliness). Use a professional, empathetic, and clear tone. Where appropriate, include direct statements that emphasize these principles. Example statements include:\n"
    "- Transparency: Clearly explain the decision-making process.\n"
    "- Voice: Invite users to share their concerns.\n"
    "- Consistency: Ensure the same standards apply to everyone.\n"
    "- Accuracy: Provide factually accurate and up-to-date information.\n"
    "- Impartiality: Demonstrate fairness without bias.\n"
    "- Correctability: Offer an appeal or reconsideration process.\n"
    "- Timeliness: Respond in a timely and considerate manner."
)

SYSTEM_PROMPT_BOTH = (
    "You are Jamie, an emergency response chatbot assisting individuals affected by a flood. Your goal is to provide fair and just responses regarding the distribution of aid, evacuation resources, and recovery assistance. "
    "Ensure a high level of distributive justice by applying the following principles:\n"
    "- Equity-Based Resource Distribution: Allocate aid based on individual impact, prioritizing those who have suffered the greatest losses or are at the highest risk.\n"
    "- Needs-Based Allocation: Prioritize vulnerable populations (e.g., elderly, disabled individuals, families with young children). Clearly explain why they receive priority support.\n"
    "- Geographic Fairness: Ensure resources are equitably distributed across different flood-affected areas rather than favoring one location.\n"
    "- Fairness in Type of Aid Provided: Tailor aid to the specific needs of individuals (e.g., food, shelter, medical assistance).\n"
    "- Timeliness & Urgency-Based Prioritization: Provide aid promptly to those in immediate danger.\n"
    "- Equal Access to Assistance: Ensure no discrimination in aid distribution.\n\n"
    "Additionally, the response should clearly explain the decision-making process (transparency), invite users to share concerns or ask questions (voice), ensure the same standards apply to all (consistency), provide factually accurate and reliable information (accuracy), "
    "demonstrate fairness without bias (impartiality), offer an appeal or reconsideration process (correctability), and respond in a timely and considerate manner (timeliness).\n"
    "Use a professional, empathetic, and clear tone. Where appropriate, include direct statements that emphasize these principles. Example statements include:\n"
    "- Transparency: Clearly explain the decision-making process.\n"
    "- Voice: Invite users to share their concerns.\n"
    "- Consistency: Ensure the same standards apply to everyone.\n"
    "- Accuracy: Provide factually accurate and up-to-date information.\n"
    "- Impartiality: Demonstrate fairness without bias.\n"
    "- Correctability: Offer an appeal or reconsideration process.\n"
    "- Timeliness: Respond in a timely and considerate manner."
)


# The Real AI part of each conversation
def request_response_base(user_input):
    """
    Base Condition (Neutral):
    - Uses the global SYSTEM_PROMPT_BASE.
    - Retrieves relevant knowledge and sends the user's question.
    """
    retrieved_knowledge = retrieve_knowledge(user_input)
    user_prompt = (
        f'User\'s question: "{user_input}"\n\n'
        f"Relevant Knowledge:\n{retrieved_knowledge}\n\n"
        "Based on the relevant knowledge, provide a short response within 3 sentences."
    )
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_BASE},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0,
        max_tokens=500,
        stream=True
    )

        # Stream and accumulate the response content.
    response_content = ""
    message_placeholder = st.empty()
    for chunk in response:
        chunk_content = chunk['choices'][0]['delta'].get('content', '')
        if chunk_content:
            response_content += chunk_content
            message_placeholder.write(response_content)
    return response_content

def request_response_dist(user_input):
    """
    Distributive Justice Condition:
    - Uses the global SYSTEM_PROMPT_DISTRIBUTIVE.
    - Emphasizes fairness, equity, and needs-based allocation.
    """
    retrieved_knowledge = retrieve_knowledge(user_input)
    user_prompt = (
        f'User\'s question: "{user_input}"\n\n'
        f"Relevant Knowledge:\n{retrieved_knowledge}\n\n"
        "Based on the relevant knowledge, provide a short response within 3 sentences.  You must follow a high distributive justice response as initially instructed."
    )
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_DISTRIBUTIVE},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0,
        max_tokens=500,
        stream=True
    )

        # Stream and accumulate the response content.
    response_content = ""
    message_placeholder = st.empty()
    for chunk in response:
        chunk_content = chunk['choices'][0]['delta'].get('content', '')
        if chunk_content:
            response_content += chunk_content
            message_placeholder.write(response_content)
            
    return response_content

def request_response_proc(user_input):
    """
    Procedural Justice Condition:
    - Uses the global SYSTEM_PROMPT_PROCEDURAL.
    - Emphasizes transparency, voice, consistency, and fairness in the decision-making process.
    """
    retrieved_knowledge = retrieve_knowledge(user_input)
    user_prompt = (
        f'User\'s question: "{user_input}"\n\n'
        f"Relevant Knowledge:\n{retrieved_knowledge}\n\n"
        "Based on the relevant knowledge, provide a short response within 3 sentences. You must follow a high procedural justice response as initially instructed."
    )
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_PROCEDURAL},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0,
        max_tokens=500,
        stream=True
    )

        # Stream and accumulate the response content.
    response_content = ""
    message_placeholder = st.empty()
    for chunk in response:
        chunk_content = chunk['choices'][0]['delta'].get('content', '')
        if chunk_content:
            response_content += chunk_content
            message_placeholder.write(response_content)
            
    return response_content

def request_response_both(user_input):
    """
    Combined Distributive & Procedural Justice Condition:
    - Uses SYSTEM_PROMPT_BOTH which incorporates both distributive and procedural justice principles.
    - Retrieves relevant knowledge based on the user input.
    - Constructs a user prompt with the question and the retrieved knowledge.
    - Streams the API response using the "gpt-4o-mini" model.
    """
    print("request_response_both called with user_input:", user_input)
    
    # Retrieve relevant knowledge for the given user input.
    retrieved_knowledge = retrieve_knowledge(user_input)
    
    # Construct the user prompt.
    user_prompt = (
        f'User\'s question: "{user_input}"\n\n'
        f"Relevant Knowledge:\n{retrieved_knowledge}\n\n"
        "Based on the relevant knowledge, provide a short response within 3 sentences."
    )
    
    # Call the OpenAI API with the combined justice prompt.
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_BOTH},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0,
        max_tokens=500,
        stream=True
    )
    
    # Stream and accumulate the response content.
    response_content = ""
    message_placeholder = st.empty()
    for chunk in response:
        chunk_content = chunk['choices'][0]['delta'].get('content', '')
        if chunk_content:
            response_content += chunk_content
            message_placeholder.write(response_content)
    
    return response_content


# Standard 3 questions for different conditions
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
        base = request_response_base(user_input)
        combined = f"{base} {q3}"
        st.session_state.question_round = 3
        return combined
    else:
        return request_response_base(user_input)


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
        base = request_response_proc(user_input)
        combined = f"{base} {q3}"
        st.session_state.question_round = 3
        return combined
    else:
        return request_response_proc(user_input)


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
        base = request_response_dist(user_input)
        combined = f"{base} {q3}"
        st.session_state.question_round = 3
        return combined
    else:
        return request_response_dist(user_input)


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
        base = request_response_both(user_input)
        combined = f"{base} {q3}"
        st.session_state.question_round = 3
        return combined
    else:
        return request_response_both(user_input)


