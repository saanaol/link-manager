# Link Manager

A web application for saving, organising and searching useful links.

The application contains or will contain the following features:

* Users can create an account and log in to the application.
* Users can add, edit and delete links.
* Users can view all links added to the application.
* Users can search for links by keyword or other criteria.
* The user profile page shows statistics and the links added by the user.
* Users can assign one or more categories to a link.
* Users can add notes or descriptions to links.

# Instructions for testing

Run the following commands:

    git clone https://github.com/saanaol/link-manager
    cd link-manager
    python3 -m venv venv
    source venv/bin/activate
    pip install flask
    sqlite3 database.db < schema.sql
    flask run

Then open the application in your browser: http://127.0.0.1:5000

In the application, you can register a new username, log in, add links, view, edit or delete links, and search links by title.
