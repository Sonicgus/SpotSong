CREATE or REPLACE FUNCTION update_top10() RETURNS TRIGGER AS $$

DECLARE
	top10_playlist_id BIGINT;
	playlist_count BIGINT;
	
BEGIN
	SELECT COUNT(*) INTO playlist_count
	FROM playlist
	WHERE is_private is NULL;
	
	IF playlist_count = 0 THEN
		INSERT INTO playlist (name, is_private, consumer_person_user_id) VALUES ('Top 10', NULL, user_id) RETURNING id into top10_playlist_id;
	ELSE
		SELECT id INTO top10_playlist_id
		FROM playlist
		WHERE is_private is NULL;
	END IF;
	
	DELETE FROM playlist_song
	WHERE playlist_id = top10_playlist_id;
	
	INSERT INTO playlist_song (playlist_id, song_ismn)
	SELECT top10_playlist_id, song_ismn
	FROM (
		SELECT view.song_ismn, COUNT(*) AS num_views
        FROM view
		WHERE view.date_view >= now() - INTERVAL '30 days'
       	GROUP BY view.song_ismn
        ORDER BY num_views DESC LIMIT 10
    ) AS top_songs;
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_top10
AFTER INSERT OR UPDATE on view
FOR EACH ROW
EXECUTE FUNCTION update_top10();
