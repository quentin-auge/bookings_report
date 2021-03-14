import os
import uuid
from datetime import date, timedelta
from io import StringIO

import pytest
import sqlalchemy
import yaml
from sqlalchemy import Column, Date, Integer, String, Table, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base

from bookings_report.psql_utils import build_psql_url, load_from_csv, unload_to_csv


@pytest.fixture(scope='module')
def engine() -> Engine:
    with open(os.path.join(os.path.dirname(__file__), '..', 'conf.yaml')) as f:
        conf = yaml.safe_load(f)

    # Connect to the database
    psql_url = 'postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}'.format(**conf)
    engine = create_engine(psql_url)

    # Create test schema if necessary
    schema = 'test'

    if not engine.dialect.has_schema(engine, schema):
        engine.execute(sqlalchemy.schema.CreateSchema(schema))

    # Recreate engine using test schema
    engine = create_engine(psql_url, connect_args={'options': f'-csearch_path={schema}'})

    return engine


@pytest.fixture(scope='module')
def fake_csv() -> str:
    csv = 'a,b,c\n'

    d = date(2020, 1, 1)
    for i in range(50000):
        csv += ','.join(map(str, [i, f'a_{i}', d + timedelta(days=i)])) + '\n'

    return csv


@pytest.fixture
def table(engine) -> Table:
    Base = declarative_base()

    class TestTable(Base):
        __tablename__ = 'test_table_{}'.format(str(uuid.uuid4())[-10:])
        a = Column(Integer, primary_key=True)
        b = Column(String)
        c = Column(Date)

    TestTable.__table__.create(bind=engine, checkfirst=True)

    try:
        yield TestTable
    finally:
        TestTable.__table__.drop(bind=engine, checkfirst=True)


def test_build_psql_url():
    conf = {'host': 'a', 'port': '1234', 'user': 'b', 'pwd': 'c', 'db': 'd'}
    expected_psql_url = f'postgresql+psycopg2://b:c@a:1234/d'
    actual_psql_url = build_psql_url(**conf)
    assert actual_psql_url == expected_psql_url


def test_load_unload_csv(fake_csv, table, engine):
    input_stream = StringIO()
    input_stream.write(fake_csv)

    load_from_csv(input_stream, table, engine)

    output_stream = StringIO()
    unload_to_csv(table, output_stream, engine)

    assert input_stream.getvalue() == output_stream.getvalue()
