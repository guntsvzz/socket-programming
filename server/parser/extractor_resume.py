import os
from typing import Optional, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
import pprint
from model import llm_groq as llm

# Define the schema with flexible sections for diverse professions
class PersonalInfo(BaseModel):
    """Schema for personal information."""
    name: Optional[str] = Field(default=None, description="The person's full name")
    phone_no: Optional[str] = Field(default=None, description="The person's phone number")
    email: Optional[str] = Field(default=None, description="The person's email address")
    website: Optional[str] = Field(default=None, description="The person's website or LinkedIn profile")

class Education(BaseModel):
    """Schema for education information."""
    degree: Optional[str] = Field(default=None, description="The degree or certification obtained")
    institution: Optional[str] = Field(default=None, description="The institution attended")
    major: Optional[str] = Field(default=None, description="Major or field of study")
    gpa: Optional[str] = Field(default=None, description="GPA or other academic metrics")

class WorkExperience(BaseModel):
    """Schema for work experience information."""
    organization: Optional[str] = Field(default=None, description="The organization or company")
    position: Optional[str] = Field(default=None, description="The position held")
    description: Optional[str] = Field(default=None, description="Details of responsibilities or achievements")
    duration: Optional[str] = Field(default=None, description="Duration of employment or association")

class Certification(BaseModel):
    """Schema for certifications and professional development."""
    title: Optional[str] = Field(default=None, description="Title of the certification or training")
    issuing_organization: Optional[str] = Field(default=None, description="The organization that issued it")
    date_issued: Optional[str] = Field(default=None, description="Date when it was issued")

class Skill(BaseModel):
    """Schema for skills."""
    technical_skills: Optional[str] = Field(default=None, description="Technical skills, if any")
    soft_skills: Optional[str] = Field(default=None, description="Soft skills such as leadership, communication")
    languages: Optional[str] = Field(default=None, description="Languages known")

class ProjectOrPublication(BaseModel):
    """Schema for projects or publications."""
    title: Optional[str] = Field(default=None, description="Title of the project or publication")
    description: Optional[str] = Field(default=None, description="Brief description")
    collaborators: Optional[str] = Field(default=None, description="Collaborators or co-authors, if applicable")
    date: Optional[str] = Field(default=None, description="Date of completion or publication")

class ResumeSchema(BaseModel):
    """Generalized schema for resume information."""
    personal_info: Optional[PersonalInfo] = Field(default=None, description="Personal information section")
    education: Optional[List[Education]] = Field(default=None, description="Education background")
    work_experience: Optional[List[WorkExperience]] = Field(default=None, description="List of work experiences")
    certifications: Optional[List[Certification]] = Field(default=None, description="Certifications and training")
    skills: Optional[Skill] = Field(default=None, description="List of skills")
    projects_and_publications: Optional[List[ProjectOrPublication]] = Field(
        default=None, description="List of projects or publications"
    )

# Enhanced prompt to accommodate diverse fields
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert in extracting structured information from resumes. "
        "Extract the relevant information for each section specified in the schema. "
        "If any section is unavailable, return null for that section."
    ),
    ("human", "{text}")
])

# Set up runnable with structured output for the defined schema
runnable = prompt | llm.with_structured_output(schema=ResumeSchema)

# Function to extract information from resume text
def extractor(prompt_text: str):
    result = runnable.invoke({"text": prompt_text})
    return result.dict()  # Convert the result to a dictionary