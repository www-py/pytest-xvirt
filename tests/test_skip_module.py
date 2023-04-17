from pytest import Pytester


def test_skip_module(pytester: Pytester):
    remote = pytester.mkpydir('foo')
    (remote / 'some_test.py').write_text(
        """
def test_1():
    pass
    """
    )

    pytester.runpytest('--xvirt-package', 'foo').assert_outcomes(passed=0)


def test_skip_module__should_skip_submodule(pytester: Pytester):
    remote = pytester.mkpydir('foo')
    (remote / 'some_test.py').write_text(
        """
def test_1():
    pass
    """
    )
    sub = pytester.mkpydir('foo/sub')
    (sub / 'sub_test.py').write_text(
        """
def test_1():
    pass
        """
    )
    pytester.runpytest('--xvirt-package', 'foo.sub').assert_outcomes(passed=1)
