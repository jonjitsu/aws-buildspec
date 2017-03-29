from click.testing import CliRunner
from aws_buildspec.cli import main, init
from .helpers import *
import pytest
import pprint
import os

def test_init_command(tmpdir):
    print(os.getcwd())
    tmpdir.chdir()
    print(os.getcwd())
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

def test_main():
    runner = CliRunner()
    result = runner.invoke(main, [])

#     assert result.output == '()\n'
    assert result.exit_code == 0

def test_run(tmpdir):
    """"""
    buildspec_yml = """---
    phases:
      install:
        commands:
           - echo install
      build:
        commands:
           - echo build
      post_build:
        commands:
           - echo post_build
    """
    runner = CliRunner()
    with Tempfile(buildspec_yml) as filename:
        result = runner.invoke(main, ['run', '-f', filename, 'install'])
        assert result.exit_code == 0
        assert result.output == u'Executing install phase\nOUT: install\n'

        result = runner.invoke(main, ['run', '-f', filename])
        assert result.output == u'Executing install phase\nOUT: install\nExecuting build phase\nOUT: build\nExecuting post_build phase\nOUT: post_build\n'
        assert result.exit_code == 0

        result = runner.invoke(main, ['run', '-f', filename, 'post_build'])
        assert result.output == u'Executing post_build phase\nOUT: post_build\n'
        assert result.exit_code == 0


