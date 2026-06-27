"""Database queries for users."""

import sqlite3
import db


def get_user(user_id):
    sql = "SELECT id, username FROM users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0] if result else None


def get_user_by_username(username):
    sql = """
        SELECT id, username, password_hash
        FROM users
        WHERE lower(username) = lower(?)
    """
    result = db.query(sql, [username])
    return result[0] if result else None


def username_exists(username):
    sql = "SELECT id FROM users WHERE lower(username) = lower(?)"
    result = db.query(sql, [username])
    return bool(result)


def add_user(username, password_hash):
    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return False

    return True


def get_session_user(user_id, username):
    sql = """SELECT id, username
             FROM users
             WHERE id = ? AND username = ?"""
    result = db.query(sql, [user_id, username])
    return result[0] if result else None
