import xvirt

from pytest import Pytester


def test_bar_fixture(pytester: Pytester):
    x = pytester.makepyfile("""
        def test_sth():
            pass
    """)

    result = pytester.runpytest('-v')

    result.stdout.fnmatch_lines(['*::test_sth PASSED*', ])


def test_skip_module(pytester: Pytester):
    remote = pytester.mkpydir('remote')
    (remote / 'some_test.py').write_text(
        """
def test_1():
    pass
    """
    )

    pytester.runpytest('--skip-module', 'remote').assert_outcomes(passed=0)
