import sqlite3
from flask import Flask, redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import db
import config

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    if "user_id" in session:
        return redirect("/links")
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if password1 != password2:
            return render_template("passwords_not_matching.html")

        password_hash = generate_password_hash(password1)

        try:
            sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
            db.execute(sql, [username, password_hash])
        except sqlite3.IntegrityError:
            return render_template("username_taken.html")  

        return render_template("account_created.html") 

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        sql = "SELECT id, password_hash FROM users WHERE username = ?"
        result = db.query(sql, [username])

        if not result:
            return render_template("passwords_not_matching.html")  
            
        user_id = result[0][0]
        password_hash = result[0][1]

        if check_password_hash(password_hash, password):
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/links")
        else:
            return render_template("passwords_not_matching.html")  

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect("/login")

@app.route("/links", methods=["GET"])
def show_links():
    if "user_id" not in session:
        return redirect("/login")

    sql = "SELECT * FROM links ORDER BY id DESC"
    links = db.query(sql)

    return render_template(
    	"links.html",
        links = links,
        search_performed = False,
        query = "")

@app.route("/add_link", methods=["POST"])
def add_link():
    title = request.form["title"]
    url = request.form["url"]
    user_id = session["user_id"]

    sql = "INSERT INTO links (title, url, user_id) VALUES (?, ?, ?)"
    db.execute(sql, [title, url, user_id])
    return redirect("/links")

@app.route("/edit_link/<int:link_id>", methods=["GET", "POST"])
def edit_link(link_id):
    if request.method == "GET":
        sql = "SELECT * FROM links WHERE id = ?"
        link = db.query(sql, [link_id])[0]
        return render_template("edit_link.html", link=link)
    else:
        title = request.form["title"]
        url = request.form["url"]
        sql = "UPDATE links SET title = ?, url = ? WHERE id = ?"
        db.execute(sql, [title, url, link_id])
        return redirect("/links")

@app.route("/remove_link/<int:link_id>", methods=["POST"])
def remove_link(link_id):
    sql = "DELETE FROM links WHERE id = ?"
    db.execute(sql, [link_id])
    return redirect("/links")

@app.route("/search_links", methods=["GET"])
def search_links():
    if "user_id" not in session:
        return redirect("/login")

    query = request.args.get("query", "").strip()

    if not query:
        return redirect("/links")

    sql = "SELECT * FROM links WHERE title LIKE ? ORDER BY id DESC"
    links = db.query(sql, ["%" + query + "%"])

    return render_template(
        "links.html",
        links = links,
        search_performed = True,
        query = query)
