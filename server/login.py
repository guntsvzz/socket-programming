import os
import json

def handle_login(body):
    username = body.get('username')
    password = body.get('password')

    # Check if either username or password is None
    if not username or not password:
        return "400 Bad Request", "Login failed: Username and password are required."

    file_path = f"../assets/database/{username}.json"

    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            user_data = json.load(f)

        if user_data['username'] == username and user_data['password'] == password:
            return "200 OK", f"User {username} logged in successfully."
        else:
            return "400 Bad Request", "Login failed: Incorrect username or password."
    else:
        return "404 Not Found", "Login failed: User does not exist."
