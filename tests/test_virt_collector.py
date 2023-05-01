from pytest import Pytester


def test_virt_collector(pytester: Pytester):
    pytester.makeconftest(
        f"""
            def pytest_collect_file(file_path, path, parent):
                from xvirt.collectors import MockCollector
                return MockCollector.from_parent(parent, name=file_path.name)
                           
        """
    )
    result = pytester.runpytest('-v')
    stdout_lines = '\n'.join(result.stdout.lines)
    for nodeid in ['test_transport.py::test_a', 'test_transport.py::test_b']:
        assert nodeid in stdout_lines
