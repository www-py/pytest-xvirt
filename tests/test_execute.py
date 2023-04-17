from pytest import Pytester


def test_transport(pytester: Pytester) -> None:
    pytester.makeconftest(
        f"""
        def pytest_xvirt_notify(event):
            from xvirt.events import EvtCollectionFinish
            if isinstance(event, EvtCollectionFinish): 
                stripped_ids = [x.split('::')[1] for x in event.node_ids]
                print(f'HOOK: ' + ', '.join(stripped_ids))
    """
    )
    pytester.makepyfile(
        """
        import os
        def test_a(): pass
        def test_b(): pass
        def test_c(): pass
    """
    )
    res = pytester.runpytest()
    res.stdout.fnmatch_lines_random(["*HOOK: test_a, test_b, test_c"])

