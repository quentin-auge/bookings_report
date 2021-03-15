# Bookings report project

Generate a monthly restaurant bookings report.

The code runs with Python >= 3.6. It is a locally pip-installable python package connecting to
a (dockerized) PostgreSQL instance using `sqlalchemy`, exposing a `bookings-report` command line
tool.

It is tested using `tox` and `pytest`.

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

usage: bookings-report [-h] --out OUT bookings_file

Generate a monthly restaurant bookings report

positional arguments:
  bookings_file      input CSV bookings

optional arguments:
  -h, --help         show this help message and exit
  --out OUT, -o OUT  output CSV report
```

Aggregate file `bookings.csv` into `monthly_restaurants_report.csv`:

```
$ bookings-report bookings.csv -o monthly_restaurants_report.csv
```

## Run the tests

Install `tox` and run it:

```
pip install tox
tox
```

Tox outputs the coverage at the end.

Sample run:

```
$ tox
```
