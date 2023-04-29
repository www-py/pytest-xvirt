import pytest

from xvirt.events import Evt
from pytest import Config


@pytest.hookspec()
def pytest_xvirt_notify(event: Evt, config: Config):
    pass
