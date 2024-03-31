import os
from typing import Optional
import psycopg2
import psycopg2.pool
import psycopg2.extensions

_pool: Optional[psycopg2.pool.SimpleConnectionPool] = None


class db_conn:
    def __enter__(self) -> psycopg2.extensions.connection:
        global _pool
        if _pool is None:
            user = os.environ.get('DB_USER')
            password = os.environ.get('DB_PASSWORD')
            hostname = os.environ.get('DB_HOST', '0.0.0.0')
            database = os.environ.get('DB_NAME', 'postgres')
            port = os.environ.get('DB_PORT', 5432)
            _pool = psycopg2.pool.SimpleConnectionPool(database=database,
                                                       user=user,
                                                       password=password,
                                                       host=hostname,
                                                       port=port,
                                                       maxconn=16,
                                                       minconn=1)

        self._con = _pool.getconn()
        return self._con

    def __exit__(self, exc_type, exc_val, exc_tb):
        _pool.putconn(self._con)
