from pytest import Pytester


def test_skip_module(pytester: Pytester):
    remote = pytester.mkpydir('foo')
    (remote / 'some_test.py').write_text(
        """
def test_1():
    pass
    """
    )

    pytester.runpytest('--xvirt-folder', str(remote)).assert_outcomes(passed=0)


def test_skip_module__should_skip_submodule(pytester: Pytester):
    remote = pytester.mkpydir('foo')
    (remote / 'some_test.py').write_text(
        """
def test_1():
    pass
def test_2():
    pass
    """
    )
    sub = pytester.mkpydir('foo/sub')
    (sub / 'sub_test.py').write_text(
        """
def test_3():
    from js import document
        """
    )
    pytester.runpytest('--xvirt-folder', str(sub)).assert_outcomes(passed=2)


def test_skip_module__should_skip_submodule2(pytester: Pytester):
    pytester.makeconftest(
        f"""
        def pytest_xvirt_notify(event,session):

            from xvirt.events import EvtCollectionFinish
            if isinstance(event, EvtCollectionFinish): 
                stripped_ids = [x.split('::')[1] for x in event.node_ids]
                print(f'HOOK: ' + ', '.join(stripped_ids))
                for x in event.node_ids:
                    print('XVIRT: ' + x)

            from xvirt.events import EvtRuntestLogreport
            if isinstance(event, EvtRuntestLogreport):
                report = session.config.hook.pytest_report_from_serializable(config=session.config, data=event.data)
                print('HOOK: ' + report.location[2])                            
    """
    )

    foo = pytester.mkpydir('foo')
    (foo / 'some_test.py').write_text(
        """
def test_1():
    pass
def test_2():
    pass
    """
    )
    sub = pytester.mkpydir('foo/sub')
    (sub / 'sub_test.py').write_text(
        """
def test_3():
    pass
        """
    )
    res = pytester.runpytest('--xvirt-folder', str(foo))
    print(res.stdout.lines)
    res.assert_outcomes(passed=0)
