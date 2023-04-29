from pathlib import Path

import pytest


def pytest_addoption(parser):
    group = parser.getgroup('xvirt')
    group.addoption(
        '--xvirt-folder',
        action='store',
        dest='xvirt_package',
        default='',
        # help='todo'
    )

    parser.addini('HELLO', 'Dummy pytest.ini setting')


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config) -> None:
    config.pluginmanager.register(XvirtPlugin(config), "xvirt-plugin")


class XvirtPlugin:

    def __init__(self, config) -> None:
        self._config = config

    @pytest.hookimpl
    def pytest_runtest_logreport(self, report):
        session = report.session
        config = session.config
        del report.session
        data = config.hook.pytest_report_to_serializable(config=config, report=report)
        import json
        data_json = json.dumps(data)
        from .events import EvtRuntestLogreport
        event = EvtRuntestLogreport(data)
        session.config.hook.pytest_xvirt_notify(event=event, session=session)


def pytest_pycollect_makemodule(module_path, path, parent):
    if parent.config.option.xvirt_package == '':
        return None
    if str(module_path.parent).startswith(parent.config.option.xvirt_package):
        empty = Path(__file__).parent / 'empty'
        return pytest.Module.from_parent(parent, fspath=empty)
    return None


def pytest_collect_file(file_path: Path, path, parent):
    pass


def pytest_pycollect_makeitem(collector, name, obj):
    pass


@pytest.hookimpl
def pytest_addhooks(pluginmanager):
    from xvirt import newhooks

    pluginmanager.add_hookspecs(newhooks)


@pytest.hookimpl
def pytest_collection_finish(session: pytest.Session):
    # if session.config.option.xvirt_mode == mode_controlled:
    from .events import EvtCollectionFinish
    event = EvtCollectionFinish([item.nodeid for item in session.items])
    session.config.hook.pytest_xvirt_notify(event=event, session=session)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    """This is need for pytest_runtest_logreport. Otherwise, there we will not have the session.config available"""
    out = yield
    report = out.get_result()
    report.session = item.session
