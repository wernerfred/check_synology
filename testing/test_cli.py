import sys


def run_program(*args) -> int:
    """
    Run `check_synology` program and return exit code.

    Support a variable number of command line options.
    """
    sys.argv = ["check_synology", *args]
    try:
        import check_synology
    except SystemExit as ex:
        return ex.code % 256


def test_no_options(capsys):
    """
    Verify running the program without options croaks as expected.
    """
    exitcode = run_program()
    response = capsys.readouterr()
    assert exitcode == 2
    assert response.out == ""
    assert (
        "check_synology: error: the following arguments are required: "
        "hostname, username, authkey, privkey, mode" in response.err
    )


def test_help(capsys):
    """
    Verify running the program with the `--help` option works as expected.
    """
    exitcode = run_program("--help")
    response = capsys.readouterr()
    assert exitcode == 0
    assert "the hostname" in response.out
    assert "critical value for selected mode" in response.out
    assert response.err == ""
