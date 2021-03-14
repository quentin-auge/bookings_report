from datetime import date

import pytest

from bookings_report.transform import parse_amount_and_currency, parse_date


@pytest.mark.parametrize('raw_amount, expected', [
    pytest.param('12,34€', (12.34, '€'), id='euro_comma'),
    pytest.param('56.78€', (56.78, '€'), id='euro_dot'),
    pytest.param('123€', (123, '€'), id='euro_int'),
    pytest.param('   12,54   € ', (12.54, '€'), id='spaces'),
    pytest.param('£12.34', (12.34, '£'), id='pounds_dot'),
    pytest.param('£56.78', (56.78, '£'), id='pounds_comma'),
    pytest.param('£123', (123, '£'), id='pounds_int'),
    pytest.param(' £  56.78   ', (56.78, '£'), id='pounds_spaces')
])
def test_parse_amount_and_currency(raw_amount, expected):
    assert parse_amount_and_currency(raw_amount) == expected


@pytest.mark.parametrize('raw_amount', [
    pytest.param('12,34£', id='trailing_pounds'),
    pytest.param('€12,34', id='leading_euro'),
    pytest.param('$12,34', id='leading_dollar'),
    pytest.param('12,34$', id='trailing_dollar'),
    pytest.param('12$34', id='middle_dollar'),
    pytest.param('12,34', id='no_currency'),
])
def test_fail_parse_currency(raw_amount):
    with pytest.raises(NotImplementedError, match='unrecognized currency'):
        print('parsed =', parse_amount_and_currency(raw_amount))


@pytest.mark.parametrize('raw_amount', [
    pytest.param('£', id='no_amount'),
    pytest.param('1a3 €', id='str_amount'),
    pytest.param('£ 1.3 €', id='double_currency')
])
def test_fail_parse_amount(raw_amount):
    with pytest.raises(NotImplementedError, match='unrecognized amount'):
        print('parsed =', parse_amount_and_currency(raw_amount))


@pytest.mark.parametrize('raw_date', [
    pytest.param('21-03-2015', id='dash_date'),
    pytest.param('21/03/2015', id='slash_date')
])
def test_parse_date(raw_date):
    assert parse_date(raw_date) == date(2015, 3, 21)


@pytest.mark.parametrize('raw_date', [
    pytest.param('03-21-2015', id='dash_date'),
    pytest.param('2015/03/21', id='slash_date'),
    pytest.param('21_03_2015', id='underscore_date')
])
def test_fail_parse_date(raw_date):
    with pytest.raises(NotImplementedError, match='Cannot parse date'):
        print('parsed =', parse_date(raw_date))
