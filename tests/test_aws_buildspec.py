
from click.testing import CliRunner

from aws_buildspec.cli import main


def test_main():
    runner = CliRunner()
    result = runner.invoke(main, [])

    assert result.output == '()\n'
    assert result.exit_code == 0

from .helpers import *
from aws_buildspec import *

def test_load_file():
    pass
