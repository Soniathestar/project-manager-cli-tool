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