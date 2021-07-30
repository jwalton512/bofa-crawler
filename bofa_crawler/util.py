import re
from time import sleep

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from bofa_crawler.expected_conditions import text_to_be_present_in_element


def get_current_url(browser: Firefox):
    """Get URL of the loaded webpage."""
    try:
        return browser.execute_script("return window.location.href")
    except WebDriverException:
        try:
            return browser.current_url
        except WebDriverException:
            return None


def navigate(browser: Firefox, link: str):
    """Navigates to `link` if `link` does not match current url."""
    current_url = get_current_url(browser)
    total_timeouts = 0

    if current_url is not None and current_url.endswith("/"):
        current_url = current_url[:-1]

    link_compare = link[:-1] if link.endswith("/") else link

    if current_url is None or current_url != link_compare:
        while True:
            try:
                browser.get(link)
                sleep(2)
                break
            except TimeoutException as e:
                if total_timeouts >= 7:
                    raise TimeoutException(
                        "Retried {} times to GET '{}' webpage "
                        "but failed out of a timeout!\n\t{}".format(
                            total_timeouts,
                            str(link).encode("utf-8"),
                            str(e).encode("utf-8"),
                        )
                    )

                total_timeouts += 1
                sleep(2)


def wait(browser: Firefox, condition, timeout: int = 10):
    """Wait a maximum of `timeout` seconds until condition is met."""
    try:
        result = WebDriverWait(browser, timeout).until(condition)
    except TimeoutException:
        return False

    return result


def wait_until(
    browser: Firefox,
    ec_params,
    condition_type: str = "POEL",
    timeout: int = 10,
):
    """Wait a maximum of `timeout` seconds until condition is met."""

    def get_locator_from_ec_params(ec_params):
        elem_address, find_method = ec_params
        find_by = (
            By.XPATH
            if find_method == "XPath"
            else By.CLASS_NAME
            if find_method == "CLASS"
            else By.CSS_SELECTOR
        )
        return (find_by, elem_address)

    if not isinstance(ec_params, list):
        ec_params = [ec_params, None]

    if condition_type == "VOEL":
        locator = get_locator_from_ec_params(ec_params)
        condition = ec.visibility_of_element_located(locator)

    elif condition_type == "POEL":
        locator = get_locator_from_ec_params(ec_params)
        condition = ec.presence_of_element_located(locator)

    elif condition_type == "CLICK":
        locator = get_locator_from_ec_params(ec_params)
        condition = ec.element_to_be_clickable(locator)

    elif condition_type == "PFL":

        def condition(driver):
            return driver.execute_script("return document.readyState") in [
                "complete" or "loaded"
            ]

    elif condition_type == "TC":
        search, _ = ec_params
        condition = ec.title_contains(search)

    elif condition_type == "TPE":
        selector, search, *_ = ec_params
        by = _[0] if len(_) else None
        locator = get_locator_from_ec_params((selector, by))
        condition = text_to_be_present_in_element(locator, search)

    return wait(browser, condition, timeout)


def dollars_to_cents(dollars) -> int:
    """Convert dollars to cents."""
    if isinstance(dollars, str):
        dollars = re.sub("[^0-9-.]", "", dollars)

    return int(float(dollars) * 100)


def html_whitespace(text: str) -> str:
    """Return `text` with whitepsace treated as it would be in HTML."""
    return re.sub("\s+", " ", text.strip())  # noqa: W605
