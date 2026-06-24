from flask import Flask, redirect, render_template, request, session, abort, flash
from werkzeug.security import generate_password_hash, check_password_hash
import config
import secrets
import users
import links
import categories
import comments

app = Flask(__name__)
app.secret_key = config.secret_key

USERNAME_MIN_LENGTH = 2
USERNAME_MAX_LENGTH = 16
PASSWORD_MIN_LENGTH = 8
TITLE_MIN_LETTERS = 3
TITLE_MAX_LENGTH = 100
URL_MAX_LENGTH = 300
NOTES_MAX_LENGTH = 1000
COMMENT_MAX_LENGTH = 500


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
        return "Title must be at most 40 characters long"

    if count_letters(title) < TITLE_MIN_LETTERS:
        return "Title must contain at least 3 letters"

    return None


@app.route("/")
def index():
    if "user_id" in session:
        return redirect("/links")
    return redirect("/login")


@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", filled = {})

    username = request.form["username"].strip()
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    filled = {"username": username}

    if not username:
        flash("Username cannot be empty")
        return render_template("register.html", filled = filled)

    if len(username) < USERNAME_MIN_LENGTH:
        flash("Username must be at least 2 characters long")
        return render_template("register.html", filled = filled)

    if len(username) > USERNAME_MAX_LENGTH:
        flash("Username must be at most 16 characters long")
        return render_template("register.html", filled = filled)

    if not password1:
        flash("Password cannot be empty")
        return render_template("register.html", filled = filled)

    if len(password1) < PASSWORD_MIN_LENGTH:
        flash("Password must be at least 8 characters long")
        return render_template("register.html", filled = filled)

    if password1 != password2:
        flash("Passwords do not match")
        return render_template("register.html", filled = filled)

    if users.username_exists(username):
        flash("Username is already taken")
        return render_template("register.html", filled = filled)

    password_hash = generate_password_hash(password1)

    if not users.add_user(username, password_hash):
        flash("Username is already taken")
        return render_template("register.html", filled = filled)

    flash("Account created. You can now sign in.")
    return redirect("/login")


@app.route("/login", methods = ["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html", filled = {})

    username = request.form["username"].strip()
    password = request.form["password"]

    filled = {"username": username}

    user = users.get_user_by_username(username)

    if not user:
        flash("Invalid username or password")
        return render_template("login.html", filled = filled)

    if check_password_hash(user["password_hash"], password):
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["csrf_token"] = secrets.token_hex(16)
        return redirect("/links")

    flash("Invalid username or password")
    return render_template("login.html", filled = filled)


@app.route("/logout", methods = ["POST"])
def logout():
    login_error = require_login()
    if login_error:
        return login_error

    check_csrf()
    session.clear()
    return redirect("/login")


@app.route("/links", methods = ["GET"])
def show_links():
    login_error = require_login()
    if login_error:
        return login_error

    all_links = links.get_all_links()

    link_categories = {}

    for link in all_links:
        link_categories[link["id"]] = categories.get_link_categories(link["id"])

    return render_template(
        "links.html",
        links = all_links,
        link_categories = link_categories,
        search_performed = False,
        query = "")


@app.route("/links/new")
def new_link():
    login_error = require_login()
    if login_error:
        return login_error

    all_categories = categories.get_all_categories()

    return render_template("new_link.html", categories = all_categories)


@app.route("/link/<int:link_id>")
def show_link(link_id):
    login_error = require_login()
    if login_error:
        return login_error

    link = links.get_link(link_id)

    if not link:
        abort(404)

    link_categories = categories.get_link_categories(link_id)
    link_comments = comments.get_link_comments(link_id)

    return render_template(
        "link.html",
        link = link,
        categories = link_categories,
        comments = link_comments)


@app.route("/add_link", methods = ["POST"])
def add_link():
    login_error = require_login()
    if login_error:
        return login_error

    check_csrf()

    title = request.form["title"].strip()
    url = request.form["url"].strip()
    notes = request.form.get("notes", "").strip()
    user_id = session["user_id"]

    title_error = validate_link_title(title)
    if title_error:
        flash(title_error)
        return render_template("edit_link.html", link=link)

    if not url:
        flash("URL cannot be empty")
        return redirect("/links/new")

    if len(url) > URL_MAX_LENGTH:
        flash("URL is too long")
        return redirect("/links/new")

    if len(notes) > NOTES_MAX_LENGTH:
        flash("Notes are too long")
        return redirect("/links/new")

    if not url.startswith(("http://", "https://")):
        flash("URL must start with http:// or https://")
        return redirect("/links/new")

    link_id = links.add_link(title, url, notes, user_id)

    category_ids = request.form.getlist("categories")

    for category_id in category_ids:
        if not categories.category_exists(category_id):
            abort(403)

        categories.add_link_category(link_id, category_id)

    return redirect("/link/" + str(link_id))


@app.route("/add_comment/<int:link_id>", methods = ["POST"])
def add_comment(link_id):
    login_error = require_login()
    if login_error:
        return login_error

    check_csrf()

    link = links.get_link(link_id)

    if not link:
        abort(404)

    content = request.form["content"].strip()

    if not content:
        flash("Additional information cannot be empty")
        return redirect("/link/" + str(link_id))

    if len(content) > COMMENT_MAX_LENGTH:
        flash("Additional information is too long")
        return redirect("/link/" + str(link_id))

    comments.add_comment(link_id, session["user_id"], content)

    return redirect("/link/" + str(link_id))


@app.route("/edit_link/<int:link_id>", methods = ["GET", "POST"])
def edit_link(link_id):
    login_error = require_login()
    if login_error:
        return login_error

    link = links.get_link(link_id)

    if not link:
        abort(404)

    require_link_owner(link)

    if request.method == "GET":
        return render_template("edit_link.html", link = link)

    check_csrf()

    title = request.form["title"].strip()
    url = request.form["url"].strip()
    notes = request.form.get("notes", "").strip()

    title_error = validate_link_title(title)
    if title_error:
        flash(title_error)
        return render_template("edit_link.html", link=link)

    if not url:
        flash("URL cannot be empty")
        return render_template("edit_link.html", link = link)

    if len(url) > URL_MAX_LENGTH:
        flash("URL is too long")
        return render_template("edit_link.html", link = link)

    if len(notes) > NOTES_MAX_LENGTH:
        flash("Notes are too long")
        return render_template("edit_link.html", link = link)

    if not url.startswith(("http://", "https://")):
        flash("URL must start with http:// or https://")
        return render_template("edit_link.html", link = link)

    links.update_link(link_id, title, url, notes)

    return redirect("/link/" + str(link_id))


@app.route("/remove_link/<int:link_id>", methods = ["GET", "POST"])
def remove_link(link_id):
    login_error = require_login()
    if login_error:
        return login_error

    link = links.get_link(link_id)

    if not link:
        abort(404)

    require_link_owner(link)

    if request.method == "GET":
        return render_template("remove_link.html", link = link)

    check_csrf()

    if "continue" in request.form:
        comments.remove_link_comments(link_id)
        categories.remove_link_categories(link_id)
        links.remove_link(link_id)
        return redirect("/links")

    return redirect("/link/" + str(link_id))


@app.route("/search_links", methods = ["GET"])
def search_links():
    login_error = require_login()
    if login_error:
        return login_error

    query = request.args.get("query", "").strip()

    if not query:
        return redirect("/links")

    found_links = links.search_links(query)

    link_categories = {}

    for link in found_links:
        link_categories[link["id"]] = categories.get_link_categories(link["id"])

    return render_template(
        "links.html",
        links = found_links,
        link_categories = link_categories,
        search_performed = True,
        query = query)


@app.route("/user/<int:user_id>")
def user_page(user_id):
    login_error = require_login()
    if login_error:
        return login_error

    user = users.get_user(user_id)

    if not user:
        abort(404)

    user_links = links.get_user_links(user_id)
    link_count = links.count_user_links(user_id)

    return render_template(
        "user.html",
        user = user,
        user_links = user_links,
        link_count = link_count)
