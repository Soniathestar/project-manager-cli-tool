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


def test_add_project_suggests_close_username_on_typo(capsys):
    main.add_user(Args(name="Alex", email=""))
    main.add_project(Args(user="Alx", title="CLI Tool", description="", due_date=""))
    out = capsys.readouterr().out
    assert "Did you mean 'Alex'?" in out


def test_add_task_suggests_close_project_title_on_typo(capsys):
    main.add_user(Args(name="Alex", email=""))
    main.add_project(Args(user="Alex", title="CLI Tool", description="", due_date=""))
    main.add_task(Args(project="CLI Toool", title="Do thing", assigned_to=""))
    out = capsys.readouterr().out
    assert "Did you mean 'CLI Tool'?" in out


def test_delete_task_removes_it():
    main.add_user(Args(name="Alex", email=""))
    main.add_project(Args(user="Alex", title="CLI Tool", description="", due_date=""))
    main.add_task(Args(project="CLI Tool", title="Write tests", assigned_to=""))
    task_id = main.tasks[0].id

    main.delete_task(Args(task_id=task_id))
    assert main.find_task(task_id) is None


def test_delete_project_blocked_if_it_has_tasks(capsys):
    main.add_user(Args(name="Alex", email=""))
    main.add_project(Args(user="Alex", title="CLI Tool", description="", due_date=""))
    main.add_task(Args(project="CLI Tool", title="Write tests", assigned_to=""))

    main.delete_project(Args(title="CLI Tool"))
    out = capsys.readouterr().out
    assert "still has" in out
    assert main.find_project("CLI Tool") is not None


def test_delete_project_works_once_tasks_are_gone():
    main.add_user(Args(name="Alex", email=""))
    main.add_project(Args(user="Alex", title="CLI Tool", description="", due_date=""))
    main.add_task(Args(project="CLI Tool", title="Write tests", assigned_to=""))
    task_id = main.tasks[0].id

    main.delete_task(Args(task_id=task_id))
    main.delete_project(Args(title="CLI Tool"))
    assert main.find_project("CLI Tool") is None


def test_delete_user_blocked_if_they_own_projects(capsys):
    main.add_user(Args(name="Alex", email=""))
    main.add_project(Args(user="Alex", title="CLI Tool", description="", due_date=""))

    main.delete_user(Args(name="Alex"))
    out = capsys.readouterr().out
    assert "still owns" in out
    assert main.find_user("Alex") is not None