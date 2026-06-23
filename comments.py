import db


def get_link_comments(link_id):
    sql = """
        SELECT c.content, c.created_at, u.username
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.link_id = ?
        ORDER BY c.id DESC
    """
    return db.query(sql, [link_id])


def add_comment(link_id, user_id, content):
    sql = """
        INSERT INTO comments (link_id, user_id, content)
        VALUES (?, ?, ?)
    """
    db.execute(sql, [link_id, user_id, content])


def remove_link_comments(link_id):
    sql = "DELETE FROM comments WHERE link_id = ?"
    db.execute(sql, [link_id])
