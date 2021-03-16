# Bookings report project

## Client and server

### PostgreSQL server

According to project requirements, PostgreSQL server is run within a docker container by
issuing a plain `docker` command with accompanying user, password, and database name.

Possible improvements:
 * this configuration could be embedded into a configuration file (say, using
`docker-compose`)
 * a custom docker image could be created and hosted, based on the original
`postgres` image
 * it might be good to freeze `postgres` image version for production purpose
 * creating separate dev/testing/staging/prod DBs is appropriate in a real-world scenario

### Client application

The client application is a Python package.  It could be dockerized as well, but it adds little
value as long at it runs on the same machine it is set up (pip-installed). Python package
`psycopg2-binary` does the heavy lifting of talking to the Postgres server without even needing
to install a `psql` client.

### Security

For convenience, client-side DB password is available in plain sight in configuration file
[psql.yaml](conf/psql.yaml), and versioned in git. I would secure it further by never comitting
it, and relying on environment variables to pass it along, or retrieving it from a secured vault
at runtime (think e.g. AWS Key Managment Store), for example.

## ETL

Apart from colum `amount` and `date`, all columns from input CSV `bookings.csv` are ready to
load into PostgreSQL table `bookings` as defined in [tables.py](bookings_report/tables.py) without
further transformation.

Parsing of columns `amount` and `date` is implemented in [transform.py](bookings_report/transform.py),
unit-tested in [test_transform.py](tests/test_transform.py).

### Transforming column `amount`

Column `amount` is definitely the most problematic to parse, being formatted as either `£xx.yy` or
`xx,yy<nbsp>€`.

A better format would be two separate columns `amount = xx.yy` and `currency = GBP|EUR`
([ISO 4217](https://en.wikipedia.org/wiki/ISO_4217)) being either. This is how table
`bookings` is structured (except `currency` is not ISO 4217).

Since the output report demands a single column `amount`, I decided to parse columns `amount`
back to its original format in final table `monthly_restaurant_report`.

In a real-world scenario, I would make sure this is the output format the shareholders want,
because it is nearly useless as such. I am not sure if tools further down the chain (e.g. Excel or
Tableau) would understand it. They may want currency conversion (say, to `EUR`) as well.

### Transforming column `date`

Column `date` is not as problematic. `%d-%m-%Y`- or `%d/%m/%Y`-formatted. Easy to parse.
Output report format `%m-%d` unambigously defined. No problem here.

## Data pipeline

Aggregating bookings into a monthly report is done through a pretty straightforward SQL query,
available in [aggregate.py](bookings_report/aggregate.py), tested in
[test_aggregate.py](tests/test_aggregate.py). Its result replaces the content of report table
`monthly_restaurant_report` defined in [tables.py](bookings_report/tables.py).

### Atomicity

Either aggregation succeeds and the content of the report table is replaced, or it doesn't, and the
report table is left untouched. It is implemented using a PostgreSQL transaction in
[aggregate.py](bookings_report/aggregate.py). This transactional behaviour is tested through
[test_aggregate.py::test_aggregate_report_transactionality()](tests/test_aggregate.py#L251).

### Indempotency

Because both the bookings and report table are re-created at each pipeline run, the pipeline can
run multiple times with the same data without crashing, and always yield the same result.

### Incremental report building

Recomputing the whole report periodically might end up wasting time and compute ressources.
The report table could be built incrementally by introducing a `[--start-month, --end-month]` time
range. Report rows would be upserted into report table using a
`DELETE FROM monthly_restaurant_report WHERE date BETWEEN start_month AND end_month`
statement instead of a `TRUNCATE` one. Atomicity is still guaranteed by the transaction.

## Tests

The test base is half unit-tested, half integration-tested.
Integration tests, such as highlighted in [test_aggregate.py](tests/test_aggregate.py) take care
of creating temporary name-randomized PostgreSQL tables isolated in a `test` schema (it might be
better to use a `test` database instead). Leveraging pytest fixtures, these tables are automatically
dropped at teardown.

The [main](bookings_report/cli.py) is untested (and excluded froù coverage, hence 100%).
I believe it should be tested through end-to-end tests, external to the data pipeline.

## Performance

`sqlachemy` provides a mysterious `copy_expert()` method for batching CSV import/export into/from
the database. It is orders of magnitude faster than pilling up individual inserts. It is essentially
why total runtime for the pipeline does not exceed a couple seconds.

Functions `load_from_csv()` and `unload_to_csv()` are convenience wrappers around `copy_expert()`.
They are implemented in [psql_utils.py](bookings_report/psql_utils.py), jointly integration-tested
in [test_psql_utils.py](tests/test_psql_utils.py).

## Logging and monitoring

Logging format (`--verbose`) is human-readable, not computer-readable.

The only way it can be leveraged in production is for manually inspecting the reason for the
pipeline having crashed.

It might be nice to log more qualitative metrics (e.g. number of bookings processed, number of
report rows replaced) in a more structured way (e.g. JSON logging), and set up some kind of
alerts on top of them.
