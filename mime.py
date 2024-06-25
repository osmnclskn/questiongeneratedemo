import streamlit as st
import openai
import magic
from langchain.document_loaders.parsers import BS4HTMLParser, PDFMinerParser
from langchain.document_loaders.parsers.txt import TextParser
from langchain_community.document_loaders import Blob
from dotenv import load_dotenv
import os
import json
from questiongenerate import PQMQualityControlQuestionGenerator

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# MIME türlerine göre işleyicilerin yapılandırılması
HANDLERS = {
    "application/pdf": PDFMinerParser(),
    "text/plain": TextParser(),
    "text/html": BS4HTMLParser(),
}

def get_mime_type(data):
    mime=magic.Magic(mime=True)
    return mime.from_buffer(data)

def process_uploaded_file(data):
    mime_type=get_mime_type(data)
    print(f"Mime Type :{mime_type}")

    blob=Blob.from_data(data=data,mime_type=mime_type)
    print(f"Blob created with MIME type {mime_type}")
    parser=HANDLERS.get(mime_type)
    if parser:
        documents=parser.parse(blob=blob)
        print(f"Processed Data : {documents}")
        return "".join([doc.page_content for doc in documents])
    else:
        st.error(f"No parser found for MIME Type : {mime_type}")
        return None

def display_questions(questions):
    for idx,question in enumerate(questions):
        st.write(f"{idx+1}.Generated Questions Output:")
        st.json(json.dumps(question.__dict__,indent=2))

def main():
    st.title("PQM Quality Control Question Generator")
    uploaded_file=st.file_uploader("Upload a file",type=["pdf","txt","html"])
    if uploaded_file is not None:
        st.success("File uploaded succesfully!")
        data=uploaded_file.read()

        mime_type=get_mime_type(data)
        print(f"MIME Type: {mime_type}")
        documents_content=process_uploaded_file(data)

        if documents_content:
            pqm_question_generator=PQMQualityControlQuestionGenerator()
            questions=[]
            for i in range(10):
                structured_out=pqm_question_generator.generate_question(documents_content,questions)
                questions.append(structured_out)
            display_questions(questions)

if __name__=="__main__":
    main()

