CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE UNIQUE INDEX idx_users_username_lower ON users(lower(username));

CREATE TABLE links (
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  url TEXT NOT NULL,
  notes TEXT,
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
    
CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    link_id INTEGER REFERENCES links ON DELETE CASCADE,
    user_id INTEGER REFERENCES users,
    content TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
    
