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


import flask
import logging
import psycopg
import jwt
import datetime

app = flask.Flask(__name__)

StatusCodes = {
    'success': 200,
    'api_error': 400,
    'internal_error': 500
}


##########################################################
# DATABASE ACCESS
##########################################################

def db_connection():
    db = psycopg.connect(
        user='spotsong',
        password='spotsong',
        host='127.0.0.1',
        port='5432',
        database='dbspotsong'
    )

    return db


##########################################################
# ENDPOINTS
##########################################################


@app.route('/dbproj')
def landing_page():
    return """

    Hello World (Python Native)!  <br/>
    <br/>
    Check the sources for instructions on how to use the endpoints!<br/>
    <br/>
    BD 2022 Team<br/>
    <br/>
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
@app.route('/dbproj/user', methods=['POST'])
def add_user():
    logger.info('POST /dbproj/user')
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'POST /dbproj/user - payload: {payload}')

    if 'username' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'username value not in payload'}
        return flask.jsonify(response)

    if 'email' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'email value not in payload'}
        return flask.jsonify(response)

    if 'password' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'password value not in payload'}
        return flask.jsonify(response)

    # parameterized queries, good for security and performance
    statement = 'INSERT INTO users (username, email, password) VALUES (%s, %s, %s)'
    values = (payload['username'], payload['email'], payload['password'])

    try:
        cur.execute(statement, values)

        # commit the transaction
        conn.commit()
        response = {'status': StatusCodes['success'], 'results': f'Inserted user {payload["username"]}'}

    except (Exception, psycopg.DatabaseError) as error:
        logger.error(f'POST /dbproj/user - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

        # an error occurred, rollback
        conn.rollback()

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

@app.route('/dbproj/user', methods=['PUT'])
def authenticate_user():
    logger.info('PUT /dbproj/user')
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'PUT /dbproj/user - payload: {payload}')

    # do not forget to validate every argument, e.g.,:
    if 'username' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'username is required to login'}
        return flask.jsonify(response)

    if 'password' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'password is required to login'}
        return flask.jsonify(response)

    # parameterized queries, good for security and performance
    statement = 'SELECT username, password FROM users WHERE username = %s and password = %s'
    values = (payload['username'], payload['password'])

    try:
        cur.execute(statement, values)

        row = cur.fetchone()

        if row is None:
            response = {'status': StatusCodes['api_error'],
                        'errors': 'Passsword ou username incorretos'}

        else:
            response = {'status': StatusCodes['success'],
                        'results': jwt.encode(
                            {'username': payload['username'], 'password': payload['password'], 'exp': (
                                    datetime.datetime.now() + datetime.timedelta(minutes=2)).timestamp()}, "segredo",
                            algorithm="HS256")}

    except (Exception, psycopg.DatabaseError) as error:
        logger.error(error)
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


if __name__ == '__main__':
    # set up logging
    logging.basicConfig(filename='log_file.log')
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s', '%H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    host = '127.0.0.1'
    port = 8080
    app.run(host=host, debug=True, threaded=True, port=port)
    logger.info(f'API online: http://{host}:{port}')
