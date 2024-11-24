
import os
from typing import Optional, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
import pprint
from model import llm_groq as llm

# Define the schema with flexible sections for diverse job descriptions
class JobTitle(BaseModel):
    """Schema for job title."""
    title: Optional[str] = Field(default=None, description="The job title")

class CompanyInfo(BaseModel):
    """Schema for company information."""
    name: Optional[str] = Field(default=None, description="The company's name")
    location: Optional[str] = Field(default=None, description="The company's location")
    industry: Optional[str] = Field(default=None, description="The industry of the company")

class JobResponsibilities(BaseModel):
    """Schema for job responsibilities."""
    responsibilities: Optional[List[str]] = Field(default=None, description="List of job responsibilities")

class RequiredSkills(BaseModel):
    """Schema for required skills."""
    skills: Optional[List[str]] = Field(default=None, description="List of required skills")

class JobDescriptionSchema(BaseModel):
    """Generalized schema for job description information."""
    job_title: Optional[JobTitle] = Field(default=None, description="Job title section")
    company_info: Optional[CompanyInfo] = Field(default=None, description="Company information section")
    job_responsibilities: Optional[JobResponsibilities] = Field(default=None, description="Job responsibilities")
    required_skills: Optional[RequiredSkills] = Field(default=None, description="Required skills")

# Enhanced prompt to accommodate diverse fields in job descriptions
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert in extracting structured information from job descriptions. "
        "Extract the relevant information for each section specified in the schema. "
        "If any section is unavailable, return null for that section."
    ),
    ("human", "{text}")
])

# Set up runnable with structured output for the defined schema
runnable = prompt | llm.with_structured_output(schema=JobDescriptionSchema)

# Function to extract information from job description text
def extractor(prompt_text: str):
    result = runnable.invoke({"text": prompt_text})
    return result.dict()  # Convert the result to a dictionary