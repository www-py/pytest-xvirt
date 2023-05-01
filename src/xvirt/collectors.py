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
    name: str


@dataclass()
class VItem(VNode):
    pass


@dataclass()
class VCollector(VNode):
    collectors: Dict[str, 'VCollector']
    items: Dict[str, VItem]


# VNode = List[Union[str, Dict[str, 'VNode']]]
# VNode = Dict[str, Union[List[str], str, 'VNode']]


def _rebuild_tree(nodeids: List[str]) -> Dict[str, 'VCollector']:
    """ the result is an array. One element of the array
     can be a str or a Dict
     Node = Array[ Union [str, Dict[str, Node]] ]
     """
    import re

    result = VCollector('')

    for nodeid in nodeids:
        parts = re.split('::|/', nodeid)
        key = parts[0]
        value = parts[1]
        result[key].append(value)
    return dict(result)
