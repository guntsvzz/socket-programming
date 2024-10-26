# modules/server/client_handler.py

import socket
import json
import os
from datetime import datetime, timezone
import uuid

from .user_management import (
    authenticate_user,
    register_user
)

from modules.speech import speech_to_text, text_to_speech  # Import speech functions
from modules.generate_answer import base_model_chatbot  # Import chatbot function
from modules.utils import bcolors  # Import bcolors for colored output

BUFFER_SIZE = 4096

# Global token store (for simplicity)
tokens = {}  # token: username

def read_line(conn):
    line = b''
    while not line.endswith(b'\r\n'):
        chunk = conn.recv(1)
        if not chunk:
            break
        line += chunk
    return line.decode('utf-8', errors='replace').strip()

def read_headers(conn):
    headers = {}
    headers_raw = ''
    while True:
        header_line = read_line(conn)
        if header_line == '':
            break
        headers_raw += header_line + '\r\n'
        if ':' in header_line:
            key, value = header_line.split(':', 1)
            headers[key.strip()] = value.strip()
    return headers, headers_raw

def send_response(conn, status_code, reason_phrase, headers, body):
    # Construct the status line
    response_line = f"HTTP/1.1 {status_code} {reason_phrase}\r\n"

    # Construct the headers
    headers_lines = ''
    for header, value in headers.items():
        headers_lines += f"{header}: {value}\r\n"
    headers_lines += "\r\n"  # End of headers

    # Prepare the body
    if isinstance(body, str):
        body_bytes = body.encode('utf-8')
    elif isinstance(body, bytes):
        body_bytes = body
    else:
        # If the body is a dictionary, serialize it to JSON
        body_bytes = json.dumps(body).encode('utf-8')

    # Determine how to print the body based on Content-Type
    content_type = headers.get("Content-Type", "")
    if content_type.startswith("application/json") or content_type.startswith("text/plain"):
        try:
            body_to_print = body.decode('utf-8')
        except Exception:
            body_to_print = "<unable to decode body>"
    else:
        body_to_print = f"<binary data: {len(body_bytes)} bytes>"

    # Print the response with colors
    print(f"{bcolors.OKBLUE}HTTP Response Message:{bcolors.ENDC}")
    print(f"{bcolors.OKGREEN}{response_line}{headers_lines}{body_to_print}{bcolors.ENDC}")

    # Send the response
    conn.sendall(response_line.encode('utf-8'))
    conn.sendall(headers_lines.encode('utf-8'))
    conn.sendall(body_bytes)

def handle_client(conn):
    try:
        # Read the request line
        request_line = read_line(conn)
        print(f"Request Line: {request_line}")

        # Read headers
        headers, headers_raw = read_headers(conn)

        # Get Content-Length
        content_length = int(headers.get('Content-Length', 0))

        # Read the request body
        body = b''
        if content_length > 0:
            remaining = content_length
            while remaining > 0:
                chunk = conn.recv(min(BUFFER_SIZE, remaining))
                if not chunk:
                    break
                body += chunk
                remaining -= len(chunk)

        # Decode the body if it's not binary data
        path = request_line.split(' ')[1]
        if path in ['/login', '/register']:
            body_decoded = body.decode('utf-8')
        else:
            body_decoded = '<binary data>'

        # Reconstruct and print the full HTTP request message with colors
        full_request = request_line + '\r\n' + headers_raw + '\r\n'
        if path in ['/login', '/register']:
            full_request += body_decoded
        print(f"{bcolors.OKBLUE}HTTP Request Message:{bcolors.ENDC}")
        print(f"{bcolors.OKGREEN}{full_request}{bcolors.ENDC}")

        # Process the request
        if path in ['/login', '/register']:
            body_data = json.loads(body_decoded)

            # Prepare response variables
            response_body = {}
            headers_to_send = {
                "Content-Type": "application/json",
                "Date": datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT'),
            }
            login_success = False

            if path == "/login":
                username = body_data.get('username')
                password = body_data.get('password')
                if authenticate_user(username, password):
                    # Generate token
                    token = str(uuid.uuid4())
                    tokens[token] = username  # Store token
                    response_body['message'] = "Login successful"
                    status_code = 200
                    reason_phrase = "OK"
                    headers_to_send["Connection"] = "keep-alive"
                    headers_to_send["Authorization"] = f"Bearer {token}"
                    login_success = True
                else:
                    response_body['message'] = "Login failed"
                    status_code = 401
                    reason_phrase = "Unauthorized"
                    headers_to_send["Connection"] = "close"

            elif path == "/register":
                student_id = body_data.get('student_id')
                username = body_data.get('username')
                password = body_data.get('password')
                success, message = register_user(student_id, username, password)
                response_body['message'] = message
                if success:
                    status_code = 200
                    reason_phrase = "OK"
                else:
                    status_code = 400
                    reason_phrase = "Bad Request"
                headers_to_send["Connection"] = "close"
            else:
                response_body['message'] = "Invalid action"
                status_code = 404
                reason_phrase = "Not Found"
                headers_to_send["Connection"] = "close"

            # Calculate Content-Length
            body_bytes = json.dumps(response_body).encode('utf-8')
            headers_to_send["Content-Length"] = str(len(body_bytes))

            # Send response
            send_response(conn, status_code, reason_phrase, headers_to_send, body_bytes)

            if not login_success:
                conn.close()
                return  # Exit the function since login failed

        else:
            # For other paths, need to check authorization
            auth_header = headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                # Missing or invalid token
                response_body = {"message": "Unauthorized"}
                body_bytes = json.dumps(response_body).encode('utf-8')
                response_headers = {
                    "Content-Type": "application/json",
                    "Content-Length": str(len(body_bytes)),
                    "Date": datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT'),
                    "Connection": "close"
                }
                send_response(conn, 401, "Unauthorized", response_headers, body_bytes)
                conn.close()
                return  # Exit the function

            token = auth_header.split('Bearer ')[1]
            if token not in tokens:
                # Invalid token
                response_body = {"message": "Unauthorized"}
                body_bytes = json.dumps(response_body).encode('utf-8')
                response_headers = {
                    "Content-Type": "application/json",
                    "Content-Length": str(len(body_bytes)),
                    "Date": datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT'),
                    "Connection": "close"
                }
                send_response(conn, 401, "Unauthorized", response_headers, body_bytes)
                conn.close()
                return  # Exit the function

            # Valid token
            username = tokens[token]

            if path == "/upload":
                # Save the received voice file
                received_voice_path = "received_voice.wav"
                with open(received_voice_path, "wb") as f:
                    f.write(body)

                print(f"Voice file received from {username}. Total bytes: {len(body)}")

                # Perform speech-to-text
                transcript = speech_to_text(received_voice_path)
                if not transcript:
                    response_body = {"message": "Failed to transcribe audio"}
                    body_bytes = json.dumps(response_body).encode('utf-8')
                    response_headers = {
                        "Content-Type": "application/json",
                        "Content-Length": str(len(body_bytes)),
                        "Date": datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT'),
                        "Connection": "keep-alive"
                    }
                    send_response(conn, 500, "Internal Server Error", response_headers, body_bytes)
                    conn.close()
                    return

                # Generate chatbot response
                messages = [{"role": "user", "content": transcript}]
                response_text = base_model_chatbot(messages)

                # Convert response text to speech
                audio_file_path = text_to_speech(response_text)
                if not audio_file_path or not os.path.exists(audio_file_path):
                    response_body = {"message": "Failed to generate audio response"}
                    body_bytes = json.dumps(response_body).encode('utf-8')
                    response_headers = {
                        "Content-Type": "application/json",
                        "Content-Length": str(len(body_bytes)),
                        "Date": datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT'),
                        "Connection": "keep-alive"
                    }
                    send_response(conn, 500, "Internal Server Error", response_headers, body_bytes)
                    conn.close()
                    return

                # Read the audio file to send back
                with open(audio_file_path, "rb") as f:
                    audio_data = f.read()

                # Prepare headers
                response_headers = {
                    "Date": datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT'),
                    "Server": "SimplePythonServer",
                    "Content-Type": "audio/wav",
                    "Content-Length": str(len(audio_data)),
                    "Connection": "keep-alive",
                    "X-Response-Text": response_text,          # Bot's response text
                    "X-Transcribed-Text": transcript           # User's transcribed text
                }

                # Send response with colored output
                print(f"{bcolors.OKBLUE}HTTP Response Message:{bcolors.ENDC}")
                print(f"{bcolors.OKGREEN}HTTP/1.1 200 OK\r\n" +
                      f"Date: {response_headers['Date']}\r\n" +
                      f"Server: {response_headers['Server']}\r\n" +
                      f"Content-Type: {response_headers['Content-Type']}\r\n" +
                      f"Content-Length: {response_headers['Content-Length']}\r\n" +
                      f"Connection: {response_headers['Connection']}\r\n" +
                      f"X-Response-Text: {response_headers['X-Response-Text']}\r\n" +
                      f"X-Transcribed-Text: {response_headers['X-Transcribed-Text']}\r\n\r\n" +
                      f"{len(audio_data)} bytes of audio data.{bcolors.ENDC}")

                # Send response
                send_response(conn, 200, "OK", response_headers, audio_data)
                print(f"Sent audio response to {username}.")

                # Clean up temporary files
                os.remove(received_voice_path)
                os.remove(audio_file_path)

            else:
                # Invalid path after login
                response_body = {"message": "Invalid request after login"}
                body_bytes = json.dumps(response_body).encode('utf-8')
                response_headers = {
                    "Content-Type": "application/json",
                    "Content-Length": str(len(body_bytes)),
                    "Date": datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT'),
                    "Connection": "keep-alive"
                }
                send_response(conn, 400, "Bad Request", response_headers, body_bytes)
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        conn.close()
