class User:
    def __init__(
        self, online_id: str, passcode: str, security_responses: dict = None
    ):
        self.online_id = online_id
        self.passcode = passcode
        self.security_responses = security_responses
        self.accounts: list[Account] = []


class Account:
    def __init__(self, name: str, account_type: str, link: str):
        self.name = name
        self.account_type = account_type
        self.link = link
        self.balance: int = None
        self.transactions: list[Transaction] = None

    def __str__(self):
        transaction_count = len(self.transactions) if self.transactions else 0
        return "<Account ({}) {}, {}, {} transactions>".format(
            self.account_type, self.name, self.balance, transaction_count
        )


class Transaction:
    def __init__(
        self,
        description: str,
        amount: int,
        is_pending: bool = False,
        ending_balance: int = None,
    ):
        self.description = description
        self.amount = amount
        self.is_pending = is_pending
        self.ending_balance = ending_balance
