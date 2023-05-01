from pytest import Pytester

from xvirt.collectors import _rebuild_tree, VCollector, VItem


def test_collectors(pytester: Pytester):
    pytester.makeconftest(
        f"""
            def pytest_collect_file(file_path, path, parent):
                from xvirt.collectors import MockCollector
                result = MockCollector.from_parent(parent, name=file_path.name)
                result.nodeid_array = ['mock_test.py::test_1', 'mock_test.py::test_2']
                return result
                           
        """
    )
    result = pytester.runpytest('-v')
    stdout_lines = '\n'.join(result.stdout.lines)
    for nodeid in ['mock_test.py::test_1', 'mock_test.py::test_1']:
        assert nodeid in stdout_lines


def test_rebuild_tree__flat():
    nodeids = ['mock_test.py::test_1', 'mock_test.py::test_2']

    actual = _rebuild_tree(nodeids)
    expect = {'mock_test.py': VCollector(
        'mock_test.py', items=[
            VItem('mock_test.py::test_1'),
            VItem('mock_test.py::test_2')
        ])
    }
    assert actual == expect


def test_rebuild_tree__node_and_leaf():
    nodeids = [
        'foo/some_test.py::test_1',
        'foo/some_test.py::test_2',
        'foo/sub/sub_test.py::test_3',
    ]

    actual = _rebuild_tree(nodeids)
    expect = {'foo': VCollector(
        'foo', collectors={
            'foo/some_test.py': VCollector(
                'foo/some_test.py', items=[
                    VItem('foo/some_test.py::test_1'),
                    VItem('foo/some_test.py::test_2'),
                ]
            ),
            'foo/sub': VCollector(
                'foo/sub', collectors={
                    'foo/sub/sub_test.py': VCollector(
                        'foo/sub/sub_test.py', items=[
                            VItem('foo/sub/sub_test.py::test_3'),
                        ]
                    )
                }
            )
        }
    )}
    assert actual == expect


def test_skip_module__should_skip_submodule2(pytester: Pytester):
    foo = pytester.mkpydir('foo')
    (foo / 'some_test.py').write_text(
        """
def test_1(): pass
def test_2(): pass
    """
    )
    sub = pytester.mkpydir('foo/sub')
    (sub / 'sub_test.py').write_text(
        """
def test_3(): pass

class TestBar:
    def test_bar_1(self): pass
    def test_bar_2(self): pass
"""
    )
    res = pytester.runpytest('-v')
    print(res.stdout.lines)
