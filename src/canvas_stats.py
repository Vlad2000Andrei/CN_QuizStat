from canvasapi import Canvas
from canvasapi.quiz import Quiz, QuizQuestion, QuizSubmission
from canvasapi.assignment import Assignment
from canvasapi.submission import Submission
from canvasapi.course import Course
import json
from datetime import datetime
from dateutil import parser
import matplotlib.pyplot as plt
import time

DEBUG = False
BASE_URL = "https://canvas.vu.nl/"
COURSE_ID = None
QUIZ_ID = None
KEY = None
DATA = {}

def load_key(keyfile="./key.secret"):
    with open(keyfile) as f:
        return f.readline()


# Load config files
with open("./quizstat_config.json", "r") as fp:
    CONFIG = json.load(fp)
    KEY = load_key(CONFIG['keyfile'])
    COURSE_ID = CONFIG['course_id']


def str_to_timestamp(s: str) -> float:
    return parser.parse(s).timestamp()


def select_id_from_list(data: list, displayed_title_attribute: str = "name"):
    data = list(data)
    print("-"*60)
    for idx, item in enumerate(data):
        print(
            f"[{idx}]\t{item.id}\t{item.__getattribute__(displayed_title_attribute)}")
    print("-"*60)

    user_choice = int(
        input("Enter the index of the item you want to analyze: "))
    while user_choice not in range(len(data)):
        print("Input not a valid index!")
        user_choice = int(
            input("Enter the index of the item you want to analyze: "))

    return data[user_choice]

# plot the submissions of an assignment as a boxplot
# also returns the timestamps and their submissions
def plot_assignment_submission_times(assignment, time_unit: str = "seconds", submissions : list = None, references = []) -> tuple:
    TIME_UNITS = {
        "seconds": 1,
        "minutes": 60,
        "hours": 3600,
        "days": 86400
    }

    if submissions is None:
        all_submissions = assignment.get_submissions()
    else:
        all_submissions = submissions
    
    timestamps = [str_to_timestamp(f.submitted_at)
                  for f in all_submissions if not f.submitted_at is None]

    (unlock_timestamp, due_timestamp, lock_timestamp) = get_assignment_start_end(assignment)

    # Choose one to be the one we calculate our times relative to
    if not due_timestamp is None:
        relative_timestamp = due_timestamp
        relative_timestamp_name = "Due Time"
    elif not lock_timestamp is None:
        relative_timestamp = lock_timestamp
        relative_timestamp_name = "Lock Time"
    else:
        relative_timestamp = unlock_timestamp
        relative_timestamp_name = "Unlock Time"

    references = [str_to_timestamp(ref) for ref in references]
    references = [(r - relative_timestamp) / TIME_UNITS[time_unit] for r in references]

    timediffs = [(t - relative_timestamp) / TIME_UNITS[time_unit]
                 for t in timestamps]
    plt.boxplot(timediffs)
    plt.ylabel(f"Time diff to {relative_timestamp_name} [{time_unit}]")
    plt.title(f"Distribution of ({len(timediffs)}) submission times relative to {relative_timestamp_name} ({datetime.fromtimestamp(relative_timestamp).strftime('%d/%m/%Y, %H:%M:%S')})")
    for reference in references:
        plt.axhline(reference, c='r')
    plt.show()

    return (timestamps, all_submissions)

def plot_assignment_scores(assignment: Assignment, submissions : list = None):
    if submissions is None:
        all_submissions = assignment.get_submissions()
    else:
        all_submissions = submissions

    scores = [s.score for s in all_submissions if not s.score is None]
    plt.boxplot(scores)
    plt.title(f"Score distribution of {assignment.name} ({len(scores)})")
    plt.ylabel(f"Score Obtained [Points]")
    plt.show()

# Get the unlock time, due time and lock time as float timestamps
def get_assignment_start_end (assignment : Assignment) -> tuple:
    # Find key submission time points
    try:
        due_timestamp = str_to_timestamp(assignment.due_at)
    except:
        due_timestamp = None

    try:
        lock_timestamp = str_to_timestamp(assignment.lock_at)
    except:
        lock_timestamp = None

    try:
        unlock_timestamp = str_to_timestamp(assignment.unlock_at)
    except:
        unlock_timestamp = None

    return (unlock_timestamp, due_timestamp, lock_timestamp)

CanvasAPI = Canvas(BASE_URL, KEY)   # Instantiate Canvas API
CN2023 = CanvasAPI.get_course(COURSE_ID)    # Get the course
QUIZZES = CN2023.get_quizzes()
ASSIGNMENTS = CN2023.get_assignments()

while True:
    assign = select_id_from_list(ASSIGNMENTS, "name")
    assign_submission_times, assign_submissions = plot_assignment_submission_times(assign, "days", references=["12 April 2024"])
    plot_assignment_scores(assign, submissions=assign_submissions)