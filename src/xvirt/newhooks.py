from typing import List, Callable

import pytest

from xvirt.events import Evt
from pytest import Config


@pytest.hookspec()
def pytest_xvirt_notify(event: Evt, config: Config):
    pass


@pytest.hookspec()
def pytest_xvirt_setup(config: Config):
    pass
