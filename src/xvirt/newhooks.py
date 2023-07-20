import pytest
from pytest import Config

from xvirt.events import Evt


@pytest.hookspec()
def pytest_xvirt_notify(event: Evt, config: Config):
    pass


@pytest.hookspec()
def pytest_xvirt_setup(config: Config):
    pass
