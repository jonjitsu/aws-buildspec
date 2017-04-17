import pprint
from random import shuffle

import pytest

from aws_buildspec import *
from aws_buildspec.executors import *
from aws_buildspec.results import STDERR
from aws_buildspec.results import STDOUT

from .helpers import *


def test_load_file():
    content = """---
    version: 0.1
    phases: {}
    """
    expected = {'version': 0.1, 'phases':{}}
    with Tempfile(content) as filename:
        assert load_file(filename) == expected

def test_execute_line():
    e = SystemExecutor()
    res = e.execute_line('echo hello world!')
    assert str(res) == 'OUT: hello world!'

    res = e.execute_line('echo first; echo second ; false && ls tests || echo failure')
    expected = 'OUT: first\nOUT: second\nOUT: failure'
    assert str(res) == expected

    with Tempfile() as filename:
        res = e.execute_line('echo some text > %s && cat %s' % (filename, filename))
        assert str(res) == 'OUT: some text'

    # with Tempfile() as filename:
    #     res = execute_line('mkdir /tmp/a/fdsa/asdf/asdfasdf/assdf 2>&1 > %s && cat %s || true' % (filename, filename))
    #     assert res == [(STDOUT, 'mkdir: cannot create directory \xe2\x80\x98/tmp/a/fdsa/asdf/asdfasdf/assdf\xe2\x80\x99: No such file or directory\n')]

def test_execute_line_raises_exception():
    e = SystemExecutor()
    with pytest.raises(Exception):
        e.execute_line('false')
    with pytest.raises(Exception):
        e.execute_line('ls -lat /aaslk/asdf/asdf/asd')

def test_execute_lines():
    e = SystemExecutor()
    lines = ['echo hello world!',
             'echo first; echo second ; false && ls tests || echo failure']
    actual = e.execute_lines(lines)
    expected = 'OUT: hello world!\nOUT: first\nOUT: second\nOUT: failure'
    assert str(actual) == expected

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
    e = SystemExecutor()
    assert e.execute_phases(['install'], spec).results == [(BUILDSPEC, 'Executing install phase'), (STDOUT, 'install phase\n')]
    return
    assert e.execute_phases(['build'], spec).results == [(BUILDSPEC, 'Executing build phase'), (STDOUT, 'build phase\n')]
    assert e.execute_phases(['install', 'build'], spec).results == [(BUILDSPEC, 'Executing install phase'),
                                                             (STDOUT, 'install phase\n'),
                                                             (BUILDSPEC, 'Executing build phase'),
                                                             (STDOUT, 'build phase\n')]

    with pytest.raises(Exception):
        e.execute_phases(['install', 'build', 'nonexistant'], spec)

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
            },
            'pre_build': {}
        }
    }
    assert decide_phases([], spec) == ['install', 'pre_build', 'build']

    assert decide_phases(['install'], spec) == ['install']
    assert decide_phases(['build'], spec) == ['build']
    assert decide_phases(['build', 'pre_build'], spec) == ['pre_build', 'build']
    with pytest.raises(Exception):
        decide_phases(['build', 'post_build'], spec)
