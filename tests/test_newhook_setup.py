import json

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


def test_xvirt_run_should_not_be_called(pytester: Pytester):
    bar = pytester.mkpydir('bar')
    (bar / 'bar_test.py').write_text('def test_bar(): pass')

    virt = pytester.mkpydir('virt')
    (virt / 'sub_test.py').write_text('even no valid python')

    _setup__pytest_xvirt_setup(pytester, virt, additional=f"""
    def run(self):   
        assert 'this should not be executed' == ''
    """)

    result = pytester.runpytest(f'{bar}/')
    result.assert_outcomes(passed=1)


def _setup__pytest_xvirt_setup(pytester, remote, additional=''):
    """
    Writes a conftest.py file with a pytest_xvirt_setup hook
    :param remote: defines the remote path to be added to xvirt_packages
    :param additional: Additional conftest.py content
    """
    remote_str = str(remote)
    content = f"""    
from xvirt import XVirt

def pytest_xvirt_setup(config):
    return XvirtTest1()
        
class XvirtTest1(XVirt):

    def remote_path(self) -> str:
        return '{remote_str}'
    
{additional}"""
    pytester.makeconftest(content)
