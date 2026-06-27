"""Validation helper functions for form inputs."""

import re


USERNAME_MIN_LENGTH = 2
USERNAME_MAX_LENGTH = 16
PASSWORD_MIN_LENGTH = 8
TITLE_MIN_LETTERS = 3
TITLE_MAX_LENGTH = 50
SEARCH_QUERY_MAX_LENGTH = TITLE_MAX_LENGTH
URL_MAX_LENGTH = 300
NOTES_MAX_LENGTH = 1000
COMMENT_MAX_LENGTH = 500
COMMENT_MAX_LINES = 10


def count_letters(text):
    return sum(1 for char in text if char.isalpha())


def validate_username(username):
    if not username:
        return "Username cannot be empty"

    if len(username) < USERNAME_MIN_LENGTH:
        return "Username must be at least 2 characters long"

    if len(username) > USERNAME_MAX_LENGTH:
        return "Username must be at most 16 characters long"

    if re.fullmatch(r"[A-Za-z0-9_-]+", username) is None:
        return "Username can contain only letters, numbers, underscores and hyphens"

    return None


def validate_password(password):
    if not password:
        return "Password cannot be empty"

    if len(password) < PASSWORD_MIN_LENGTH:
        return "Password must be at least 8 characters long"

    return None


def validate_link_title(title):
    if not title:
        return "Title cannot be empty"

    if len(title) > TITLE_MAX_LENGTH:
        return "Title must be at most 50 characters long"

    if count_letters(title) < TITLE_MIN_LETTERS:
        return "Title must contain at least 3 letters"

    return None


def validate_url(url):
    if not url:
        return "URL cannot be empty"

    if len(url) > URL_MAX_LENGTH:
        return "URL is too long"

    if not url.startswith(("http://", "https://")):
        return "URL must start with http:// or https://"

    return None


def validate_notes(notes):
    if len(notes) > NOTES_MAX_LENGTH:
        return "Notes are too long"

    return None


def validate_comment(comment):
    if not comment:
        return "Comment cannot be empty"

    if len(comment) > COMMENT_MAX_LENGTH:
        return "Comment is too long"

    if comment.count("\n") + 1 > COMMENT_MAX_LINES:
        return "Comment can have at most 10 lines"

    return None


def validate_search_query(query):
    if len(query) > SEARCH_QUERY_MAX_LENGTH:
        return "Search query must be at most 50 characters long"

    return None
