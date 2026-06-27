"""Authentication, session and CSRF helper functions."""

import secrets

from flask import abort, redirect, request, session

import users


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)

    return session["csrf_token"]


def check_csrf():
    if "csrf_token" not in session:
        abort(403)

    if request.form.get("csrf_token") != session["csrf_token"]:
        abort(403)


def require_login():
    user_id = session.get("user_id")
    username = session.get("username")

    if not user_id or not username:
        session.clear()
        return redirect("/login")

    if not users.get_session_user(user_id, username):
        session.clear()
        return redirect("/login")

    return None


def require_link_owner(link):
    if link["user_id"] != session["user_id"]:
        abort(403)


def login_user(user):
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["csrf_token"] = secrets.token_hex(16)


def logout_user():
    session.clear()


def is_logged_in():
    user_id = session.get("user_id")
    username = session.get("username")

    if not user_id or not username:
        return False

    return bool(users.get_session_user(user_id, username))


def get_user_id():
    return session["user_id"]
