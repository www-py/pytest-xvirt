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

        return [m('test_1'), m('test_1')]

    @property
    def nodeid(self) -> str:
        return "mock_test.py"


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
