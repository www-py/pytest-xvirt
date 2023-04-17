import pytest

from xvirt.events import Evt


@pytest.hookspec()
def pytest_xvirt_notify(event: Evt):
    pass
