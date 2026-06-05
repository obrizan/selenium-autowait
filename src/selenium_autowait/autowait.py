"""Global Selenium monkey patches that add waits to common interactions."""

from collections.abc import Callable
from typing import Any

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

ClickMethod = Callable[[WebElement], None]
SendKeysMethod = Callable[..., None]
ClearMethod = Callable[[WebElement], None]
FindElementMethod = Callable[[WebDriver, str, str | None], WebElement]

_original_click: ClickMethod | None = None
_original_send_keys: SendKeysMethod | None = None
_original_clear: ClearMethod | None = None
_original_find_element: FindElementMethod | None = None


def _ensure_enabled() -> tuple[
    ClickMethod, SendKeysMethod, ClearMethod, FindElementMethod
]:
    if (
        _original_click is None
        or _original_send_keys is None
        or _original_clear is None
        or _original_find_element is None
    ):
        msg = "Autowait is not enabled."
        raise RuntimeError(msg)
    return (
        _original_click,
        _original_send_keys,
        _original_clear,
        _original_find_element,
    )


def patched_click_factory(timeout: float) -> ClickMethod:
    """Create a click method that waits until the element is clickable."""

    def patched_click(self: WebElement) -> None:
        driver = self.parent
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(self))
        original_click, _, _, _ = _ensure_enabled()
        original_click(self)

    return patched_click


def patched_send_keys_factory(timeout: float) -> SendKeysMethod:
    """Create a send_keys method that waits until the element is clickable."""

    def patched_send_keys(self: WebElement, *value: Any, **kwargs: Any) -> None:
        driver = self.parent
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(self))
        _, original_send_keys, _, _ = _ensure_enabled()
        original_send_keys(self, *value, **kwargs)

    return patched_send_keys


def patched_clear_factory(timeout: float) -> ClearMethod:
    """Create a clear method that waits until the element is clickable."""

    def patched_clear(self: WebElement) -> None:
        driver = self.parent
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(self))
        _, _, original_clear, _ = _ensure_enabled()
        original_clear(self)

    return patched_clear


def patched_find_element_factory(timeout: float) -> FindElementMethod:
    """Create a find_element method that waits until the element is found."""

    def patched_find_element(
        self: WebDriver, by: str = By.ID, value: str | None = None
    ) -> WebElement:
        return WebDriverWait(self, timeout).until(
            lambda driver: _ensure_enabled()[3](driver, by, value)
        )

    return patched_find_element


def enable_autowait(timeout: float = 10.0) -> None:
    """Enable automatic waiting globally for supported Selenium interactions."""
    global _original_clear
    global _original_click
    global _original_find_element
    global _original_send_keys

    if timeout <= 0:
        msg = "Autowait timeout must be greater than 0."
        raise ValueError(msg)
    if (
        _original_click is not None
        or _original_send_keys is not None
        or _original_clear is not None
        or _original_find_element is not None
    ):
        msg = "Autowait already enabled."
        raise RuntimeError(msg)

    _original_click = WebElement.click
    _original_send_keys = WebElement.send_keys
    _original_clear = WebElement.clear
    _original_find_element = WebDriver.find_element

    setattr(WebElement, "click", patched_click_factory(float(timeout)))
    setattr(WebElement, "send_keys", patched_send_keys_factory(float(timeout)))
    setattr(WebElement, "clear", patched_clear_factory(float(timeout)))
    setattr(WebDriver, "find_element", patched_find_element_factory(float(timeout)))


def disable_autowait() -> None:
    """Disable autowait and restore the original Selenium methods."""
    global _original_clear
    global _original_click
    global _original_find_element
    global _original_send_keys

    original_click, original_send_keys, original_clear, original_find_element = (
        _ensure_enabled()
    )

    setattr(WebElement, "click", original_click)
    setattr(WebElement, "send_keys", original_send_keys)
    setattr(WebElement, "clear", original_clear)
    setattr(WebDriver, "find_element", original_find_element)

    _original_click = None
    _original_send_keys = None
    _original_clear = None
    _original_find_element = None
