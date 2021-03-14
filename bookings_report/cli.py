import argparse
import os


def main():
    # Arguments parsing

    parser = argparse.ArgumentParser(description='Generate a monthly restaurant bookings report')
    parser.add_argument('bookings_file', help='input CSV bookings')
    parser.add_argument('--out', '-o', required=True, help='output CSV report')
    args = parser.parse_args()


if __name__ == '__main__':
    main()
