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
        db_chain = SQLDatabaseChain.from_llm(
            llm, db, verbose=True, return_intermediate_steps=True
        )
        st.session_state.db_chain = db_chain
        st.session_state.db = db
        st.success("Connected to MySQL database!")
    except Exception as e:
        st.error(f"Connection failed: {e}")

if st.session_state.db_chain:
    st.write("Available tables:", st.session_state.db.get_table_names())

    # Initialize conversation history in session state
    if "conversation" not in st.session_state:
        st.session_state.conversation = []

    # Display previous conversation
    for i, (user_query, llm_response, sql_steps) in enumerate(st.session_state.conversation):
        st.markdown(f"**You:** {user_query}")
        st.markdown(f"**LLM:** {llm_response}")
        if sql_steps:
            for sql_cmd in sql_steps:
                st.code(sql_cmd, language="sql")

    # New prompt input box after last output
    new_query = st.text_input("Ask me anything about the database:", key=f"query_{len(st.session_state.conversation)}")
    if new_query:
        try:
            response = st.session_state.db_chain(new_query)
            llm_result = response.get("result", "")
            sql_cmds = []
            if "intermediate_steps" in response and response["intermediate_steps"]:
                for step in response["intermediate_steps"]:
                    if isinstance(step, dict) and "sql_cmd" in step:
                        sql_cmds.append(step["sql_cmd"])
            # Append to conversation history
            st.session_state.conversation.append((new_query, llm_result, sql_cmds))
            st.rerun()  # Refresh to show new output and new input box
        except Exception as e:
            st.error(f"Error: {e}")

