import sqlalchemy
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.ext.declarative import declarative_base

MappedTable = declarative_base()


def aggregate_report(bookings_table: MappedTable, report_table: MappedTable, engine: Engine):
    """
    Aggregate bookings table into a monthly report, and replace report table content with it.

    Args:
        bookings_table: source bookings table mapper
        report_table: destination report table mapper
        engine: sqlalchemy engine

    Notes:
        Make the operation transactional.
    """

    with engine.begin() as connection:
        # Truncate already-existing report table
        _run_truncate_query(report_table, connection)

        # Recreate report
        _run_aggregate_report_query(bookings_table, report_table, connection)


def _run_truncate_query(table: MappedTable, connection: Connection) -> sqlalchemy.Text:
    truncate_query = sqlalchemy.text(f'TRUNCATE TABLE {table.__tablename__}')
    connection.execute(truncate_query)


def _run_aggregate_report_query(bookings_table: MappedTable, report_table: MappedTable,
                                connection: Connection):
    agg_query = sqlalchemy.text(f'''
    INSERT INTO {report_table.__tablename__}
        WITH report AS
        (
            SELECT
                restaurant_id,
                restaurant_name,
                country,
                to_char(date, 'YYYY-MM') AS month,
                SUM(amount) AS amount,
                COUNT(*) AS number_of_bookings,
                SUM(guests) AS number_of_guests,
                currency
            FROM {bookings_table.__tablename__}
            GROUP BY 1, 2, 3, 4, 8  -- group by currency
        )
        SELECT
            restaurant_id,
            restaurant_name,
            country,
            month,
            number_of_bookings,
            number_of_guests,
            CASE
                WHEN currency = '€' THEN
                    replace(amount::text || ' €', '.', ',')

                WHEN currency = '£' THEN
                    '£' || amount::text

                ELSE
                    -- `amount` is non-nullable in destination table;
                    -- Crash if amount formatting fails.
                    NULL
            END AS amount
        FROM report
    ''')

    connection.execute(agg_query)
