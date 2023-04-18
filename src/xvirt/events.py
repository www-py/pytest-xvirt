from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass
from typing import List, Any, Dict


def _class_fullname(c):
    return c.__module__ + '.' + c.__qualname__


@dataclass()
class Evt:

    def to_json(self) -> str:
        values = dataclasses.asdict(self)
        values['class='] = _class_fullname(self.__class__)
        json_string = json.dumps(values)
        return json_string

    @staticmethod
    def from_json(json_string: str) -> 'Evt':
        def object_hook(d: dict) -> any:
            class_fullname = d.pop('class=', '')
            if class_fullname == '': return d
            constructor = _evt_constructor(class_fullname)
            instance = constructor(**d)
            return instance

        return json.loads(json_string, object_hook=object_hook)


@dataclass()
class EvtCollectionFinish(Evt):
    node_ids: List[str]


@dataclass()
class EvtRuntestLogreport(Evt):
    data: Dict[str, Any]


_evt_constructor_dict = {}


def _evt_constructor(class_fullname: str):
    try:
        return _evt_constructor_dict[class_fullname]
    except KeyError:
        module_name, class_name = class_fullname.rsplit('.', 1)
        assert module_name == __name__
        constructor = globals().get(class_name, None)
        if constructor is None or not issubclass(constructor, Evt):
            raise Exception(f'Unsupported deserialization of {class_fullname}')
        _evt_constructor_dict[class_fullname] = constructor
        return constructor
