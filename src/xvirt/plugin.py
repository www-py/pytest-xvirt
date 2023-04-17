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


def pytest_pycollect_makemodule(module_path, path, parent):
    if module_path.parent == Path(parent.config.option.xvirt_package):
        empty = Path(__file__).parent / 'empty'
        return pytest.Module.from_parent(parent, fspath=empty)
    return None


@pytest.hookimpl
def pytest_addhooks(pluginmanager):
    from xvirt import newhooks

    pluginmanager.add_hookspecs(newhooks)


@pytest.hookimpl
def pytest_collection_finish(session: pytest.Session):
    # if session.config.option.xvirt_mode == mode_controlled:
    from .events import EvtCollectionFinish
    event = EvtCollectionFinish([item.nodeid for item in session.items])
    session.config.hook.pytest_xvirt_notify(event=event)
