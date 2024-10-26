# authentication.py

import streamlit as st
from modules.client.client_utils import send_authentication_request
from modules.utils import bcolors

def authentication_flow():
    print("Entered authentication_flow")
    st.sidebar.title("Login / Register")
    menu = st.sidebar.selectbox("Menu", ["Login", "Register"])

    if menu == "Login":
        username = st.sidebar.text_input("User")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            status_code, message, headers, auth_header, status_line = send_authentication_request(
                'login', username, password)
            print(f"{bcolors.OKBLUE}Login response: {status_code}, {message}{bcolors.ENDC}")
            print(f"{bcolors.OKGREEN}{status_line}{bcolors.ENDC}")
            if headers:
                for header, value in headers.items():
                    print(f"{bcolors.OKGREEN}{header}: {value}{bcolors.ENDC}")
            else:
                print("No headers received.")
            print(f"{bcolors.WARNING}Data Returned: {message}{bcolors.ENDC}")
            if status_code == '200':
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.session_state['auth_token'] = auth_header  # Store the token
                st.sidebar.success(message)
                st.experimental_rerun()
            else:
                st.sidebar.error(message)
    elif menu == "Register":
        student_id = st.sidebar.text_input("Student ID")
        username = st.sidebar.text_input("User")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Register"):
            status_code, message, headers, _, status_line = send_authentication_request(
                'register', username, password, student_id=student_id)
            print(f"{bcolors.OKBLUE}Registration response: {status_code}, {message}{bcolors.ENDC}")
            print(f"{bcolors.OKGREEN}{status_line}{bcolors.ENDC}")
            if headers:
                for header, value in headers.items():
                    print(f"{bcolors.OKGREEN}{header}: {value}{bcolors.ENDC}")
                print(f"{bcolors.WARNING}Data Returned: {message}{bcolors.ENDC}")
            else:
                print("No headers received.")
            if status_code == '200':
                st.sidebar.success(message)
            else:
                st.sidebar.error(message)
