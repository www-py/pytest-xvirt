from pytest import Pytester


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
