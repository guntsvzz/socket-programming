# modules/server/user_management.py

import json
import os
import hashlib
import binascii

# File to store user data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
USER_DATA_FILE = os.path.join(BASE_DIR, 'assets', 'database', 'user_data.json')

# Function to load user data from the JSON file
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    else:
        return {}

# Function to save user data to the JSON file
def save_user_data(user_data):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(user_data, file)

# Function to hash a password
def hash_password(password, salt=None):
    if salt is None:
        # Generate a new salt
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    else:
        salt = salt.encode('ascii')  # Use the existing salt

    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)

    # Return the salt and hashed password
    return (salt + pwdhash).decode('ascii')

# Function to verify a password
def verify_password(stored_password, provided_password):
    salt = stored_password[:64]
    stored_pwdhash = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'), salt.encode('ascii'), 100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_pwdhash

# Function to authenticate a user
def authenticate_user(username, password):
    users = load_user_data()
    if username in users:
        stored_password = users[username]['password']
        if verify_password(stored_password, password):
            return True
    return False

# Function for user registration
def register_user(student_id, username, password):
    users = load_user_data()
    # Check if student_id is already registered
    for user_info in users.values():
        if user_info['student_id'] == student_id:
            return False, "Student ID already registered!"
    # Check if username already exists
    if username in users:
        return False, "Username already exists!"
    hashed_password = hash_password(password)
    users[username] = {"student_id": student_id, "password": hashed_password}
    save_user_data(users)
    return True, "Registration successful! Please log in."
