# storage.py
# Handles reading/writing the JSON files in the data/ folder.

import json
import os

from models.user import User
from models.project import Project
from models.task import Task

DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
PROJECTS_FILE = os.path.join(DATA_DIR, "projects.json")
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")


def read_json(path):
    # if the file doesn't exist yet (first run) just return an empty list
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        print(f"Could not read {path}, starting with an empty list.")
        return []


def write_json(path, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_users():
    return [User.from_dict(d) for d in read_json(USERS_FILE)]


def load_projects():
    return [Project.from_dict(d) for d in read_json(PROJECTS_FILE)]


def load_tasks():
    return [Task.from_dict(d) for d in read_json(TASKS_FILE)]


def save_users(users):
    write_json(USERS_FILE, [u.to_dict() for u in users])


def save_projects(projects):
    write_json(PROJECTS_FILE, [p.to_dict() for p in projects])


def save_tasks(tasks):
    write_json(TASKS_FILE, [t.to_dict() for t in tasks])