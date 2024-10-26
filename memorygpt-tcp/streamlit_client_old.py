# streamlit_client.py

print("Starting Streamlit client application")

import streamlit as st
from st_audiorec import st_audiorec
from modules.utils import bcolors
from modules.client.client_utils import send_authentication_request, send_voice_file_tcp
import base64

def authentication_flow():
    print("Entered authentication_flow")
    st.sidebar.title("Login / Register")
    menu = st.sidebar.selectbox("Menu", ["Login", "Register"])

    if menu == "Login":
        username = st.sidebar.text_input("User")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            status_code, message, headers, auth_header, status_line = send_authentication_request('login', username, password)
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
            status_code, message, headers, _, status_line = send_authentication_request('register', username, password, student_id=student_id)
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

def voice_recorder():
    print("Entered voice_recorder")
    st.title("Voice Recorder")

    audio_data = st_audiorec()

    if audio_data is not None:
        st.audio(audio_data, format='audio/wav')
        st.write(f"Recorded audio data size: {len(audio_data)} bytes")

        if st.button("Send to server"):
            auth_token = st.session_state.get('auth_token')
            if auth_token:
                token = auth_token
                status_code, response, headers, status_line = send_voice_file_tcp(audio_data, token)
                print(f"{bcolors.OKBLUE}Voice file upload response: {status_code}{bcolors.ENDC}")
                if headers:
                    print(f"{bcolors.OKGREEN}{status_line}{bcolors.ENDC}")
                    for header, value in headers.items():
                        print(f"{bcolors.OKGREEN}{header}: {value}{bcolors.ENDC}")
                else:
                    print("No headers received.")

                if status_code == '200':
                    # Decode base64-encoded data
                    decoded_data = base64.b64decode(response)
                    with open("received_return_voice.wav", "wb") as f:
                        f.write(decoded_data)
                    st.success("Received processed voice from server.")
                    st.audio("received_return_voice.wav", format='audio/wav')
                    # Print base64-encoded data
                    print(f"{bcolors.WARNING}Data Returned (Base64): {response}{bcolors.ENDC}")
                else:
                    print(f"Error status code received: {status_code}")
                    print(f"Error response: {response}")
                    # print(f"{bcolors.WARNING}Data Returned: {response}{bcolors.ENDC}")
                    st.error(response)
            else:
                st.error("No authentication token. Please log in again.")

def logout():
    print("User logged out")
    st.session_state['logged_in'] = False
    st.session_state['username'] = None
    st.session_state['auth_token'] = None
    st.info("You have been logged out.")
    st.experimental_rerun()

def main():
    print("Running main function")
    print(f"st.session_state: {st.session_state}")

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['username'] = None
        st.session_state['auth_token'] = None

    if not st.session_state['logged_in']:
        authentication_flow()
    else:
        st.sidebar.write(f"Logged in as {st.session_state['username']}")

        if st.sidebar.button("Logout"):
            logout()

        voice_recorder()

if __name__ == '__main__':
    print("Executing main")
    main()
