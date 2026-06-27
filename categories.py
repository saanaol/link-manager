import db


def get_all_categories():
    sql = "SELECT id, name FROM categories ORDER BY name"
    return db.query(sql)


def category_exists(category_id):
    sql = "SELECT id FROM categories WHERE id = ?"
    result = db.query(sql, [category_id])
    return bool(result)
