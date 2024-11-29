import sys
import socket
import json

# Global variable to store cookies
cookies = {}

# Socket setup
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 9999))

def send_request(action, body_data):
    # request_line = f"POST /{action} HTTP/1.1"
    request_line = f"POST /{action}"
    body = json.dumps(body_data)
    headers = {
        "Host": "localhost",
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Content-Length": str(len(body)),
        "Connection": "keep-alive"
    }
    if cookies:
        headers["Cookie"] = "; ".join(f"{key}={value}" for key, value in cookies.items())
    request_message = request_line + "\r\n"
    for header_name, header_value in headers.items():
        request_message += f"{header_name}: {header_value}\r\n"
    request_message += "\r\n" + body

    client_socket.send(request_message.encode('utf-8'))
    response = client_socket.recv(1024).decode('utf-8')
    print(response)

    for line in response.split("\r\n"):
        if line.startswith("Set-Cookie"):
            cookie_data = line.split(": ", 1)[1].split(";")[0]
            key, value = cookie_data.split("=")
            cookies[key] = value

    return response

client_socket.close()