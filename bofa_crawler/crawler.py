from selenium.webdriver.common.keys import Keys

from bofa_crawler.bank import User
from bofa_crawler.browser import get_browser
from bofa_crawler.constants import BOFA_SIGN_IN_URL
from bofa_crawler.parser import AccountListParser, get_account_parser
from bofa_crawler.util import navigate, wait_until


class BofaCrawler:
    def __init__(
        self,
        user: User,
        accounts: list,
        headless: bool = False,
        disable_images: bool = False,
        geckodriver_path: str = None,
    ):
        self.user = user
        self.accounts = accounts
        self.browser = get_browser(
            headless=headless,
            disable_images=disable_images,
            geckodriver_path=geckodriver_path,
        )

    def start(self):
        """Begin crawling."""
        if self._sign_in():
            self._get_accounts()

    def end(self):
        """End crawling."""
        self.browser.quit()

    def _sign_in(self):
        """Attempt to sign in using user credentials."""
        # TODO: handle security questions if prompted
        try:
            navigate(self.browser, BOFA_SIGN_IN_URL)

            oid = wait_until(self.browser, "#oid")
            oid.send_keys(self.user.online_id)

            passcode = wait_until(self.browser, "#pass", "CLICK")
            passcode.send_keys(self.user.passcode)
            passcode.send_keys(Keys.RETURN)

            wait_until(self.browser, "div.Accounts", "VOEL")
        except Exception:
            return False

        return True

    def _get_accounts(self):
        account_list_parser = AccountListParser(self.browser.page_source)
        self.user.accounts.extend(
            account_list_parser.get_accounts(self.accounts)
        )

        self._get_user_accounts_detail()

    def _get_user_accounts_detail(self):
        for account in self.user.accounts:
            self.browser.get(account.link)
            name_selector = (
                "a[name='page_title_acct_switcher'] > span:nth-child(2)"
            )
            if not wait_until(
                self.browser, [name_selector, account.name], "TPE"
            ):
                return
            parser = get_account_parser(account, self.browser.page_source)
            account.balance = parser.get_balance()
            account.transactions = parser.get_transactions()
