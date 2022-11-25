import psycopg2
import numpy
import face_recognition

class MyDB:
    def __init__(self, dbname, user, password, host, port):
        self.conn =  psycopg2.connect(
            dbname=dbname,
            user=user, 
            password=password,
            host=host,
            port=port
        )
        self.cusor = self.conn.cursor()
        
    def __del__(self):
        if self.conn:
            self.conn.close()
    
    def get_user_data_from_db(self):
        self.cusor.execute('''
            select first_name, last_name, vec_low, vec_high from accounts_myuser
            where vec_low is not NULL
            ''')
        users_info = self.cusor.fetchall()
        names = list(map(lambda info: f'{info[0]} {info[1]}', users_info))
        encodings = list(map(lambda info: self.make_encoding(info[2], info[3]), users_info))

        return {
            'names': names,
            'encodings': encodings
        }

    def cubetype_np_parser(self, cube_str):
        cube_str = cube_str[1:]
        cube_str = cube_str[:-1]
        return numpy.fromstring(cube_str, dtype=float, sep=',')
        
    def merge_array(self, *args):
        return numpy.concatenate(args)
    
    def make_encoding(self, cube_str_low, cube_str_high):
        vec_low = self.cubetype_np_parser(cube_str_low)
        vec_high = self.cubetype_np_parser(cube_str_high)
        return self.merge_array(vec_low, vec_high)
    
    def detect_face_from_db(self, encodings, threshold):
        self.cusor.execute(
            """
        SELECT first_name, last_name, id FROM accounts_myuser 
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
        user = self.cusor.fetchone()
        return user
        
