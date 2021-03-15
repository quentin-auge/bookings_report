import uuid
from datetime import date
from typing import Any, Dict, List

from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from bookings_report.aggregate import aggregate_report
from bookings_report.tables import get_bookings_table, get_report_table

MappedTable = declarative_base()


def _create_test_bookings_table(rows: List[Dict[str, Any]], engine: Engine) -> MappedTable:
    TestBookings = get_bookings_table(table_name='test_bookings_{}'.format(str(uuid.uuid4())[-10:]))
    TestBookings.__table__.create(bind=engine, checkfirst=True)

    Session = sessionmaker(bind=engine)
    session = Session()

    for row in rows:
        row = _transform_test_booking_row(row)
        booking = TestBookings(**row)
        session.add(booking)

    session.commit()

    return TestBookings


def _create_test_report_table(engine: Engine) -> MappedTable:
    TestReport = get_report_table(table_name='test_report_{}'.format(str(uuid.uuid4())[-10:]))
    TestReport.__table__.create(bind=engine, checkfirst=True)
    return TestReport


def _transform_test_booking_row(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'booking_id': str(uuid.uuid4()),
        'restaurant_id': '00000000-0000-0000-0000-00000000000' + str(row['restaurant_id']),
        'restaurant_name': 'restaurant',
        'client_id': str(uuid.uuid4()),
        'client_name': 'client',
        'country': 'country',
        'amount': row['amount'],
        'currency': row['currency'],
        'guests': row['guests'],
        'date': row['date']
    }


def _create_report_results(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return list(map(_transform_test_report_row, rows))


def _transform_test_report_row(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'restaurant_id': '00000000-0000-0000-0000-00000000000' + str(row['restaurant_id']),
        'restaurant_name': 'restaurant',
        'country': 'country',
        'month': row['month'],
        'number_of_bookings': row['number_of_bookings'],
        'number_of_guests': row['number_of_guests'],
        'amount': row['amount']
    }


def _query_report_rows(report_table: MappedTable, engine: Engine) -> List[Dict[str, Any]]:
    Session = sessionmaker(bind=engine)
    session = Session()

    rows = []
    for row in session.query(report_table).all():
        row = row.__dict__
        row.pop('_sa_instance_state', None)
        rows.append(row)
    return rows


def test_aggregate_report(engine):
    # Create and fill a bookings table

    booking_rows = [
        # Restaurant 1, month 1

        {
            'restaurant_id': 1,
            'amount': 1.01,
            'currency': '€',
            'guests': 1,
            'date': date(2020, 1, 14)
        },
        {
            'restaurant_id': 1,
            'amount': 2.02,
            'currency': '€',
            'guests': 2,
            'date': date(2020, 1, 12)
        },

        # Restaurant 1, month 2
        {
            'restaurant_id': 1,
            'amount': 3.03,
            'currency': '€',
            'guests': 3,
            'date': date(2020, 2, 15)
        },
        {
            'restaurant_id': 1,
            'amount': 4.04,
            'currency': '€',
            'guests': 4,
            'date': date(2020, 2, 9)
        },

        # Restaurant 2, month 2
        {
            'restaurant_id': 2,
            'amount': 5.55,
            'currency': '£',
            'guests': 5,
            'date': date(2020, 2, 6)
        },
        {
            'restaurant_id': 2,
            'amount': 6.66,
            'currency': '£',
            'guests': 6,
            'date': date(2020, 2, 21)
        },
        {
            'restaurant_id': 2,
            'amount': 7.77,
            'currency': '£',
            'guests': 7,
            'date': date(2020, 2, 18)
        },

        # Restaurant 2, month 3
        {
            'restaurant_id': 2,
            'amount': 8.88,
            'currency': '£',
            'guests': 8,
            'date': date(2020, 3, 3)
        }
    ]

    TestBookings = _create_test_bookings_table(booking_rows, engine)

    # Create and fill report table

    TestReport = _create_test_report_table(engine)
    aggregate_report(TestBookings, TestReport, engine)

    # Create expected report rows

    expected_report_rows = [
        # Restaurant 1, month 1
        {
            'restaurant_id': 1,
            'month': '2020-01',
            'number_of_bookings': 2,
            'number_of_guests': 3,
            'amount': '3,03 €'
        },

        # Restaurant 1, month 2
        {
            'restaurant_id': 1,
            'month': '2020-02',
            'number_of_bookings': 2,
            'number_of_guests': 7,
            'amount': '7,07 €'
        },

        # Restaurant 1, month 2
        {
            'restaurant_id': 2,
            'month': '2020-02',
            'number_of_bookings': 3,
            'number_of_guests': 18,
            'amount': '£19.98'
        },

        # Restaurant 2, month 3
        {
            'restaurant_id': 2,
            'month': '2020-03',
            'number_of_bookings': 1,
            'number_of_guests': 8,
            'amount': '£8.88'
        }
    ]

    expected_report_rows = _create_report_results(expected_report_rows)

    # Query actual report rows

    actual_report_rows = _query_report_rows(TestReport, engine)

    # Sort results (using primary keys) to allow for list equality test

    actual_report_rows.sort(key=lambda row: (row['restaurant_id'], row['month']))
    expected_report_rows.sort(key=lambda row: (row['restaurant_id'], row['month']))

    assert actual_report_rows == expected_report_rows
