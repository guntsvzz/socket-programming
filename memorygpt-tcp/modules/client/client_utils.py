# modules/client/client_utils.py

import socket
import json
from modules.utils import bcolors  # Import bcolors for colored output

BUFFER_SIZE = 4096

def read_line(sock):
    line = b''
    while not line.endswith(b'\r\n'):
        chunk = sock.recv(1)
        if not chunk:
            break
        line += chunk
    return line.decode('utf-8', errors='replace').strip()

def read_headers(sock):
    headers = {}
    while True:
        header_line = read_line(sock)
        if header_line == '':
            break
        if ':' in header_line:
            key, value = header_line.split(':', 1)
            headers[key.strip().lower()] = value.strip()
    return headers

def send_authentication_request(action, username, password, student_id=None, host='localhost', port=8888):
    client_socket = None
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(10)
        client_socket.connect((host, port))
        print("Connected to the server.")

        if action == 'login':
            request_line = "POST /login HTTP/1.1"
            body_data = {
                'username': username,
                'password': password
            }
        elif action == 'register':
            request_line = "POST /register HTTP/1.1"
            body_data = {
                'student_id': student_id,
                'username': username,
                'password': password
            }
        else:
            client_socket.close()
            return None, "Invalid action", None, None, None

        body = json.dumps(body_data)
        headers = {
            "Host": host,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:80.0) Gecko/20100101 Firefox/80.0",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Content-Type": "application/json",
            "Content-Length": str(len(body)),
            "Connection": "keep-alive"
        }

        # Construct the HTTP request message
        request_message = request_line + "\r\n"
        for header_name, header_value in headers.items():
            request_message += f"{header_name}: {header_value}\r\n"
        request_message += "\r\n"
        request_message += body

        # Print the HTTP request message with colors
        print(f"{bcolors.OKBLUE}HTTP Request Message:{bcolors.ENDC}")
        print(f"{bcolors.OKGREEN}{request_message}{bcolors.ENDC}")

        # Send the request
        client_socket.sendall(request_message.encode('utf-8'))

        # Read the response
        response_line = read_line(client_socket)
        if response_line:
            parts = response_line.strip().split(' ')
            if len(parts) >= 2:
                status_code = parts[1]
                reason_phrase = ' '.join(parts[2:])
                status_line = response_line.strip()
            else:
                client_socket.close()
                return None, "Invalid response from server", None, None, None
        else:
            client_socket.close()
            return None, "No response from server", None, None, None

        response_headers = read_headers(client_socket)

        content_length_str = response_headers.get('content-length', '0')
        try:
            content_length = int(content_length_str)
        except ValueError:
            content_length = 0

        if content_length > 0:
            body = client_socket.recv(content_length).decode('utf-8')
            response_data = json.loads(body)
            message = response_data.get('message', '')
        else:
            body = ''
            message = ''

        auth_header = response_headers.get('authorization', '')

        client_socket.close()

        if status_code == '200' and action == 'login':
            return status_code, message, response_headers, auth_header, status_line
        else:
            return status_code, message, response_headers, None, status_line

    except Exception as e:
        print(f"An error occurred in send_authentication_request: {str(e)}")
        if client_socket:
            client_socket.close()
        return None, f"An error occurred: {str(e)}", None, None, None

def send_voice_file_tcp(audio_data, token, host='localhost', port=8888):
    client_socket = None
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(20)
        client_socket.connect((host, port))
        print("Connected to the server for voice file upload.")

        request_line = "POST /upload HTTP/1.1"
        headers = {
            "Host": host,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:80.0) Gecko/20100101 Firefox/80.0",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Content-Type": "audio/wav",
            "Content-Length": str(len(audio_data)),
            "Authorization": token,
            "Connection": "keep-alive"
        }

        # Construct the HTTP request message
        request_message = request_line + "\r\n"
        for header_name, header_value in headers.items():
            request_message += f"{header_name}: {header_value}\r\n"
        request_message += "\r\n"

        # Print the HTTP request message with colors
        print(f"{bcolors.OKBLUE}HTTP Request Message:{bcolors.ENDC}")
        print(f"{bcolors.OKGREEN}{request_message}{bcolors.ENDC}")

        # Send the request
        client_socket.sendall(request_message.encode('utf-8'))
        client_socket.sendall(audio_data)
        print("Audio data sent to server.")

        response_line = read_line(client_socket)
        if response_line:
            parts = response_line.strip().split(' ')
            if len(parts) >= 2:
                status_code = parts[1]
                reason_phrase = ' '.join(parts[2:])
                status_line = response_line.strip()
            else:
                client_socket.close()
                return None, "Invalid response from server", {}, ''
        else:
            client_socket.close()
            return None, "No response from server", {}, ''

        response_headers = read_headers(client_socket)

        content_length_str = response_headers.get('content-length', '0')
        try:
            content_length = int(content_length_str)
        except ValueError:
            content_length = 0
        content_type = response_headers.get('content-type', '')
        response_text = response_headers.get('x-response-text', '')         # Bot's response text
        transcribed_text = response_headers.get('x-transcribed-text', '')   # User's transcribed text

        if content_length > 0:
            body = b''
            remaining = content_length
            while remaining > 0:
                chunk = client_socket.recv(min(BUFFER_SIZE, remaining))
                if not chunk:
                    break
                body += chunk
                remaining -= len(chunk)
            client_socket.close()

            if content_type == 'audio/wav':
                # Return the binary audio data and the transcribed texts
                return status_code, body, response_headers, status_line
            elif content_type == 'text/plain':
                # Decode base64-encoded data
                encoded_data = body.decode('utf-8')
                return status_code, encoded_data, response_headers, status_line
            else:
                # Assume it's JSON with an error message
                response_data = json.loads(body.decode('utf-8'))
                message = response_data.get('message', '')
                return status_code, message, response_headers, status_line
        else:
            client_socket.close()
            return status_code, None, response_headers, status_line

    except Exception as e:
        print(f"An error occurred in send_voice_file_tcp: {str(e)}")
        if client_socket:
            client_socket.close()
        return None, f"An error occurred: {str(e)}", {}, ''
