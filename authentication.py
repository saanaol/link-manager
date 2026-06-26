import secrets

from flask import abort, redirect, request, session


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)

    return session["csrf_token"]


def check_csrf():
    if request.form.get("csrf_token") != session.get("csrf_token"):
        abort(403)


def require_login():
    if "user_id" not in session:
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
    return "user_id" in session


def get_user_id():
    return session["user_id"]
