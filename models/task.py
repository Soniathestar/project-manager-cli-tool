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