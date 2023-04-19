from pytest import Pytester


# todo parte server
def test_transport(pytester: Pytester) -> None:
    pytester.makeconftest(
        f"""
        def pytest_xvirt_notify(event,session):

            from xvirt.events import EvtCollectionFinish
            if isinstance(event, EvtCollectionFinish): 
                stripped_ids = [x.split('::')[1] for x in event.node_ids]
                print(f'HOOK: ' + ', '.join(stripped_ids))

            from xvirt.events import EvtRuntestLogreport
            if isinstance(event, EvtRuntestLogreport):
                report = session.config.hook.pytest_report_from_serializable(config=session.config, data=event.data)
                print('HOOK: ' + report.location[2])                            
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

    res.stdout.fnmatch_lines_random(["*HOOK: test_a"])
    res.stdout.fnmatch_lines_random(["*HOOK: test_b"])
    res.stdout.fnmatch_lines_random(["*HOOK: test_c"])
