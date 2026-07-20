
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
