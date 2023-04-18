import pytest

from xvirt.events import Evt
from pytest import Session


@pytest.hookspec()
def pytest_xvirt_notify(event: Evt, session: Session):
    pass
