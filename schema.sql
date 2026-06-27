CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE UNIQUE INDEX index_users_username_lower ON users(lower(username));

CREATE TABLE links (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    notes TEXT,
    user_id INTEGER REFERENCES users,
    category_id INTEGER REFERENCES categories,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    link_id INTEGER REFERENCES links ON DELETE CASCADE,
    user_id INTEGER REFERENCES users,
    content TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX index_links_user_id ON links(user_id);

CREATE INDEX index_comments_link_id ON comments(link_id);
CREATE INDEX index_comments_user_id ON comments(user_id);

CREATE INDEX index_links_category_id ON links(category_id);
