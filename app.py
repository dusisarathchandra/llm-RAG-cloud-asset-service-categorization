import streamlit as st
import psycopg2
import json
from datetime import datetime
from psycopg2 import sql
from groq import Groq
import warnings
import streamlit as st
import time
from elasticsearch import Elasticsearch
from openai import OpenAI
from retrieval import RetrieveContext
from src.constants import LLM_CLIENT, DEPLOYMENT, API_KEY_GROQ
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

def groq_llm(prompt):
    print("**************************************")
    print("Using Groq API to generate response")
    client = Groq(api_key=API_KEY_GROQ)
    response = client.chat.completions.create(
        model="gemma2-9b-it",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        stream=False,
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
    llm_func = ollama_llm if DEPLOYMENT == 'local' else groq_llm
    answer = llm_func(prompt)
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
if DEPLOYMENT == "local":
    create_feedback_table()

# Streamlit application
st.title("Cloud Asset Service Categorizer")

# Display a tip about the app with an image
st.info("""Welcome to the Cloud Asset Service Category Identifier app! 
        Provide a short description about the cloud asset & Click the button to find out its likely Category & Service.
        For more information on usecase visit [here](https://github.com/dusisarathchandra/llm-RAG-cloud-asset-service-categorization/blob/main/setup-docs/cloud-asset-service-categorization.md): """, icon="💡")

# Input box for the question
query = st.text_input("Enter your question:", placeholder="e.g., Interactive query to analyze data on S3", max_chars=500)
response = ""

# Button to fetch the cloud service category
if st.button("Fetch the cloud asset service category"):
    with st.spinner("Hold tight, while I fetch the cloud asset service category! This might take a while 🙂"):
        st.session_state.response = rag_vector_ollama(query)
        st.session_state.response = remove_backticks(st.session_state.response)
        st.session_state.response = json.loads(st.session_state.response)
        print(st.session_state.response)
        st.success(st.session_state.response)
        st.session_state.button_clicked = True
        print("************************************** after success")
if DEPLOYMENT == "local":     
    # Show feedback buttons only if the "Fetch the cloud service category" button is clicked
    if st.session_state.button_clicked:
        st.write("Rate your experience:")
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