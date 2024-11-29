import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QStackedWidget, QTextEdit, QFileDialog
)
from send_request import send_request

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