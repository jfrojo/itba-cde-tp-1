from psycopg2 import pool
from threading import current_thread

class Database:

    def __init__(self, hostname, port, database, username, password, max_connections=32):
        p = pool.ThreadedConnectionPool(1, max_connections, 
            host=hostname,
            port=port,
            database=database,
            user=username,
            password=password
        )
        
        if(not p):
            raise Exception("could not connect with the provided database")

        self._pool = p
        self._conns = {}
    
    def __enter__(self):
        conn = self._pool.getconn()
        self._conns[current_thread().native_id] = conn

        return conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        conn = self._conns[current_thread().native_id]
        if(conn is not None):
            conn.commit()
            self._pool.putconn(conn)
            self._conns[current_thread().native_id] = None

    def close(self):
        self._pool.closeall()

    def execute(self, cursor, query, params = []):
        cursor.execute(query, params)

    def fetch(self, cursor):
        return cursor.fetchone()

    def fetch_all(self, cursor):
        return cursor.fetchall()

    def has_results(self, cursor):
        return cursor.rowcount != 0

    def query(self, cursor, query, params = []):
        cursor.execute(query, params)
        return cursor.fetchall()