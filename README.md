# Link Manager

A web application for saving, organising and searching useful links.

The application contains the following features:

* Users can create an account and log in to the application.
* Users can add, edit and delete links.
* Users can view all links added to the application.
* Users can search for links by title.
* Users can assign one or more categories to a link.
* Users can add additional information to links added by other users.
* The application uses CSRF protection.

# Instructions for testing

Run the following commands:

```
git clone https://github.com/saanaol/link-manager
cd link-manager
python3 -m venv venv
source venv/bin/activate
pip install flask
sqlite3 database.db < schema.sql
flask run
```

Then open the application in your browser.

In the application, you can:

1. Register a new user, log in and log out.
2. Add a new link and select one or more categories for it.
3. Check that the added link and its categories.
4. Search for a link by title and return to the full link list.
5. Open the user profile page by clicking the username shown next to a link.
6. Check the user profile page including the user's statistics and links added by that user.
9. Add additional information to the first user's link.
10. Check that the additional information below the related link.
11. Edit and delete your own links.

