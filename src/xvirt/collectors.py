from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional, Iterable, Union, List, Dict
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
        return "mock_test.py"


class VirtItem(Item):
    def runtest(self) -> None:
        pass

    @property
    def nodeid(self) -> str:
        return self._virt_nodeid


class VirtCollector(Collector):

    def collect(self) -> Iterable[Union["Item", "Collector"]]:
        # _rebuild_tree(self.nodeid_array)
        # raise Exception(self.nodeid_array)
        items = []
        for nodeid in self.nodeid_array:
            virt_item = VirtItem.from_parent(self, name=nodeid)
            virt_item._virt_nodeid = nodeid
            items.append(virt_item)
        return items

    @property
    def nodeid(self) -> str:
        return 'should-not-be-used-1'

