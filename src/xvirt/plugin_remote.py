import pytest


class XvirtPluginRemote:

    def __init__(self, config) -> None:
        self._config = config

    @pytest.hookimpl
    def pytest_runtest_logreport(self, report):
        if report.when != 'call':
            return
        config = self._config
        data = config.hook.pytest_report_to_serializable(config=config, report=report)
        from .events import EvtRuntestLogreport
        event = EvtRuntestLogreport(data)
        config.hook.pytest_xvirt_send_event(event_json=event.to_json(), config=config)

    @pytest.hookimpl
    def pytest_collection_finish(self, session: pytest.Session):
        # if session.config.option.xvirt_mode == mode_controlled:
        from .events import EvtCollectionFinish
        event = EvtCollectionFinish([item.nodeid for item in session.items])
        session.config.hook.pytest_xvirt_send_event(event_json=event.to_json(), config=session.config)

    @pytest.hookimpl
    def pytest_collectreport(self, report):
        if report.outcome != 'failed':
            return
        config = self._config
        data = config.hook.pytest_report_to_serializable(config=config, report=report)
        from .events import EvtRuntestLogreport
        event = EvtRuntestLogreport(data)
        config.hook.pytest_xvirt_send_event(event_json=event.to_json(), config=config)
