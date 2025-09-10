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

# Streamlit UI for MySQL credentials
st.title("Conversational Data Explorer (MySQL)")

host = st.text_input("MySQL Host", value="localhost")
port = st.text_input("MySQL Port", value="3306")
user = st.text_input("MySQL Username", value="root")
password = st.text_input("MySQL Password", type="password")
database = st.text_input("MySQL Database", value="userdb")

# Use session state to persist connection and chain
if "db_chain" not in st.session_state:
    st.session_state.db_chain = None
    st.session_state.db = None

if st.button("Connect"):
    try:
        uri = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
        db = SQLDatabase.from_uri(uri)
        llm = ChatOpenAI(model="gpt-4", temperature=1, openai_api_key=api_key)
        db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)
        st.session_state.db_chain = db_chain
        st.session_state.db = db
        st.success("Connected to MySQL database!")
    except Exception as e:
        st.error(f"Connection failed: {e}")

if st.session_state.db_chain:
    st.write("Available tables:", st.session_state.db.get_table_names())
    query = st.text_input("Ask me anything about the database:")
    if query:
        try:
            response = st.session_state.db_chain.run(query)
            st.write(response)
        except Exception as e:
            st.error(f"Error: {e}")

