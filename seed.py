import random
import sqlite3

from werkzeug.security import generate_password_hash


DATABASE = "database.db"

USER_COUNT = 1000
LINK_COUNT = 10**6
COMMENT_COUNT = 10**7

HEAVY_USER_ID = 1
HEAVY_USER_LINK_COUNT = 5000

HEAVY_LINK_ID = 1
HEAVY_LINK_COMMENT_COUNT = 10000

PASSWORD = "password"
BATCH_SIZE = 5000


db = sqlite3.connect(DATABASE)
db.execute("PRAGMA foreign_keys = ON")


def clear_data():
    db.execute("DELETE FROM comments")
    db.execute("DELETE FROM links")
    db.execute("DELETE FROM users")


def get_category_ids():
    sql = "SELECT id FROM categories"
    rows = db.execute(sql).fetchall()
    return [row[0] for row in rows]


def insert_users():
    password_hash = generate_password_hash(PASSWORD)

    sql = """
        INSERT INTO users (id, username, password_hash)
        VALUES (?, ?, ?)
    """

    batch = []

    for i in range(1, USER_COUNT + 1):
        username = "user" + str(i)
        batch.append((i, username, password_hash))

        if len(batch) == BATCH_SIZE:
            db.executemany(sql, batch)
            batch = []

    if batch:
        db.executemany(sql, batch)


def get_link_user_id(link_id):
    if link_id <= HEAVY_USER_LINK_COUNT:
        return HEAVY_USER_ID

    return random.randint(2, USER_COUNT)


def insert_links(category_ids):
    sql = """
        INSERT INTO links (
            id, title, url, notes, user_id, category_id, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
    """

    batch = []

    for i in range(1, LINK_COUNT + 1):
        title = "Test link " + str(i)
        url = "https://example.com/link-" + str(i)
        notes = "This is a test note for link " + str(i)
        user_id = get_link_user_id(i)
        category_id = random.choice(category_ids)

        batch.append((i, title, url, notes, user_id, category_id))

        if len(batch) == BATCH_SIZE:
            db.executemany(sql, batch)
            batch = []

    if batch:
        db.executemany(sql, batch)


def get_comment_link_id(comment_number):
    if comment_number <= HEAVY_LINK_COMMENT_COUNT:
        return HEAVY_LINK_ID

    return random.randint(2, LINK_COUNT)


def insert_comments():
    sql = """
        INSERT INTO comments (link_id, user_id, content, created_at)
        VALUES (?, ?, ?, datetime('now'))
    """

    batch = []

    for i in range(1, COMMENT_COUNT + 1):
        link_id = get_comment_link_id(i)
        user_id = random.randint(1, USER_COUNT)
        content = "Test comment " + str(i)

        batch.append((link_id, user_id, content))

        if len(batch) == BATCH_SIZE:
            db.executemany(sql, batch)
            batch = []

    if batch:
        db.executemany(sql, batch)


def main():
    random.seed(1)

    category_ids = get_category_ids()

    if not category_ids:
        print("No categories found.")
        print("Run this first: sqlite3 database.db < init.sql")
        db.close()
        return

    clear_data()
    insert_users()
    insert_links(category_ids)
    insert_comments()

    db.commit()
    db.close()

    print("Seed data created.")
    print("Users:", USER_COUNT)
    print("Links:", LINK_COUNT)
    print("Comments:", COMMENT_COUNT)
    print("Heavy user:", "user" + str(HEAVY_USER_ID))
    print("Heavy user links:", HEAVY_USER_LINK_COUNT)
    print("Heavy link:", "/link/" + str(HEAVY_LINK_ID))
    print("Heavy link comments:", HEAVY_LINK_COMMENT_COUNT)
    print("Password for all test users:", PASSWORD)


main()
