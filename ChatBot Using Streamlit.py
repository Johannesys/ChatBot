import openai
import pandas as pd
import streamlit as st
from PyPDF2 import PdfReader
from io import StringIO
import docx

# Set API Key OpenAI
openai.api_key = "Insert Your API Key"
def load_database(file):
    """
    Reads database files and returns dataframes or text.
    """
    try:
        if file.name.endswith(".csv"):
            return pd.read_csv(file), "dataframe"
        elif file.name.endswith(".xlsx"):
            return pd.read_excel(file, engine='openpyxl'), "dataframe"
        elif file.name.endswith(".pdf"):
            # Ekstrak teks dari PDF
            pdf_reader = PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text, "text"
        elif file.name.endswith(".docx"):
            # Ekstrak teks dari Word
            doc = docx.Document(file)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text, "text"
        else:
            raise ValueError("File formats are not supported. Use .csv, .xlsx, .pdf, or .docx")
    except Exception as e:
        st.error(f"Error to read file: {e}")
        return None, None

def analyze_database(content, content_type, prompt):
    """
    Functions for analyzing databases or texts with the OpenAI API.
    """
    if content_type == "dataframe":
        content_text = content.to_csv(index=False)
        input_content = f"This is the format of CSV:\n{content_text}"
    elif content_type == "text":
        input_content = f"this is a text:\n{content}"
    else:
        st.error("Content Unreconized.")
        return None

    messages = [
        {"role": "system", "content": "You're an data analyst would help to understand the file."},
        {"role": "user", "content": f"{prompt}\n\n{input_content}"}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        st.error(f"Error saat memproses prompt: {e}")
        return None

# Streamlit app
st.title("ChatBot")

# Upload file
uploaded_file = st.file_uploader("Upload file (.csv, .xlsx, .pdf, atau .docx):", type=["csv", "xlsx", "pdf", "docx"])

if uploaded_file:
    # Load and display the content
    content, content_type = load_database(uploaded_file)
    if content is not None:
        if content_type == "dataframe":
            st.write("Database Succesfully load:")
            st.dataframe(content)
        elif content_type == "text":
            st.write("Text succesfully load:")
            st.text_area("loaded text:", content, height=300)

        # Input prompt
        user_prompt = st.text_input("Enter your Prompt:")

        if user_prompt:
            # Analyze the content
            result = analyze_database(content, content_type, user_prompt)
            if result:
                st.subheader("analysis result:")
                st.write(result)
