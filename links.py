"""Database queries for links."""

import db


def count_links():
    sql = "SELECT COUNT(*) AS count FROM links"
    return db.query(sql)[0]["count"]


def get_links(page, page_size):
    sql = """
        SELECT l.id, l.title, l.url, l.user_id, l.category_id,
               u.username, c.name category_name
        FROM links l
        JOIN users u ON l.user_id = u.id
        LEFT JOIN categories c ON l.category_id = c.id
        ORDER BY l.id DESC
        LIMIT ? OFFSET ?
    """
    limit = page_size
    offset = page_size * (page - 1)

    return db.query(sql, [limit, offset])


def get_all_links():
    sql = """
        SELECT l.id, l.title, l.url, l.user_id, l.category_id,
               u.username, c.name category_name
        FROM links l
        JOIN users u ON l.user_id = u.id
        LEFT JOIN categories c ON l.category_id = c.id
        ORDER BY l.id DESC
    """
    return db.query(sql)


def get_link(link_id):
    sql = """
        SELECT l.id, l.title, l.url, l.notes, l.user_id,
               l.category_id, l.created_at, l.updated_at,
               u.username, c.name category_name
        FROM links l
        JOIN users u ON l.user_id = u.id
        LEFT JOIN categories c ON l.category_id = c.id
        WHERE l.id = ?
    """
    result = db.query(sql, [link_id])
    return result[0] if result else None


def add_link(title, url, notes, user_id, category_id):
    sql = """INSERT INTO links (title, url, notes, user_id, category_id)
             VALUES (?, ?, ?, ?, ?)"""
    db.execute(sql, [title, url, notes, user_id, category_id])
    return db.last_insert_id()


def update_link(link_id, title, url, notes, category_id):
    sql = """UPDATE links
             SET title = ?, url = ?, notes = ?, category_id = ?,
                 updated_at = datetime('now')
             WHERE id = ?"""
    db.execute(sql, [title, url, notes, category_id, link_id])


def remove_link(link_id):
    sql = "DELETE FROM links WHERE id = ?"
    db.execute(sql, [link_id])


def count_search_links(query):
    sql = """
        SELECT COUNT(*) AS count
        FROM links l
        LEFT JOIN categories c ON l.category_id = c.id
        WHERE l.title LIKE ? OR
              l.url LIKE ? OR
              l.notes LIKE ? OR
              c.name LIKE ?
    """
    pattern = "%" + query + "%"

    return db.query(sql, [
        pattern,
        pattern,
        pattern,
        pattern
    ])[0]["count"]


def search_links(query, page, page_size):
    sql = """
        SELECT l.id, l.title, l.url, l.user_id, l.category_id,
               u.username, c.name category_name
        FROM links l
        JOIN users u ON l.user_id = u.id
        LEFT JOIN categories c ON l.category_id = c.id
        WHERE l.title LIKE ? OR
              l.url LIKE ? OR
              l.notes LIKE ? OR
              c.name LIKE ?
        ORDER BY l.id DESC
        LIMIT ? OFFSET ?
    """
    pattern = "%" + query + "%"
    limit = page_size
    offset = page_size * (page - 1)

    return db.query(sql, [
        pattern,
        pattern,
        pattern,
        pattern,
        limit,
        offset
    ])


def get_user_links(user_id, page, page_size):
    sql = """
        SELECT l.id, l.title, l.url, l.category_id,
               c.name category_name
        FROM links l
        LEFT JOIN categories c ON l.category_id = c.id
        WHERE l.user_id = ?
        ORDER BY l.id DESC
        LIMIT ? OFFSET ?
    """
    limit = page_size
    offset = page_size * (page - 1)

    return db.query(sql, [user_id, limit, offset])


def count_user_links(user_id):
    sql = "SELECT COUNT(*) AS count FROM links WHERE user_id = ?"
    return db.query(sql, [user_id])[0]["count"]
