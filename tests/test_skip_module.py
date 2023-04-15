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
