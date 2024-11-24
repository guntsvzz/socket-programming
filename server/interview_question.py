from pydantic import BaseModel, Field
from typing import Optional
from langchain_core.output_parsers import JsonOutputParser
from model import llm_groq
from langchain_core.prompts.prompt import PromptTemplate
import os
import json

# Define the output structure for interview questions
class QuestionCategory(BaseModel):
    pre_screen: list[str] = Field(description="List of pre-screening questions")
    technical_skill: list[str] = Field(description="List of technical skill questions")
    job_specific_task: list[str] = Field(description="List of job-specific task questions")
    # assessment: list[str] = Field(description="List of assessment questions")

class AttitudeCategory(BaseModel):
    behavioral: list[str] = Field(description="List of behavioral questions")
    situational: list[str] = Field(description="List of situational questions")
    cultural_fit: list[str] = Field(description="List of cultural fit questions")
    motivational: list[str] = Field(description="List of motivational questions")
    soft_skill: list[str] = Field(description="List of soft skill questions")
    open_end: list[str] = Field(description="List of open end & reflection questions")
    
class StandardPersonalizedQuestions(BaseModel):
    skill_based: QuestionCategory = Field(description="Skill-based questions category")
    attitude_based: AttitudeCategory = Field(description="Attitude-based questions category")

# Set up JSON output parser for StandardPersonalizedQuestions
parser = JsonOutputParser(pydantic_object=StandardPersonalizedQuestions)

text = """
You are helping an interviewer prepare challenging and insightful questions for assessing a candidate.
Your goal is to generate a comprehensive list of questions that enable the interviewer to evaluate the candidate’s skills, experience, and fit for the role effectively.

# STEPS
- Wait until you receive input data for context. Do not proceed until this information is provided.
- Based on the input data, identify the 10 most challenging questions the interviewer might ask to thoroughly evaluate the candidate.
- For each challenging question:
- Develop a detailed optimal answer (as an example of what an ideal response might look like).
- Provide an explanation for why this answer is effective and what it demonstrates.
- Create a relevant follow-up question to encourage deeper discussion.
- Then, think of 20 additional likely interview questions that the interviewer might use for further assessment.
- Summarize top interviewing tips in a GENERAL TIPS section for conducting an effective interview.

# OUTPUT INSTRUCTIONS
Output only the requested sections in human-readable Markdown.
- Avoid introductory text, disclaimers, or notes.
- Use bullet points for lists and avoid numbering.
- Avoid cliches, jargon, and journalistic language.
- Do not include phrases like 'In conclusion' or 'To sum up.'
- Only output the requested sections.

{format_instructions}
Input:
{input_data}"""

prompt_question = PromptTemplate(
    template = text,
    input_variables=["input_data"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

llm = llm_groq

# Run the chain to generate personalized questions based on the input
question_chain = prompt_question | llm | parser

def handle_interview(body):
    username = body.get("username")
    file_path = f"../assets/database/{username}.json"
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            user_data = json.load(f)
            
        input_data = {
            "resume": user_data['resume'],
            "job_description": user_data['job_description'],
        }
        interview_questions = question_chain.invoke({"input_data": input_data})
        
        
            # Load the existing user data
        with open(file_path, 'r') as f:
            user_data = json.load(f)
        
        # Update the resume section
        user_data['questions'] = interview_questions
        
        # Save the updated data back to the file
        with open(file_path, 'w') as f:
            json.dump(user_data, f, indent=4)
            
        return "200 OK", f"Generated Question successfully for user {username}."
    else:
        return "404 Not Found", "Login failed: User does not exist."