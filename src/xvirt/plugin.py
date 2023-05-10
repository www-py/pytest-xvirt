from pathlib import Path

import pytest


@pytest.hookimpl
def pytest_addhooks(pluginmanager):
    from xvirt import newhooks

    pluginmanager.add_hookspecs(newhooks)


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config) -> None:
    config.pluginmanager.register(XvirtPlugin(config), "xvirt-plugin")
    xvirt_packages = []
    config.hook.pytest_xvirt_setup(config=config, xvirt_packages=xvirt_packages)
    if len(xvirt_packages) == 1:
        config.option.xvirt_package = xvirt_packages[0]
        return
    if len(xvirt_packages) > 1:
        raise Exception('multiple packages not supported')


class XvirtPlugin:

    def __init__(self, config) -> None:
        self._config = config
        config.option.xvirt_bool = False

    @pytest.hookimpl
    def pytest_runtest_logreport(self, report):
        config = self._config
        data = config.hook.pytest_report_to_serializable(config=config, report=report)
        import json
        data_json = json.dumps(data)
        from .events import EvtRuntestLogreport
        event = EvtRuntestLogreport(data)
        config.hook.pytest_xvirt_notify(event=event, config=config)

    @pytest.hookimpl
    def pytest_pycollect_makemodule(self, module_path, path, parent):
        if not hasattr(parent.config.option, 'xvirt_package'):
            return None
        if parent.config.option.xvirt_package == '':
            return None
        if str(module_path.parent).startswith(parent.config.option.xvirt_package):
            empty = Path(__file__).parent / 'empty'
            return pytest.Module.from_parent(parent, fspath=empty)
        return None


    @pytest.hookimpl
    def pytest_collect_file(self,file_path: Path, path, parent):
        # return None
        if not hasattr(parent.config.option, 'xvirt_package'):
            return None
        if parent.config.option.xvirt_package == '':
            return None

        if not str(file_path).startswith(parent.config.option.xvirt_package):
            return None

        if parent.config.option.xvirt_bool:
            return
        parent.config.option.xvirt_bool = True

        result = parent.config.hook.pytest_xvirt_collect_file(file_path=file_path, path=path, parent=parent)
        if len(result) == 0:
            return None
        assert len(result) == 1
        return result[0]


def pytest_pycollect_makeitem(collector, name, obj):
    pass


@pytest.hookimpl
def pytest_collection_finish(session: pytest.Session):
    # if session.config.option.xvirt_mode == mode_controlled:
    from .events import EvtCollectionFinish
    event = EvtCollectionFinish([item.nodeid for item in session.items])
    session.config.hook.pytest_xvirt_notify(event=event, config=session.config)
