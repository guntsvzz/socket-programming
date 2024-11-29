import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QStackedWidget, QTextEdit
)
from send_request import send_request

class ChatPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        # Username input field
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Enter your username")
        layout.addWidget(self.username_input)

        # Chat display area
        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        # User input field
        self.message_input = QLineEdit(self)
        self.message_input.setPlaceholderText("Type your answer...")
        layout.addWidget(self.message_input)

        # Submit button
        self.submit_button = QPushButton("Submit", self)
        self.submit_button.clicked.connect(self.submit_answer)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

        # Question tracking
        self.current_question_index = -1
        self.questions = []

    def fetch_questions(self):
        """Fetch the first question from the server."""
        username = self.username_input.text().strip()
        if not username:
            self.chat_display.append("System: Please enter a username to start.")
            return

        self.chat_display.append("System: Fetching questions...")
        response = send_request('qa_interview', {'username': username})

        try:
            _, json_content = response.split("\r\n\r\n", 1)
            response_json = json.loads(json_content)

            # Extract question
            question_data = response_json.get("message", {})
            question = question_data.get("question", None)
            if question:
                self.questions = [question]
                self.current_question_index = 0
                self.chat_display.append(f"System: {question}")
            else:
                self.chat_display.append("System: No questions returned by server.")
        except (json.JSONDecodeError, IndexError) as e:
            self.chat_display.append("System: Error fetching questions from server.")

    def submit_answer(self):
        """Handle user's answer and fetch the next question."""
        answer = self.message_input.text().strip()
        if not answer:
            self.chat_display.append("System: Please provide an answer before submitting.")
            return

        username = self.username_input.text().strip()
        if not username:
            self.chat_display.append("System: Please enter a username to continue.")
            return

        # Ensure there are questions
        if not self.questions or self.current_question_index < 0:
            self.chat_display.append("System: No questions available. Please fetch questions first.")
            return

        # Get the current question
        current_question = self.questions[self.current_question_index]

        # Display answer
        self.chat_display.append(f"You: {answer}")
        self.message_input.clear()

        # Send question and answer to the server
        body_data = {"username": username, "question": current_question, "answer": answer}
        response = send_request('qa_interview', body_data)

        try:
            _, json_content = response.split("\r\n\r\n", 1)
            response_json = json.loads(json_content)

            # Fetch the next question
            question_data = response_json.get("message", {})
            next_question = question_data.get("question", None)
            if next_question:
                self.questions.append(next_question)
                self.current_question_index += 1
                self.chat_display.append(f"System: {next_question}")
            else:
                self.chat_display.append("System: No more questions available.")
        except (json.JSONDecodeError, IndexError) as e:
            self.chat_display.append("System: Error retrieving the next question from server.")
