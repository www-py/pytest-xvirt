from pathlib import Path

import pytest

from xvirt import events_handler


@pytest.hookimpl
def pytest_addhooks(pluginmanager):
    from xvirt import newhooks

    pluginmanager.add_hookspecs(newhooks)


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config) -> None:
    xvirt_packages = []
    config.hook.pytest_xvirt_setup(config=config, xvirt_packages=xvirt_packages)
    xvirt_package = ''
    if len(xvirt_packages) == 1:
        xvirt_package = xvirt_packages[0]
        # config.option.xvirt_package = xvirt_package
    elif len(xvirt_packages) > 1:
        raise Exception('multiple packages not supported')

    config.pluginmanager.register(XvirtPlugin(config, xvirt_package), "xvirt-plugin")


class XvirtPlugin:

    def __init__(self, config, xvirt_package) -> None:
        self._config = config
        self._xvirt_collect_file_done = False
        self._xvirt_package = xvirt_package

    @pytest.hookimpl
    def pytest_runtest_logreport(self, report):
        if report.when != 'call':
            return
        config = self._config
        data = config.hook.pytest_report_to_serializable(config=config, report=report)
        import json
        data_json = json.dumps(data)
        from .events import EvtRuntestLogreport
        event = EvtRuntestLogreport(data)
        config.hook.pytest_xvirt_notify(event=event, config=config)

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

        result = parent.config.hook.pytest_xvirt_collect_file(
            file_path=file_path, path=path, parent=parent
            , events_handler=events_handler.make(file_path, parent)
        )
        if len(result) == 0:
            return None
        assert len(result) == 1
        return result[0]

    def is_xvirt_package(self, path):
        if self._xvirt_package == '':
            return False
        str_path = str(path)
        return str_path.startswith(self._xvirt_package)


@pytest.hookimpl
def pytest_collection_finish(session: pytest.Session):
    # if session.config.option.xvirt_mode == mode_controlled:
    from .events import EvtCollectionFinish
    event = EvtCollectionFinish([item.nodeid for item in session.items])
    session.config.hook.pytest_xvirt_notify(event=event, config=session.config)
