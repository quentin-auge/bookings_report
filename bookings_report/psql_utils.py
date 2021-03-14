from typing import TextIO

from sqlalchemy import Table
from sqlalchemy.engine import Engine


def build_psql_url(host: str, port: str, user: str, pwd: str, db: str) -> str:
    """
    Generate a PostgreSQL connection URL.
    """
    return f'postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}'


def load_from_csv(stream: TextIO, table: Table, engine: Engine):
    """
    Efficiently load a CSV to a PostgreSQL table.

    Args:
        stream: readable stream (file, `StringIO`, ...) containing the source CSV
        table: already-created PostgreSQL table
        engine: sqlalchemy engine
    """

    stream.seek(0)

    connection = engine.raw_connection()
    cursor = connection.cursor()

    copy_query = f'COPY {table.__tablename__} FROM STDIN WITH (FORMAT CSV, HEADER TRUE)'
    cursor.copy_expert(copy_query, stream)

    connection.commit()
    cursor.close()


def unload_to_csv(table: Table, stream: TextIO, engine: Engine):
    """
    Efficiently unload a PostgreSQL table to a stream.

    Args:
        stream: writable stream (file, `StringIO`, ...) receiving the unloaded CSV
        table: PostgreSQL table to unload
        engine: sqlalchemy engine
    """

    stream.seek(0)

    connection = engine.raw_connection()
    cursor = connection.cursor()

    copy_query = f'COPY {table.__tablename__} TO STDOUT WITH CSV HEADER'
    cursor.copy_expert(copy_query, stream)

    connection.commit()
    cursor.close()
