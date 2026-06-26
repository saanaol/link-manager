import math
import secrets

import markupsafe
from flask import Flask, abort, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

import categories
import comments
import config
import links
import users


app = Flask(__name__)
app.secret_key = config.secret_key


USERNAME_MIN_LENGTH = 2
USERNAME_MAX_LENGTH = 16
PASSWORD_MIN_LENGTH = 8
TITLE_MIN_LETTERS = 3
TITLE_MAX_LENGTH = 100
SEARCH_QUERY_MAX_LENGTH = TITLE_MAX_LENGTH
URL_MAX_LENGTH = 300
NOTES_MAX_LENGTH = 1000
COMMENT_MAX_LENGTH = 500
COMMENT_MAX_LINES = 10
PAGE_SIZE = 10
COMMENT_PAGE_SIZE = 5
USER_LINK_PAGE_SIZE = 10


@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)
    return session["csrf_token"]


app.jinja_env.globals["csrf_token"] = csrf_token


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


def count_letters(text):
    return sum(1 for char in text if char.isalpha())


def validate_link_title(title):
    if not title:
        return "Title cannot be empty"

    if len(title) > TITLE_MAX_LENGTH:
        return "Title must be at most 100 characters long"

    if count_letters(title) < TITLE_MIN_LETTERS:
        return "Title must contain at least 3 letters"

    return None


def render_new_link_form(title="", url="", notes="", selected_category_ids=None):
    if selected_category_ids is None:
        selected_category_ids = []

    all_categories = categories.get_all_categories()

    return render_template(
        "new_link.html",
        categories=all_categories,
        filled={
            "title": title,
            "url": url,
            "notes": notes,
        },
        selected_category_ids=selected_category_ids)


def render_link_page(link_id, filled_comment=""):
    link = links.get_link(link_id)

    if not link:
        abort(404)

    page = 1
    comment_count = comments.count_link_comments(link_id)
    page_count = math.ceil(comment_count / COMMENT_PAGE_SIZE)
    page_count = max(page_count, 1)

    link_categories = categories.get_link_categories(link_id)
    link_comments = comments.get_link_comments(
        link_id,
        page,
        COMMENT_PAGE_SIZE)

    return render_template(
        "link.html",
        link=link,
        categories=link_categories,
        comments=link_comments,
        filled_comment=filled_comment,
        page=page,
        page_count=page_count)


@app.route("/")
def index():
    if "user_id" in session:
        return redirect("/links")

    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", filled={})

    username = request.form["username"].strip()
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    filled = {"username": username}

    if not username:
        flash("Username cannot be empty")
        return render_template("register.html", filled=filled)

    if len(username) < USERNAME_MIN_LENGTH:
        flash("Username must be at least 2 characters long")
        return render_template("register.html", filled=filled)

    if len(username) > USERNAME_MAX_LENGTH:
        flash("Username must be at most 16 characters long")
        return render_template("register.html", filled=filled)

    if not password1:
        flash("Password cannot be empty")
        return render_template("register.html", filled=filled)

    if len(password1) < PASSWORD_MIN_LENGTH:
        flash("Password must be at least 8 characters long")
        return render_template("register.html", filled=filled)

    if password1 != password2:
        flash("Passwords do not match")
        return render_template("register.html", filled=filled)

    if users.username_exists(username):
        flash("Username is already taken")
        return render_template("register.html", filled=filled)

    password_hash = generate_password_hash(password1)

    if not users.add_user(username, password_hash):
        flash("Username is already taken")
        return render_template("register.html", filled=filled)

    flash("Account created. You can now sign in.")
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", filled={})

    username = request.form["username"].strip()
    password = request.form["password"]

    filled = {"username": username}

    user = users.get_user_by_username(username)

    if not user:
        flash("Invalid username or password")
        return render_template("login.html", filled=filled)

    if check_password_hash(user["password_hash"], password):
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["csrf_token"] = secrets.token_hex(16)
        return redirect("/links")

    flash("Invalid username or password")
    return render_template("login.html", filled=filled)


@app.route("/logout", methods=["POST"])
def logout():
    login_error = require_login()
    if login_error:
        return login_error

    check_csrf()
    session.clear()
    return redirect("/login")


@app.route("/links", methods=["GET"])
@app.route("/links/<int:page>", methods=["GET"])
def show_links(page=1):
    login_error = require_login()
    if login_error:
        return login_error

    link_count = links.count_links()
    page_count = math.ceil(link_count / PAGE_SIZE)
    page_count = max(page_count, 1)

    if page < 1:
        return redirect("/links")

    if page > page_count:
        return redirect("/links/" + str(page_count))

    page_links = links.get_links(page, PAGE_SIZE)

    link_categories = {}
    for link in page_links:
        link_categories[link["id"]] = categories.get_link_categories(link["id"])

    return render_template(
        "links.html",
        links=page_links,
        link_categories=link_categories,
        search_performed=False,
        query="",
        page=page,
        page_count=page_count)


@app.route("/links/new")
def new_link():
    login_error = require_login()
    if login_error:
        return login_error

    return render_new_link_form()


@app.route("/link/<int:link_id>")
def show_link(link_id):
    login_error = require_login()
    if login_error:
        return login_error

    link = links.get_link(link_id)

    if not link:
        abort(404)

    page = request.args.get("page", 1, type=int)

    if page < 1:
        return redirect("/link/" + str(link_id))

    comment_count = comments.count_link_comments(link_id)
    page_count = math.ceil(comment_count / COMMENT_PAGE_SIZE)
    page_count = max(page_count, 1)

    if page > page_count:
        return redirect("/link/" + str(link_id) + "?page=" + str(page_count))

    link_categories = categories.get_link_categories(link_id)
    link_comments = comments.get_link_comments(
        link_id,
        page,
        COMMENT_PAGE_SIZE)

    return render_template(
        "link.html",
        link=link,
        categories=link_categories,
        comments=link_comments,
        page=page,
        page_count=page_count,
        filled_comment="")


@app.route("/add_link", methods=["POST"])
def add_link():
    login_error = require_login()
    if login_error:
        return login_error

    check_csrf()

    title = request.form["title"].strip()
    url = request.form["url"].strip()
    notes = request.form.get("notes", "").strip()
    selected_category_ids = request.form.getlist("categories")
    user_id = session["user_id"]

    title_error = validate_link_title(title)
    if title_error:
        flash(title_error)
        return render_new_link_form(title, url, notes, selected_category_ids)

    if not url:
        flash("URL cannot be empty")
        return render_new_link_form(title, url, notes, selected_category_ids)

    if len(url) > URL_MAX_LENGTH:
        flash("URL is too long")
        return render_new_link_form(title, url, notes, selected_category_ids)

    if len(notes) > NOTES_MAX_LENGTH:
        flash("Notes are too long")
        return render_new_link_form(title, url, notes, selected_category_ids)

    if not url.startswith(("http://", "https://")):
        flash("URL must start with http:// or https://")
        return render_new_link_form(title, url, notes, selected_category_ids)

    for category_id in selected_category_ids:
        if not categories.category_exists(category_id):
            abort(403)

    link_id = links.add_link(title, url, notes, user_id)

    for category_id in selected_category_ids:
        categories.add_link_category(link_id, category_id)

    return redirect("/link/" + str(link_id))


@app.route("/add_comment/<int:link_id>", methods=["POST"])
def add_comment(link_id):
    login_error = require_login()
    if login_error:
        return login_error

    check_csrf()

    link = links.get_link(link_id)

    if not link:
        abort(404)

    content = request.form["content"]
    cleaned_content = content.strip()

    if not cleaned_content:
        flash("Comment cannot be empty")
        return render_link_page(link_id, content)

    if len(cleaned_content) > COMMENT_MAX_LENGTH:
        flash("Comment is too long")
        return render_link_page(link_id, content)

    if cleaned_content.count("\n") + 1 > COMMENT_MAX_LINES:
        flash("Comment can have at most 10 lines")
        return render_link_page(link_id, content)

    comments.add_comment(link_id, session["user_id"], cleaned_content)

    return redirect("/link/" + str(link_id))


@app.route("/edit_link/<int:link_id>", methods=["GET", "POST"])
def edit_link(link_id):
    login_error = require_login()
    if login_error:
        return login_error

    link = links.get_link(link_id)

    if not link:
        abort(404)

    require_link_owner(link)

    all_categories = categories.get_all_categories()
    selected_category_ids = categories.get_link_category_ids(link_id)

    if request.method == "GET":
        return render_template(
            "edit_link.html",
            link=link,
            categories=all_categories,
            selected_category_ids=selected_category_ids)

    check_csrf()

    title = request.form["title"].strip()
    url = request.form["url"].strip()
    notes = request.form.get("notes", "").strip()
    selected_category_ids = request.form.getlist("categories")

    def render_edit_form():
        return render_template(
            "edit_link.html",
            link=link,
            categories=all_categories,
            selected_category_ids=selected_category_ids)

    title_error = validate_link_title(title)
    if title_error:
        flash(title_error)
        return render_edit_form()

    if not url:
        flash("URL cannot be empty")
        return render_edit_form()

    if len(url) > URL_MAX_LENGTH:
        flash("URL is too long")
        return render_edit_form()

    if len(notes) > NOTES_MAX_LENGTH:
        flash("Notes are too long")
        return render_edit_form()

    if not url.startswith(("http://", "https://")):
        flash("URL must start with http:// or https://")
        return render_edit_form()

    for category_id in selected_category_ids:
        if not categories.category_exists(category_id):
            abort(403)

    links.update_link(link_id, title, url, notes)

    categories.remove_link_categories(link_id)
    for category_id in selected_category_ids:
        categories.add_link_category(link_id, category_id)

    return redirect("/link/" + str(link_id))


@app.route("/remove_link/<int:link_id>", methods=["GET", "POST"])
def remove_link(link_id):
    login_error = require_login()
    if login_error:
        return login_error

    link = links.get_link(link_id)

    if not link:
        abort(404)

    require_link_owner(link)

    if request.method == "GET":
        return render_template("remove_link.html", link=link)

    check_csrf()

    if "continue" in request.form:
        comments.remove_link_comments(link_id)
        categories.remove_link_categories(link_id)
        links.remove_link(link_id)
        return redirect("/links")

    return redirect("/link/" + str(link_id))


@app.route("/search_links", methods=["GET"])
def search_links():
    login_error = require_login()
    if login_error:
        return login_error

    query = request.args.get("query", "").strip()

    if len(query) > SEARCH_QUERY_MAX_LENGTH:
        flash("Search query must be at most 100 characters long")
        return redirect("/links")

    if not query:
        return redirect("/links")

    found_links = links.search_links(query)

    link_categories = {}
    for link in found_links:
        link_categories[link["id"]] = categories.get_link_categories(link["id"])

    return render_template(
        "links.html",
        links=found_links,
        link_categories=link_categories,
        search_performed=True,
        query=query)


@app.route("/user/<int:user_id>")
def user_page(user_id):
    login_error = require_login()
    if login_error:
        return login_error

    user = users.get_user(user_id)

    if not user:
        abort(404)

    page = request.args.get("page", 1, type=int)

    if page < 1:
        return redirect("/user/" + str(user_id))

    link_count = links.count_user_links(user_id)
    page_count = math.ceil(link_count / USER_LINK_PAGE_SIZE)
    page_count = max(page_count, 1)

    if page > page_count:
        return redirect("/user/" + str(user_id) + "?page=" + str(page_count))

    user_links = links.get_user_links(user_id, page, USER_LINK_PAGE_SIZE)
    comment_count = comments.count_user_comments(user_id)

    return render_template(
        "user.html",
        user=user,
        user_id=user_id,
        user_links=user_links,
        link_count=link_count,
        comment_count=comment_count,
        page=page,
        page_count=page_count)
