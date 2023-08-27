import pytest

from .events import EvtCollectReportFail, EvtCollectionFinish, EvtRuntestLogreport, EvtRemoteFinished


class XvirtPluginRemote:

    def __init__(self, config) -> None:
        self._config = config
        self._events_index = 0

    @pytest.hookimpl
    def pytest_collection_finish(self, session: pytest.Session):
        # if session.config.option.xvirt_mode == mode_controlled:
        self._send(EvtCollectionFinish([item.nodeid for item in session.items]))

    @pytest.hookimpl
    def pytest_runtest_logreport(self, report):
        if report.when != 'call':
            return
        self._send(EvtRuntestLogreport(self._pytest_serialize(report)))

    @pytest.hookimpl
    def pytest_collectreport(self, report):
        if report.outcome != 'failed':
            return
        self._send(EvtCollectReportFail(self._pytest_serialize(report)))

    @pytest.hookimpl
    def pytest_sessionfinish(self):
        self._send(EvtRemoteFinished())

    def _pytest_serialize(self, report):
        data = self._config.hook.pytest_report_to_serializable(config=self._config, report=report)
        return data

    def _send(self, event):
        self._events_index += 1
        self._config.hook.pytest_xvirt_send_event(event_json=event.to_json(self._events_index), config=self._config)
