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