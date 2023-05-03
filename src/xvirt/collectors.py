from typing import Iterable, Union

from pytest import Collector, Item


class VirtItem(Item):
    def runtest(self) -> None:
        pass

    @property
    def nodeid(self) -> str:
        return self._virt_nodeid


class VirtCollector(Collector):
    nodeid_array = []

    def collect(self) -> Iterable[Union["Item", "Collector"]]:
        items = []
        for nodeid in self.nodeid_array:
            virt_item = VirtItem.from_parent(self, name=nodeid)
            virt_item._virt_nodeid = nodeid
            items.append(virt_item)
        return items
