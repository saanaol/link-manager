import db


def get_all_categories():
    sql = "SELECT id, name FROM categories ORDER BY name"
    return db.query(sql)


def get_link_categories(link_id):
    sql = """
        SELECT c.name
        FROM categories c
        JOIN link_categories lc ON c.id = lc.category_id
        WHERE lc.link_id = ?
        ORDER BY c.name
    """
    return db.query(sql, [link_id])


def category_exists(category_id):
    sql = "SELECT id FROM categories WHERE id = ?"
    result = db.query(sql, [category_id])
    return bool(result)


def add_link_category(link_id, category_id):
    sql = """
        INSERT INTO link_categories (link_id, category_id)
        VALUES (?, ?)
    """
    db.execute(sql, [link_id, category_id])


def remove_link_categories(link_id):
    sql = "DELETE FROM link_categories WHERE link_id = ?"
    db.execute(sql, [link_id])
