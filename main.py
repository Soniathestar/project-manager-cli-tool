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


# command functions

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
