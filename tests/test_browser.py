import shutil
from unittest.mock import ANY

import pytest
from selenium.webdriver import Firefox, FirefoxOptions, FirefoxProfile

from bofa_crawler.browser import (
    GeckodriverNotFoundError,
    get_browser,
    get_geckodriver,
)


def test_get_geckodriver(mocker):
    mocker.patch.object(
        shutil, "which", side_effect=["geckodriver", None, "geckodriver.exe"]
    )
    assert get_geckodriver() == "geckodriver"
    assert shutil.which.called_with("geckodriver")

    shutil.which.reset_mock()

    assert get_geckodriver() == "geckodriver.exe"
    assert shutil.which.called_with("geckodriver")
    assert shutil.which.called_with("geckodriver.exe")


def test_raises_if_geckodriver_none(mocker):
    mocker.patch.object(shutil, "which", return_value=None)
    with pytest.raises(GeckodriverNotFoundError):
        get_geckodriver()


def test_get_browser(firefox, options, profile, mocker):
    mocker.patch(
        "bofa_crawler.browser.get_geckodriver", return_value="geckotest"
    )
    assert isinstance(get_browser(), Firefox)
    firefox.assert_called_once_with(
        options=options.return_value,
        firefox_profile=profile.return_value,
        executable_path="geckotest",
    )


def test_get_browser_with_geckodriver_path(firefox, options, profile):
    get_browser(geckodriver_path="geckotest")
    firefox.assert_called_once_with(
        options=ANY, firefox_profile=ANY, executable_path="geckotest"
    )


def test_get_browser_headless(firefox, options):
    get_browser(headless=True)
    options.return_value.add_argument.assert_called_with("-headless")


def test_get_browser_disable_images(firefox, profile):
    get_browser(disable_images=True)
    profile.return_value.set_preference.assert_called_once_with(
        "permissions.default.image", 2
    )


@pytest.fixture(name="firefox")
def patched_firefox(mocker):
    return mocker.patch("bofa_crawler.browser.Firefox", spec_set=Firefox)


@pytest.fixture(name="options")
def patched_firefox_options(mocker):
    return mocker.patch(
        "bofa_crawler.browser.FirefoxOptions", spec_set=FirefoxOptions
    )


@pytest.fixture(name="profile")
def patched_firefox_profile(mocker):
    return mocker.patch(
        "bofa_crawler.browser.FirefoxProfile", spec_set=FirefoxProfile
    )
