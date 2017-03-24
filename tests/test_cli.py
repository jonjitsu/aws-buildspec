from click.testing import CliRunner
from aws_buildspec.cli import main, init
from .helpers import *
import pytest
import pprint

def test_main():
    runner = CliRunner()
    result = runner.invoke(main, [])

#     assert result.output == '()\n'
    assert result.exit_code == 0

def test_init_command(tmpdir):
    tmpdir.chdir()
    runner = CliRunner()
    result = runner.invoke(main, ['init'])
    assert tmpdir.join('buildspec.yml').isfile()
    assert len(tmpdir.listdir()) == 1
    assert result.output == 'Generated buildspec.yml\n'
    assert result.exit_code == 0

def test_init_command_with_argument(tmpdir):
    tmpdir.chdir()
    runner = CliRunner()
    result = runner.invoke(main, ['init', 'simple'])
    assert tmpdir.join('buildspec.yml').isfile()
    assert len(tmpdir.listdir()) == 1
    assert result.output == 'Generated buildspec.yml\n'
    assert result.exit_code == 0

def test_init_command_with_invalid_argument():
    runner = CliRunner()
    result = runner.invoke(main, ['init', 'invalidtypecheers'])
    assert result.exit_code != 0

def test_init_command_with_alternate_filename(tmpdir):
    tmpdir.chdir()
    runner = CliRunner()
    result = runner.invoke(main, ['init', '-f', 'blah.yml'])
    assert tmpdir.join('blah.yml').isfile()
    assert len(tmpdir.listdir()) == 1
    assert result.output == 'Generated blah.yml\n'
    assert result.exit_code == 0
