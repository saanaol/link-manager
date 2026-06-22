import sqlite3
from flask import Flask, redirect, render_template, request, session, abort, flash
from werkzeug.security import generate_password_hash, check_password_hash
import db
import config
import secrets

app = Flask(__name__)
app.secret_key = config.secret_key


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)
    return session["csrf_token"]


app.jinja_env.globals["csrf_token"] = csrf_token


def check_csrf():
    if request.form.get("csrf_token") != session.get("csrf_token"):
        abort(403)


def get_link(link_id):
    sql = """
        SELECT l.id, l.title, l.url, l.notes, l.user_id, u.username
        FROM links l
        JOIN users u ON l.user_id = u.id
        WHERE l.id = ?
    """
    result = db.query(sql, [link_id])
    return result[0] if result else None


def get_link_categories(link_id):
    sql = """
        SELECT c.name
        FROM categories c
        JOIN link_categories lc ON c.id = lc.category_id
        WHERE lc.link_id = ?
        ORDER BY c.name
    """
    return db.query(sql, [link_id])


def get_link_comments(link_id):
    sql = """
        SELECT c.content, c.created_at, u.username
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.link_id = ?
        ORDER BY c.id DESC
    """
    return db.query(sql, [link_id])


@app.route("/")
def index():
    if "user_id" in session:
        return redirect("/links")
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", filled = {})

    username = request.form["username"].strip()
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    filled = {"username": username}

    if password1 != password2:
        flash("Passwords do not match")
        return render_template("register.html", filled = filled)

    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        flash("Username is already taken")
        return render_template("register.html", filled = filled)

    flash("Account created. You can now sign in.")
    return redirect("/login")
    

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html", filled = {})

    username = request.form["username"].strip()
    password = request.form["password"]

    filled = {"username": username}

    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])

    if not result:
        flash("Invalid username or password")
        return render_template("login.html", filled = filled)

    user_id = result[0]["id"]
    password_hash = result[0]["password_hash"]

    if check_password_hash(password_hash, password):
        session["user_id"] = user_id
        session["username"] = username
        session["csrf_token"] = secrets.token_hex(16)
        return redirect("/links")

    flash("Invalid username or password")
    return render_template("login.html", filled = filled)


@app.route("/logout", methods=["POST"])
def logout():
    check_csrf()
    session.clear()
    return redirect("/login")


@app.route("/links", methods=["GET"])
def show_links():
    if "user_id" not in session:
        return redirect("/login")

    sql = """
        SELECT l.id, l.title, l.url, l.user_id, u.username
        FROM links l
        JOIN users u ON l.user_id = u.id
        ORDER BY l.id DESC
    """
    links = db.query(sql)

    link_categories = {}

    for link in links:
        link_categories[link["id"]] = get_link_categories(link["id"])

    return render_template(
        "links.html",
        links = links,
        link_categories = link_categories,
        search_performed = False,
        query = "")


@app.route("/links/new")
def new_link():
    if "user_id" not in session:
        return redirect("/login")

    sql = "SELECT id, name FROM categories ORDER BY name"
    categories = db.query(sql)

    return render_template("new_link.html", categories=categories)


@app.route("/link/<int:link_id>")
def show_link(link_id):
    if "user_id" not in session:
        return redirect("/login")

    link = get_link(link_id)

    if not link:
        abort(404)

    categories = get_link_categories(link_id)
    comments = get_link_comments(link_id)

    return render_template(
        "link.html",
        link = link,
        categories = categories,
        comments = comments)


@app.route("/add_link", methods=["POST"])
def add_link():
    if "user_id" not in session:
        return redirect("/login")

    check_csrf()

    title = request.form["title"].strip()
    url = request.form["url"].strip()
    notes = request.form["notes"].strip()
    user_id = session["user_id"]

    if not title or not url:
        abort(403)

    if len(title) > 100 or len(url) > 300 or len(notes) > 1000:
        abort(403)

    sql = """
        INSERT INTO links (title, url, notes, user_id)
        VALUES (?, ?, ?, ?)
    """
    db.execute(sql, [title, url, notes, user_id])

    link_id = db.last_insert_id()

    category_ids = request.form.getlist("categories")

    for category_id in category_ids:
        sql = """
            INSERT INTO link_categories (link_id, category_id)
            VALUES (?, ?)
        """
        db.execute(sql, [link_id, category_id])

    return redirect("/link/" + str(link_id))


@app.route("/add_comment/<int:link_id>", methods=["POST"])
def add_comment(link_id):
    if "user_id" not in session:
        return redirect("/login")

    check_csrf()

    sql = "SELECT user_id FROM links WHERE id = ?"
    result = db.query(sql, [link_id])

    if not result:
        abort(404)

    link = result[0]

    if link["user_id"] == session["user_id"]:
        abort(403)

    content = request.form["content"].strip()

    if not content or len(content) > 500:
        abort(403)

    sql = """
        INSERT INTO comments (link_id, user_id, content)
        VALUES (?, ?, ?)
    """
    db.execute(sql, [link_id, session["user_id"], content])

    return redirect("/link/" + str(link_id))


@app.route("/edit_link/<int:link_id>", methods=["GET", "POST"])
def edit_link(link_id):
    if "user_id" not in session:
        return redirect("/login")

    link = get_link(link_id)

    if not link:
        abort(404)

    if link["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("edit_link.html", link=link)

    check_csrf()

    title = request.form["title"].strip()
    url = request.form["url"].strip()
    notes = request.form.get("notes", "").strip()

    if not title or not url:
        abort(403)

    if len(title) > 100 or len(url) > 300 or len(notes) > 1000:
        abort(403)

    sql = """
        UPDATE links
        SET title = ?, url = ?, notes = ?
        WHERE id = ?
    """
    db.execute(sql, [title, url, notes, link_id])

    return redirect("/link/" + str(link_id))


@app.route("/remove_link/<int:link_id>", methods=["GET", "POST"])
def remove_link(link_id):
    if "user_id" not in session:
        return redirect("/login")

    link = get_link(link_id)

    if not link:
        abort(404)

    if link["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_link.html", link = link)

    check_csrf()

    if "continue" in request.form:
        sql = "DELETE FROM links WHERE id = ?"
        db.execute(sql, [link_id])
        return redirect("/links")

    return redirect("/link/" + str(link_id))


@app.route("/search_links", methods=["GET"])
def search_links():
    if "user_id" not in session:
        return redirect("/login")

    query = request.args.get("query", "").strip()

    if not query:
        return redirect("/links")

    sql = """
        SELECT l.id, l.title, l.url, l.user_id, u.username
        FROM links l
        JOIN users u ON l.user_id = u.id
        WHERE l.title LIKE ? OR l.url LIKE ? OR l.notes LIKE ?
        ORDER BY l.id DESC
    """
    pattern = "%" + query + "%"
    links = db.query(sql, [pattern, pattern, pattern])

    link_categories = {}

    for link in links:
        link_categories[link["id"]] = get_link_categories(link["id"])

    return render_template(
        "links.html",
        links = links,
        link_categories = link_categories,
        search_performed = True,
        query = query)


@app.route("/user/<int:user_id>")
def user_page(user_id):
    if "user_id" not in session:
        return redirect("/login")

    sql = "SELECT id, username FROM users WHERE id = ?"
    result = db.query(sql, [user_id])

    if not result:
        abort(404)

    user = result[0]

    sql = """
        SELECT id, title, url
        FROM links
        WHERE user_id = ?
        ORDER BY id DESC
    """
    user_links = db.query(sql, [user_id])

    sql = "SELECT COUNT(*) AS count FROM links WHERE user_id = ?"
    link_count = db.query(sql, [user_id])[0]["count"]

    return render_template(
        "user.html",
        user = user,
        user_links = user_links,
        link_count = link_count)
