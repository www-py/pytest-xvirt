from pytest import Pytester


# todo raccogliere dei event.node_ids di alcuni test (magari nidificati, non piatti)
# todo e trovare un modo di metterli nella pytest_collect_file per ricreare la struttura ad albero
def test_transport(pytester: Pytester) -> None:
    pytester.makeconftest(
        f"""
        def pytest_xvirt_notify(event, config):

            from xvirt.events import EvtCollectionFinish
            if isinstance(event, EvtCollectionFinish): 
                stripped_ids = [x.split('::')[1] for x in event.node_ids]
                print(f'HOOK: ' + ', '.join(stripped_ids))
                for x in event.node_ids:
                    print('XVIRT: ' + x)

            from xvirt.events import EvtRuntestLogreport
            if isinstance(event, EvtRuntestLogreport):
                report = config.hook.pytest_report_from_serializable(config=config, data=event.data)
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
    print(res.stdout.lines)
