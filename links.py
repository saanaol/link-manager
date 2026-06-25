import db


def count_links():
    sql = "SELECT COUNT(*) AS count FROM links"
    return db.query(sql)[0]["count"]


def get_links(page, page_size):
    sql = """
        SELECT l.id, l.title, l.url, l.user_id, u.username
        FROM links l
        JOIN users u ON l.user_id = u.id
        ORDER BY l.id DESC
        LIMIT ? OFFSET ?
    """
    limit = page_size
    offset = page_size * (page - 1)

    return db.query(sql, [limit, offset])


def get_all_links():
    sql = """
        SELECT l.id, l.title, l.url, l.user_id, u.username
        FROM links l
        JOIN users u ON l.user_id = u.id
        ORDER BY l.id DESC
    """
    return db.query(sql)


def get_link(link_id):
    sql = """
        SELECT l.id, l.title, l.url, l.notes, l.user_id,
               l.created_at, l.updated_at, u.username
        FROM links l
        JOIN users u ON l.user_id = u.id
        WHERE l.id = ?
    """
    result = db.query(sql, [link_id])
    return result[0] if result else None


def add_link(title, url, notes, user_id):
    sql = """
        INSERT INTO links (title, url, notes, user_id, created_at)
        VALUES (?, ?, ?, ?, datetime('now'))
    """
    db.execute(sql, [title, url, notes, user_id])
    return db.last_insert_id()


def update_link(link_id, title, url, notes):
    sql = """
        UPDATE links
        SET title = ?, url = ?, notes = ?, updated_at = datetime('now')
        WHERE id = ?
    """
    db.execute(sql, [title, url, notes, link_id])


def remove_link(link_id):
    sql = "DELETE FROM links WHERE id = ?"
    db.execute(sql, [link_id])


def search_links(query):
    sql = """
        SELECT l.id, l.title, l.url, l.user_id, u.username
        FROM links l
        JOIN users u ON l.user_id = u.id
        WHERE l.title LIKE ? OR l.url LIKE ? OR l.notes LIKE ?
        ORDER BY l.id DESC
    """
    pattern = "%" + query + "%"
    return db.query(sql, [pattern, pattern, pattern])


def get_user_links(user_id):
    sql = """
        SELECT id, title, url
        FROM links
        WHERE user_id = ?
        ORDER BY id DESC
    """
    return db.query(sql, [user_id])


def count_user_links(user_id):
    sql = "SELECT COUNT(*) AS count FROM links WHERE user_id = ?"
    return db.query(sql, [user_id])[0]["count"]
