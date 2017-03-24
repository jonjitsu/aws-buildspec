from .helpers import *
import pytest
import pprint
from aws_buildspec import *

def test_load_file():
    content = """---
    version: 0.1
    phases: {}
    """
    expected = {'version': 0.1, 'phases':{}}
    with Tempfile(content) as filename:
        assert load_file(filename) == expected

def test_execute_line():
    res = execute_line('echo hello world!')
    assert res == [(STDOUT, 'hello world!\n')]

    res = execute_line('echo first; echo second ; false && ls tests || echo failure')
    assert res == [(STDOUT, 'first\n'), (STDOUT, 'second\n'), (STDOUT, 'failure\n')]

    res = execute_line('echo some text > /tmp/afile && cat /tmp/afile')
    assert res == [(STDOUT, 'some text\n')]

    res = execute_line('mkdir /tmp/a/fdsa/asdf/asdfasdf/assdf 2>&1 > /tmp/afile && cat /tmp/afile || true')
    assert res == [(STDOUT, 'mkdir: cannot create directory \xe2\x80\x98/tmp/a/fdsa/asdf/asdfasdf/assdf\xe2\x80\x99: No such file or directory\n')]

def test_execute_line_raises_exception():
    with pytest.raises(Exception):
        execute_line('false')
    with pytest.raises(Exception):
        execute_line('ls -lat /aaslk/asdf/asdf/asd')
