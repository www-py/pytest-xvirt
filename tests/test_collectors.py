import json

from pytest import Pytester


def test_collectors(pytester: Pytester):
    nodeids = [
        'mock_test.py::test_1',
        'mock_test.py::test_2',
        'foo/sub/sub_test.py::TestBar::test_bar_1',
        'foo/sub/sub_test.py::TestBar::test_bar_2',
        'foo/some_test.py::test_1',
        'foo/some_test.py::test_2',
        'foo/sub/sub_test.py::test_3',
    ]
    nodeids_json = json.dumps(nodeids)
    pytester.makeconftest(
        # language=python
        f"""
            def pytest_collect_file(file_path, path, parent):
                from xvirt.collectors import VirtCollector
                result = VirtCollector.from_parent(parent, name=file_path.name)
                result.nodeid_array = {nodeids_json}
                return result
                           
        """
    )
    result = pytester.runpytest('-v')
    result.assert_outcomes(passed=len(nodeids))

    stdout_lines = '\n'.join(result.stdout.lines)
    for nodeid in nodeids:
        assert nodeid in stdout_lines


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
