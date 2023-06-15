CREATE TABLE users (
	id	 BIGSERIAL,
	username VARCHAR(30) NOT NULL,
	password VARCHAR(512) NOT NULL,
	email	 VARCHAR(255) NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE consumer (
	person_users_id BIGINT,
	PRIMARY KEY(person_users_id)
);

CREATE TABLE artist (
	artistic_name		 VARCHAR(512) NOT NULL,
	administrator_users_id BIGINT NOT NULL,
	label_id		 BIGINT NOT NULL,
	person_users_id	 BIGINT,
	PRIMARY KEY(person_users_id)
);

CREATE TABLE administrator (
	users_id BIGINT,
	PRIMARY KEY(users_id)
);

CREATE TABLE playlist (
	id			 BIGSERIAL,
	name			 VARCHAR(512) NOT NULL,
	is_private		 BOOL,
	consumer_person_users_id BIGINT NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE comment (
	id			 BIGSERIAL,
	text			 VARCHAR(512),
	song_ismn		 BIGINT NOT NULL,
	consumer_person_users_id BIGINT NOT NULL,
	comment_id		 BIGINT,
	PRIMARY KEY(id)
);

CREATE TABLE label (
	id	 BIGSERIAL,
	name VARCHAR(512) NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE song (
	ismn			 BIGSERIAL,
	title			 VARCHAR(512) NOT NULL,
	release_date		 TIMESTAMP NOT NULL,
	duration		 VARCHAR(512) NOT NULL,
	genre			 VARCHAR(512) NOT NULL,
	artist_person_users_id BIGINT NOT NULL,
	label_id		 BIGINT NOT NULL,
	PRIMARY KEY(ismn)
);

CREATE TABLE person (
	address	 VARCHAR(512) NOT NULL,
	contact	 VARCHAR(512) NOT NULL,
	users_id BIGINT,
	PRIMARY KEY(users_id)
);

CREATE TABLE album (
	id			 BIGSERIAL,
	title			 VARCHAR(512) NOT NULL,
	release_date		 TIMESTAMP NOT NULL,
	artist_person_users_id BIGINT NOT NULL,
	label_id		 BIGINT NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE card (
	id			 BIGSERIAL,
	code			 VARCHAR(16) NOT NULL,
	expire		 TIMESTAMP NOT NULL,
	amount		 INTEGER NOT NULL,
	type			 INTEGER NOT NULL,
	administrator_users_id BIGINT NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE view (
	id			 BIGSERIAL,
	date_view		 TIMESTAMP NOT NULL,
	song_ismn		 BIGINT,
	consumer_person_users_id BIGINT,
	PRIMARY KEY(id,song_ismn,consumer_person_users_id)
);

CREATE TABLE history_card (
	cost			 INTEGER,
	purchase_subscription_id BIGINT,
	card_id			 BIGINT,
	PRIMARY KEY(purchase_subscription_id,card_id)
);

CREATE TABLE purchase_subscription (
	id			 BIGSERIAL,
	purchase_date		 TIMESTAMP,
	subscription_id		 BIGSERIAL NOT NULL,
	subscription_plan	 INTEGER NOT NULL,
	subscription_init_date	 TIMESTAMP NOT NULL,
	subscription_end_date	 TIMESTAMP NOT NULL,
	consumer_person_users_id BIGINT NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE playlist_song (
	playlist_id BIGINT,
	song_ismn	 BIGINT,
	PRIMARY KEY(playlist_id,song_ismn)
);

CREATE TABLE song_album (
	song_ismn BIGINT,
	album_id	 BIGINT,
	PRIMARY KEY(song_ismn,album_id)
);

CREATE TABLE artist_song (
	artist_person_users_id BIGINT,
	song_ismn		 BIGINT,
	PRIMARY KEY(artist_person_users_id,song_ismn)
);

ALTER TABLE users ADD UNIQUE (username);
ALTER TABLE consumer ADD CONSTRAINT consumer_fk1 FOREIGN KEY (person_users_id) REFERENCES person(users_id);
ALTER TABLE artist ADD UNIQUE (artistic_name);
ALTER TABLE artist ADD CONSTRAINT artist_fk1 FOREIGN KEY (administrator_users_id) REFERENCES administrator(users_id);
ALTER TABLE artist ADD CONSTRAINT artist_fk2 FOREIGN KEY (label_id) REFERENCES label(id);
ALTER TABLE artist ADD CONSTRAINT artist_fk3 FOREIGN KEY (person_users_id) REFERENCES person(users_id);
ALTER TABLE administrator ADD CONSTRAINT administrator_fk1 FOREIGN KEY (users_id) REFERENCES users(id);
ALTER TABLE playlist ADD CONSTRAINT playlist_fk1 FOREIGN KEY (consumer_person_users_id) REFERENCES consumer(person_users_id);
ALTER TABLE comment ADD CONSTRAINT comment_fk1 FOREIGN KEY (song_ismn) REFERENCES song(ismn);
ALTER TABLE comment ADD CONSTRAINT comment_fk2 FOREIGN KEY (consumer_person_users_id) REFERENCES consumer(person_users_id);
ALTER TABLE comment ADD CONSTRAINT comment_fk3 FOREIGN KEY (comment_id) REFERENCES comment(id);
ALTER TABLE label ADD UNIQUE (name);
ALTER TABLE song ADD CONSTRAINT song_fk1 FOREIGN KEY (artist_person_users_id) REFERENCES artist(person_users_id);
ALTER TABLE song ADD CONSTRAINT song_fk2 FOREIGN KEY (label_id) REFERENCES label(id);
ALTER TABLE person ADD CONSTRAINT person_fk1 FOREIGN KEY (users_id) REFERENCES users(id);
ALTER TABLE album ADD CONSTRAINT album_fk1 FOREIGN KEY (artist_person_users_id) REFERENCES artist(person_users_id);
ALTER TABLE album ADD CONSTRAINT album_fk2 FOREIGN KEY (label_id) REFERENCES label(id);
ALTER TABLE card ADD UNIQUE (code);
ALTER TABLE card ADD CONSTRAINT card_fk1 FOREIGN KEY (administrator_users_id) REFERENCES administrator(users_id);
ALTER TABLE view ADD CONSTRAINT view_fk1 FOREIGN KEY (song_ismn) REFERENCES song(ismn);
ALTER TABLE view ADD CONSTRAINT view_fk2 FOREIGN KEY (consumer_person_users_id) REFERENCES consumer(person_users_id);
ALTER TABLE history_card ADD CONSTRAINT history_card_fk1 FOREIGN KEY (purchase_subscription_id) REFERENCES purchase_subscription(id);
ALTER TABLE history_card ADD CONSTRAINT history_card_fk2 FOREIGN KEY (card_id) REFERENCES card(id);
ALTER TABLE purchase_subscription ADD UNIQUE (subscription_id);
ALTER TABLE purchase_subscription ADD CONSTRAINT purchase_subscription_fk1 FOREIGN KEY (consumer_person_users_id) REFERENCES consumer(person_users_id);
ALTER TABLE playlist_song ADD CONSTRAINT playlist_song_fk1 FOREIGN KEY (playlist_id) REFERENCES playlist(id);
ALTER TABLE playlist_song ADD CONSTRAINT playlist_song_fk2 FOREIGN KEY (song_ismn) REFERENCES song(ismn);
ALTER TABLE song_album ADD CONSTRAINT song_album_fk1 FOREIGN KEY (song_ismn) REFERENCES song(ismn);
ALTER TABLE song_album ADD CONSTRAINT song_album_fk2 FOREIGN KEY (album_id) REFERENCES album(id);
ALTER TABLE artist_song ADD CONSTRAINT artist_song_fk1 FOREIGN KEY (artist_person_users_id) REFERENCES artist(person_users_id);
ALTER TABLE artist_song ADD CONSTRAINT artist_song_fk2 FOREIGN KEY (song_ismn) REFERENCES song(ismn);

