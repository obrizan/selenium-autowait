from collections.abc import Generator

import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from selenium_autowait import disable_autowait, enable_autowait


@pytest.fixture(autouse=True)
def restore_autowait() -> Generator[None, None, None]:
    try:
        disable_autowait()
    except RuntimeError:
        pass
    yield
    try:
        disable_autowait()
    except RuntimeError:
        pass


def test_enable_autowait_patches_and_disable_restores_original_methods() -> None:
    original_click = WebElement.click
    original_send_keys = WebElement.send_keys
    original_clear = WebElement.clear
    original_find_element = WebDriver.find_element

    enable_autowait()

    assert WebElement.click is not original_click
    assert WebElement.send_keys is not original_send_keys
    assert WebElement.clear is not original_clear
    assert WebDriver.find_element is not original_find_element

    disable_autowait()

    assert WebElement.click is original_click
    assert WebElement.send_keys is original_send_keys
    assert WebElement.clear is original_clear
    assert WebDriver.find_element is original_find_element


def test_enable_autowait_twice_raises_runtime_error() -> None:
    enable_autowait()

    with pytest.raises(RuntimeError, match="Autowait already enabled"):
        enable_autowait()


def test_disable_autowait_before_enable_raises_runtime_error() -> None:
    with pytest.raises(RuntimeError, match="Autowait is not enabled"):
        disable_autowait()


@pytest.mark.parametrize("timeout", [0, -1, -0.5])
def test_enable_autowait_rejects_non_positive_timeout(timeout: float) -> None:
    with pytest.raises(ValueError, match="greater than 0"):
        enable_autowait(timeout=timeout)
