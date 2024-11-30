from langchain_groq import ChatGroq
from langchain_openai import AzureChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv("../.env")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_version = os.getenv("OPENAI_API_VERSION")
groq_api_key = os.getenv("GROQ_API_KEY")

# llm_groq = ChatGroq(
#     model="llama3-8b-8192",
#     groq_api_key=groq_api_key
# )

llm_groq = AzureChatOpenAI(
    model       = 'gpt-4o-mini',
    verbose     = True,
    temperature = 0,
    # max_tokens  = 256
)