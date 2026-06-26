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


def get_categories_for_links(link_ids):
    if not link_ids:
        return {}

    placeholders = ",".join(["?"] * len(link_ids))

    sql = f"""
        SELECT lc.link_id, c.name
        FROM link_categories lc
        JOIN categories c ON lc.category_id = c.id
        WHERE lc.link_id IN ({placeholders})
        ORDER BY c.name
    """

    rows = db.query(sql, link_ids)

    link_categories = {}
    for link_id in link_ids:
        link_categories[link_id] = []

    for row in rows:
        link_categories[row["link_id"]].append(row)

    return link_categories


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


def get_link_category_ids(link_id):
    sql = "SELECT category_id FROM link_categories WHERE link_id = ?"
    result = db.query(sql, [link_id])
    return [str(row["category_id"]) for row in result]
