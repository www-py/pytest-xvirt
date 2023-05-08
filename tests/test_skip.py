from pytest import Pytester


def test_skip_module(pytester: Pytester):
    remote = pytester.mkpydir('foo')
    _xvirt_setup_server(pytester, remote)

    (remote / 'some_test.py').write_text(
        """
def test_1():
    pass
    """
    )

    pytester.runpytest().assert_outcomes(passed=0)


def test_skip_module__should_skip_submodule(pytester: Pytester):
    remote = pytester.mkpydir('foo')
    sub = pytester.mkpydir('foo/sub')
    _xvirt_setup_server(pytester, sub)

    (remote / 'some_test.py').write_text(
        """
def test_1():
    pass
def test_2():
    pass
    """
    )
    (sub / 'sub_test.py').write_text(
        """
def test_3():
    from js import document
        """
    )
    pytester.runpytest().assert_outcomes(passed=2)


def _xvirt_setup_server(pytester, remote):
    pytester.makeconftest(_xvirt_setup_server_code(remote))


def _xvirt_setup_server_code(remote):
    remote_str = str(remote)
    return f"""            
            def pytest_xvirt_setup(config):
                config.option.xvirt_package = '{remote_str}'       
        """
