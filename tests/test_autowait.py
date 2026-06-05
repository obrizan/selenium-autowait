import os

import pytest
from selenium.common import (
    ElementNotInteractableException,
    InvalidElementStateException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver


def test_click(driver: WebDriver) -> None:
    driver.get(f"file://{os.path.abspath('tests/autowait.html')}")
    first_button = driver.find_element(By.ID, "first")
    second_button = driver.find_element(By.ID, "second")
    first_button.click()
    second_button.click()
    assert driver.find_element(By.ID, "placeholder").text == ""


def test_send_keys(driver: WebDriver):
    driver.get(f"file://{os.path.abspath('tests/autowait.html')}")

    third_button = driver.find_element(By.ID, "third")
    third_button.click()
    input_el = driver.find_element(By.ID, "input")

    with pytest.raises(ElementNotInteractableException):
        input_el.send_keys("hello")

    assert input_el.get_attribute("value") == ""


def test_click_auto_wait(driver: WebDriver, autowait):
    driver.get(f"file://{os.path.abspath('tests/autowait.html')}")
    first_button = driver.find_element(By.ID, "first")
    second_button = driver.find_element(By.ID, "second")
    first_button.click()
    second_button.click()
    assert driver.find_element(By.ID, "placeholder").text == "Second button works!"


def test_send_keys_auto_wait(driver: WebDriver, autowait):
    driver.get(f"file://{os.path.abspath('tests/autowait.html')}")

    third_button = driver.find_element(By.ID, "third")
    third_button.click()
    input_el = driver.find_element(By.ID, "input")
    input_el.send_keys("hello")

    assert input_el.get_attribute("value") == "hello"


def test_clear(driver: WebDriver):
    driver.get(f"file://{os.path.abspath('tests/autowait.html')}")

    fourth_button = driver.find_element(By.ID, "fourth")
    textarea_el = driver.find_element(By.ID, "textarea")
    fourth_button.click()
    with pytest.raises(InvalidElementStateException):
        textarea_el.clear()
    assert textarea_el.get_attribute("value") == "Some text which must be cleared"


def test_clear_autowait(driver: WebDriver, autowait):
    driver.get(f"file://{os.path.abspath('tests/autowait.html')}")

    fourth_button = driver.find_element(By.ID, "fourth")
    textarea_el = driver.find_element(By.ID, "textarea")
    fourth_button.click()
    textarea_el.clear()

    assert textarea_el.get_attribute("value") == ""
