import psycopg2
import numpy
import face_recognition
from datetime import datetime
import time

def connect_db():
    """
    Create new connection to database
    """
    conn = psycopg2.connect(
        dbname='security',
        user='postgres',
        password='71102Tony',
        host='localhost',
        port='5433'
    )
    return conn

def add_visit(user_id):
    """
    Insert new visit row to database
    corresponding to user_id
    """
    try:
        print("adding")
        connection = connect_db()
        cursor = connection.cursor()
        cursor.execute(
            f"""
            INSERT INTO accounts_visit ("time", user_id) VALUES (CURRENT_TIMESTAMP, {user_id});
            """
        )
        connection.commit()
    except psycopg2.Error as e:
        connection.close()
        raise psycopg2.Error("DB error: "+str(e))
    connection.close()

def cube_np_parser(cube_str):
    """
    convert CUBE type postges to numpy array
    """

    cube_str = cube_str[1:]
    cube_str = cube_str[:-1]
    return numpy.fromstring(cube_str, dtype=float, sep=',')

def encoding_parser(cube_vec_low, cube_vec_high):
    """
    Combine 2 vector in Database to form a 128-dim encoding vector
    """
    vec_low = cube_np_parser(cube_vec_low)
    vec_high = cube_np_parser(cube_vec_high)
    return numpy.concatenate((vec_low, vec_high))

def get_users():
    """
    Get information of all current ordinary users in database
    """
    try:
        connection = connect_db()
        cursor = connection.cursor()
        cursor.execute(
            f"""
            SELECT id, first_name, last_name, vec_low, vec_high  from accounts_myuser 
                WHERE vec_low IS NOT NULL
            """
        )
        def  sumarize_user(user):
            return {
                'id': user[0],
                'name': f"{user[1]} {user[2]}",
            }
        users_info = cursor.fetchall()
        users = list(map(sumarize_user, users_info))
        encodings = list(map(lambda user: encoding_parser(user[3], user[4]), users_info))
        return {
            'users': users,
            'encodings': encodings
        } 
    except psycopg2.Error as e:
        print(e)
        connection.close()
        raise psycopg2.Error(e)

def detect_face(encodings, threshold):
    """
    Calculate the Euclidean Distance 
    between given encodings and in database

    Determine the Face is correct if distance < threshold
    """

    # for measure query time
    start_time = time.time() 
    try:    
        connection = connect_db()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT  id, first_name, last_name FROM accounts_myuser
            WHERE sqrt(power(CUBE(array[{}]) <-> vec_low, 2) 
            + power(CUBE(array[{}]) <-> vec_high, 2)) <= {}
            """.format(
                ','.join(str(s) for s in encodings[0:64]),
                ','.join(str(s) for s in encodings[64:128]),
                    threshold
                ) +  
            """ORDER BY 
                sqrt(power(CUBE(array[{}]) <-> vec_low, 2) 
                    + power(CUBE(array[{}]) <-> vec_high, 2)) ASC LIMIT 1
            """.format(
                ','.join(str(s) for s in encodings[0:64]),
                ','.join(str(s) for s in encodings[64:128]),
                )
        )
        user = cursor.fetchone()
        connection.close()
        print("--- %s seconds ---" % (time.time() - start_time))
        return user

    except psycopg2.Error as e:
        connection.close()
        print(e)
        raise psycopg2.Error(e)