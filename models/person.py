# person.py
# Base class for User. Just holds a name and email.
# User inherits from this so we're using inheritance somewhere in the design.

class Person:
    def __init__(self, name, email=""):
        self.name = name
        self.email = email

    def __repr__(self):
        return f"{self.name} <{self.email}>"