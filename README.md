# Bookings report project

Generate a monthly restaurant bookings report.

The code runs with Python >= 3.6. It is a locally pip-installable python package connecting to a
(dockerized) PostgreSQL instance using `sqlalchemy`, exposing a `bookings-report` command line tool.

A justification of design decisions and suggestions of further improvements is available in
[design.md](design.md).

It is tested using `tox` and `pytest` with 100% code coverage (excluding the main).

## Setup

### Postgres server

* Make sure you've got a docker deamon up and running on your local machine.

* Pull the latest version of `postgres` image

```
$ docker pull postgres
```

* Run it

```
$ docker run -e POSTGRES_USER=docker -e POSTGRES_PASSWORD='%N2GV*#dFKws7S' -e POSTGRES_DB=db -p 54321:5432 postgres
```

### Project

* Clone this repository

* Move into project directory
  ```
  cd bookings_report/
  ```

* Create a virtual environment and activate it:
  ```
  virtualenv -p python3 .venv
  source .venv/bin/activate
  ```

* Install the application inside the virtualenv
  ```
  pip install .
  ```

It exposes a `bookings-report` command line tool.

## Run the application

Usage:

```
$ bookings-report --help
usage: bookings-report [-h] [--out report_file] [--conf psql_conf] [--verbose]
                       bookings_file

Generate a monthly restaurant bookings report

positional arguments:
  bookings_file         input CSV bookings

optional arguments:
  -h, --help            show this help message and exit
  --out report_file, -o report_file
                        output CSV report
  --conf psql_conf      YAML database configuration (default: conf/psql.yaml)
  --verbose, -v         verbose logging
```

Aggregate file `bookings.csv` into PostgreSQL table `monthly_restaurants_report` and export to
CSV `monthly_restaurants_report.csv` (sample app output):

```
$ time bookings-report -o monthly_restaurant_report.csv bookings.csv -v
INFO:sqlalchemy.orm.mapper.Mapper:(Bookings|bookings) _configure_property(booking_id, Column)
INFO:sqlalchemy.orm.mapper.Mapper:(Bookings|bookings) _configure_property(restaurant_id, Column)
INFO:sqlalchemy.orm.mapper.Mapper:(Bookings|bookings) _configure_property(restaurant_name, Column)
INFO:sqlalchemy.orm.mapper.Mapper:(Bookings|bookings) _configure_property(client_id, Column)
INFO:sqlalchemy.orm.mapper.Mapper:(Bookings|bookings) _configure_property(client_name, Column)
INFO:sqlalchemy.orm.mapper.Mapper:(Bookings|bookings) _configure_property(amount, Column)
INFO:sqlalchemy.orm.mapper.Mapper:(Bookings|bookings) _configure_property(currency, Column)
INFO:sqlalchemy.orm.mapper.Mapper:(Bookings|bookings) _configure_property(guests, Column)
INFO:sqlalchemy.orm.mapper.Mapper:(Bookings|bookings) _configure_property(date, Column)
INFO:sqlalchemy.orm.mapper.Mapper:(Bookings|bookings) _configure_property(country, Column)
INFO:sqlalchemy.orm.mapper.Mapper:(Bookings|bookings) Identified primary key columns: ColumnSet([Column('booking_id', UUID(), table=<bookings>, primary_key=True, nullable=False)])
INFO:sqlalchemy.orm.mapper.Mapper:(Bookings|bookings) constructed
[...]
INFO:sqlalchemy.engine:COPY bookings FROM STDIN WITH (FORMAT CSV, HEADER TRUE)
[...]
INFO:sqlalchemy.orm.mapper.Mapper:(Bookings|monthly_restaurant_report) _configure_property(booking_id, Column)
INFO:sqlalchemy.orm.mapper.Mapper:(Bookings|monthly_restaurant_report) _configure_property(restaurant_id, Column)
INFO:sqlalchemy.orm.mapper.Mapper:(Bookings|monthly_restaurant_report) _configure_property(restaurant_name, Column)
INFO:sqlalchemy.orm.mapper.Mapper:(Bookings|monthly_restaurant_report) _configure_property(client_id, Column)
INFO:sqlalchemy.orm.mapper.Mapper:(Bookings|monthly_restaurant_report) _configure_property(client_name, Column)
INFO:sqlalchemy.orm.mapper.Mapper:(Bookings|monthly_restaurant_report) _configure_property(amount, Column)
INFO:sqlalchemy.orm.mapper.Mapper:(Bookings|monthly_restaurant_report) _configure_property(currency, Column)
INFO:sqlalchemy.orm.mapper.Mapper:(Bookings|monthly_restaurant_report) _configure_property(guests, Column)
INFO:sqlalchemy.orm.mapper.Mapper:(Bookings|monthly_restaurant_report) _configure_property(date, Column)
INFO:sqlalchemy.orm.mapper.Mapper:(Bookings|monthly_restaurant_report) _configure_property(country, Column)
INFO:sqlalchemy.orm.mapper.Mapper:(Bookings|monthly_restaurant_report) Identified primary key columns: ColumnSet([Column('booking_id', UUID(), table=<monthly_restaurant_report>, primary_key=True, nullable=False)])
INFO:sqlalchemy.orm.mapper.Mapper:(Bookings|monthly_restaurant_report) constructed
[...]
INFO:sqlalchemy.engine.base.Engine:BEGIN (implicit)
INFO:sqlalchemy.engine.base.Engine:TRUNCATE TABLE monthly_restaurant_report
INFO:sqlalchemy.engine.base.Engine:
    INSERT INTO monthly_restaurant_report
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
            FROM bookings
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
INFO:sqlalchemy.engine.base.Engine:COMMIT
[...]
INFO:bookings_report.cli:Writing report to monthly_restaurant_report.csv
INFO:sqlalchemy.engine:COPY monthly_restaurant_report TO STDOUT WITH CSV HEADER
[...]

real    0m1.317s
user    0m0.845s
sys     0m0.032s
```

Sample result (requires `csvlook` (`pip install csvkit`)):

```
$ head monthly_restaurant_report.csv | csvlook -I
| restaurant_id                        | restaurant_name     | country        | month   | number_of_bookings | number_of_guests | amount   |
| ------------------------------------ | ------------------- | -------------- | ------- | ------------------ | ---------------- | -------- |
| 19ad4a46-3ac0-405d-97b3-65a16d066f4b | Chargeurs           | France         | 2011-04 | 1                  | 4                | 104,08 € |
| d342086c-266d-481d-a862-7f0973b3a10b | Abengoa             | España         | 2005-09 | 3                  | 20               | 435,24 € |
| 4d855010-a547-4e19-a43a-37df6e84c83a | Mivar               | Italia         | 2015-04 | 2                  | 16               | 224,88 € |
| d342086c-266d-481d-a862-7f0973b3a10b | Abengoa             | España         | 2018-02 | 3                  | 18               | 456,80 € |
| af869ab5-ab57-4c50-8456-a74341edc070 | Taylor Wimpey (TW.) | United Kingdom | 2007-10 | 4                  | 36               | £465.77  |
| 651effa3-2819-43a4-98a7-bef16977c4d8 | Vera Borea          | France         | 2003-01 | 1                  | 10               | 94,01 €  |
| bc390fcf-b073-4ee1-8034-84dc16b8e736 | AgileBio            | France         | 2000-06 | 4                  | 24               | 542,49 € |
| 81b15746-2dcb-4b3b-92ac-49cf8865e26b | Guerciotti          | Italia         | 2005-04 | 2                  | 10               | 162,24 € |
| 19ad4a46-3ac0-405d-97b3-65a16d066f4b | Chargeurs           | France         | 2001-12 | 1                  | 4                | 95,09 €  |

```

## Run the tests

Install `tox` and run it:

```
pip install tox
tox
```

Sample run:

```
$ tox
GLOB sdist-make: setup.py
py3 inst-nodeps: .tox/.tmp/package/1/bookings-report-0.1.zip
py3 run-test: commands[0] | pytest --cov bookings_report
========================= test session starts ========================
platform linux -- Python 3.8.0, pytest-6.2.2, py-1.10.0, pluggy-0.13.1
cachedir: .tox/py3/.pytest_cache
rootdir: .
plugins: cov-2.11.1
collected 27 items

test_aggregate.py ...                                           [ 11%]
test_psql_utils.py ..                                           [ 18%]
test_transform.py ......................                        [100%]


----------- coverage: platform linux, python 3.8.0-final-0 -----------
Name                              Stmts   Miss Branch BrPart  Cover
----------------------------------------------------------------------
bookings_report/aggregate.py       14      0      0      0   100%
bookings_report/psql_utils.py      26      0      0      0   100%
bookings_report/tables.py          29      0      0      0   100%
bookings_report/transform.py       27      0      4      0   100%
---------------------------------------------------------------------
TOTAL                              96      0      4      0   100%

======================== 27 passed in 2.05s =========================
______________________________ summary ______________________________
  py3: commands succeeded
  congratulations :)
```
