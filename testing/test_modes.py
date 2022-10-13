from testing.test_cli import run_program


def test_load(synology_mock, capsys):
    """
    Verify running the program with `mode=load`.
    """
    exitcode = run_program("localhost:1161", "test-user", "test-authkey", "test-privkey", "load")
    response = capsys.readouterr()
    assert exitcode == 0
    assert response.out.strip() == "OK - load average: 13.42, 8.13, 5.33 | load1=13.42c load5=8.13c load15=5.33c"
