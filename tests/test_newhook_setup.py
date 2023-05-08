from pytest import Pytester


def test_no_execute(pytester: Pytester):
    remote = pytester.mkpydir('foo')
    _setup__pytest_xvirt_setup(pytester, remote)

    (remote / 'some_test.py').write_text('even no valid python')

    pytester.runpytest().assert_outcomes(passed=0)


def test_no_execute_for_submodule(pytester: Pytester):
    remote = pytester.mkpydir('foo')
    sub = pytester.mkpydir('foo/sub')
    _setup__pytest_xvirt_setup(pytester, sub)

    (remote / 'some_test.py').write_text('def test_1(): pass\ndef test_2(): pass')
    (sub / 'sub_test.py').write_text('even no valid python')
    pytester.runpytest().assert_outcomes(passed=2)


def _setup__pytest_xvirt_setup(pytester, remote):
    remote_str = str(remote)
    content = f"""            
                def pytest_xvirt_setup(config, xvirt_packages):
                    xvirt_packages.append('{remote_str}')
            """
    pytester.makeconftest(content)
