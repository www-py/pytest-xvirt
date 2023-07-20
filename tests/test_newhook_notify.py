from pytest import Pytester


def test_newhook_xvirt_notify(pytester: Pytester) -> None:
    pytester.makeconftest(
        f"""
        from xvirt.events import Evt
        def pytest_xvirt_send_event(event_json, config):
            event = Evt.from_json(event_json)
            from xvirt.events import EvtCollectionFinish
            if isinstance(event, EvtCollectionFinish): 
                stripped_ids = [x.split('::')[1] for x in event.node_ids]
                print('\\nHOOK1: ' + ', '.join(stripped_ids))
                for x in event.node_ids:
                    print('XVIRT: ' + x)

            from xvirt.events import EvtRuntestLogreport
            if isinstance(event, EvtRuntestLogreport):
                report = config.hook.pytest_report_from_serializable(config=config, data=event.data)
                print('\\nHOOK2: ' + report.location[2] + ' ' + ( 'OK' if report.passed else 'BAD') )                            
    """
    )
    pytester.makepyfile(
        """
        import os
        def test_a(): pass
        def test_b(): pass
        def test_c(): 
            1/0
    """
    )
    res = pytester.runpytest('-q')
    print(res.stdout.lines)
    exactly_once = new_verifier(res.stdout.lines)

    exactly_once("HOOK1: test_a, test_b, test_c")
    exactly_once("HOOK2: test_a OK")
    exactly_once("HOOK2: test_b OK")
    exactly_once("HOOK2: test_c BAD")


def new_verifier(lines):
    def v(string):
        counter = 0
        for line in lines:
            if string == line:
                counter += 1
        if counter != 1:
            raise Exception(f'Line `{string} was found {counter} times`')

    return v
