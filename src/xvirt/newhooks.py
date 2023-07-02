from typing import List, Callable

import pytest

from xvirt.events import Evt
from pytest import Config


@pytest.hookspec()
def pytest_xvirt_notify(event: Evt, config: Config):
    pass


@pytest.hookspec()
def pytest_xvirt_setup(xvirt_packages: List[str], config: Config):
    pass


@pytest.hookspec()
def pytest_xvirt_collect_file(file_path, path, parent, events_handler: Callable[[Callable[[], str]], None]):
    pass
