# =============================================
# ============== Bases de Dados ===============
# ============== LEI  2022/2023 ===============
# =============================================
# === Department of Informatics Engineering ===
# =========== University of Coimbra ===========
# =============================================
#
# Authors:
#   Diogo Tavares <uc2020236566@student.uc.pt>
#   Gustavo Lima <uc2020217743@student.uc.pt>
#   Nuno Rodrigues <uc2020246759@student.uc.pt>
#   BD 2022 Team - https://dei.uc.pt/lei/
#   University of Coimbra

import bcrypt
import flask
import logging
import psycopg
import jwt
import datetime
import os
import random
from dotenv import load_dotenv

load_dotenv()

# get env vars
secret_key = os.getenv("SECRET_KEY")
userdb = os.getenv("USER")
passdb = os.getenv("PASSWORD")
hostdb = os.getenv("HOSTDB")
portdb = os.getenv("PORTDB")
namedb = os.getenv("NAMEDB")

# set up logging
logging.basicConfig(filename="log_file.log")
logger = logging.getLogger("logger")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter("%(asctime)s [%(levelname)s]:  %(message)s", "%H:%M:%S")
ch.setFormatter(formatter)
logger.addHandler(ch)

app = flask.Flask(__name__)

StatusCodes = {"success": 200, "api_error": 400, "internal_error": 500}


##########################################################
# DATABASE ACCESS
##########################################################


def db_connection():
    db = psycopg.connect(
        user=userdb,
        password=passdb,
        host=hostdb,
        port=portdb,
        dbname=namedb,
    )

    return db


##########################################################
# ENDPOINTS
##########################################################


@app.route("/dbproj")
def landing_page():
    return """
    <title>SpotSong</title>
    
    <h1>Welcome to SpotSong!</h1>
    
    <br>Check the sources for instructions on how to use the endpoints!</br>

    <br>BD 2022 Team</br>
    """


#
# POST
#
# Add a new user in a JSON payload
#
# To use it, you need to use postman or curl:
#
# curl -X POST http://localhost:8080/dbproj/user -H 'Content-Type: application/json' -d '{'username': 'username',
# 'email': email, 'password': 'password'}'
#
@app.route("/dbproj/user", methods=["POST"])
def add_user():
    logger.info("POST /dbproj/user")
    payload = flask.request.get_json()

    logger.debug(f"POST /dbproj/user - payload: {payload}")

    # validate every argument:
    if "username" not in payload:
        response = {
            "status": StatusCodes["api_error"],
            "results": "username value not in payload",
        }
        return flask.jsonify(response)

    if "email" not in payload:
        response = {
            "status": StatusCodes["api_error"],
            "results": "email value not in payload",
        }
        return flask.jsonify(response)

    if "password" not in payload:
        response = {
            "status": StatusCodes["api_error"],
            "results": "password value not in payload",
        }
        return flask.jsonify(response)

    hashed_password = bcrypt.hashpw(
        payload["password"].encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    # parameterized queries, good for security and performance
    statement = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s) RETURNING id;"
    values = (
        payload["username"],
        payload["email"],
        hashed_password,
    )

    conn = db_connection()
    cur = conn.cursor()

    try:
        # begin the transaction
        cur.execute("BEGIN TRANSACTION;")

        cur.execute(statement, values)
        user_id = cur.fetchone()[0]

        # commit the transaction
        cur.execute("COMMIT;")
        response = {
            "status": StatusCodes["success"],
            "results": f"Inserted user {user_id}",
        }

    except (Exception, psycopg.DatabaseError) as error:
        logger.error(f"POST /dbproj/user - error: {error}")
        response = {"status": StatusCodes["internal_error"], "errors": str(error)}

        # an error occurred, rollback
        cur.execute("ROLLBACK;")

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


#
# PUT
#
# Authenticate a User based on a JSON payload
#
# To use it, you need to use postman or curl:
#
# curl -X PUT http://localhost:8080/dbproj/user -H 'Content-Type: application/json' -d '{'username': 'username',
# 'password': 'password'}'
#


@app.route("/dbproj/user", methods=["PUT"])
def authenticate_user():
    logger.info("PUT /dbproj/user")
    payload = flask.request.get_json()

    logger.debug(f"PUT /dbproj/user - payload: {payload}")

    # validate every argument:
    if "username" not in payload:
        response = {
            "status": StatusCodes["api_error"],
            "results": "username is required to login",
        }
        return flask.jsonify(response)

    if "password" not in payload:
        response = {
            "status": StatusCodes["api_error"],
            "results": "password is required to login",
        }
        return flask.jsonify(response)

    # parameterized queries, good for security and performance
    statement = "SELECT id, password FROM users WHERE username = %s;"
    values = (payload["username"],)

    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute(statement, values)

        row = cur.fetchone()

        if bcrypt.checkpw(payload["password"].encode("utf-8"), row[1].encode("utf-8")):
            response = {
                "status": StatusCodes["success"],
                "results": jwt.encode(
                    {
                        "user_id": row[0],
                        "exp": (
                            datetime.datetime.now() + datetime.timedelta(minutes=5)
                        ).timestamp(),
                    },
                    secret_key,
                    algorithm="HS256",
                ),
            }
        else:
            response = {
                "status": StatusCodes["api_error"],
                "errors": "Passsword incorreta",
            }

    except (Exception, psycopg.DatabaseError) as error:
        logger.error(error)
        response = {"status": StatusCodes["internal_error"], "errors": str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


#
# POST
#
# Add a new song in a JSON payload
#
# To use it, you need to use postman or curl:
#
# curl -X POST http://localhost:8080/dbproj/song -H 'Content-Type: application/json' -d '{“song_name”: “name”, “release_date”: “date”, “publisher”: publisher_id, “other_artists”: [artist_id1, artist_id2, (…)]}, (…)}
#
@app.route("/dbproj/song", methods=["POST"])
def add_song():
    logger.info("POST /dbproj/song")
    payload = flask.request.get_json()

    logger.debug(f"POST /dbproj/song - payload: {payload}")

    # validate every argument:
    if "token" not in payload:
        response = {
            "status": StatusCodes["api_error"],
            "results": "token value not in payload",
        }
        return flask.jsonify(response)

    if "song_name" not in payload:
        response = {
            "status": StatusCodes["api_error"],
            "results": "song_name value not in payload",
        }
        return flask.jsonify(response)

    if "duration" not in payload:
        response = {
            "status": StatusCodes["api_error"],
            "results": "duration value not in payload",
        }
        return flask.jsonify(response)

    if "genre" not in payload:
        response = {
            "status": StatusCodes["api_error"],
            "results": "genre value not in payload",
        }
        return flask.jsonify(response)

    if "release_date" not in payload:
        response = {
            "status": StatusCodes["api_error"],
            "results": "release_date value not in payload",
        }
        return flask.jsonify(response)

    if "publisher_id" not in payload:
        response = {
            "status": StatusCodes["api_error"],
            "results": "publisher_id value not in payload",
        }
        return flask.jsonify(response)

    try:
        credentials = jwt.decode(payload["token"], secret_key, algorithms="HS256")

    except jwt.exceptions.ExpiredSignatureError:
        response = {
            "status": StatusCodes["api_error"],
            "results": "token invalido. tente autenticar novamente",
        }
        return flask.jsonify(response)

    if "user_id" not in credentials:
        response = {"status": StatusCodes["api_error"], "results": "Invalid token"}
        return flask.jsonify(response)

    conn = db_connection()
    cur = conn.cursor()

    # parameterized queries, good for security and performance
    statement = "INSERT INTO song (title, release_date, duration, genre, artist_person_users_id, label_id) VALUES (%s, %s, %s, %s, %s, %s) RETURNING ismn;"
    values = (
        payload["song_name"],
        payload["release_date"],
        payload["duration"],
        payload["genre"],
        credentials["user_id"],
        payload["publisher_id"],
    )

    try:
        # begin the transaction
        cur.execute("BEGIN TRANSACTION;")

        cur.execute(statement, values)

        song_id = cur.fetchone()[0]

        statement = "INSERT INTO artist_song (artist_person_users_id, song_ismn) VALUES (%s, %s)"
        values = (
            credentials["user_id"],
            song_id,
        )

        cur.execute(statement, values)

        if "other_artists" in payload:
            for artist_id in payload["other_artists"]:
                statement = "INSERT INTO artist_song (artist_person_users_id, song_ismn) VALUES (%s, %s)"
                values = (
                    artist_id,
                    song_id,
                )

                cur.execute(statement, values)

        # commit the transaction
        cur.execute("COMMIT;")

        response = {
            "status": StatusCodes["success"],
            "results": f"Inserted song {song_id}",
        }

    except (Exception, psycopg.DatabaseError) as error:
        logger.error(f"POST /dbproj/song - error: {error}")
        response = {"status": StatusCodes["internal_error"], "errors": str(error)}

        # an error occurred, rollback
        cur.execute("ROLLBACK;")

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


#
# GET
#
# Search a song in a JSON payload
#
# To use it, you need to use postman or curl:
#
# curl -X GET http://localhost:8080/dbproj/song/{keyword} -H 'Content-Type: application/json' -d
#
@app.route("/dbproj/song/<keyword>", methods=["GET"])
def search_song(keyword):
    logger.info("GET /dbproj/song/{keyword}")

    logger.debug("GET /dbproj/song/{keyword}")

    conn = db_connection()
    cur = conn.cursor()

    # parameterized queries, good for security and performance
    statement = f"SELECT s.ismn AS song_id, s.title AS song_title, a.artistic_name AS artist_name, al.id AS album_id FROM song s INNER JOIN artist_song sa ON s.ismn = sa.song_ismn INNER JOIN artist a ON sa.artist_person_users_id = a.person_users_id LEFT JOIN song_album als ON s.ismn = als.song_ismn LEFT JOIN album al ON als.album_id = al.id WHERE s.title LIKE '%{keyword}%'; "

    try:
        cur.execute(statement)

        all = cur.fetchall()

        dicisongs = {}
        albuns = []

        for element in all:
            song_id = element[0]
            if song_id in dicisongs:
                dicisongs[song_id]["artists"].append(element[2])
            else:
                dicisongs[song_id] = {"song_title": element[1], "artists": [element[2]]}

            album = element[3]

            if album is not None:
                if album not in albuns:
                    albuns.append(album)

        results = []

        for song_id, song_info in dicisongs.items():
            song = {"title": song_info["song_title"], "artists": song_info["artists"]}
            results.append(song)

        results.append({"albuns": albuns})

        response = {"status": StatusCodes["success"], "results": results}

    except (Exception, psycopg.DatabaseError) as error:
        logger.error(f"GET /dbproj/song/{keyword} - error: {error}")
        response = {"status": StatusCodes["internal_error"], "errors": str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


#
# GET
#
# Search a song in a JSON payload
#
# To use it, you need to use postman or curl:
#
# curl -X GET http://localhost:8080/dbproj/artist_info/artist_id -H 'Content-Type: application/json' -d
#
@app.route("/dbproj/artist_info/<artist_id>", methods=["GET"])
def detail_artist(artist_id):
    logger.info("GET /dbproj/song/{artist_id}")

    logger.debug("GET /dbproj/song/{artist_id}")

    conn = db_connection()
    cur = conn.cursor()

    # parameterized queries, good for security and performance
    statement = "SELECT artist.artistic_name, song.ismn, album.id FROM artist JOIN artist_song ON artist_song.artist_person_users_id = artist.person_users_id JOIN song ON song.ismn = artist_song.song_ismn JOIN song_album ON song_album.song_ismn = song.ismn JOIN album ON album.id = song_album.album_id WHERE artist.person_users_id = %s;"
    values = (artist_id,)

    try:
        cur.execute(statement, values)

        all = cur.fetchall()

        if len(all) == 0:
            response = {
                "status": StatusCodes["api_error"],
                "errors": "Nothing foud with that user id",
            }
            conn.close()
            return flask.jsonify(response)

        artistic_name = all[0][0]
        songs = []
        albuns = []

        for element in all:
            song_id = element[1]
            album_id = element[2]

            if song_id not in songs:
                songs.append(song_id)

            if album_id not in albuns:
                albuns.append(album_id)

                results = []

        results.append({"name": artistic_name})

        results.append({"songs": songs})

        results.append({"albuns": albuns})

        response = {"status": StatusCodes["success"], "results": results}

    except (Exception, psycopg.DatabaseError) as error:
        logger.error(f"GET /dbproj/song/{artist_id} - error: {error}")
        response = {"status": StatusCodes["internal_error"], "errors": str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


#
# POST
#
# Add a new album in a JSON payload
#
# To use it, you need to use postman or curl:
#
# curl -X POST http://localhost:8080/dbproj/album -H 'Content-Type: application/json' -d '{“album_name”: “name”, “release_date”: “date”, “publisher”: publisher_id, “other_artists”: [artist_id1, artist_id2, (…)]}, (…)}
#
@app.route("/dbproj/album", methods=["POST"])
def add_album():
    logger.info("POST /dbproj/album")
    payload = flask.request.get_json()

    logger.debug(f"POST /dbproj/album - payload: {payload}")

    # validate every argument:
    if "token" not in payload:
        response = {
            "status": StatusCodes["api_error"],
            "results": "token value not in payload",
        }
        return flask.jsonify(response)

    if "album_name" not in payload:
        response = {
            "status": StatusCodes["api_error"],
            "results": "album_name value not in payload",
        }
        return flask.jsonify(response)

    if "release_date" not in payload:
        response = {
            "status": StatusCodes["api_error"],
            "results": "release_date value not in payload",
        }
        return flask.jsonify(response)

    if "publisher_id" not in payload:
        response = {
            "status": StatusCodes["api_error"],
            "results": "publisher_id value not in payload",
        }
        return flask.jsonify(response)

    if "songs" not in payload:
        response = {
            "status": StatusCodes["api_error"],
            "results": "songs not in payload",
        }
        return flask.jsonify(response)

    if len(payload["songs"]) == 0:
        response = {
            "status": StatusCodes["api_error"],
            "results": "there are not songs in the payload",
        }
        return flask.jsonify(response)

    try:
        credentials = jwt.decode(payload["token"], secret_key, algorithms="HS256")

    except jwt.exceptions.ExpiredSignatureError:
        response = {
            "status": StatusCodes["api_error"],
            "results": "token invalido. tente autenticar novamente",
        }
        return flask.jsonify(response)

    if "user_id" not in credentials:
        response = {"status": StatusCodes["api_error"], "results": "Invalid token"}
        return flask.jsonify(response)

    for song in payload["songs"]:
        if "song_id" not in song:
            if "song_name" not in song:
                response = {
                    "status": StatusCodes["api_error"],
                    "results": "song_name value not in song",
                }
                return flask.jsonify(response)

            if "duration" not in song:
                response = {
                    "status": StatusCodes["api_error"],
                    "results": "duration value not in song",
                }
                return flask.jsonify(response)

            if "genre" not in song:
                response = {
                    "status": StatusCodes["api_error"],
                    "results": "genre value not in song",
                }
                return flask.jsonify(response)

            if "release_date" not in song:
                response = {
                    "status": StatusCodes["api_error"],
                    "results": "release_date value not in song",
                }
                return flask.jsonify(response)

            if "publisher_id" not in song:
                response = {
                    "status": StatusCodes["api_error"],
                    "results": "publisher_id value not in song",
                }
                return flask.jsonify(response)

    conn = db_connection()
    cur = conn.cursor()

    try:
        # begin the transaction
        cur.execute("BEGIN TRANSACTION;")

        for song in payload["songs"]:
            if "song_id" in song:
                #  validate if the artist is associated with the selected existing songs
                statement = "SELECT artist_person_users_id FROM artist_song WHERE song_ismn = %s AND artist_person_users_id = %s"
                values = (
                    song["song_id"],
                    credentials["user_id"],
                )

                cur.execute(statement, values)
                if cur.fetchone()[0] is None:
                    response = {
                        "status": StatusCodes["api_error"],
                        "errors": f'you are not associated with {song["song_id"]} song',
                    }
                    conn.close()
                    return flask.jsonify(response)

        # parameterized queries, good for security and performance
        statement = "INSERT INTO album (title, release_date, artist_person_users_id, label_id) VALUES (%s,%s,%s,%s) RETURNING id;"
        values = (
            payload["album_name"],
            payload["release_date"],
            credentials["user_id"],
            payload["publisher_id"],
        )

        cur.execute(statement, values)

        album_id = cur.fetchone()[0]

        for song in payload["songs"]:
            song_id = 0
            if "song_id" in song:
                song_id = song["song_id"]

            else:
                statement = "INSERT INTO song (title, release_date, duration, genre, artist_person_users_id, label_id) VALUES (%s, %s, %s, %s, %s, %s) RETURNING ismn;"
                values = (
                    song["song_name"],
                    song["release_date"],
                    song["duration"],
                    song["genre"],
                    credentials["user_id"],
                    song["publisher_id"],
                )
                cur.execute(statement, values)

                song_id = cur.fetchone()[0]

                statement = "INSERT INTO artist_song (artist_person_users_id, song_ismn) VALUES (%s, %s);"
                values = (
                    credentials["user_id"],
                    song_id,
                )

                cur.execute(statement, values)

                if "other_artists" in song:
                    for artist_id in song["other_artists"]:
                        statement = "INSERT INTO artist_song (artist_person_users_id, song_ismn) VALUES (%s, %s);"
                        values = (
                            artist_id,
                            song_id,
                        )
                        cur.execute(statement, values)

            statement = "INSERT INTO song_album (song_ismn, album_id) VALUES (%s,%s);"
            values = (
                song_id,
                album_id,
            )
            cur.execute(statement, values)

        # commit the transaction
        cur.execute("COMMIT;")

        response = {
            "status": StatusCodes["success"],
            "results": f"Inserted album {album_id}",
        }

    except (Exception, psycopg.DatabaseError) as error:
        logger.error(f"POST /dbproj/album_id - error: {error}")
        response = {"status": StatusCodes["internal_error"], "errors": str(error)}

        # an error occurred, rollback
        cur.execute("ROLLBACK;")

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


#
# POST
#
# Add a new comment for a song in a JSON payload
#
# To use it, you need to use postman or curl:
#
# curl -X POST http://localhost:8080/dbproj/comments/{song_ismn} -H 'Content-Type: application/json' -d '{"comment": "comment_details", "consumer_person_users_id": 1}'
#
@app.route("/dbproj/comments/<song_ismn>", methods=["POST"])
def add_comment(song_ismn):
    logger.info(f"POST /dbproj/comments/{song_ismn}")
    payload = flask.request.get_json()

    logger.debug(f"POST /dbproj/comments/{song_ismn} - payload: {payload}")

    # validate every argument
    if "comment" not in payload:
        response = {
            "status": StatusCodes["api_error"],
            "results": "comment value not in payload",
        }
        return flask.jsonify(response)

    if "token" not in payload:
        response = {
            "status": StatusCodes["api_error"],
            "results": "token value not in payload",
        }
        return flask.jsonify(response)

    try:
        credentials = jwt.decode(payload["token"], secret_key, algorithms="HS256")

    except jwt.exceptions.ExpiredSignatureError:
        response = {
            "status": StatusCodes["api_error"],
            "results": "token invalido. tente autenticar novamente",
        }
        return flask.jsonify(response)

    if "user_id" not in credentials:
        response = {"status": StatusCodes["api_error"], "results": "Invalid token"}
        return flask.jsonify(response)

    conn = db_connection()
    cur = conn.cursor()

    # parameterized queries, good for security and performance
    statement = "INSERT INTO comment (text, song_ismn, consumer_person_users_id) VALUES (%s, %s, %s) RETURNING id;"
    values = (payload["comment"], song_ismn, credentials["user_id"])

    try:
        # begin the transaction
        cur.execute("BEGIN TRANSACTION;")

        cur.execute(statement, values)

        comment_id = cur.fetchone()[0]

        # commit the transaction
        cur.execute("COMMIT;")

        response = {
            "status": StatusCodes["success"],
            "results": f"Inserted comment {comment_id}",
        }

    except (Exception, psycopg.DatabaseError) as error:
        logger.error(f"POST /dbproj/comments/{song_ismn} - error: {error}")
        response = {"status": StatusCodes["internal_error"], "errors": str(error)}

        # an error occurred, rollback
        cur.execute("ROLLBACK;")

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


#
# POST
#
# Add a new playlist in a JSON payload
#
# To use it, you need to use postman or curl:
#
# curl -X POST http://localhost:8080/dbproj/playlist -H 'Content-Type: application/json' -d '{"comment": "comment_details", "consumer_person_users_id": 1}'
#
@app.route("/dbproj/playlist", methods=["POST"])
def add_playlist():
    logger.info(f"POST /dbproj/playlist")
    payload = flask.request.get_json()

    logger.debug(f"POST /dbproj/playlist - payload: {payload}")

    # validate every argument
    if "playlist_name" not in payload:
        response = {
            "status": StatusCodes["api_error"],
            "results": "playlist_name value not in payload",
        }
        return flask.jsonify(response)

    if "visibility" not in payload:
        response = {
            "status": StatusCodes["api_error"],
            "results": "visibility value not in payload",
        }
        return flask.jsonify(response)

    if "songs" not in payload:
        response = {
            "status": StatusCodes["api_error"],
            "results": "songs value not in payload",
        }
        return flask.jsonify(response)

    if "token" not in payload:
        response = {
            "status": StatusCodes["api_error"],
            "results": "token value not in payload",
        }
        return flask.jsonify(response)

    try:
        credentials = jwt.decode(payload["token"], secret_key, algorithms="HS256")

    except jwt.exceptions.ExpiredSignatureError:
        response = {
            "status": StatusCodes["api_error"],
            "results": "token invalido. tente autenticar novamente",
        }
        return flask.jsonify(response)

    if "user_id" not in credentials:
        response = {"status": StatusCodes["api_error"], "results": "Invalid token"}
        return flask.jsonify(response)

    visibilidade = ""

    if payload["visibility"] == "private":
        visibilidade = "true"
    elif payload["visibility"] == "public":
        visibilidade = "false"
    else:
        response = {
            "status": StatusCodes["api_error"],
            "results": "token value not in payload",
        }
        return flask.jsonify(response)

    conn = db_connection()
    cur = conn.cursor()

    # parameterized queries, good for security and performance
    statement = "INSERT INTO playlist (name, is_private, consumer_person_users_id) VALUES (%s, %s, %s) RETURNING id;"
    values = (payload["playlist_name"], visibilidade, credentials["user_id"])

    try:
        # begin the transaction
        cur.execute("BEGIN TRANSACTION;")

        cur.execute(statement, values)

        playlist_id = cur.fetchone()[0]

        for song in payload["songs"]:
            statement = (
                "INSERT INTO playlist_song (song_ismn, playlist_id) VALUES (%s, %s);"
            )

            values = (song, playlist_id)

            cur.execute(statement, values)

        # commit the transaction
        cur.execute("COMMIT;")

        response = {
            "status": StatusCodes["success"],
            "results": f"Inserted playlist {playlist_id}",
        }

    except (Exception, psycopg.DatabaseError) as error:
        logger.error(f"POST /dbproj/playlist - error: {error}")
        response = {"status": StatusCodes["internal_error"], "errors": str(error)}

        # an error occurred, rollback
        cur.execute("ROLLBACK;")

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


#
# POST
#
@app.route("/dbproj/card", methods=["POST"])
def generate_cards():
    logger.info("POST /dbproj/card")
    payload = flask.request.get_json()

    logger.debug(f"POST /dbproj/card - payload: {payload}")

    # validate every argument:
    if "number_cards" not in payload:
        response = {
            "status": StatusCodes["api_error"],
            "results": "number_cards value not in payload",
        }
        return flask.jsonify(response)

    if "card_price" not in payload:
        response = {
            "status": StatusCodes["api_error"],
            "results": "card_price value not in payload",
        }
        return flask.jsonify(response)

    if "token" not in payload:
        response = {
            "status": StatusCodes["api_error"],
            "results": "token value not in payload",
        }
        return flask.jsonify(response)

    try:
        credentials = jwt.decode(payload["token"], secret_key, algorithms="HS256")

    except jwt.exceptions.ExpiredSignatureError:
        response = {
            "status": StatusCodes["api_error"],
            "results": "token invalido. tente autenticar novamente",
        }
        return flask.jsonify(response)

    if "user_id" not in credentials:
        response = {"status": StatusCodes["api_error"], "results": "Invalid token"}
        return flask.jsonify(response)

    amount = 0

    if payload["card_price"] == 10:
        amount = 10
    elif payload["card_price"] == 25:
        amount = 25
    elif payload["card_price"] == 50:
        amount = 50
    else:
        response = {"status": StatusCodes["api_error"], "results": "Invalid card_price"}
        return flask.jsonify(response)

    conn = db_connection()
    cur = conn.cursor()

    chars = "QWERTYUIOPASDFGHJKLZXCVBNM1234567890"

    try:
        # begin the transaction
        cur.execute("BEGIN TRANSACTION;")

        cards = []
        for i in range(int(payload["number_cards"])):
            statement = "INSERT INTO card (code, expire, amount, type, administrator_users_id) VALUES (%s, %s, %s, %s, %s) RETURNING id;"
            values = (
                "".join(random.choices(chars, k=16)),
                datetime.datetime.now() + datetime.timedelta(days=30),
                amount,
                amount,
                credentials["user_id"],
            )

            cur.execute(statement, values)
            card_id = cur.fetchone()[0]
            cards.append(card_id)

        # commit the transaction
        cur.execute("COMMIT;")

        response = {"status": StatusCodes["success"], "results": cards}

    except (Exception, psycopg.DatabaseError) as error:
        logger.error(f"POST /dbproj/card - error: {error}")
        response = {"status": StatusCodes["internal_error"], "errors": str(error)}

        # an error occurred, rollback
        cur.execute("ROLLBACK;")

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


#
# POST
# http://localhost:8080/dbproj/subcription
#
@app.route("/dbproj/subcription", methods=["POST"])
def subscribe_premium():
    logger.info("POST /dbproj/subcription")
    payload = flask.request.get_json()

    logger.debug(f"POST /dbproj/subcription - payload: {payload}")

    # validate every argument:
    if "period" not in payload:
        response = {
            "status": StatusCodes["api_error"],
            "results": "period value not in payload",
        }
        return flask.jsonify(response)

    if "cards" not in payload:
        response = {
            "status": StatusCodes["api_error"],
            "results": "cards not in payload",
        }
        return flask.jsonify(response)

    if "token" not in payload:
        response = {
            "status": StatusCodes["api_error"],
            "results": "token value not in payload",
        }
        return flask.jsonify(response)

    try:
        credentials = jwt.decode(payload["token"], secret_key, algorithms="HS256")

    except jwt.exceptions.ExpiredSignatureError:
        response = {
            "status": StatusCodes["api_error"],
            "results": "token invalido. tente autenticar novamente",
        }
        return flask.jsonify(response)

    if "user_id" not in credentials:
        response = {"status": StatusCodes["api_error"], "results": "Invalid token"}
        return flask.jsonify(response)

    conn = db_connection()
    cur = conn.cursor()

    today = datetime.datetime.now()

    # buscar o preço do plano

    statement = "SELECT price, days_period, id FROM plan WHERE name = %s AND last_update <= %s ORDER BY last_update DESC LIMIT 1;"
    values = (payload["period"], today)

    cur.execute(statement, values)
    all = cur.fetchone()

    price = all[0]
    days_period = all[1]
    plan_id = all[2]

    if price is None:
        response = {
            "status": StatusCodes["api_error"],
            "results": "Plano indisponivel",
        }
        return flask.jsonify(response)

    # verificar se é já subscrito

    statement = "SELECT end_date FROM subscription WHERE end_date >= %s ORDER BY end_date DESC LIMIT 1"
    values = (today,)
    cur.execute(statement, values)
    res = cur.fetchone()

    sub_end = datetime.timedelta(days=0)

    if res is not None:
        sub_end = res[0]

    try:
        # begin the transaction
        cur.execute("BEGIN TRANSACTION;")

        statement = "SELECT id, amount FROM card WHERE expire >= %s AND code = ANY(%s) AND amount > 0 ORDER BY expire;"
        values = (
            today,
            payload["cards"],
        )
        cur.execute(statement, values)
        cards = cur.fetchall()

        if cards is None:
            response = {
                "status": StatusCodes["api_error"],
                "results": "Saldo indisponivel",
            }
            return flask.jsonify(response)

        statement = "INSERT INTO subscription (init_date, end_date, purchase_date, plan_id, consumer_person_users_id) VALUES (%s, %s, %s, %s, %s) RETURNING id;"
        sub_end_timedelta = sub_end - datetime.datetime.now()

        values = (
            sub_end,
            today + sub_end_timedelta + datetime.timedelta(days=days_period),
            today,
            plan_id,
            credentials["user_id"],
        )

        cur.execute(statement, values)
        sub_id = cur.fetchone()[0]

        for card in cards:
            aux = price
            price -= card[1]

            if price < 0:
                statement = "INSERT INTO history_card (cost, card_id, subscription_id) VALUES (%s, %s, %s);"
                values = (aux, card[0], sub_id)
                cur.execute(statement, values)

                statement = "UPDATE card SET amount = %s WHERE id = %s;"
                values = (-price, card[0])
                cur.execute(statement, values)
                break

            statement = "INSERT INTO history_card (cost, card_id, subscription_id) VALUES (%s, %s, %s);"
            values = (card[1], card[0], sub_id)

            statement = "UPDATE card SET amount = 0 WHERE id = %s;"
            values = card[0]

            if price == 0:
                break

        if price > 0:
            response = {
                "status": StatusCodes["api_error"],
                "results": "Saldo indisponivel",
            }
            return flask.jsonify(response)

        # commit the transaction
        cur.execute("COMMIT;")

        response = {"status": StatusCodes["success"], "results": sub_id}

    except (Exception, psycopg.DatabaseError) as error:
        logger.error(f"POST /dbproj/subcription - error: {error}")
        response = {"status": StatusCodes["internal_error"], "errors": str(error)}

        # an error occurred, rollback
        cur.execute("ROLLBACK;")

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


def main():
    host = "127.0.0.1"
    port = 8080

    logger.info(f"API online: http://{host}:{port}/dbproj")
    app.run(host=host, debug=True, threaded=True, port=port)


if __name__ == "__main__":
    main()
