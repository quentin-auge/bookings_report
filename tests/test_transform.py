import pytest

from bookings_report.transform import parse_amount_and_currency


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
        print('parseed =', parse_amount_and_currency(raw_amount))


@pytest.mark.parametrize('raw_amount', [
    pytest.param('£', id='no_amount'),
    pytest.param('1a3 €', id='str_amount'),
    pytest.param('£ 1.3 €', id='double_currency')
])
def test_fail_parse_amount(raw_amount):
    with pytest.raises(NotImplementedError, match='unrecognized amount'):
        print('parseed =', parse_amount_and_currency(raw_amount))
