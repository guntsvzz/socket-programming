import os
from glob import glob
# import subprocess

import openai
from openai import OpenAI, AzureOpenAI
from dotenv import load_dotenv

from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_community.chat_models import ChatOpenAI, AzureChatOpenAI
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory

load_dotenv("../.env")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_version = os.getenv("OPENAI_API_VERSION")

client = AzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=azure_endpoint)

def base_model_chatbot(messages):
    system_message = [
        {
            "role": "system", 
            "content": "You are an helpful AI chatbot, that answers questions asked by User."
        }
    ]
    messages = system_message + messages
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=128
    )
    return response.choices[0].message.content


class VectorDB:
    """Class to manage document loading and vector database creation."""
    def __init__(self, docs_directory:str):
        self.docs_directory = docs_directory

    def create_vector_db(self):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        files = glob(os.path.join(self.docs_directory, "*.pdf"))
        loadPDFs = [PyPDFLoader(pdf_file) for pdf_file in files]
        pdf_docs = list()
        for loader in loadPDFs:
            pdf_docs.extend(loader.load())
        chunks = text_splitter.split_documents(pdf_docs)
            
        return Chroma.from_documents(chunks, AzureOpenAIEmbeddings()) 
    
class ConversationalRetrievalChain:
    """Class to manage the QA chain setup."""

    def __init__(self, model_name="gpt-4o-mini", temperature=0):
        self.model_name = model_name
        self.temperature = temperature
      
    def create_chain(self):
        model = AzureChatOpenAI(model_name=self.model_name,
                           temperature=self.temperature,
                           )
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
            )
        vector_db = VectorDB('docs/')
        retriever = vector_db.create_vector_db().as_retriever(search_type="similarity",
                                                              search_kwargs={"k": 2},
                                                              )
        return RetrievalQA.from_chain_type(
            llm=model,
            retriever=retriever,
            memory=memory,
            )
    
def with_pdf_chatbot(messages):
    """Main function to execute the QA system."""
    query = messages[-1]['content'].strip()
    qa_chain = ConversationalRetrievalChain().create_chain()
    result = qa_chain({"query": query})
    return result['result']
