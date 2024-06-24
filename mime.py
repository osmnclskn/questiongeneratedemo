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

def main():
    st.title("Document Processor")

    uploaded_file = st.file_uploader('Upload a file', type=["pdf", "txt", "html"])
    
    if uploaded_file is not None:
        st.success("File uploaded successfully!")
        data = uploaded_file.read()

        # MIME türünün belirlenmesi
        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(data)
        st.write(f"MIME Type: {mime_type}")
        print(f"MIME Type: {mime_type}")

        # Blob oluşturma
        blob = Blob.from_data(
            data=data,
            mime_type=mime_type,
        )
        print(f"Blob created with MIME type {mime_type}")
        
        parser = HANDLERS.get(mime_type)
        if parser:
            documents = parser.parse(blob=blob)
            st.write(f"Processed Data: {documents}")
            print(f"Processed Data: {documents}")

            # Documents içeriğini stringe çevirme
            documents_content = " ".join([doc.page_content for doc in documents])
        
            pqm_question_generator = PQMQualityControlQuestionGenerator()

            # OpenAI ile soru üretme
            questions=[]
            for i in range(10):
                structured_out = pqm_question_generator.generate_question(documents_content, questions)
                questions.append(structured_out)
                

            for idx in range(len(questions)):
                st.write(f"{idx+1}. Question JSON Output: ")
                st.json(json.dumps(questions[idx].__dict__, indent=2))
        else:
            st.error(f"No parser found for MIME Type: {mime_type}")
        
if __name__ == "__main__":
    main()