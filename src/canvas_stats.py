from canvasapi import Canvas
from canvasapi.quiz import Quiz
import json
from datetime import datetime
import matplotlib.pyplot as plt

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


CanvasAPI = Canvas(BASE_URL, KEY) # Instantiate Canvas API
CN2023 = CanvasAPI.get_course(COURSE_ID)    # Get the course
quizzes = CN2023.get_quizzes()
assignments = CN2023.get_assignments()
for assignment in assignments:
    print(assignment.id, "\t", assignment.name)

chat_client = CN2023.get_assignment(261779)
submission_dates = [f.submitted_at for f in chat_client.get_submissions() if not f.submitted_at is None]
print(submission_dates[:10])
