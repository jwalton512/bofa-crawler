import shutil

from selenium.webdriver import Firefox, FirefoxOptions, FirefoxProfile


class GeckodriverNotFoundError(Exception):
    """Raised when geckodriver path cannot be found."""


def get_geckodriver():
    """Get path for geckodriver binary."""
    gecko_path = shutil.which("geckodriver") or shutil.which("geckodriver.exe")
    if gecko_path:
        return gecko_path

    raise (GeckodriverNotFoundError)


def get_browser(
    headless=False, disable_images=False, geckodriver_path: str = None
):
    """Get a new webdriver instance."""
    options = FirefoxOptions()
    profile = FirefoxProfile()

    if headless:
        options.add_argument("-headless")

    if disable_images:
        profile.set_preference("permissions.default.image", 2)

    driver = geckodriver_path or get_geckodriver()

    browser = Firefox(
        options=options,
        firefox_profile=profile,
        executable_path=driver,
    )
    return browser
