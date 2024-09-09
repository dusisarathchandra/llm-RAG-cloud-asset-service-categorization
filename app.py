# import warnings
# import streamlit as st
# import time
# from elasticsearch import Elasticsearch
# from openai import OpenAI
# from retrieval import RetrieveContext
# from src.constants import LLM_CLIENT
# from src.building_prompt import build_prompt

# # ignore some warnings
# warnings.simplefilter(action="ignore", category=FutureWarning)

# es_client = Elasticsearch('http://localhost:9200')
# client = OpenAI(base_url='http://localhost:11434/v1/', api_key='ollama')


# # def elastic_search(query, index_name="asset-categories"):
# #     search_query = {
# #         "size": 10,
# #         "query": {
# #             "bool": {
# #                 "must": {
# #                     "multi_match": {
# #                         "query": query,
# #                         "fields": ["description^5", "category^3", "service", "cloud_provider"],
# #                         "type": "best_fields"
# #                     }
# #                 },
# #             }
# #         }
# #     }

# #     response = es_client.search(index=index_name, body=search_query)
    
# #     result_docs = []
    
# #     for hit in response['hits']['hits']:
# #         result_docs.append(hit['_source'])
    
# #     return result_docs

# # def build_prompt(query, search_results):
# #     prompt_template = """
# # You're a cloud asset category finder. Answer the DESCRIPTION based on the CONTEXT.
# # Use only the facts from the CONTEXT when answering the DESCRIPTION. Generate a short answer by saying `YOUR CATEGORY IS: `.

# # DESCRIPTION: {question}

# # CONTEXT: 
# # {context}
# # """.strip()

# #     context = ""
    
# #     for doc in search_results:
# #         context = context + f"answer: {doc['category']}\nservice: {doc['service']}\ndescription: {doc['description']}\ncloud_provider: {doc['cloud_provider']}\n\n"
    
# #     prompt = prompt_template.format(question=query, context=context).strip()
# #     return prompt


# def ollama_llm(prompt):
#     response = client.chat.completions.create(
#         model='gemma2:2b',
#         messages=[{"role": "user", "content": prompt}]
#     )
    
#     return response.choices[0].message.content

# def rag_vector_ollama(query):
#     search_results = RetrieveContext().get_vector_context(query)[['description', 'category', 'service', 'cloud_provider']].to_dict(orient='records')
#     print("**************************************")
#     prompt = build_prompt(query, search_results)
#     answer = ollama_llm(prompt)
#     return answer

# def rag_elastic_ollama(query):
#     search_results = RetrieveContext().get_elastic_search_context(query)
#     prompt = build_prompt(query, search_results)
#     answer = ollama_llm(prompt)
#     return f"Category for '{query}' is '{answer}'"

# # Streamlit application
# st.title("Cloud Service Category Fetcher")

# # Display a tip about the app with an image
# st.info("""Welcome to the Cloud Service Category Fetcher app! Give some details about the cloud service and click the button to fetch the cloud service category.""", icon="💡")

# # Input box for the question
# query = st.text_input("Enter your question:", placeholder="e.g., What is the best cloud storage service?", max_chars=500)

# # # User input widget (at the bottom, outside of the chat history)
# # user_prompt = st.chat_input(
# #     placeholder="Ask your question here, e.g. 'Is Wi-Fi dangerous?', 'Is a microwave dangerous?', 'How to eat healthy?'",
# #     key="user_input",
# #     max_chars=500,
# # )
# # Button to fetch the cloud service category
# if st.button("Fetch the cloud service category"):
#     with st.spinner("Fetching the cloud service category..."):
#         response = rag_vector_ollama(query)
#         st.success(response)

import streamlit as st
import psycopg2
import json
from datetime import datetime
from psycopg2 import sql

import warnings
import streamlit as st
import time
from elasticsearch import Elasticsearch
from openai import OpenAI
from retrieval import RetrieveContext
from src.constants import LLM_CLIENT
from src.building_prompt import build_prompt

# ignore some warnings
warnings.simplefilter(action="ignore", category=FutureWarning)

es_client = Elasticsearch('http://localhost:9200')
client = OpenAI(base_url='http://localhost:11434/v1/', api_key='ollama')
# Initialize session state
if 'feedback_submitted' not in st.session_state:
    st.session_state.feedback_submitted = False

if 'response' not in st.session_state:
    st.session_state.response = ""

if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False

if 'query' not in st.session_state:
    st.session_state.query = ""

def create_feedback_table():
    try:
        print("Connect to user_feedback database to create feedback table if it doesn't exist")
        connection = psycopg2.connect(
            dbname="user_feedback",
            user="postgres",
            password="admin",
            host="localhost",
            port="5432"
        )
        cursor = connection.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_feedback (
            id SERIAL PRIMARY KEY,
            query TEXT NOT NULL,
            answer TEXT NOT NULL,
            feedback INTEGER NOT NULL,
            feedback_type TEXT NOT NULL,
            category TEXT NOT NULL,
            service TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL
        )
        """
        cursor.execute(create_table_query)
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        st.error(f"Error creating feedback table: {e}")

def insert_feedback(query, answer, feedback, feedback_type, category, service):
    print(f"Connect to user_feedback table to insert feedback: {feedback} with category: {category} and service: {service}")
    try:
        # Convert answer to JSON string if it's a dictionary
        if isinstance(answer, dict):
            answer = json.dumps(answer)
        connection = psycopg2.connect(
            dbname="user_feedback",
            user="postgres",
            password="admin",
            host="localhost",
            port="5432"
        )
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO user_feedback (query, answer, feedback, feedback_type, category, service, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (query, answer, feedback, feedback_type, category, service, datetime.now()))
        connection.commit()
        cursor.close()
        connection.close()
        print(f"user feedback: {feedback} successfully stored in database")
    except Exception as e:
        st.error(f"Error inserting feedback: {e}")

def ollama_llm(prompt):
    response = client.chat.completions.create(
        model='gemma2:2b',
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

# Replace occurrences of "```json" and "```" with an empty string
def remove_backticks(text):
    return text.replace("```json", "").replace("```", "").strip()

def rag_vector_ollama(query):
    search_results = RetrieveContext().get_vector_context(query)[['description', 'category', 'service', 'cloud_provider']].to_dict(orient='records')
    print("**************************************")
    prompt = build_prompt(query, search_results)
    print(f'\nprompt: {prompt}\n')
    answer = ollama_llm(prompt)
    return answer

def rag_elastic_ollama(query):
    search_results = RetrieveContext().get_elastic_search_context(query)
    prompt = build_prompt(query, search_results)
    answer = ollama_llm(prompt)
    return f"Category for '{query}' is '{answer}'"

def create_database_if_not_exists():
    try:
        # Connect to the default 'postgres' database
        connection = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="admin",
            host="localhost",
            port="5432"
        )
        connection.autocommit = True
        cursor = connection.cursor()

        # Check if the 'user_feedback' database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'user_feedback'")
        exists = cursor.fetchone()

        # If the database does not exist, create it
        if not exists:
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier('user_feedback')
            ))
            print("Database 'user_feedback' created successfully.")
        else:
            print("Database 'user_feedback' already exists.")

        cursor.close()
        connection.close()

        # Connect to the 'user_feedback' database
        connection = psycopg2.connect(
            dbname="user_feedback",
            user="postgres",
            password="admin",
            host="localhost",
            port="5432"
        )
        print("Connected to 'user_feedback' database successfully.")
        return connection

    except Exception as e:
        print(f"Error: {e}")

# Call the function to create the database if it doesn't exist and connect to it
# connection = create_database_if_not_exists()
# Ensure the feedback table exists
create_feedback_table()

# Streamlit application
st.title("Cloud Service Category Fetcher")

# Display a tip about the app with an image
st.info("""Welcome to the Cloud Service Category Fetcher app! Give some details about the cloud service and click the button to fetch the cloud service category.""", icon="💡")

# Input box for the question
query = st.text_input("Enter your question:", placeholder="e.g., What is the best cloud storage service?", max_chars=500)
response = ""

# Button to fetch the cloud service category
if st.button("Fetch the cloud service category"):
    with st.spinner("Fetching the cloud service category..."):
        st.session_state.response = rag_vector_ollama(query)
        st.write(f"Type of st.session_state.response: {type(st.session_state.response)}")
        print(remove_backticks(st.session_state.response))
        st.session_state.response = remove_backticks(st.session_state.response)
        st.session_state.response = json.loads(st.session_state.response)
        print(st.session_state.response)
        st.success(st.session_state.response)
        st.session_state.button_clicked = True
        print("************************************** after success")
     
# Show feedback buttons only if the "Fetch the cloud service category" button is clicked
if st.session_state.button_clicked:
    st.write("Please rate the service (1 to 5):")
    col1, col2, col3, col4, col5 = st.columns(5)
    category = st.session_state.response.get('category', 'Unknown')
    service = st.session_state.response.get('service', 'Unknown')

    if not st.session_state.get('feedback_submitted', False):
        with col1:
            if st.button("😞"):
                insert_feedback(query, st.session_state.response, 1, "Negative", category, service)
                st.session_state.feedback_submitted = True
                st.write("Feedback submitted: 😞")
        with col2:
            if st.button("😕"):
                insert_feedback(query, st.session_state.response, 2, "Can be better", category, service)
                st.session_state.feedback_submitted = True
                st.write("Feedback submitted: 😕")
        with col3:
            if st.button("😐"):
                insert_feedback(query, st.session_state.response, 3, "Neutral", category, service)
                st.session_state.feedback_submitted = True
                st.write("Feedback submitted: 😐")
        with col4:
            if st.button("🙂"):
                insert_feedback(query, st.session_state.response, 4, "Good", category, service)
                st.session_state.feedback_submitted = True
                st.write("Feedback submitted: 🙂")
        with col5:
            if st.button("😍"):
                insert_feedback(query, st.session_state.response, 5, "Excellent", category, service)
                st.session_state.feedback_submitted = True
                st.write("Feedback submitted: 😍")
    else:
        st.info("Feedback already submitted.")

# Clear buttons and response if feedback is submitted
if st.session_state.feedback_submitted:
    st.write("Thank you for your feedback!")
    st.session_state.feedback_submitted = False
    st.session_state.response = ""
    st.session_state.button_clicked = False
    st.session_state.query = ""