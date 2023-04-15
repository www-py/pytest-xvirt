
def pytest_addoption(parser):
    group = parser.getgroup('cookie-1')
    group.addoption(
        '--skip-module',
        action='store',
        dest='dest_foo',
        default='2023',
        help='Set the value for the fixture "bar".'
    )

    parser.addini('HELLO', 'Dummy pytest.ini setting')
