from unittest.mock import MagicMock, PropertyMock

import pytest
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver import Firefox

from bofa_crawler.util import dollars_to_cents, get_current_url, navigate


def test_get_current_url_using_execute_script():
    browser = MagicMock(spec_set=Firefox)
    browser.execute_script.return_value = "foo"
    assert get_current_url(browser) == "foo"


def test_get_current_url_using_browser_property():
    browser = MagicMock(spec_set=Firefox)
    browser.execute_script.side_effect = WebDriverException
    browser.current_url = "bar"
    assert get_current_url(browser) == "bar"


def test_get_current_url_returns_none_if_none():
    browser = MagicMock(spec_set=Firefox)
    browser.execute_script.side_effect = WebDriverException
    type(browser).current_url = PropertyMock(side_effect=WebDriverException)
    assert get_current_url(browser) is None


def test_navigate_browses_to_url(sleep):
    browser = MagicMock(spec_set=Firefox)
    navigate(browser, "http://example.test")
    browser.get.assert_called_once_with("http://example.test")


@pytest.mark.parametrize(
    "navigate_url, current_url",
    [
        ("example", "example"),
        ("slash", "slash/"),
        ("slash/", "slash"),
    ],
)
def test_navigate_does_nothing_if_url_matches_current(
    mocker, navigate_url, current_url
):
    browser = MagicMock(spec_set=Firefox)
    mocker.patch("bofa_crawler.util.get_current_url", return_value=current_url)
    navigate(browser, navigate_url)
    browser.get.assert_not_called()


def test_navigate_raises_exception_after_7_timeouts(sleep):
    browser = MagicMock(spec_set=Firefox)
    browser.get.side_effect = TimeoutException

    with pytest.raises(TimeoutException, match="Retried 7 times"):
        navigate(browser, "test")

    assert browser.get.call_count == 8
    assert sleep.call_count == 7


@pytest.mark.parametrize(
    "input, expected",
    [
        (7.92, 792),
        ("7.92", 792),
        ("$7.92", 792),
        ("$7,000.42", 700042),
        ("-$700", -70000),
    ],
)
def test_dollars_to_cents(input, expected):
    assert dollars_to_cents(input) == expected


@pytest.fixture
def sleep(mocker):
    return mocker.patch("bofa_crawler.util.sleep")
