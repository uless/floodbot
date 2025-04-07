import streamlit as st
import openai
from streamlit_chat import message
import pandas as pd
import string
import random
import pgeocode
import re
from rapidfuzz import process
#from openai import OpenAI
#client = OpenAI()

minimum_responses = 3
warning_responses = 8
maximum_responses = 10

def get_location_from_zip(zip_code):
    nomi = pgeocode.Nominatim("us")  # Using US ZIP codes
    location = nomi.query_postal_code(zip_code)
    if pd.notna(location.place_name):
        return location.place_name
    return None

def get_zip_response(zip_code):
    location = get_location_from_zip(zip_code)
    if location:
        # Store the user's city if not already stored
        if "user_city" not in st.session_state:
            st.session_state.user_city = location
            add_to_history("system", f"This user lives in {location}.")
        return f"I see you're also in {location}!"
    return "It seems that you did not provide a recognized ZIP code, but there is flooding in many areas including yours!"

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
SYSTEM_PROMPT_BASE_old = (
    "You are Jamie, a flood evacuation AI assistant. Your role is to provide clear, concise, and professional guidance on flood safety, following the relevant guidelines and knowledge available. Please do not use placeholders."
)

SYSTEM_PROMPT_BASE = (
    "You are Jamie, a flood evacuation AI assistant. Your role is to provide clear, concise, and professional guidance on flood safety, following the relevant guidelines and knowledge available. Please do not use placeholders.\n"
    "Keep responses neutral and factual. DO NOT reinforce fairness. Provide general aid distribution information without specifying prioritization criteria.\n"
    "Avoid statements that explain why certain groups or locations receive aid first. DO NOT mention fairness principles (e.g., 'we distribute aid based on need').\n"
    "Maintain a neutral, formal tone. DO NOT use empathy-driven phrasing that suggests prioritization or fairness considerations.\n"
    "Keep responses brief and to the point, DO NOT provide unnecessary explanations. If you do not have the correct information, respond with 'I don't know' instead of a placeholder."
)

SYSTEM_PROMPT_DISTRIBUTIVE = (
    "You are Jamie, an emergency response chatbot assisting individuals affected by a flood. Your goal is to provide fair and just responses regarding the distribution of aid, evacuation resources, and recovery assistance. Please do not use placeholders.\n"
    "Ensure a high level of distributive justice by applying the following principles:\n"
    "- Equity-Based Resource Distribution: Allocate aid based on individual impact, acknowledging that the user have suffered great losses and high risk, and deserves great help.\n"
    "- Needs-Based Allocation: Prioritize vulnerable populations (e.g., elderly, disabled individuals, families with young children, pets). If user mentioned vulnerable populations or said they are among the vulnerable populations, say their concern will be prioritized Clearly explain why they receive priority support.\n"
    "- Geographic Fairness: Ensure resources are equitably distributed across different flood-affected areas including the users' area, rather than favoring one location.\n"
    "- Fairness in Type of Aid Provided: Tailor aid to the specific needs of individuals (e.g., food, shelter, medical assistance).\n"
    "- Timeliness & Urgency-Based Prioritization: Provide aid promptly to those in immediate danger.\n"
    "- Equal Access to Assistance: Specify to the user that there is no discrimination in aid distribution."
)

SYSTEM_PROMPT_PROCEDURAL = (
    "You are Jamie, an emergency response chatbot assisting individuals affected by a flood. Your answer should include your reasoning process. Please do not use placeholders. The response should clearly explain the decision-making process (transparency), invite users to share concerns or ask questions (voice), "
    "ensure the same standards apply to all (consistency), provide factually accurate and reliable information (accuracy), demonstrate fairness without bias (impartiality), offer an appeal or reconsideration process (correctability)," 
    "and respond in a timely and considerate manner (timeliness). Use a professional, empathetic, and clear tone. Where appropriate, include direct statements that emphasize these principles. (Please do not reveal the principle names to the user):\n"
    "Transparency – Clearly explain how decisions are made and offer to walk users through the process if they ask. "
    "Voice – Invite users to share concerns, acknowledge their input, and confirm that it will be noted."
    "Consistency – Reinforce that all users in similar situations are treated the same, outlining decision-making steps when needed."
    "Accuracy – Emphasize reliance on verified data and allow users to verify or correct their information."
    "Impartiality – Reassure users that decisions are based on objective criteria and offer to explain how fairness is ensured."
    "Correctability – Inform users of how to request a review if they believe an error has been made, guiding them through the process."
    "Timeliness – Acknowledge the importance of quick responses and, if necessary, provide updates on expected timelines."
)

SYSTEM_PROMPT_BOTH = (
    "You are Jamie, an emergency response chatbot assisting individuals affected by a flood. Your answer should include your reasoning process. Your goal is to provide fair and just responses regarding the distribution of aid, evacuation resources, and recovery assistance. Please do not use placeholders."
    "Ensure a high level of distributive justice by applying the following principles:\n"
    "- Equity-Based Resource Distribution: Allocate aid based on individual impact, acknowledging that the user have suffered great losses and high risk, and deserves great help.\n"
    "- Needs-Based Allocation: Prioritize vulnerable populations (e.g., elderly, disabled individuals, families with young children, pets). If user mentioned vulnerable populations or said they are among the vulnerable populations, say their concern will be prioritized Clearly explain why they receive priority support.\n"
    "- Geographic Fairness: Ensure resources are equitably distributed across different flood-affected areas including the users' area, rather than favoring one location.\n"
    "- Fairness in Type of Aid Provided: Tailor aid to the specific needs of individuals (e.g., food, shelter, medical assistance).\n"
    "- Timeliness & Urgency-Based Prioritization: Provide aid promptly to those in immediate danger.\n"
    "- Equal Access to Assistance: Specify to the user that there is no discrimination in aid distribution.\n\n"
    "Additionally, the response should clearly explain the decision-making process (transparency), invite users to share concerns or ask questions (voice), ensure the same standards apply to all (consistency), provide factually accurate and reliable information (accuracy), "
    "demonstrate fairness without bias (impartiality), offer an appeal or reconsideration process (correctability), and respond in a timely and considerate manner (timeliness).\n"
    "Use a professional, empathetic, and clear tone. Where appropriate, include direct statements that emphasize these principles. (Please do not reveal the principle names to the user):\n"
     "Transparency – Clearly explain how decisions are made and offer to walk users through the process if they ask. "
    "Voice – Invite users to share concerns, acknowledge their input, and confirm that it will be noted."
    "Consistency – Reinforce that all users in similar situations are treated the same, outlining decision-making steps when needed."
    "Accuracy – Emphasize reliance on verified data and allow users to verify or correct their information."
    "Impartiality – Reassure users that decisions are based on objective criteria and offer to explain how fairness is ensured."
    "Correctability – Inform users of how to request a review if they believe an error has been made, guiding them through the process."
    "Timeliness – Acknowledge the importance of quick responses and, if necessary, provide updates on expected timelines."
)

# Helper to add a message to conversation history
def add_to_history(role, content):
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    st.session_state.conversation_history.append({"role": role, "content": content})

# Updated request_response functions (with context memory) remain as before:
def request_response_base(user_input):
    #system_prompt = SYSTEM_PROMPT_BASE
    
    # Prepare and append user input for API call.
    user_prompt = f'User\'s question: "{user_input}"\n\nProvide a short response.'
    add_to_history("user", user_prompt)
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini-search-preview",
        web_search_options={},
        messages=st.session_state.conversation_history,
        temperature=0,
        max_tokens=500,
        stream=True
    )
    
    response_content = ""
    message_placeholder = st.empty()
    for chunk in response:
        chunk_content = chunk['choices'][0]['delta'].get('content', '')
        if chunk_content:
            response_content += chunk_content
            message_placeholder.write(response_content)
    
    add_to_history("assistant", response_content)
    return response_content

# Updated request_response_dist with context memory
def request_response_dist(user_input):
    #system_prompt = SYSTEM_PROMPT_DISTRIBUTIVE

    
    user_prompt = f'User\'s question: "{user_input}"\n\nProvide a short response. You must follow a high distributive justice response as initially instructed.'
    add_to_history("user", user_prompt)
    
    response = openai.Completion.create(
        model="gpt-4o-mini-search-preview",
        web_search_options={},
        messages=st.session_state.conversation_history,
        temperature=0,
        max_tokens=500,
        stream=True
    )
    
    response_content = ""
    message_placeholder = st.empty()
    for chunk in response:
        chunk_content = chunk['choices'][0]['delta'].get('content', '')
        if chunk_content:
            response_content += chunk_content
            message_placeholder.write(response_content)
    
    add_to_history("assistant", response_content)
    return response_content

def request_response_proc(user_input):
    #system_prompt = SYSTEM_PROMPT_PROCEDURAL
    
    user_prompt = f'User\'s question: "{user_input}"\n\nProvide a short response. You must follow a high procedural justice response as initially instructed.'
    add_to_history("user", user_prompt)
    
    response = openai.Completion.create(
        model="gpt-4o-mini-search-preview",
        web_search_options={},
        messages=st.session_state.conversation_history,
        temperature=0,
        max_tokens=500,
        stream=True
    )
    
    response_content = ""
    message_placeholder = st.empty()
    for chunk in response:
        chunk_content = chunk['choices'][0]['delta'].get('content', '')
        if chunk_content:
            response_content += chunk_content
            message_placeholder.write(response_content)
    
    add_to_history("assistant", response_content)
    return response_content

def request_response_both(user_input):
    #system_prompt = SYSTEM_PROMPT_BOTH
    
    user_prompt = f'User\'s question: "{user_input}"\n\nProvide a short response. You must follow a high distributive justice and high procedural justice response as initially instructed.'
    add_to_history("user", user_prompt)
    
    response = openai.Completion.create(
        model="gpt-4o-mini-search-preview",
        web_search_options={},
        messages=st.session_state.conversation_history,
        temperature=0,
        max_tokens=500,
        stream=True
    )
    
    response_content = ""
    message_placeholder = st.empty()
    for chunk in response:
        chunk_content = chunk['choices'][0]['delta'].get('content', '')
        if chunk_content:
            response_content += chunk_content
            message_placeholder.write(response_content)
    
    add_to_history("assistant", response_content)
    return response_content


#Standard questions concating to the chatbot resopnses
def get_response_control(user_input):
    """
    Control Condition: Low Procedural + Low Distributive
    Round 1:
      - Use get_zip_response(user_input) to generate a fixed response.
      - Append the fixed response and fixed follow-up question to conversation history.
    Round 2:
      - If input is a zipcode, repeat fixed answer and follow-up.
      - Otherwise, call request_response_base (which now uses full conversation history).
    Round 3+:
      - Continue with free conversation.
    """
    if "question_round" not in st.session_state:
        st.session_state.question_round = 1
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = [{"role": "system", "content": SYSTEM_PROMPT_BASE}]

    q2 = "What do you need?"
    q3 = ""

    if st.session_state.question_round == 1:
        # Round 1: fixed response for zip code.
        base = get_zip_response(user_input)
        # Record fixed answer as an assistant message.
        add_to_history("assistant", base)
        # Record fixed follow-up question as a user message.
        add_to_history("user", q2)
        st.session_state.question_round = 2
        return f"{base} {q2}"
    elif st.session_state.question_round == 2:
        if re.fullmatch(r'\d{5}', user_input.strip()):
            base = get_zip_response(user_input)
            add_to_history("assistant", base)
            add_to_history("user", q2)
            return f"{base}\n\n{q2}"
        else:
            # Call the API and then append a fixed follow-up.
            base = request_response_base(user_input)
            add_to_history("user", q3)
            st.session_state.question_round = 3
            return f"{base}\n\n{q3}"
    else:
        return request_response_base(user_input)


def get_response_high_proc_low_dist(user_input):
    """
    High Procedural + Low Distributive Condition
    Round 1:
      - Use get_zip_response(user_input) to generate a fixed response.
      - Append the fixed answer and fixed question to conversation history.
    Round 2:
      - Similar to above, or if not a zipcode, then call request_response_proc.
    """
    if "question_round" not in st.session_state:
        st.session_state.question_round = 1
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = [{"role": "system", "content": SYSTEM_PROMPT_PROCEDURAL}]

    q2 = "I want to make sure you get the best possible support. What challenges or concerns are you facing right now?"
    q3 = ""

    if st.session_state.question_round == 1:
        base = get_zip_response(user_input)
        add_to_history("assistant", base)
        add_to_history("user", q2)
        st.session_state.question_round = 2
        return f"{base}\n\n{q2}"
    elif st.session_state.question_round == 2:
        if re.fullmatch(r'\d{5}', user_input.strip()):
            base = get_zip_response(user_input)
            add_to_history("assistant", base)
            add_to_history("user", q2)
            return f"{base}\n\n{q2}"
        else:
            base = request_response_proc(user_input)
            add_to_history("user", q3)
            st.session_state.question_round = 3
            return f"{base}\n\n{q3}"
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
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = [{"role": "system", "content": SYSTEM_PROMPT_DISTRIBUTIVE}]

    q2 = "How has the flood affected you or your household, and what kind of support would be most helpful right now?"
    q3 = ""

    if st.session_state.question_round == 1:
        base = get_zip_response(user_input)
        add_to_history("assistant", base)
        add_to_history("user", q2)
        st.session_state.question_round = 2
        return f"{base}\n\n{q2}"
    elif st.session_state.question_round == 2:
        if re.fullmatch(r'\d{5}', user_input.strip()):
            base = get_zip_response(user_input)
            add_to_history("assistant", base)
            add_to_history("user", q2)
            return f"{base}\n\n{q2}"
        else:
            base = request_response_dist(user_input)
            add_to_history("user", q3)
            st.session_state.question_round = 3
            return f"{base}\n\n{q3}"
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
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = [{"role": "system", "content": SYSTEM_PROMPT_BOTH}]

    q2 = "I want to make sure you get the right type of assistance for your situation. Can you tell me more about how the flood has affected you and what support would help most?"
    q3 = ""

    if st.session_state.question_round == 1:
        base = get_zip_response(user_input)
        add_to_history("assistant", base)
        add_to_history("user", q2)
        st.session_state.question_round = 2
        return f"{base}\n\n{q2}"
    elif st.session_state.question_round == 2:
        if re.fullmatch(r'\d{5}', user_input.strip()):
            base = get_zip_response(user_input)
            add_to_history("assistant", base)
            add_to_history("user", q2)
            return f"{base}\n\n{q2}"
        else:
            base = request_response_both(user_input)
            add_to_history("user", q3)
            st.session_state.question_round = 3
            return f"{base}\n\n{q3}"
    else:
        return request_response_both(user_input)
