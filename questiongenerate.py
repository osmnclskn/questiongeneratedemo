import json
import os
from typing import List, Optional

import openai
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI

load_dotenv()

class Question(BaseModel):
    category: str = Field(description="Determine the category based on the topic.")
    title: str = Field(description="A concise title for the question.")
    question: str = Field(description="Clearly state the question.")
    answer_options: List[str] = Field(description="[\"Yes\", \"No\"], [\"Pass\", \"Fail\"]")
    reason: Optional[str] = Field(description="Explain why this question is significant for quality control concerning the topic provided.")


class PQMQualityControlQuestionGenerator:
    def __init__(self,human_message_template=None):
        api_key = os.getenv("OPENAI_API_KEY")
        self.llm = ChatOpenAI(api_key=api_key, model="gpt-3.5-turbo", temperature=0)
        self.system_message_content = "You are an AI trained to assist in generating detailed and context-specific quality control questions."
        self.human_message_template = human_message_template if human_message_template is not  None else  """
            As an expert in quality control, generate a precise and actionable quality control question based on the document content provided below. \\
            also the question shouldn't be in the old questions. Ensure the question is suitable for a quality control checklist.

            Document Content: {doc_content}
            Old Question(s): {old_questions}
        """ 
        self.structured_llm = self.llm.with_structured_output(Question)

    def generate_question(self, doc_content, old_questions):
        human_message_content = self.human_message_template.format(doc_content=doc_content, old_questions=old_questions)
        messages = [
            SystemMessage(content=self.system_message_content),
            HumanMessage(content=human_message_content)
        ]
        response = self.structured_llm.invoke(input=messages)
        return response

    def parse_response_to_json(self, content):
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {}