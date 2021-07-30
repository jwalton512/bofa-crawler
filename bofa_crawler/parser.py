from abc import ABC, abstractmethod

from bs4 import BeautifulSoup
from bs4.element import PageElement

from bofa_crawler.bank import Account, Transaction
from bofa_crawler.constants import SECURE_BASE_URL
from bofa_crawler.util import dollars_to_cents, html_whitespace


class HtmlParser(ABC):
    def __init__(self, page_source: str):
        self.soup = BeautifulSoup(page_source, "html.parser")


class AccountListParser(HtmlParser):
    """Get bank accounts from desired `accounts`."""

    def get_accounts(self, accounts):
        """Get accounts."""
        user_accounts = []
        account_item_elems = self.soup.select(".Accounts .AccountItem")
        for account_item_elem in account_item_elems:
            name_elem = account_item_elem.select_one(".AccountName > a")
            name = html_whitespace(name_elem.text) if name_elem else None
            if name in accounts:
                account_type = self._get_account_type(account_item_elem)
                link = SECURE_BASE_URL + name_elem.get("href")
                account = Account(name, account_type, link)
                user_accounts.append(account)

        return user_accounts

    def _get_account_type(self, account_item: PageElement):
        account_class_map = {
            "AccountItemDeposit": "Deposit",
            "AccountItemCreditCard": "CreditCard",
        }

        for account_class, account_type in account_class_map.items():
            if account_class in account_item["class"]:
                return account_type


class AccountParser(HtmlParser, ABC):
    def __init__(self, account: Account, page_source: str):
        super().__init__(page_source)
        self.account = account

    @abstractmethod
    def get_balance(self):
        """Retrieve account balance."""
        pass

    @abstractmethod
    def get_transactions(self):
        """Retrieve recent transactions."""
        pass


class CreditCardParser(AccountParser):
    def __init__(self, account: Account, page_source: str):
        super().__init__(account, page_source)
        # Load transactions now because pending transactions are used
        # for determining pending balance
        self.transactions = self._get_transactions()

    def get_transactions(self):
        """Retrieve recent transactions."""
        return self.transactions

    def get_balance(self):
        """Retrieve account balance."""
        pending_balance = self._get_pending_balance()
        return pending_balance or self._get_current_balance()

    def _get_transactions(self):
        transactions = []
        trans_row_elems_selector = "table#transactions > tbody > tr"
        trans_row_elems = self.soup.select(trans_row_elems_selector)
        for trans_row in trans_row_elems:
            is_pending = "trans-pending-row" in trans_row["class"]
            amount = self._get_transaction_amount(trans_row)
            description = self._get_transaction_description(trans_row)
            ending_balance = self._get_transaction_ending_balance(trans_row)
            transaction = Transaction(
                description, amount, is_pending, ending_balance
            )
            transactions.append(transaction)

        return transactions

    def _get_transaction_amount(self, trans_row: PageElement):
        selector = ".trans-amount-cell"
        elem = trans_row.select_one(selector)
        if elem:
            return dollars_to_cents(elem.text)

    def _get_transaction_description(self, trans_row: PageElement):
        selector = ".trans-desc-cell > a > span"
        elem = trans_row.select_one(selector).next_sibling
        if elem:
            return elem.strip()

    def _get_transaction_ending_balance(self, trans_row: PageElement):
        selector = ".trans-balance-cell"
        elem = trans_row.select_one(selector)
        if elem:
            return dollars_to_cents(elem.text)

    def _get_current_balance(self):
        cur_bal_selector = ".summary-details-row .summary-acct-row .TL_NPI_L1"
        cur_bal_elem = self.soup.select_one(cur_bal_selector)
        if cur_bal_elem:
            return dollars_to_cents(cur_bal_elem.text)

    def _get_pending_balance(self):
        if self.transactions:
            transaction = self.transactions[0]
            if transaction.is_pending:
                return transaction.ending_balance


class DepositParser(AccountParser):
    def get_balance(self):
        """Retrieve account balance."""
        balance_selector = ".ad-acct-summary-module-deposit-skin .TL_NPI_Amt"
        balance_elem = self.soup.select_one(balance_selector)
        if balance_elem:
            return dollars_to_cents(balance_elem.text)

    def get_transactions(self):
        """Retrieve recent transactions."""

        def is_transaction(class_):
            return class_ in ["record", "in-transit-record"]

        transactions = []
        trans_table = self.soup.select_one("table.transaction-records > tbody")
        trans_row_elems = trans_table.find_all("tr", class_=is_transaction)
        for trans_row in trans_row_elems:
            is_pending = "in-transit-record" in trans_row["class"]
            amount = self._get_transaction_amount(trans_row)
            description = self._get_transaction_description(trans_row)
            ending_balance = self._get_transaction_ending_balance(trans_row)
            transaction = Transaction(
                description, amount, is_pending, ending_balance
            )
            transactions.append(transaction)

        return transactions

    def _get_transaction_amount(self, trans_row: PageElement):
        selector = "td.amount"
        elem = trans_row.select_one(selector)
        if elem:
            return dollars_to_cents(elem.text)

    def _get_transaction_description(self, trans_row: PageElement):
        selector = "td.description"
        elem = trans_row.select_one(selector)
        if elem:
            return elem.text.strip()

    def _get_transaction_ending_balance(self, trans_row: PageElement):
        selector = "td.balance"
        elem = trans_row.select_one(selector)
        if elem:
            return dollars_to_cents(elem.text)


def get_account_parser(account: Account, page_source: str):
    """Get parser instance for the account based on type."""
    parsers = {"CreditCard": CreditCardParser, "Deposit": DepositParser}

    return parsers[account.account_type](account, page_source)
