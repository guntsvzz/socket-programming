import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QStackedWidget, QTextEdit
)
from send_request import send_request


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
