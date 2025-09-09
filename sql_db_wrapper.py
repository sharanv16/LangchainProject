from langchain_community.utilities import SQLDatabase
from langchain_community.chat_models import ChatOpenAI
from langchain_experimental.sql import SQLDatabaseChain

import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env
load_dotenv()

# Access the key
api_key = os.getenv("OPENAI_API_KEY")

# Connect to DB (example: SQLite)
db = SQLDatabase.from_uri("sqlite:///sample.db")

# Load model
llm = ChatOpenAI(model="gpt-4", temperature=1)

# Create LangChain SQL agent
db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)

# Streamlit UI
st.title("Conversational Data Explorer")

query = st.text_input("Ask me anything about the database:")

if query:
    try:
        response = db_chain.run(query)
        st.write(response)
    except Exception as e:
        st.error(f"Error: {e}")

