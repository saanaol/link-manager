"""Flask routes for the application."""

import markupsafe
from flask import Flask, abort, flash, redirect, render_template, request, url_for
from werkzeug.security import check_password_hash, generate_password_hash

import authentication
import categories
import comments
import config
import links
import pagination
import users
import validators


app = Flask(__name__)
app.secret_key = config.SECRET_KEY


PAGE_SIZE = 10
COMMENT_PAGE_SIZE = 5
USER_LINK_PAGE_SIZE = 10


@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)


app.jinja_env.globals["csrf_token"] = authentication.csrf_token


def get_link_form_error(title, url, notes):
    title_error = validators.validate_link_title(title)
    if title_error:
        return title_error

    url_error = validators.validate_url(url)
    if url_error:
        return url_error

    notes_error = validators.validate_notes(notes)
    if notes_error:
        return notes_error

    return None


def check_category_id(category_id):
    if category_id and not categories.category_exists(category_id):
        abort(403)


def get_category_id_from_form():
    category_id = request.form.get("category_id", "")

    if category_id:
        return category_id

    return None


def render_new_link_form(title="", url="", notes="", selected_category_id=""):
    all_categories = categories.get_all_categories()

    return render_template(
        "new_link.html",
        categories=all_categories,
        filled={
            "title": title,
            "url": url,
            "notes": notes,
        },
        selected_category_id=selected_category_id)


def render_link_page(link_id, filled_comment=""):
    link = links.get_link(link_id)

    if not link:
        abort(404)

    page = 1
    comment_count = comments.count_link_comments(link_id)
    page_count = pagination.get_page_count(comment_count, COMMENT_PAGE_SIZE)

    link_comments = comments.get_link_comments(
        link_id,
        page,
        COMMENT_PAGE_SIZE)

    return render_template(
        "link.html",
        link=link,
        comments=link_comments,
        filled_comment=filled_comment,
        page=page,
        page_count=page_count)


@app.route("/")
def index():
    if authentication.is_logged_in():
        return redirect("/links")

    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", filled={})

    authentication.check_csrf()

    username = request.form["username"].strip()
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    filled = {"username": username}

    username_error = validators.validate_username(username)
    if username_error:
        flash(username_error)
        return render_template("register.html", filled=filled)

    password_error = validators.validate_password(password1)
    if password_error:
        flash(password_error)
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

    authentication.check_csrf()

    username = request.form["username"].strip()
    password = request.form["password"]

    filled = {"username": username}

    user = users.get_user_by_username(username)

    if not user:
        flash("Invalid username or password")
        return render_template("login.html", filled=filled)

    if check_password_hash(user["password_hash"], password):
        authentication.login_user(user)
        return redirect("/links")

    flash("Invalid username or password")
    return render_template("login.html", filled=filled)


@app.route("/logout", methods=["POST"])
def logout():
    login_error = authentication.require_login()
    if login_error:
        return login_error

    authentication.check_csrf()
    authentication.logout_user()
    return redirect("/login")


@app.route("/links", methods=["GET"])
@app.route("/links/<int:page>", methods=["GET"])
def show_links(page=1):
    login_error = authentication.require_login()
    if login_error:
        return login_error

    link_count = links.count_links()
    page_count = pagination.get_page_count(link_count, PAGE_SIZE)

    if page < 1:
        return redirect("/links")

    if page > page_count:
        return redirect("/links/" + str(page_count))

    page_links = links.get_links(page, PAGE_SIZE)

    return render_template(
        "links.html",
        links=page_links,
        search_performed=False,
        query="",
        page=page,
        page_count=page_count)


@app.route("/links/new")
def new_link():
    login_error = authentication.require_login()
    if login_error:
        return login_error

    return render_new_link_form()


@app.route("/link/<int:link_id>")
def show_link(link_id):
    login_error = authentication.require_login()
    if login_error:
        return login_error

    link = links.get_link(link_id)

    if not link:
        abort(404)

    page = request.args.get("page", 1, type=int)

    if page < 1:
        return redirect("/link/" + str(link_id))

    comment_count = comments.count_link_comments(link_id)
    page_count = pagination.get_page_count(comment_count, COMMENT_PAGE_SIZE)

    if page > page_count:
        return redirect("/link/" + str(link_id) + "?page=" + str(page_count))

    link_comments = comments.get_link_comments(
        link_id,
        page,
        COMMENT_PAGE_SIZE)

    return render_template(
        "link.html",
        link=link,
        comments=link_comments,
        page=page,
        page_count=page_count,
        filled_comment="")


@app.route("/add_link", methods=["POST"])
def add_link():
    login_error = authentication.require_login()
    if login_error:
        return login_error

    authentication.check_csrf()

    title = request.form["title"].strip()
    url = request.form["url"].strip()
    notes = request.form.get("notes", "").strip()
    category_id = get_category_id_from_form()
    selected_category_id = category_id or ""
    user_id = authentication.get_user_id()

    form_error = get_link_form_error(title, url, notes)
    if form_error:
        flash(form_error)
        return render_new_link_form(title, url, notes, selected_category_id)

    check_category_id(category_id)

    link_id = links.add_link(title, url, notes, user_id, category_id)

    return redirect("/link/" + str(link_id))


@app.route("/add_comment/<int:link_id>", methods=["POST"])
def add_comment(link_id):
    login_error = authentication.require_login()
    if login_error:
        return login_error

    authentication.check_csrf()

    link = links.get_link(link_id)

    if not link:
        abort(404)

    content = request.form["content"]
    cleaned_content = content.strip()

    comment_error = validators.validate_comment(cleaned_content)
    if comment_error:
        flash(comment_error)
        return render_link_page(link_id, content)

    comments.add_comment(
        link_id,
        authentication.get_user_id(),
        cleaned_content)

    return redirect("/link/" + str(link_id))


@app.route("/edit_link/<int:link_id>", methods=["GET", "POST"])
def edit_link(link_id):
    login_error = authentication.require_login()
    if login_error:
        return login_error

    link = links.get_link(link_id)

    if not link:
        abort(404)

    authentication.require_link_owner(link)

    all_categories = categories.get_all_categories()

    if request.method == "GET":
        selected_category_id = ""
        if link["category_id"]:
            selected_category_id = str(link["category_id"])

        return render_template(
            "edit_link.html",
            link=link,
            categories=all_categories,
            selected_category_id=selected_category_id)

    authentication.check_csrf()

    title = request.form["title"].strip()
    url = request.form["url"].strip()
    notes = request.form.get("notes", "").strip()
    category_id = get_category_id_from_form()
    selected_category_id = category_id or ""

    def render_edit_form():
        filled_link = {
            "id": link["id"],
            "title": title,
            "url": url,
            "notes": notes,
            "user_id": link["user_id"],
            "category_id": category_id,
        }

        return render_template(
            "edit_link.html",
            link=filled_link,
            categories=all_categories,
            selected_category_id=selected_category_id)

    form_error = get_link_form_error(title, url, notes)
    if form_error:
        flash(form_error)
        return render_edit_form()

    check_category_id(category_id)

    links.update_link(link_id, title, url, notes, category_id)

    return redirect("/link/" + str(link_id))


@app.route("/remove_link/<int:link_id>", methods=["GET", "POST"])
def remove_link(link_id):
    login_error = authentication.require_login()
    if login_error:
        return login_error

    link = links.get_link(link_id)

    if not link:
        abort(404)

    authentication.require_link_owner(link)

    if request.method == "GET":
        return render_template("remove_link.html", link=link)

    authentication.check_csrf()

    if "continue" in request.form:
        comments.remove_link_comments(link_id)
        links.remove_link(link_id)
        return redirect("/links")

    return redirect("/link/" + str(link_id))


@app.route("/search_links", methods=["GET"])
def search_links():
    login_error = authentication.require_login()
    if login_error:
        return login_error

    query = request.args.get("query", "").strip()
    page = request.args.get("page", 1, type=int)

    query_error = validators.validate_search_query(query)
    if query_error:
        flash(query_error)
        return redirect("/links")

    if not query:
        return redirect("/links")

    if page < 1:
        return redirect(url_for("search_links", query=query))

    link_count = links.count_search_links(query)
    page_count = pagination.get_page_count(link_count, PAGE_SIZE)

    if page > page_count:
        return redirect(url_for(
            "search_links",
            query=query,
            page=page_count))

    found_links = links.search_links(query, page, PAGE_SIZE)

    return render_template(
        "links.html",
        links=found_links,
        search_performed=True,
        query=query,
        page=page,
        page_count=page_count)


@app.route("/user/<int:user_id>")
def user_page(user_id):
    login_error = authentication.require_login()
    if login_error:
        return login_error

    user = users.get_user(user_id)

    if not user:
        abort(404)

    page = request.args.get("page", 1, type=int)

    if page < 1:
        return redirect("/user/" + str(user_id))

    link_count = links.count_user_links(user_id)
    page_count = pagination.get_page_count(link_count, USER_LINK_PAGE_SIZE)

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
