from pathlib import Path
from typing import List

import pytest

from xvirt import events_handler, XVirt


@pytest.hookimpl
def pytest_addhooks(pluginmanager):
    from xvirt import newhooks

    pluginmanager.add_hookspecs(newhooks)


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config) -> None:
    config.pluginmanager.register(XvirtPluginRemote(config), "xvirt-plugin-remote")
    xvirt_packages = []
    xvirt_instances: List[XVirt] = config.hook.pytest_xvirt_setup(config=config, xvirt_packages=xvirt_packages)
    instances_count = len(xvirt_instances)
    if instances_count == 0:
        return
    if instances_count != 1:
        raise Exception('multiple xvirt users not supported')

    xvirt_instance = xvirt_instances[0]
    xvirt_package = xvirt_instance.remote_path()
    config.pluginmanager.register(XvirtPlugin(xvirt_instance, config, xvirt_package), "xvirt-plugin-server")


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


class XvirtPlugin:

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
        evt_handler_fun = events_handler.make(file_path, parent)
        return evt_handler_fun(self._xvirt_instance)

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
    session.config.hook.pytest_xvirt_send_event(event_json=event.to_json(), config=session.config)
