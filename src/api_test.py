import requests as req
import bs4 as soup
import os
import json

DEBUG = True
BASE_URL = "https://canvas.vu.nl/api/v1"
COURSE_ID = "68322"
QUIZ_ID = "58223"
KEY = None


def load_key(keyfile="./key.secret"):
    with open(keyfile) as f:
        return f.readline()


def get_quiz_content(base_url, course_id, quiz_id, auth_key) -> dict:
    quiz = req.get(f'{base_url}/courses/{course_id}/quizzes/{quiz_id}',
                   headers={'Authorization': f'Bearer {auth_key}'})
    if DEBUG:
        quiz_beautified = json.dumps(quiz.json(), indent=2)
        print(quiz_beautified)
    
    return dict(quiz.json())

def get_assignment_content(base_url, course_id, assignment_id, auth_key) -> dict:
    assignment = req.get(f'{base_url}/courses/{course_id}/assignments/{assignment_id}',
                         headers={'Authorization': f'Bearer {auth_key}'})
    
    if DEBUG:
        assignment_beautified = json.dumps(assignment.json(), indent=2)
        print(assignment_beautified)
    
    return dict(assignment.json())

def get_assignment_submissions(base_url, course_id, assignment_id, auth_key) -> dict:
    submissions = req.get(f'{base_url}/courses/{course_id}/assignments/{assignment_id}/submissions?include[]=submission_history',
                         headers={'Authorization': f'Bearer {auth_key}'})
    
    if DEBUG:
        submissions_beautified = json.dumps(submissions.json(), indent=2)
        print(submissions_beautified)
    
    return submissions.json()

KEY = load_key()
quiz_details = get_quiz_content(BASE_URL, COURSE_ID, QUIZ_ID, KEY)
assignment_details = get_assignment_content(BASE_URL, COURSE_ID, quiz_details["assignment_id"], KEY)
assignment_submissions = get_assignment_submissions(BASE_URL, COURSE_ID, quiz_details["assignment_id"], KEY)

