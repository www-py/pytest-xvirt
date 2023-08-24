from pathlib import Path

import pytest

from xvirt import XVirt
from xvirt.events import EvtCollectionFinish, EvtRuntestLogreport, Evt


class XvirtPluginServer:

    def __init__(self, xvirt_instance: XVirt, config, xvirt_package) -> None:
        self._xvirt_instance = xvirt_instance
        self._config = config
        self._xvirt_collect_file_done = False
        self._xvirt_package = xvirt_package

    @pytest.hookimpl
    def pytest_pycollect_makemodule(self, module_path, path, parent):
        if self.is_xvirt_package(module_path.parent):
            empty = Path(__file__).parent / 'empty'
            return pytest.Module.from_parent(parent, fspath=empty)

    @pytest.hookimpl
    def pytest_collect_file(self, file_path: Path, path, parent):

        if not self.is_xvirt_package(file_path):
            return None

        if self._xvirt_collect_file_done:
            return

        self._xvirt_collect_file_done = True

        self._xvirt_instance.run()
        evt_handler_fun = _make(file_path, parent)
        return evt_handler_fun(self._xvirt_instance)

    def is_xvirt_package(self, path):
        if self._xvirt_package == '':
            return False
        str_path = str(path)
        return str_path.startswith(self._xvirt_package)


def _order_events2(xvirt_instance: XVirt):
    def re():
        event = xvirt_instance.recv_event()
        if event is None:
            return None
        return Evt.from_json(event)

    events = []
    while True:
        evt = re()
        if evt is None:
            yield None
            return

        if isinstance(evt, EvtCollectionFinish):
            yield evt
            break
        else:
            events.append(evt)

    for evt in events:
        yield evt

    while True:
        yield re()


def _make(file_path, parent):
    def events_handler(xvirt_instance: XVirt):

        recv_event = _order_events2(xvirt_instance)
        evt_cf = next(recv_event)
        if evt_cf is None:  # this means that the user did not implement the remote side
            return None

        from xvirt.collectors import VirtCollector
        result = VirtCollector.from_parent(parent, name=file_path.name)
        result.nodeid_array = evt_cf.node_ids

        # report phase
        config = parent.config
        recv_count = 0
        while recv_count < len(evt_cf.node_ids):
            evt_rep = next(recv_event)
            assert isinstance(evt_rep, EvtRuntestLogreport)
            rep = config.hook.pytest_report_from_serializable(config=config, data=evt_rep.data)
            config.hook.pytest_runtest_logreport(report=rep)
            recv_count += 1

        xvirt_instance.finalize()
        return result

    return events_handler
