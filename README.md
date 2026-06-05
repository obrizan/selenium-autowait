# selenium-autowait

`selenium-autowait` adds automatic waiting to common Selenium interactions.

After autowait is enabled, Selenium waits before calling:

| Method | Wait condition |
| --- | --- |
| `WebDriver.find_element` | Until the element is found |
| `WebElement.click` | Until the element is clickable |
| `WebElement.send_keys` | Until the element is clickable |
| `WebElement.clear` | Until the element is clickable |

This is useful for tests where elements may appear, become enabled, or become
clickable shortly after the page changes.

## Table of contents

- [Installation](#installation)
- [Usage](#usage)
  - [Plain Python](#plain-python)
  - [unittest](#unittest)
  - [pytest](#pytest)
- [Analyze test results with Testinel](#analyze-test-results-with-testinel)
- [Testing](#testing)
- [Notes](#notes)
- [Disclaimer](#disclaimer)

## Installation

Install the base package from PyPI:

```bash
pip install selenium-autowait
```

Or with `uv`:

```bash
uv add selenium-autowait
```

The base package requires Python 3.11 or newer and depends on Selenium. Pytest
support is optional.

To use the bundled pytest fixture, install the pytest extra:

```bash
pip install "selenium-autowait[pytest]"
```

Or with `uv`:

```bash
uv add "selenium-autowait[pytest]"
```

## Usage

Autowait works by globally monkey-patching Selenium's `WebDriver` and
`WebElement` classes. Enable it before the Selenium interactions that should
wait automatically, and disable it when that behavior is no longer needed.

The default timeout is `10.0` seconds. To change it, pass `timeout` when
enabling autowait:

```python
from selenium_autowait import enable_autowait


enable_autowait(timeout=5.0)
```

### Plain Python

Enable autowait before interacting with Selenium elements:

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium_autowait import disable_autowait, enable_autowait


driver = webdriver.Chrome()
enable_autowait()

driver.get("https://example.com")
button = driver.find_element(By.ID, "submit")

# Will wait until the button is clickable.
button.click()
disable_autowait()
driver.quit()
```

### unittest

Enable autowait once for the test class in `setUpClass`, then disable it in
`tearDownClass`:

```python
import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium_autowait import disable_autowait, enable_autowait


class SubmitTests(unittest.TestCase):
    driver: WebDriver

    @classmethod
    def setUpClass(cls) -> None:
        enable_autowait()
        cls.driver = webdriver.Chrome()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.driver.quit()
        disable_autowait()

    def test_submit(self) -> None:
        self.driver.get("https://example.com")
        self.driver.find_element(By.ID, "submit").click()
```

### pytest

If installed with the `pytest` extra, the package exposes an `autowait` fixture
through pytest's plugin entry point. Use the fixture in tests that should wait
automatically:

```python
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver


def test_submit(driver: WebDriver, autowait: None) -> None:
    driver.get("https://example.com")
    driver.find_element(By.ID, "submit").click()
```

You can also define the fixture yourself if you prefer local control:

```python
from collections.abc import Generator

import pytest

from selenium_autowait import disable_autowait, enable_autowait


@pytest.fixture
def autowait() -> Generator[None, None, None]:
    enable_autowait(timeout=10.0)
    yield
    disable_autowait()
```

To enable autowait once for the whole pytest session, define a session-scoped
fixture in `conftest.py`:

```python
from collections.abc import Generator

import pytest

from selenium_autowait import disable_autowait, enable_autowait


@pytest.fixture(scope="session", autouse=True)
def autowait_session() -> Generator[None, None, None]:
    enable_autowait(timeout=10.0)
    yield
    disable_autowait()
```

## Analyze test results with Testinel

`selenium-autowait` helps reduce flaky Selenium failures caused by elements that
are not ready yet. When failures still happen, [Testinel](https://testinel.dev/)
can help you understand them faster.

Testinel is a web-based analytics platform for automated testing. It turns test
runs, logs, and failures into actionable reports, helping teams identify
recurring root causes, review historical stability trends, and navigate from
high-level test health to exact failing tests and logs.

Testinel supports Python, pytest, Selenium, and Playwright-based test workflows.

## Testing

Install the development dependencies with `uv`:

```bash
uv sync --group dev
```

Run the default test matrix with tox:

```bash
uv run tox
```

The tox matrix covers Python 3.11 through 3.15, pytest 8 and 9, the minimum
supported pytest version, the minimum supported Selenium version, and the latest
available Selenium version. The tests use Chrome through Selenium, so Chrome and
WebDriver support must be available on the test machine.

To run a single environment:

```bash
uv run tox -e py314-pytest9-seleniumlatest
```

Before publishing a release, run:

```bash
uv run pytest
uv run ruff check .
uv run ty check .
uv build
uvx --from twine twine check dist/*
```

## Notes

- Autowait globally monkey-patches Selenium `WebElement` and `WebDriver`
  methods.
- Call `enable_autowait()` once before using autowaited Selenium interactions.
- Calling `enable_autowait()` more than once raises `RuntimeError`.
- Calling `disable_autowait()` when autowait is not enabled raises
  `RuntimeError`.
- Passing a non-positive timeout raises `ValueError`.
- `click`, `send_keys`, and `clear` wait until the element is clickable before
  performing the original Selenium action.

## Disclaimer

Selenium is a trademark of its respective owners. `selenium-autowait` is an independent third-party plugin for Selenium and is not affiliated with, endorsed by, or sponsored by the Selenium project or its maintainers. The Selenium name is used solely to describe compatibility with Selenium.
