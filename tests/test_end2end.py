from pathlib import Path

from pytest import Pytester

from tests.test_newhook_setup import _setup__pytest_xvirt_setup

parent = Path(__file__)


def test(pytester: Pytester):
    foo = pytester.mkpydir('foo')
    (foo / 'some_test.py').write_text('def test_1(): pass\ndef test_2(): pass')
    tcp_port = find_port()
    additional = (parent / 'end2end_support_server.py').read_text()
    additional = additional.replace('1234567890', str(tcp_port))
    _setup__pytest_xvirt_setup(pytester, foo, additional=additional)
    result = pytester.runpytest()
    result.assert_outcomes(passed=2)
