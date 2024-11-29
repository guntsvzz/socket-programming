import os
import json

user_progress = {}
user_answers = {}

# def handle_qa_interview(body):
#     username = body.get("username")
#     question = body.get("question")
#     answer = body.get("answer")

#     if not username:
#         return "400 Bad Request", "Username is required."

#     # Example response with the next question
#     next_question = "What are your strengths?"
#     return "200 OK", {"message": next_question}


def handle_qa_interview(body):
    """Handle QA Interview request by returning the next question."""
    username = body.get("username")
    question_answered = body.get("question")
    answer = body.get("answer")

    if not username:
        return "400 Bad Request", "Username is required."

    user_file = f"../assets/database/{username}.json"
    if not os.path.exists(user_file):
        return "404 Not Found", "User file not found."

    try:
        with open(user_file, 'r') as file:
            user_data = json.load(file)

        questions = user_data.get("questions", {})
        # print(questions)
        if not questions:
            return "404 Not Found", "No questions found for the user."

        # Flatten all questions into a list
        formatted_questions = []
        for category, subcategories in questions.items():
            for subcategory, sub_questions in subcategories.items():
                formatted_questions.extend(sub_questions)

        # Store the user's answer
        if username not in user_answers:
            user_answers[username] = []
        if question_answered and answer:
            user_answers[username].append({"question": question_answered, "answer": answer})

        # Determine the next question
        current_index = user_progress.get(username, 0)
        if current_index < len(formatted_questions):
            next_question = formatted_questions[current_index]
            user_progress[username] = current_index + 1  # Increment progress
            return "200 OK", {"question": next_question}
        else:
            return "200 OK", {"question": "No more questions available."}

    except Exception as e:
        print(f"Error processing user file: {str(e)}")
        return "500 Internal Server Error", f"An error occurred: {str(e)}"
