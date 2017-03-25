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

def test_execute_line(tmpdir):
    res = execute_line('echo hello world!')
    assert res == [(STDOUT, 'hello world!\n')]

    res = execute_line('echo first; echo second ; false && ls tests || echo failure')
    assert res == [(STDOUT, 'first\n'), (STDOUT, 'second\n'), (STDOUT, 'failure\n')]

    with Tempfile() as filename:
        res = execute_line('echo some text > %s && cat %s' % (filename, filename))
        assert res == [(STDOUT, 'some text\n')]

    with Tempfile() as filename:
        res = execute_line('mkdir /tmp/a/fdsa/asdf/asdfasdf/assdf 2>&1 > %s && cat %s || true' % (filename, filename))
        assert res == [(STDOUT, 'mkdir: cannot create directory \xe2\x80\x98/tmp/a/fdsa/asdf/asdfasdf/assdf\xe2\x80\x99: No such file or directory\n')]

def test_execute_line_raises_exception():
    with pytest.raises(Exception):
        execute_line('false')
    with pytest.raises(Exception):
        execute_line('ls -lat /aaslk/asdf/asdf/asd')

def test_execute_lines():
    lines = ['echo hello world!',
             'echo first; echo second ; false && ls tests || echo failure']
