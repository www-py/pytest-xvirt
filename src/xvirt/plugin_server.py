from pathlib import Path

import pytest

from xvirt import XVirt
from xvirt.events import EvtCollectionFinish, EvtRuntestLogreport, Evt, EvtCollectReportFail, EvtRemoteFinished


class XvirtPluginServer:

    def __init__(self, xvirt_instance: XVirt, config, xvirt_package) -> None:
        self._xvirt_instance = xvirt_instance
        self._config = config
        self._xvirt_collect_file_done = False
        self._xvirt_package = xvirt_package
        self._report_map = {}
        self._report_nodeid_set = set()
        self._remote_finished = False

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

        return self._events_handler(file_path, parent)

    def pytest_collection_finish(self, session: pytest.Session):

        pass
        # for rep in self._report_buffer:
        #     self._config.hook.pytest_runtest_logreport(report=rep)

    def pytest_runtest_makereport(self, item):
        if item.nodeid not in self._report_nodeid_set:
            return None
        self._wait_all_remote()
        return self._report_map.pop(item.nodeid, None)

    def is_xvirt_package(self, path):
        if self._xvirt_package == '':
            return False
        str_path = str(path)
        return str_path.startswith(self._xvirt_package)

    def _events_handler(self, file_path, parent):
        config = parent.config

        def re():
            while True:
                event = self._xvirt_instance.recv_event()
                if event is None:
                    yield None
                yield Evt.from_json(event)

        recv_event = _order(re())
        self._recv_event = recv_event

        evt_cf = next(recv_event)
        if evt_cf is None:  # this means that the user did not implement the remote side
            return None

        if isinstance(evt_cf, EvtCollectReportFail):
            rep = config.hook.pytest_report_from_serializable(config=config, data=evt_cf.data)
            config.hook.pytest_collectreport(report=rep)
            self._xvirt_instance.finalize()
            return None

        assert isinstance(evt_cf, EvtCollectionFinish)
        from xvirt.collectors import VirtCollector
        result = VirtCollector.from_parent(parent, name=file_path.name)
        result.nodeid_array = evt_cf.node_ids
        self._report_nodeid_set = set(evt_cf.node_ids)
        self._wait_all_remote()
        return result

    def _wait_all_remote(self):
        if self._remote_finished:
            return
        self._remote_finished = True

        while True:
            evt_rep = next(self._recv_event)
            if isinstance(evt_rep, EvtRemoteFinished):
                break
            assert isinstance(evt_rep, EvtRuntestLogreport)
            rep = self._config.hook.pytest_report_from_serializable(config=self._config, data=evt_rep.data)
            self._config.hook.pytest_runtest_logreport(report=rep)
            if rep.outcome == 'failed':
                self._report_map[rep.nodeid] = rep

        self._xvirt_instance.finalize()


def _order(source):
    buffer = {}
    expected_index = 1

    for item in source:
        if item is None:
            yield None
            continue

        if item.index < expected_index:
            raise Exception(f'index={item.index} < expected_index={expected_index}')

        if item.index in buffer:
            raise Exception(f'index={item.index} already in buffer')

        buffer[item.index] = item

        while expected_index in buffer:
            print(f'yielding event {expected_index} available: {buffer.keys()}')
            yield buffer.pop(expected_index)
            expected_index += 1
