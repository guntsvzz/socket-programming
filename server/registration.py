import json
import os

def handle_registration(body):
    # Check if student_id, username, or password is None or an empty string
    student_id = body.get('student_id')
    username = body.get('username')
    password = body.get('password')
    
    if not student_id or not username or not password:
        return "400 Bad Request", "Registration failed: student_id, username, and password are required and cannot be empty."
    
    user_data = {
        'student_id': student_id,
        'username': username,
        'password': password,
        'resume': {},
        'job_description': {},
        'questions': {},
        'conversation': {}
    }

    file_path = f"../assets/database/{username}.json"
    if os.path.exists(file_path):
        return "400 Bad Request", f"Registration failed: User {username} already exists."
    
    os.makedirs("../assets/database", exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(user_data, f, indent=4)

    return "200 OK", f"User {username} registered successfully and data saved to {file_path}."
