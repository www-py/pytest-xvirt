from typing import Optional, Iterable, Union
import pytest
from pytest import Collector, Item


class MockItem(Item):
    def runtest(self) -> None:
        pass


class MockCollector(Collector):

    def collect(self) -> Iterable[Union["Item", "Collector"]]:
        def m(name):
            return MockItem.from_parent(self, name=name)

        return [m('test_a'), m('test_b')]

    @property
    def nodeid(self) -> str:
        return "test_transport.py"
