from pathlib import Path

from pytest import Pytester

from tests.find_port import find_port

parent = Path(__file__).parent


def test(pytester: Pytester):
    def read_text(filename): return (parent / filename).read_text()

    # GIVEN
    virt = pytester.mkpydir('foo')
    (virt / 'some_test.py').write_text('def test_1(): pass\ndef test_2(): pass\ndef test_3(): 1/0')

    additional = read_text('end2end_support_server.py') \
        .replace('##xvirt_package_marker##', str(virt)) \
        .replace('##finalize_marker##', 'finalize_was_called') \
        .replace('##end2end_support_client_marker##', read_text('end2end_support_client.py')) \
        .replace('1234567890', str(find_port()))  # this replaces work on 2 inception levels: server&client

    pytester.makeconftest(additional)

    # WHEN
    result = pytester.runpytest()

    # THEN
    result.assert_outcomes(passed=2, failed=1)

    assert (virt.parent / 'finalize_was_called').exists()
