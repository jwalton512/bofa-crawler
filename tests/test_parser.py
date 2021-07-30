from unittest.mock import Mock

import pytest

from bofa_crawler.bank import Account
from bofa_crawler.parser import (
    CreditCardParser,
    DepositParser,
    get_account_parser,
)


@pytest.mark.parametrize(
    "account_type, expected_parser",
    [("CreditCard", CreditCardParser), ("Deposit", DepositParser)],
)
def test_get_account_parser(account_type, expected_parser):
    account = Mock(spec=Account, account_type=account_type)
    assert isinstance(get_account_parser(account, ""), expected_parser)
