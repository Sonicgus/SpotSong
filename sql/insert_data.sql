INSERT INTO label (name) VALUES ('soni');

INSERT INTO users (username, password, email) VALUES ('admin', 'admin', 'admin@example.com');
INSERT INTO administrator (users_id) SELECT id FROM users WHERE username = 'admin';

INSERT INTO users (username, password, email) VALUES ('artista', 'artista', 'artista@example.com');
INSERT INTO person (address, number, users_id) SELECT 'rua fulano de tal', '969 999 999', id FROM users WHERE username = 'artista';
INSERT INTO artist (administrator_users_id, artistic_name, label_id, person_users_id) SELECT 1,'artisteiro', l.id, u.id FROM label l, users u WHERE l.name = 'soni' AND u.username = 'artista';

INSERT INTO users (username, password, email) VALUES ('blueday', 'blueday', 'blueday@example.com');
INSERT INTO person (address, number, users_id) SELECT 'rua fulano de tal', '969 999 999', id FROM users WHERE username = 'blueday';
INSERT INTO artist (administrator_users_id, artistic_name, label_id, person_users_id) SELECT 1, 'bluedays', l.id, u.id FROM label l, users u WHERE l.name = 'soni' AND u.username = 'blueday';

INSERT INTO song (title, release_date, duration, genre, artist_person_users_id, label_id) VALUES ('opa ganda style','2023-06-11 10:30:00','2023-06-11 10:30:00','rap',2,1);

INSERT INTO artist_song (artist_person_users_id, song_ismn) VALUES (2, 1);

INSERT INTO album (title, release_date, artist_person_users_id, label_id) VALUES ('classicos dos anos 90','2023-06-11 10:30:00',2,1);

INSERT INTO song_album (song_ismn, album_id) VALUES (1,1);

INSERT INTO users (username, password, email) VALUES ('quim', 'quim', 'quim@example.com');
INSERT INTO person (address, number, users_id) SELECT 'rua fulano de tal', '969 999 999', id FROM users WHERE username = 'quim';
INSERT INTO consumer (person_users_id) SELECT id FROM users WHERE username = 'quim';