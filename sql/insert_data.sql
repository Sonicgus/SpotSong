INSERT INTO users (username, password, email) VALUES ('admin', 'admin', 'admin@example.com');
INSERT INTO administrator (users_id) SELECT id FROM users WHERE username = 'admin';
