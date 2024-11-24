import json
import os
from reader import reader
from parser.extractor_job_description import extractor

def handle_upload_job_description(body):
    username = body.get("username")
    resume_file_path = body.get("filename")

    # Check if the file extension is PDF
    if not resume_file_path.lower().endswith('.pdf'):
        return "400 Bad Request", "The uploaded file is not a PDF."

    file_path = f"../assets/database/{username}.json"
    
    # Check if the user exists
    if not os.path.exists(file_path):
        return "404 Not Found", f"User {username} does not exist."
    
    # Read the resume document using the fake_function
    try:
        resume_content = reader(resume_file_path)
        resume_content = extractor(prompt_text=resume_content['content'])
    except Exception as e:
        return "500 Internal Server Error", f"Error reading resume file: {str(e)}"
    
    # Load the existing user data
    with open(file_path, 'r') as f:
        user_data = json.load(f)
    
    # Update the job description section
    user_data['job_description'] = resume_content
    
    # Save the updated data back to the file
    with open(file_path, 'w') as f:
        json.dump(user_data, f, indent=4)
    
    return "200 OK", f"Job description uploaded successfully and extracted data done for user {username}."