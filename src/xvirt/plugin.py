from pathlib import Path

import pytest


def pytest_addoption(parser):
    group = parser.getgroup('cookie-1')
    group.addoption(
        '--xvirt-package',
        action='store',
        dest='xvirt_package',
        default='',
        help='todo'
    )

    parser.addini('HELLO', 'Dummy pytest.ini setting')


def pytest_pycollect_makemodule(module_path, path, parent):
    if module_path.parent.name == parent.config.option.xvirt_package:
        empty = Path(__file__).parent / 'empty'
        return pytest.Module.from_parent(parent, fspath=empty)
    return None
