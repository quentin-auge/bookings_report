import argparse
import atexit
import logging
from csv import DictReader, DictWriter
from io import StringIO

import sqlalchemy
import yaml

from bookings_report.aggregate import aggregate_report
from bookings_report.psql_utils import build_psql_uri, load_from_csv, unload_to_csv
from bookings_report.tables import get_bookings_table, get_report_table
from bookings_report.transform import parse_amount_and_currency, parse_date

LOGGER = logging.getLogger(__name__)


def main():
    # Parse arguments

    parser = argparse.ArgumentParser(description='Generate a monthly restaurant bookings report')
    parser.add_argument('bookings_file', help='input CSV bookings')
    parser.add_argument('--out', '-o', metavar='report_file', help='output CSV report')
    parser.add_argument('--conf', metavar='psql_conf', default='conf/psql.yaml',
                        help='YAML database configuration (default: %(default)s)')
    parser.add_argument('--verbose', '-v', action='store_true', help='verbose logging')
    args = parser.parse_args()

    # Configure logging

    logging.basicConfig(level=logging.WARNING)

    if args.verbose:
        logging.root.setLevel(logging.INFO)
        logging.getLogger('sqlalchemy').setLevel(logging.INFO)

    # Connect to the database

    with open(args.conf) as f:
        conf = yaml.safe_load(f)

    psql_uri = build_psql_uri(**conf)

    engine = sqlalchemy.create_engine(psql_uri)

    # Create bookings table (temporary table)

    bookings_table = get_bookings_table('bookings')

    # Drop bookings table if it already exists
    bookings_table.__table__.drop(bind=engine, checkfirst=True)
    bookings_table.__table__.create(bind=engine)
    # Schedule drop table at end of script
    atexit.register(lambda: bookings_table.__table__.drop(bind=engine, checkfirst=True))

    # Retrieve bookings table column names
    columns = [c.key for c in bookings_table.__table__.columns]

    # Extract data from booking file

    with open(args.bookings_file) as f:
        reader = DictReader(f)

        stream = StringIO()
        writer = DictWriter(stream, fieldnames=columns)

        writer.writeheader()

        # Transform booking rows for proper loading into the database
        for row in reader:
            row['amount'], row['currency'] = parse_amount_and_currency(raw_amount=row['amount'])
            row['date'] = parse_date(row['date'])
            writer.writerow(row)

    # Load booking rows into the database
    load_from_csv(stream, bookings_table, engine)

    # Access report table

    report_table = get_report_table('monthly_restaurant_report')

    # Create report table if it does not exist
    report_table.__table__.create(bind=engine, checkfirst=True)

    # Perform report aggregation
    aggregate_report(bookings_table, report_table, engine)

    # Export to CSV

    if args.out:
        with open(args.out, 'w') as f:
            LOGGER.info(f'Writing report to {args.out}')
            unload_to_csv(report_table, f, engine)


if __name__ == '__main__':
    main()
