from unittest.mock import Mock

import pytest

from bofa_crawler.parser import CreditCardParser, get_account_parser


@pytest.mark.parametrize(
    "account, expected_parser",
    [(Mock(account_type="CreditCard"), CreditCardParser)],
)
def test_get_account_parser(account, expected_parser):
    assert isinstance(get_account_parser(account, ""), expected_parser)
