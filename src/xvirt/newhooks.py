import pytest
from pytest import Config


@pytest.hookspec()
def pytest_xvirt_notify(event_json: str, config: Config):
    pass


@pytest.hookspec()
def pytest_xvirt_setup(config: Config):
    pass
