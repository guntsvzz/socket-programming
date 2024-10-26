# streamlit_client.py

import streamlit as st
from modules.client.client_utils import send_voice_file_tcp
from modules.utils import bcolors
from authentication import authentication_flow  # Import the authentication_flow from the new file
from st_audiorec import st_audiorec  # Assuming you have this component or similar
import os

def chat_interface():
    print("Entered chat_interface")
    st.title("MemoryGPT")

    if 'messages' not in st.session_state:
        st.session_state['messages'] = []

    # Create footer container for the microphone
    footer_container = st.container()
    with footer_container:
        audio_bytes = st_audiorec()

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Process audio input
    if audio_bytes:
        auth_token = st.session_state.get('auth_token')
        if auth_token:
            with st.spinner("Processing..."):
                # Send the audio to the server
                status_code, response, headers, status_line = send_voice_file_tcp(audio_bytes, auth_token)
                print(f"{bcolors.OKBLUE}Voice file upload response: {status_code}{bcolors.ENDC}")
                if headers:
                    print(f"{bcolors.OKGREEN}{status_line}{bcolors.ENDC}")
                    for header, value in headers.items():
                        print(f"{bcolors.OKGREEN}{header}: {value}{bcolors.ENDC}")
                else:
                    print("No headers received.")

                if status_code == '200':
                    # Extract the transcribed text from headers
                    transcribed_text = headers.get('x-transcribed-text', "No transcribed text received.")
                    response_text = headers.get('x-response-text', "No response text received.")

                    # Append the user's transcribed message to the chat
                    st.session_state.messages.append({"role": "user", "content": transcribed_text})

                    # Save the received audio response from the server
                    received_audio_path = "received_response.wav"
                    with open(received_audio_path, "wb") as f:
                        f.write(response)

                    # Display the user's message
                    with st.chat_message("user"):
                        st.write(transcribed_text)

                    # Display the assistant's message with audio and transcribed text
                    with st.chat_message("assistant"):
                        st.audio(received_audio_path, format='audio/wav')
                        st.write(response_text)  # Display the bot's transcribed response

                    # Add the assistant's message to the session state
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                else:
                    print(f"Error status code received: {status_code}")
                    print(f"Error response: {response}")
                    st.error(response)
        else:
            st.error("No authentication token. Please log in again.")

def logout():
    print("User logged out")
    st.session_state['logged_in'] = False
    st.session_state['username'] = None
    st.session_state['auth_token'] = None
    st.session_state['messages'] = []
    st.info("You have been logged out.")
    st.experimental_rerun()

def main():
    print("Running main function")
    print(f"st.session_state: {st.session_state}")

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['username'] = None
        st.session_state['auth_token'] = None
        st.session_state['messages'] = []

    if not st.session_state['logged_in']:
        authentication_flow()
    else:
        st.sidebar.write(f"Logged in as {st.session_state['username']}")

        if st.sidebar.button("Logout"):
            logout()

    chat_interface()

if __name__ == '__main__':
    print("Executing main")
    main()
