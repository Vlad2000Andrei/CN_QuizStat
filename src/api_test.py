import requests as req
import bs4 as soup
import os
import json
import pandas as pd
import matplotlib.pyplot as plt

DEBUG = False
BASE_URL = "https://canvas.vu.nl/api/v1"
COURSE_ID = "68322"
QUIZ_ID = "58223"
KEY = None
DATA = {}


def load_key(keyfile="./key.secret"):
    with open(keyfile) as f:
        return f.readline()

def get_other_pages(headers) -> dict:
    raw_links: list[str] = headers['Link'].split(",")
    result = {}
    for raw_link in raw_links:
        [link, rel] = raw_link.split("; ", maxsplit=1)
        link = link.removeprefix("<").removesuffix(">")
        rel = rel.removeprefix("rel=\"").removesuffix("\"")
        result[rel] = link

    return result

def get_quizzes(base_url, course_id, auth_key) -> list:
    quizzes = req.get(f'{base_url}/courses/{course_id}/quizzes/?per_page=100',
                   headers={'Authorization': f'Bearer {auth_key}'})
    dbg_print_json(quizzes.json())

    return list(quizzes.json())

# Get information about a quiz
def get_quiz_details(base_url, course_id, quiz_id, auth_key) -> dict:
    quiz = req.get(f'{base_url}/courses/{course_id}/quizzes/{quiz_id}',
                   headers={'Authorization': f'Bearer {auth_key}'})
    dbg_print_json(quiz.json())

    return dict(quiz.json())


def get_quiz_questions(base_url, course_id, quiz_id, auth_key) -> list:
    quiz = req.get(f'{base_url}/courses/{course_id}/quizzes/{quiz_id}/questions',
                   headers={'Authorization': f'Bearer {auth_key}'})
    dbg_print_json(quiz.json())

    return list(quiz.json())

# Get information about an assignment
def get_assignment_content(base_url, course_id, assignment_id, auth_key) -> dict:
    assignment = req.get(f'{base_url}/courses/{course_id}/assignments/{assignment_id}',
                         headers={'Authorization': f'Bearer {auth_key}'})
    dbg_print_json(assignment.json())

    return dict(assignment.json())

# Get submissions of an assignment
def get_assignment_submissions(base_url, course_id, assignment_id, auth_key) -> dict:
    HEADERS = {'Authorization': f'Bearer {auth_key}'}
    URL = f'{base_url}/courses/{course_id}/assignments/{assignment_id}/submissions?include[]=submission_history&per_page=100'

    raw_submissions = req.get(url=URL, headers=HEADERS)

    pages = get_other_pages(raw_submissions.headers)
    submissions = extract_submissions(raw_submissions.json())
    while not pages["current"] == pages["last"]:
        raw_submissions = req.get(pages["next"], headers=HEADERS)
        submissions = submissions + extract_submissions(raw_submissions.json())
        pages = get_other_pages(raw_submissions.headers)
        print(f'{pages["current"]}', f'\tQuota Remaining: {raw_submissions.headers["X-Rate-Limit-Remaining"]}\tCost: {raw_submissions.headers["X-Request-Cost"]}')

    return submissions

def get_submission_status(quiz_submissions) -> pd.Series:
    statuses = map(
        lambda submission: submission['workflow_state'], quiz_submissions)
    statuses = pd.Series(statuses)
    print(statuses.value_counts())

    status_counts = statuses.value_counts()
    barplot = plt.bar(x=status_counts.index.values,
                      height=status_counts.values)
    plt.title("Submission Status for Quiz")
    plt.show()
    return statuses

def get_question_status(questions, submissions):
    question_results = []
    for question in questions:  # For every question in the quiz
        statuses = []
        question_id = question['id']
        
        for submission in submissions:  # For every answer that actually has content
            if "submission_data" in submission:
                for answer in submission['submission_data']:    # For every question that was answered
                    if answer['question_id'] == question_id:
                        statuses.append(str(answer['correct']))
            else:
                statuses.append("N/A")

        question_results.append({
            "id": question_id,
            "text": question['question_text'],
            "results": pd.Series(statuses)
        })

    for result in question_results:
        plt.bar(x=result["results"].value_counts().index.values,
                height=result["results"].value_counts().values)
        plt.title(result["text"])
        plt.show()

# extract only the submission information from all of the quiz responses
def extract_submissions(api_response: dict) -> list[dict]:
    result = []
    for response in api_response:
        result.append(response["submission_history"][0])
    return result

# Prints a JSON with a set level of indent for debugging
def print_json(obj):
    print(json.dumps(obj, indent=4))

# Prints a JSON with a set level of indent for debugging if debug is enabled
def dbg_print_json(obj):
    if DEBUG:
        print_json(obj)

# Prints a given object if debug is enabled
def dbg_print(obj):
    if DEBUG:
        print(obj)




# Find the API key from a file
KEY = load_key()

# Get the list of quizzes:
all_quizzes = get_quizzes(BASE_URL,COURSE_ID,KEY)
for quiz in all_quizzes:
    print(f"Index: {all_quizzes.index(quiz)}\tID: {quiz['id']}\t Name: '{quiz['title']}'")
user_choice = int(input("Enter the index of the quiz you want to analyze: "))
while user_choice not in range(len(all_quizzes)): 
    print("Input not a valid index!")
    user_choice = int(input("Enter the index of the quiz you want to analyze: "))

QUIZ_ID = all_quizzes[user_choice]['id']

# Get all the data we need from the Canvas API
quiz_details = get_quiz_details(BASE_URL, COURSE_ID, QUIZ_ID, KEY)
quiz_questions = get_quiz_questions(BASE_URL, COURSE_ID, QUIZ_ID, KEY)
assignment_details = get_assignment_content(BASE_URL, COURSE_ID, quiz_details["assignment_id"], KEY)
submissions = get_assignment_submissions(BASE_URL, COURSE_ID, quiz_details["assignment_id"], KEY)

# Visualize the data
DATA[QUIZ_ID] = submissions
get_submission_status(submissions)
get_question_status(quiz_questions, submissions)
