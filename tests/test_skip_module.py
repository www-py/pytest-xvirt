import xvirt


def test_bar_fixture(testdir):
    testdir.makepyfile("""
        def test_sth():
            pass
    """)

    result = testdir.runpytest('-v')

    result.stdout.fnmatch_lines(['*::test_sth PASSED*', ])
