import os
import streamlit as st
from langchain.chains import create_sql_query_chain
from langchain_google_genai import GoogleGenerativeAI
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError
from langchain_community.utilities import SQLDatabase

google_api_key = "AIzaSyC2wwbtfXzeAOqS81zHYlGtJQcrE-KidHs"

# Database connection parameters
db_user = "root"
db_password = "9160"
db_host = "localhost"
db_name = "scott"

# Create SQLAlchemy engine
engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")

# Initialize SQLDatabase
db = SQLDatabase(engine, sample_rows_in_table_info=3)

# Initialize LLM
llm = GoogleGenerativeAI(model="gemini-pro", google_api_key=google_api_key)

# Create SQL query chain
chain = create_sql_query_chain(llm, db)

def execute_query(question):
    try:
        # Generate SQL query from question
        response = chain.invoke({"question": question})
        
        # Clean the generated SQL query
        cleaned_query = response.strip("```sql").strip("```")
        
        # Execute the query
        result = db.run(cleaned_query)
        
        # Return the query and the result
        return cleaned_query, result
    except ProgrammingError as e:
        st.error(f"An error occurred: {e}")
        return None, None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None, None


# Streamlit interface
st.title("Question Answering App")

# Input from user
question = st.text_input("Enter your question:")

if st.button("Execute"):
    if question:
        cleaned_query, query_result = execute_query(question)
        if cleaned_query and query_result is not None:
            st.write("Generated SQL Query:")
            st.code(cleaned_query, language="sql")
            st.write("Query Result:")
            st.write(query_result)
        else:
            st.write("No result returned due to an error.")
    else:
        st.write("Please enter a question.")
