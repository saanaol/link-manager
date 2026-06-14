CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE links (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    user_id INTEGER REFERENCES users
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE link_categories (
    link_id INTEGER REFERENCES links ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories ON DELETE CASCADE,
    PRIMARY KEY (link_id, category_id)
);

INSERT INTO categories (name) VALUES
    ('Programming'),
    ('School'),
    ('Work'),
    ('Article'),
    ('Other');
