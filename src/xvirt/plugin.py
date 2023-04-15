from pathlib import Path

import pytest


def pytest_addoption(parser):
    group = parser.getgroup('cookie-1')
    group.addoption(
        '--skip-module',
        action='store',
        dest='dest_foo',
        default='2023',
        help='Set the value for the fixture "bar".'
    )

    parser.addini('HELLO', 'Dummy pytest.ini setting')



def pytest_pycollect_makemodule(module_path, path, parent):
    if module_path.parent.name == 'remote':
        empty = Path(__file__).parent / 'empty'
        return pytest.Module.from_parent(parent, fspath=empty)
    return None
