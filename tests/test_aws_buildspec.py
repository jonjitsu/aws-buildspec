from click.testing import CliRunner
from .helpers import *
from aws_buildspec.cli import main


def test_main():
    runner = CliRunner()
    result = runner.invoke(main, [])

    assert result.output == '()\n'
    assert result.exit_code == 0

from aws_buildspec import *

def test_load_file():
    content = """---
    version: 0.1
    phases: {}
    """
    expected = {'version': 0.1, 'phases':{}}
    with Tempfile(content) as filename:
        assert load_file(filename) == expected
