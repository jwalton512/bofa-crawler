from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as ec


class text_to_be_present_in_element(object):
    """Expectation that given text is present within the specified element."""

    def __init__(self, locator, text_):
        self.locator = locator
        self.text = text_

    def __call__(self, driver):
        try:
            element = ec._find_element(driver, self.locator)
            element_text = element.text
            element_inner_text = element.get_attribute("innerText")
            return (self.text in element_text) or (
                self.text in element_inner_text
            )
        except StaleElementReferenceException:
            return False
