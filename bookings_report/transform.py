from datetime import date, datetime
from typing import Tuple


def parse_amount_and_currency(raw_amount: str) -> Tuple[float, str]:
    """
    Parse raw amount string into float amount and currency.

    Args:
        raw_amount: raw amount string

    Returns:
        Amount and currency

    Raises:
        :exc:`NotImplementedError` on invalid currency (not ending with `€` or starting with `£`).
        :exc:`NotImplementedError` on invalid amount (comma and dot decimal separator accepted).

    Examples:
        >>> parse_amount_and_currency('12,34 €')
        (12.34, '€')

        >>> parse_amount_and_currency('£12.34')
        (12.34, '£')
    """

    raw_amount = raw_amount.strip()

    error_msg = f"Cannot parse amount '{raw_amount}'"

    # Parse currencu

    if raw_amount.startswith('£'):
        currency = '£'
        raw_amount = raw_amount[1:]

    elif raw_amount.endswith('€'):
        currency = '€'
        raw_amount = raw_amount[:-1]

    else:
        raise NotImplementedError(f'{error_msg}: unrecognized currency')

    # Parse amount

    try:
        amount = float(raw_amount.replace(',', '.'))
    except ValueError:
        raise NotImplementedError(f"{error_msg}: unrecognized amount '{raw_amount}'")

    return amount, currency


def parse_date(raw_date: str) -> date:
    """
    Parse '%d-%m-%Y' and '%d/%m/%Y' formatted dates indifferently.

    Args:
        raw_date: raw date string

    Returns:
        Parsed date

    Raises:
        :exc:`NotImplementedError` on invalid date format.

    Examples:
        >>> parse_amount_and_currency('21/03/2015')
        date(2015, 3, 21)

        >>> parse_amount_and_currency('21-03-2015')
        date(2015, 3, 21)
    """

    raw_date = raw_date.strip()

    try:
        parsed_date = datetime.strptime(raw_date, '%d-%m-%Y').date()
    except ValueError:
        try:
            parsed_date = datetime.strptime(raw_date, '%d/%m/%Y').date()
        except:
            raise NotImplementedError(f"Cannot parse date '{raw_date}' as '%d-%m-%Y' or '%d/%m/%Y'")

    return parsed_date
