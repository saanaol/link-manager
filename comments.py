"""Database queries for comments."""

import db


def count_link_comments(link_id):
    sql = "SELECT COUNT(*) AS count FROM comments WHERE link_id = ?"
    return db.query(sql, [link_id])[0]["count"]


def get_link_comments(link_id, page, page_size):
    sql = """
        SELECT c.content, c.created_at, u.id user_id, u.username
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.link_id = ?
        ORDER BY c.id DESC
        LIMIT ? OFFSET ?
    """
    limit = page_size
    offset = page_size * (page - 1)

    return db.query(sql, [link_id, limit, offset])


def add_comment(link_id, user_id, content):
    sql = """
        INSERT INTO comments (link_id, user_id, content)
        VALUES (?, ?, ?)
    """
    db.execute(sql, [link_id, user_id, content])


def remove_link_comments(link_id):
    sql = "DELETE FROM comments WHERE link_id = ?"
    db.execute(sql, [link_id])


def count_user_comments(user_id):
    sql = "SELECT COUNT(*) AS count FROM comments WHERE user_id = ?"
    return db.query(sql, [user_id])[0]["count"]
