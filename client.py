import socket
import json

# Global variable to store cookies
cookies = {}

def send_request(action, body_data):
    request_line = f"POST /{action} HTTP/1.1"
    body = json.dumps(body_data)
    headers = {
        "Host": "localhost",
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Content-Length": str(len(body)),
        "Connection": "keep-alive"
    }

    # Include cookies in the headers if they exist
    if cookies:
        headers["Cookie"] = "; ".join(f"{key}={value}" for key, value in cookies.items())

    # Construct the HTTP request message
    request_message = request_line + "\r\n"
    for header_name, header_value in headers.items():
        request_message += f"{header_name}: {header_value}\r\n"
    request_message += "\r\n" + body

    # Send the request and receive response
    client_socket.send(request_message.encode('utf-8'))
    response = client_socket.recv(1024).decode('utf-8')
    print(response)
    
    # Extract cookies from the response if present
    for line in response.split("\r\n"):
        if line.startswith("Set-Cookie"):
            cookie_data = line.split(": ", 1)[1].split(";")[0]
            key, value = cookie_data.split("=")
            cookies[key] = value

def login():
    username = input("Enter username: ")
    password = input("Enter password: ")
    send_request('login', {'username': username, 'password': password})

def register():
    student_id = input("Enter student ID: ")
    username = input("Enter username: ")
    password = input("Enter password: ")
    send_request('register', {'student_id': student_id, 'username': username, 'password': password})

def upload_resume():
    username = input("Enter username: ")
    filename = input("Enter document filename: ")
    send_request('upload_resume', {'username': username, 'filename': filename})
    
def upload_job_description():
    username = input("Enter username: ")
    filename = input("Enter document filename: ")
    send_request('upload_job_description', {'username': username, 'filename': filename})
    
def interview_questions():
    username = input("Enter username: ")
    send_request('interview_questions', {'username': username})
    
def send_stt():
    username = input("Enter username: ")
    filename = input("Enter voice filename: ")
    send_request('send_stt', {'filename': filename})
        
def send_tts():  
    username = input("Enter username: ")  
    text_message = input("Enter text message: ")
    send_request('send_tts', {'text_message': text_message})

def send_text():
    username = input("Enter username: ")
    text_message = input("Enter text message: ")
    send_request('send_text', {'text_message': text_message})

if __name__ == '__main__':
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 8888))

    try:
        while True:
            print("\nSelect an action:")
            print("1. Login")
            print("2. Register")
            print("3. Upload Resume")
            print("4. Upload Job Desccription")
            print("5. Generated Interview Questions")
            print("6. Test Speech to Text")
            print("7. Test Text to Speech")
            print("8. Test Text")
            print("9. Exit")

            choice = input("Enter your choice: ")

            if choice == '1':
                login()
            elif choice == '2':
                register()
            elif choice == '3':
                upload_resume() #../assets/documents/resume/resume-02-Gun.pdf
            elif choice == '4':
                upload_job_description() #../assets/documents/job_description/job-desc-02-security-operations-manager.pdf
            elif choice == '5':
                interview_questions()
            elif choice == '6':
                send_stt() #../assets/audio/test_voice.wav
            elif choice == '7':
                send_tts( ) 
            elif choice == '8':
                send_text()
            elif choice == '9':
                print("Exiting...")
                break
            else:
                print("Invalid choice.")

    finally:
        client_socket.close()
