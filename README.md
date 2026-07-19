No problem — here's everything, file by file. Create these paths in your project folder and paste in the matching content.

## `main.py````python
# main.py
# Entry point for the project tracker CLI.
#
# Example usage:
#   python main.py add-user --name "Alex" --email "alex@example.com"
#   python main.py add-project --user "Alex" --title "CLI Tool"
#   python main.py add-task --project "CLI Tool" --title "Implement add-task"

import argparse
import logging
import os
import sys

from models.user import User
from models.project import Project
from models.task import Task
from utils import storage

from rich.console import Console
from rich.table import Table

console = Console()

# basic logging so we have a record of what happened while testing/debugging
os.makedirs("data", exist_ok=True)
logger = logging.getLogger("project_tracker")
logger.setLevel(logging.INFO)
if not logger.handlers:  # avoid adding duplicate handlers if main gets imported twice
    file_handler = logging.FileHandler(os.path.join("data", "app.log"))
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(file_handler)

# these hold everything currently loaded in memory
users = []
projects = []
tasks = []


def load_data():
    global users, projects, tasks
    users = storage.load_users()
    projects = storage.load_projects()
    tasks = storage.load_tasks()


def save_data():
    storage.save_users(users)
    storage.save_projects(projects)
    storage.save_tasks(tasks)


def find_user(name):
    for u in users:
        if u.name.lower() == name.lower():
            return u
    return None


def find_project(title):
    for p in projects:
        if p.title.lower() == title.lower():
            return p
    return None


def find_task(task_id):
    for t in tasks:
        if t.id == task_id:
            return t
    return None


def print_table(title, columns, rows):
    if not rows:
        print(f"{title}: nothing to show yet")
        return
    table = Table(title=title)
    for col in columns:
        table.add_column(col)
    for row in rows:
        table.add_row(*[str(c) for c in row])
    console.print(table)


# ---------- command functions ----------

def add_user(args):
    if find_user(args.name):
        logger.warning(f"add-user failed, duplicate name: {args.name}")
        print(f"Error: a user named '{args.name}' already exists.")
        return
    user = User(name=args.name, email=args.email or "")
    users.append(user)
    save_data()
    logger.info(f"Added user {user.id}: {user.name}")
    print(f"Added {user}")


def list_users(args):
    rows = [(u.id, u.name, u.email) for u in users]
    print_table("Users", ["ID", "Name", "Email"], rows)


def add_project(args):
    owner = find_user(args.user)
    if not owner:
        logger.warning(f"add-project failed, no such user: {args.user}")
        print(f"Error: no user named '{args.user}'. Add them first with add-user.")
        return
    if find_project(args.title):
        logger.warning(f"add-project failed, duplicate title: {args.title}")
        print(f"Error: a project called '{args.title}' already exists.")
        return

    try:
        project = Project(
            title=args.title,
            owner_id=owner.id,
            description=args.description or "",
            due_date=args.due_date or "",
        )
    except ValueError as e:
        logger.error(f"add-project validation error: {e}")
        print(f"Error: {e}")
        return

    projects.append(project)
    save_data()
    logger.info(f"Added project {project.id}: {project.title} (owner={owner.name})")
    print(f"Added {project} for {owner.name}")


def list_projects(args):
    if args.user:
        owner = find_user(args.user)
        if not owner:
            print(f"Error: no user named '{args.user}'.")
            return
        shown = [p for p in projects if p.owner_id == owner.id]
        title = f"Projects for {owner.name}"
    else:
        shown = projects
        title = "All Projects"

    rows = []
    for p in shown:
        owner = next((u for u in users if u.id == p.owner_id), None)
        owner_name = owner.name if owner else "?"
        task_count = len([t for t in tasks if t.project_id == p.id])
        rows.append((p.id, p.title, owner_name, p.due_date or "-", task_count))

    print_table(title, ["ID", "Title", "Owner", "Due Date", "# Tasks"], rows)


def add_task(args):
    project = find_project(args.project)
    if not project:
        logger.warning(f"add-task failed, no such project: {args.project}")
        print(f"Error: no project called '{args.project}'. Add it first with add-project.")
        return

    task = Task(title=args.title, project_id=project.id, assigned_to=args.assigned_to or "")
    tasks.append(task)
    save_data()
    logger.info(f"Added task {task.id}: {task.title} (project={project.title})")
    print(f"Added {task} to project '{project.title}'")


def list_tasks(args):
    project = find_project(args.project)
    if not project:
        print(f"Error: no project called '{args.project}'.")
        return

    shown = [t for t in tasks if t.project_id == project.id]
    rows = [(t.id, t.title, t.status, t.assigned_to or "-") for t in shown]
    print_table(f"Tasks for {project.title}", ["ID", "Title", "Status", "Assigned To"], rows)


def complete_task(args):
    task = find_task(args.task_id)
    if not task:
        logger.warning(f"complete-task failed, no such task id: {args.task_id}")
        print(f"Error: no task with id {args.task_id}.")
        return

    task.complete()
    save_data()
    logger.info(f"Completed task {task.id}: {task.title}")
    print(f"Marked complete: {task}")


# ---------- argparse setup ----------

def build_parser():
    parser = argparse.ArgumentParser(description="A simple project tracker CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p = subparsers.add_parser("add-user", help="Create a new user")
    p.add_argument("--name", required=True)
    p.add_argument("--email")
    p.set_defaults(func=add_user)

    p = subparsers.add_parser("list-users", help="Show all users")
    p.set_defaults(func=list_users)

    p = subparsers.add_parser("add-project", help="Add a project for a user")
    p.add_argument("--user", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--description")
    p.add_argument("--due-date", dest="due_date")
    p.set_defaults(func=add_project)

    p = subparsers.add_parser("list-projects", help="Show projects, optionally for one user")
    p.add_argument("--user")
    p.set_defaults(func=list_projects)

    p = subparsers.add_parser("add-task", help="Add a task to a project")
    p.add_argument("--project", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--assigned-to", dest="assigned_to")
    p.set_defaults(func=add_task)

    p = subparsers.add_parser("list-tasks", help="Show tasks for a project")
    p.add_argument("--project", required=True)
    p.set_defaults(func=list_tasks)

    p = subparsers.add_parser("complete-task", help="Mark a task as done")
    p.add_argument("--task-id", dest="task_id", type=int, required=True)
    p.set_defaults(func=complete_task)

    return parser


def main():
    load_data()
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
```

## `models/person.py`

```python
# person.py
# Base class for User. Just holds a name and email.
# User inherits from this so we're using inheritance somewhere in the design.

class Person:
    def __init__(self, name, email=""):
        self.name = name
        self.email = email

    def __repr__(self):
        return f"{self.name} <{self.email}>"
```

## `models/user.py`

```python
# user.py
# A User is a Person that can own multiple projects.

from models.person import Person


class User(Person):
    # keeps track of the next id to hand out
    next_id = 1

    def __init__(self, name, email="", user_id=None):
        super().__init__(name, email)

        if user_id is None:
            self.id = User.next_id
            User.next_id += 1
        else:
            # loading an existing user from the JSON file
            self.id = user_id
            if user_id >= User.next_id:
                User.next_id = user_id + 1

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email}

    @staticmethod
    def from_dict(data):
        return User(name=data["name"], email=data.get("email", ""), user_id=data["id"])

    def __str__(self):
        return f"User #{self.id}: {self.name} ({self.email})"
```

## `models/project.py`

```python
# project.py
# A Project belongs to one User and can have many Tasks.

from utils.validators import is_valid_date


class Project:
    next_id = 1

    def __init__(self, title, owner_id, description="", due_date="", project_id=None):
        if not title.strip():
            raise ValueError("Project title cannot be empty.")
        if due_date and not is_valid_date(due_date):
            raise ValueError("due_date must look like YYYY-MM-DD.")

        self.title = title
        self.owner_id = owner_id
        self.description = description
        self.due_date = due_date

        if project_id is None:
            self.id = Project.next_id
            Project.next_id += 1
        else:
            self.id = project_id
            if project_id >= Project.next_id:
                Project.next_id = project_id + 1

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "owner_id": self.owner_id,
        }

    @staticmethod
    def from_dict(data):
        return Project(
            title=data["title"],
            owner_id=data["owner_id"],
            description=data.get("description", ""),
            due_date=data.get("due_date", ""),
            project_id=data["id"],
        )

    def __str__(self):
        due = f" (due {self.due_date})" if self.due_date else ""
        return f"Project #{self.id}: {self.title}{due}"
```

## `models/task.py`

```python
# task.py
# A Task belongs to one Project and can be assigned to a user by name.

VALID_STATUSES = ["todo", "in-progress", "done"]


class Task:
    next_id = 1

    def __init__(self, title, project_id, assigned_to="", status="todo", task_id=None):
        if not title.strip():
            raise ValueError("Task title cannot be empty.")

        self.title = title
        self.project_id = project_id
        self.assigned_to = assigned_to
        self.status = status  # goes through the setter below

        if task_id is None:
            self.id = Task.next_id
            Task.next_id += 1
        else:
            self.id = task_id
            if task_id >= Task.next_id:
                Task.next_id = task_id + 1

    # using a property here so status can't be set to something invalid
    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if value not in VALID_STATUSES:
            raise ValueError(f"status must be one of {VALID_STATUSES}")
        self._status = value

    def complete(self):
        self.status = "done"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "assigned_to": self.assigned_to,
            "project_id": self.project_id,
        }

    @staticmethod
    def from_dict(data):
        return Task(
            title=data["title"],
            project_id=data["project_id"],
            assigned_to=data.get("assigned_to", ""),
            status=data.get("status", "todo"),
            task_id=data["id"],
        )

    def __str__(self):
        who = f" -> {self.assigned_to}" if self.assigned_to else ""
        return f"Task #{self.id} [{self.status}]: {self.title}{who}"
```

## `models/__init__.py`

```python
from models.person import Person
from models.user import User
from models.project import Project
from models.task import Task
```

## `utils/__init__.py`

Just create an empty file with that name.

## `utils/storage.py`

```python
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
```

## `utils/validators.py`

```python
# validators.py
# A couple of small helper functions used when validating user input.

import re


def is_valid_date(date_str):
    # expects something like 2026-08-01
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", date_str))


def is_valid_email(email):
    if not email:
        return True
    return "@" in email and "." in email
```

## `tests/__init__.py`

Just create an empty file with that name.

## `tests/test_models.py````python
# test_models.py
# Basic tests for the User, Project, and Task classes.

import pytest

from models.user import User
from models.project import Project
from models.task import Task


def test_user_has_id_and_email():
    u = User(name="Alex", email="alex@example.com")
    assert u.name == "Alex"
    assert u.email == "alex@example.com"
    assert u.id > 0


def test_two_users_get_different_ids():
    u1 = User(name="Alex")
    u2 = User(name="Sam")
    assert u1.id != u2.id


def test_project_needs_a_title():
    with pytest.raises(ValueError):
        Project(title="", owner_id=1)


def test_project_bad_due_date_raises_error():
    with pytest.raises(ValueError):
        Project(title="CLI Tool", owner_id=1, due_date="not-a-date")


def test_project_good_due_date_is_fine():
    p = Project(title="CLI Tool", owner_id=1, due_date="2026-08-01")
    assert p.due_date == "2026-08-01"


def test_task_starts_as_todo():
    t = Task(title="Write tests", project_id=1)
    assert t.status == "todo"


def test_task_complete_sets_status_to_done():
    t = Task(title="Write tests", project_id=1)
    t.complete()
    assert t.status == "done"


def test_task_rejects_bad_status():
    t = Task(title="Write tests", project_id=1)
    with pytest.raises(ValueError):
        t.status = "not-a-real-status"


def test_task_to_dict_and_back():
    t = Task(title="Write tests", project_id=1, assigned_to="Sam")
    data = t.to_dict()
    t2 = Task.from_dict(data)
    assert t2.title == t.title
    assert t2.assigned_to == "Sam"
```

## `tests/test_cli.py````python
# test_cli.py
# Tests for the command functions in main.py.
# We fake argparse's Namespace with a tiny helper class, and clear
# out main's user/project/task lists before each test so they don't
# affect each other.

import os

import pytest

import main


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture(autouse=True)
def reset_lists(monkeypatch):
    main.users.clear()
    main.projects.clear()
    main.tasks.clear()
    # don't actually touch the JSON files while testing
    monkeypatch.setattr(main, "save_data", lambda: None)
    yield


def test_add_user(capsys):
    main.add_user(Args(name="Alex", email="alex@example.com"))
    assert main.find_user("Alex") is not None
    out = capsys.readouterr().out
    assert "Added" in out


def test_add_user_twice_fails(capsys):
    main.add_user(Args(name="Alex", email=""))
    main.add_user(Args(name="Alex", email=""))
    out = capsys.readouterr().out
    assert "already exists" in out
    assert len(main.users) == 1


def test_add_project_needs_existing_user(capsys):
    main.add_project(Args(user="Ghost", title="CLI Tool", description="", due_date=""))
    out = capsys.readouterr().out
    assert "no user named" in out


def test_add_project_works(capsys):
    main.add_user(Args(name="Alex", email=""))
    main.add_project(Args(user="Alex", title="CLI Tool", description="", due_date=""))
    project = main.find_project("CLI Tool")
    assert project is not None
    owner = main.find_user("Alex")
    assert project.owner_id == owner.id


def test_add_task_needs_existing_project(capsys):
    main.add_task(Args(project="Ghost Project", title="Do thing", assigned_to=""))
    out = capsys.readouterr().out
    assert "no project called" in out


def test_add_task_and_complete_it():
    main.add_user(Args(name="Alex", email=""))
    main.add_project(Args(user="Alex", title="CLI Tool", description="", due_date=""))
    main.add_task(Args(project="CLI Tool", title="Write tests", assigned_to="Sam"))

    task = main.tasks[0]
    assert task.status == "todo"

    main.complete_task(Args(task_id=task.id))
    assert task.status == "done"


def test_complete_task_bad_id(capsys):
    main.complete_task(Args(task_id=999))
    out = capsys.readouterr().out
    assert "no task with id" in out


def test_logging_is_set_up_and_writes_to_a_file():
    # main.py sets up its own logger, pointing at data/app.log
    assert main.logger.handlers
    main.add_user(Args(name="LoggedUser", email=""))
    assert os.path.exists("data/app.log")
```

## `requirements.txt`

```
rich>=13.0.0
pytest>=8.0.0
```

## `Pipfile`

```
[[source]]
url = "https://pypi.org/simple"
verify_ssl = true
name = "pypi"

[packages]
rich = "*"

[dev-packages]
pytest = "*"

[requires]
python_version = "3.10"
```

## `.gitignore`

```
__pycache__/
*.pyc
.pytest_cache/
.venv/
venv/
*.egg-info/
data/app.log
```

## `README.md````markdown
# Project Tracker CLI

A command-line tool for managing users, projects, and tasks. This was built
for my Python summative lab — it lets you add users, give them projects,
add tasks to those projects, and mark tasks as done, all from the terminal.
Data is saved to JSON files so it's still there next time you run it.

## Project Structure

```
project-tracker-cli/
├── main.py             # CLI commands (argparse) live here
├── models/
│   ├── person.py        # base class for User
│   ├── user.py
│   ├── project.py
│   └── task.py
├── utils/
│   ├── storage.py       # reading/writing the JSON files
│   └── validators.py
├── data/                 # saved users/projects/tasks + app.log
├── tests/                # pytest tests
├── requirements.txt
├── Pipfile
└── README.md
```

## Setup

1. Clone the repo
   ```
   git clone https://github.com/<your-username>/project-tracker-cli.git
   cd project-tracker-cli
   ```

2. (optional) make a virtual environment
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the dependencies
   ```
   pip install -r requirements.txt
   ```
   (a `Pipfile` is also included if you'd rather use `pipenv install`)

## How to Use It

```
python main.py add-user --name "Alex" --email "alex@example.com"
python main.py list-users

python main.py add-project --user "Alex" --title "CLI Tool" --description "Build a project tracker" --due-date "2026-08-01"
python main.py list-projects
python main.py list-projects --user "Alex"

python main.py add-task --project "CLI Tool" --title "Implement add-task" --assigned-to "Sam"
python main.py list-tasks --project "CLI Tool"
python main.py complete-task --task-id 1
```

Run `python main.py --help` to see all commands, or `python main.py <command> --help`
for a specific one.

## Tests

```
python -m pytest tests/ -v
```

Tests cover the model classes (User/Project/Task) and the CLI command
functions in main.py.

## Logging

Every add/complete action gets logged to `data/app.log` (successes as
INFO, failed attempts like a duplicate name as WARNING). Useful for
tracing what happened while testing/debugging.


## Built With

- Python 3.10+
- argparse, json (standard library)
- rich (for the nicer looking tables)
- pytest (for testing)
```

---

**Folder layout to create:**
```
project-tracker-cli/
├── main.py
├── requirements.txt
├── Pipfile
├── .gitignore
├── README.md
├── models/
│   ├── __init__.py
│   ├── person.py
│   ├── user.py
│   ├── project.py
│   └── task.py
├── utils/
│   ├── __init__.py
│   ├── storage.py
│   └── validators.py
├── data/
└── tests/
    ├── __init__.py
    ├── test_models.py
    └── test_cli.py
```
