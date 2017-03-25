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

    # with Tempfile() as filename:
    #     res = execute_line('mkdir /tmp/a/fdsa/asdf/asdfasdf/assdf 2>&1 > %s && cat %s || true' % (filename, filename))
    #     assert res == [(STDOUT, 'mkdir: cannot create directory \xe2\x80\x98/tmp/a/fdsa/asdf/asdfasdf/assdf\xe2\x80\x99: No such file or directory\n')]

def test_execute_line_raises_exception():
    with pytest.raises(Exception):
        execute_line('false')
    with pytest.raises(Exception):
        execute_line('ls -lat /aaslk/asdf/asdf/asd')

def test_execute_lines():
    lines = ['echo hello world!',
             'echo first; echo second ; false && ls tests || echo failure']
    assert execute_lines(lines) == [(STDOUT, 'hello world!\n'), (STDOUT, 'first\n'), (STDOUT, 'second\n'), (STDOUT, 'failure\n')]

def test_execute_phases():
    spec = {
        'phases': {
            'install': {
                'commands': ['echo install phase']
            },
            'build': {
                'commands': ['echo build phase']
            }
        }
    }
    assert execute_phases(['install'], spec) == [(STDOUT, 'install phase\n')]
    assert execute_phases(['build'], spec) == [(STDOUT, 'build phase\n')]
    assert execute_phases(['install', 'build'], spec) == [(STDOUT, 'install phase\n'), (STDOUT, 'build phase\n')]

    with pytest.raises(Exception):
        execute_phases(['install', 'build', 'nonexistant'], spec)

from random import shuffle
def test_sort_phases():
    assert sort_phases([]) == []
    assert sort_phases(['install']) == ['install']
    assert sort_phases(['build', 'install']) == ['install', 'build']

    phases_ordered = ['install', 'pre_build', 'build', 'post_build']
    phases = phases_ordered[:]
    for i in range(10):
        assert sort_phases(phases) == phases_ordered
        shuffle(phases)


def test_decide_phases():
    spec = {}
    assert decide_phases([], spec) == []
    spec = {'phases':{}}
    assert decide_phases([], spec) == []

    spec = {
        'phases': {
            'install': {
                'commands': ['echo install phase']
            },
            'build': {
                'commands': ['echo build phase']
            }
        }
    }
    # assert decide_phases([], spec) == ['install', 'build']
