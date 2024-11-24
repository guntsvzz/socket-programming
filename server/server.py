import socket
import threading
from login import handle_login
from registration import handle_registration
from resume import handle_upload_resume
from job_description import handle_upload_job_description
from text import handle_text
from interview_question import handle_interview
from datetime import datetime
import json
import os

# Ensure the assets/database directory exists
os.makedirs("../assets/database", exist_ok=True)

def format_response(status_code, message):
    """Format the response with a status code, headers, and a JSON message body."""
    # response_line = f"HTTP/1.1 {status_code}\r\n"
    response_line = f"{status_code}\r\n"
    headers = {
        "Content-Type": "application/json",
        "Date": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"),
        "Connection": "close",
    }
    body = json.dumps({"message": message})
    headers["Content-Length"] = str(len(body))

    headers_formatted = "".join(f"{key}: {value}\r\n" for key, value in headers.items())
    return response_line + headers_formatted + "\r\n" + body


def handle_client(client_socket):
    while True:
        try:
            # Receive the request message
            request_message = client_socket.recv(4096).decode('utf-8')
            if not request_message:
                break

            # Print the full request message for logging
            print("Received Request:\n" + request_message + "\n" + "-" * 50)

            # Parse the request
            request_lines = request_message.split('\r\n')
            request_line = request_lines[0]
            headers = {}
            i = 1
            while request_lines[i]:
                key, value = request_lines[i].split(': ', 1)
                headers[key] = value
                i += 1
            try:
                body = json.loads(request_lines[i+1])
            except json.JSONDecodeError:
                response = format_response("400 Bad Request", "Invalid JSON format")
                client_socket.send(response.encode('utf-8'))
                break

            # Log the parsed request details
            print(f"Request Line: {request_line}")
            print("Headers:")
            for header_name, header_value in headers.items():
                print(f"  {header_name}: {header_value}")
            print("Body:", body)
            print("-" * 50)

            # Determine action based on request line
            if request_line.startswith("POST /login"):
                status_code, message = handle_login(body)

            elif request_line.startswith("POST /register"):
                status_code, message = handle_registration(body)

            elif request_line.startswith("POST /upload_resume"):
                status_code, message = handle_upload_resume(body)
                
            elif request_line.startswith("POST /upload_job_description"):
                status_code, message = handle_upload_job_description(body)

            elif request_line.startswith("POST /interview_question"):
                status_code, message = handle_interview(body)

            elif request_line.startswith("POST /send_text"):
                status_code, message = handle_text(body) #"200 OK", f"Received text: {body.get('text_message')}"

            else:
                status_code, message = "404 Not Found", "Invalid action"

            # Send response back to client
            response = format_response(status_code, message)
            client_socket.send(response.encode('utf-8'))

        except Exception as e:
            print(f"An error occurred: {e}")
            response = format_response("500 Internal Server Error", str(e))
            client_socket.send(response.encode('utf-8'))
            # break

    client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 9999))
    server_socket.listen(5)
    print("Server listening on port 9999")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Accepted connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == '__main__':
    start_server()
