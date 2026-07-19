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