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


@dataclass()
class VNode:
    nodeid: str


@dataclass()
class VItem(VNode):
    pass


@dataclass()
class VCollector(VNode):
    collectors: Dict[str, 'VCollector'] = field(default_factory=dict)
    items: List[VItem] = field(default_factory=list)

    def collector(self, nodeid: str) -> 'VCollector':
        result = self.collectors.get(nodeid, None)
        if result is not None:
            return result

        result = VCollector(nodeid)
        self.collectors[nodeid] = result
        return result


def _rebuild_tree(nodeids: List[str]) -> Dict[str, VCollector]:
    root = VCollector('')

    for nodeid in nodeids:
        (key, value) = nodeid.split('::', 1)
        path = key.split('/')
        collector = root
        for idx in range(len(path)):
            collector_nodeid = '/'.join(path[:idx + 1])
            collector = collector.collector(collector_nodeid)

        collector.items.append(VItem(nodeid))

    return root.collectors
