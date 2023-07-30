from pathlib import Path

from xvirt import path_rewrite

_root_path = Path('/home/simone/Documents/python/wwwpy')
_remote_root = '/wwwpy_bundle'


def test_path_rewrite_from_root():
    invocation_dir = '/home/simone/Documents/python/wwwpy/tests'
    result = path_rewrite(invocation_dir, _root_path, _remote_root)
    assert result == _remote_root + '/tests'


def test_path_rewrite_only_remote():
    invocation_dir = '/home/simone/Documents/python/wwwpy/tests/remote'
    result = path_rewrite(invocation_dir, _root_path, _remote_root)
    assert result == _remote_root + '/tests/remote'
