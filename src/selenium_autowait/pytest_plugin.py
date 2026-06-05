from collections.abc import Generator

import pytest

from .autowait import disable_autowait, enable_autowait


@pytest.fixture
def autowait() -> Generator[None, None, None]:
    enable_autowait()
    yield
    disable_autowait()
