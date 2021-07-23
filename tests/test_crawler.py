from unittest.mock import ANY, Mock

import pytest

from bofa_crawler.crawler import BofaCrawler


def test_instantiate(get_browser):
    user = Mock()
    accounts = ["account1", "account2"]
    crawler = BofaCrawler(
        user,
        accounts,
        headless=True,
        disable_images=True,
        geckodriver_path="geckotest",
    )
    assert crawler.user == user
    assert crawler.accounts == accounts
    get_browser.assert_called_once_with(
        headless=True, disable_images=True, geckodriver_path="geckotest"
    )


def test_start(mocker, get_browser, crawler):
    sign_in = mocker.patch.object(crawler, "_sign_in", return_value=True)
    get_accounts = mocker.patch.object(crawler, "_get_accounts")
    crawler.start()
    sign_in.assert_called_once_with()
    get_accounts.assert_called_once()


def test_end(mocker, get_browser, crawler):
    browser = get_browser.return_value
    crawler.end()
    browser.quit.assert_called_once()


@pytest.fixture
def crawler(get_browser):
    user = Mock()
    accounts = ["account1", "account2"]
    return BofaCrawler(user, accounts)


@pytest.fixture
def get_browser(mocker):
    return mocker.patch("bofa_crawler.crawler.get_browser")
