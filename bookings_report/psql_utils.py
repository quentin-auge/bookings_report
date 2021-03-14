import logging
from typing import TextIO

from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_LOGGER = logging.getLogger('sqlalchemy.engine')

MappedTable = declarative_base()


def build_psql_uri(host: str, port: str, user: str, pwd: str, db: str) -> str:
    """
    Generate a PostgreSQL connection URL.
    """
    return f'postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}'


def load_from_csv(stream: TextIO, table: MappedTable, engine: Engine):
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
    # For some reason, `cursor.copy_expert()` does not feel like logging anything
    SQLALCHEMY_LOGGER.info(copy_query)

    cursor.copy_expert(copy_query, stream)

    connection.commit()
    cursor.close()


def unload_to_csv(table: MappedTable, stream: TextIO, engine: Engine):
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
    # For some reason, `cursor.copy_expert()` does not feel like logging anything
    SQLALCHEMY_LOGGER.info(copy_query)

    cursor.copy_expert(copy_query, stream)

    connection.commit()
    cursor.close()
