import sys
import socket
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QStackedWidget, QTextEdit
)
import re
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

class LoginPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget

        layout = QVBoxLayout()
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Password")
        layout.addWidget(self.password_input)

        # Student ID input field for registration
        self.student_id_input = QLineEdit(self)
        self.student_id_input.setPlaceholderText("Student ID")
        layout.addWidget(self.student_id_input)


        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.register)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        response = send_request('login', {'username': username, 'password': password})
        print(response)  # For debugging
        self.stacked_widget.setCurrentIndex(1)  # Go to the upload page if login successful

    def register(self):
        # Extract text from the QLineEdit fields
        student_id = self.student_id_input.text()  # assuming you have added this field for student ID
        username = self.username_input.text()
        password = self.password_input.text()

        # Now pass the extracted text to send_request
        response = send_request('register', {'student_id': student_id, 'username': username, 'password': password})
        print(response)


from PyQt5.QtWidgets import QFileDialog, QVBoxLayout, QLineEdit, QPushButton, QWidget

class UploadPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget

        layout = QVBoxLayout()

        # Username input field (optional, for reference)
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        # Button to upload Resume
        self.resume_button = QPushButton("Upload Resume")
        self.resume_button.clicked.connect(self.upload_resume)
        layout.addWidget(self.resume_button)

        # Button to upload Job Description
        self.job_desc_button = QPushButton("Upload Job Description")
        self.job_desc_button.clicked.connect(self.upload_job_description)
        layout.addWidget(self.job_desc_button)

        # Button for next page
        self.next_page_button = QPushButton("Next Page")
        self.next_page_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        layout.addWidget(self.next_page_button)

        self.setLayout(layout)

    def upload_resume(self):
        # Open a file dialog to select a resume file
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Resume", "", "PDF Files (*.pdf);;All Files (*)")
        if file_path:
            # Get username from the input field
            username = self.username_input.text()

            # Send the file path and filename to the server (no file content)
            response = send_request('upload_resume', {
                'username': username,
                'filename': file_path  # Only send the file path, not the content
            })
            print(response)  # For debugging

    def upload_job_description(self):
        # Open a file dialog to select a job description file
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Job Description", "", "PDF Files (*.pdf);;All Files (*)")
        if file_path:
            # Get username from the input field
            username = self.username_input.text()

            # Send the file path and filename to the server (no file content)
            response = send_request('upload_job_description', {
                'username': username,
                'filename': file_path  # Only send the file path, not the content
            })
            print(response)  # For debugging

class ChatPage(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        
        # Chat display area
        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)  # Prevent editing the chat display
        layout.addWidget(self.chat_display)

        # User input field
        self.user_input = QLineEdit(self)
        self.user_input.setPlaceholderText("Type your message...")
        layout.addWidget(self.user_input)

        # Send message button
        self.send_button = QPushButton("Send", self)
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)

        self.setLayout(layout)

    def send_message(self):
        # Get the user input
        message = self.user_input.text()
        if not message:
            return  # Don't send empty messages

        # Display user message in chat area
        self.chat_display.append(f"You: {message}")

        # Use an instance variable to retain the question state
        if not hasattr(self, 'current_question'):
            self.current_question = None  # Initialize if not already set

        # Send the message to the server
        response = send_request('qa_interview', {
            'username': 'gun',  # Replace with the actual username
            'question': self.current_question or "Default question",  # Use stored question or default
            'answer': message  # User's answer
        })

        # Extract the new question from the response
        match = re.search(r'"question":\s*"(.*?)"', response)
        if match:
            self.current_question = match.group(1)  # Update the current question
            print(self.current_question)  # Debugging: print the current question

        # Show the server's response in the chat area
        self.chat_display.append(f"Server: {self.current_question}")

        # Clear the input field
        self.user_input.clear()


    # def send_text(self):
    #     username = "gun"  # Replace with actual username handling logic
    #     text_message = self.message_input.text()
    #     # response = send_request('send_text', {'username': username, 'text_message': text_message})
        
    #     # Send the message to the 'qa_interview' endpoint
    #     response = send_request('qa_interview', {
    #         'username': 'gun',  # Replace with the actual username
    #         'question': text_message,  # The user's message
    #         'answer': text_message    # The answer (if applicable)
    #     })

    #     # Display user's message
    #     self.chat_display.append(f"You: {text_message}")

    #     # Attempt to extract JSON content from the response
    #     system_message = "Error: Unable to parse response from server"  # Default error message
    #     response_lines = response.splitlines()
    #     json_data = ""

    #     # Try to find the JSON part in the response
    #     for line in response_lines:
    #         if line.startswith("{") and line.endswith("}"):
    #             json_data = line
    #             break
    #         elif line.startswith("{"):
    #             json_data = line  # Start of JSON data
    #         elif line.endswith("}") and json_data:
    #             json_data += line  # End of JSON data
    #             break
    #         elif json_data:
    #             json_data += line  # Continue appending JSON data

    #     # Parse the found JSON data
    #     try:
    #         if json_data:
    #             response_json = json.loads(json_data)
    #             system_message = response_json.get("message", "No message")
    #     except json.JSONDecodeError:
    #         system_message = "Error: Invalid JSON response from server"

    #     # Display system's response message
    #     self.chat_display.append(f"System: {system_message}")
    #     self.message_input.clear()
class MainWindow(QStackedWidget):
    def __init__(self):
        super().__init__()

        self.login_page = LoginPage(self)
        self.upload_page = UploadPage(self)
        self.chat_page = ChatPage()

        self.addWidget(self.login_page)
        self.addWidget(self.upload_page)
        self.addWidget(self.chat_page)

        self.setCurrentIndex(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("PyQt5 Interview System")
    window.resize(400, 300)
    window.show()
    app.exec_()

client_socket.close()
