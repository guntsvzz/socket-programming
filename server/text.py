import os
from glob import glob
# import subprocess

import openai
from openai import OpenAI, AzureOpenAI
from dotenv import load_dotenv
from groq import Groq

load_dotenv("../.env")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_version = os.getenv("OPENAI_API_VERSION")
groq_api_key = os.getenv("GROQ_API_KEY")

def base_model_chatbot(messages, model="groq"):
    system_message = [
        {
            "role": "system", 
            "content": "You are an helpful AI chatbot, that answers questions asked by User."
        }
    ]
    
    messages = system_message + messages
    if model == 'openai':
        
        client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=azure_endpoint)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=128
        )
    elif model =='groq':
        
        client = Groq(
            api_key=groq_api_key)
                
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages = messages,
        )
    return response.choices[0].message.content

def handle_text(body):
    # Ensure messages is a list of dictionaries
    messages = body.get('text_message')
    
    if isinstance(messages, str):
        # Convert a single message string into a list format
        messages = [{"role": "user", "content": messages}]
    
    try:
        response = base_model_chatbot(messages)
        return "200 OK", f"{response}"
    
    except Exception as e:
        return "500 Internal Server Error", f"An error occurred: {str(e)}"
