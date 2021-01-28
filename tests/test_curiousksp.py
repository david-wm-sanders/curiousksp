"""[pytest] Tests for curiousksp."""
from curiousksp.cli import main


def test_main():
    """Check that curiousksp.cli.main returns 0 when no args are given."""
    assert main([]) == 0
