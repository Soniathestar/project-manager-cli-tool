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