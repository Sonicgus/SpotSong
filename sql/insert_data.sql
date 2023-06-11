INSERT INTO label (name) VALUES ('soni');

INSERT INTO users (username, password, email) VALUES ('admin', 'admin', 'admin@example.com');
INSERT INTO administrator (users_id) SELECT id FROM users WHERE username = 'admin';

INSERT INTO users (username, password, email) VALUES ('artista', 'artista', 'artista@example.com');
INSERT INTO person (address, number, users_id) SELECT 'rua fulano de tal', '969 999 999', id FROM users WHERE username = 'artista';
INSERT INTO artist (artistic_name, label_id, person_users_id) SELECT 'artisteiro', l.id, u.id FROM label l, users u WHERE l.name = 'soni' AND u.username = 'artista';
