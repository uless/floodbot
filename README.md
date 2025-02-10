# Application for Gathering Human-Chatbot Conversations

This Application serves as a tool for gathering human-chatbot conversations for research purposes. It offers user-friendly functionality and seamless integration with any chatbot. This repository corresponds to the paper titled "Human-Machine Justice in Disaster Response: How AI Chatbots Influence Risk Perception and Public Behavior" in collaboration with Dr. Shupei Yuan and Dr. Luye Bao. This chatbot project is adapted from the prior project with Dr. Kaiping Chen, Dr. Yixuan Li, and Jirayu Burapacheep:  ["Conversational AI and equity through assessing GPT-3’s communication with diverse social groups on contentious topics"]([https://www.nature.com/articles/s41598-024-51969-w]).


## Overview

The application is developed using Python and relies on [Streamlit](https://www.streamlit.io/), a framework designed for creating ML and data science applications. We utilize [MongoDB](https://www.mongodb.com/) as the storage solution for the conversations and deploy the application on Streamlit's [sharing platform](https://share.streamlit.io/). This repository provides the application's source code, along with instructions for the setup and deployment process.

## Knowledge Base

Knowledge based for this flood-ready chatbot is collected from this main page [Floods|Ready.gov](https://www.ready.gov/floods), as well as the following sub-pages:

Three webpages in the "During the flood" about relevant reseach on actions during the flood:

[Flood │ Evacuate Safely When Ordered To](https://community.fema.gov/ProtectiveActions/s/article/Flood-Evacuate-Safely-When-Ordered-To)

[Flood │ Don’t Drive During a Flood](https://community.fema.gov/ProtectiveActions/s/article/Flood-Dont-Drive-During-a-Flood)

[Flood │ Move to Higher Ground](https://community.fema.gov/ProtectiveActions/s/article/Flood-Move-to-Higher-Ground)

And two other information sheets:

[Flood Information Sheet](https://www.ready.gov/sites/default/files/2025-01/fema_flood-hazard-info-sheet.pdf)

[Your Homeowners Insurance Does Not Cover Flood](https://www.ready.gov/sites/default/files/2020-03/homeowners-does-not-cover-flooding.pdf)


## Setup

### Clone the repository

To begin, clone the repository by running the following command:

```bash
git clone https://github.com/Top34051/chat-with-gpt-3.git
```

### Install dependencies

Make sure you have Python 3.7 or above installed. To install the required dependencies, execute the following command:

```bash
pip install -r requirements.txt
```

### MongoDB Setup

The application relies on MongoDB for storing conversations. To set up MongoDB, please follow the instructions [here](https://docs.mongodb.com/manual/installation/). Once MongoDB is set up, proceed with their guidelines to create a database named `survey-data` and a collection named `test`. Afterward, create a directory `.streamlit` and add your MongoDB connection string to the `.streamlit/secrets.toml` file.

### OpenAI API setup for GPT-3 access

To enable response generation using the OpenAI API, you need to set up the API. Refer to the instructions [here](https://beta.openai.com/docs/developer-quickstart/your-api-keys) for the necessary steps. Place your API key in the `secrets.toml` file. Once both MongoDB and the OpenAI API are properly configured, your `secrets.toml` file should resemble the following:

```toml
openai_api_key = <YOUR OPENAI API KEY>
db_endpoint = <YOUR MONGODB CONNECTION STRING>
```

## Deployment

### Local deployment

To run the application locally, execute one of the following commands:

```bash
streamlit run 01-plain.py
streamlit run 02-comment-box.py
streamlit run 03-chatbot.py
```

Each command corresponds to a different survey. The first two commands are for the information-seeking survey, and the last two commands are for the opinion-seeking survey. The first two commands are for the Black Lives Matter topic, and the last two commands are for the climate change topic. The only difference between each files is the description of the survey and the topic of the conversation.

### Streamlit sharing deployment

To deploy the application on Streamlit sharing, follow the instructions [here](https://docs.streamlit.io/en/stable/deploy_streamlit_app.html). Make sure to add your MongoDB connection string and OpenAI API key to the `secrets.toml` file. Once the application is deployed, you can access it through the link provided by Streamlit sharing.

## Analyze Cleaned Data

To analyze the cleaned data, run the following command:

```bash
streamlit run analyze.py
```

The analysis application allows you to download a file that excludes conversations failing to meet the quality criteria. Additionally, it annotates each conversation round with the corresponding round index.

