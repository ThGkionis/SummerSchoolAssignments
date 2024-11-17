import streamlit as st
from openai import OpenAI
import json
import time

# Replace "your_api_key_here" with your actual OpenAI API key
client = OpenAI(api_key="your_api_key_here")

class Question:
    def __init__(self, question, options, correct_answer, explanation=None):
        self.question = question
        self.options = options
        self.correct_answer = correct_answer
        self.explanation = explanation

class Quiz:
    def __init__(self):
        self.questions = self.load_or_generate_questions()
        self.initialize_session_state()

    def load_or_generate_questions(self):
        # Check if questions already exist in the session state
        if 'questions' not in st.session_state:
            # Predefined questions or load from a source
            st.session_state.questions = [
                Question("What is the capital of France?", ["London", "Paris", "Berlin", "Madrid"], "Paris",
                         "Paris is the capital and most populous city of France."),
                Question("Who developed the theory of relativity?",
                         ["Isaac Newton", "Albert Einstein", "Nikola Tesla", "Marie Curie"], "Albert Einstein",
                         "Albert Einstein is known for developing the theory of relativity, one of the two pillars of modern physics.")
            ]
            # Optionally, add a step here to generate new questions via GPT-3 and append them
        return st.session_state.questions

    def initialize_session_state(self):
        if 'current_question_index' not in st.session_state:
            st.session_state.current_question_index = 0
        if 'score' not in st.session_state:
            st.session_state.score = 0
        if 'answers_submitted' not in st.session_state:
            st.session_state.answers_submitted = 0
        if 'skipped_questions' not in st.session_state:
            st.session_state.skipped_questions = []
        if 'start_time' not in st.session_state:
            st.session_state.start_time = None
        if 'time_limit' not in st.session_state:
            st.session_state.time_limit = 30  # Set a 30-second time limit for each question

    def display_quiz(self):
        self.update_progress_bar()
        if st.session_state.answers_submitted >= len(st.session_state.questions):
            self.display_results()
        else:
            self.display_current_question()

    def start_timer(self):
        st.session_state.start_time = time.time()

    def reset_timer(self):
        st.session_state.start_time = None

    def display_current_question(self):
        if st.session_state.current_question_index >= len(st.session_state.questions):
            st.error("No more questions available.")
            return

        question = st.session_state.questions[st.session_state.current_question_index]

        if st.session_state.start_time is None:
            self.start_timer()

        elapsed_time = time.time() - st.session_state.start_time
        remaining_time = st.session_state.time_limit - elapsed_time
        if remaining_time <= 0:
            st.warning("Time's up!")
            self.check_answer(None)  # Treat no answer as incorrect
            st.session_state.answers_submitted += 1
            self.move_to_next_question()
            st.rerun()
        else:
            st.markdown(f"### {question.question}")
            st.markdown(f"Time remaining: {int(remaining_time)} seconds")
            options = question.options
            answer = st.radio("Choose one:", options, key=f"question_{st.session_state.current_question_index}")

            col1, col2 = st.columns(2)
            if col1.button("Submit Answer", key=f"submit_{st.session_state.current_question_index}"):
                self.check_answer(answer)
                st.session_state.answers_submitted += 1
                self.move_to_next_question()
                st.rerun()

            if col2.button("Skip Question", key=f"skip_{st.session_state.current_question_index}"):
                st.session_state.skipped_questions.append(st.session_state.current_question_index)
                self.move_to_next_question()
                st.rerun()

    def move_to_next_question(self):
        # Move to the next question
        st.session_state.current_question_index += 1

        # Handle wrapping around to the start
        if st.session_state.current_question_index >= len(st.session_state.questions):
            st.session_state.current_question_index = 0

        # Skip over questions that were already skipped
        while st.session_state.current_question_index in st.session_state.skipped_questions:
            st.session_state.current_question_index += 1
            if st.session_state.current_question_index >= len(st.session_state.questions):
                st.session_state.current_question_index = 0

            # Check if all questions have been attempted or skipped
            if len(st.session_state.skipped_questions) >= len(st.session_state.questions):
                st.session_state.current_question_index = -1
                st.warning("All questions have been skipped or attempted.")
                return

        # If we're at the last question and it's already been skipped, end the quiz
        if len(st.session_state.questions) - len(st.session_state.skipped_questions) <= 0:
            st.session_state.current_question_index = -1
            st.warning("All questions have been skipped or attempted.")
            return

        self.reset_timer()  # Reset the timer for the next question

    def check_answer(self, user_answer):
        correct_answer = st.session_state.questions[st.session_state.current_question_index].correct_answer

        if user_answer is None:
            st.error("Time's up! No answer provided.")
        elif user_answer == correct_answer:
            st.session_state.score += 1
            st.success("Correct!")
        else:
            st.error("Wrong answer!")

        if st.session_state.questions[st.session_state.current_question_index].explanation:
            st.info(st.session_state.questions[st.session_state.current_question_index].explanation)

    def display_results(self):
        st.markdown(f"## Quiz completed! Your score: {st.session_state.score}/{len(st.session_state.questions)}")
        if st.session_state.score / len(st.session_state.questions) == 1.0:
            st.success("Congrats, you got everything correct!")
            st.balloons()
        else:
            st.warning("You can do better! Try again.")

        if st.button("Restart Quiz"):
            self.restart_quiz()

    def update_progress_bar(self):
        total_questions = len(st.session_state.questions)
        progress = st.session_state.answers_submitted / total_questions
        st.progress(progress)
        st.write(f"Question {st.session_state.current_question_index + 1} of {total_questions}")

    def restart_quiz(self):
        st.session_state.current_question_index = 0
        st.session_state.score = 0
        st.session_state.answers_submitted = 0
        st.session_state.skipped_questions = []  # Clear skipped questions
        self.reset_timer()  # Reset the timer
        st.rerun()

# Function to convert the GPT response into a Question object and append it to the questions list
# Function to generate a new question via GPT-3 and append it to the session state questions
def generate_and_append_question(user_prompt, category, n=1):
    history = ""
    for q in st.session_state.questions:
        history += f"Question: {q.question} Answer: {q.correct_answer}\n"

    gpt_prompt = '''Generate a JSON response for a trivia question including the question, option, correct answer, and explanation. The format should be as follows:
{
    "Question": "The actual question text goes here?",
    "Options": ["Option1", "Option2", "Option3", "Option4"],
    "CorrectAnswer": "TheCorrectAnswer",
    "Explanation": "A detailed explanation on why the correct answer is correct."
}'''
    try:
        for _ in range(n):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": gpt_prompt},
                    {"role": "user", "content": f"Create a question about {user_prompt} in the category {category}. Previous questions: {history}"}
                ]
            )

            try:
                gpt_response = json.loads(response.choices[0].message.content)
                new_question = Question(
                    question=gpt_response["Question"],
                    options=gpt_response["Options"],
                    correct_answer=gpt_response["CorrectAnswer"],
                    explanation=gpt_response["Explanation"]
                )
                st.session_state.questions.append(new_question)
            except json.JSONDecodeError:
                st.error("Failed to decode the GPT response. The API response might not be in the expected format.")
                st.write(f"Raw GTP response: {response.choices[0].message.content}")

    except Exception as e:
        st.error(f"An error occurred while generating the questions: {str(e)}")
        st.write("Please check your API key and network connection.")

# Main app Logic
if 'quiz_initialized' not in st.session_state:
    st.session_state.quiz = Quiz()
    st.session_state.quiz_initialized = True

st.title("Interactive Quiz App")
st.write("Test your knowledge with this interactive quiz!")

# Category Selection
category = st.selectbox("Select a category", ["General Knowledge", "Science", "History", "Technology"])

user_input = st.text_input("Enter a topic to generate a new question")

col1, col2 = st.columns(2)
if col1.button('Generate New Question'):
    generate_and_append_question(user_input, category)

if col2.button('Generate 3 New Questions'):
    generate_and_append_question(user_input, category, n=3)

st.session_state.quiz.display_quiz()
