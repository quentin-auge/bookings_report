import os

import pytest
import sqlalchemy
import yaml
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


@pytest.fixture(scope='session')
def engine() -> Engine:
    with open(os.path.join(os.path.dirname(__file__), '..', 'conf', 'psql.yaml')) as f:
        conf = yaml.safe_load(f)

    # Connect to the database
    psql_uri = 'postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}'.format(**conf)
    engine = create_engine(psql_uri)

    # Create test schema if necessary
    schema = 'test'

    if not engine.dialect.has_schema(engine, schema):
        engine.execute(sqlalchemy.schema.CreateSchema(schema))

    # Recreate engine using test schema
    engine = create_engine(psql_uri, connect_args={'options': f'-csearch_path={schema}'})

    return engine
